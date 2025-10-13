# Multi-Judge Model Comparison Feature

## Overview

PromptForge supports running the same analysis comparison with **different judge models** to compare how different LLMs evaluate the same outputs. This enables meta-analysis of judge model behavior and helps users choose the most appropriate judge for their use case.

**Date**: 2025-10-12
**Feature Status**: ✅ Available (built into validation logic)

---

## Use Cases

### 1. **Judge Model Evaluation**
Compare how Claude Sonnet 4.5, GPT-4o, and GPT-4o-mini evaluate the same two analyses.

**Example**:
```
Analysis A: GPT-4o-mini @ temp=0.25
Analysis B: Claude Sonnet 4.5 @ temp=0.25

Run 3 comparisons:
1. Judge: Claude Sonnet 4.5 → Winner: B (detailed reasoning)
2. Judge: GPT-4o → Winner: B (similar reasoning)
3. Judge: GPT-4o-mini → Winner: A (different perspective!)
```

**Insight**: GPT-4o-mini may be biased toward its own outputs or have different evaluation criteria.

### 2. **Cost-Performance Tradeoff**
Determine if expensive judge models provide meaningfully different insights vs cheaper alternatives.

**Example**:
```
Judge A: Claude Sonnet 4.5 ($15 per million tokens)
Judge B: GPT-4o-mini ($0.15 per million tokens)

If verdicts align 95% of the time → use GPT-4o-mini for routine comparisons
If verdicts differ significantly → use Claude Sonnet 4.5 for critical decisions
```

### 3. **Consensus Evaluation**
Run multiple judge models and look for consensus to increase confidence in results.

**Example**:
```
3 judge models evaluate the same comparison:
- Claude Sonnet 4.5: Winner B (confidence: high)
- GPT-4o: Winner B (confidence: high)
- GPT-4o-mini: Winner A (confidence: medium)

Consensus: 2/3 agree on Winner B → high confidence result
```

### 4. **Judge Model Benchmarking**
Systematically compare judge model performance across multiple analysis pairs.

**Example**:
```
Run 10 comparison pairs through 3 judge models:
- Measure agreement rate
- Analyze reasoning quality
- Compare cost per evaluation
- Identify systematic biases
```

---

## How It Works

### Duplicate Prevention Logic

The system prevents **true duplicates** (same analyses + same judge model) while allowing **multi-judge comparisons**:

```python
# Check if comparison already exists
existing_comparison_stmt = select(InsightComparison).where(
    and_(
        InsightComparison.organization_id == self.organization_id,
        or_(
            # Check both orderings: A vs B and B vs A
            and_(
                InsightComparison.analysis_a_id == analysis_a_id,
                InsightComparison.analysis_b_id == analysis_b_id,
            ),
            and_(
                InsightComparison.analysis_a_id == analysis_b_id,
                InsightComparison.analysis_b_id == analysis_a_id,
            ),
        ),
    )
)

# CRITICAL: Also filter by judge model
if judge_model:
    existing_comparison_stmt = existing_comparison_stmt.where(
        InsightComparison.judge_model == judge_model
    )
```

**Result**:
- ✅ Analysis A vs B with Claude Sonnet 4.5 → allowed
- ✅ Analysis A vs B with GPT-4o → allowed (different judge)
- ✅ Analysis A vs B with GPT-4o-mini → allowed (different judge)
- ❌ Analysis A vs B with Claude Sonnet 4.5 (again) → blocked (duplicate)

---

## API Usage

### Endpoint
`POST /api/v1/insights/comparisons`

### Request Body
```json
{
  "analysis_a_id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
  "analysis_b_id": "8bfeb736-4c31-47da-ad3d-77c23474ea24",
  "judge_model": "claude-sonnet-4-5-20250929",
  "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
}
```

### Multi-Judge Workflow

**Step 1: Run first comparison with Claude Sonnet 4.5**
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
    "analysis_b_id": "8bfeb736-4c31-47da-ad3d-77c23474ea24",
    "judge_model": "claude-sonnet-4-5-20250929",
    "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
  }'
