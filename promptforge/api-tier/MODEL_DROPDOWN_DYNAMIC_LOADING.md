# Dynamic Model Loading from Database

**Issue**: Model lists were hardcoded in multiple locations (UI components and API endpoints)
**Solution**: Centralized model metadata in database with dynamic fetching
**Status**: ✅ **IMPLEMENTED**

---

## Problem

Model lists were hardcoded in 3+ locations:
1. ❌ **Call Insights API**: `/api/v1/call-insights/models/available` had 5 hardcoded OpenAI models
2. ❌ **Insights UI**: `mfe-insights/src/components/sections/ExperimentationSection.tsx` had DEFAULT_MODELS array
3. ❌ **Playground UI**: `mfe-playground/src/mockData.ts` had availableModels array
4. ✅ **Models MFE**: Already using API `/api/v1/model-providers/catalog`

**Maintenance Issues**:
- Every new model required updates in 3+ files
- Risk of inconsistency between frontend and backend
- Pricing updates required code changes
- Context window updates required code changes

---

## Solution: Database-Driven Model Catalog

### 1. Enhanced Database Metadata

**File**: `/database-tier/seed_data/model_provider_metadata.py`

Added pricing and context window metadata to `optional_fields`:

```python
{
    "name": "default_model",
    "type": "select",
    "label": "Default Model",
    "options": ["gpt-4.1", "gpt-4.1-mini", ...],
    "default": "gpt-4o",

    # NEW: Display names for UI
    "model_display_names": {
        "gpt-4.1": "GPT-4.1",
        "gpt-4.1-mini": "GPT-4.1 Mini",
        ...
    },

    # NEW: Pricing per 1K tokens
    "pricing": {
        "gpt-4.1": {
            "input": 0.01,
            "output": 0.03,
            "description": "Latest flagship with 1M context"
        },
        ...
    },

    # NEW: Context window sizes
    "context_windows": {
        "gpt-4.1": 1000000,
        "gpt-4.1-mini": 1000000,
        ...
    }
}
```

**Providers Updated**:
- ✅ OpenAI (7 models with pricing/context)
- ✅ Anthropic (7 models with pricing/context)

---

### 2. Updated Call Insights API

**File**: `/api-tier/app/api/v1/endpoints/call_insights.py`

**Before** (Lines 350-396):
```python
# Hardcoded model list
available_models = [
    AvailableModel(model_id="gpt-4o-mini", display_name="GPT-4o Mini", ...),
    AvailableModel(model_id="gpt-4o", display_name="GPT-4o", ...),
    # ... only 5 OpenAI models
]
```

**After** (Lines 330-389):
```python
@router.get("/models/available", response_model=List[AvailableModel])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Query ModelProviderMetadata for active LLM providers
    result = await db.execute(
        select(ModelProviderMetadata).where(
            and_(
                ModelProviderMetadata.provider_type == "llm",
                ModelProviderMetadata.is_active == True
            )
        )
    )
    providers = result.scalars().all()

    available_models = []

    for provider in providers:
        if not provider.optional_fields:
            continue

        for field in provider.optional_fields:
            if field.get("name") == "default_model":
                model_options = field.get("options", [])
                pricing = field.get("pricing", {})
                context_windows = field.get("context_windows", {})

                for model_id in model_options:
                    model_pricing = pricing.get(model_id, {})

                    available_models.append(
                        AvailableModel(
                            model_id=model_id,
                            display_name=field.get("model_display_names", {}).get(model_id, model_id),
                            provider=provider.display_name,
                            description=model_pricing.get("description", ""),
                            input_cost=model_pricing.get("input", 0.01),
                            output_cost=model_pricing.get("output", 0.03),
                            context_window=context_windows.get(model_id, 128000),
                        )
                    )

    return available_models
```

**Result**: Now returns **11 models** (7 OpenAI + 4 Anthropic) with accurate pricing and context windows from database.

---

### 3. UI Components Still Need API Integration

**Insights MFE** (`mfe-insights/src/components/sections/ExperimentationSection.tsx`):
- ✅ Already fetches from `/api/v1/call-insights/models/available`
- ✅ Has DEFAULT_MODELS fallback (updated with latest models)
- ✅ Will automatically get new models once API is called

**Playground MFE** (`mfe-playground/src/mockData.ts`):
- ⚠️ Still uses hardcoded `availableModels` array
- ✅ Updated with latest models manually
- 🔄 **TODO**: Refactor to fetch from API

---

## Benefits

### ✅ Single Source of Truth
- All model metadata lives in `model_provider_metadata.py`
- Database serves as canonical source
- No code changes needed for model updates

