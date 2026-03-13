from typing import Literal

from pydantic import BaseModel


class WsIncomingMessage(BaseModel):
    type: str
    content: str = ""


class WsToolCall(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    tool: str
    input: dict


class WsToolResult(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool: str
    result: str


class WsStream(BaseModel):
    type: Literal["stream"] = "stream"
    content: str


class WsReply(BaseModel):
    type: Literal["reply"] = "reply"
    content: str


class WsError(BaseModel):
    type: Literal["error"] = "error"
    message: str


class WsStatus(BaseModel):
    type: Literal["status"] = "status"
    content: str


class WsCleared(BaseModel):
    type: Literal["cleared"] = "cleared"
