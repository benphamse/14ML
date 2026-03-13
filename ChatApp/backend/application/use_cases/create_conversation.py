from domain.entities.conversation_summary import ConversationSummary
from domain.ports.conversation_repository_port import ConversationRepositoryPort


class CreateConversationUseCase:
    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repo = repository

    async def execute(self, user_id: str, title: str | None = None) -> ConversationSummary:
        return await self._repo.create_conversation(user_id, title or "New Conversation")
