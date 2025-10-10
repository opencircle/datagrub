"""fix llm_metadata to use JSONB type

Revision ID: i5g9h0i1j2k3
Revises: h4f8g9h0i1j2
Create Date: 2025-10-06 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i5g9h0i1j2k3'
down_revision = 'h4f8g9h0i1j2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Convert llm_metadata column from JSON to JSONB and recreate GIN index
    """
    # Drop the existing index first (if it exists)
    try:
        op.drop_index('ix_trace_evaluations_llm_metadata', table_name='trace_evaluations')
    except Exception:
        pass  # Index might not exist

    # Alter column type from JSON to JSONB
    # PostgreSQL can cast JSON to JSONB automatically
    op.execute("""
        ALTER TABLE trace_evaluations
        ALTER COLUMN llm_metadata TYPE jsonb USING llm_metadata::jsonb
    """)

    # Recreate GIN index on JSONB column
    op.create_index(
        'ix_trace_evaluations_llm_metadata',
        'trace_evaluations',
        ['llm_metadata'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Convert llm_metadata back from JSONB to JSON
    """
    # Drop GIN index
    op.drop_index('ix_trace_evaluations_llm_metadata', table_name='trace_evaluations')

    # Alter column type from JSONB to JSON
    op.execute("""
        ALTER TABLE trace_evaluations
        ALTER COLUMN llm_metadata TYPE json USING llm_metadata::json
    """)
