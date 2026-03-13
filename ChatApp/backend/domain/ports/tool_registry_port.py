from abc import ABC, abstractmethod

from domain.ports.tool_port import Tool


class ToolRegistryPort(ABC):
    @abstractmethod
    def get_tool(self, name: str) -> Tool: ...

    @abstractmethod
    def list_all(self) -> list[dict]: ...
