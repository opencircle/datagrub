# LLM Metadata Tracking Guide

## Overview

PromptForge captures comprehensive LLM metrics when evaluations involve LLM invocations (e.g., LLM-as-Judge evaluations, vendor evaluations using LLMs). This provides complete observability into token usage, costs, performance, and configuration for all LLM-driven evaluation runs.

## Features

- **Token Usage Tracking**: Input, output, total tokens, plus cache metrics for providers like Anthropic
- **Cost Breakdown**: Detailed cost attribution (input, output, cache) with pricing references
- **Performance Metrics**: Latency, time-to-first-token, throughput measurements
- **Request Configuration**: Temperature, top_p, max_tokens, and other parameters
- **Response Metadata**: Finish reasons, model versions, request IDs
- **Rate Limit Info**: Current limits, remaining quota, reset times
- **Vendor Display**: Clear vendor names (DeepEval, Ragas, MLflow, etc.) in evaluation summaries

## Database Schema

### New Columns

#### `trace_evaluations.llm_metadata` (JSONB)
Comprehensive LLM metrics stored as structured JSON following the `LLMMetadata` schema.

**Indexed**: Yes (GIN index for efficient JSONB queries)

#### `evaluation_catalog.vendor_name` (VARCHAR(100))
Display name of the evaluation vendor for UI presentation.

**Indexed**: Yes (for filtering)
**Examples**: "DeepEval", "Ragas", "MLflow", "Deepchecks", "Arize Phoenix"

## JSON Schema

The `llm_metadata` field follows this structured schema:

```json
{
  "provider": "openai",
  "provider_model": "gpt-4-turbo-2024-04-09",
  "token_usage": {
    "input_tokens": 1234,
    "output_tokens": 567,
    "total_tokens": 1801,
    "cache_read_tokens": null,
    "cache_creation_tokens": null
  },
  "cost_metrics": {
    "input_cost": 0.01234,
    "output_cost": 0.01701,
    "cache_read_cost": null,
    "cache_write_cost": null,
    "total_cost": 0.02935,
    "input_price_per_1k": 0.01,
    "output_price_per_1k": 0.03
  },
  "performance_metrics": {
    "total_duration_ms": 3245.67,
    "time_to_first_token_ms": 234.12,
    "tokens_per_second": 174.8,
    "queue_time_ms": 45.2,
    "processing_time_ms": 3200.47
  },
  "request_parameters": {
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.0,
    "top_p": 1.0,
    "top_k": null,
    "max_tokens": 1024,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop_sequences": null,
    "seed": 42
  },
  "response_metadata": {
    "finish_reason": "stop",
    "model_version": "gpt-4-turbo-2024-04-09",
    "request_id": "req_abc123xyz789",
    "system_fingerprint": "fp_xyz123"
  },
  "rate_limit_info": {
    "requests_limit": 500,
    "requests_remaining": 487,
    "requests_reset_at": "2025-10-06T23:59:00Z",
    "tokens_limit": 150000,
    "tokens_remaining": 148199,
    "tokens_reset_at": "2025-10-06T23:59:00Z"
  },
  "provider_specific": {
    "organization_id": "org-abc123",
    "custom_field": "value"
  },
  "request_timestamp": "2025-10-06T15:30:00.123Z",
  "response_timestamp": "2025-10-06T15:30:03.368Z"
}
```

## Python Schema Classes

### Full Schema (`LLMMetadata`)

Located in `app/schemas/llm_metadata.py`:

```python
from app.schemas.llm_metadata import (
    LLMMetadata,
    LLMTokenUsage,
    LLMCostMetrics,
    LLMPerformanceMetrics,
    LLMRequestParameters,
    LLMResponseMetadata,
    LLMRateLimitInfo,
    FinishReason
)

# Create structured metadata
metadata = LLMMetadata(
    provider="openai",
    provider_model="gpt-4-turbo-2024-04-09",
    token_usage=LLMTokenUsage(
        input_tokens=1234,
        output_tokens=567,
        total_tokens=1801
    ),
    cost_metrics=LLMCostMetrics(
        input_cost=0.01234,
        output_cost=0.01701,
        total_cost=0.02935
    ),
    performance_metrics=LLMPerformanceMetrics(
        total_duration_ms=3245.67,
        tokens_per_second=174.8
    )
)

# Convert to dict for storage
llm_metadata_dict = metadata.model_dump(exclude_none=True)
```

