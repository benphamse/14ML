from datetime import datetime

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    title: str | None = None


class RenameConversationRequest(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    tool_steps: list[dict] | None = None
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    messages: list[MessageResponse]
