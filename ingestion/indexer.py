"""Indexation vectorielle idempotente dans Qdrant."""

import hashlib
import os
import uuid
from typing import Iterable

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from ingestion.pipeline import build_chunks


COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "technical_knowledge")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
BATCH_SIZE = 64


def point_id(chunk: dict) -> str:
    identity = "|".join(
        str(chunk.get(key, ""))
        for key in ("library", "commit", "path", "section", "chunk_index", "content")
    )
    digest = hashlib.sha256(identity.encode("utf-8")).digest()
    return str(uuid.UUID(bytes=digest[:16]))


def source_url(chunk: dict) -> str | None:
    repository = chunk.get("repository")
    revision = chunk.get("commit") or chunk.get("branch")
    path = chunk.get("path")
    if not repository or not revision or not path:
        return None
    return f"{repository.removesuffix('.git')}/blob/{revision}/{path}"


def payload(chunk: dict) -> dict:
    return {
        key: value
        for key, value in chunk.items()
        if key != "content" and value is not None
    } | {"source_url": source_url(chunk), "content": chunk["content"]}


def batched(items: list[dict], size: int) -> Iterable[list[dict]]:
    for offset in range(0, len(items), size):
        yield items[offset : offset + size]


def index_library(library: str, qdrant_url: str | None = None) -> int:
    chunks = build_chunks(library)
    if not chunks:
        return 0

    embedder = TextEmbedding(model_name=EMBEDDING_MODEL)
    client = QdrantClient(url=qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333"))
    vector_size = len(next(embedder.embed([chunks[0]["content"]])))

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    for batch in batched(chunks, BATCH_SIZE):
        vectors = list(embedder.embed([chunk["content"] for chunk in batch]))
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(id=point_id(chunk), vector=vector.tolist(), payload=payload(chunk))
                for chunk, vector in zip(batch, vectors, strict=True)
            ],
            wait=True,
        )
    return len(chunks)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index a configured library in Qdrant")
    parser.add_argument("library", nargs="?", default="fastapi")
    args = parser.parse_args()
    print(f"Indexed {index_library(args.library)} chunks for {args.library}.")
