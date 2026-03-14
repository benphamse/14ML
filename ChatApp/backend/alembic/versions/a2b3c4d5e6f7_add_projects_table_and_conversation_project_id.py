"""add projects table and conversation project_id

Revision ID: a2b3c4d5e6f7
Revises: 104471ef7d65
Create Date: 2026-03-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP


# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = '104471ef7d65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False, server_default=''),
        sa.Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        'ix_projects_user_id_updated',
        'projects',
        ['user_id', sa.text('updated_at DESC')],
    )

    op.add_column(
        'conversations',
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index(
        'ix_conversations_project_id',
        'conversations',
        ['project_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_conversations_project_id', table_name='conversations')
    op.drop_column('conversations', 'project_id')
    op.drop_index('ix_projects_user_id_updated', table_name='projects')
    op.drop_table('projects')