```

**Response**:
```json
{
  "comparison_id": "comp-001",
  "overall_winner": "B",
  "overall_reasoning": "Model B outperforms by 19.4% overall...",
  "judge_trace": {
    "model": "claude-sonnet-4-5-20250929",
    "total_tokens": 8500,
    "cost": 0.255
  }
}
```

**Step 2: Re-run same comparison with GPT-4o**
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
    "analysis_b_id": "8bfeb736-4c31-47da-ad3d-77c23474ea24",
    "judge_model": "gpt-4o",
    "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
  }'
```

**Response**:
```json
{
  "comparison_id": "comp-002",
  "overall_winner": "B",
  "overall_reasoning": "Model B demonstrates superior performance...",
  "judge_trace": {
    "model": "gpt-4o",
    "total_tokens": 7800,
    "cost": 0.195
  }
}
```

**Step 3: Re-run with GPT-4o-mini**
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
    "analysis_b_id": "8bfeb736-4c31-47da-ad3d-77c23474ea24",
    "judge_model": "gpt-4o-mini",
    "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
  }'
```

**Response**:
```json
{
  "comparison_id": "comp-003",
  "overall_winner": "A",
  "overall_reasoning": "Model A provides more grounded responses...",
  "judge_trace": {
    "model": "gpt-4o-mini",
    "total_tokens": 6200,
    "cost": 0.015
  }
}
```

**Step 4: Attempt duplicate (should fail)**
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
    "analysis_b_id": "8bfeb736-4c31-47da-ad3d-77c23474ea24",
    "judge_model": "claude-sonnet-4-5-20250929",
    "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
  }'
```

**Response** (400 Bad Request):
```json
{
  "detail": "Comparison already exists between these analyses with judge model 'claude-sonnet-4-5-20250929'. Comparison ID: comp-001"
}
```

---

## Database Schema

Each comparison is stored with the judge model used:

```sql
CREATE TABLE insight_comparisons (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    analysis_a_id UUID NOT NULL,
    analysis_b_id UUID NOT NULL,
    judge_model VARCHAR(255) NOT NULL,        -- e.g., "claude-sonnet-4-5-20250929"
    judge_model_version VARCHAR(255),         -- e.g., "claude-sonnet-4-5-20250929"
    evaluation_criteria TEXT[] NOT NULL,
    overall_winner VARCHAR(10) NOT NULL,      -- 'A', 'B', or 'tie'
    overall_reasoning TEXT NOT NULL,
    stage1_winner VARCHAR(10),
    stage1_scores JSONB,
    stage1_reasoning TEXT,
    stage2_winner VARCHAR(10),
    stage2_scores JSONB,
    stage2_reasoning TEXT,
    stage3_winner VARCHAR(10),
    stage3_scores JSONB,
    stage3_reasoning TEXT,
    judge_trace_id UUID,
    comparison_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for efficient duplicate checking
CREATE INDEX idx_comparison_lookup ON insight_comparisons(
    organization_id,
    analysis_a_id,
    analysis_b_id,
    judge_model
);
```

**Key Point**: The unique constraint is on `(organization_id, analysis_a_id, analysis_b_id, judge_model)`, allowing multiple comparisons for the same analysis pair with different judges.

---

## Frontend Integration

### Comparison History UI Enhancement

The comparison history should show:
1. **Analysis pair** (A vs B titles)
2. **Judge model** used
3. **Winner** and key metrics
4. **Ability to re-run** with different judge

**Example UI**:
```
┌─────────────────────────────────────────────────────────────────┐
│ Comparison History                                              │
├─────────────────────────────────────────────────────────────────┤
│ Analysis A vs Analysis B                                        │
│ ├─ Judge: Claude Sonnet 4.5 → Winner: B (19.4% better)         │
│ ├─ Judge: GPT-4o → Winner: B (17.2% better)                    │
│ └─ Judge: GPT-4o-mini → Winner: A (2.1% better)                │
│                                                                 │
│ [Re-run with different judge ▼]                                │
└─────────────────────────────────────────────────────────────────┘
```

### Re-run Button Implementation

Add a "Re-run with different judge" button in the comparison results view:

