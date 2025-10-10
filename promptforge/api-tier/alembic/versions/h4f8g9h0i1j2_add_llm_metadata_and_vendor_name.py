"""add llm_metadata and vendor_name columns

Revision ID: h4f8g9h0i1j2
Revises: g3e7f8g9h0i1
Create Date: 2025-10-06 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h4f8g9h0i1j2'
down_revision = 'g3e7f8g9h0i1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add comprehensive LLM metadata tracking to trace_evaluations table.
    Add vendor_name to evaluation_catalog table for UI display.

    LLM metadata captures all available metrics when evaluations involve LLM invocations:
    - Token usage (input, output, cache)
    - Cost breakdown
    - Performance metrics (latency, throughput)
    - Request parameters (temperature, top_p, etc.)
    - Response metadata (finish_reason, model_version, etc.)
    - Rate limit information
    """
    # Add comprehensive LLM metadata as JSONB to trace_evaluations
    op.add_column(
        'trace_evaluations',
        sa.Column(
            'llm_metadata',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='Comprehensive LLM metrics for evaluation invocations'
        )
    )

    # Create GIN index for efficient JSONB queries
    op.create_index(
        'ix_trace_evaluations_llm_metadata',
        'trace_evaluations',
        ['llm_metadata'],
        postgresql_using='gin'
    )

    # Add vendor_name to evaluation_catalog for easier UI display
    op.add_column(
        'evaluation_catalog',
        sa.Column(
            'vendor_name',
            sa.String(100),
            nullable=True,
            comment='Display name of the vendor (e.g., DeepEval, Ragas, MLflow)'
        )
    )

    # Create index on vendor_name for filtering
    op.create_index(
        'ix_evaluation_catalog_vendor_name',
        'evaluation_catalog',
        ['vendor_name']
    )


def downgrade() -> None:
    """Remove LLM metadata and vendor_name columns"""
    # Drop vendor_name from evaluation_catalog
    op.drop_index('ix_evaluation_catalog_vendor_name', table_name='evaluation_catalog')
    op.drop_column('evaluation_catalog', 'vendor_name')

    # Drop llm_metadata from trace_evaluations
    op.drop_index('ix_trace_evaluations_llm_metadata', table_name='trace_evaluations')
    op.drop_column('trace_evaluations', 'llm_metadata')
