from uuid import UUID

from fastapi import APIRouter, Request, HTTPException

from application.dto.conversation_dto import (
    CreateConversationRequest,
    RenameConversationRequest,
    ConversationResponse,
    ConversationListResponse,
    ConversationMessagesResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/conversations")


def _to_response(summary) -> ConversationResponse:
    return ConversationResponse(
        id=str(summary.id),
        title=summary.title,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    request: Request,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
):
    use_case = request.app.state.list_conversations_use_case
    conversations = await use_case.execute(user_id, limit, offset)
    return ConversationListResponse(
        conversations=[_to_response(c) for c in conversations]
    )


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: Request,
    user_id: str,
    body: CreateConversationRequest | None = None,
):
    use_case = request.app.state.create_conversation_use_case
    title = body.title if body and body.title else None
    summary = await use_case.execute(user_id, title)
    return _to_response(summary)


@router.get("/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    request: Request,
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0,
):
    use_case = request.app.state.get_conversation_messages_use_case
    messages = await use_case.execute(conversation_id, limit, offset)
    return ConversationMessagesResponse(
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                tool_steps=m.tool_steps,
                created_at=m.created_at,
            )
            for m in messages
        ]
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    request: Request,
    conversation_id: UUID,
    body: RenameConversationRequest,
):
    use_case = request.app.state.rename_conversation_use_case
    summary = await use_case.execute(conversation_id, body.title)
    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _to_response(summary)


@router.delete("/{conversation_id}")
async def delete_conversation(
    request: Request,
    conversation_id: UUID,
):
    use_case = request.app.state.delete_conversation_use_case
    deleted = await use_case.execute(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}
