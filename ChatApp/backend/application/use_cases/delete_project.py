from uuid import UUID

from domain.ports.project_repository_port import ProjectRepositoryPort
from domain.ports.vector_store_port import VectorStorePort

COLLECTION_NAME = "project_memories"


class DeleteProjectUseCase:
    def __init__(
        self,
        repository: ProjectRepositoryPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._repository = repository
        self._vector_store = vector_store

    async def execute(self, project_id: UUID) -> bool:
        deleted = await self._repository.delete_project(project_id)
        if deleted:
            await self._vector_store.delete_by_filter(
                COLLECTION_NAME, {"project_id": str(project_id)}
            )
        return deleted
