# Insight Comparison Tabular Format

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Status**: ✅ Production Ready

---

## Overview

The Insight Comparison feature now generates **structured tabular analysis** instead of dense paragraphs, making it easier to scan and understand model performance differences.

## Format Specification

### Table Structure

The judge model generates a markdown table with these columns:

| Column | Description | Example Values |
|--------|-------------|----------------|
| **Category** | Grouping of related metrics | Stage 1: Fact Extraction, Cost Analysis, Recommendation |
| **Parameter** | Specific metric being compared | Groundedness, Avg Score, Total Cost, Winner |
| **Model A** | Value for baseline model | 0.85, $0.0020, ❌ |
| **Model B** | Value for comparison model | 0.92, $0.0021, ✅ |
| **Comparative Delta** | Percentage or absolute difference | +8.2%, +$0.0001, +19.4% quality |
| **Commentary** | Human-readable explanation | "Model B better grounded facts" |

### Required Sections

#### 1. Stage-wise Performance (3 sections)

Each DTA pipeline stage includes:
- Individual criterion scores (Groundedness, Faithfulness, Completeness, Clarity, Accuracy)
- Average score per stage
- Stage weight (30%, 35%, 35%)
- Weighted score contribution
- Winner indication

**Example:**
```markdown
| **Stage 1: Fact Extraction** | Groundedness | 0.85 | 0.92 | +8.2% | Model B better grounded facts in transcript |
| | Faithfulness | 0.90 | 0.95 | +5.6% | Model B more faithful to source material |
| | **Avg Score** | **0.840** | **0.902** | **+7.4%** | Model B wins Stage 1 |
| | Weight | 30% | 30% | — | Stage 1 contributes 30% to overall |
| | Weighted Score | 0.252 | 0.271 | +7.5% | Stage 1 weighted contribution |
```

#### 2. Overall Quality

Aggregates weighted scores across all stages:
```markdown
| **Overall Quality** | Weighted Total | **0.753** | **0.899** | **+19.4%** | Model B superior overall quality |
| | Quality Grade | B | A | +1 grade | Model B significantly better |
```

#### 3. Cost Analysis

Shows token usage and cost comparison:
```markdown
| **Cost Analysis** | Total Tokens | 12,453 | 13,821 | — | Token usage comparison |
| | Total Cost | $0.00120 | $0.00121 | +$0.00001 (+0.8%) | Model B costs marginally more |
| | Cost Efficiency | Fair | Excellent | — | Model B better value for quality |
```

#### 4. Critical Findings

Highlights risks and quality issues:
```markdown
| **Critical Findings** | Risk Level | ⚠️ HIGH | ✅ LOW | — | Model A unreliable in Stage 2 |
| | Hallucination | Detected | None | — | Model A generated unfounded insights |
| | Consistency | Inconsistent | Consistent | — | Model B reliable across all stages |
| | Business Impact | Risky | Trustworthy | — | Model A could lead to poor decisions |
```

**⚠️ Warning Triggers:**
- Any score below 0.60 → Flag as "⚠️ [Issue Type]"
- Hallucination detected → "⚠️ Model X hallucination detected"
- Large score variance → "⚠️ Inconsistent performance"

#### 5. Recommendation

Final verdict with winner indicators:
```markdown
| **Recommendation** | Winner | ❌ | ✅ | +19.4% quality | Model B strongly recommended |
| | Use Case | Not recommended | Production ready | — | Model B suitable for all scenarios |
| | Justification | Unreliable insights | Consistent quality | — | Model B eliminates hallucination risk |
```

### Summary Section

After the table, a 2-3 sentence summary:

```markdown
## Summary

**Model B outperforms by 19.4% overall** with consistent, reliable performance across all stages. The cost difference of +$0.00001 (+0.8%) is negligible compared to the quality gain.

**Primary Deciding Factor:** Model A's severe failure in Stage 2 (Insights) with groundedness scores of 0.45 and accuracy of 0.55 indicates hallucination and unreliable insights — a critical failure mode for business decision-making. Model B eliminates this risk while delivering superior results in all stages.

**Recommendation:** Use Model B exclusively. The quality improvement (+19.4%) and elimination of hallucination risk far outweigh the marginal cost increase.
```

