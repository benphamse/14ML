import datetime

from infrastructure.tools.base_tool import BaseTool


class GetCurrentTimeTool(BaseTool):
    _name = "get_current_time"
    _description = "Get the current date and time."
    _parameters = {"type": "object", "properties": {}}

    async def execute(self, args: dict) -> dict:
        return self.format_success(
            current_time=datetime.datetime.now().isoformat(),
            timezone="local",
        )
