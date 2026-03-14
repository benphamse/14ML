import json
import logging
from datetime import datetime
from uuid import UUID

from domain.entities.chat_message import ChatMessage
from domain.entities.conversation_summary import ConversationSummary
from domain.ports.cache_port import CachePort
from domain.ports.conversation_repository_port import ConversationRepositoryPort

logger = logging.getLogger(__name__)

_TTL_LIST = 60    # conversation list changes on every new message
_TTL_CONV = 120   # single conversation summary
_TTL_MSGS = 60    # message list changes on every new message


# ── Serialization helpers ──────────────────────────────────────────────────

def _conv_to_json(conv: ConversationSummary) -> str:
    return json.dumps({
        "id": str(conv.id),
        "user_id": conv.user_id,
        "project_id": str(conv.project_id) if conv.project_id else None,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
    })


def _json_to_conv(data: str) -> ConversationSummary:
    d = json.loads(data)
    return ConversationSummary(
        id=UUID(d["id"]),
        user_id=d["user_id"],
        project_id=UUID(d["project_id"]) if d["project_id"] else None,
        title=d["title"],
        created_at=datetime.fromisoformat(d["created_at"]),
        updated_at=datetime.fromisoformat(d["updated_at"]),
    )


def _msg_to_dict(msg: ChatMessage) -> dict:
    return {
        "id": str(msg.id),
        "conversation_id": str(msg.conversation_id),
        "role": msg.role,
        "content": msg.content,
        "tool_steps": msg.tool_steps,
        "created_at": msg.created_at.isoformat(),
    }


def _json_to_msgs(data: str) -> list[ChatMessage]:
    items = json.loads(data)
    result = []
    for d in items:
        msg = ChatMessage(
            id=UUID(d["id"]),
            conversation_id=UUID(d["conversation_id"]),
            role=d["role"],
            content=d["content"],
            tool_steps=d["tool_steps"],
            created_at=datetime.fromisoformat(d["created_at"]),
        )
        result.append(msg)
    return result


# ── Cached repository ──────────────────────────────────────────────────────

class CachedConversationRepository(ConversationRepositoryPort):
    def __init__(self, repo: ConversationRepositoryPort, cache: CachePort) -> None:
        self._repo = repo
        self._cache = cache

    # ── Read methods (cache-aside) ─────────────────────────────────────────

    async def list_conversations(
        self, user_id: str, limit: int = 50, offset: int = 0, project_id: UUID | None = None,
    ) -> list[ConversationSummary]:
        key = f"conv:list:{user_id}:{project_id or 'none'}:{limit}:{offset}"
        try:
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug("cache_hit key=%s", key)
                return [_json_to_conv(item) for item in json.loads(cached)]
        except Exception:
            logger.warning("cache_error on get key=%s", key, exc_info=True)

        result = await self._repo.list_conversations(user_id, limit, offset, project_id=project_id)
        try:
            await self._cache.set(key, json.dumps([json.loads(_conv_to_json(c)) for c in result]), _TTL_LIST)
        except Exception:
            logger.warning("cache_error on set key=%s", key, exc_info=True)
        return result

    async def get_conversation(self, conversation_id: UUID) -> ConversationSummary | None:
        key = f"conv:{conversation_id}"
        try:
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug("cache_hit key=%s", key)
                return _json_to_conv(cached)
        except Exception:
            logger.warning("cache_error on get key=%s", key, exc_info=True)

        result = await self._repo.get_conversation(conversation_id)
        if result is not None:
            try:
                await self._cache.set(key, _conv_to_json(result), _TTL_CONV)
            except Exception:
                logger.warning("cache_error on set key=%s", key, exc_info=True)
        return result

    async def get_messages(
        self, conversation_id: UUID, limit: int = 100, offset: int = 0,
    ) -> list[ChatMessage]:
        key = f"conv:msgs:{conversation_id}:{limit}:{offset}"
        try:
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug("cache_hit key=%s", key)
                return _json_to_msgs(cached)
        except Exception:
            logger.warning("cache_error on get key=%s", key, exc_info=True)

        result = await self._repo.get_messages(conversation_id, limit, offset)
        try:
            await self._cache.set(key, json.dumps([_msg_to_dict(m) for m in result]), _TTL_MSGS)
        except Exception:
            logger.warning("cache_error on set key=%s", key, exc_info=True)
        return result

    # ── Write methods (invalidate cache) ──────────────────────────────────

    async def create_conversation(
        self, user_id: str, title: str = "New Conversation", project_id: UUID | None = None,
    ) -> ConversationSummary:
        result = await self._repo.create_conversation(user_id, title, project_id=project_id)
        await self._invalidate_list(user_id)
        return result

    async def rename_conversation(self, conversation_id: UUID, title: str) -> ConversationSummary | None:
        result = await self._repo.rename_conversation(conversation_id, title)
        await self._invalidate_conv(conversation_id)
        await self._invalidate_all_lists()
        return result

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        result = await self._repo.delete_conversation(conversation_id)
        if result:
            await self._invalidate_conv(conversation_id)
            await self._invalidate_msgs(conversation_id)
            await self._invalidate_all_lists()
        return result

    async def add_message(
        self, conversation_id: UUID, role: str, content: str, tool_steps: list[dict] | None = None,
    ) -> ChatMessage:
        result = await self._repo.add_message(conversation_id, role, content, tool_steps)
        await self._invalidate_conv(conversation_id)
        await self._invalidate_msgs(conversation_id)
        await self._invalidate_all_lists()
        return result

    # ── Invalidation helpers ───────────────────────────────────────────────

    async def _invalidate_conv(self, conversation_id: UUID) -> None:
        try:
            await self._cache.delete(f"conv:{conversation_id}")
        except Exception:
            logger.warning("cache_error invalidating conv:%s", conversation_id, exc_info=True)

    async def _invalidate_msgs(self, conversation_id: UUID) -> None:
        try:
            await self._cache.delete_pattern(f"conv:msgs:{conversation_id}:*")
        except Exception:
            logger.warning("cache_error invalidating conv:msgs:%s:*", conversation_id, exc_info=True)

    async def _invalidate_list(self, user_id: str) -> None:
        try:
            await self._cache.delete_pattern(f"conv:list:{user_id}:*")
        except Exception:
            logger.warning("cache_error invalidating conv:list:%s:*", user_id, exc_info=True)

    async def _invalidate_all_lists(self) -> None:
        try:
            await self._cache.delete_pattern("conv:list:*")
        except Exception:
            logger.warning("cache_error invalidating conv:list:*", exc_info=True)
