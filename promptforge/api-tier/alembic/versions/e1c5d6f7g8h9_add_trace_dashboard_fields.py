"""add trace dashboard fields

Revision ID: e1c5d6f7g8h9
Revises: d0b4c5f6g7h8
Create Date: 2025-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e1c5d6f7g8h9'
down_revision: Union[str, None] = 'd0b4c5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to traces table
    # P0: Critical fields for trace dashboard
    op.add_column('traces', sa.Column('input_tokens', sa.Integer(), nullable=True))
    op.add_column('traces', sa.Column('output_tokens', sa.Integer(), nullable=True))
    op.add_column('traces', sa.Column('model_name', sa.String(100), nullable=True))
    op.add_column('traces', sa.Column('provider', sa.String(100), nullable=True))
    op.add_column('traces', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))

    # P1: Important fields
    op.add_column('traces', sa.Column('environment', sa.String(50), nullable=True))
    op.add_column('traces', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))

    # Add foreign key constraint for user_id
    op.create_foreign_key(
        'fk_traces_user_id',
        'traces',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Add indexes for better query performance
    op.create_index('ix_traces_user_id', 'traces', ['user_id'])
    op.create_index('ix_traces_environment', 'traces', ['environment'])
    op.create_index('ix_traces_model_name', 'traces', ['model_name'])
    op.create_index('ix_traces_provider', 'traces', ['provider'])

    # Update status column comment to include 'retry' status
    # Note: status column already exists, just adding 'retry' as a valid value


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_traces_provider', table_name='traces')
    op.drop_index('ix_traces_model_name', table_name='traces')
    op.drop_index('ix_traces_environment', table_name='traces')
    op.drop_index('ix_traces_user_id', table_name='traces')

    # Drop foreign key constraint
    op.drop_constraint('fk_traces_user_id', 'traces', type_='foreignkey')

    # Drop columns
    op.drop_column('traces', 'retry_count')
    op.drop_column('traces', 'environment')
    op.drop_column('traces', 'user_id')
    op.drop_column('traces', 'provider')
    op.drop_column('traces', 'model_name')
    op.drop_column('traces', 'output_tokens')
    op.drop_column('traces', 'input_tokens')
