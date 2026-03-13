from uuid import UUID

from domain.ports.conversation_repository_port import ConversationRepositoryPort


class DeleteConversationUseCase:
    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repo = repository

    async def execute(self, conversation_id: UUID) -> bool:
        return await self._repo.delete_conversation(conversation_id)
