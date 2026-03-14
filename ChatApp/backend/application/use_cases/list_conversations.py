from uuid import UUID

from domain.entities.conversation_summary import ConversationSummary
from domain.ports.conversation_repository_port import ConversationRepositoryPort


class ListConversationsUseCase:
    def __init__(self, repository: ConversationRepositoryPort) -> None:
        self._repo = repository

    async def execute(
        self, user_id: str, limit: int = 50, offset: int = 0, project_id: UUID | None = None,
    ) -> list[ConversationSummary]:
        return await self._repo.list_conversations(user_id, limit, offset, project_id=project_id)
