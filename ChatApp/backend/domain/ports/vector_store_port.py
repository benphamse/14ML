from abc import ABC, abstractmethod


class VectorStorePort(ABC):
    @abstractmethod
    async def ensure_collection(self, collection: str, vector_size: int) -> None: ...

    @abstractmethod
    async def upsert(self, collection: str, point_id: str, vector: list[float], payload: dict) -> None: ...

    @abstractmethod
    async def search(
        self, collection: str, vector: list[float], filter_conditions: dict, limit: int = 5,
    ) -> list[dict]: ...

    @abstractmethod
    async def delete(self, collection: str, point_ids: list[str]) -> None: ...

    @abstractmethod
    async def delete_by_filter(self, collection: str, filter_conditions: dict) -> None: ...