---

## Visual Indicators

| Indicator | Meaning | Usage |
|-----------|---------|-------|
| ✅ | Winner / Recommended | Final recommendation, low risk |
| ❌ | Not recommended | Poor performance or high risk |
| ⚠️ | Warning / Critical issue | Scores below 0.60, hallucination detected |
| — | Not applicable | No meaningful comparison |
| **Bold** | Emphasis | Section headers, aggregate scores |

---

## Implementation Details

### Backend Changes

**File**: `promptforge/api-tier/app/prompts/judge_comparison_prompts.py`

The `OVERALL_VERDICT_PROMPT` now:
1. Instructs judge model to generate structured markdown tables
2. Requires specific table columns: Category | Parameter | Model A | Model B | Comparative Delta | Commentary
3. Mandates all required sections (stages, cost, findings, recommendation)
4. Enforces visual indicators (✅/❌/⚠️)
5. Requires concise summary after table

**File**: `promptforge/api-tier/app/services/insight_comparison_service.py`

Cost difference formatting updated:
```python
# Before
cost_diff_str = f"+${cost_diff:.4f}" if cost_diff > 0 else f"-${abs(cost_diff):.4f}"

# After (includes percentage)
cost_diff_percent = ((cost_diff / cost_a) * 100) if cost_a > 0 else 0
cost_diff_str = f"+${cost_diff:.5f} (+{cost_diff_percent:.1f}%)" if cost_diff > 0 else f"-${abs(cost_diff):.5f} ({cost_diff_percent:.1f}%)"
```

### Frontend Changes

**File**: `promptforge/ui-tier/mfe-insights/src/components/comparison/ComparisonResults.tsx`

1. **Added markdown rendering:**
```typescript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const renderMarkdown = (markdown: string): string => {
  const rawHtml = marked(markdown, { breaks: true, gfm: true }) as string;
  return DOMPurify.sanitize(rawHtml);
};
```

2. **Replaced plain text with styled markdown:**
```tsx
<div
  className="prose prose-sm max-w-none text-neutral-700
             prose-headings:text-neutral-800 prose-headings:font-bold
             prose-table:border-collapse prose-table:w-full
             prose-th:bg-neutral-100 prose-th:border prose-th:border-neutral-300 prose-th:px-4 prose-th:py-2
             prose-td:border prose-td:border-neutral-200 prose-td:px-4 prose-td:py-2
             prose-tr:even:bg-neutral-50
             prose-strong:text-neutral-900 prose-strong:font-bold"
  dangerouslySetInnerHTML={{ __html: renderMarkdown(comparison.overall_reasoning) }}
/>
```

**Dependencies Added:**
```bash
npm install marked dompurify
npm install --save-dev @types/dompurify
```

---

## Benefits

### Before (Dense Paragraph)
```
Model B demonstrated significantly superior performance across the two most critical stages,
winning decisively in Stage 2 (Insights) and Stage 3 (Summary), while Model A only won Stage 1
(Fact Extraction). **Quality Analysis by Stage:** - Stage 1 (30% weight): Model A won with
0.934 avg vs Model B's 0.856 avg (+9.1% better). Model A showed stronger fact extraction...
[300+ words of continuous text]
```

**Issues:**
- Hard to scan quickly
- Difficult to compare specific metrics
- No visual hierarchy
- Tedious to find key information

### After (Tabular Format)

**Benefits:**
- ✅ **Scannable**: Find specific metrics instantly
- ✅ **Visual hierarchy**: Tables organize information logically
- ✅ **Quick comparison**: Side-by-side model values
- ✅ **Clear deltas**: Percentage differences highlighted
- ✅ **Risk indicators**: Warnings (⚠️) stand out immediately
- ✅ **Concise summary**: Key takeaways at a glance

---

## Testing

### Manual Testing Steps

1. **Create two analyses** with same transcript but different models
2. **Run comparison** via UI or API
3. **Verify table structure**:
   - All 5 sections present (Stages 1-3, Cost, Findings, Recommendation)
   - All required columns rendered
   - Visual indicators (✅/❌/⚠️) display correctly
