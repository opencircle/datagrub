# Model Parameter Compatibility System

## Overview

This document describes the parameter compatibility system that handles differences between older and newer OpenAI model APIs. Starting with GPT-5 and GPT-4.1 model families, OpenAI changed the parameter name from `max_tokens` to `max_completion_tokens`.

## Problem

OpenAI models have different parameter compatibility requirements:

### 1. Different Parameter Names

**Legacy Models (GPT-3.5, GPT-4, GPT-4o):**
```json
{
  "model": "gpt-4o-mini",
  "messages": [...],
  "max_tokens": 500  // ✅ Correct parameter
}
```

**New Models (GPT-5, GPT-4.1):**
```json
{
  "model": "gpt-5-nano",
  "messages": [...],
  "max_completion_tokens": 500  // ✅ Correct parameter
}
```

### 2. Different Supported Parameters

**GPT-5 Nano** has unique restrictions:
- ❌ Does NOT support `top_p`
- ✅ Always uses `temperature=1.0` (fixed, cannot be changed)
- ✅ Only supports `max_completion_tokens`

```json
{
  "model": "gpt-5-nano",
  "messages": [...],
  "temperature": 1.0,           // ✅ Fixed at 1.0
  "max_completion_tokens": 500  // ✅ Supported
  // top_p not allowed ❌
}
```

### API Errors

Using wrong parameter names or unsupported parameters results in errors:

**Wrong parameter name:**
```json
{
  "error": {
    "message": "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.",
    "type": "invalid_request_error",
    "param": "max_tokens"
  }
}
```

**Unsupported parameter:**
```json
{
  "error": {
    "message": "Unsupported parameter: 'top_p' is not supported with this model.",
    "type": "invalid_request_error",
    "param": "top_p"
  }
}
```

## Solution

### 1. Model Compatibility Mapping

File: `app/services/model_provider.py`

A compatibility matrix defines which parameter names and features each model family supports:

```python
MODEL_PARAMETER_COMPATIBILITY = {
    # GPT-5 family - New API parameters
    "gpt-5": {
        "max_tokens_param": "max_completion_tokens",
        "supports_response_format": True,
        "api_version": "2024-02-01",
        "supported_params": ["temperature", "top_p", "max_completion_tokens"],
        "default_overrides": {}
    },
    "gpt-5-nano": {
        "max_tokens_param": "max_completion_tokens",
        "supports_response_format": True,
        "api_version": "2024-02-01",
        "supported_params": ["max_completion_tokens"],  # Only max_completion_tokens
        "default_overrides": {"temperature": 1.0}  # Always temperature=1
    },

    # GPT-4o family - Legacy API parameters
    "gpt-4o": {
        "max_tokens_param": "max_tokens",
        "supports_response_format": True,
        "api_version": "2023-12-01",
        "supported_params": ["temperature", "top_p", "max_tokens"],
        "default_overrides": {}
    },

    # ... more models
}
```

**New Fields:**
- `supported_params`: List of parameter names the model accepts
- `default_overrides`: Parameters that are fixed for this model (e.g., gpt-5-nano always uses temperature=1.0)

### 2. Compatibility Lookup Function

The `_get_model_compatibility()` class method handles lookup:

```python
@classmethod
def _get_model_compatibility(cls, model: str) -> Dict[str, Any]:
    """
    Get parameter compatibility settings for a model
    Uses exact match first, then prefix matching for versioned models
    """
    # Try exact match first
    if model in cls.MODEL_PARAMETER_COMPATIBILITY:
        return cls.MODEL_PARAMETER_COMPATIBILITY[model]

    # Try prefix matching for versioned models (e.g., gpt-4-turbo-2024-04-09)
    model_lower = model.lower()
    for model_prefix, config in cls.MODEL_PARAMETER_COMPATIBILITY.items():
        if model_lower.startswith(model_prefix):
            return config

    # Default to legacy parameters for unknown models
    return {
        "max_tokens_param": "max_tokens",
        "supports_response_format": False,
        "api_version": "2023-12-01"
    }
```

**Features:**
- Exact matching for base model names (`gpt-5`, `gpt-4o`)
- Prefix matching for dated versions (`gpt-4-turbo-2024-04-09`)
- Safe fallback to legacy parameters for unknown models

