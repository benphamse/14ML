import datetime

from infrastructure.tools.base_tool import BaseTool


class CreateNoteTool(BaseTool):
    _name = "create_note"
    _description = "Create a note or save information for later reference in this conversation."
    _parameters = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the note",
            },
            "content": {
                "type": "string",
                "description": "Content of the note",
            },
        },
        "required": ["title", "content"],
    }

    def __init__(self) -> None:
        self._notes: list[dict] = []

    async def execute(self, args: dict) -> dict:
        note = {
            "title": args.get("title", "Untitled"),
            "content": args.get("content", ""),
            "created_at": datetime.datetime.now().isoformat(),
        }
        self._notes.append(note)
        return self.format_success(
            message=f"Note '{note['title']}' saved successfully.",
            total_notes=len(self._notes),
        )
