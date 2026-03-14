from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.project import Project


class ProjectRepositoryPort(ABC):
    @abstractmethod
    async def create_project(self, user_id: str, name: str, description: str = "") -> Project: ...

    @abstractmethod
    async def list_projects(self, user_id: str, limit: int = 50, offset: int = 0) -> list[Project]: ...

    @abstractmethod
    async def get_project(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def update_project(
        self, project_id: UUID, name: str | None = None, description: str | None = None,
    ) -> Project | None: ...

    @abstractmethod
    async def delete_project(self, project_id: UUID) -> bool: ...
