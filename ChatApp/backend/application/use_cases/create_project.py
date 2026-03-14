from domain.entities.project import Project
from domain.ports.project_repository_port import ProjectRepositoryPort


class CreateProjectUseCase:
    def __init__(self, repository: ProjectRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, user_id: str, name: str, description: str = "") -> Project:
        return await self._repository.create_project(user_id, name, description)
