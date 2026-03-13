from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    arguments: dict
    result: dict
