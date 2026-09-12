"""API de recherche sémantique avec citations vers les sources indexées."""

import os

from fastapi import FastAPI, HTTPException, Query
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from ingestion.indexer import COLLECTION_NAME, EMBEDDING_MODEL


app = FastAPI(title="Elysion7", version="0.1.0")
embedder = TextEmbedding(model_name=EMBEDDING_MODEL)


def client() -> QdrantClient:
    return QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))


@app.get("/health")
def health() -> dict:
    qdrant = client()
    return {"status": "ok", "collection": COLLECTION_NAME, "indexed": qdrant.collection_exists(COLLECTION_NAME)}


@app.get("/search")
def search(
    query: str = Query(min_length=3, max_length=500),
    library: str | None = None,
    limit: int = Query(default=5, ge=1, le=20),
) -> dict:
    qdrant = client()
    if not qdrant.collection_exists(COLLECTION_NAME):
        raise HTTPException(status_code=503, detail="No collection has been indexed yet.")

    query_filter = None
    if library:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="library", match=models.MatchValue(value=library))]
        )
    vector = next(embedder.embed([query])).tolist()
    points = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    ).points
    return {
        "query": query,
        "results": [
            {
                "score": point.score,
                "content": point.payload["content"],
                "citation": {
                    "library": point.payload["library"],
                    "path": point.payload["path"],
                    "section": point.payload.get("section"),
                    "commit": point.payload.get("commit"),
                    "url": point.payload.get("source_url"),
                },
            }
            for point in points
        ],
    }
