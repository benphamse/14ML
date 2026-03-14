from domain.entities.project import Project
from domain.ports.project_repository_port import ProjectRepositoryPort


class ListProjectsUseCase:
    def __init__(self, repository: ProjectRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, user_id: str, limit: int = 50, offset: int = 0) -> list[Project]:
        return await self._repository.list_projects(user_id, limit, offset)
