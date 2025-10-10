"""add evaluation cost tracking fields

Revision ID: g3e7f8g9h0i1
Revises: f2d6e7f8g9h0
Create Date: 2025-10-06 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g3e7f8g9h0i1'
down_revision = 'f2d6e7f8g9h0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add cost tracking fields to trace_evaluations table.

    For LLM-based evaluations (e.g., DeepEval, Ragas), track:
    - Token usage (input, output, total)
    - Cost of running the evaluation
    - Vendor-specific metrics as JSON
    """
    # Add token tracking fields
    op.add_column('trace_evaluations', sa.Column('input_tokens', sa.Integer(), nullable=True))
    op.add_column('trace_evaluations', sa.Column('output_tokens', sa.Integer(), nullable=True))
    op.add_column('trace_evaluations', sa.Column('total_tokens', sa.Integer(), nullable=True))

    # Add cost tracking field
    op.add_column('trace_evaluations', sa.Column('evaluation_cost', sa.Float(), nullable=True))

    # Add vendor-specific metrics as JSONB for better querying
    op.add_column('trace_evaluations', sa.Column('vendor_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Create index on vendor_metrics for faster JSONB queries
    op.create_index('ix_trace_evaluations_vendor_metrics', 'trace_evaluations', ['vendor_metrics'], postgresql_using='gin')


def downgrade() -> None:
    """Remove cost tracking fields"""
    op.drop_index('ix_trace_evaluations_vendor_metrics', table_name='trace_evaluations')
    op.drop_column('trace_evaluations', 'vendor_metrics')
    op.drop_column('trace_evaluations', 'evaluation_cost')
    op.drop_column('trace_evaluations', 'total_tokens')
    op.drop_column('trace_evaluations', 'output_tokens')
    op.drop_column('trace_evaluations', 'input_tokens')
