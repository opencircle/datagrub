"""drop legacy evaluation tables

Revision ID: m9n0o1p2q3r4
Revises: l8j2k3l4m5n6
Create Date: 2025-10-09 12:00:00.000000

This migration drops the old evaluation and evaluation_results tables
which have been replaced by the trace_evaluations system.

All evaluation functionality now uses:
- evaluation_catalog: Available evaluations (vendor/promptforge/custom)
- trace_evaluations: Results of evaluations run on traces

The old tables were:
- evaluations: Legacy evaluation tracking (replaced)
- evaluation_results: Legacy evaluation results (replaced)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm9n0o1p2q3r4'
down_revision = 'l8j2k3l4m5n6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop legacy evaluation tables"""
    # Drop foreign key constraints first
    op.drop_constraint('evaluation_results_evaluation_id_fkey', 'evaluation_results', type_='foreignkey')

    # Drop tables
    op.drop_table('evaluation_results')
    op.drop_table('evaluations')


def downgrade() -> None:
    """Recreate legacy evaluation tables"""
    # Recreate evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('evaluation_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='evaluations_created_by_fkey'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='evaluations_project_id_fkey'),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompt_versions.id'], name='evaluations_prompt_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='evaluations_pkey')
    )

    # Recreate evaluation_results table
    op.create_table(
        'evaluation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_name', sa.String(length=255), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('expected_output', sa.Text(), nullable=True),
        sa.Column('actual_output', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], name='evaluation_results_evaluation_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='evaluation_results_pkey')
    )

    # Recreate indexes
    op.create_index('ix_evaluations_created_by', 'evaluations', ['created_by'])
    op.create_index('ix_evaluations_project_id', 'evaluations', ['project_id'])
    op.create_index('ix_evaluation_results_evaluation_id', 'evaluation_results', ['evaluation_id'])
