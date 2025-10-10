"""add_system_prompts_and_models_to_call_insights

Revision ID: 1762fd0c1389
Revises: j6h0i1j2k3l4
Create Date: 2025-10-08 13:10:03.142247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1762fd0c1389'
down_revision: Union[str, None] = 'j6h0i1j2k3l4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add system prompt columns for each DTA stage
    op.add_column('call_insights_analysis', sa.Column('system_prompt_stage1', sa.Text(), nullable=True))
    op.add_column('call_insights_analysis', sa.Column('system_prompt_stage2', sa.Text(), nullable=True))
    op.add_column('call_insights_analysis', sa.Column('system_prompt_stage3', sa.Text(), nullable=True))

    # Add model tracking columns for each stage (for experimentation)
    op.add_column('call_insights_analysis', sa.Column('model_stage1', sa.String(length=100), nullable=True, server_default='gpt-4o-mini'))
    op.add_column('call_insights_analysis', sa.Column('model_stage2', sa.String(length=100), nullable=True, server_default='gpt-4o-mini'))
    op.add_column('call_insights_analysis', sa.Column('model_stage3', sa.String(length=100), nullable=True, server_default='gpt-4o-mini'))


def downgrade() -> None:
    # Remove model tracking columns
    op.drop_column('call_insights_analysis', 'model_stage3')
    op.drop_column('call_insights_analysis', 'model_stage2')
    op.drop_column('call_insights_analysis', 'model_stage1')

    # Remove system prompt columns
    op.drop_column('call_insights_analysis', 'system_prompt_stage3')
    op.drop_column('call_insights_analysis', 'system_prompt_stage2')
    op.drop_column('call_insights_analysis', 'system_prompt_stage1')
