# Phase 2 – Insight Comparator Feature Specification

**Status:** Phase 1 Implementation Ready
**Version:** 1.0
**Last Updated:** 2025-10-11
**Module:** Deep Insights MFE (`mfe-insights`)
**Priority:** High - Model Selection & Cost Optimization Feature

---

## Overview

The **Insight Comparator** enables organizations to make data-driven decisions about model selection by comparing AI-generated insights from different models in a **blind, unbiased evaluation**. This feature helps answer critical business questions:

- Should we use GPT-4o or Claude Sonnet 3.5 for production?
- Can GPT-4o-mini deliver similar quality at 10x lower cost?
- Which model performs better for our specific domain (finance, healthcare, etc.)?
- How do custom system prompts impact output quality across models?

**Key Innovation:** Uses a third **Judge Model** (default: Claude 4.5 Sonnet) to perform unbiased comparative evaluation without knowing which model produced which output.

---

## 1. Business Value & Use Cases

### Primary Use Cases

1. **Cost Optimization**
   - Compare expensive models (GPT-4o, Claude Opus) vs. cost-effective alternatives (GPT-4o-mini, Claude Haiku)
   - Quantify quality delta to justify cost savings
   - Find optimal model for specific use cases

2. **Quality Assurance**
   - Validate new model versions before production rollout
   - A/B test different system prompts with same model
   - Ensure consistent quality across model providers

3. **Multi-Model Strategy**
   - Use different models for different stages (fact extraction vs. reasoning)
   - Identify strengths/weaknesses per model type
   - Build hybrid pipelines (cheap for facts, premium for insights)

4. **Regulatory Compliance**
   - Compare outputs for bias, groundedness, factual accuracy
   - Document model selection rationale for audits
   - Track quality metrics over time

### Success Metrics

- **Cost Savings:** Identify opportunities to reduce inference costs by 70-90%
- **Quality Benchmarking:** Quantify model performance on organization-specific data
- **Decision Support:** Provide objective data for model selection discussions
- **Audit Trail:** Complete history of comparisons for compliance

---

## 2. Integration with Existing PromptForge Architecture

### Leverages Existing Systems

✅ **Call Insights Analysis Table** (`call_insights_analysis`)
- Source of analyses to compare
- Contains: transcript, all 3 stage outputs, models used, system prompts, traces
- Searchable by title, transcript content, date range
- Already tracks model performance metrics (tokens, cost, duration)

✅ **Trace System** (`traces` table + `trace_evaluations`)
- Parent-child trace relationships for DTA pipeline
- Per-stage token tracking (input/output/total)
- Cost calculation with model-specific pricing
- Evaluation results already linked to traces

✅ **Evaluation Framework** (6 frameworks integrated)
- DeepEval, Ragas, MLflow, Deepchecks, Arize Phoenix, PromptForge
- 93 vendor evaluations + custom evaluations + LLM-as-Judge
- Standard metrics: groundedness, faithfulness, coherence, accuracy, completeness
- Evaluation catalog with source tracking

✅ **Model Provider Service** (`app/services/model_provider.py`)
- Unified interface for OpenAI, Anthropic, others
- Already handles multiple models per organization
- API key management per organization
- Token tracking and cost calculation

### New Components Required

🆕 **Insight Comparisons Table** (`insight_comparisons`)
- Stores comparison results
- Links to 2 `call_insights_analysis` records
- Judge model verdict and scores
- Comparison metadata

🆕 **Comparison Service** (`app/services/insight_comparison_service.py`)
- Orchestrates blind comparison workflow
- Anonymizes outputs (Model A vs. Model B)
- Calls judge model for evaluation
- Parses and stores results

🆕 **Comparison API Endpoints** (`app/api/v1/endpoints/insight_comparison.py`)
- `POST /api/v1/insights/compare` - Create comparison
- `GET /api/v1/insights/comparisons` - List comparisons with filters
- `GET /api/v1/insights/comparisons/{id}` - Get specific comparison
- `DELETE /api/v1/insights/comparisons/{id}` - Delete comparison

🆕 **Comparison UI Components** (in `mfe-insights`)
- **ComparisonSection.tsx** - Main comparison interface
- **ComparisonSelector.tsx** - Select 2 analyses from history
- **ComparisonResults.tsx** - Side-by-side display with verdict
- **ComparisonMetrics.tsx** - Metric comparison visualization

---

## 3. Phase 1 Implementation Scope

### Phase 1: Core Comparison (This Implementation)

**Goal:** Enable users to select 2 existing insight analyses from history and compare them using a judge model.

