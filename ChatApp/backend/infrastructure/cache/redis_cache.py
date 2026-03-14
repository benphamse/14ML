import logging

from redis.asyncio import Redis

from domain.ports.cache_port import CachePort

logger = logging.getLogger(__name__)


class RedisCache(CachePort):
    def __init__(self, url: str) -> None:
        self._client: Redis = Redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
            if keys:
                await self._client.delete(*keys)
            if cursor == 0:
                break

    async def close(self) -> None:
        await self._client.aclose()
