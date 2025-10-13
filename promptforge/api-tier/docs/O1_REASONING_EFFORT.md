# OpenAI O1 reasoning_effort Parameter Guide

## Overview
The `reasoning_effort` parameter controls how much thinking time OpenAI O1 reasoning models (o1-preview, o1-mini, o1) use when generating responses. This parameter directly impacts response quality, latency, and cost.

**Important**: O1 models are OpenAI's reasoning models (formerly anticipated as "GPT-5"). They use a different architecture optimized for complex reasoning tasks.

## Parameter Values

**Note**: O1 models support three levels: `low`, `medium`, `high`. Unlike other models, O1 does NOT support `minimal`.

### `low`
**Use Cases:**
- Simple comparisons with 1-2 criteria
- Basic summarization
- Straightforward question answering
- Fast evaluations where speed matters

**Characteristics:**
- ✅ Faster response times
- ✅ Lower reasoning token usage
- ✅ Good cost efficiency
- ⚠️ Moderate analytical depth
- ⚠️ May miss subtle patterns

**Example Tasks:**
- Quick comparison on 1-2 metrics
- Simple classification tasks
- Fast preliminary analysis

### `medium` ⭐ **RECOMMENDED FOR COMPARISONS**
**Use Cases:**
- Multi-stage analysis comparisons
- Quality evaluation across multiple criteria
- Balanced accuracy vs. cost tradeoffs
- Most blind judge evaluations

**Characteristics:**
- ✅ Balanced reasoning depth
- ✅ Reliable quality assessments
- ✅ Good accuracy for most tasks
- ⚠️ Moderate latency (~2-4 seconds)
- ⚠️ Moderate reasoning token cost

**Example Tasks:**
- Compare Call Insights analyses (PromptForge use case)
- Evaluate outputs on multiple criteria (groundedness, faithfulness, completeness)
- Score and rank multiple options

**Why This is Default:**
- Provides sufficient reasoning depth for accurate comparisons
- Balances quality with cost (not too expensive)
- Handles nuanced evaluation across 5 criteria
- Suitable for production use at scale

### `high`
**Use Cases:**
- Complex multi-dimensional analysis
- Critical decision-making tasks
- Research and deep investigation
- Maximum quality requirements

**Characteristics:**
- ✅ Maximum analytical depth
- ✅ Best quality outputs
- ✅ Catches subtle patterns and edge cases
- ❌ Slowest response times (~5-10+ seconds)
- ❌ Highest reasoning token usage
- ❌ Most expensive

**Example Tasks:**
- Complex legal or medical analysis
- Strategic business decisions
- Research requiring deep reasoning
- High-stakes evaluations

## Cost Implications

### Reasoning Tokens
O1 models use "reasoning tokens" during the thinking phase. These tokens are charged at the output token rate.

**Approximate Reasoning Token Usage** (per comparison):
- `low`: 500-1500 tokens
- `medium`: 1500-3000 tokens ⭐
- `high`: 3000-10000+ tokens

**Cost Example** (o1-preview at $0.06/1K output tokens):
- `low`: $0.03 - $0.09 per comparison
- `medium`: $0.09 - $0.18 per comparison ⭐
- `high`: $0.18 - $0.60+ per comparison

### Cost-Benefit Analysis
For PromptForge Call Insights comparisons:
- **low**: May be sufficient for simple 1-2 criteria comparisons
- **medium**: Optimal balance - reliable evaluation at reasonable cost ⭐
- **high**: Best for complex multi-dimensional analysis, 2-3x more expensive but highest quality

## Usage in PromptForge

### API Request Example
```json
{
  "analysis_a_id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_b_id": "550e8400-e29b-41d4-a716-446655440001",
  "judge_model": "o1-preview",
  "judge_reasoning_effort": "medium",
  "evaluation_criteria": [
    "groundedness",
    "faithfulness",
    "completeness",
    "clarity",
    "accuracy"
  ]
}
```

### Default Values by Model
- **o1-preview**: `"medium"` (recommended for full-quality comparisons)
- **o1-mini**: `"medium"` (faster and cheaper than o1-preview)
- **o1**: `"medium"` (full production model when available)

### When to Override Default

**Use `low` when:**
- Running hundreds of comparisons (cost-conscious)
- Using o1-mini for basic evaluations
- Evaluating on 1-2 simple criteria
- Speed matters more than maximum accuracy

