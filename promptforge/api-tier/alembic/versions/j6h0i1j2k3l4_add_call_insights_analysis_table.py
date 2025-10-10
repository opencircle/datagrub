"""add call insights analysis table

Revision ID: j6h0i1j2k3l4
Revises: i5g9h0i1j2k3
Create Date: 2025-10-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'j6h0i1j2k3l4'
down_revision = 'i5g9h0i1j2k3'
branch_labels = None
depends_on = None


def upgrade():
    # Create call_insights_analysis table
    op.create_table(
        'call_insights_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transcript_title', sa.String(length=500), nullable=True),
        sa.Column('transcript_input', sa.Text(), nullable=False),
        sa.Column('facts_output', sa.Text(), nullable=False),
        sa.Column('insights_output', sa.Text(), nullable=False),
        sa.Column('summary_output', sa.Text(), nullable=False),
        sa.Column('pii_redacted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('stage_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parent_trace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_duration_ms', sa.Float(), nullable=True),
        sa.Column('analysis_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['parent_trace_id'], ['traces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient queries
    op.create_index('ix_call_insights_analysis_organization_id', 'call_insights_analysis', ['organization_id'])
    op.create_index('ix_call_insights_analysis_project_id', 'call_insights_analysis', ['project_id'])
    op.create_index('ix_call_insights_analysis_transcript_title', 'call_insights_analysis', ['transcript_title'])
    op.create_index('ix_call_insights_analysis_created_at', 'call_insights_analysis', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_call_insights_analysis_created_at', table_name='call_insights_analysis')
    op.drop_index('ix_call_insights_analysis_transcript_title', table_name='call_insights_analysis')
    op.drop_index('ix_call_insights_analysis_project_id', table_name='call_insights_analysis')
    op.drop_index('ix_call_insights_analysis_organization_id', table_name='call_insights_analysis')

    # Drop table
    op.drop_table('call_insights_analysis')