**Features:**
- ✅ Select 2 analyses from insight history (same transcript, different models/prompts)
- ✅ Configurable judge model (default: Claude 4.5 Sonnet)
- ✅ Customizable evaluation rubric (select from standard metrics)
- ✅ Blind evaluation (judge doesn't know which model is which)
- ✅ Side-by-side comparison view
- ✅ Judge verdict with scores and reasoning
- ✅ Comparison history with search/filter
- ✅ Per-stage comparison (Stage 1 Facts, Stage 2 Insights, Stage 3 Summary)
- ✅ Overall winner + per-stage winners
- ✅ Export comparison results (JSON)

**Out of Scope (Future Phases):**
- ❌ Automatic model execution (user must pre-run analyses)
- ❌ Batch comparisons (compare >2 models)
- ❌ Radar chart visualization
- ❌ PDF export
- ❌ Comparison templates
- ❌ Automated recommendations

### Future Phase 2: Automated Comparison

- Trigger analyses for both models from comparison UI
- Compare models that don't have existing analyses
- Batch comparison (3+ models at once)
- Automated cost-benefit recommendations

### Future Phase 3: Advanced Analytics

- Historical trend analysis
- Model performance dashboards
- Radar chart visualizations
- Automated model selection recommendations
- Comparison templates for common scenarios

---

## 4. Data Model

### `insight_comparisons` Table Schema

```sql
CREATE TABLE insight_comparisons (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Organization & User
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Analyses Being Compared
    analysis_a_id UUID NOT NULL REFERENCES call_insights_analysis(id) ON DELETE CASCADE,
    analysis_b_id UUID NOT NULL REFERENCES call_insights_analysis(id) ON DELETE CASCADE,

    -- Judge Configuration
    judge_model VARCHAR(100) NOT NULL DEFAULT 'claude-sonnet-4.5',
    evaluation_criteria JSONB NOT NULL,  -- ['groundedness', 'clarity', 'completeness', etc.]

    -- Overall Results
    overall_winner VARCHAR(1) CHECK (overall_winner IN ('A', 'B', 'tie')),  -- A, B, or tie
    overall_reasoning TEXT NOT NULL,

    -- Per-Stage Results
    stage1_winner VARCHAR(1) CHECK (stage1_winner IN ('A', 'B', 'tie')),
    stage1_scores JSONB,  -- {"A": {"groundedness": 0.9, ...}, "B": {...}}
    stage1_reasoning TEXT,

    stage2_winner VARCHAR(1) CHECK (stage2_winner IN ('A', 'B', 'tie')),
    stage2_scores JSONB,
    stage2_reasoning TEXT,

    stage3_winner VARCHAR(1) CHECK (stage3_winner IN ('A', 'B', 'tie')),
    stage3_scores JSONB,
    stage3_reasoning TEXT,

    -- Judge Trace
    judge_trace_id UUID REFERENCES traces(id),  -- Trace of judge model invocation

    -- Metadata
    comparison_metadata JSONB,  -- Additional metadata (judge tokens, cost, etc.)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    CONSTRAINT unique_comparison UNIQUE (analysis_a_id, analysis_b_id, judge_model, evaluation_criteria),
    INDEX idx_comparisons_org (organization_id),
    INDEX idx_comparisons_user (user_id),
    INDEX idx_comparisons_created (created_at DESC)
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Unique comparison identifier |
| **organization_id** | UUID | Organization scope (RBAC) |
| **user_id** | UUID | User who created comparison |
| **analysis_a_id** | UUID | First analysis (Model A) |
| **analysis_b_id** | UUID | Second analysis (Model B) |
| **judge_model** | VARCHAR(100) | Judge model used (claude-sonnet-4.5, gpt-4o, etc.) |
| **evaluation_criteria** | JSONB | Array of criteria ['groundedness', 'clarity', ...] |
| **overall_winner** | VARCHAR(1) | Overall winner: 'A', 'B', or 'tie' |
| **overall_reasoning** | TEXT | Judge's overall reasoning |
| **stage1_winner** | VARCHAR(1) | Winner for Stage 1 (Fact Extraction) |
| **stage1_scores** | JSONB | Scores for Stage 1: `{"A": {...}, "B": {...}}` |
| **stage1_reasoning** | TEXT | Judge reasoning for Stage 1 |
| **stage2_winner** | VARCHAR(1) | Winner for Stage 2 (Reasoning & Insights) |
| **stage2_scores** | JSONB | Scores for Stage 2 |
| **stage2_reasoning** | TEXT | Judge reasoning for Stage 2 |
| **stage3_winner** | VARCHAR(1) | Winner for Stage 3 (Summary) |
| **stage3_scores** | JSONB | Scores for Stage 3 |
| **stage3_reasoning** | TEXT | Judge reasoning for Stage 3 |
| **judge_trace_id** | UUID | FK to traces table (judge invocation) |
| **comparison_metadata** | JSONB | Judge tokens, cost, duration, etc. |
| **created_at** | TIMESTAMP | Creation timestamp |
| **updated_at** | TIMESTAMP | Last update timestamp |

### Unique Constraint

Prevents duplicate comparisons: same analyses + same judge + same criteria = one comparison.

If user wants to re-run with different judge or criteria, creates new comparison.

---

## 5. API Design

### Base Path
```
/api/v1/insights/comparisons
```

### 5.1 POST /api/v1/insights/comparisons - Create Comparison

**Request Body:**
```json
{
  "analysis_a_id": "uuid",
  "analysis_b_id": "uuid",
  "judge_model": "claude-sonnet-4.5",  // Optional, defaults to claude-sonnet-4.5
  "evaluation_criteria": [              // Optional, defaults to all 5
    "groundedness",
    "faithfulness",
    "completeness",
    "clarity",
    "accuracy"
  ]
}
```

**Validation:**
- Both analyses must exist and belong to user's organization
- Both analyses must have same transcript (or very similar - TBD)
- Judge model must be available for organization
- Evaluation criteria must be valid (from predefined list)

**Response (201 Created):**
```json
{
  "id": "comparison-uuid",
  "organization_id": "org-uuid",
  "user_id": "user-uuid",

  "analysis_a": {
    "id": "uuid",
    "transcript_title": "Customer Call - Q3 2025",
    "model_stage1": "gpt-4o-mini",
    "model_stage2": "gpt-4o-mini",
    "model_stage3": "gpt-4o-mini",
    "total_tokens": 3500,
    "total_cost": 0.0012,
    "created_at": "2025-10-10T14:20:00Z"
  },

  "analysis_b": {
    "id": "uuid",
    "transcript_title": "Customer Call - Q3 2025",
    "model_stage1": "gpt-4o",
    "model_stage2": "gpt-4o",
    "model_stage3": "gpt-4o",
    "total_tokens": 3600,
    "total_cost": 0.0180,
    "created_at": "2025-10-10T14:25:00Z"
  },

  "judge_model": "claude-sonnet-4.5",
  "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"],

  "overall_winner": "B",
  "overall_reasoning": "Model B (gpt-4o) provided more grounded and complete analysis with 15% better scores across key metrics. The cost difference ($0.015 more) is justified by significantly improved factual accuracy and insight depth.",

  "stage_results": [
    {
      "stage": "Stage 1: Fact Extraction",
      "winner": "B",
      "scores": {
        "A": {
          "groundedness": 0.82,
          "faithfulness": 0.85,
          "completeness": 0.78,
          "clarity": 0.88,
          "accuracy": 0.80
        },
        "B": {
          "groundedness": 0.95,
          "faithfulness": 0.93,
          "completeness": 0.90,
          "clarity": 0.89,
          "accuracy": 0.94
        }
      },
      "reasoning": "Model B extracted more comprehensive facts with higher accuracy. Found 3 additional key entities that Model A missed."
    },
    {
      "stage": "Stage 2: Reasoning & Insights",
      "winner": "B",
      "scores": {
        "A": {
          "groundedness": 0.75,
          "faithfulness": 0.78,
          "completeness": 0.72,
          "clarity": 0.85,
          "accuracy": 0.73
        },
        "B": {
          "groundedness": 0.88,
          "faithfulness": 0.87,
          "completeness": 0.85,
          "clarity": 0.86,
          "accuracy": 0.89
        }
      },
      "reasoning": "Model B generated deeper insights with better contextual understanding. Identified 2 actionable recommendations that Model A missed."
    },
    {
      "stage": "Stage 3: Summary Synthesis",
      "winner": "tie",
      "scores": {
        "A": {
          "groundedness": 0.90,
          "faithfulness": 0.88,
          "completeness": 0.85,
          "clarity": 0.92,
          "accuracy": 0.87
        },
        "B": {
          "groundedness": 0.91,
          "faithfulness": 0.89,
          "completeness": 0.86,
          "clarity": 0.91,
          "accuracy": 0.88
        }
      },
      "reasoning": "Both models produced high-quality summaries with minimal difference (<3%). Model A had slightly better clarity, Model B had marginally better groundedness."
    }
  ],

  "judge_trace": {
    "trace_id": "judge-trace-uuid",
    "model": "claude-sonnet-4.5",
    "total_tokens": 8500,
    "cost": 0.0255,
    "duration_ms": 4200
  },

  "created_at": "2025-10-10T14:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request (missing fields, invalid criteria)
- `404 Not Found` - Analysis A or B not found
- `403 Forbidden` - Analyses belong to different organization
- `409 Conflict` - Comparison already exists (unique constraint)
- `422 Unprocessable Entity` - Analyses have different transcripts
- `500 Internal Server Error` - Judge model invocation failed

---

### 5.2 GET /api/v1/insights/comparisons - List Comparisons

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20, max: 100) - Results per page
- `sort_by` (enum, default: 'created_at') - Sort field: created_at, overall_winner
- `sort_direction` (enum, default: 'desc') - Sort order: asc, desc
- `judge_model` (string, optional) - Filter by judge model
- `winner` (enum, optional) - Filter by overall winner: A, B, tie
- `search` (string, optional) - Search by transcript title

