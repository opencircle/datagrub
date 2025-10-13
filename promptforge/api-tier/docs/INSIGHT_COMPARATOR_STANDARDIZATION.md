# Insight Comparator Model Selection Standardization

## Overview

The Insight Comparator now uses the **same model selection system** as the Playground for consistency and simplicity.

**Date:** 2025-10-11
**Status:** ✅ Implemented

## Changes Made

### 1. Frontend: ComparisonSelector Component

**Location:** `ui-tier/mfe-insights/src/components/comparison/ComparisonSelector.tsx`

**Before:**
```tsx
// Hardcoded friendly names
const judgeModels = [
  { id: 'claude-sonnet-4.5', label: 'Claude Sonnet 4.5 (Recommended)', cost: '$0.003 / 1K' },
  { id: 'gpt-4o', label: 'GPT-4o', cost: '$0.005 / 1K' },
  { id: 'gpt-4-turbo', label: 'GPT-4 Turbo', cost: '$0.01 / 1K' },
];
```

**After:**
```tsx
// Fetch from same endpoint as Playground
const { data: availableModels = [], isLoading: isLoadingModels } = useQuery<AvailableModel[]>({
  queryKey: ['models', 'available'],
  queryFn: async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/models/available`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },
  staleTime: 60000, // Cache for 1 minute
});

// Sort by cost, mark recommended models
const sortedJudgeModels = availableModels
  .map((model) => ({
    ...model,
    avg_cost: (model.input_cost + model.output_cost) / 2,
    is_recommended:
      model.model_id.includes('claude-sonnet-4') ||
      model.model_id.includes('gpt-4o-mini'),
  }))
  .sort((a, b) => a.avg_cost - b.avg_cost);
```

**Benefits:**
- ✅ **Same API endpoint** as Playground (`/api/v1/models/available`)
- ✅ **Exact API versions** returned (e.g., `"claude-sonnet-4-5-20250929"`)
- ✅ **Org-specific** (only shows models user has configured)
- ✅ **Dynamic pricing** from database
- ✅ **Auto-updates** when providers change

### 2. Backend: InsightComparisonService

**Location:** `api-tier/app/services/insight_comparison_service.py`

**Before:**
```python
from app.services.model_catalog_service import ModelCatalogService

class InsightComparisonService:
    def __init__(self, db: AsyncSession, organization_id: str):
        self.catalog_service = ModelCatalogService(db)

    async def create_comparison(
        self,
        judge_model: str = "claude-sonnet-4.5",  # Friendly name
        ...
    ):
        # Resolve friendly name → exact version
        judge_model_version = await self.catalog_service.get_model_version(judge_model)
        # "claude-sonnet-4.5" → "claude-sonnet-4-5-20250929"
```

**After:**
```python
# No catalog service needed!

class InsightComparisonService:
    def __init__(self, db: AsyncSession, organization_id: str):
        # Removed: self.catalog_service = ModelCatalogService(db)
        pass

    async def create_comparison(
        self,
        judge_model: str = "claude-sonnet-4-5-20250929",  # Exact API version
        ...
    ):
        # Use directly - already exact version from UI
        judge_model_version = judge_model
```

**Benefits:**
- ✅ **No resolution step** needed
- ✅ **Simpler code** - removed catalog dependency
- ✅ **Consistent** with Playground flow
- ✅ **Fewer database queries**

### 3. Database Model: InsightComparison

**Location:** `api-tier/app/models/insight_comparison.py`

**Before:**
```python
judge_model = Column(String(100), nullable=False, default="claude-sonnet-4.5")  # Friendly name for UI
judge_model_version = Column(String(200), nullable=True)  # Exact API version
```

**After:**
```python
judge_model = Column(String(100), nullable=False, default="claude-sonnet-4-5-20250929")  # Exact API version
judge_model_version = Column(String(200), nullable=True)  # Exact API version (kept for compatibility)
```

**Note:** Both columns now store the same value (exact API version). The `judge_model_version` column is kept for backward compatibility with existing comparisons.

## Comparison: Before vs After

| Aspect | Before (Catalog System) | After (Standardized) |
|--------|------------------------|----------------------|
| **UI Model Dropdown** | Hardcoded list | Dynamic from `/api/v1/models/available` |
| **Model IDs** | Friendly names | Exact API versions |
| **Backend Resolution** | Catalog lookup required | Direct use (no lookup) |
| **Consistency** | Different from Playground | Same as Playground ✅ |
| **Org-specific** | No (global catalog) | Yes (per-org configs) ✅ |
| **Pricing** | Hardcoded in UI | Dynamic from database ✅ |
| **Maintenance** | Two systems to update | One system ✅ |

## Data Flow: Playground vs Insight Comparator

### Playground (Already Standardized)

```
1. UI fetches: GET /api/v1/models/available
   Response: [
     {
       "model_id": "claude-sonnet-4-5-20250929",
       "display_name": "Claude Sonnet 4.5",
       "provider": "Anthropic",
       "input_cost": 0.003,
       "output_cost": 0.015
     }
   ]

