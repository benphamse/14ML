from google.generativeai.types import FunctionDeclaration, Tool as GeminiTool

from domain.ports.tool_port import Tool
from domain.ports.tool_registry_port import ToolRegistryPort


class ToolRegistry(ToolRegistryPort):
    def __init__(self, tools: list[Tool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def get_tool(self, name: str) -> Tool:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        return tool

    def get_gemini_tools(self) -> list[GeminiTool]:
        declarations = [
            FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
            )
            for tool in self._tools.values()
        ]
        return [GeminiTool(function_declarations=declarations)]

    def list_all(self) -> list[dict]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]
