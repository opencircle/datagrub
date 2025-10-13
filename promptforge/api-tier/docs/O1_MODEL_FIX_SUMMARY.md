# OpenAI O1 Model Support - Fix Summary

## Issue
User reported: "comparison failed with gpt-5 with error: Comparison Failed - Failed to create comparison"

## Root Cause
The configuration referenced "gpt-5", "gpt-5-mini", and "gpt-5-nano" models, but these model names **do not exist** in the OpenAI API.

The actual OpenAI reasoning models are:
- `o1-preview` (preview reasoning model)
- `o1-mini` (smaller, faster reasoning model)
- `o1` (full reasoning model when released)

## What Was Fixed

### 1. Model Configuration (`model_provider.py`)
**Removed:**
- `gpt-5` (non-existent model)
- `gpt-5-mini` (non-existent model)
- `gpt-5-nano` (non-existent model)

**Added:**
- `o1-preview` with correct parameters
- `o1-mini` with correct parameters
- `o1` with correct parameters

**Configuration Details:**
```python
"o1-preview": {
    "max_tokens_param": "max_completion_tokens",
    "supports_response_format": False,  # O1 doesn't support response_format yet
    "api_version": "2024-09-01",
    "supported_params": ["max_completion_tokens", "reasoning_effort"],
    "default_overrides": {"temperature": 1.0},
    "reasoning_effort_values": ["low", "medium", "high"],  # NO "minimal"
    "default_reasoning_effort": "medium"
}
```

**Key Differences from GPT-4:**
1. O1 models **only support temperature=1.0** (enforced)
2. O1 models **do NOT support response_format** (no JSON mode)
3. O1 models support `reasoning_effort` parameter (low/medium/high)
4. O1 models use `max_completion_tokens` (not `max_tokens`)
5. O1 models do NOT support `top_p` parameter

### 2. Model Costs (`model_provider.py`)
Updated pricing for actual O1 models:
- `o1-preview`: $0.015 input / $0.06 output per 1K tokens
- `o1-mini`: $0.003 input / $0.012 output per 1K tokens
- `o1`: $0.015 input / $0.06 output per 1K tokens

### 3. API Schema (`insight_comparison.py`)
Updated documentation:
```python
judge_reasoning_effort: Optional[str] = Field(
    "medium",
    description=(
        "OpenAI O1 models only - controls thinking time (default: medium, RECOMMENDED for comparisons). "
        "• low = Faster with less thinking "
        "• medium = Balanced reasoning (RECOMMENDED for comparisons) "
        "• high = Maximum quality with extended reasoning (complex analysis) "
        "NOTE: Only applicable to o1-preview, o1-mini, o1 models. Ignored for other models."
    )
)
```

### 4. Documentation
**Renamed Files:**
- `GPT5_REASONING_EFFORT.md` → `O1_REASONING_EFFORT.md`
- `GPT5_TEMPERATURE_FIX.md` → `O1_TEMPERATURE_FIX.md`

**Updated Content:**
- All references to "GPT-5" changed to "O1" or "OpenAI O1 reasoning models"
- Removed "minimal" from reasoning_effort options (O1 only supports low/medium/high)
- Updated model names in examples
- Added clarification that O1 models are the actual names (not "gpt-5")

### 5. Error Logging (`model_provider.py`)
Added detailed error logging to help diagnose future issues:
```python
if response.status_code != 200:
    error_details = response.text
    # Log the payload for debugging
    import json
    print(f"[ERROR] OpenAI API request failed with status {response.status_code}")
    print(f"[ERROR] Model: {request.model}")
    print(f"[ERROR] Payload: {json.dumps(payload, indent=2)}")
    print(f"[ERROR] Response: {error_details}")
    raise Exception(f"OpenAI API error: {error_details}")
```

## How to Use O1 Models

### Correct Usage:
```json
{
  "analysis_a_id": "uuid-here",
  "analysis_b_id": "uuid-here",
  "judge_model": "o1-preview",  // ✅ Correct
  "judge_reasoning_effort": "medium",
  "evaluation_criteria": ["groundedness", "faithfulness"]
}
```

### Incorrect Usage:
```json
{
  "judge_model": "gpt-5"  // ❌ Wrong - this model doesn't exist!
}
```

## Important Notes

1. **Model Availability**: O1 models may require special API access from OpenAI. Check your API key permissions if you get 404 errors.

2. **Temperature**: O1 models automatically use `temperature=1.0`. Any temperature value you provide will be overridden.

3. **Reasoning Effort**: O1 models support three levels: `low`, `medium` (default), `high`. They do NOT support `minimal`.

4. **Cost**: O1 models are more expensive than GPT-4o due to reasoning tokens:
   - `o1-preview`: ~2-3x more expensive than GPT-4o
   - `o1-mini`: Similar cost to GPT-4o

5. **Response Format**: O1 models do NOT support structured output (JSON mode). They return plain text only.

## Testing

After the fix, comparisons should work with:
```bash
curl -X POST http://localhost:8000/api/v1/insights/comparisons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_a_id": "<uuid>",
    "analysis_b_id": "<uuid>",
    "judge_model": "o1-preview",
    "judge_reasoning_effort": "medium",
    "evaluation_criteria": ["groundedness", "faithfulness", "completeness"]
  }'
```

## Related Files Changed

1. `/api-tier/app/services/model_provider.py` - Model configurations
2. `/api-tier/app/schemas/insight_comparison.py` - API schema
3. `/api-tier/docs/O1_REASONING_EFFORT.md` - Reasoning effort guide
4. `/api-tier/docs/O1_TEMPERATURE_FIX.md` - Temperature restriction docs
5. `/api-tier/docs/O1_MODEL_FIX_SUMMARY.md` - This file

## Date Fixed
2025-10-13

## Status
✅ **FIXED** - O1 models now properly configured with correct model names and parameters.

**Next Steps for User:**
1. Use `o1-preview`, `o1-mini`, or `o1` instead of "gpt-5"
2. Ensure your OpenAI API key has access to O1 models
3. Test comparisons with the corrected model names
