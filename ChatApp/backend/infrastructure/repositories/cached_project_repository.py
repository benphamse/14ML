import json
import logging
from datetime import datetime
from uuid import UUID

from domain.entities.project import Project
from domain.ports.cache_port import CachePort
from domain.ports.project_repository_port import ProjectRepositoryPort

logger = logging.getLogger(__name__)

_TTL_LIST = 300   # project lists change rarely
_TTL_PROJ = 300   # single project


# ── Serialization helpers ──────────────────────────────────────────────────

def _proj_to_json(project: Project) -> str:
    return json.dumps({
        "id": str(project.id),
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    })


def _json_to_proj(data: str) -> Project:
    d = json.loads(data)
    return Project(
        id=UUID(d["id"]),
        user_id=d["user_id"],
        name=d["name"],
        description=d["description"],
        created_at=datetime.fromisoformat(d["created_at"]),
        updated_at=datetime.fromisoformat(d["updated_at"]),
    )


# ── Cached repository ──────────────────────────────────────────────────────

class CachedProjectRepository(ProjectRepositoryPort):
    def __init__(self, repo: ProjectRepositoryPort, cache: CachePort) -> None:
        self._repo = repo
        self._cache = cache

    # ── Read methods (cache-aside) ─────────────────────────────────────────

    async def list_projects(
        self, user_id: str, limit: int = 50, offset: int = 0,
    ) -> list[Project]:
        key = f"proj:list:{user_id}:{limit}:{offset}"
        try:
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug("cache_hit key=%s", key)
                return [_json_to_proj(json.dumps(item)) for item in json.loads(cached)]
        except Exception:
            logger.warning("cache_error on get key=%s", key, exc_info=True)

        result = await self._repo.list_projects(user_id, limit, offset)
        try:
            await self._cache.set(key, json.dumps([json.loads(_proj_to_json(p)) for p in result]), _TTL_LIST)
        except Exception:
            logger.warning("cache_error on set key=%s", key, exc_info=True)
        return result

    async def get_project(self, project_id: UUID) -> Project | None:
        key = f"proj:{project_id}"
        try:
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug("cache_hit key=%s", key)
                return _json_to_proj(cached)
        except Exception:
            logger.warning("cache_error on get key=%s", key, exc_info=True)

        result = await self._repo.get_project(project_id)
        if result is not None:
            try:
                await self._cache.set(key, _proj_to_json(result), _TTL_PROJ)
            except Exception:
                logger.warning("cache_error on set key=%s", key, exc_info=True)
        return result

    # ── Write methods (invalidate cache) ──────────────────────────────────

    async def create_project(self, user_id: str, name: str, description: str = "") -> Project:
        result = await self._repo.create_project(user_id, name, description)
        await self._invalidate_list(user_id)
        return result

    async def update_project(
        self, project_id: UUID, name: str | None = None, description: str | None = None,
    ) -> Project | None:
        result = await self._repo.update_project(project_id, name, description)
        await self._invalidate_proj(project_id)
        await self._invalidate_all_lists()
        return result

    async def delete_project(self, project_id: UUID) -> bool:
        result = await self._repo.delete_project(project_id)
        if result:
            await self._invalidate_proj(project_id)
            await self._invalidate_all_lists()
        return result

    # ── Invalidation helpers ───────────────────────────────────────────────

    async def _invalidate_proj(self, project_id: UUID) -> None:
        try:
            await self._cache.delete(f"proj:{project_id}")
        except Exception:
            logger.warning("cache_error invalidating proj:%s", project_id, exc_info=True)

    async def _invalidate_list(self, user_id: str) -> None:
        try:
            await self._cache.delete_pattern(f"proj:list:{user_id}:*")
        except Exception:
            logger.warning("cache_error invalidating proj:list:%s:*", user_id, exc_info=True)

    async def _invalidate_all_lists(self) -> None:
        try:
            await self._cache.delete_pattern("proj:list:*")
        except Exception:
            logger.warning("cache_error invalidating proj:list:*", exc_info=True)
