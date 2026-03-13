from dataclasses import dataclass, field

from domain.entities.tool_result import ToolResult


@dataclass
class Message:
    role: str
    content: str
    tool_steps: list[ToolResult] = field(default_factory=list)

    @staticmethod
    def user(content: str) -> "Message":
        return Message(role="user", content=content)

    @staticmethod
    def assistant(content: str, tool_steps: list[ToolResult] | None = None) -> "Message":
        return Message(role="assistant", content=content, tool_steps=tool_steps or [])