2. User selects: "Claude Sonnet 4.5" (UI shows display_name)

3. UI sends to backend: { "model": "claude-sonnet-4-5-20250929" } (uses model_id)

4. Backend uses exact version directly for API call ✅
```

### Insight Comparator (Now Standardized)

```
1. UI fetches: GET /api/v1/models/available (SAME endpoint) ✅
   Response: [
     {
       "model_id": "claude-sonnet-4-5-20250929",
       "display_name": "Claude Sonnet 4.5",
       "provider": "Anthropic",
       "input_cost": 0.003,
       "output_cost": 0.015
     }
   ]

2. User selects: "Claude Sonnet 4.5 (Recommended)" (UI shows display_name)

3. UI sends to backend: { "judge_model": "claude-sonnet-4-5-20250929" } (uses model_id) ✅

4. Backend uses exact version directly for API call ✅
```

**Result:** ✅ **Both systems now work identically!**

## Model Selection UI

### Playground Model Dropdown
```tsx
<select value={selectedModel?.id || ''}>
  {availableModels.map((model) => (
    <option key={model.id} value={model.id}>
      {model.name} ({model.costMultiplier}x) - ${model.input_cost}/${model.output_cost}
    </option>
  ))}
</select>
```

### Insight Comparator Judge Model Selection
```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-3">
  {sortedJudgeModels.map((model) => (
    <button
      key={model.model_id}
      onClick={() => setJudgeModel(model.model_id)}
      className={judgeModel === model.model_id ? 'border-[#FF385C]' : ''}
    >
      <span>{model.display_name}</span>
      {model.is_recommended && <span>(Recommended)</span>}
      <div>${model.input_cost.toFixed(5)} / ${model.output_cost.toFixed(5)} per 1K</div>
      <div>{model.provider}</div>
    </button>
  ))}
</div>
```

**Both now use:**
- ✅ `model.model_id` (exact API version) as value
- ✅ `model.display_name` for UI display
- ✅ Dynamic pricing from database

## ModelProviderMetadata Structure

**Single source of truth for all model dropdowns:**

```sql
SELECT
  provider_name,
  jsonb_pretty(optional_fields->'default_model')
