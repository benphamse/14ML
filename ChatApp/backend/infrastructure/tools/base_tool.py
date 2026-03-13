import json
from abc import abstractmethod

from domain.ports.tool_port import Tool


class BaseTool(Tool):
    """Intermediate abstract class providing shared behavior for all tools."""

    _name: str
    _description: str
    _parameters: dict

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> dict:
        return self._parameters

    @abstractmethod
    async def execute(self, args: dict) -> dict: ...

    def format_success(self, **kwargs) -> dict:
        return kwargs

    def format_error(self, message: str) -> dict:
        return {"error": message}

    def serialize_result(self, result: dict) -> str:
        return json.dumps(result)