**Response (200 OK):**
```json
{
  "comparisons": [
    {
      "id": "uuid",
      "analysis_a_title": "Customer Call - Q3 2025",
      "analysis_b_title": "Customer Call - Q3 2025",
      "model_a_summary": "gpt-4o-mini (all stages)",
      "model_b_summary": "gpt-4o (all stages)",
      "judge_model": "claude-sonnet-4.5",
      "overall_winner": "B",
      "cost_difference": "+$0.015",  // B costs $0.015 more
      "quality_improvement": "+15%",  // B scores 15% better on average
      "created_at": "2025-10-10T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 45,
    "total_pages": 3
  }
}
```

---

### 5.3 GET /api/v1/insights/comparisons/{id} - Get Comparison Detail

**Path Parameters:**
- `id` (UUID) - Comparison ID

**Response (200 OK):**
Same structure as POST response (full comparison details).

**Error Responses:**
- `404 Not Found` - Comparison not found
- `403 Forbidden` - Comparison belongs to different organization

---

### 5.4 DELETE /api/v1/insights/comparisons/{id} - Delete Comparison

**Path Parameters:**
- `id` (UUID) - Comparison ID

**Response (204 No Content)**

**Error Responses:**
- `404 Not Found` - Comparison not found
- `403 Forbidden` - Comparison belongs to different organization

---

## 6. Judge Model Evaluation Logic

### 6.1 Judge Model Selection

**Default:** Claude 4.5 Sonnet (`claude-sonnet-4.5`)

