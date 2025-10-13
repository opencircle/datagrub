"""add_insight_comparisons_table

Revision ID: n0p1q2r3s4t5
Revises: 4461438681f4
Create Date: 2025-10-11 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = 'n0p1q2r3s4t5'
down_revision: Union[str, None] = '4461438681f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create insight_comparisons table for storing blind model comparison results.

    This table enables organizations to compare AI model outputs (e.g., GPT-4o vs GPT-4o-mini)
    using a judge model for unbiased evaluation. Supports per-stage comparison for the
    3-stage DTA pipeline (facts, insights, summary).

    Key Features:
    - Blind evaluation (judge doesn't know which model is which)
    - Per-stage winners and scores
    - Overall winner with cost-benefit reasoning
    - Organization-scoped with CASCADE delete on analyses
    """
    # Create insight_comparisons table
    op.create_table(
        'insight_comparisons',
        # Primary Key
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Organization & User (RBAC)
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),

        # Analyses Being Compared
        sa.Column(
            'analysis_a_id',
            UUID(as_uuid=True),
            sa.ForeignKey('call_insights_analysis.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        ),
        sa.Column(
            'analysis_b_id',
            UUID(as_uuid=True),
            sa.ForeignKey('call_insights_analysis.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        ),

        # Judge Configuration
        sa.Column('judge_model', sa.String(100), nullable=False, server_default='claude-sonnet-4.5'),
        sa.Column('evaluation_criteria', JSONB, nullable=False),

        # Overall Results
        sa.Column('overall_winner', sa.String(1), nullable=True),
        sa.Column('overall_reasoning', sa.Text, nullable=False),

        # Stage 1: Fact Extraction
        sa.Column('stage1_winner', sa.String(1), nullable=True),
        sa.Column('stage1_scores', JSONB, nullable=True),
        sa.Column('stage1_reasoning', sa.Text, nullable=True),

        # Stage 2: Reasoning & Insights
        sa.Column('stage2_winner', sa.String(1), nullable=True),
        sa.Column('stage2_scores', JSONB, nullable=True),
        sa.Column('stage2_reasoning', sa.Text, nullable=True),

        # Stage 3: Summary Synthesis
        sa.Column('stage3_winner', sa.String(1), nullable=True),
        sa.Column('stage3_scores', JSONB, nullable=True),
        sa.Column('stage3_reasoning', sa.Text, nullable=True),

        # Judge Trace (links to traces table for judge model invocation)
        sa.Column('judge_trace_id', UUID(as_uuid=True), sa.ForeignKey('traces.id'), nullable=True),

        # Metadata (judge tokens, cost, duration, etc.)
        sa.Column('comparison_metadata', JSONB, nullable=True),

        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), onupdate=sa.func.now()),

        # Check Constraints - Winner values must be 'A', 'B', or 'tie'
        sa.CheckConstraint("overall_winner IN ('A', 'B', 'tie')", name='ck_overall_winner_valid'),
        sa.CheckConstraint("stage1_winner IN ('A', 'B', 'tie')", name='ck_stage1_winner_valid'),
        sa.CheckConstraint("stage2_winner IN ('A', 'B', 'tie')", name='ck_stage2_winner_valid'),
        sa.CheckConstraint("stage3_winner IN ('A', 'B', 'tie')", name='ck_stage3_winner_valid'),

        # Unique Constraint - Prevent duplicate comparisons
        # Same analyses + same judge model = one comparison
        sa.UniqueConstraint('analysis_a_id', 'analysis_b_id', 'judge_model', name='uq_comparison'),
    )

    # Additional indexes for query performance
    # Index for organization-scoped queries
    op.create_index(
        'idx_comparisons_org_created',
        'insight_comparisons',
        ['organization_id', sa.text('created_at DESC')]
    )

    # Index for user-specific queries
    op.create_index(
        'idx_comparisons_user_created',
        'insight_comparisons',
        ['user_id', sa.text('created_at DESC')]
    )

    # Index for judge model filtering
    op.create_index(
        'idx_comparisons_judge_model',
        'insight_comparisons',
        ['judge_model']
    )


def downgrade() -> None:
    """
    Drop insight_comparisons table and all indexes.

    BACKWARD COMPATIBLE: This only removes the new table. Existing tables are not affected.
    CASCADE delete ensures no orphaned records remain.
    """
    # Drop indexes first (indexes are dropped automatically with table, but explicit for clarity)
    op.drop_index('idx_comparisons_judge_model', table_name='insight_comparisons')
    op.drop_index('idx_comparisons_user_created', table_name='insight_comparisons')
    op.drop_index('idx_comparisons_org_created', table_name='insight_comparisons')

    # Drop table (CASCADE deletes will handle foreign key references)
    op.drop_table('insight_comparisons')
