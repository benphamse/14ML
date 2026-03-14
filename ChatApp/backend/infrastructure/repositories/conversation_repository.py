from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from domain.entities.chat_message import ChatMessage
from domain.entities.conversation_summary import ConversationSummary
from domain.ports.conversation_repository_port import ConversationRepositoryPort


class ConversationRepository(ConversationRepositoryPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_conversation(
        self, user_id: str, title: str = "New Conversation", project_id: UUID | None = None,
    ) -> ConversationSummary:
        async with self._session_factory() as session:
            conv = ConversationSummary(user_id=user_id, title=title, project_id=project_id)
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            return conv

    async def list_conversations(
        self, user_id: str, limit: int = 50, offset: int = 0, project_id: UUID | None = None,
    ) -> list[ConversationSummary]:
        async with self._session_factory() as session:
            stmt = (
                select(ConversationSummary)
                .where(ConversationSummary.user_id == user_id)
                .order_by(ConversationSummary.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            if project_id is not None:
                stmt = stmt.where(ConversationSummary.project_id == project_id)
            else:
                stmt = stmt.where(ConversationSummary.project_id.is_(None))
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_conversation(self, conversation_id: UUID) -> ConversationSummary | None:
        async with self._session_factory() as session:
            return await session.get(ConversationSummary, conversation_id)

    async def rename_conversation(self, conversation_id: UUID, title: str) -> ConversationSummary | None:
        async with self._session_factory() as session:
            conv = await session.get(ConversationSummary, conversation_id)
            if not conv:
                return None
            conv.title = title
            conv.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(conv)
            return conv

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        async with self._session_factory() as session:
            stmt = delete(ConversationSummary).where(ConversationSummary.id == conversation_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def add_message(
        self, conversation_id: UUID, role: str, content: str, tool_steps: list[dict] | None = None
    ) -> ChatMessage:
        async with self._session_factory() as session:
            msg = ChatMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_steps=tool_steps,
            )
            session.add(msg)

            # Update conversation timestamp
            await session.execute(
                update(ConversationSummary)
                .where(ConversationSummary.id == conversation_id)
                .values(updated_at=datetime.now(timezone.utc))
            )

            # Auto-generate title from first user message
            if role == "user":
                conv = await session.get(ConversationSummary, conversation_id)
                if conv and conv.title == "New Conversation":
                    conv.title = content[:60].strip() + ("..." if len(content) > 60 else "")

            await session.commit()
            await session.refresh(msg)
            return msg

    async def get_messages(self, conversation_id: UUID, limit: int = 100, offset: int = 0) -> list[ChatMessage]:
        async with self._session_factory() as session:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.conversation_id == conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