### 3. Dynamic Payload Construction with Parameter Filtering

#### OpenAI Models

The `_execute_openai()` method builds API payloads dynamically, filtering out unsupported parameters:

```python
async def _execute_openai(self, request: ModelExecutionRequest) -> ModelExecutionResult:
    """Execute with OpenAI API using model-specific parameter compatibility"""
    api_key = await self._get_api_key("openai")

    # Get model-specific compatibility settings
    compatibility = self._get_model_compatibility(request.model)

    # Build base payload
    payload = {
        "model": request.model,
        "messages": request.messages,
    }

    # Get supported parameters and overrides for this model
    supported_params = compatibility.get("supported_params", ["temperature", "top_p", "max_tokens"])
    default_overrides = compatibility.get("default_overrides", {})
    max_tokens_param = compatibility["max_tokens_param"]

    # Apply default overrides first (e.g., gpt-5-nano always uses temperature=1)
    for param, value in default_overrides.items():
        payload[param] = value

    # Add request parameters only if supported by the model
    if "temperature" in supported_params and "temperature" not in default_overrides:
        payload["temperature"] = request.temperature

    if "top_p" in supported_params and "top_p" not in default_overrides:
        payload["top_p"] = request.top_p

    # Add max_tokens using model-specific parameter name
    if max_tokens_param in supported_params:
        payload[max_tokens_param] = request.max_tokens

    # Make API call...
```

**Key Features:**
1. **Parameter Filtering**: Only includes parameters the model supports
2. **Default Overrides**: Applies fixed parameter values (e.g., temperature=1 for gpt-5-nano)
3. **Override Priority**: Default overrides take precedence over request parameters

#### Anthropic Models

The `_execute_anthropic()` method handles Anthropic's unique constraint that `temperature` and `top_p` are mutually exclusive:

```python
async def _execute_anthropic(self, request: ModelExecutionRequest) -> ModelExecutionResult:
    """Execute with Anthropic API using parameter compatibility"""
    api_key = await self._get_api_key("anthropic")

    # Get model-specific compatibility settings
    compatibility = self._get_model_compatibility(request.model)

    # Build base payload
    payload: Dict[str, Any] = {
        "model": request.model,
        "messages": messages,
        "max_tokens": request.max_tokens,
    }

    # Get supported parameters
    supported_params = compatibility.get("supported_params", ["temperature", "max_tokens"])

    # Anthropic constraint: temperature and top_p are mutually exclusive
    # Use only temperature (preferred for deterministic judge evaluations)
    if "temperature" in supported_params:
        payload["temperature"] = request.temperature
    # Do NOT add top_p for Anthropic models (causes API error)

    # Make API call...
```

**Anthropic-Specific Features:**
1. **Mutually Exclusive Parameters**: Only `temperature` OR `top_p`, never both
2. **Preferred Parameter**: Uses `temperature` by default (better for judge model evaluations)
3. **Automatic Omission**: `top_p` is automatically excluded from all Claude requests
4. **Error Prevention**: Prevents `invalid_request_error` from Anthropic API

### 4. Database Metadata

File: `database-tier/seed_data/model_provider_metadata.py`

The database seed script includes parameter compatibility metadata for documentation and future UI features:

```python
"parameter_compatibility": {
    "gpt-5": {
        "max_tokens_param": "max_completion_tokens",
        "supports_response_format": True,
        "api_version": "2024-02-01"
    },
    "gpt-5-mini": {
        "max_tokens_param": "max_completion_tokens",
        "supports_response_format": True,
        "api_version": "2024-02-01"
    },
    # ... more models
}
```

## Supported Models

### OpenAI - New API (max_completion_tokens)

| Model | temperature | top_p | max_completion_tokens | Notes |
|-------|------------|-------|----------------------|-------|
| gpt-5 | ✅ | ✅ | ✅ | Full parameter support |
| gpt-5-mini | ✅ | ✅ | ✅ | Full parameter support |
| gpt-5-nano | ❌ (fixed at 1.0) | ❌ | ✅ | Restricted model |
| gpt-4.1 | ✅ | ✅ | ✅ | Full parameter support |
| gpt-4.1-mini | ✅ | ✅ | ✅ | Full parameter support |

### OpenAI - Legacy API (max_tokens)