**Why Claude 4.5 Sonnet?**
- ✅ **Excellent reasoning:** Best-in-class analytical capabilities
- ✅ **Low bias:** Consistent, objective evaluations
- ✅ **JSON reliability:** Structured output compliance
- ✅ **Factual accuracy:** Strong at groundedness assessment
- ✅ **Cost-effective:** $3/$15 per million tokens (reasonable for judge role)

**Alternative Judge Models:**
- **GPT-4o** - Good alternative, slightly higher cost ($2.50/$10 per million)
- **GPT-4 Turbo** - Reliable but older
- **Claude Opus** - Higher quality but expensive ($15/$75 per million)

**Not Recommended:**
- ❌ **GPT-4o-mini / Claude Haiku** - Too shallow for nuanced comparison
- ❌ **GPT-3.5** - Inconsistent reasoning quality

### 6.2 Blind Evaluation Process

**Anonymization:**
1. Randomly assign analyses to "Model A" and "Model B"
2. Remove all model identifiers from outputs
3. Present to judge model without context

**Per-Stage Evaluation:**
Judge evaluates each stage independently:

**Stage 1 Prompt (Fact Extraction Comparison):**
```
You are an expert evaluator comparing two AI-generated fact extractions.

TRANSCRIPT (original input):
{transcript}

RESPONSE A (Fact Extraction):
{facts_a}

RESPONSE B (Fact Extraction):
{facts_b}

Evaluate both responses based on these criteria:
- Groundedness: Are facts supported by the transcript?
- Faithfulness: Does it adhere to source information?
- Completeness: Did it extract all key facts?
- Clarity: Is the extraction well-organized?
- Accuracy: Are details correct?

For each criterion, assign scores from 0.0 to 1.0.
Determine the winner (A, B, or tie).

Respond ONLY in this JSON format:
{
  "scores": {
    "A": {
      "groundedness": <float>,
      "faithfulness": <float>,
      "completeness": <float>,
      "clarity": <float>,
      "accuracy": <float>
    },
    "B": {
      "groundedness": <float>,
      "faithfulness": <float>,
      "completeness": <float>,
      "clarity": <float>,
      "accuracy": <float>
    }
  },
  "winner": "A" | "B" | "tie",
  "reasoning": "<detailed explanation>"
}
```

**Stage 2 Prompt (Reasoning & Insights Comparison):**
```
You are an expert evaluator comparing two AI-generated insight analyses.

FACTS (from Stage 1):
{facts_output}

RESPONSE A (Insights):
{insights_a}

RESPONSE B (Insights):
{insights_b}

Evaluate both responses based on these criteria:
- Groundedness: Are insights supported by facts?
- Faithfulness: Do insights align with source data?
- Completeness: Did it identify all key patterns?
- Clarity: Is reasoning clear and logical?
- Accuracy: Are conclusions correct?

For each criterion, assign scores from 0.0 to 1.0.
Determine the winner (A, B, or tie).

Respond ONLY in this JSON format:
{
  "scores": {
    "A": {...},
    "B": {...}
  },
  "winner": "A" | "B" | "tie",
  "reasoning": "<detailed explanation>"
}
```

**Stage 3 Prompt (Summary Comparison):**
```
You are an expert evaluator comparing two AI-generated summaries.

ORIGINAL INSIGHTS:
{insights_output}

RESPONSE A (Summary):
{summary_a}

RESPONSE B (Summary):
{summary_b}

Evaluate both responses based on these criteria:
- Groundedness: Is summary grounded in insights?
- Faithfulness: Does it preserve key information?
- Completeness: Did it cover all critical points?
- Clarity: Is it concise and readable?
- Accuracy: Are details accurate?

For each criterion, assign scores from 0.0 to 1.0.
Determine the winner (A, B, or tie).

Respond ONLY in this JSON format:
{
  "scores": {
    "A": {...},
    "B": {...}
  },
  "winner": "A" | "B" | "tie",
  "reasoning": "<detailed explanation>"
}
```

**Overall Evaluation:**
After all 3 stages, judge provides overall verdict:

```
You have evaluated three stages of analysis:

STAGE 1 WINNER: {stage1_winner}
STAGE 1 REASONING: {stage1_reasoning}

STAGE 2 WINNER: {stage2_winner}
STAGE 2 REASONING: {stage2_reasoning}

STAGE 3 WINNER: {stage3_winner}
STAGE 3 REASONING: {stage3_reasoning}

MODEL A COST: ${cost_a}
MODEL B COST: ${cost_b}

Provide an overall winner and business recommendation.
Consider:
- Which model won more stages?
- Quality differences across stages
- Cost vs. quality trade-off
- Business impact of quality differences

Respond in JSON format:
{
  "overall_winner": "A" | "B" | "tie",
  "reasoning": "<comprehensive business recommendation including cost-benefit analysis>"
}
```

### 6.3 JSON Parsing & Error Handling

**Robust Parsing:**
- Use `json.loads()` with error handling
- If JSON parsing fails, retry with corrected prompt
- Log all judge responses for debugging
- Store raw judge response in `comparison_metadata`

**Validation:**
- Scores must be 0.0-1.0
- Winner must be 'A', 'B', or 'tie'
- Reasoning must be non-empty
- All required fields present

**Fallback:**
- If 3 retries fail, mark comparison as failed
- Store error details in metadata
- Return 500 error to user with actionable message

---

## 7. UI/UX Design Specification

### 7.1 Location & Navigation