```typescript
// ComparisonResults.tsx
const handleRerunWithDifferentJudge = async (newJudgeModel: string) => {
  try {
    const result = await createComparison({
      analysis_a_id: comparison.analysis_a.id,
      analysis_b_id: comparison.analysis_b.id,
      judge_model: newJudgeModel,
      evaluation_criteria: comparison.evaluation_criteria,
    });

    // Navigate to new comparison result
    onComparisonCreated(result.id);
  } catch (error) {
    if (error.message.includes('already exists')) {
      alert('This comparison with this judge model already exists. Please select a different judge model.');
    } else {
      alert(`Failed to create comparison: ${error.message}`);
    }
  }
};
```

---

## Analysis & Insights

### Judge Model Agreement Matrix

After running multiple judges on the same comparison, you can create an agreement matrix:

```
                Claude 4.5  GPT-4o  GPT-4o-mini
Claude 4.5          100%      92%         67%
GPT-4o               92%     100%         71%
GPT-4o-mini          67%      71%        100%
```

**Interpretation**:
- High agreement (90%+): Claude 4.5 ↔ GPT-4o → Strong consensus
- Medium agreement (70-90%): Slight differences in evaluation
- Low agreement (<70%): GPT-4o-mini evaluates differently → investigate why

### Cost-Benefit Analysis

| Judge Model | Cost per Comparison | Agreement with Claude 4.5 | Recommendation |
|-------------|---------------------|---------------------------|----------------|
| Claude Sonnet 4.5 | $0.255 | 100% (baseline) | Use for critical decisions |
| GPT-4o | $0.195 | 92% | Good balance of cost/quality |
| GPT-4o-mini | $0.015 | 67% | Use for quick checks only |

**Conclusion**: GPT-4o offers the best cost-performance tradeoff (92% agreement at 24% lower cost).

### Systematic Bias Detection

Run 20 comparisons with each judge model and analyze patterns:

```python
# Example analysis
claude_verdicts = [comp for comp in comparisons if comp.judge_model == 'claude-sonnet-4-5-20250929']
gpt4o_verdicts = [comp for comp in comparisons if comp.judge_model == 'gpt-4o']
gpt4o_mini_verdicts = [comp for comp in comparisons if comp.judge_model == 'gpt-4o-mini']

# Check for bias toward own outputs
def check_self_bias(verdicts, model_name):
    """Check if judge favors analyses using the same model"""
    self_wins = sum(1 for v in verdicts if v.winner_uses_same_model(model_name))
    return self_wins / len(verdicts)

claude_self_bias = check_self_bias(claude_verdicts, 'claude')
gpt_self_bias = check_self_bias(gpt4o_mini_verdicts, 'gpt-4o-mini')

print(f"Claude self-bias: {claude_self_bias:.1%}")
print(f"GPT-4o-mini self-bias: {gpt_self_bias:.1%}")
```

---

## Best Practices

### 1. **Start with Premium Judge**
Begin with Claude Sonnet 4.5 or GPT-4o for baseline evaluation, then compare cheaper alternatives.

### 2. **Use Same Evaluation Criteria**
Always use the same criteria across judge models for fair comparison:
```json
{
  "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
}
```

### 3. **Look for Consensus**
If 2+ judge models agree, high confidence in the verdict. If they disagree, investigate why.

### 4. **Document Disagreements**
When judge models disagree, document the reasoning differences to understand evaluation philosophies.

### 5. **Batch Processing**
Run multiple judges in parallel for faster results:
```python
import asyncio

async def run_multi_judge_comparison(analysis_a_id, analysis_b_id):
    judges = ['claude-sonnet-4-5-20250929', 'gpt-4o', 'gpt-4o-mini']

    tasks = [
        create_comparison(analysis_a_id, analysis_b_id, judge)
        for judge in judges
    ]

    results = await asyncio.gather(*tasks)
    return results
```

### 6. **Cost Monitoring**
Track cumulative cost across judge models:
```python
total_cost = sum(comp.judge_trace.cost for comp in comparisons)
print(f"Total judge cost: ${total_cost:.2f}")
```