4. **Check calculations**:
   - Weighted scores add up correctly
   - Percentage deltas accurate
   - Cost difference includes percentage
5. **Verify summary**:
   - Appears after table
   - Includes overall percentage, cost impact, primary deciding factor

### API Testing

```bash
# Create comparison
curl -X POST "http://localhost:8000/api/v1/insight-comparisons" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_a_id": "uuid-of-analysis-a",
    "analysis_b_id": "uuid-of-analysis-b",
    "judge_model": "claude-sonnet-4-5-20250929",
    "judge_temperature": 0.0
  }'

# Verify response contains markdown table
jq '.overall_reasoning' response.json
```

### Expected Output

```markdown
## Comparative Analysis

| Category | Parameter | Model A | Model B | Comparative Delta | Commentary |
|----------|-----------|---------|---------|-------------------|------------|
| **Stage 1: Fact Extraction** | Groundedness | 0.85 | 0.92 | +8.2% | ... |
...
```

---

## Maintenance

### Updating Table Format

If table structure changes:

1. **Update prompt** in `judge_comparison_prompts.py`
2. **Update this documentation**
3. **Update frontend CSS** if new visual indicators added
4. **Test end-to-end** with real comparisons

### Adding New Sections

To add new analysis sections (e.g., "Latency Analysis"):

1. Add section to `OVERALL_VERDICT_PROMPT` example
2. Update "Required Sections" in this doc
3. Add corresponding test cases
4. Document visual indicators if new ones introduced

---

## Migration Notes

### Breaking Changes

- **JSON `reasoning` field**: Now contains markdown table instead of plain paragraph
- **Frontend rendering**: Requires markdown parsing library (`marked`)
- **CSS styling**: Requires Tailwind Typography plugin (`@tailwindcss/typography`)

### Backward Compatibility

Old comparisons with paragraph format will still display, but won't have table styling. Consider:

```typescript
// Detect if markdown contains table
const hasTable = markdown.includes('|');

if (hasTable) {
  return renderMarkdownTable(markdown);
} else {
  return <p className="text-neutral-700">{markdown}</p>;
}
```

---

## References

- **Prompt Engineering**: `/api-tier/app/prompts/judge_comparison_prompts.py`
- **Service Logic**: `/api-tier/app/services/insight_comparison_service.py`
- **Frontend Component**: `/ui-tier/mfe-insights/src/components/comparison/ComparisonResults.tsx`
- **API Endpoint**: `/api-tier/app/api/v1/endpoints/insight_comparison.py`
- **Database Model**: `/api-tier/app/models/insight_comparison.py`

---

**Status**: ✅ Implementation complete and production-ready

---

## Version 2.1.0 Updates (2025-10-12)

### Enhanced Summary Formatting

**New Structure:**
1. **Executive Summary** with clear headings and bullet points
2. **Temperature Analysis** section with stage-wise settings
3. **Improved stage-wise reasoning** with markdown formatting

### Temperature Analysis Integration

The comparison now includes comprehensive temperature analysis to help optimize model parameters:

**Temperature Analysis Section:**
```markdown
### Temperature Analysis
**Model A Temperature Settings:**
- Stage 1: 0.3
- Stage 2: 0.5
- Stage 3: 0.2

**Model B Temperature Settings:**
- Stage 1: 0.0
- Stage 2: 0.3
- Stage 3: 0.0

**Temperature Impact:**
- **Fact Extraction (Stage 1):** Lower temperatures (0.0-0.3) recommended for deterministic fact extraction
- **Insight Generation (Stage 2):** Moderate temperatures (0.3-0.5) balance creativity with groundedness
- **Summarization (Stage 3):** Lower temperatures (0.0-0.3) ensure consistent, accurate summaries
- **Recommendation:** Use temperature ≤ 0.3 for all stages to minimize hallucination risk
```

### Enhanced Executive Summary Format

