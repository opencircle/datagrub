# Organization-Scoped Models API

**Issue**: Model dropdowns showing all models (including Gemini) regardless of what the organization has configured
**Solution**: Filter models by organization's configured providers
**Status**: ✅ **IMPLEMENTED**

---

## Problem

The `/api/v1/call-insights/models/available` endpoint was returning ALL models from ALL providers in the database metadata, regardless of whether the organization had configured API keys for those providers.

**User Impact**:
- Playground showing Gemini models even though organization hasn't configured Google API key
- Users could select models they can't actually use
- Confusing UX - why show unavailable models?

---

## Solution

### 1. Organization-Scoped Filtering

**New Logic**:
1. Query `ModelProviderConfig` to get list of configured provider names for the organization
2. Filter `ModelProviderMetadata` to only include those configured providers
3. Return only models from configured providers

**Security**: Organization ID comes from JWT token (`current_user.organization_id`), ensuring users only see their org's configured providers.

---

## API Endpoints

### ✅ Primary Endpoint (Recommended)

**`GET /api/v1/models/available`**

**File**: `/api-tier/app/api/v1/models.py`

**Description**: General-purpose endpoint for all model selection dropdowns

**Use Cases**:
- ✅ Playground model selection
- ✅ Insights multi-stage model selection
- ✅ Custom evaluation model selection

**Request**:
```bash
GET /api/v1/models/available
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "model_id": "gpt-4o",
    "display_name": "GPT-4o",
    "provider": "OpenAI",
    "description": "Multimodal flagship",
    "input_cost": 0.005,
    "output_cost": 0.015,
    "context_window": 128000
  },
  {
    "model_id": "claude-sonnet-4-5-20250929",
    "display_name": "Claude Sonnet 4.5",
    "provider": "Anthropic",
    "description": "Highest intelligence",
    "input_cost": 0.003,
    "output_cost": 0.015,
    "context_window": 200000
  }
]
```

**Key Features**:
- ✅ Organization-scoped (only configured providers)
- ✅ Returns pricing and context window data
- ✅ Includes display names and descriptions
- ✅ Reusable across all MFEs

---

### ✅ Legacy Endpoint (Also Updated)

**`GET /api/v1/call-insights/models/available`**

**File**: `/api-tier/app/api/v1/endpoints/call_insights.py`

**Description**: Originally for Call Insights, now also organization-scoped

**Status**: Updated to use same organization-filtering logic

**Note**: This endpoint is now redundant. Recommend migrating to `/api/v1/models/available`.

---

## Implementation Details

### Database Query Flow

```python
# Step 1: Get configured provider names for organization
configured_providers = await db.execute(
    select(ModelProviderConfig.provider_name).where(
        and_(
            ModelProviderConfig.organization_id == current_user.organization_id,
            ModelProviderConfig.is_active == True
        )
    ).distinct()
)
configured_names = {row[0] for row in configured_providers.all()}
# Example: {'openai', 'anthropic'}

# Step 2: Get metadata only for configured providers
providers = await db.execute(
    select(ModelProviderMetadata).where(
        and_(
            ModelProviderMetadata.provider_type == "llm",
            ModelProviderMetadata.is_active == True,
            ModelProviderMetadata.provider_name.in_(configured_names)  # FILTER HERE
        )
    )
)

# Step 3: Extract models from provider metadata
for provider in providers:
    for field in provider.optional_fields:
        if field.get("name") == "default_model":
            # Extract models, pricing, context windows
            ...
```

---

## Before vs After

### Before ❌

**API Query**:
```sql
SELECT * FROM model_provider_metadata
WHERE provider_type = 'llm' AND is_active = true;
-- Returns: openai, anthropic, google, cohere, etc.
```

**Result**: All models from all providers, regardless of organization configuration

