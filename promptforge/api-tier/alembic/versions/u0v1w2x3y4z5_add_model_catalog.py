"""add model catalog

Revision ID: u0v1w2x3y4z5
Revises: n0p1q2r3s4t5
Create Date: 2025-10-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'u0v1w2x3y4z5'
down_revision = 'n0p1q2r3s4t5'
branch_labels = None
depends_on = None


def upgrade():
    # Create model_catalog table
    op.create_table(
        'model_catalog',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('model_name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('model_version', sa.String(200), nullable=False),
        sa.Column('provider_name', sa.String(100), nullable=False, index=True),
        sa.Column('model_family', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('context_window', postgresql.JSON),
        sa.Column('capabilities', postgresql.JSON),
        sa.Column('pricing', postgresql.JSON),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False, index=True),
        sa.Column('is_deprecated', sa.Boolean, default=False, nullable=False),
        sa.Column('is_recommended', sa.Boolean, default=False, nullable=False),
        sa.Column('release_date', sa.DateTime),
        sa.Column('deprecation_date', sa.DateTime, nullable=True),
        sa.Column('notes', sa.Text),
        sa.Column('documentation_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint("model_name != ''", name='ck_model_name_not_empty'),
        sa.CheckConstraint("model_version != ''", name='ck_model_version_not_empty'),
        sa.CheckConstraint("provider_name IN ('openai', 'anthropic', 'google', 'cohere', 'mistral')", name='ck_provider_name'),
    )

    # Add judge_model_version column to insight_comparisons table
    op.add_column('insight_comparisons', sa.Column('judge_model_version', sa.String(200), nullable=True))

    # Seed initial model catalog data
    op.execute("""
        INSERT INTO model_catalog (id, model_name, model_version, provider_name, model_family, display_name, description, context_window, capabilities, pricing, is_active, is_deprecated, is_recommended, release_date, documentation_url, notes, created_at, updated_at)
        VALUES
        -- Anthropic Claude 4 Family
        (gen_random_uuid(), 'claude-sonnet-4.5', 'claude-sonnet-4-5-20250929', 'anthropic', 'claude-4', 'Claude Sonnet 4.5', 'Most intelligent model for complex agents and coding', '{"input": 200000, "output": 8192}', '["text", "vision", "thinking", "computer_use"]', '{"input": 3.0, "output": 15.0, "currency": "USD"}', true, false, true, '2025-09-29', 'https://docs.anthropic.com/en/docs/about-claude/models', 'Recommended for judge model comparisons', now(), now()),
        (gen_random_uuid(), 'claude-sonnet-4', 'claude-sonnet-4-20250514', 'anthropic', 'claude-4', 'Claude Sonnet 4', 'Strong performance for complex tasks', '{"input": 200000, "output": 8192}', '["text", "vision", "thinking"]', '{"input": 3.0, "output": 15.0, "currency": "USD"}', true, false, false, '2025-05-14', 'https://docs.anthropic.com/en/docs/about-claude/models', NULL, now(), now()),
        (gen_random_uuid(), 'claude-opus-4.1', 'claude-opus-4-1-20250805', 'anthropic', 'claude-4', 'Claude Opus 4.1', 'Highest intelligence for most difficult tasks', '{"input": 200000, "output": 16384}', '["text", "vision", "thinking"]', '{"input": 15.0, "output": 75.0, "currency": "USD"}', true, false, false, '2025-08-05', 'https://docs.anthropic.com/en/docs/about-claude/models', 'Most capable but expensive', now(), now()),
        (gen_random_uuid(), 'claude-opus-4', 'claude-opus-4-20250514', 'anthropic', 'claude-4', 'Claude Opus 4', 'Top-tier intelligence', '{"input": 200000, "output": 8192}', '["text", "vision", "thinking"]', '{"input": 15.0, "output": 75.0, "currency": "USD"}', true, false, false, '2025-05-14', 'https://docs.anthropic.com/en/docs/about-claude/models', NULL, now(), now()),

        -- Anthropic Claude 3 Family
        (gen_random_uuid(), 'claude-sonnet-3.7', 'claude-3-7-sonnet-20250219', 'anthropic', 'claude-3', 'Claude Sonnet 3.7', 'Enhanced Claude 3 Sonnet', '{"input": 200000, "output": 8192}', '["text", "vision"]', '{"input": 3.0, "output": 15.0, "currency": "USD"}', true, false, false, '2025-02-19', 'https://docs.anthropic.com/en/docs/about-claude/models', NULL, now(), now()),
        (gen_random_uuid(), 'claude-3-haiku', 'claude-3-haiku-20240307', 'anthropic', 'claude-3', 'Claude 3 Haiku', 'Fast and cost-effective', '{"input": 200000, "output": 4096}', '["text", "vision"]', '{"input": 0.25, "output": 1.25, "currency": "USD"}', true, false, false, '2024-03-07', 'https://docs.anthropic.com/en/docs/about-claude/models', 'Good for high-volume tasks', now(), now()),
        (gen_random_uuid(), 'claude-haiku-3.5', 'claude-3-5-haiku-20241022', 'anthropic', 'claude-3', 'Claude Haiku 3.5', 'Enhanced Haiku with better speed', '{"input": 200000, "output": 8192}', '["text", "vision"]', '{"input": 1.0, "output": 5.0, "currency": "USD"}', true, false, false, '2024-10-22', 'https://docs.anthropic.com/en/docs/about-claude/models', NULL, now(), now()),

        -- OpenAI GPT-5 Family
        (gen_random_uuid(), 'gpt-5', 'gpt-5', 'openai', 'gpt-5', 'GPT-5', 'OpenAI flagship reasoning model', '{"input": 128000, "output": 16384}', '["text", "vision", "reasoning", "function_calling"]', '{"input": 20.0, "output": 60.0, "currency": "USD"}', true, false, true, '2025-01-01', 'https://platform.openai.com/docs/models/gpt-5', 'Uses max_completion_tokens parameter', now(), now()),
        (gen_random_uuid(), 'gpt-5-mini', 'gpt-5-mini', 'openai', 'gpt-5', 'GPT-5 Mini', 'Efficient GPT-5 variant', '{"input": 128000, "output": 16384}', '["text", "vision", "reasoning", "function_calling"]', '{"input": 4.0, "output": 12.0, "currency": "USD"}', true, false, false, '2025-01-01', 'https://platform.openai.com/docs/models/gpt-5', 'Uses max_completion_tokens parameter', now(), now()),
        (gen_random_uuid(), 'gpt-5-nano', 'gpt-5-nano', 'openai', 'gpt-5', 'GPT-5 Nano', 'Ultra-fast GPT-5 variant', '{"input": 128000, "output": 16384}', '["text", "function_calling"]', '{"input": 0.1, "output": 0.4, "currency": "USD"}', true, false, false, '2025-01-01', 'https://platform.openai.com/docs/models/gpt-5', 'Always uses temperature=1, only supports max_completion_tokens', now(), now()),

        -- OpenAI GPT-4.1 Family
        (gen_random_uuid(), 'gpt-4.1', 'gpt-4.1', 'openai', 'gpt-4', 'GPT-4.1', 'Enhanced GPT-4 with better reasoning', '{"input": 128000, "output": 16384}', '["text", "vision", "function_calling"]', '{"input": 10.0, "output": 30.0, "currency": "USD"}', true, false, false, '2025-01-01', 'https://platform.openai.com/docs/models/gpt-4', 'Uses max_completion_tokens parameter', now(), now()),
        (gen_random_uuid(), 'gpt-4.1-mini', 'gpt-4.1-mini', 'openai', 'gpt-4', 'GPT-4.1 Mini', 'Smaller efficient GPT-4.1', '{"input": 128000, "output": 16384}', '["text", "vision", "function_calling"]', '{"input": 2.0, "output": 6.0, "currency": "USD"}', true, false, false, '2025-01-01', 'https://platform.openai.com/docs/models/gpt-4', 'Uses max_completion_tokens parameter', now(), now()),

        -- OpenAI GPT-4o Family
        (gen_random_uuid(), 'gpt-4o', 'gpt-4o', 'openai', 'gpt-4', 'GPT-4o', 'Optimized GPT-4', '{"input": 128000, "output": 16384}', '["text", "vision", "function_calling"]', '{"input": 5.0, "output": 15.0, "currency": "USD"}', true, false, true, '2024-08-06', 'https://platform.openai.com/docs/models/gpt-4o', 'Uses legacy max_tokens parameter', now(), now()),
        (gen_random_uuid(), 'gpt-4o-mini', 'gpt-4o-mini', 'openai', 'gpt-4', 'GPT-4o Mini', 'Cost-effective GPT-4o', '{"input": 128000, "output": 16384}', '["text", "vision", "function_calling"]', '{"input": 0.15, "output": 0.6, "currency": "USD"}', true, false, true, '2024-07-18', 'https://platform.openai.com/docs/models/gpt-4o', 'Uses legacy max_tokens parameter, great for development', now(), now()),

        -- OpenAI GPT-4 Legacy
        (gen_random_uuid(), 'gpt-4-turbo', 'gpt-4-turbo', 'openai', 'gpt-4', 'GPT-4 Turbo', 'Faster GPT-4', '{"input": 128000, "output": 4096}', '["text", "vision", "function_calling"]', '{"input": 10.0, "output": 30.0, "currency": "USD"}', true, false, false, '2024-04-09', 'https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4', 'Uses legacy max_tokens parameter', now(), now()),
        (gen_random_uuid(), 'gpt-4', 'gpt-4', 'openai', 'gpt-4', 'GPT-4', 'Original GPT-4', '{"input": 8192, "output": 8192}', '["text", "function_calling"]', '{"input": 30.0, "output": 60.0, "currency": "USD"}', false, true, false, '2023-03-14', 'https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4', 'Deprecated - use GPT-4o instead', now(), now()),

        -- OpenAI GPT-3.5
        (gen_random_uuid(), 'gpt-3.5-turbo', 'gpt-3.5-turbo', 'openai', 'gpt-3.5', 'GPT-3.5 Turbo', 'Fast and inexpensive', '{"input": 16385, "output": 4096}', '["text", "function_calling"]', '{"input": 1.5, "output": 2.0, "currency": "USD"}', true, false, false, '2023-03-01', 'https://platform.openai.com/docs/models/gpt-3-5-turbo', 'Good for simple tasks', now(), now());
    """)

    # Backfill judge_model_version for existing comparisons
    op.execute("""
        UPDATE insight_comparisons
        SET judge_model_version = mc.model_version
        FROM model_catalog mc
        WHERE insight_comparisons.judge_model = mc.model_name
        AND insight_comparisons.judge_model_version IS NULL;
    """)


def downgrade():
    # Remove judge_model_version column
    op.drop_column('insight_comparisons', 'judge_model_version')

    # Drop model_catalog table
    op.drop_table('model_catalog')