**Primary Location:** Deep Insights MFE (`/insights`)

**Tab Navigation:**
- **Analysis** (existing) - Main DTA analysis interface
- **Comparison** (new) - Model comparison interface ⭐
- **History** (existing, enhanced) - Now shows comparisons too

### 7.2 Comparison Tab Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Deep Insights > Comparison                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [Compare Models]  [Compare Prompts]  [History]                         │
│   (Active)                                                               │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Select Analyses to Compare                                          │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                      │ │
│  │  Analysis A: [Dropdown - Select from history]                       │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │ Customer Call - Q3 2025                                       │  │ │
│  │  │ Models: gpt-4o-mini (all stages)                              │  │ │
│  │  │ Tokens: 3,500 | Cost: $0.0012 | Date: Oct 10, 2025           │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                      │ │
│  │  Analysis B: [Dropdown - Select from history]                       │ │
│  │  ┌──────────────────────────────────────────────────────────────┐  │ │
│  │  │ Customer Call - Q3 2025                                       │  │ │
│  │  │ Models: gpt-4o (all stages)                                   │  │ │
│  │  │ Tokens: 3,600 | Cost: $0.0180 | Date: Oct 10, 2025           │  │ │
│  │  └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                      │ │
│  │  Judge Model: [claude-sonnet-4.5 ▼]                                 │ │
│  │  Evaluation Criteria: [✓] Groundedness [✓] Faithfulness [✓] ...    │ │
│  │                                                                      │ │
│  │  [Run Comparison]                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Comparison Results                                                  │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                      │ │
│  │  Overall Winner: Model B (gpt-4o)                   +15% Quality    │ │
│  │  Cost Difference: +$0.015                          Worth It? ✓ Yes  │ │
│  │                                                                      │ │
│  │  Judge Reasoning:                                                    │ │
│  │  "Model B (gpt-4o) provided more grounded and complete analysis..." │ │
│  │                                                                      │ │
│  │  ┌────────────────────────┬────────────────────────┐               │ │
│  │  │ Model A (gpt-4o-mini)  │ Model B (gpt-4o)       │               │ │
│  │  ├────────────────────────┼────────────────────────┤               │ │
│  │  │ STAGE 1: Fact Extraction                         │               │ │
│  │  │ ⚪ Score: 0.83          │ ✅ Winner: 0.92        │               │ │
│  │  │ - Groundedness: 0.82    │ - Groundedness: 0.95   │               │ │
│  │  │ - Faithfulness: 0.85    │ - Faithfulness: 0.93   │               │ │
│  │  │ - Completeness: 0.78    │ - Completeness: 0.90   │               │ │
│  │  │ - Clarity: 0.88         │ - Clarity: 0.89        │               │ │
│  │  │ - Accuracy: 0.80        │ - Accuracy: 0.94       │               │ │
│  │  │                         │                         │               │ │
│  │  │ [View Facts Output]     │ [View Facts Output]    │               │ │
│  │  ├────────────────────────┼────────────────────────┤               │ │
│  │  │ STAGE 2: Reasoning & Insights                    │               │ │
│  │  │ ⚪ Score: 0.77          │ ✅ Winner: 0.87        │               │ │
│  │  │ ... (similar layout) ...                         │               │ │
│  │  ├────────────────────────┼────────────────────────┤               │ │
│  │  │ STAGE 3: Summary Synthesis                       │               │ │
│  │  │ 🟡 Tie: 0.88           │ 🟡 Tie: 0.89           │               │ │
│  │  │ ... (similar layout) ...                         │               │ │
│  │  └────────────────────────┴────────────────────────┘               │ │
│  │                                                                      │ │
│  │  [Export JSON]  [Save to Project]  [Run Again]                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 UI Components

#### **ComparisonSection.tsx** (Main Container)
- Manages comparison workflow state
- Orchestrates child components
- Handles API calls
- Displays loading states and errors

#### **ComparisonSelector.tsx** (Analysis Selection)
**Props:**
- `onAnalysisASelected: (id: string) => void`
- `onAnalysisBSelected: (id: string) => void`
- `selectedAnalysisA: string | null`
- `selectedAnalysisB: string | null`

**Features:**
- Dropdown with search (powered by `HistorySection` API)
- Shows preview card: title, models, tokens, cost, date
- Validation: same transcript, different configurations
- Warning if transcripts don't match

#### **ComparisonConfig.tsx** (Judge & Criteria Selection)
**Props:**
- `judgeModel: string`
- `onJudgeModelChange: (model: string) => void`
- `evaluationCriteria: string[]`
- `onCriteriaChange: (criteria: string[]) => void`

**Features:**
- Judge model dropdown (claude-sonnet-4.5, gpt-4o, gpt-4-turbo)
- Multi-select criteria checkboxes
- Default: all 5 criteria selected
- Info tooltip explaining each criterion

#### **ComparisonResults.tsx** (Results Display)
**Props:**
- `comparison: ComparisonResponse`

**Features:**
- **Header Section:**
  - Overall winner badge (large, prominent)
  - Quality improvement percentage
  - Cost difference (+ or -)
  - Worth it indicator (checkmark or warning)

- **Judge Reasoning Card:**
  - Expandable/collapsible
  - Full reasoning text
  - Judge model used
  - Judge cost/tokens

- **Per-Stage Comparison:**
  - 3 expandable sections (Stage 1, 2, 3)
  - Side-by-side layout
  - Winner badge per stage
  - Score breakdown per criterion
  - "View Output" button (opens modal with full text)

