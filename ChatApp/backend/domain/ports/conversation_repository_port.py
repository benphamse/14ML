from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.chat_message import ChatMessage
from domain.entities.conversation_summary import ConversationSummary


class ConversationRepositoryPort(ABC):
    @abstractmethod
    async def create_conversation(
        self, user_id: str, title: str = "New Conversation", project_id: UUID | None = None,
    ) -> ConversationSummary: ...

    @abstractmethod
    async def list_conversations(
        self, user_id: str, limit: int = 50, offset: int = 0, project_id: UUID | None = None,
    ) -> list[ConversationSummary]: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: UUID) -> ConversationSummary | None: ...

    @abstractmethod
    async def rename_conversation(self, conversation_id: UUID, title: str) -> ConversationSummary | None: ...

    @abstractmethod
    async def delete_conversation(self, conversation_id: UUID) -> bool: ...

    @abstractmethod
    async def add_message(
        self, conversation_id: UUID, role: str, content: str, tool_steps: list[dict] | None = None
    ) -> ChatMessage: ...

    @abstractmethod
    async def get_messages(self, conversation_id: UUID, limit: int = 100, offset: int = 0) -> list[ChatMessage]: ...
