import logging
import os

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2"
)

logger = logging.getLogger("cartostrophe")
_ENCODER: SentenceTransformer | None = None


def get_encoder() -> SentenceTransformer:
    global _ENCODER
    if _ENCODER is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _ENCODER = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _ENCODER


def build_product_text(product: dict) -> str:
    parts = [
        product.get("name_en"),
        product.get("description_en"),
        product.get("name_ar"),
        product.get("description_ar"),
        ",".join(product.get("attributes", []))
    ]
    return " ".join(part for part in parts if part)


def embed_products(
    products: list[dict], encoder: SentenceTransformer
) -> list[list[float]]:
    logger.info("Encoding %s product texts", len(products))
    texts = [build_product_text(product) for product in products]
    vectors = encoder.encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]
