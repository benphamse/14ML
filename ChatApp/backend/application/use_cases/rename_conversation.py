from uuid import UUID

from domain.entities.conversation_summary import ConversationSummary
from domain.ports.conversation_repository_port import ConversationRepositoryPort


class RenameConversationUseCase:
    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repo = repository

    async def execute(self, conversation_id: UUID, title: str) -> ConversationSummary | None:
        return await self._repo.rename_conversation(conversation_id, title)
