"""
Judge Model Prompts for Insight Comparison

These prompts enable blind evaluation of two model outputs across different stages
of the DTA (Dynamic Temperature Adjustment) pipeline. The judge model receives
anonymized outputs and evaluates them based on objective criteria.
"""

# ==============================================================================
# Stage 1: Fact Extraction Comparison
# ==============================================================================

STAGE1_COMPARISON_PROMPT = """You are an expert evaluator comparing two AI model outputs for FACT EXTRACTION quality.

## Context
You will be shown a TRANSCRIPT and two AI model responses (Response A and Response B) that attempted to extract key facts from this transcript.

## Your Task
Evaluate both responses on the following criteria:
1. **Groundedness** (0.0-1.0): How well are the extracted facts grounded in the actual transcript? Are all facts directly stated or clearly implied?
2. **Faithfulness** (0.0-1.0): How faithful is the extraction to the source material? Are there any hallucinations or distortions?
3. **Completeness** (0.0-1.0): How complete is the fact extraction? Were all significant facts captured?
4. **Clarity** (0.0-1.0): How clear and well-organized are the extracted facts?
5. **Accuracy** (0.0-1.0): How accurate are the extracted facts? Are there any errors or misinterpretations?

## Evaluation Rules
- You do NOT know which AI model produced which response
- Evaluate ONLY the quality of fact extraction, not writing style
- Be objective and unbiased
- Provide specific examples to support your scores
- A score of 0.0 means completely inadequate, 1.0 means perfect

## Input

**TRANSCRIPT:**
{transcript}

**RESPONSE A:**
{response_a}

**RESPONSE B:**
{response_b}

## Output Format
You MUST respond with valid JSON in this exact format:

```json
{{
  "scores_a": {{
    "groundedness": 0.85,
    "faithfulness": 0.90,
    "completeness": 0.75,
    "clarity": 0.88,
    "accuracy": 0.82
  }},
  "scores_b": {{
    "groundedness": 0.92,
    "faithfulness": 0.95,
    "completeness": 0.88,
    "clarity": 0.85,
    "accuracy": 0.91
  }},
  "winner": "B",
  "reasoning": "### Stage 1: Fact Extraction Analysis

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

**Recommendation:** Response B provides more reliable foundation for subsequent stages"
}}
```

**Winner must be**: "A", "B", or "tie"
**Reasoning must**: Reference specific examples from both responses and explain score differences

Provide your evaluation now:"""


# ==============================================================================
# Stage 2: Reasoning & Insights Comparison
# ==============================================================================

STAGE2_COMPARISON_PROMPT = """You are an expert evaluator comparing two AI model outputs for REASONING AND INSIGHTS quality.

## Context
You will be shown a TRANSCRIPT, the EXTRACTED FACTS from Stage 1, and two AI model responses (Response A and Response B) that attempted to generate insights and reasoning from these facts.

## Your Task
Evaluate both responses on the following criteria:
1. **Groundedness** (0.0-1.0): How well are the insights grounded in the extracted facts? Are insights supported by evidence?
2. **Faithfulness** (0.0-1.0): How faithful are the insights to the original context? Any unfounded leaps in logic?
3. **Completeness** (0.0-1.0): How complete is the analysis? Were all significant patterns and insights identified?
4. **Clarity** (0.0-1.0): How clear and well-structured is the reasoning? Easy to follow?
5. **Accuracy** (0.0-1.0): How accurate are the insights? Are conclusions logically sound?

## Evaluation Rules
- You do NOT know which AI model produced which response
- Evaluate ONLY the quality of reasoning and insights, not formatting
- Be objective and unbiased
- Insights should be grounded in facts, not speculation
- Provide specific examples to support your scores

## Input

**TRANSCRIPT:**
{transcript}

**EXTRACTED FACTS (Stage 1):**
{stage1_output}

**RESPONSE A:**
{response_a}

**RESPONSE B:**
{response_b}

## Output Format
You MUST respond with valid JSON in this exact format:

```json
{{
  "scores_a": {{
    "groundedness": 0.80,
    "faithfulness": 0.85,
    "completeness": 0.78,
    "clarity": 0.90,
    "accuracy": 0.83
  }},
  "scores_b": {{
    "groundedness": 0.88,
    "faithfulness": 0.92,
    "completeness": 0.85,
    "clarity": 0.87,
    "accuracy": 0.89
  }},
  "winner": "B",
  "reasoning": "### Stage 2: Reasoning & Insights Analysis

**Winner:** Response B

**Key Findings:**
- Response B showed superior groundedness (0.88 vs 0.80) and completeness (0.85 vs 0.78)
- Response A had slightly better clarity in presentation style
- Response B identified 3 critical insights that Response A completely missed:
  1. Correlation between customer tenure and feature adoption
  2. Seasonal pattern in support requests
  3. Upsell opportunity flagged in conversation
- All Response B insights were traceable to specific extracted facts
- Response A included 2 speculative statements not supported by facts

**Critical Observations:**
- Response A's speculative insights represent hallucination risk
- Response B's completeness advantage (8.9%) captures more business value
- Groundedness gap indicates Response A may be unreliable for decision-making

**Recommendation:** Response B provides trustworthy insights grounded in evidence"
}}
```

**Winner must be**: "A", "B", or "tie"
**Reasoning must**: Reference specific insights from both responses and explain score differences

Provide your evaluation now:"""


