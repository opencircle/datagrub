"""add_encryption_keys_table

Revision ID: 4461438681f4
Revises: m9n0o1p2q3r4
Create Date: 2025-10-09 21:02:09.007119

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision: str = '4461438681f4'
down_revision: Union[str, None] = 'm9n0o1p2q3r4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create encryption_keys table
    op.create_table(
        'encryption_keys',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('environment', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('key_value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('rotated_at', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Insert default development key (same as current settings)
    op.execute("""
        INSERT INTO encryption_keys (id, environment, key_value, description, is_active)
        VALUES (
            gen_random_uuid(),
            'development',
            'vF8k9mN2pQ5wX7zC3bH6jL4tR1yU8sA0dG2iK5nM9oP3qT6vW4xZ7cB1eF3hJ5=',
            'Default encryption key for development environment',
            true
        )
    """)


def downgrade() -> None:
    op.drop_table('encryption_keys')