**New Structure:**
```markdown
## Executive Summary

### Overall Verdict
**Model B outperforms by 19.4% overall** with consistent, reliable performance across all stages.

### Key Findings
- **Quality Improvement:** +19.4% average score improvement
- **Cost Impact:** +$0.00001 (+0.8%) — negligible cost difference
- **Risk Assessment:** Model A shows critical failure in Stage 2 (Insights)
- **Business Impact:** Model B eliminates hallucination risk and ensures reliable insights

### Primary Deciding Factor
Model A's severe failure in Stage 2 (Insights) with groundedness scores of 0.45 and accuracy of 0.55 indicates hallucination and unreliable insights — a critical failure mode for business decision-making.

### Temperature Analysis
[Temperature settings and recommendations]

### Final Recommendation
✅ **Use Model B exclusively** for production workloads

**Rationale:**
- Superior quality (+19.4%) with negligible cost increase
- Eliminates critical hallucination risk observed in Model A
- Consistent performance across all pipeline stages
- Optimal temperature configuration ensures reliable outputs
```

### Stage-Wise Reasoning Format

Each stage now includes structured markdown with sections:

```markdown
### Stage 1: Fact Extraction Analysis

**Winner:** Response B

**Key Findings:**
- Response B achieved higher groundedness (0.92 vs 0.85) and completeness (0.88 vs 0.75)
- Response B captured all key customer pain points (lines 45-67)
- Response A missed critical pricing concern mentioned in transcript
- Both responses were faithful to source material
- Response B used systematic topic-based organization

**Critical Observations:**
- Response B's methodical approach resulted in superior accuracy
- Response A's fact extraction gaps could impact downstream analysis
- Completeness difference of 17.3% is significant for business use

**Recommendation:** Response B provides more reliable foundation for subsequent stages
```

### Frontend Enhancements

**Updated Components:**
1. **Stage Reasoning** - Now renders markdown with proper bullet formatting
2. **Model Summaries** - Added note about temperature settings in analysis
3. **Executive Summary** - Renders with full markdown support including lists

**CSS Classes Added:**
```css
prose-headings:text-sm prose-headings:text-neutral-800 prose-headings:font-bold
prose-p:text-sm prose-p:my-1
prose-ul:my-1 prose-ul:text-sm
prose-li:my-0.5
prose-strong:text-neutral-900 prose-strong:font-semibold
```

### Backend Implementation

**New Method in `InsightComparisonService`:**
```python
async def _get_temperature_settings(self, analysis: CallInsightsAnalysis) -> Dict[str, str]:
    """Extract temperature settings from analysis metadata or traces"""
    # Check if temperature is stored in analysis_metadata
    if analysis.analysis_metadata and "temperature_settings" in analysis.analysis_metadata:
        temps = analysis.analysis_metadata["temperature_settings"]
        return {
            "stage1": str(temps.get("stage1", "N/A")),
            "stage2": str(temps.get("stage2", "N/A")),
            "stage3": str(temps.get("stage3", "N/A")),
        }

    # Fallback: try to get from parent trace
    if analysis.parent_trace_id:
        from app.models.trace import Trace
        trace = await self.db.get(Trace, analysis.parent_trace_id)
        if trace and trace.temperature is not None:
            temp = str(trace.temperature)
            return {"stage1": temp, "stage2": temp, "stage3": temp}

    # Default if not found
    return {"stage1": "N/A", "stage2": "N/A", "stage3": "N/A"}
```

### Temperature Recommendations

Based on analysis of model performance:

| Stage | Purpose | Recommended Temperature | Rationale |
|-------|---------|------------------------|-----------|
| **Stage 1** | Fact Extraction | 0.0 - 0.3 | Deterministic fact extraction minimizes hallucination |
| **Stage 2** | Insight Generation | 0.3 - 0.5 | Balances creativity with groundedness for valuable insights |
| **Stage 3** | Summarization | 0.0 - 0.3 | Ensures consistent, accurate summaries without embellishment |

**General Guidance:**
- For production use cases requiring high reliability: Use temperature ≤ 0.3 across all stages
- For exploratory analysis where creative insights are valued: Use up to 0.5 for Stage 2
- Never exceed 0.5 for any stage in production environments
- Monitor groundedness scores; if below 0.70, reduce temperature by 0.1

---

**Status**: ✅ Implementation complete with enhanced formatting and temperature analysis