---

## Error Handling

### Duplicate Comparison Error
```json
{
  "status_code": 400,
  "detail": "Comparison already exists between these analyses with judge model 'claude-sonnet-4-5-20250929'. Comparison ID: abc-123"
}
```

**User Action**: Change judge model or view existing comparison.

### Judge Model Not Available
```json
{
  "status_code": 400,
  "detail": "Judge model 'invalid-model' not found. Please check available models."
}
```

**User Action**: Check `/api/v1/models/available` for supported judge models.

### Analysis Not Found
```json
{
  "status_code": 404,
  "detail": "Analysis A not found: 9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4"
}
```

**User Action**: Verify analysis IDs are correct.

---

## Future Enhancements

### 1. **Judge Model Recommendation**
Automatically suggest optimal judge model based on:
- Analysis complexity
- Cost budget
- Required confidence level

### 2. **Consensus Dashboard**
Visualize agreement/disagreement across multiple judges with interactive charts.

### 3. **Judge Model Benchmarking Suite**
Pre-built test suite to evaluate new judge models against established baselines.

### 4. **Automated Multi-Judge Evaluation**
Single API endpoint to run comparison across multiple judges:
```json
POST /api/v1/insights/comparisons/multi-judge
{
  "analysis_a_id": "...",
  "analysis_b_id": "...",
  "judge_models": ["claude-sonnet-4-5-20250929", "gpt-4o", "gpt-4o-mini"]
}
```

### 5. **Meta-Judge Analysis**
Train a meta-judge model to predict which judge model will be most reliable for a given comparison type.

---

## Testing

### Test Scenario 1: Multi-Judge Comparison
```python
async def test_multi_judge_comparison():
    """Test running same comparison with different judges"""
    analysis_a_id = "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4"
    analysis_b_id = "8bfeb736-4c31-47da-ad3d-77c23474ea24"

    # Run with Claude Sonnet 4.5
    comp1 = await create_comparison(
        analysis_a_id, analysis_b_id,
        judge_model="claude-sonnet-4-5-20250929"
    )
    assert comp1.comparison_id is not None

    # Run with GPT-4o (should succeed)
    comp2 = await create_comparison(
        analysis_a_id, analysis_b_id,
        judge_model="gpt-4o"
    )
    assert comp2.comparison_id is not None
    assert comp2.comparison_id != comp1.comparison_id

    # Run with Claude Sonnet 4.5 again (should fail)
    with pytest.raises(ValueError, match="already exists"):
        await create_comparison(
            analysis_a_id, analysis_b_id,
            judge_model="claude-sonnet-4-5-20250929"
        )
```

### Test Scenario 2: Reversed Analysis Order
```python
async def test_reversed_analysis_order():
    """Test that A vs B and B vs A are treated as same comparison"""
    analysis_a_id = "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4"
    analysis_b_id = "8bfeb736-4c31-47da-ad3d-77c23474ea24"

    # Run A vs B with Claude
    comp1 = await create_comparison(
        analysis_a_id, analysis_b_id,
        judge_model="claude-sonnet-4-5-20250929"
    )

    # Run B vs A with Claude (should fail)
    with pytest.raises(ValueError, match="already exists"):
        await create_comparison(
            analysis_b_id, analysis_a_id,  # Reversed order
            judge_model="claude-sonnet-4-5-20250929"
        )

    # Run B vs A with GPT-4o (should succeed - different judge)
    comp2 = await create_comparison(
        analysis_b_id, analysis_a_id,
        judge_model="gpt-4o"
    )
    assert comp2.comparison_id is not None
```

---

## Related Documentation

- **API Docs**: `docs/INSIGHT_COMPARATOR_IMPLEMENTATION_SUMMARY.md`
- **JSON Fixes**: `docs/INSIGHT_COMPARISON_JSON_FIXES.md`
- **Database Schema**: `docs/DATABASE_SCHEMA.md`
- **Model Catalog**: `docs/MODEL_CATALOG.md`

---

*Last Updated: 2025-10-12*
*Feature Version: 1.0*
*API Version: v1*
