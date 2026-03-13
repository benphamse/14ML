from fastapi import APIRouter, Request

from application.dto.chat_dto import ChatRequest, ChatResponse
from application.use_cases.run_agent import RunAgentUseCase
from domain.entities.conversation import Conversation
from presentation.websocket.ws_step_notifier import ListStepNotifier

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    run_agent: RunAgentUseCase = request.app.state.run_agent_use_case
    notifier = ListStepNotifier()

    conversation = Conversation()
    for msg in body.messages:
        if msg.get("role") == "user":
            conversation.add_user_message(msg.get("content", ""))
        elif msg.get("role") == "assistant":
            conversation.add_assistant_message(msg.get("content", ""))

    reply = await run_agent.execute(conversation, notifier)
    return ChatResponse(reply=reply, tool_steps=notifier.steps)