### Flattened Schema (`LLMMetadataFlat`)

For simpler use cases or backward compatibility:

```python
from app.schemas.llm_metadata import LLMMetadataFlat

metadata = LLMMetadataFlat(
    provider="anthropic",
    provider_model="claude-3-opus-20240229",
    input_tokens=1500,
    output_tokens=800,
    total_cost=0.045,
    total_duration_ms=2100.5
)
```

## API Usage

### Trace Details Endpoint

**Endpoint**: `GET /api/v1/traces/{trace_id}/detail`

**Response includes**:
- `evaluations[].vendor_name` - Display name of evaluation vendor
- `evaluations[].llm_metadata` - Full LLM metrics object
- `evaluations[].input_tokens` - Quick access to token count
- `evaluations[].output_tokens` - Quick access to token count
- `evaluations[].total_tokens` - Quick access to token count
- `evaluations[].evaluation_cost` - Quick access to cost

**Example Response**:

```json
{
  "id": "uuid",
  "trace_id": "trace-123",
  "evaluations": [
    {
      "id": "eval-uuid",
      "evaluation_name": "Contextual Relevancy",
      "evaluation_source": "vendor",
      "vendor_name": "DeepEval",
      "score": 0.87,
      "execution_time_ms": 3245.67,
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801,
      "evaluation_cost": 0.02935,
      "llm_metadata": {
        "provider": "openai",
        "provider_model": "gpt-4-turbo-2024-04-09",
        "token_usage": { "input_tokens": 1234, "output_tokens": 567 },
        "cost_metrics": { "total_cost": 0.02935 },
        "performance_metrics": { "total_duration_ms": 3245.67 }
      }
    }
  ]
}
```

## Storing LLM Metadata

### In Evaluation Adapters

When implementing evaluation adapters, populate `llm_metadata` after LLM invocations:

```python
from app.schemas.llm_metadata import LLMMetadata, LLMTokenUsage, LLMCostMetrics

async def run_evaluation(self, trace_data, config):
    # Make LLM call
    response = await llm_client.chat(...)

    # Extract metrics from response
    llm_metadata = LLMMetadata(
        provider="openai",
        provider_model=response.model,
        token_usage=LLMTokenUsage(
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        ),
        cost_metrics=LLMCostMetrics(
            input_cost=calculate_cost(response.usage.prompt_tokens, "input"),
            output_cost=calculate_cost(response.usage.completion_tokens, "output"),
            total_cost=calculate_total_cost(response.usage)
        ),
        performance_metrics=LLMPerformanceMetrics(
            total_duration_ms=response.response_time_ms
        ),
        request_parameters=LLMRequestParameters(
            temperature=config.get("temperature", 0.0),
            max_tokens=config.get("max_tokens", 1024)
        )
    )

    # Return evaluation result with metadata
    return TraceEvaluationResult(
        score=0.87,
        reason="High contextual relevancy",
        llm_metadata=llm_metadata.model_dump(exclude_none=True)
    )
```

### In TraceEvaluation Creation

```python
from app.models.evaluation_catalog import TraceEvaluation
from app.schemas.llm_metadata import LLMMetadata

# Create trace evaluation with LLM metadata
trace_eval = TraceEvaluation(
    trace_id=trace_id,
    evaluation_catalog_id=eval_catalog_id,
    score=result.score,
    passed=result.passed,
    reason=result.reason,
    execution_time_ms=result.execution_time_ms,

    # Legacy fields for quick access
    input_tokens=result.llm_metadata.get("token_usage", {}).get("input_tokens"),
    output_tokens=result.llm_metadata.get("token_usage", {}).get("output_tokens"),
    total_tokens=result.llm_metadata.get("token_usage", {}).get("total_tokens"),
    evaluation_cost=result.llm_metadata.get("cost_metrics", {}).get("total_cost"),

    # Full structured metadata
    llm_metadata=result.llm_metadata
)

db.add(trace_eval)
await db.commit()
```

## Querying LLM Metadata

