from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from domain.entities.project import Project
from domain.ports.project_repository_port import ProjectRepositoryPort
from infrastructure.database.models import ProjectModel


class ProjectRepository(ProjectRepositoryPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_project(self, user_id: str, name: str, description: str = "") -> Project:
        async with self._session_factory() as session:
            project = ProjectModel(user_id=user_id, name=name, description=description)
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return self._to_entity(project)

    async def list_projects(self, user_id: str, limit: int = 50, offset: int = 0) -> list[Project]:
        async with self._session_factory() as session:
            stmt = (
                select(ProjectModel)
                .where(ProjectModel.user_id == user_id)
                .order_by(ProjectModel.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return [self._to_entity(row) for row in result.scalars().all()]

    async def get_project(self, project_id: UUID) -> Project | None:
        async with self._session_factory() as session:
            project = await session.get(ProjectModel, project_id)
            return self._to_entity(project) if project else None

    async def update_project(
        self, project_id: UUID, name: str | None = None, description: str | None = None,
    ) -> Project | None:
        async with self._session_factory() as session:
            project = await session.get(ProjectModel, project_id)
            if not project:
                return None
            if name is not None:
                project.name = name
            if description is not None:
                project.description = description
            project.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(project)
            return self._to_entity(project)

    async def delete_project(self, project_id: UUID) -> bool:
        async with self._session_factory() as session:
            stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    def _to_entity(model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