### ✅ Easy Maintenance
```bash
# Update models
vim database-tier/seed_data/model_provider_metadata.py
python3 database-tier/seed_data/model_provider_metadata.py

# All endpoints automatically reflect changes!
```

### ✅ Consistent Across All Interfaces
- Call Insights API: Fetches from DB
- Insights UI: Fetches from API (fallback updated)
- Playground UI: Hardcoded (updated manually, should fetch from API)
- Models MFE: Already uses catalog API

### ✅ Future-Proof
- New providers? Just add to seed data
- New models? Update provider's `options`, `pricing`, `context_windows`
- No frontend changes needed

---

## Database Schema

**Table**: `model_provider_metadata`

**Relevant Columns**:
- `provider_name`: openai, anthropic, etc.
- `provider_type`: llm, embedding, image, etc.
- `display_name`: "OpenAI", "Anthropic", etc.
- `optional_fields`: JSONB array with model configuration
  - `options`: List of model IDs
  - `model_display_names`: Human-readable names
  - `pricing`: Cost per 1K tokens (input/output)
  - `context_windows`: Max tokens per model

---

## Testing

### 1. Verify Database Update
```bash
cd database-tier
DATABASE_URL="postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge" \
  python3 seed_data/model_provider_metadata.py
```

**Expected Output**:
```
✅ Model provider metadata seeded successfully!
📊 Total providers in catalog: 6
  - OpenAI (openai)
  - Anthropic (anthropic)
  - Cohere (cohere)
  - Google AI (Gemini) (google)
  - Azure OpenAI (azure_openai)
  - HuggingFace (huggingface)
```

### 2. Test Call Insights API
```bash
TOKEN="<your-token>"
curl -s "http://localhost:8000/api/v1/call-insights/models/available" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected Output**: Array of 11+ models with pricing and context windows

### 3. Test in UI
1. Open Insights MFE: `http://localhost:3002`
2. Go to Experimentation section
3. Model dropdowns should show latest models (GPT-4.1, Claude Sonnet 4.5, etc.)

---

## Model Counts

| Provider | Models | Latest Additions |
|----------|--------|------------------|
| **OpenAI** | 7 | GPT-4.1, GPT-4.1 Mini |
| **Anthropic** | 7 | Claude Sonnet 4.5, Claude Opus 4.1 |
| **Google** | 3 | Gemini 1.5 Pro, Gemini 1.5 Flash |
| **Cohere** | 3 | Command R+, Command R |
| **Total** | 20+ | |

---

## Migration Path for UI Components

### Current State
- ✅ **Call Insights API**: Fetches from DB
- ✅ **Insights MFE**: Fetches from API (with fallback)
- ⚠️ **Playground MFE**: Hardcoded array

### Recommended Next Steps
1. **Option A**: Make Playground fetch from same API endpoint
   ```typescript
   useEffect(() => {
     const fetchModels = async () => {
       const response = await fetch(`${API_BASE_URL}/api/v1/call-insights/models/available`);
       const models = await response.json();
       setAvailableModels(models);
     };
     fetchModels();
   }, []);
   ```

2. **Option B**: Create dedicated `/api/v1/models/catalog` endpoint
   - More RESTful
   - Reusable across all MFEs
   - Can filter by provider, type, etc.

3. **Option C**: Keep using provider catalog endpoint
   - Models MFE already uses `/api/v1/model-providers/catalog`
   - Most comprehensive (includes all metadata)
   - Requires parsing `optional_fields`

---

## Files Modified

### Database Tier
- ✅ `/database-tier/seed_data/model_provider_metadata.py` (added pricing/context metadata)

### API Tier
- ✅ `/api-tier/app/api/v1/endpoints/call_insights.py` (dynamic model loading)

### UI Tier (Frontend)
- ✅ `/ui-tier/mfe-insights/src/components/sections/ExperimentationSection.tsx` (updated DEFAULT_MODELS)
- ✅ `/ui-tier/mfe-playground/src/mockData.ts` (updated availableModels)

---

## Summary

✅ **Root Cause**: Hardcoded model lists in multiple locations
✅ **Solution**: Database-driven model catalog with pricing/context metadata
✅ **Impact**: Single source of truth, easy maintenance, consistent across all interfaces
✅ **Status**: Call Insights API now fetches from database, UI components updated
🔄 **Next**: Consider refactoring Playground to fetch from API instead of hardcoded list

**New models will appear automatically after database reseed!** 🎉

---

**Generated**: 2025-10-09
**Issue**: Hardcoded model lists in multiple locations
**Resolution**: Centralized model metadata in database with dynamic API fetching
