"""
FastAPI backend for the Agentic AI Chat Application.
Provides REST and WebSocket endpoints.
"""

import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_agent
from tools import FUNCTION_DECLARATIONS

app = FastAPI(title="Agentic AI Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[dict]


class ChatResponse(BaseModel):
    reply: str
    tool_steps: list[dict] = []


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/tools")
async def list_tools():
    return {"tools": [{"name": fd.name, "description": fd.description} for fd in FUNCTION_DECLARATIONS]}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Synchronous chat endpoint - sends all messages, returns final response."""
    steps = []

    async def on_step(step_data):
        steps.append(step_data)

    reply, _ = await run_agent(request.messages, on_step=on_step)
    return ChatResponse(reply=reply, tool_steps=steps)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming of agent steps.

    Protocol:
    - Client sends: {"type": "message", "messages": [...]}
    - Server sends: {"type": "tool_call", ...} for each tool invocation
    - Server sends: {"type": "tool_result", ...} for each tool result
    - Server sends: {"type": "reply", "content": "..."} for the final answer
    - Server sends: {"type": "error", "message": "..."} on errors
    """
    await websocket.accept()
    conversation_history: list[dict] = []

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                user_content = msg.get("content", "")
                conversation_history.append({
                    "role": "user",
                    "content": user_content,
                })

                async def on_step(step_data):
                    await websocket.send_text(json.dumps(step_data))

                try:
                    reply, conversation_history = await run_agent(
                        conversation_history, on_step=on_step
                    )
                    # Keep only serializable parts of the history
                    conversation_history = _serialize_history(conversation_history)

                    await websocket.send_text(json.dumps({
                        "type": "reply",
                        "content": reply,
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e),
                    }))

            elif msg.get("type") == "clear":
                conversation_history = []
                await websocket.send_text(json.dumps({
                    "type": "cleared",
                }))

    except WebSocketDisconnect:
        pass


def _serialize_history(messages: list) -> list[dict]:
    """Convert message history to JSON-serializable format."""
    serialized = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content")
            if isinstance(content, str):
                serialized.append({"role": role, "content": content})
            elif isinstance(content, list):
                # Could be tool_result blocks or content blocks
                serialized_content = []
                for block in content:
                    if isinstance(block, dict):
                        serialized_content.append(block)
                    elif hasattr(block, "model_dump"):
                        serialized_content.append(block.model_dump())
                    else:
                        serialized_content.append({"type": "text", "text": str(block)})
                serialized.append({"role": role, "content": serialized_content})
            else:
                serialized.append({"role": role, "content": str(content)})
    return serialized


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
