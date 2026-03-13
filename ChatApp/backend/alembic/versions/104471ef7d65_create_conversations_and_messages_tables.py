"""create conversations and messages tables

Revision ID: 104471ef7d65
Revises:
Create Date: 2026-03-13 22:29:07.553791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = '104471ef7d65'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(500), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        'ix_conversations_user_id_updated',
        'conversations',
        ['user_id', sa.text('updated_at DESC')],
    )

    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False, server_default=''),
        sa.Column('tool_steps', JSONB, nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        'ix_messages_conversation_id_created',
        'messages',
        ['conversation_id', 'created_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_messages_conversation_id_created', table_name='messages')
    op.drop_table('messages')
    op.drop_index('ix_conversations_user_id_updated', table_name='conversations')
    op.drop_table('conversations')
