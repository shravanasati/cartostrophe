import json
import logging
import os
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from qdrant_client.models import FieldCondition, Filter, MatchValue, Range, MinShould

from embeddings import get_encoder
from nlu_engine import GROQ_BASE_URL, NLUEngine, ProductFilter
from qdrant_store import QDRANT_COLLECTION, get_client

logger = logging.getLogger("cartostrophe")


class SelectionResult(BaseModel):
    ids: list[int] = Field(default_factory=list, description="Selected product ids")
    reasoning_en: str = Field(
        default="",
        description="Concise explanation for why these products match the query",
    )
    reasoning_ar: str = Field(
        default="",
        description="Concise explanation for why these products match the query, in Arabic",
    )


class SelectionResultIndices(BaseModel):
    indices: list[int] = Field(
        default_factory=list,
        description="Selected candidate indices (0-based)",
    )
    reasoning_en: str = Field(
        default="",
        description="Concise explanation for why these products match the query",
    )
    reasoning_ar: str = Field(
        default="",
        description="Concise explanation for why these products match the query, in Arabic",
    )


SELECTOR_MODEL = "llama-3.3-70b-versatile"


SYSTEM_PROMPT = """You select the most relevant products for a user query.
Use only the provided candidates.
Return up to 5 candidate indices (0-based) in order of relevance.
If none of the candidates match the query, return an empty list.
Ensure that the returned indices are a subset of the eligible_indices.
Provide a concise, crisp reasoning summary (2-4 sentences) in English and Arabic.
"""


def _get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY or OPENAI_API_KEY")
    return api_key


def _create_selector() -> Any:
    model = ChatOpenAI(
        model=SELECTOR_MODEL,
        base_url=GROQ_BASE_URL,
        api_key=_get_api_key(),
        temperature=0,
    )
    return create_agent(
        model=model,
        tools=[],
        response_format=SelectionResultIndices,
        system_prompt=SYSTEM_PROMPT,
    )


def _build_filter(filters: ProductFilter) -> Filter | None:
    conditions: list[FieldCondition] = []
    attribute_conditions: list[FieldCondition] = []

    if filters.category:
        condition = FieldCondition(
            key="category", match=MatchValue(value=filters.category)
        )
        conditions.append(condition)
        logger.info("Filter: category=%s", filters.category)
    if filters.target_customer:
        condition = FieldCondition(
            key="target_customer", match=MatchValue(value=filters.target_customer)
        )
        conditions.append(condition)
        logger.info("Filter: target_customer=%s", filters.target_customer)
    if filters.attributes:
        for attribute in filters.attributes:
            condition = FieldCondition(
                key="attributes", match=MatchValue(value=attribute)
            )
            if filters.attributes_strict:
                conditions.append(condition)
            else:
                attribute_conditions.append(condition)
            logger.info("Filter: attributes includes %s", attribute)

    if filters.target_customer == "baby":
        if filters.min_age is not None:
            condition = FieldCondition(
                key="max_age", range=Range(gte=filters.min_age)
            )
            conditions.append(condition)
            logger.info("Filter: max_age >= %s", filters.min_age)
        if filters.max_age is not None:
            condition = FieldCondition(
                key="min_age", range=Range(lte=filters.max_age)
            )
            conditions.append(condition)
            logger.info("Filter: min_age <= %s", filters.max_age)

    if filters.price_min is not None or filters.price_max is not None:
        condition = FieldCondition(
            key="price",
            range=Range(gte=filters.price_min, lte=filters.price_max),
        )
        conditions.append(condition)
        logger.info(
            "Filter: price between %s and %s",
            filters.price_min,
            filters.price_max,
        )
    if filters.rating_min is not None or filters.rating_max is not None:
        condition = FieldCondition(
            key="rating",
            range=Range(gte=filters.rating_min, lte=filters.rating_max),
        )
        conditions.append(condition)
        logger.info(
            "Filter: rating between %s and %s",
            filters.rating_min,
            filters.rating_max,
        )

    if not conditions and not attribute_conditions:
        return None

    if attribute_conditions:
        return Filter(
            must=conditions,
            min_should=MinShould(min_count=0, conditions=attribute_conditions),
        )

    return Filter(must=conditions)


def _summarize_product(product: dict) -> dict:
    return {
        "id": product.get("id"),
        "name_en": product.get("name_en"),
        "category": product.get("category"),
        "price": product.get("price"),
        "min_age": product.get("min_age"),
        "max_age": product.get("max_age"),
        "target_customer": product.get("target_customer"),
        "attributes": product.get("attributes"),
        "rating": product.get("rating"),
        "description_en": product.get("description_en"),
    }


def _semantic_search(prompt: str, filters: ProductFilter, limit: int) -> list[dict]:
    encoder = get_encoder()
    vector = encoder.encode([prompt], normalize_embeddings=True)[0].tolist()
    client = get_client()
    qdrant_filter = _build_filter(filters)
    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        query_filter=qdrant_filter,
        limit=limit,
        with_payload=True,
    )
    if not len(results.points):
        return []
    products: list[dict] = []
    for result in results.points:
        print(result)
        payload = result.payload or {}
        if "id" not in payload:
            payload = {**payload, "id": result.id}
        products.append(payload)
    return products


def select_products(prompt: str, limit: int = 20) -> SelectionResult:
    nlu = NLUEngine()
    filters = nlu.extract(prompt)
    candidates = _semantic_search(prompt, filters, limit)
    if not candidates:
        return SelectionResult(
            ids=[],
            reasoning_en=(
                "No matching products found with the current filters. "
                "Try relaxing constraints like attributes, age, or price."
            ),
            reasoning_ar=(
                "لم يتم العثور على منتجات مطابقة مع عوامل التصفية الحالية. "
                "جرّب تخفيف القيود مثل السمات أو العمر أو السعر."
            ),
        )

    selector = _create_selector()
    candidate_ids = [candidate.get("id") for candidate in candidates]
    eligible_indices = [index for index, item_id in enumerate(candidate_ids) if item_id is not None]
    payload = {
        "query": prompt,
        "filters": filters.model_dump(mode="json", exclude_none=True),
        "candidates": [_summarize_product(candidate) for candidate in candidates],
        "eligible_indices": eligible_indices,
        # "index_to_id": [
        #     {"index": index, "id": item_id}
        #     for index, item_id in enumerate(candidate_ids)
        #     if item_id is not None
        # ],
    }
    result: dict[str, Any] = selector.invoke(
        {"messages": [{"role": "user", "content": json.dumps(payload)}]}
    )
    selection: SelectionResultIndices = result["structured_response"]
    print(candidate_ids, selection.indices)

    normalized_indices: list[int] = []
    for index in selection.indices:
        if isinstance(index, int):
            normalized_indices.append(index)
        elif isinstance(index, str) and index.isdigit():
            normalized_indices.append(int(index))

    normalized_indices = [
        index for index in normalized_indices if index in eligible_indices
    ]
    ids = [candidate_ids[index] for index in normalized_indices]
    selection = SelectionResult(
        ids=ids,
        reasoning_en=selection.reasoning_en,
        reasoning_ar=selection.reasoning_ar,
    )

    if not selection.ids and not selection.reasoning_en:
        selection.reasoning_en = (
            "No matching products found with the current filters. "
            "Try relaxing constraints like attributes, age, or price."
        )
    if not selection.ids and not selection.reasoning_ar:
        selection.reasoning_ar = (
            "لم يتم العثور على منتجات مطابقة مع عوامل التصفية الحالية. "
            "جرّب تخفيف القيود مثل السمات أو العمر أو السعر."
        )
    return selection

