import json
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

from application.use_cases.run_agent import RunAgentUseCase
from domain.entities.conversation import Conversation
from domain.ports.conversation_repository_port import ConversationRepositoryPort
from presentation.websocket.ws_step_notifier import WsStepNotifier


async def websocket_chat(
    websocket: WebSocket,
    run_agent: RunAgentUseCase,
    repository: ConversationRepositoryPort,
    conversation_id: UUID,
) -> None:
    await websocket.accept()

    # Load existing messages from DB to rebuild in-memory conversation
    conversation = Conversation()
    existing_messages = await repository.get_messages(conversation_id)
    for msg in existing_messages:
        if msg.role == "user":
            conversation.add_user_message(msg.content)
        elif msg.role == "assistant":
            conversation.add_assistant_message(msg.content)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "message":
                user_content = msg.get("content", "")
                conversation.add_user_message(user_content)

                # Persist user message
                await repository.add_message(conversation_id, "user", user_content)

                notifier = WsStepNotifier(websocket)
                tool_steps: list[dict] = []
                original_notify = notifier.notify

                async def capturing_notify(step_data: dict) -> None:
                    if step_data.get("type") in ("tool_call", "tool_result"):
                        tool_steps.append(step_data)
                    await original_notify(step_data)

                notifier.notify = capturing_notify  # type: ignore[method-assign]

                try:
                    reply = await run_agent.execute(conversation, notifier)

                    # Persist assistant message with tool steps
                    await repository.add_message(
                        conversation_id, "assistant", reply,
                        tool_steps=tool_steps if tool_steps else None,
                    )

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
