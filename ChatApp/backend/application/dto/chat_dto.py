from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list[dict]


class ChatResponse(BaseModel):
    reply: str
    tool_steps: list[dict] = []