- **Action Buttons:**
  - Export JSON
  - Save to Project (bookmark for later)
  - Run Again (re-run with different judge/criteria)

#### **ComparisonHistory.tsx** (History Table)
**Features:**
- Paginated table of past comparisons
- Columns:
  - Date
  - Transcript Title
  - Model A Summary
  - Model B Summary
  - Judge Model
  - Overall Winner
  - Quality Delta
  - Cost Delta
  - Actions (View, Delete)
- Filters:
  - Judge model
  - Winner (A, B, tie)
  - Date range
- Search by transcript title

### 7.4 Design System Compliance

**Colors:**
- **Winner Badge:** `bg-green-100 text-green-800 border-green-200`
- **Tie Badge:** `bg-yellow-100 text-yellow-800 border-yellow-200`
- **Model A Card:** `bg-blue-50 border-blue-200`
- **Model B Card:** `bg-purple-50 border-purple-200`
- **Metrics:** Primary color `#FF385C` for emphasis

**Typography:**
- **Headers:** `text-2xl font-bold text-neutral-700`
- **Body:** `text-sm text-neutral-600`
- **Scores:** `text-3xl font-bold` (large, prominent)
- **Reasoning:** `text-sm leading-relaxed text-neutral-700`

**Spacing:**
- **Cards:** `rounded-2xl p-8 gap-6`
- **Touch Targets:** `h-12` minimum for all interactive elements
- **Grid Gaps:** `gap-6` for sections, `gap-4` for cards

**Accessibility:**
- WCAG AAA compliant (7:1 contrast ratios)
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader support (aria-labels)
- Focus indicators (`ring-4 ring-[#FF385C]/10`)

---

## 8. Backend Implementation Details

### 8.1 File Structure

```
api-tier/
├── app/
│   ├── models/
│   │   └── insight_comparison.py          # New SQLAlchemy model
│   ├── schemas/
│   │   └── insight_comparison.py          # New Pydantic schemas
│   ├── api/v1/endpoints/
│   │   └── insight_comparison.py          # New API routes
│   ├── services/
│   │   └── insight_comparison_service.py  # New comparison service
│   └── prompts/
│       └── judge_comparison_prompts.py     # Judge model prompts
└── tests/
    └── mfe_insights/
        └── test_insight_comparison_api.py  # New API tests
```

### 8.2 Service Layer Architecture

**InsightComparisonService** (`app/services/insight_comparison_service.py`)

```python
class InsightComparisonService:
    """
    Service for comparing two insight analyses using a judge model.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_provider_service = ModelProviderService(db)

    async def create_comparison(
        self,
        analysis_a_id: UUID,
        analysis_b_id: UUID,
        judge_model: str,
        evaluation_criteria: List[str],
        organization_id: UUID,
        user_id: UUID
    ) -> InsightComparison:
        """
        Create a new comparison between two analyses.

        Steps:
        1. Validate analyses exist and belong to organization
        2. Validate transcripts match (or very similar)
        3. Check if comparison already exists (unique constraint)
        4. Randomly assign A/B labels
        5. Run judge evaluation for each stage
        6. Parse and store results
        7. Create trace for judge invocation
        8. Return comparison object
        """

    async def _evaluate_stage(
        self,
        stage_name: str,
        output_a: str,
        output_b: str,
        context: Dict[str, Any],
        judge_model: str,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate a single stage using judge model.

        Returns:
        {
            "winner": "A" | "B" | "tie",
            "scores": {"A": {...}, "B": {...}},
            "reasoning": "..."
        }
        """

    async def _run_judge_model(
        self,
        prompt: str,
        judge_model: str,
        organization_id: UUID
    ) -> str:
        """
        Invoke judge model with anonymized outputs.

        Uses ModelProviderService for unified model execution.
        """

    def _calculate_overall_winner(
        self,
        stage_results: List[Dict]
    ) -> Tuple[str, str]:
        """
        Determine overall winner based on stage results.

        Logic:
        - If one model wins 2+ stages: that model wins
        - If each wins 1 stage and 1 tie: consider average scores
        - If average scores within 5%: tie
        """
```

### 8.3 Prompt Templates

**Judge Prompts** (`app/prompts/judge_comparison_prompts.py`)

```python
STAGE1_COMPARISON_PROMPT = """
You are an expert evaluator comparing two AI-generated fact extractions.

TRANSCRIPT (original input):
{transcript}

RESPONSE A (Fact Extraction):
{facts_a}

RESPONSE B (Fact Extraction):
{facts_b}

Evaluate both responses based on these criteria:
{criteria_description}

For each criterion, assign scores from 0.0 to 1.0.
Determine the winner (A, B, or tie).

Respond ONLY in this JSON format:
{{
  "scores": {{
    "A": {{
      {criteria_json_keys}
    }},
    "B": {{
      {criteria_json_keys}
    }}
  }},
  "winner": "A" | "B" | "tie",
  "reasoning": "<detailed explanation>"
}}
"""

# Similar for STAGE2_COMPARISON_PROMPT, STAGE3_COMPARISON_PROMPT, OVERALL_VERDICT_PROMPT
```

---

## 9. Testing Strategy

### 9.1 API Tests (`tests/mfe_insights/test_insight_comparison_api.py`)

**Test Cases:**

