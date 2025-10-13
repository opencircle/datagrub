# OpenAI O1 Temperature Restriction Fix

## Issue
When using OpenAI O1 reasoning models (o1-preview, o1-mini, o1) as judge models in comparisons, the API was returning errors:

```
OpenAI API error: {
  "error": {
    "message": "Unsupported value: 'temperature' does not support 0.0 with this model. Only the default (1) value is supported.",
    "type": "invalid_request_error",
    "param": "temperature",
    "code": "unsupported_value"
  }
}
```

## Root Cause
OpenAI's O1 reasoning model family only accepts `temperature=1.0`. Any other temperature value (including 0.0, which is commonly used for deterministic judge evaluations) causes an API error.

The comparison service was defaulting to `judge_temperature=0.0` for deterministic evaluations, which failed for O1 models.

## Solution
Updated `/api-tier/app/services/model_provider.py` to enforce `temperature=1.0` for all O1 reasoning models:

### Configuration Changes

```python
# OpenAI O1 reasoning models (formerly anticipated as GPT-5)
# IMPORTANT: O1 models only support temperature=1.0 (enforced by OpenAI API)
"o1-preview": {
    "max_tokens_param": "max_completion_tokens",
    "supports_response_format": False,  # O1 doesn't support response_format yet
    "api_version": "2024-09-01",
    "supported_params": ["max_completion_tokens", "reasoning_effort"],
    "default_overrides": {"temperature": 1.0},  # Always uses temperature=1.0
    "reasoning_effort_values": ["low", "medium", "high"],
    "default_reasoning_effort": "medium"
},
"o1-mini": {
    "max_tokens_param": "max_completion_tokens",
    "supports_response_format": False,
    "api_version": "2024-09-01",
    "supported_params": ["max_completion_tokens", "reasoning_effort"],
    "default_overrides": {"temperature": 1.0},
    "reasoning_effort_values": ["low", "medium", "high"],
    "default_reasoning_effort": "medium"
},
"o1": {
    "max_tokens_param": "max_completion_tokens",
    "supports_response_format": False,
    "api_version": "2024-09-01",
    "supported_params": ["max_completion_tokens", "reasoning_effort"],
    "default_overrides": {"temperature": 1.0},
    "reasoning_effort_values": ["low", "medium", "high"],
    "default_reasoning_effort": "medium"
},
```

### How It Works

1. **Default Overrides Applied First**: When executing a model, `default_overrides` are applied before any request parameters (line 200-202)
2. **Request Parameters Filtered**: Only parameters in `supported_params` that are NOT in `default_overrides` are added from the request (lines 205-209)
3. **Temperature Always 1.0**: For GPT-5 models, temperature is in `default_overrides` but NOT in `supported_params`, ensuring it's always 1.0

## Impact

### Before Fix
- ❌ Comparisons using O1 judge models failed with temperature errors
- ❌ Users couldn't use O1 models for evaluations
- ❌ Any attempt to set temperature < 1.0 caused API errors

### After Fix
- ✅ O1 models work correctly as judge models
- ✅ Temperature is automatically enforced to 1.0 (no user action needed)
- ✅ Comparison service continues to work with all models
- ✅ Users can select O1 models without errors

## Models Affected

All OpenAI O1 reasoning models now enforce `temperature=1.0`:
- `o1-preview` (O1 preview model)
- `o1-mini` (O1 mini model)
- `o1` (O1 full model)

## Testing

To verify the fix:

1. **Create a comparison with O1 judge model**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/insights/comparisons \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_a_id": "<uuid>",
       "analysis_b_id": "<uuid>",
       "judge_model": "o1-preview",
       "evaluation_criteria": ["groundedness", "faithfulness"]
     }'
   ```

2. **Expected Result**: Comparison completes successfully with O1 using temperature=1.0

3. **Verify in logs**: Check that API calls to OpenAI include `"temperature": 1.0`

## Related Files

- `/api-tier/app/services/model_provider.py` - Model parameter compatibility configuration
- `/api-tier/app/services/insight_comparison_service.py` - Comparison service that uses judge models
- `/api-tier/docs/MODEL_PARAMETER_COMPATIBILITY.md` - Documentation of model parameter rules

## Notes

- **GPT-4.1 and GPT-4o models are NOT affected** - They support full temperature range (0.0-1.0)
- **Claude models are NOT affected** - They support temperature and have different restrictions (no simultaneous temperature + top_p)
- **This is an OpenAI API restriction**, not a PromptForge limitation
- **Important**: O1 models are the actual model names (not "gpt-5")

## Date Fixed
2025-10-13 (Updated to use correct O1 model names)

## Issue Resolution
This fix resolves the error: `"Unsupported value: 'temperature' does not support 0.0 with this model. Only the default (1) value is supported."`