**Use `medium` when:** ⭐
- Running production comparisons (DEFAULT - use this!)
- Evaluating on multiple criteria (3-5 dimensions)
- Quality matters more than cost
- Standard use case for most users

**Use `high` when:**
- Quality is absolutely critical
- Comparing highly complex analyses
- Budget allows for premium evaluation
- Research or validation scenarios

## Implementation Details

### Model Parameter Compatibility
Located: `/api-tier/app/services/model_provider.py`

```python
# OpenAI O1 model configuration
"o1-preview": {
    "max_tokens_param": "max_completion_tokens",
    "supports_response_format": False,
    "api_version": "2024-09-01",
    "supported_params": ["max_completion_tokens", "reasoning_effort"],
    "default_overrides": {"temperature": 1.0},
    "reasoning_effort_values": ["low", "medium", "high"],  # No "minimal" for O1
    "default_reasoning_effort": "medium"
}
```

### Validation
Invalid reasoning_effort values automatically fall back to the model's default:
- Invalid: `"super-high"`, `"fast"`, `"quality"`, `"minimal"` (not supported by O1)
- Fallback: `"medium"` (for all O1 models)

### API Schema
Located: `/api-tier/app/schemas/insight_comparison.py`

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

## Compatibility

### Supported Models
- ✅ `o1-preview` (OpenAI O1 preview model)
- ✅ `o1-mini` (OpenAI O1 mini model)
- ✅ `o1` (OpenAI O1 full model when released)

### Unsupported Models (Parameter Ignored)
- ❌ `gpt-4o`, `gpt-4o-mini` (do not support reasoning_effort)
- ❌ `gpt-4`, `gpt-4-turbo`, `gpt-4.1` (legacy and standard GPT models)
- ❌ `claude-*` (Anthropic models use different parameters)

When using non-O1 models, the `reasoning_effort` parameter is safely ignored (no API error).

## Best Practices

### 1. Start with Default
Always start with `"medium"` - it's the recommended default for a reason.

### 2. Profile Your Use Case
If you need to optimize, run A/B tests:
- Compare `medium` vs. `low` on 100 comparisons
- Measure quality difference and cost savings
- Make data-driven decision

### 3. Consider Evaluation Criteria Count
- 1-2 criteria: `"low"` may suffice
- 3-5 criteria: `"medium"` recommended
- 6+ criteria: Consider `"high"`

### 4. Monitor Costs
Track reasoning token usage in judge_trace metadata:
```json
{
  "judge_trace": {
    "model": "gpt-5",
    "total_tokens": 8500,
    "cost": 0.0255,
    "duration_ms": 4200
  }
}
```

### 5. Scale Considerations
For high-volume use cases (1000+ comparisons/day):
- Use `"low"` or `"medium"` by default
- Reserve `"high"` for critical/disputed evaluations
- Consider gpt-5-nano with `"low"` for cost optimization

## Troubleshooting

### Issue: Reasoning tokens higher than expected
**Cause:** Using `"high"` for simple comparisons
**Solution:** Switch to `"medium"` or `"low"`

### Issue: Judge evaluations inconsistent
**Cause:** Using `"minimal"` for multi-criteria comparison
**Solution:** Use `"medium"` (recommended default)

### Issue: API error about reasoning_effort
**Cause:** Invalid value provided or using `"minimal"` with O1 models
**Solution:** Use only: `"low"`, `"medium"`, `"high"` (O1 does NOT support "minimal")

### Issue: Parameter ignored (non-O1 model)
**Cause:** Using reasoning_effort with GPT-4 or Claude models
**Solution:** This is expected - parameter only works with O1 reasoning models

## Related Documentation

- `/api-tier/docs/O1_TEMPERATURE_FIX.md` - O1 temperature restriction
- `/api-tier/docs/MODEL_PARAMETER_COMPATIBILITY.md` - Model parameter rules
- `/api-tier/docs/MULTI_JUDGE_COMPARISON.md` - Comparison system overview

## Date Added
2025-10-13

## Summary
The `reasoning_effort` parameter gives fine-grained control over OpenAI O1 reasoning models' thinking time. For most PromptForge comparisons, use the default `"medium"` value, which provides reliable multi-criteria evaluation at reasonable cost.

**Important**: Use `o1-preview`, `o1-mini`, or `o1` as model names (not "gpt-5" which doesn't exist).
