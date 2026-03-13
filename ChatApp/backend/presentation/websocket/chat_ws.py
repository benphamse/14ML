import json

from fastapi import WebSocket, WebSocketDisconnect

from application.use_cases.run_agent import RunAgentUseCase
from domain.entities.conversation import Conversation
from presentation.websocket.ws_step_notifier import WsStepNotifier


async def websocket_chat(websocket: WebSocket, run_agent: RunAgentUseCase) -> None:
    await websocket.accept()
    conversation = Conversation()

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                user_content = msg.get("content", "")
                conversation.add_user_message(user_content)
                notifier = WsStepNotifier(websocket)

                try:
                    reply = await run_agent.execute(conversation, notifier)
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
                conversation.clear()
                await websocket.send_text(json.dumps({"type": "cleared"}))

    except WebSocketDisconnect:
        pass
