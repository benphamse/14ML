"""
Agent tools that the AI can use during conversations.
Each tool has a definition (Gemini function declaration format) and an execute function.
"""

import httpx
import json
import datetime
from google.generativeai.types import FunctionDeclaration, Tool


FUNCTION_DECLARATIONS = [
    FunctionDeclaration(
        name="get_current_time",
        description="Get the current date and time.",
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
    FunctionDeclaration(
        name="calculator",
        description="Evaluate a mathematical expression. Supports basic arithmetic, powers, roots, etc.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '2 + 2', 'sqrt(16)', '2**10'",
                },
            },
            "required": ["expression"],
        },
    ),
    FunctionDeclaration(
        name="web_search",
        description="Search the web for information. Returns a summary of search results.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
            },
            "required": ["query"],
        },
    ),
    FunctionDeclaration(
        name="create_note",
        description="Create a note or save information for later reference in this conversation.",
        parameters={
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
        },
    ),
]

GEMINI_TOOLS = [Tool(function_declarations=FUNCTION_DECLARATIONS)]

# In-memory note storage (per-session)
_notes: list[dict] = []


async def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool and return the result as a dict."""
    if tool_name == "get_current_time":
        return {
            "current_time": datetime.datetime.now().isoformat(),
            "timezone": "local",
        }

    elif tool_name == "calculator":
        expression = tool_input.get("expression", "")
        try:
            import math
            allowed = {
                k: v for k, v in math.__dict__.items() if not k.startswith("_")
            }
            allowed["abs"] = abs
            allowed["round"] = round
            result = eval(expression, {"__builtins__": {}}, allowed)
            return {"expression": expression, "result": str(result)}
        except Exception as e:
            return {"error": f"Could not evaluate: {e}"}

    elif tool_name == "web_search":
        query = tool_input.get("query", "")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": "1"},
                )
                data = resp.json()
                results = []
                if data.get("AbstractText"):
                    results.append({"type": "abstract", "text": data["AbstractText"]})
                for topic in data.get("RelatedTopics", [])[:5]:
                    if "Text" in topic:
                        results.append({"type": "related", "text": topic["Text"]})
                if not results:
                    return {"message": f"No results found for: {query}"}
                return {"query": query, "results": results}
        except Exception as e:
            return {"error": f"Search failed: {e}"}

    elif tool_name == "create_note":
        note = {
            "title": tool_input.get("title", "Untitled"),
            "content": tool_input.get("content", ""),
            "created_at": datetime.datetime.now().isoformat(),
        }
        _notes.append(note)
        return {
            "message": f"Note '{note['title']}' saved successfully.",
            "total_notes": len(_notes),
        }

    else:
        return {"error": f"Unknown tool: {tool_name}"}
