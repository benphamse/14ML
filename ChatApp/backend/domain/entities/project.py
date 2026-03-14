from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Project:
    id: UUID
    user_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