| Model | temperature | top_p | max_tokens | Notes |
|-------|------------|-------|-----------|-------|
| gpt-4o | ✅ | ✅ | ✅ | Full parameter support |
| gpt-4o-mini | ✅ | ✅ | ✅ | Full parameter support |
| gpt-4-turbo | ✅ | ✅ | ✅ | Full parameter support |
| gpt-4 | ✅ | ✅ | ✅ | Full parameter support |
| gpt-3.5-turbo | ✅ | ✅ | ✅ | Full parameter support |

### Anthropic Claude (All Versions)

| Model | temperature | top_p | max_tokens | Notes |
|-------|------------|-------|-----------|-------|
| claude-sonnet-4-5-* | ✅ | ❌ | ✅ | **CANNOT use temperature AND top_p together** |
| claude-opus-4-* | ✅ | ❌ | ✅ | **CANNOT use temperature AND top_p together** |
| claude-3-5-* | ✅ | ❌ | ✅ | **CANNOT use temperature AND top_p together** |
| claude-3-* | ✅ | ❌ | ✅ | **CANNOT use temperature AND top_p together** |

**⚠️ Critical Anthropic Constraint:** The Anthropic API considers `temperature` and `top_p` **mutually exclusive**. You can use one OR the other, but NOT both. Our implementation uses `temperature` by default and omits `top_p` for all Claude models.

## Adding New Models

To add support for a new model family:

### Step 1: Update MODEL_PARAMETER_COMPATIBILITY

In `app/services/model_provider.py`:

```python
MODEL_PARAMETER_COMPATIBILITY = {
    # ... existing models

    # Example: New OpenAI model
    "gpt-6": {
        "max_tokens_param": "max_completion_tokens",  # or "max_tokens" for legacy
        "supports_response_format": True,
        "api_version": "2024-06-01",
        "supported_params": ["temperature", "top_p", "max_completion_tokens"],
        "default_overrides": {}
    },

    # Example: Model with mutually exclusive parameters (like Anthropic)
    "new-provider-model": {
        "max_tokens_param": "max_tokens",
        "supports_response_format": False,
        "api_version": "2024-01-01",
        "supported_params": ["temperature", "max_tokens"],  # Exclude mutually exclusive param
        "default_overrides": {},
        "mutually_exclusive": ["temperature", "top_p"],  # Documentation only
        "preferred_param": "temperature"
    }
}
```

### Step 2: Update MODEL_COSTS

In `app/services/model_provider.py`:

```python
MODEL_COSTS = {
    # ... existing models
    "gpt-6": {"input": 0.03, "output": 0.09}
}
```

### Step 3: Update Database Seed Script

In `database-tier/seed_data/model_provider_metadata.py`:

1. Add to `options` list
2. Add to `model_display_names`
3. Add to `pricing`
4. Add to `context_windows`
5. Add to `parameter_compatibility`
6. Add to `supported_models`

### Step 4: Run Seed Script

```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
./venv/bin/python ../database-tier/seed_data/model_provider_metadata.py
```

## Testing

### Test with GPT-5 Model
```bash
curl -X POST "http://localhost:8000/api/v1/playground/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, world!",
    "model": "gpt-5-nano",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 100,
      "top_p": 0.9
    }
  }'
```

Expected API payload (uses `max_completion_tokens`):
```json
{
  "model": "gpt-5-nano",
  "messages": [...],
  "temperature": 0.7,
  "top_p": 0.9,
  "max_completion_tokens": 100
}
```

### Test with GPT-4o Model
```bash
curl -X POST "http://localhost:8000/api/v1/playground/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, world!",
    "model": "gpt-4o-mini",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 100,
      "top_p": 0.9
    }
  }'
```

Expected API payload (uses `max_tokens`):
```json
{
  "model": "gpt-4o-mini",
  "messages": [...],
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 100
}
```

## Error Handling

### Unknown Model
If a model is not in the compatibility mapping, it defaults to legacy parameters:
```python
{
    "max_tokens_param": "max_tokens",
    "supports_response_format": False,
    "api_version": "2023-12-01"
}
```

This ensures backwards compatibility with any OpenAI model not explicitly configured.

### Versioned Models
Models with version suffixes (e.g., `gpt-4-turbo-2024-04-09`) are matched by prefix:
- `gpt-4-turbo-2024-04-09` matches `gpt-4-turbo` config
- `gpt-5-preview-20250615` matches `gpt-5` config