1. **test_create_comparison_success**
   - Create 2 analyses with different models
   - Create comparison
   - Verify: comparison created, judge invoked, scores returned, overall winner determined

2. **test_create_comparison_duplicate**
   - Create comparison
   - Try to create same comparison again
   - Verify: 409 Conflict error (unique constraint)

3. **test_create_comparison_analyses_not_found**
   - Try to create comparison with non-existent analysis IDs
   - Verify: 404 Not Found error

4. **test_create_comparison_different_organizations**
   - Create 2 analyses in different orgs
   - Try to create comparison
   - Verify: 403 Forbidden error

5. **test_create_comparison_different_transcripts**
   - Create 2 analyses with different transcripts
   - Try to create comparison
   - Verify: 422 Unprocessable Entity error

6. **test_list_comparisons**
   - Create 5 comparisons
   - List with pagination, filters, search
   - Verify: correct comparisons returned, pagination works

7. **test_get_comparison_detail**
   - Create comparison
   - Get detail by ID
   - Verify: full comparison data returned

8. **test_delete_comparison**
   - Create comparison
   - Delete by ID
   - Verify: comparison deleted, 404 on subsequent get

9. **test_judge_model_invocation**
   - Mock judge model response
   - Verify: prompt format, JSON parsing, error handling

10. **test_per_stage_evaluation**
    - Test each stage evaluation independently
    - Verify: scores within 0-1 range, winner logic correct

### 9.2 Integration Tests

1. **End-to-End Comparison Workflow**
   - Create 2 analyses via API
   - Create comparison via API
   - Verify: entire workflow succeeds, judge trace created

2. **Judge Model Failure Handling**
   - Mock judge model failure
   - Verify: graceful error, retry logic, user-friendly error message

3. **Performance Test**
   - Create comparison with large transcripts (10K+ words)
   - Verify: completes within reasonable time (<30 seconds)

### 9.3 UI Component Tests

1. **ComparisonSelector.test.tsx**
   - Test analysis selection
   - Test validation (same transcript check)
   - Test warning display

2. **ComparisonResults.test.tsx**
   - Test winner badge display
   - Test score visualization
   - Test expandable sections
   - Test modal interactions

3. **ComparisonHistory.test.tsx**
   - Test table rendering
   - Test pagination
   - Test filters and search
   - Test delete action

---

## 10. Migration Plan

### 10.1 Database Migration

**File:** `alembic/versions/YYYYMMDD_add_insight_comparisons_table.py`

```python
"""Add insight_comparisons table

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-10-11 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'insight_comparisons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('judge_model', sa.String(100), nullable=False),
        sa.Column('evaluation_criteria', postgresql.JSONB, nullable=False),
        sa.Column('overall_winner', sa.String(1), nullable=True),
        sa.Column('overall_reasoning', sa.Text, nullable=False),
        sa.Column('stage1_winner', sa.String(1), nullable=True),
        sa.Column('stage1_scores', postgresql.JSONB, nullable=True),
        sa.Column('stage1_reasoning', sa.Text, nullable=True),
        sa.Column('stage2_winner', sa.String(1), nullable=True),
        sa.Column('stage2_scores', postgresql.JSONB, nullable=True),
        sa.Column('stage2_reasoning', sa.Text, nullable=True),
        sa.Column('stage3_winner', sa.String(1), nullable=True),
        sa.Column('stage3_scores', postgresql.JSONB, nullable=True),
        sa.Column('stage3_reasoning', sa.Text, nullable=True),
        sa.Column('judge_trace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('comparison_metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['analysis_a_id'], ['call_insights_analysis.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['analysis_b_id'], ['call_insights_analysis.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['judge_trace_id'], ['traces.id']),
        sa.CheckConstraint("overall_winner IN ('A', 'B', 'tie')"),
        sa.CheckConstraint("stage1_winner IN ('A', 'B', 'tie')"),
        sa.CheckConstraint("stage2_winner IN ('A', 'B', 'tie')"),
        sa.CheckConstraint("stage3_winner IN ('A', 'B', 'tie')"),
        sa.UniqueConstraint('analysis_a_id', 'analysis_b_id', 'judge_model', 'evaluation_criteria', name='unique_comparison')
    )

    op.create_index('idx_comparisons_org', 'insight_comparisons', ['organization_id'])
    op.create_index('idx_comparisons_user', 'insight_comparisons', ['user_id'])
    op.create_index('idx_comparisons_created', 'insight_comparisons', [sa.text('created_at DESC')])

def downgrade():
    op.drop_index('idx_comparisons_created', table_name='insight_comparisons')
    op.drop_index('idx_comparisons_user', table_name='insight_comparisons')
    op.drop_index('idx_comparisons_org', table_name='insight_comparisons')
    op.drop_table('insight_comparisons')
```

### 10.2 Deployment Steps

1. **Backend Deployment:**
   ```bash
   # 1. Run migration
   docker-compose exec api alembic upgrade head

   # 2. Restart API service
   docker-compose restart api

   # 3. Verify migration
   docker exec promptforge-postgres psql -U promptforge -d promptforge -c "\d insight_comparisons"
   ```

2. **Frontend Deployment:**
   ```bash
   # 1. Build mfe-insights
   cd ui-tier/mfe-insights
   npm run build

   # 2. Restart shell container
   docker-compose restart shell
   ```

3. **Smoke Tests:**
   ```bash
   # 1. Create 2 analyses
   # 2. Create comparison
   # 3. Verify comparison in UI
   ```

