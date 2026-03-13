from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ConversationSummary:
    id: UUID
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