## Benefits

1. **Future-proof**: Easy to add new models without breaking existing code
2. **Backwards compatible**: Older models continue working with legacy parameters
3. **Centralized**: All compatibility logic in one place
4. **Database-driven**: Model metadata stored in database for consistency
5. **Self-documenting**: Clear mapping of which models use which parameters
6. **Safe defaults**: Unknown models fall back to legacy parameters
7. **Extensible**: Easy to add new parameter types in the future

## Migration Path

For future OpenAI API changes:

1. Update `MODEL_PARAMETER_COMPATIBILITY` with new parameter names
2. Modify `_execute_openai()` to handle new parameters
3. Update database seed script
4. Run database migration
5. Deploy updated code

No changes required in:
- Frontend code (model selection dropdowns)
- Playground/Insights components
- API endpoints
- Database schema

## References

- OpenAI API Documentation: https://platform.openai.com/docs/api-reference/chat
- Model Pricing: https://openai.com/api/pricing
- GPT-5 Announcement: https://openai.com/gpt-5

---

## Quick Reference: Parameter Compatibility

### OpenAI Models
```python
# GPT-5, GPT-4.1: Use max_completion_tokens
payload = {
    "model": "gpt-5",
    "temperature": 0.7,    # ✅
    "top_p": 0.9,          # ✅
    "max_completion_tokens": 500  # ✅
}

# GPT-5-nano: Special restrictions
payload = {
    "model": "gpt-5-nano",
    "temperature": 1.0,    # ✅ (ALWAYS 1.0, fixed)
    # NO top_p              # ❌
    "max_completion_tokens": 500  # ✅
}

# GPT-4o, GPT-4-turbo, GPT-3.5: Use max_tokens
payload = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,    # ✅
    "top_p": 0.9,          # ✅
    "max_tokens": 500      # ✅ (legacy parameter name)
}
```

### Anthropic Claude Models
```python
# ALL Claude models: temperature OR top_p (NOT BOTH)
payload = {
    "model": "claude-sonnet-4-5-20250929",
    "temperature": 0.7,    # ✅ (preferred)
    # NO top_p              # ❌ CANNOT use with temperature
    "max_tokens": 2000     # ✅
}

# Alternative (use top_p instead of temperature)
payload = {
    "model": "claude-sonnet-4-5-20250929",
    # NO temperature        # ❌ CANNOT use with top_p
    "top_p": 0.9,          # ✅
    "max_tokens": 2000     # ✅
}
```

### Common Errors

**Anthropic Error:**
```json
{
  "type": "invalid_request_error",
  "message": "`temperature` and `top_p` cannot both be specified for this model."
}
```
**Fix:** Remove one of the parameters (our implementation uses `temperature` only).

**OpenAI GPT-5 Error:**
```json
{
  "error": {
    "message": "Unsupported parameter: 'max_tokens' is not supported. Use 'max_completion_tokens'.",
    "type": "invalid_request_error"
  }
}
```
**Fix:** Use `max_completion_tokens` for GPT-5/4.1 families.

---

**Last Updated:** 2025-10-11
**Version:** 1.2
**Changes:** Added Anthropic Claude parameter compatibility (temperature/top_p mutual exclusion)

---

## Appendix: Model Version Mapping (Added 2025-10-11)

### Why Insight Comparator Failed but Playground Worked

**Issue:** Insight Comparator failed with `{"type":"not_found_error","message":"model: claude-sonnet-4.5"}`

**Root Cause:** Two different model identification systems:

#### System 1: ModelProviderMetadata (Used by Playground) ✅
- **Model IDs:** Exact API versions (e.g., `"claude-sonnet-4-5-20250929"`)
- **Location:** `model_provider_metadata.optional_fields['default_model']['options']`
- **Used By:** `/api/v1/models/available` → Playground dropdowns
- **Why it worked:** Returns exact API versions that providers recognize

```json
{
  "model_id": "claude-sonnet-4-5-20250929",  // ← Exact API version
  "display_name": "Claude Sonnet 4.5",       // ← UI-friendly name
  "provider": "Anthropic"
}
```

