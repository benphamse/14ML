import uuid
from uuid import UUID

from domain.ports.embedding_service_port import EmbeddingServicePort
from domain.ports.vector_store_port import VectorStorePort

COLLECTION_NAME = "project_memories"


class EmbedConversationTurnUseCase:
    def __init__(
        self,
        embedding_service: EmbeddingServicePort,
        vector_store: VectorStorePort,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    async def execute(
        self,
        project_id: UUID,
        conversation_id: UUID,
        user_content: str,
        assistant_content: str,
    ) -> None:
        text = f"User: {user_content}\nAssistant: {assistant_content}"
        vector = await self._embedding_service.embed_text(text)
        point_id = str(uuid.uuid4())
        await self._vector_store.upsert(
            collection=COLLECTION_NAME,
            point_id=point_id,
            vector=vector,
            payload={
                "project_id": str(project_id),
                "conversation_id": str(conversation_id),
                "text": text,
            },
        )