**Example**: Organization has only OpenAI configured, but UI shows:
- ✅ GPT-4o (can use)
- ✅ GPT-4o-mini (can use)
- ❌ Gemini 1.5 Pro (can't use - not configured!)
- ❌ Command R+ (can't use - not configured!)

---

### After ✅

**API Query**:
```sql
-- Step 1: Get configured providers for organization
SELECT DISTINCT provider_name FROM model_provider_configs
WHERE organization_id = '...' AND is_active = true;
-- Returns: ['openai', 'anthropic']

-- Step 2: Get metadata only for those providers
SELECT * FROM model_provider_metadata
WHERE provider_type = 'llm'
  AND is_active = true
  AND provider_name IN ('openai', 'anthropic');
-- Returns: only openai and anthropic
```

**Result**: Only models from configured providers

**Example**: Organization has OpenAI and Anthropic configured, UI shows:
- ✅ GPT-4.1 (can use)
- ✅ GPT-4o (can use)
- ✅ Claude Sonnet 4.5 (can use)
- ✅ Claude Opus 4.1 (can use)
- No Gemini models (correct!)
- No Cohere models (correct!)

---

## UI Integration

### Recommended Approach

All MFEs should use `/api/v1/models/available`:

```typescript
// Example: Playground MFE
const [availableModels, setAvailableModels] = useState([]);

useEffect(() => {
  const fetchModels = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/models/available`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('promptforge_access_token')}`,
          },
        }
      );
      if (response.ok) {
        const models = await response.json();
        setAvailableModels(models);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      // Use fallback if needed
    }
  };

  fetchModels();
}, []);
```

---

## Migration Path

### 1. Insights MFE ✅

**Current**: Already fetches from `/api/v1/call-insights/models/available`
**Action**: Update to use `/api/v1/models/available` (recommended but not required)

**File**: `/ui-tier/mfe-insights/src/components/sections/ExperimentationSection.tsx`

```typescript
// Change from:
const url = `${API_BASE_URL}/api/v1/call-insights/models/available`;

// To:
const url = `${API_BASE_URL}/api/v1/models/available`;
```

---

### 2. Playground MFE 🔄

**Current**: Uses hardcoded `availableModels` array in `mockData.ts`
**Action**: **REQUIRED** - Fetch from API instead

**File**: `/ui-tier/mfe-playground/src/mockData.ts`

**Before**:
```typescript
export const availableModels: Model[] = [
  { id: 'gpt-4.1', name: 'GPT-4.1', provider: 'OpenAI' },
  { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', provider: 'Google' }, // ❌ Shows even if not configured
  // ... hardcoded list
];
```

**After** (recommended refactor):
```typescript
// Remove hardcoded array, fetch from API in component
import { useState, useEffect } from 'react';

const PlaygroundComponent = () => {
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/models/available`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(models => setAvailableModels(models));
  }, []);

  // ... rest of component
};
```

---

### 3. Custom Evaluations 🔄

**File**: Check evaluation creation/configuration components
**Action**: Use `/api/v1/models/available` for model selection dropdowns

---

## Testing

### 1. Verify Organization Filtering

```bash
# Login as admin user
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@promptforge.com","password":"admin123"}' | \
  jq -r '.access_token')

# Get available models
curl -s http://localhost:8000/api/v1/models/available \
  -H "Authorization: Bearer $TOKEN" | jq '.[].provider' | sort | uniq

# Expected: Only providers the organization has configured (e.g., "OpenAI", "Anthropic")
# Should NOT include: "Google AI (Gemini)" if not configured
```

### 2. Test Empty Provider List

```bash
# Remove all provider configs for org (via Models MFE or API)
curl -s http://localhost:8000/api/v1/models/available \
  -H "Authorization: Bearer $TOKEN"

# Expected: []
```

### 3. Test After Adding Provider

```bash
# Add Google provider via Models MFE
# Then fetch models again
curl -s http://localhost:8000/api/v1/models/available \
  -H "Authorization: Bearer $TOKEN" | jq '.[].provider' | sort | uniq

# Expected: Now includes "Google AI (Gemini)"
```

---

## Benefits

### ✅ Accurate Model Selection
- Users only see models they can actually use
- No confusion about unavailable models

### ✅ Organization Isolation
- Each organization sees only their configured providers
- JWT-based authentication ensures security

### ✅ Dynamic Updates
- Add a provider → models appear immediately
- Remove a provider → models disappear immediately
- No code changes needed

### ✅ Consistent Across All MFEs
- Single API endpoint for all model selection use cases
- Playground, Insights, Evaluations all use same endpoint
- Consistent behavior and UX

---

## Files Modified

### API Tier
- ✅ `/api-tier/app/api/v1/models.py` - Added `/available` endpoint
- ✅ `/api-tier/app/api/v1/endpoints/call_insights.py` - Updated to filter by organization

### Documentation
- ✅ `/api-tier/ORGANIZATION_SCOPED_MODELS_API.md` (this file)

### UI Tier (TODO)
- 🔄 `/ui-tier/mfe-insights/src/components/sections/ExperimentationSection.tsx` - Update endpoint (optional)
- 🔄 `/ui-tier/mfe-playground/src/mockData.ts` - Refactor to fetch from API (required)
- 🔄 Custom evaluation components - Update to use `/api/v1/models/available`

---

## Next Steps

1. **Update Playground MFE** to fetch from `/api/v1/models/available` instead of using hardcoded array
2. **Update Insights MFE** to use `/api/v1/models/available` (optional, current endpoint also works)
3. **Update Custom Evaluation components** to use `/api/v1/models/available`
4. **Test thoroughly** with different provider configurations

---

**Generated**: 2025-10-09
**Issue**: Models showing for unconfigured providers (e.g., Gemini without Google API key)
**Resolution**: Organization-scoped filtering based on configured providers in ModelProviderConfig
