# Multi-Judge Comparison - Quick Start Guide

## What is Multi-Judge Comparison?

Run the **same analysis comparison** with **different LLM judge models** to:
- ✅ Compare how different judges evaluate the same outputs
- ✅ Find consensus across multiple judges for high-confidence results
- ✅ Identify judge model biases and preferences
- ✅ Optimize cost by finding cheaper judges that agree with premium ones

---

## Quick Example

**Scenario**: You have two analyses (A and B) and want to see if Claude and GPT-4o agree on which is better.

### Step 1: Run First Comparison (Claude Sonnet 4.5)
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "abc-123",
    "analysis_b_id": "def-456",
    "judge_model": "claude-sonnet-4-5-20250929"
  }'
```

**Result**: Winner: B (19.4% better)

### Step 2: Re-run with Different Judge (GPT-4o)
```bash
curl -X POST 'http://localhost:8000/api/v1/insights/comparisons' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "analysis_a_id": "abc-123",
    "analysis_b_id": "def-456",
    "judge_model": "gpt-4o"
  }'
```

**Result**: Winner: B (17.2% better)

### Step 3: Compare Results
Both judges agree Winner = B → **High confidence!**

---

## Available Judge Models

| Judge Model | Cost per Comparison | Best For |
|-------------|---------------------|----------|
| `claude-sonnet-4-5-20250929` | $0.25 | Critical decisions, detailed reasoning |
| `gpt-4o` | $0.20 | Balanced cost/quality |
| `gpt-4o-mini` | $0.015 | Quick checks, high-volume testing |

---

## Key Rules

### ✅ Allowed
- Same analyses + **different judge model** → Creates new comparison
- Different analyses + same judge model → Creates new comparison

### ❌ Blocked
- Same analyses + **same judge model** → Error: "Comparison already exists"

---

## UI Workflow

### From Comparison History:

1. **Find an existing comparison**
   ```
   Analysis A vs Analysis B
   Judge: Claude Sonnet 4.5 → Winner: B
   ```

2. **Click "Re-run with different judge"**

3. **Select new judge model**
   - Claude Sonnet 4.5 (grayed out - already used)
   - GPT-4o ✓
   - GPT-4o-mini ✓

4. **Click "Run Comparison"**

5. **View results side-by-side**
   ```
   Claude 4.5: Winner B (19.4% better) | $0.255
   GPT-4o:     Winner B (17.2% better) | $0.195
   ```

### From Comparison Selector:

1. **Select two analyses to compare**

2. **Choose judge model** (dropdown shows all available models)

3. **If comparison already exists with that judge:**
   ```
   ⚠️ This comparison already exists with Claude Sonnet 4.5.
   [View Existing] [Choose Different Judge]
   ```

4. **Select different judge model and run**

---

## Common Use Cases

### 1. Verify Important Decisions
```
Question: Should we use Model A or Model B in production?

Steps:
1. Run comparison with Claude Sonnet 4.5 → Winner: B
2. Run comparison with GPT-4o → Winner: B
3. Run comparison with GPT-4o-mini → Winner: A (!)

Result: 2/3 agree on B → Proceed with Model B
```

### 2. Find Cost-Effective Judge
```
Question: Can we use GPT-4o-mini instead of Claude for routine checks?

Steps:
1. Run 10 comparisons with Claude Sonnet 4.5 (baseline)
2. Re-run same 10 with GPT-4o-mini
3. Calculate agreement rate: 95% agreement!

Result: Use GPT-4o-mini for 95% savings with minimal accuracy loss
```

### 3. Detect Judge Bias
```
Question: Does GPT-4o-mini favor its own outputs?

Steps:
1. Create comparison: GPT-4o-mini vs Claude Sonnet 4.5
2. Run with Claude Sonnet 4.5 judge → Winner: Claude
3. Re-run with GPT-4o-mini judge → Winner: GPT-4o-mini (!)

Result: Possible self-bias detected in GPT-4o-mini
```

---

## API Response

### Success (New Comparison)
```json
{
  "comparison_id": "new-comp-123",
  "overall_winner": "B",
  "overall_reasoning": "Model B outperforms...",
  "judge_trace": {
    "model": "gpt-4o",
    "total_tokens": 7800,
    "cost": 0.195
  }
}
```

### Error (Duplicate)
```json
{
  "status_code": 400,
  "detail": "Comparison already exists between these analyses with judge model 'claude-sonnet-4-5-20250929'. Comparison ID: existing-comp-456"
}
```

**Solution**: Change `judge_model` to a different model or view the existing comparison.

---

## Tips & Tricks

### 1. **Batch Process Multiple Judges**
Run all judges in parallel for faster results:
```python
judges = ['claude-sonnet-4-5-20250929', 'gpt-4o', 'gpt-4o-mini']

tasks = [
    create_comparison(analysis_a, analysis_b, judge)
    for judge in judges
]

results = await asyncio.gather(*tasks)
```

### 2. **Look for Consensus**
- 3/3 agree → Very high confidence
- 2/3 agree → High confidence
- 1/3 agree → Low confidence, investigate why

### 3. **Start Premium, Then Optimize**
1. Use Claude Sonnet 4.5 for baseline (most expensive, best quality)
2. Re-run with cheaper models
3. Find the cheapest model that agrees with Claude 95%+ of the time

### 4. **Track Agreement Rate**
```python
def calculate_agreement(comp1, comp2):
    """Calculate agreement between two comparisons"""
    return comp1.overall_winner == comp2.overall_winner

agreement_rate = sum(
    calculate_agreement(claude_comp, gpt_comp)
    for claude_comp, gpt_comp in zip(claude_comps, gpt_comps)
) / len(claude_comps)

print(f"Agreement rate: {agreement_rate:.1%}")
```

---

## Troubleshooting

### Error: "Comparison already exists"
**Cause**: Trying to create duplicate (same analyses + same judge)
**Solution**: Change judge model or view existing comparison

### Error: "Analysis not found"
**Cause**: Invalid analysis ID
**Solution**: Verify analysis IDs from history endpoint

### Error: "Judge model not available"
**Cause**: Invalid or unconfigured judge model
**Solution**: Check `/api/v1/models/available` for supported models

### Different Results from Same Judge
**Cause**: Using `temperature > 0` in judge model
**Solution**: Use `temperature=0.0` for deterministic results

---

## Next Steps

1. **Try it out**: Run your first multi-judge comparison
2. **Compare judges**: Run 5-10 comparisons with different judges
3. **Analyze patterns**: Look for agreement/disagreement trends
4. **Optimize costs**: Find the cheapest judge that maintains quality
5. **Read full docs**: See `docs/MULTI_JUDGE_COMPARISON.md` for advanced usage

---

*Feature Status: ✅ Available Now*
*Last Updated: 2025-10-12*
