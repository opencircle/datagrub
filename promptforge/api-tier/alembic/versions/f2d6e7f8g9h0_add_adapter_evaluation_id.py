"""add adapter_evaluation_id to evaluation_catalog

Revision ID: f2d6e7f8g9h0
Revises: e1c5d6f7g8h9
Create Date: 2025-10-06 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2d6e7f8g9h0'
down_revision = 'e1c5d6f7g8h9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add adapter_evaluation_id column to evaluation_catalog table.
    This field stores the adapter's internal ID (e.g., 'pf-prompt-quality-score')
    which is used by adapters to identify and execute evaluations.
    """
    # Add adapter_evaluation_id column
    op.add_column('evaluation_catalog', sa.Column('adapter_evaluation_id', sa.String(255), nullable=True))

    # Create index for faster lookups
    op.create_index('ix_evaluation_catalog_adapter_evaluation_id', 'evaluation_catalog', ['adapter_evaluation_id'])

    # Populate adapter_evaluation_id for PromptForge evaluations
    # Map name -> adapter_evaluation_id based on PromptForge adapter definitions
    promptforge_mappings = {
        'Prompt Quality Score': 'pf-prompt-quality-score',
        'Cost Efficiency': 'pf-cost-efficiency',
        'Latency Performance': 'pf-latency-performance',
        'Response Completeness': 'pf-response-completeness',
        'Context Utilization': 'pf-context-utilization',
        'Instruction Following': 'pf-instruction-following',
        'Output Format Compliance': 'pf-output-format-compliance',
        'Safety & Toxicity': 'pf-safety-toxicity',
        'Factual Consistency': 'pf-factual-consistency',
        'Semantic Coherence': 'pf-semantic-coherence',
    }

    # Update existing PromptForge evaluations
    connection = op.get_bind()

    # Set adapter_class for all PromptForge evaluations
    connection.execute(
        sa.text(
            "UPDATE evaluation_catalog SET adapter_class = 'PromptForgeAdapter' "
            "WHERE source = 'PROMPTFORGE'"
        )
    )

    # Set adapter_evaluation_id for each PromptForge evaluation
    for name, adapter_id in promptforge_mappings.items():
        connection.execute(
            sa.text(
                "UPDATE evaluation_catalog SET adapter_evaluation_id = :adapter_id "
                "WHERE name = :name AND source = 'PROMPTFORGE'"
            ),
            {"adapter_id": adapter_id, "name": name}
        )

    # Populate adapter_evaluation_id for vendor evaluations
    # Create slugify function for vendor evaluation names
    connection.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION slugify_name(text) RETURNS text AS $$
            SELECT lower(regexp_replace(regexp_replace($1, '[^a-zA-Z0-9\\s-]', '', 'g'), '\\s+', '-', 'g'));
            $$ LANGUAGE SQL IMMUTABLE;
            """
        )
    )

    # Update vendor evaluations with slugified names
    for adapter_class, prefix in [
        ('DeepEvalAdapter', 'deepeval'),
        ('RagasAdapter', 'ragas'),
        ('MLflowAdapter', 'mlflow'),
        ('DeepchecksAdapter', 'deepchecks'),
        ('ArizePhoenixAdapter', 'phoenix'),
    ]:
        connection.execute(
            sa.text(
                f"UPDATE evaluation_catalog SET adapter_evaluation_id = '{prefix}-' || slugify_name(name) "
                f"WHERE adapter_class = '{adapter_class}' AND adapter_evaluation_id IS NULL"
            )
        )


def downgrade() -> None:
    """Remove adapter_evaluation_id column"""
    op.drop_index('ix_evaluation_catalog_adapter_evaluation_id', table_name='evaluation_catalog')
    op.drop_column('evaluation_catalog', 'adapter_evaluation_id')