### Filter by Provider

```python
from sqlalchemy import select
from app.models.evaluation_catalog import TraceEvaluation

# Find all evaluations using OpenAI
query = select(TraceEvaluation).where(
    TraceEvaluation.llm_metadata["provider"].astext == "openai"
)
```

### Filter by Token Usage

```python
# Find expensive evaluations (>5000 tokens)
query = select(TraceEvaluation).where(
    TraceEvaluation.llm_metadata["token_usage"]["total_tokens"].astext.cast(Integer) > 5000
)
```

### Aggregate Cost by Provider

```python
from sqlalchemy import func

# Sum costs by provider
query = select(
    TraceEvaluation.llm_metadata["provider"].astext.label("provider"),
    func.sum(
        TraceEvaluation.llm_metadata["cost_metrics"]["total_cost"].astext.cast(Float)
    ).label("total_cost")
).group_by(
    TraceEvaluation.llm_metadata["provider"].astext
)
```

## Migration

### Running the Migration

```bash
# Navigate to api-tier
cd promptforge/api-tier

# Run migration
alembic upgrade head
```

### Expected Changes

1. **trace_evaluations** table:
   - New column: `llm_metadata` (JSONB, indexed with GIN)

2. **evaluation_catalog** table:
   - New column: `vendor_name` (VARCHAR(100), indexed)

### Rollback

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade g3e7f8g9h0i1
```

## UI Integration

### Displaying Vendor Names

The `vendor_name` field should be displayed prominently in evaluation summaries:

```tsx
// Example React component
<EvaluationCard>
  <VendorBadge>{evaluation.vendor_name || evaluation.evaluation_source}</VendorBadge>
  <EvaluationName>{evaluation.evaluation_name}</EvaluationName>
  <Score>{evaluation.score}</Score>
</EvaluationCard>
```

### Displaying LLM Metrics

```tsx
// Show token usage and cost
{evaluation.llm_metadata && (
  <MetricsPanel>
    <TokenUsage>
      <Label>Tokens:</Label>
      <Value>
        {evaluation.llm_metadata.token_usage.input_tokens} in /
        {evaluation.llm_metadata.token_usage.output_tokens} out
      </Value>
    </TokenUsage>
    <Cost>
      <Label>Cost:</Label>
      <Value>${evaluation.llm_metadata.cost_metrics.total_cost.toFixed(4)}</Value>
    </Cost>
    <Performance>
      <Label>Duration:</Label>
      <Value>{evaluation.llm_metadata.performance_metrics.total_duration_ms}ms</Value>
    </Performance>
  </MetricsPanel>
)}
```

### Expandable Detailed View

```tsx
// Collapsible section with full metadata
<Accordion>
  <AccordionHeader>LLM Details</AccordionHeader>
  <AccordionContent>
    <MetadataViewer data={evaluation.llm_metadata} />
  </AccordionContent>
</Accordion>
```

## Cost Calculation

### Provider Pricing Reference

```python
# app/utils/llm_pricing.py

PRICING_TABLE = {
    "openai": {
        "gpt-4-turbo-2024-04-09": {
            "input_per_1k": 0.01,
            "output_per_1k": 0.03
        },
        "gpt-3.5-turbo": {
            "input_per_1k": 0.0005,
            "output_per_1k": 0.0015
        }
    },
    "anthropic": {
        "claude-3-opus-20240229": {
            "input_per_1k": 0.015,
            "output_per_1k": 0.075
        },
        "claude-3-sonnet-20240229": {
            "input_per_1k": 0.003,
            "output_per_1k": 0.015
        }
    }
}

def calculate_llm_cost(provider: str, model: str, input_tokens: int, output_tokens: int):
    """Calculate cost for LLM usage"""
    pricing = PRICING_TABLE.get(provider, {}).get(model, {})

    input_cost = (input_tokens / 1000) * pricing.get("input_per_1k", 0)
    output_cost = (output_tokens / 1000) * pricing.get("output_per_1k", 0)

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "input_price_per_1k": pricing.get("input_per_1k"),
        "output_price_per_1k": pricing.get("output_per_1k")
    }
