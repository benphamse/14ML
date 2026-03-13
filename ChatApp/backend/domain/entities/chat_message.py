from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ChatMessage:
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    tool_steps: list[dict] | None
    created_at: datetime