#### System 2: ModelCatalog (Used by Insight Comparator) ❌ → ✅
- **Model IDs:** Friendly names (e.g., `"claude-sonnet-4.5"`)
- **Location:** `model_catalog` table
- **Used By:** Insight Comparator judge model selection
- **Why it failed initially:** Sent friendly name directly to API
- **Fix:** Added resolution step to convert friendly names to exact versions

### The Fix: Model Version Resolution

**Insight Comparator now resolves friendly names:**

```python
from app.services.model_catalog_service import ModelCatalogService

async def create_comparison(judge_model: str):
    catalog = ModelCatalogService(db)

    # Step 1: Resolve friendly name → exact API version
    judge_model_version = await catalog.get_model_version(judge_model)
    # "claude-sonnet-4.5" → "claude-sonnet-4-5-20250929"

    # Step 2: Use exact version for API calls
    response = await anthropic.messages.create(
        model=judge_model_version,  # ✅ Exact version
        ...
    )

    # Step 3: Store both values for traceability
    comparison.judge_model = judge_model              # UI-friendly
    comparison.judge_model_version = judge_model_version  # Exact version used
```

### Model Identification Comparison

| Aspect | ModelProviderMetadata | ModelCatalog |
|--------|----------------------|--------------|
| **Model IDs** | Exact API versions | Friendly names |
| **Example** | `claude-sonnet-4-5-20250929` | `claude-sonnet-4.5` |
| **Used By** | Playground, Insight Run | Insight Comparator judge |
| **Updates** | When provider configs change | Manual catalog updates |
| **Source** | Provider configuration | Curated central catalog |
| **Org-specific** | ✅ Yes (shows only configured) | ❌ No (global catalog) |

### Recommendation: Use ModelProviderMetadata for All Dropdowns

**Benefits:**
1. ✅ Single source of truth for available models
2. ✅ Automatically syncs with org's configured providers
3. ✅ No version resolution needed (already exact)
4. ✅ Display names already included
5. ✅ Org-specific (only shows models user can access)

**Migration for Insight Comparator UI:**
```tsx
// Current (uses hardcoded friendly name)
const judge_model = "claude-sonnet-4.5";

// Recommended (fetch from /api/v1/models/available)
const response = await fetch('/api/v1/models/available');
const models = await response.json();

// Dropdown shows: "Claude Sonnet 4.5"
// Value sent to API: "claude-sonnet-4-5-20250929"
<select>
  {models.map(m => (
    <option value={m.model_id}>{m.display_name}</option>
  ))}
</select>
```

### Database Schema

**ModelProviderMetadata (Existing):**
```sql
-- Stores exact API versions in JSONB
optional_fields::jsonb
  → default_model
    → options: ["claude-sonnet-4-5-20250929", ...]
    → model_display_names: {"claude-sonnet-4-5-20250929": "Claude Sonnet 4.5"}
```

**ModelCatalog (New):**
```sql
CREATE TABLE model_catalog (
    model_name VARCHAR(100),        -- "claude-sonnet-4.5" (friendly)
    model_version VARCHAR(200),     -- "claude-sonnet-4-5-20250929" (exact)
    provider_name VARCHAR(100),     -- "anthropic"
    is_active BOOLEAN,
    is_recommended BOOLEAN
);
```

### Testing

**Verify ModelProviderMetadata returns exact versions:**
```bash
TOKEN="your-token"
curl "http://localhost:8000/api/v1/models/available" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {model_id, display_name}'
```

**Expected:**
```json
{
  "model_id": "claude-sonnet-4-5-20250929",
  "display_name": "Claude Sonnet 4.5"
}
```

**Verify ModelCatalog resolution:**
```sql
SELECT model_name, model_version
FROM model_catalog
WHERE model_name = 'claude-sonnet-4.5';
```

**Expected:**
```
model_name        | model_version
------------------+---------------------------
claude-sonnet-4.5 | claude-sonnet-4-5-20250929
```

### Summary

- ✅ **Playground works:** Uses exact API versions from ModelProviderMetadata
- ✅ **Insight Comparator now works:** Resolves friendly names via ModelCatalog
- 🔄 **Recommendation:** Migrate Insight Comparator to use ModelProviderMetadata for consistency
- 📊 **Keep ModelCatalog for:** Historical tracking, cross-org recommendations, lifecycle management
