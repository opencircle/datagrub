# Model Catalog System

## Overview

The Model Catalog system provides a centralized registry for AI model version management in PromptForge. It decouples user-friendly model names (shown in the UI) from exact API version identifiers (used for API calls).

## Architecture

### Key Components

1. **ModelCatalog Model** (`app/models/model_catalog.py`)
   - Database table storing model metadata
   - Maps friendly names to exact API versions
   - Tracks capabilities, pricing, lifecycle status

2. **ModelCatalogService** (`app/services/model_catalog_service.py`)
   - Service layer for model lookups
   - Caches model versions for performance
   - Provides filtering and listing capabilities

3. **Integration with InsightComparisonService** (`app/services/insight_comparison_service.py`)
   - Resolves judge model name to version before API calls
   - Stores both friendly name and exact version in database

### Database Schema

#### model_catalog Table
```sql
CREATE TABLE model_catalog (
    id UUID PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,      -- Friendly name (e.g., "claude-sonnet-4.5")
    model_version VARCHAR(200) NOT NULL,          -- Exact API identifier (e.g., "claude-sonnet-4-5-20250929")
    provider_name VARCHAR(100) NOT NULL,          -- openai, anthropic, google, etc.
    model_family VARCHAR(100) NOT NULL,           -- gpt-4, claude-4, etc.
    display_name VARCHAR(255) NOT NULL,           -- Human-readable name
    description TEXT,
    context_window JSON,                          -- {"input": 200000, "output": 8192}
    capabilities JSON,                            -- ["text", "vision", "thinking"]
    pricing JSON,                                 -- {"input": 3.0, "output": 15.0, "currency": "USD"}
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_deprecated BOOLEAN NOT NULL DEFAULT false,
    is_recommended BOOLEAN NOT NULL DEFAULT false,
    release_date TIMESTAMP,
    deprecation_date TIMESTAMP,
    notes TEXT,
    documentation_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);
```

#### insight_comparisons Table Update
```sql
ALTER TABLE insight_comparisons
ADD COLUMN judge_model_version VARCHAR(200);
```

### Seeded Models

The catalog is pre-seeded with 17 models:

**Anthropic Models:**
- Claude 4 Family: sonnet-4.5 ⭐, sonnet-4, opus-4.1, opus-4
- Claude 3 Family: sonnet-3.7, haiku-3, haiku-3.5

**OpenAI Models:**
- GPT-5 Family: gpt-5 ⭐, gpt-5-mini, gpt-5-nano
- GPT-4.1 Family: gpt-4.1, gpt-4.1-mini
- GPT-4o Family: gpt-4o ⭐, gpt-4o-mini ⭐
- GPT-4 Legacy: gpt-4-turbo, gpt-4 (deprecated)
- GPT-3.5: gpt-3.5-turbo

⭐ = Recommended models

## Usage

### Resolving Model Versions

**In Python Service:**
```python
from app.services.model_catalog_service import ModelCatalogService

async def create_comparison(db: AsyncSession, judge_model: str):
    catalog = ModelCatalogService(db)

    # Resolve friendly name to exact API version
    judge_model_version = await catalog.get_model_version(judge_model)
    # "claude-sonnet-4.5" → "claude-sonnet-4-5-20250929"

    # Use exact version for API calls
    response = await anthropic_client.messages.create(
        model=judge_model_version,  # Use exact version
        ...
    )
```

### Listing Available Models

**Get all active models:**
```python
catalog = ModelCatalogService(db)
models = await catalog.list_active_models()
# Returns list of model details sorted by recommendation and release date
```

**Filter by provider:**
```python
openai_models = await catalog.list_active_models(provider_name="openai")
anthropic_models = await catalog.list_active_models(provider_name="anthropic")
```

**Filter by family:**
```python
gpt4_models = await catalog.list_active_models(model_family="gpt-4")
claude4_models = await catalog.list_active_models(model_family="claude-4")
```

### API Response Format

When creating a comparison, both values are stored:
```json
{
  "id": "uuid",
  "judge_model": "claude-sonnet-4.5",           // Friendly name for UI
  "judge_model_version": "claude-sonnet-4-5-20250929",  // Exact version used
  "overall_winner": "A",
  ...
}
```

## Benefits

1. **Version Management**: Update model versions without changing application code
2. **UI Consistency**: Users see stable, friendly names like "claude-sonnet-4.5"
3. **API Accuracy**: API calls use exact versions like "claude-sonnet-4-5-20250929"
4. **Traceability**: Track which exact model version was used for each comparison
5. **Future-Proofing**: Easy to add new models or update versions via database

## Testing

### Verify Catalog Contents
```sql
SELECT model_name, model_version, provider_name, is_active, is_recommended
FROM model_catalog
ORDER BY provider_name, model_family, model_name;
```

### Test Model Resolution
```python
# Should return "claude-sonnet-4-5-20250929"
version = await catalog.get_model_version("claude-sonnet-4.5")

# Should raise ValueError
version = await catalog.get_model_version("invalid-model")
```

### Check Comparison Storage
```sql
SELECT judge_model, judge_model_version, created_at
FROM insight_comparisons
ORDER BY created_at DESC
LIMIT 5;
```

## Updating Model Versions

To update a model version (e.g., when Anthropic releases claude-sonnet-4-5-20251015):

```sql
UPDATE model_catalog
SET model_version = 'claude-sonnet-4-5-20251015',
    updated_at = now()
WHERE model_name = 'claude-sonnet-4.5';
```

No code changes required - all existing references to "claude-sonnet-4.5" will automatically use the new version.

## Adding New Models

To add a new model to the catalog:

```sql
INSERT INTO model_catalog (
    id, model_name, model_version, provider_name, model_family,
    display_name, description, context_window, capabilities, pricing,
    is_active, is_deprecated, is_recommended, release_date,
    documentation_url, notes, created_at, updated_at
)
VALUES (
    gen_random_uuid(),
    'claude-sonnet-5',                          -- Friendly name
    'claude-sonnet-5-20260101',                 -- Exact API version
    'anthropic',
    'claude-5',
    'Claude Sonnet 5',
    'Next generation Claude model',
    '{"input": 300000, "output": 16384}',
    '["text", "vision", "thinking", "computer_use"]',
    '{"input": 4.0, "output": 20.0, "currency": "USD"}',
    true,                                        -- is_active
    false,                                       -- is_deprecated
    true,                                        -- is_recommended
    '2026-01-01',
    'https://docs.anthropic.com/en/docs/about-claude/models',
    'Latest Claude model',
    now(),
    now()
);
```

## Error Handling

The system handles model resolution errors gracefully:

```python
try:
    version = await catalog.get_model_version(judge_model)
except ValueError as e:
    # Returns: "Model not found or inactive: invalid-model"
    raise ValueError(f"Invalid judge model '{judge_model}': {str(e)}")
```

## Migration

The model catalog was added via Alembic migration `u0v1w2x3y4z5`:
- Creates `model_catalog` table
- Adds `judge_model_version` column to `insight_comparisons`
- Seeds 17 initial models
- Backfills existing comparisons (if any)

To apply:
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
./venv/bin/alembic upgrade head
```

## References

- Model Catalog Model: `app/models/model_catalog.py`
- Model Catalog Service: `app/services/model_catalog_service.py`
- Insight Comparison Service: `app/services/insight_comparison_service.py`
- Migration: `alembic/versions/u0v1w2x3y4z5_add_model_catalog.py`
- Anthropic Models: https://docs.anthropic.com/en/docs/about-claude/models
- OpenAI Models: https://platform.openai.com/docs/models
