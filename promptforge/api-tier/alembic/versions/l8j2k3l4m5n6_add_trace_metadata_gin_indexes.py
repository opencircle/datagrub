"""add trace_metadata GIN indexes for parent-child hierarchy

Revision ID: l8j2k3l4m5n6
Revises: k7i1j2k3l4m5
Create Date: 2025-10-08 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'l8j2k3l4m5n6'
down_revision = 'k7i1j2k3l4m5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add B-tree indexes on trace_metadata JSON field extractions for parent-child trace hierarchy performance.

    Indexes added:
    1. idx_trace_metadata_parent_id_text - For querying child traces by parent_trace_id
    2. idx_trace_metadata_source_text - For filtering traces by source

    Performance impact:
    - Query time reduction: O(n) → O(log n)
    - Expected improvement: 5-10x faster for trace list queries

    Note: Using B-tree indexes instead of GIN because trace_metadata is JSON (not JSONB)
    """

    # B-tree index for parent_trace_id text searches (used in WHERE clauses)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_trace_metadata_parent_id_text
        ON traces ((trace_metadata->>'parent_trace_id'))
        WHERE trace_metadata IS NOT NULL
    """)

    # B-tree index for source text searches
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_trace_metadata_source_text
        ON traces ((trace_metadata->>'source'))
        WHERE trace_metadata IS NOT NULL
    """)


def downgrade() -> None:
    """Remove indexes on trace_metadata"""

    op.execute("DROP INDEX IF EXISTS idx_trace_metadata_parent_id_text")
    op.execute("DROP INDEX IF EXISTS idx_trace_metadata_source_text")
