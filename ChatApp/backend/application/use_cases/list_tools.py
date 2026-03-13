from domain.ports.tool_registry_port import ToolRegistryPort


class ListToolsUseCase:
    def __init__(self, tool_registry: ToolRegistryPort) -> None:
        self._registry = tool_registry

    def execute(self) -> list[dict]:
        return self._registry.list_all()
