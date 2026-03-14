from uuid import UUID

from domain.ports.embedding_service_port import EmbeddingServicePort
from domain.ports.vector_store_port import VectorStorePort

COLLECTION_NAME = "project_memories"


class SearchProjectMemoryUseCase:
    def __init__(
        self,
        embedding_service: EmbeddingServicePort,
        vector_store: VectorStorePort,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    async def execute(self, project_id: UUID, query: str, limit: int = 5) -> list[str]:
        vector = await self._embedding_service.embed_query(query)
        results = await self._vector_store.search(
            collection=COLLECTION_NAME,
            vector=vector,
            filter_conditions={"project_id": str(project_id)},
            limit=limit,
        )
        return [r["text"] for r in results if "text" in r]