```

## Best Practices

### 1. Always Populate LLM Metadata for LLM-based Evaluations

```python
# ✅ GOOD: Comprehensive metadata
result = TraceEvaluationResult(
    score=0.87,
    llm_metadata=full_metadata.model_dump(exclude_none=True)
)

# ❌ BAD: Missing metadata for LLM evaluation
result = TraceEvaluationResult(
    score=0.87
    # No llm_metadata provided!
)
```

### 2. Use Structured Schema Classes

```python
# ✅ GOOD: Type-safe structured data
from app.schemas.llm_metadata import LLMMetadata, LLMTokenUsage

metadata = LLMMetadata(
    provider="openai",
    token_usage=LLMTokenUsage(input_tokens=1234)
)

# ❌ BAD: Raw dict with typos
metadata = {
    "provder": "openai",  # Typo!
    "tokn_usage": {"inpt_tokens": 1234}  # Typo!
}
```

### 3. Exclude None Values

```python
# ✅ GOOD: Clean JSON without null noise
llm_metadata=metadata.model_dump(exclude_none=True)

# ❌ BAD: Cluttered with null values
llm_metadata=metadata.model_dump()
```

### 4. Set Vendor Names in Catalog

```python
# ✅ GOOD: Clear vendor display
eval_catalog = EvaluationCatalog(
    name="Contextual Relevancy",
    source=EvaluationSource.VENDOR,
    adapter_class="DeepEvalAdapter",
    vendor_name="DeepEval"  # Clear display name
)

# ❌ BAD: No vendor name
eval_catalog = EvaluationCatalog(
    name="Contextual Relevancy",
    source=EvaluationSource.VENDOR,
    adapter_class="DeepEvalAdapter"
    # vendor_name not set!
)
```

## Monitoring and Analytics

### Track Evaluation Costs

```sql
-- Total cost by evaluation type
SELECT
    ec.name,
    ec.vendor_name,
    COUNT(*) as execution_count,
    SUM((te.llm_metadata->'cost_metrics'->>'total_cost')::float) as total_cost,
    AVG((te.llm_metadata->'cost_metrics'->>'total_cost')::float) as avg_cost_per_eval
FROM trace_evaluations te
JOIN evaluation_catalog ec ON te.evaluation_catalog_id = ec.id
WHERE te.llm_metadata IS NOT NULL
GROUP BY ec.name, ec.vendor_name
ORDER BY total_cost DESC;
```

### Track Token Usage

```sql
-- Token consumption by provider
SELECT
    te.llm_metadata->>'provider' as provider,
    SUM((te.llm_metadata->'token_usage'->>'input_tokens')::int) as total_input_tokens,
    SUM((te.llm_metadata->'token_usage'->>'output_tokens')::int) as total_output_tokens,
    SUM((te.llm_metadata->'token_usage'->>'total_tokens')::int) as total_tokens
FROM trace_evaluations te
WHERE te.llm_metadata IS NOT NULL
GROUP BY provider
ORDER BY total_tokens DESC;
```

### Performance Monitoring

```sql
-- Average latency by model
SELECT
    te.llm_metadata->>'provider_model' as model,
    COUNT(*) as eval_count,
    AVG((te.llm_metadata->'performance_metrics'->>'total_duration_ms')::float) as avg_latency_ms,
    MAX((te.llm_metadata->'performance_metrics'->>'total_duration_ms')::float) as max_latency_ms
FROM trace_evaluations te
WHERE te.llm_metadata IS NOT NULL
GROUP BY model
ORDER BY avg_latency_ms DESC;
```

## Related Documentation

- [Evaluation Abstraction Layer (EAL) Guide](./EVALUATION_ABSTRACTION_LAYER.md)
- [Trace API Reference](./API_REFERENCE.md#traces)
- [Cost Tracking & Optimization](./COST_TRACKING.md)
- [Evaluation Adapters Development](./ADAPTER_DEVELOPMENT.md)

## Changelog

**v1.0.0** (2025-10-06)
- Initial implementation of LLM metadata tracking
- Added `llm_metadata` JSONB column to `trace_evaluations`
- Added `vendor_name` column to `evaluation_catalog`
- Created comprehensive schema with nested objects
- Implemented GIN indexes for efficient JSONB queries
- Updated trace details API to expose LLM metrics
