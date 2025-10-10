"""add model provider config tables

Revision ID: c9a3b4d5e6f7
Revises: b8f209885293
Create Date: 2025-10-05 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c9a3b4d5e6f7'
down_revision = 'b8f209885293'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create model_provider_metadata table
    op.create_table('model_provider_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('required_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('optional_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('default_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('supported_models', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('api_key_pattern', sa.String(length=255), nullable=True),
        sa.Column('api_key_prefix', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_name')
    )
    op.create_index(op.f('ix_model_provider_metadata_is_active'), 'model_provider_metadata', ['is_active'], unique=False)
    op.create_index(op.f('ix_model_provider_metadata_provider_type'), 'model_provider_metadata', ['provider_type'], unique=False)

    # Create model_provider_configs table
    op.create_table('model_provider_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('provider_name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('api_key_hash', sa.String(length=128), nullable=False),
        sa.Column('config_encrypted', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("provider_name != ''", name='ck_provider_name_not_empty'),
        sa.CheckConstraint("provider_type IN ('llm', 'embedding', 'image', 'audio', 'multimodal')", name='ck_provider_type'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'project_id', 'provider_name', 'provider_type', name='uq_org_project_provider')
    )
    op.create_index(op.f('ix_model_provider_configs_is_active'), 'model_provider_configs', ['is_active'], unique=False)
    op.create_index(op.f('ix_model_provider_configs_organization_id'), 'model_provider_configs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_model_provider_configs_project_id'), 'model_provider_configs', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_model_provider_configs_project_id'), table_name='model_provider_configs')
    op.drop_index(op.f('ix_model_provider_configs_organization_id'), table_name='model_provider_configs')
    op.drop_index(op.f('ix_model_provider_configs_is_active'), table_name='model_provider_configs')
    op.drop_table('model_provider_configs')
    op.drop_index(op.f('ix_model_provider_metadata_provider_type'), table_name='model_provider_metadata')
    op.drop_index(op.f('ix_model_provider_metadata_is_active'), table_name='model_provider_metadata')
    op.drop_table('model_provider_metadata')
