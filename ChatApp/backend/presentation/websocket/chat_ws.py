import asyncio
import json
import logging
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

from application.use_cases.embed_conversation_turn import EmbedConversationTurnUseCase
from application.use_cases.run_agent import RunAgentUseCase
from application.use_cases.search_project_memory import SearchProjectMemoryUseCase
from domain.entities.conversation import Conversation
from domain.ports.conversation_repository_port import ConversationRepositoryPort
from infrastructure.llm.gemini_service import SYSTEM_PROMPT
from presentation.websocket.ws_step_notifier import WsStepNotifier

logger = logging.getLogger(__name__)


def _build_rag_system_prompt(base_prompt: str, memory_snippets: list[str]) -> str:
    context = "\n---\n".join(memory_snippets)
    return (
        f"{base_prompt}\n\n"
        "## Relevant context from previous conversations in this project:\n"
        f"{context}\n\n"
        "Use the above context to provide more informed answers when relevant, "
        "but don't mention that you're reading from memory unless asked."
    )


async def websocket_chat(
    websocket: WebSocket,
    run_agent: RunAgentUseCase,
    repository: ConversationRepositoryPort,
    conversation_id: UUID,
    search_memory: SearchProjectMemoryUseCase | None = None,
    embed_turn: EmbedConversationTurnUseCase | None = None,
) -> None:
    await websocket.accept()

    # Resolve project_id for this conversation
    conv_summary = await repository.get_conversation(conversation_id)
    project_id = conv_summary.project_id if conv_summary else None

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

                # RAG: search project memory if conversation belongs to a project
                rag_context: str | None = None
                if project_id and search_memory:
                    try:
                        snippets = await search_memory.execute(project_id, user_content, limit=5)
                        if snippets:
                            rag_context = _build_rag_system_prompt(SYSTEM_PROMPT, snippets)
                    except Exception:
                        logger.warning("RAG search failed for project %s", project_id, exc_info=True)

                notifier = WsStepNotifier(websocket)
                tool_steps: list[dict] = []
                original_notify = notifier.notify

                async def capturing_notify(step_data: dict) -> None:
                    if step_data.get("type") in ("tool_call", "tool_result"):
                        tool_steps.append(step_data)
                    await original_notify(step_data)

                notifier.notify = capturing_notify  # type: ignore[method-assign]

                try:
                    reply = await run_agent.execute(
                        conversation, notifier, rag_context=rag_context,
                    )

                    # Persist assistant message with tool steps
                    await repository.add_message(
                        conversation_id, "assistant", reply,
                        tool_steps=tool_steps if tool_steps else None,
                    )

                    await websocket.send_text(json.dumps({
                        "type": "reply",
                        "content": reply,
                    }))

                    # RAG: embed the turn asynchronously
                    if project_id and embed_turn:
                        asyncio.create_task(
                            embed_turn.execute(project_id, conversation_id, user_content, reply)
                        )
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