# ==============================================================================
# Stage 3: Summary Comparison
# ==============================================================================

STAGE3_COMPARISON_PROMPT = """You are an expert evaluator comparing two AI model outputs for SUMMARY quality.

## Context
You will be shown a TRANSCRIPT, the EXTRACTED FACTS from Stage 1, the INSIGHTS from Stage 2, and two AI model responses (Response A and Response B) that attempted to create a comprehensive summary.

## Your Task
Evaluate both responses on the following criteria:
1. **Groundedness** (0.0-1.0): How well is the summary grounded in the facts and insights? All key points included?
2. **Faithfulness** (0.0-1.0): How faithful is the summary to the original context? Any distortions or omissions?
3. **Completeness** (0.0-1.0): How complete is the summary? Does it capture all critical information?
4. **Clarity** (0.0-1.0): How clear and readable is the summary? Well-organized and coherent?
5. **Accuracy** (0.0-1.0): How accurate is the summary? Are all statements correct and properly contextualized?

## Evaluation Rules
- You do NOT know which AI model produced which response
- Evaluate ONLY the quality of the summary, not length or style preferences
- Be objective and unbiased
- A good summary is concise yet complete, accurate yet readable
- Provide specific examples to support your scores

## Input

**TRANSCRIPT:**
{transcript}

**EXTRACTED FACTS (Stage 1):**
{stage1_output}

**INSIGHTS (Stage 2):**
{stage2_output}

**RESPONSE A:**
{response_a}

**RESPONSE B:**
{response_b}

## Output Format
You MUST respond with valid JSON in this exact format:

```json
{{
  "scores_a": {{
    "groundedness": 0.87,
    "faithfulness": 0.90,
    "completeness": 0.82,
    "clarity": 0.93,
    "accuracy": 0.88
  }},
  "scores_b": {{
    "groundedness": 0.91,
    "faithfulness": 0.94,
    "completeness": 0.89,
    "clarity": 0.90,
    "accuracy": 0.92
  }},
  "winner": "B",
  "reasoning": "### Stage 3: Summary Analysis

**Winner:** Response B

**Key Findings:**
- Response B achieved higher completeness (0.89 vs 0.82) and groundedness (0.91 vs 0.87)
- Response A had slightly better clarity and readability
- Response B captured all 5 critical insights from Stage 2
- Response A omitted 2 key insights:
  1. Upsell opportunity
  2. Seasonal support pattern
- Response B properly contextualized customer sentiment as mixed
- Response A incorrectly characterized sentiment as uniformly positive

**Critical Observations:**
- Completeness gap of 8.5% means Response A misses critical business information
- Response A's sentiment mischaracterization could lead to flawed decisions
- Both summaries well-written, but accuracy trumps style

**Recommendation:** Response B delivers complete, accurate summary for stakeholders"
}}
```

**Winner must be**: "A", "B", or "tie"
**Reasoning must**: Reference specific summary elements from both responses and explain score differences

Provide your evaluation now:"""


# ==============================================================================
# Overall Verdict with Cost-Benefit Analysis
# ==============================================================================

