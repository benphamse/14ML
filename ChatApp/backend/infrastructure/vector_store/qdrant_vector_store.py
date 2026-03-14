import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from domain.ports.vector_store_port import VectorStorePort

logger = logging.getLogger(__name__)


class QdrantVectorStore(VectorStorePort):
    def __init__(self, url: str) -> None:
        self._client = AsyncQdrantClient(url=url)

    async def ensure_collection(self, collection: str, vector_size: int) -> None:
        collections = await self._client.get_collections()
        existing = [c.name for c in collections.collections]
        if collection not in existing:
            await self._client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection: %s (dim=%d)", collection, vector_size)

    async def upsert(self, collection: str, point_id: str, vector: list[float], payload: dict) -> None:
        await self._client.upsert(
            collection_name=collection,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    async def search(
        self, collection: str, vector: list[float], filter_conditions: dict, limit: int = 5,
    ) -> list[dict]:
        must = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filter_conditions.items()
        ]
        results = await self._client.query_points(
            collection_name=collection,
            query=vector,
            query_filter=Filter(must=must),
            limit=limit,
            with_payload=True,
        )
        return [
            {"id": str(point.id), "score": point.score, **point.payload}
            for point in results.points
        ]

    async def delete(self, collection: str, point_ids: list[str]) -> None:
        await self._client.delete(
            collection_name=collection,
            points_selector=point_ids,
        )

    async def delete_by_filter(self, collection: str, filter_conditions: dict) -> None:
        must = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filter_conditions.items()
        ]
        await self._client.delete(
            collection_name=collection,
            points_selector=Filter(must=must),
        )

    async def close(self) -> None:
        await self._client.close()
