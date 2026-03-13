from uuid import UUID

from domain.entities.chat_message import ChatMessage
from domain.ports.conversation_repository_port import ConversationRepositoryPort


class GetConversationMessagesUseCase:
    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repo = repository

    async def execute(self, conversation_id: UUID, limit: int = 100, offset: int = 0) -> list[ChatMessage]:
        return await self._repo.get_messages(conversation_id, limit, offset)
