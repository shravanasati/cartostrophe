import logging
import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
QDRANT_COLLECTION = "products"

logger = logging.getLogger("cartostrophe")


def create_client() -> QdrantClient:
    logger.info("Creating Qdrant client: %s", QDRANT_URL)
    client = QdrantClient(url=QDRANT_URL)
    try:
        client.get_collections()
    except Exception as exc:  # Fail fast if Qdrant is unavailable.
        logger.exception("Qdrant connection failed")
        raise RuntimeError("Failed to connect to Qdrant") from exc
    logger.info("Qdrant connection ok")
    return client


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    if client.collection_exists(QDRANT_COLLECTION):
        collection_info = client.get_collection(QDRANT_COLLECTION)
        existing_size = collection_info.config.params.vectors.size
        logger.info(
            "Found Qdrant collection '%s' with size %s",
            QDRANT_COLLECTION,
            existing_size,
        )
        if existing_size != vector_size:
            raise RuntimeError(
                "Qdrant collection size mismatch. "
                f"Expected {vector_size}, found {existing_size}."
            )
        return

    logger.info(
        "Creating Qdrant collection '%s' with size %s",
        QDRANT_COLLECTION,
        vector_size,
    )
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def is_collection_empty(client: QdrantClient) -> bool:
    count = client.count(collection_name=QDRANT_COLLECTION, exact=True).count
    if count:
        logger.info(
            "Qdrant collection '%s' already has %s points",
            QDRANT_COLLECTION,
            count,
        )
    return count == 0


def seed_if_empty(
    client: QdrantClient,
    products: list[dict],
    vectors: list[list[float]],
) -> bool:
    if not is_collection_empty(client):
        return False

    if len(products) != len(vectors):
        raise ValueError("Products and vectors length mismatch")

    logger.info("Seeding Qdrant with %s products", len(products))
    points = [
        PointStruct(
            id=product["id"],
            vector=vectors[index],
            payload=product,
        )
        for index, product in enumerate(products)
    ]
    client.upsert(
        collection_name=QDRANT_COLLECTION,
        wait=True,
        points=points,
    )
    logger.info("Seeding completed")
    return True