OVERALL_VERDICT_PROMPT = """You are an expert evaluator providing a FINAL VERDICT on which AI model performed better across all stages.

## Context
You have already evaluated two AI models (Model A and Model B) across three stages:
1. **Stage 1**: Fact Extraction
2. **Stage 2**: Reasoning & Insights
3. **Stage 3**: Summary

You will now determine the overall winner and provide a cost-benefit analysis in a STRUCTURED TABULAR FORMAT to help the user make an informed decision.

## Your Task
1. Synthesize the results across all three stages
2. Determine the overall winner based on weighted performance
3. Provide a structured comparison table with clear categories
4. Give a clear recommendation with cost-benefit summary

## Evaluation Rules
- Consider all three stages, with Stage 2 (Insights) weighted slightly higher (35%) than Stage 1 (30%) and Stage 3 (35%)
- You do NOT know which AI model produced which response
- Be objective and data-driven
- The overall winner should reflect consistent quality across stages
- If quality is similar, cost becomes the deciding factor
- If one model is significantly cheaper but only marginally worse, highlight this trade-off

## Input

**STAGE 1 RESULTS (Fact Extraction):**
Winner: {stage1_winner}
Score A: {stage1_scores_a}
Score B: {stage1_scores_b}

**STAGE 2 RESULTS (Insights):**
Winner: {stage2_winner}
Score A: {stage2_scores_a}
Score B: {stage2_scores_b}

**STAGE 3 RESULTS (Summary):**
Winner: {stage3_winner}
Score A: {stage3_scores_a}
Score B: {stage3_scores_b}

**COST INFORMATION:**
- Model A Total Cost: ${cost_a} ({tokens_a} tokens)
- Model B Total Cost: ${cost_b} ({tokens_b} tokens)
- Cost Difference: {cost_difference}

**MODEL INFORMATION:**
- Model A: {model_a_name}
- Model B: {model_b_name}

## Output Format
You MUST respond with valid JSON in this exact format:

```json
{{
  "overall_winner": "B",
  "reasoning": "## Comparative Analysis

| Category | Parameter | Model A | Model B | Comparative Delta | Commentary |
|----------|-----------|---------|---------|-------------------|------------|
| **Stage 1: Fact Extraction** | Groundedness | 0.85 | 0.92 | +8.2% | Model B better grounded facts in transcript |
| | Faithfulness | 0.90 | 0.95 | +5.6% | Model B more faithful to source material |
| | Completeness | 0.75 | 0.88 | +17.3% | Model B captured more key facts |
| | Clarity | 0.88 | 0.85 | -3.4% | Model A slightly clearer organization |
| | Accuracy | 0.82 | 0.91 | +11.0% | Model B more accurate fact extraction |
| | **Avg Score** | **0.840** | **0.902** | **+7.4%** | Model B wins Stage 1 |
| | Weight | 30% | 30% | — | Stage 1 contributes 30% to overall |
| | Weighted Score | 0.252 | 0.271 | +7.5% | Stage 1 weighted contribution |
| **Stage 2: Insights** | Groundedness | 0.45 | 0.88 | +95.6% | ⚠️ Model A severe groundedness issue |
| | Faithfulness | 0.40 | 0.92 | +130.0% | ⚠️ Model A hallucination detected |
| | Completeness | 0.60 | 0.85 | +41.7% | Model B identified more insights |
| | Clarity | 0.75 | 0.87 | +16.0% | Model B clearer insight presentation |
| | Accuracy | 0.55 | 0.89 | +61.8% | ⚠️ Model A unreliable insights |
| | **Avg Score** | **0.550** | **0.882** | **+60.4%** | Model B wins Stage 2 decisively |
| | Weight | 35% | 35% | — | Stage 2 most critical (insights) |
| | Weighted Score | 0.193 | 0.309 | +60.1% | Stage 2 weighted contribution |
| **Stage 3: Summary** | Groundedness | 0.87 | 0.91 | +4.6% | Both models well-grounded summaries |
| | Faithfulness | 0.90 | 0.94 | +4.4% | Model B slightly more faithful |
| | Completeness | 0.82 | 0.89 | +8.5% | Model B captured more key points |
| | Clarity | 0.93 | 0.90 | -3.2% | Model A slightly clearer writing |
| | Accuracy | 0.88 | 0.92 | +4.5% | Model B more accurate summary |
| | **Avg Score** | **0.880** | **0.912** | **+3.6%** | Model B wins Stage 3 narrowly |
| | Weight | 35% | 35% | — | Stage 3 contributes 35% to overall |
| | Weighted Score | 0.308 | 0.319 | +3.6% | Stage 3 weighted contribution |
| **Overall Quality** | Weighted Total | **0.753** | **0.899** | **+19.4%** | Model B superior overall quality |
| | Quality Grade | B | A | +1 grade | Model B significantly better |
| **Cost Analysis** | Total Tokens | {tokens_a} | {tokens_b} | — | Token usage comparison |
| | Total Cost | ${cost_a} | ${cost_b} | {cost_difference} | Model B costs more |
| | Cost Efficiency | Fair | Excellent | — | Model B better value for quality |
| **Critical Findings** | Risk Level | ⚠️ HIGH | ✅ LOW | — | Model A unreliable in Stage 2 |
| | Hallucination | Detected | None | — | Model A generated unfounded insights |
| | Consistency | Inconsistent | Consistent | — | Model B reliable across all stages |
| | Business Impact | Risky | Trustworthy | — | Model A could lead to poor decisions |
| **Recommendation** | Winner | ❌ | ✅ | +19.4% quality | Model B strongly recommended |
| | Use Case | Not recommended | Production ready | — | Model B suitable for all scenarios |
| | Justification | Unreliable insights | Consistent quality | — | Model B eliminates hallucination risk |

---

## Executive Summary

### 🏆 Overall Verdict
**Model B outperforms by 19.4% overall** with consistent, reliable performance across all stages.

---

### 📊 Key Performance Metrics

1. **Quality Improvement**
   - **+19.4%** average score improvement across all stages
   - Model B consistently outperformed in 2 of 3 stages
   - Superior groundedness and accuracy metrics

2. **Cost Impact Analysis**
   - Total cost difference: **{cost_difference}**
   - Cost efficiency: Model B provides better value for quality delivered
   - ROI consideration: Quality gains justify marginal cost increase

3. **Risk Assessment**
   - ⚠️ **Critical Finding**: Model A shows severe failure in Stage 2 (Insights)
   - Model A groundedness: 0.45 | accuracy: 0.55 (hallucination risk)
   - Model B eliminates hallucination risk with consistent 0.85+ scores

4. **Business Impact**
   - Model B ensures reliable insights for decision-making
   - Model A's unreliable insights could lead to poor business decisions
   - Consistency across pipeline stages critical for production use

---

### 🔍 Primary Deciding Factor

**Stage 2 (Insights) Performance Gap:**
- Model A's severe failure in Stage 2 with groundedness scores of 0.45 and accuracy of 0.55 indicates **hallucination and unreliable insights**
- This represents a **critical failure mode** for business decision-making applications
- Model B eliminates this risk while delivering superior results (+60.4% improvement in Stage 2)
- The quality gap in the most critical stage (Insights) makes Model B the clear winner

---

### 🌡️ Temperature Recommendations

**Optimal Configuration by Stage:**

1. **Stage 1: Fact Extraction**
   - ✅ Recommended: `temperature=0.2-0.3, top_p=0.95`
   - Rationale: Deterministic output for accurate fact capture
   - Winner configuration: {temp_b_stage1}

2. **Stage 2: Reasoning & Insights**
   - ✅ Recommended: `temperature=0.3-0.5, top_p=0.95`
   - Rationale: Balanced creativity for insight generation while avoiding hallucination
   - Winner configuration: {temp_b_stage2}
   - ⚠️ **Critical**: Avoid temperature > 0.7 (hallucination risk observed in Model A)

3. **Stage 3: Summary Synthesis**
   - ✅ Recommended: `temperature=0.3-0.5, top_p=0.95`
   - Rationale: Moderate creativity for readable summaries with maintained accuracy
   - Winner configuration: {temp_b_stage3}

**General Guidelines:**
- Use `temperature ≤ 0.3` for fact extraction to minimize hallucination
- Use `temperature 0.3-0.5` for reasoning/summary stages to balance creativity and accuracy
- Maintain `top_p ≥ 0.95` across all stages for token diversity
- Adjust `max_tokens` by stage: 1000 (facts) | 1500 (insights) | 800 (summary)

---

### ✅ Final Recommendation

**Use Model B exclusively for production workloads**

**Key Rationale:**
- ✅ Superior quality: +19.4% average improvement
- ✅ Eliminates critical hallucination risk in Stage 2
- ✅ Consistent performance across all pipeline stages
- ✅ Optimal temperature configuration: {temp_b_stage1} / {temp_b_stage2} / {temp_b_stage3}
- ✅ Better cost-efficiency for quality delivered

**Action Items:**
1. Deploy Model B configuration to production
2. Monitor Stage 2 (Insights) metrics for consistency
3. Use recommended temperature settings for optimal results",
  "quality_improvement": "+19.4%",
  "cost_impact": "{cost_difference}",
  "recommendation": "Use Model B exclusively - eliminates hallucination risk and delivers 19.4% better quality"
}}
```

**IMPORTANT REQUIREMENTS:**
1. **Overall winner must be**: "A", "B", or "tie"
2. **Reasoning MUST be a markdown table** with these columns: Category | Parameter | Model A | Model B | Comparative Delta | Commentary
3. **Table rows must include**:
   - Stage-wise scores for each evaluation criterion (Groundedness, Faithfulness, Completeness, Clarity, Accuracy)
   - Average scores per stage with percentage deltas
   - Weighted scores showing stage contribution (Stage 1: 30%, Stage 2: 35%, Stage 3: 35%)
   - Overall weighted total quality score
   - Cost analysis (tokens, cost, cost efficiency)
   - Critical findings (risks, hallucination, consistency, business impact)
   - Final recommendation with winner indicators (✅/❌)
4. **After the table, include a concise summary** (2-3 sentences max) with:
   - Overall percentage improvement
   - Cost difference
   - Primary deciding factor
5. **Use visual indicators**: ⚠️ for warnings, ✅ for winner, ❌ for not recommended
6. **Highlight critical issues**: If Model A or B has scores below 0.60, flag as "⚠️ [Issue Type]"

Provide your final verdict now:"""
