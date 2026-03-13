import httpx

from infrastructure.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    _name = "web_search"
    _description = "Search the web for information. Returns a summary of search results."
    _parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
        },
        "required": ["query"],
    }

    async def execute(self, args: dict) -> dict:
        query = args.get("query", "")
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
                    return self.format_success(message=f"No results found for: {query}")
                return self.format_success(query=query, results=results)
        except Exception as e:
            return self.format_error(f"Search failed: {e}")