FROM model_provider_metadata
WHERE provider_name = 'anthropic';
```

**Returns:**
```json
{
  "name": "default_model",
  "type": "select",
  "label": "Default Model",
  "default": "claude-sonnet-4-5-20250929",
  "options": [
    "claude-sonnet-4-5-20250929",        // ← Exact API versions
    "claude-opus-4-1-20250805",
    "claude-3-5-sonnet-20241022"
  ],
  "model_display_names": {
    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",  // ← Display names
    "claude-opus-4-1-20250805": "Claude Opus 4.1"
  },
  "pricing": {
    "claude-sonnet-4-5-20250929": {
      "input": 0.003,
      "output": 0.015,
      "description": "Highest intelligence"
    }
  }
}
```

## API Endpoint: /api/v1/models/available

**Location:** `api-tier/app/api/v1/endpoints/models.py`

**Implementation:**
```python
@router.get("/available", response_model=List[AvailableModelResponse])
async def get_available_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of available models for the current user's organization

    Returns models from providers that the organization has configured API keys for.
    Used by:
    - Playground model selection
    - Insights multi-stage model selection
    - Insight Comparator judge model selection ← NEW
    """
    # Get configured providers for this org
    configured_providers = await db.execute(
        select(ModelProviderConfig.provider_name).where(
            ModelProviderConfig.organization_id == current_user.organization_id,
            ModelProviderConfig.is_active == True
        )
    )

    # Get metadata for configured providers
    providers = await db.execute(
        select(ModelProviderMetadata).where(
            ModelProviderMetadata.provider_type == "llm",
            ModelProviderMetadata.is_active == True,
            ModelProviderMetadata.provider_name.in_(configured_provider_names)
        )
    )

    # Build response
    for provider in providers:
        for field in provider.optional_fields:
            if field.get("name") == "default_model":
                for model_id in field.get("options", []):
                    available_models.append(
                        AvailableModelResponse(
                            model_id=model_id,  # Exact API version
                            display_name=field.get("model_display_names", {}).get(model_id),
                            provider=provider.display_name,
                            input_cost=field.get("pricing", {}).get(model_id, {}).get("input"),
                            output_cost=field.get("pricing", {}).get(model_id, {}).get("output"),
                        )
                    )

    return available_models
```

## Migration Impact

### No Database Migration Required ✅

The existing `judge_model_version` column can accommodate exact API versions (up to 200 chars).

**Existing comparisons:**
- Created with friendly names (e.g., `"claude-sonnet-4.5"`)
- Stored exact version in `judge_model_version`
- Continue to work normally

**New comparisons:**
- Will use exact versions in both `judge_model` and `judge_model_version`
- Backward compatible with old data

### Example Data Comparison

**Old Comparison (Before Standardization):**
```sql
judge_model          | judge_model_version
---------------------+---------------------------
claude-sonnet-4.5    | claude-sonnet-4-5-20250929
```

**New Comparison (After Standardization):**
```sql
judge_model                   | judge_model_version
------------------------------+---------------------------
claude-sonnet-4-5-20250929    | claude-sonnet-4-5-20250929
```

Both work correctly!

## Testing

### 1. Verify Model Dropdown

**UI:**
1. Navigate to `/insights/comparisons`
2. Check judge model dropdown shows:
   - Dynamic list of models
   - Display names (e.g., "Claude Sonnet 4.5")
   - Pricing per model
   - Provider names
   - "Recommended" badges

**Expected:**
- Should match Playground dropdown style
- Should only show models for configured providers

### 2. Verify Model Selection

**UI:**
1. Select "Claude Sonnet 4.5 (Recommended)"
2. Open browser DevTools → Network tab
3. Create comparison
4. Check request payload

**Expected Request:**
```json
{
  "analysis_a_id": "uuid",
  "analysis_b_id": "uuid",
  "judge_model": "claude-sonnet-4-5-20250929",  // ← Exact API version
  "evaluation_criteria": ["groundedness", "faithfulness", ...]
}
```

### 3. Verify Database Storage

**SQL:**
```sql
SELECT
  judge_model,
  judge_model_version,
  overall_winner,
  created_at
FROM insight_comparisons
ORDER BY created_at DESC
LIMIT 1;
```

**Expected:**
```
judge_model                   | judge_model_version            | overall_winner | created_at
------------------------------+-------------------------------+----------------+-------------------
claude-sonnet-4-5-20250929    | claude-sonnet-4-5-20250929     | A              | 2025-10-11 ...
```

### 4. Verify API Call

**Check trace logs:**
```sql
SELECT
  model,
  input_prompt,
  status,
  tokens_used,
  cost
FROM traces
WHERE metadata->>'source' = 'insight_comparison'
ORDER BY created_at DESC
LIMIT 1;
```

**Expected:**
- `model`: `"claude-sonnet-4-5-20250929"` (exact version used)
- `status`: `"success"`

## Benefits of Standardization

### For Users
1. ✅ **Consistent Experience** - Same model selection across Playground and Comparator
2. ✅ **Accurate Pricing** - See real costs from database, not hardcoded estimates
3. ✅ **Org-Specific** - Only see models you have access to
4. ✅ **Auto-Updates** - New models appear automatically when providers add them

### For Developers
1. ✅ **Single Source of Truth** - `ModelProviderMetadata` for all model data
2. ✅ **Simpler Code** - Removed `ModelCatalogService` dependency
3. ✅ **Fewer Bugs** - No version resolution errors
4. ✅ **Easier Maintenance** - Update provider metadata once, everywhere benefits

### For System
1. ✅ **Fewer Database Queries** - No catalog lookups
2. ✅ **Better Performance** - Direct model usage
3. ✅ **Clearer Architecture** - One system instead of two
4. ✅ **Easier Testing** - Consistent behavior to test

## What Was Removed

### ModelCatalogService Dependency (Insight Comparator Only)

**Note:** The `ModelCatalog` table and service **still exist** and may be useful for:
- Historical model version tracking
- Cross-organization model recommendations
- Model lifecycle management (deprecation dates, etc.)
- Future features that need stable friendly names

**What changed:** Insight Comparator no longer uses it for model selection.

## Future Recommendations

### Option 1: Keep ModelCatalog for Analytics ✅ (Recommended)

**Use Case:** Track which exact model versions were used historically
```sql
-- Example: Find all comparisons using Claude Sonnet 4.5 across versions
SELECT
  judge_model_version,
  COUNT(*) as comparison_count,
  AVG((comparison_metadata->>'total_cost')::float) as avg_cost
FROM insight_comparisons
WHERE judge_model_version LIKE 'claude-sonnet-4-5-%'
GROUP BY judge_model_version
ORDER BY judge_model_version DESC;
```

### Option 2: Deprecate ModelCatalog

If not needed for analytics:
1. Keep table for historical data
2. Remove from new code paths
3. Document as legacy system

## Summary

✅ **Standardization Complete**

- **UI:** Fetches from `/api/v1/models/available`
- **Backend:** Uses exact API versions directly
- **Database:** Stores exact versions in both columns
- **Consistency:** Same system as Playground

**Result:** Simpler, more maintainable, and consistent model selection across the entire application!

---

**Last Updated:** 2025-10-11
**Status:** ✅ Implemented and Documented
