from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from domain.entities.chat_message import ChatMessage
from domain.entities.conversation_summary import ConversationSummary
from domain.ports.conversation_repository_port import ConversationRepositoryPort
from infrastructure.database.models import ConversationModel, MessageModel


class ConversationRepository(ConversationRepositoryPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_conversation(self, user_id: str, title: str = "New Conversation") -> ConversationSummary:
        async with self._session_factory() as session:
            conv = ConversationModel(user_id=user_id, title=title)
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            return self._to_summary(conv)

    async def list_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> list[ConversationSummary]:
        async with self._session_factory() as session:
            stmt = (
                select(ConversationModel)
                .where(ConversationModel.user_id == user_id)
                .order_by(ConversationModel.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return [self._to_summary(row) for row in result.scalars().all()]

    async def get_conversation(self, conversation_id: UUID) -> ConversationSummary | None:
        async with self._session_factory() as session:
            conv = await session.get(ConversationModel, conversation_id)
            return self._to_summary(conv) if conv else None

    async def rename_conversation(self, conversation_id: UUID, title: str) -> ConversationSummary | None:
        async with self._session_factory() as session:
            conv = await session.get(ConversationModel, conversation_id)
            if not conv:
                return None
            conv.title = title
            conv.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(conv)
            return self._to_summary(conv)

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        async with self._session_factory() as session:
            stmt = delete(ConversationModel).where(ConversationModel.id == conversation_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def add_message(
        self, conversation_id: UUID, role: str, content: str, tool_steps: list[dict] | None = None
    ) -> ChatMessage:
        async with self._session_factory() as session:
            msg = MessageModel(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_steps=tool_steps,
            )
            session.add(msg)

            # Update conversation timestamp
            await session.execute(
                update(ConversationModel)
                .where(ConversationModel.id == conversation_id)
                .values(updated_at=datetime.now(timezone.utc))
            )

            # Auto-generate title from first user message
            if role == "user":
                conv = await session.get(ConversationModel, conversation_id)
                if conv and conv.title == "New Conversation":
                    conv.title = content[:60].strip() + ("..." if len(content) > 60 else "")

            await session.commit()
            await session.refresh(msg)
            return self._to_chat_message(msg)

    async def get_messages(self, conversation_id: UUID, limit: int = 100, offset: int = 0) -> list[ChatMessage]:
        async with self._session_factory() as session:
            stmt = (
                select(MessageModel)
                .where(MessageModel.conversation_id == conversation_id)
                .order_by(MessageModel.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return [self._to_chat_message(row) for row in result.scalars().all()]

    @staticmethod
    def _to_summary(conv: ConversationModel) -> ConversationSummary:
        return ConversationSummary(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )

    @staticmethod
    def _to_chat_message(msg: MessageModel) -> ChatMessage:
        return ChatMessage(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            tool_steps=msg.tool_steps,
            created_at=msg.created_at,
        )
