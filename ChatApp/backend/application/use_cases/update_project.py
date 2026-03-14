from uuid import UUID

from domain.entities.project import Project
from domain.ports.project_repository_port import ProjectRepositoryPort


class UpdateProjectUseCase:
    def __init__(self, repository: ProjectRepositoryPort) -> None:
        self._repository = repository

    async def execute(
        self, project_id: UUID, name: str | None = None, description: str | None = None,
    ) -> Project | None:
        return await self._repository.update_project(project_id, name, description)
