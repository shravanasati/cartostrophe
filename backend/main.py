import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from embeddings import embed_products, get_encoder
from qdrant_store import ensure_collection, get_client, is_collection_empty, seed_if_empty
from nlu_engine import NLUEngine, ProductFilter
from rag import SelectionResult, select_products
from dotenv import load_dotenv

load_dotenv()

_root_logger = logging.getLogger()
_root_logger.setLevel(logging.WARNING)
logger = logging.getLogger("cartostrophe")
logger.setLevel(logging.INFO)
logger.propagate = False
_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_handler.setFormatter(
    logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",     datefmt="%Y-%m-%d %H:%M:%S")
)
logger.addHandler(_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_client()
    encoder = get_encoder()
    vector_size = encoder.get_embedding_dimension()
    ensure_collection(client, vector_size)

    seeded = False
    if is_collection_empty(client):
        products = _load_products()
        vectors = embed_products(products, encoder)
        seeded = seed_if_empty(client, products, vectors)
    app.state.qdrant_client = client
    app.state.qdrant_seeded = seeded
    app.state.encoder = encoder
    yield
    client.close()


app = FastAPI(lifespan=lifespan)


class RagRequest(BaseModel):
    prompt: str = Field(..., description="User query")
    limit: int = Field(default=20, ge=1, le=50, description="Candidate pool size")


class NluRequest(BaseModel):
    prompt: str = Field(..., description="User query")


def _load_products() -> list[dict]:
    dataset_path = Path(__file__).with_name("dataset.json")
    with dataset_path.open("r", encoding="utf-8") as dataset_file:
        data = json.load(dataset_file)
    if not isinstance(data, list):
        raise ValueError("dataset.json must contain a list of products")
    return data


@app.get("/")
async def root():
    return {"message": "Hello from Cartostrophe API"}


@app.post("/search", response_model=SelectionResult)
async def rag_search(request: RagRequest) -> SelectionResult:
    return select_products(request.prompt, request.limit)


@app.post("/nlu", response_model=ProductFilter)
async def nlu_extract(request: NluRequest) -> ProductFilter:
    engine = NLUEngine()
    return engine.extract(request.prompt)
