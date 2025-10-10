"""add missing evaluation fields for custom evals and multi-tenancy

Revision ID: k7i1j2k3l4m5
Revises: 1762fd0c1389
Create Date: 2025-10-08 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'k7i1j2k3l4m5'
down_revision = '1762fd0c1389'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add missing fields for:
    1. Multi-tenant isolation (organization_id in trace_evaluations)
    2. Custom evaluation support (prompt_input, prompt_output, created_by in evaluation_catalog)
    3. Performance indexes
    """

    # === trace_evaluations table ===

    # Add organization_id for multi-tenant isolation
    # Step 1: Add column as nullable first (for existing data)
    op.add_column(
        'trace_evaluations',
        sa.Column('organization_id', sa.UUID(), nullable=True)
    )

    # Step 2: Backfill from evaluation_catalog for custom evaluations (where org_id exists)
    op.execute("""
        UPDATE trace_evaluations te
        SET organization_id = ec.organization_id
        FROM evaluation_catalog ec
        WHERE te.evaluation_catalog_id = ec.id
        AND ec.organization_id IS NOT NULL
        AND te.organization_id IS NULL
    """)

    # Step 3: Backfill remaining NULLs from trace -> project -> organization
    # (for evaluations on public/vendor catalog items)
    op.execute("""
        UPDATE trace_evaluations te
        SET organization_id = p.organization_id
        FROM traces t
        JOIN projects p ON t.project_id = p.id
        WHERE te.trace_id = t.id
        AND te.organization_id IS NULL
    """)

    # Step 4: Make it NOT NULL now that data is backfilled
    op.alter_column('trace_evaluations', 'organization_id', nullable=False)

    # Step 5: Add foreign key constraint
    op.create_foreign_key(
        'fk_trace_eval_organization',
        'trace_evaluations',
        'organizations',
        ['organization_id'],
        ['id']
    )

    # Add performance indexes
    op.create_index(
        'idx_trace_eval_org',
        'trace_evaluations',
        ['organization_id']
    )

    op.create_index(
        'idx_trace_eval_created',
        'trace_evaluations',
        [sa.text('created_at DESC')]
    )

    op.create_index(
        'idx_trace_eval_model',
        'trace_evaluations',
        ['model_used']
    )

    # Composite index for common query patterns (org + created_at)
    op.create_index(
        'idx_trace_eval_org_created',
        'trace_evaluations',
        ['organization_id', sa.text('created_at DESC')]
    )

    # === evaluation_catalog table ===

    # Add custom evaluation fields
    op.add_column(
        'evaluation_catalog',
        sa.Column(
            'prompt_input',
            sa.Text(),
            nullable=True,
            comment='Model input definition: defines how to access the model\'s input for evaluation (use {{model_input}})'
        )
    )

    op.add_column(
        'evaluation_catalog',
        sa.Column(
            'prompt_output',
            sa.Text(),
            nullable=True,
            comment='Model output definition: defines how to access the model\'s output for evaluation (use {{model_output}})'
        )
    )

    # Evaluation system prompt runs AFTER model invocation to assess model input/output
    op.add_column(
        'evaluation_catalog',
        sa.Column(
            'custom_system_prompt',
            sa.Text(),
            nullable=True,
            comment='Evaluation system prompt: evaluates model input/output after invocation, returns score (0-1) and pass/fail'
        )
    )

    op.add_column(
        'evaluation_catalog',
        sa.Column(
            'created_by',
            sa.UUID(),
            nullable=True,
            comment='User who created this custom evaluation'
        )
    )

    # Add foreign key for created_by
    op.create_foreign_key(
        'fk_eval_catalog_created_by',
        'evaluation_catalog',
        'users',
        ['created_by'],
        ['id']
    )

    # Add index on created_by for filtering
    op.create_index(
        'idx_eval_catalog_created_by',
        'evaluation_catalog',
        ['created_by']
    )


def downgrade() -> None:
    """Remove added fields and indexes"""

    # Drop indexes
    op.drop_index('idx_eval_catalog_created_by', table_name='evaluation_catalog')
    op.drop_index('idx_trace_eval_org_created', table_name='trace_evaluations')
    op.drop_index('idx_trace_eval_model', table_name='trace_evaluations')
    op.drop_index('idx_trace_eval_created', table_name='trace_evaluations')
    op.drop_index('idx_trace_eval_org', table_name='trace_evaluations')

    # Drop foreign keys
    op.drop_constraint('fk_eval_catalog_created_by', 'evaluation_catalog', type_='foreignkey')
    op.drop_constraint('fk_trace_eval_organization', 'trace_evaluations', type_='foreignkey')

    # Drop columns from evaluation_catalog
    op.drop_column('evaluation_catalog', 'created_by')
    op.drop_column('evaluation_catalog', 'custom_system_prompt')
    op.drop_column('evaluation_catalog', 'prompt_output')
    op.drop_column('evaluation_catalog', 'prompt_input')

    # Drop organization_id from trace_evaluations
    op.drop_column('trace_evaluations', 'organization_id')