---

## 11. Success Criteria

### 11.1 Functional Requirements

✅ **User can:**
- Select 2 existing analyses from history
- Configure judge model and evaluation criteria
- Run blind comparison
- View side-by-side results with winner
- See per-stage scores and reasoning
- Export comparison results (JSON)
- View comparison history with filters
- Delete old comparisons

### 11.2 Non-Functional Requirements

✅ **Performance:**
- Comparison completes in <30 seconds (for 5K word transcripts)
- List comparisons loads in <2 seconds (100 records)
- UI is responsive and smooth

✅ **Quality:**
- Judge model produces consistent evaluations (test with same inputs)
- Scores are within 0.0-1.0 range
- Winner logic is clear and reproducible

✅ **Usability:**
- WCAG AAA accessible
- Mobile-responsive (tablet support)
- Clear error messages
- Intuitive workflow

✅ **Security:**
- Organization-scoped access (RBAC)
- Input validation on all endpoints
- No PII leakage in judge prompts

### 11.3 Business Metrics

📊 **Track:**
- Number of comparisons created per week
- Most common model pairs compared
- Average quality improvement found
- Cost savings identified
- User adoption rate

---

## 12. Future Enhancements (Post-Phase 1)

### Phase 2: Automated Comparison
- Run analyses directly from comparison UI (no need to pre-run)
- Batch comparison (compare 3+ models simultaneously)
- Automated recommendations based on cost-benefit analysis

### Phase 3: Advanced Analytics
- Historical trend analysis (model performance over time)
- Comparison templates (finance domain, healthcare domain, etc.)
- Radar chart visualizations
- Automated model selection recommendations
- PDF export with executive summary

### Phase 4: Organization Insights
- Organization-wide model performance dashboards
- Benchmark against industry standards
- Cost optimization recommendations
- Quality regression detection

---

## 13. Implementation Checklist

### Backend Tasks
- [ ] Create `InsightComparison` SQLAlchemy model
- [ ] Create Pydantic schemas (`ComparisonRequest`, `ComparisonResponse`)
- [ ] Create Alembic migration for `insight_comparisons` table
- [ ] Implement `InsightComparisonService`
- [ ] Create judge model prompt templates
- [ ] Implement API endpoints (POST/GET/DELETE)
- [ ] Add RBAC checks to all endpoints
- [ ] Write comprehensive API tests (10 test cases)
- [ ] Add logging and error handling
- [ ] Document API in OpenAPI spec

### Frontend Tasks
- [ ] Create TypeScript interfaces (`Comparison`, `ComparisonRequest`)
- [ ] Implement `comparisonService.ts` API client
- [ ] Create `ComparisonSection.tsx` main container
- [ ] Create `ComparisonSelector.tsx` component
- [ ] Create `ComparisonConfig.tsx` component
- [ ] Create `ComparisonResults.tsx` component
- [ ] Create `ComparisonHistory.tsx` component
- [ ] Add "Comparison" tab to InsightsPage
- [ ] Implement React hooks (`useComparisonCreate`, `useComparisonList`)
- [ ] Add loading states and error handling
- [ ] Write UI component tests
- [ ] Ensure WCAG AAA compliance

### Testing & Validation
- [ ] Run all API tests (100% pass rate)
- [ ] Run all UI component tests
- [ ] Manual end-to-end testing
- [ ] Performance testing (large transcripts)
- [ ] Accessibility testing (keyboard, screen reader)
- [ ] Security testing (RBAC, input validation)

### Subagent Validation
- [ ] API Architect review (API design, service layer)
- [ ] UI Architect review (component structure, state management)
- [ ] UX Specialist review (design compliance, accessibility)
- [ ] DB Architect review (schema design, indexing)
- [ ] Checker Agent review (overall quality, regressions)

### Documentation & Deployment
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Update Phase2_Insights_History.md with comparison feature
- [ ] Create deployment runbook
- [ ] Run migration in dev environment
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production

---

## 14. Related Documentation

- **Phase2_Insights_History.md** - Deep Insights feature (existing analyses)
- **Phase2_Summarization_Insights_API_DTA.md** - DTA pipeline API spec
- **Phase2_Evaluation_Framework.md** - Evaluation abstraction layer
- **Phase2_Trace_Dashboard.md** - Trace visualization
- **Phase2_UI_Framework.md** - UI design system standards

---

## 15. Questions & Decisions

### Open Questions
1. **Transcript Matching:** How similar do transcripts need to be? Exact match? 95% similarity? TBD
2. **Comparison Limit:** Should we limit comparisons per organization? (e.g., 1000 max)
3. **Judge Model Cost:** Should we show judge cost in UI? (adds transparency but may confuse users)

### Design Decisions
✅ **Per-stage evaluation:** Decided YES - provides granular insights (which stage is weaker)
✅ **Blind evaluation:** Decided YES - prevents judge bias
✅ **Default judge:** Claude 4.5 Sonnet - best balance of quality, cost, reliability
✅ **Unique constraint:** Decided YES - prevents duplicate comparisons, saves costs
✅ **Delete comparisons:** Decided YES - users should be able to clean up old comparisons

---

**Version:** 1.0
**Author:** Claude Code with PromptForge Orchestrator
**Approved by:** [Pending Subagent Validation]
**Implementation Target:** Q4 2025
**Estimated Effort:** 10-15 days (2-3 sprints)
