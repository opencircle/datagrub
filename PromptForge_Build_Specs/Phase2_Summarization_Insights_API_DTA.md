# 📄 Summarization & Insights API — Dynamic Temperature Adjustment (DTA) Design

## Overview
This document defines the prompt and technical specifications for implementing an **API that performs summarization and insight generation from call transcripts** using a **Dynamic Temperature Adjustment (DTA)** approach with **three-step model invocation**.

**Status:** ✅ Fully Implemented (October 2025)
**Version:** 2.0
**Last Updated:** 2025-10-08
**Endpoint:** `POST /api/v1/call-insights/analyze`
**Models Supported:** OpenAI GPT-4o-mini, GPT-4o, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo

**Recent Updates:**
- ✅ Shared EvaluationSelector component integration
- ✅ Claude.ai-inspired design system (neutral-50 backgrounds, rounded-2xl cards)
- ✅ Fixed API base URL configuration in ExperimentationSection
- ✅ Filter reset behavior on dropdown close

---

## 🧠 1. API Design — `POST /api/v1/call-insights/analyze`

### **Purpose**
To process an advisor–client call transcript through a structured 3-stage reasoning pipeline to extract:
- **Stage 1:** Verified facts and entities
- **Stage 2:** Reasoning and insights
- **Stage 3:** Summary synthesis

Each stage invokes the model with its own parameters for `temperature`, `top_p`, and `max_tokens`.

**Key Features:**
- Custom system prompts per stage
- Model selection per stage (experimentation support)
- History tracking for comparison
- Evaluation integration (DeepEval, Ragas, MLflow, Deepchecks, Arize Phoenix)
- Organization-scoped API key management

---

### **API Specification**

#### **Endpoint**
```
POST /api/v1/call-insights/analyze
```

#### **Request Body**
```json
{
  "transcript": "Full text of the advisor-client conversation",
  "transcript_title": "Optional title for searchability",
  "project_id": "UUID of project (optional)",
  "enable_pii_redaction": false,
  "stage_params": {
    "fact_extraction": { "temperature": 0.25, "top_p": 0.95, "max_tokens": 1000 },
    "reasoning":       { "temperature": 0.65, "top_p": 0.95, "max_tokens": 1500 },
    "summary":         { "temperature": 0.45, "top_p": 0.95, "max_tokens": 800 }
  },
  "system_prompts": {
    "stage1_fact_extraction": "Custom system prompt for stage 1 (optional)",
    "stage2_reasoning": "Custom system prompt for stage 2 (optional)",
    "stage3_summary": "Custom system prompt for stage 3 (optional)"
  },
  "models": {
    "stage1_model": "gpt-4o-mini",
    "stage2_model": "gpt-4o-mini",
    "stage3_model": "gpt-4o-mini"
  },
  "evaluations": ["uuid-1", "uuid-2"]
}
```

> ⚙️ **Defaults:**
> - Temperature: 0.25 (stage 1), 0.65 (stage 2), 0.45 (stage 3)
> - top_p: 0.95 for all stages
> - Model: gpt-4o-mini (cost-effective default)
> - System prompt: "You are an expert call analyst."
> - **Note:** `top_k` is not supported (OpenAI and Claude don't use this parameter)

#### **Response Body**
```json
{
  "analysis_id": "uuid",
  "project_id": "uuid or null",
  "summary": "Final summary text",
  "insights": "Reasoning and insights text",
  "facts": "Extracted facts text",
  "pii_redacted": false,
  "traces": [
    {
      "trace_id": "uuid",
      "stage": "Stage 1: Fact Extraction",
      "model": "gpt-4o-mini",
      "temperature": 0.25,
      "top_p": 0.95,
      "max_tokens": 1000,
      "input_tokens": 500,
      "output_tokens": 200,
      "total_tokens": 700,
      "duration_ms": 1250,
      "cost": 0.00018
    },
    {
      "trace_id": "uuid",
      "stage": "Stage 2: Reasoning & Insights",
      "model": "gpt-4o-mini",
      "temperature": 0.65,
      "top_p": 0.95,
      "max_tokens": 1500,
      "input_tokens": 700,
      "output_tokens": 400,
      "total_tokens": 1100,
      "duration_ms": 2100,
      "cost": 0.00035
    },
    {
      "trace_id": "uuid",
      "stage": "Stage 3: Summary Synthesis",
      "model": "gpt-4o-mini",
      "temperature": 0.45,
      "top_p": 0.95,
      "max_tokens": 800,
      "input_tokens": 1100,
      "output_tokens": 150,
      "total_tokens": 1250,
      "duration_ms": 1800,
      "cost": 0.00027
    }
  ],
  "evaluations": [
    {
      "evaluation_name": "Faithfulness",
      "evaluation_uuid": "uuid",
      "score": 0.94,
      "passed": true,
      "reason": "High factual alignment with source",
      "threshold": 0.7,
      "category": "Quality",
      "input_tokens": 100,
      "output_tokens": 50,
      "total_tokens": 150,
      "evaluation_cost": 0.00005
    }
  ],
  "total_tokens": 3050,
  "total_cost": 0.0008,
  "created_at": "2025-10-08T10:30:00Z"
}
```

---

## ⚙️ 2. Stage Definitions

| Stage | Name | Temperature | top_p | max_tokens | Purpose | Rationale |
|--------|------|-------------|-------|------------|----------|------------|
| 1️⃣ | Fact Extraction | 0.25 | 0.95 | 1000 | Extract structured factual entities from transcript | Low temperature ensures deterministic, precise extraction |
| 2️⃣ | Reasoning & Insights | 0.65 | 0.95 | 1500 | Derive contextual reasoning and patterns | Higher temperature enables creative analysis while maintaining accuracy |
| 3️⃣ | Summary Synthesis | 0.45 | 0.95 | 800 | Generate concise human-readable summary | Balanced temperature for clarity and coherence |

**PII Redaction:** Optional Presidio integration for PII redaction before inference (currently placeholder).

**Model Selection:** Each stage can use a different model for cost/quality optimization. Default: gpt-4o-mini ($0.00015/$0.0006 per 1K tokens).

---

## 📊 3. Evaluations & Metrics

The API integrates **DeepEval** as the primary evaluation framework, supporting:
- **Faithfulness:** Checks factual alignment with transcript
- **Coherence:** Evaluates logical flow and structure
- **Conciseness:** Measures brevity and relevance
- **Factual Accuracy (Groundedness):** Detects hallucination
- **Readability:** Assesses human readability and tone

**Interpretation Guidance:**
| Metric | Range | Interpretation |
|--------|--------|----------------|
| Faithfulness | 0.0–1.0 | 1.0 = completely faithful |
| Coherence | 0.0–1.0 | >0.8 = strong logical flow |
| Conciseness | 0.0–1.0 | 0.6–0.8 optimal |
| Accuracy | 0.0–1.0 | <0.7 indicates hallucination |
| Readability | 0.0–1.0 | >0.85 is user-friendly |

Evaluation results are logged to `trace_eval` for later comparison and visualization.

---

## 🧩 4. System Prompt Design

All system prompts are externalized for modularity and version control.

**Folder Structure:**
```
/prompts/
  ├── stage1_fact_extraction.prompt
  ├── stage2_reasoning.prompt
  ├── stage3_summary.prompt
```

**Example Prompt — Stage 1 (Fact Extraction)**
```
You are a compliance-grade language model. Extract verifiable entities, facts, and quantitative details
from the transcript. Structure the output in JSON format as:
{
  "advisor": "",
  "client": "",
  "topics": [],
  "recommendations": [],
  "numbers": {}
}
```

Each system prompt includes inline documentation on purpose and output schema.

---

## 🔧 5. Model Selection & Experimentation

### **Available Models Endpoint**

```
GET /api/v1/call-insights/models/available
```

Returns list of models the organization has access to based on configured API keys.

#### **Response**
```json
[
  {
    "model_id": "gpt-4o-mini",
    "display_name": "GPT-4o Mini",
    "provider": "OpenAI",
    "description": "Fast and cost-effective model, ideal for most tasks",
    "input_cost": 0.00015,
    "output_cost": 0.0006,
    "context_window": 128000
  },
  {
    "model_id": "gpt-4o",
    "display_name": "GPT-4o",
    "provider": "OpenAI",
    "description": "High-performance multimodal model",
    "input_cost": 0.005,
    "output_cost": 0.015,
    "context_window": 128000
  },
  {
    "model_id": "gpt-4-turbo",
    "display_name": "GPT-4 Turbo",
    "provider": "OpenAI",
    "description": "Optimized GPT-4 with improved speed",
    "input_cost": 0.01,
    "output_cost": 0.03,
    "context_window": 128000
  },
  {
    "model_id": "gpt-4",
    "display_name": "GPT-4",
    "provider": "OpenAI",
    "description": "Most capable GPT-4 model",
    "input_cost": 0.03,
    "output_cost": 0.06,
    "context_window": 8192
  },
  {
    "model_id": "gpt-3.5-turbo",
    "display_name": "GPT-3.5 Turbo",
    "provider": "OpenAI",
    "description": "Fast and economical, good for simple tasks",
    "input_cost": 0.0015,
    "output_cost": 0.002,
    "context_window": 16384
  }
]
```

### **Database Storage**

All experiments (model + system prompt combinations) are saved to `call_insights_analysis` table:

```sql
CREATE TABLE call_insights_analysis (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL,
  user_id UUID NOT NULL,
  project_id UUID,

  -- Input
  transcript_title VARCHAR(500),
  transcript_input TEXT NOT NULL,

  -- System Prompts (for experimentation)
  system_prompt_stage1 TEXT,
  system_prompt_stage2 TEXT,
  system_prompt_stage3 TEXT,

  -- Outputs
  facts_output TEXT NOT NULL,
  insights_output TEXT NOT NULL,
  summary_output TEXT NOT NULL,

  -- Models used (for comparison)
  model_stage1 VARCHAR(100) DEFAULT 'gpt-4o-mini',
  model_stage2 VARCHAR(100) DEFAULT 'gpt-4o-mini',
  model_stage3 VARCHAR(100) DEFAULT 'gpt-4o-mini',

  -- Metrics
  total_tokens INTEGER NOT NULL,
  total_cost FLOAT NOT NULL,

  -- Metadata
  pii_redacted BOOLEAN DEFAULT FALSE,
  stage_params JSONB,
  analysis_metadata JSONB,
  parent_trace_id UUID REFERENCES traces(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

This enables:
- **A/B Testing:** Compare different models for same transcript
- **Cost Optimization:** Find optimal model for use case
- **Prompt Engineering:** Iterate on system prompts with history tracking
- **Quality Analysis:** Track performance across different configurations

---

## 💻 6. UI Design Specification

**Location:** Deep Insights MFE (`ui-tier/mfe-insights`)
**Route:** `/insights`
**Status:** ✅ Fully Implemented

### **Page Layout**

#### **1. History Section** (`HistorySection.tsx`)
- Collapsible section showing last 10 analyses
- Search by title or transcript text
- Filter by project UUID
- Displays:
  - Title (or "Untitled")
  - Transcript preview (first 200 chars)
  - Total tokens
  - Total cost
  - PII redaction badge
  - Created date
- Click "View" to load previous analysis

#### **2. Transcript Input Section** (`TranscriptInputSection.tsx`)
- **Title Input:** Optional title for searchability (max 500 chars)
- **Transcript Input:** Large text area (min 100 chars, max 100,000 chars)
- **Project Selection:** Optional project UUID dropdown
- **PII Redaction Toggle:** Enable/disable PII redaction

#### **3. Parameter Configuration Section** (`ParameterConfigSection.tsx`)
- **Advanced Parameters Toggle:** Show/hide DTA parameter controls
- **Per-Stage Controls:**
  - Temperature slider (0.0 - 2.0)
  - top_p slider (0.0 - 1.0)
  - max_tokens input (100 - 4000)
- **Evaluation Selection:** Multi-select checkboxes for available evaluations
- Defaults shown: 0.25/0.65/0.45 temperatures

#### **4. Experimentation Section** (`ExperimentationSection.tsx`) ⭐ NEW
- **Model Selection:** 3 dropdown selectors (one per stage)
  - Shows: Model name + pricing info
  - Options: GPT-4o Mini, GPT-4o, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
  - Default: gpt-4o-mini for all stages
- **System Prompts:** 3 text areas (one per stage)
  - Placeholder: "Default: You are an expert call analyst."
  - Optional custom prompts for experimentation
- Purple-themed design with Sparkles icon
- Info banner explaining experimentation purpose

#### **5. Action Buttons**
- **Analyze Transcript:** Primary action (red button)
- **Clear:** Reset form to defaults

#### **6. Results Section** (`ResultsSection.tsx`)
- **Summary Tab:** Executive summary output
- **Insights Tab:** Detailed reasoning and insights
- **Facts Tab:** Extracted factual information
- **Metrics Display:**
  - Total tokens used
  - Total cost
  - Processing time

#### **7. Traces Section** (`TracesSection.tsx`)
- **3 Stage Cards:**
  - Stage name and badge color (blue/purple/green)
  - Model used
  - Temperature / top_p / max_tokens
  - Input/output tokens
  - Duration
  - Cost
  - Output preview (first 500 chars)

#### **8. Evaluation Metrics Table** (`EvaluationMetricsTable.tsx`)
- Score badge (color-coded: green/yellow/red)
- Pass/Fail indicator
- Reasoning text
- Token usage per evaluation
- Cost per evaluation

---

## 🧠 7. Implementation Notes

**Stack:**
- Backend: FastAPI with async/await
- Frontend: React + TypeScript + Tailwind CSS (Module Federation MFE)
- Evaluation Engine: DeepEval, Ragas (with extensibility for MLflow, Deepchecks, Arize Phoenix)
- Database: PostgreSQL with asyncpg driver
- Observability: Built-in trace logging with evaluation results

**Key Implementation Details:**
- Organization-scoped API key management via `model_provider_configs` table
- Runtime dependency injection for evaluation adapters (pass db_session in request)
- Database session passed to evaluations for API key retrieval
- All traces stored with parent-child relationships
- Cost calculated at per-token level with model-specific pricing
- History fully searchable by title and transcript content

**Files:**
- Backend Service: `app/services/call_insights_service.py`
- API Endpoints: `app/api/v1/endpoints/call_insights.py`
- Database Model: `app/models/call_insights.py`
- Frontend Page: `ui-tier/mfe-insights/src/components/InsightsPage.tsx`
- Migration: `alembic/versions/1762fd0c1389_add_system_prompts_and_models_to_call_.py`

### Frontend UI Components

**Location:** `ui-tier/mfe-insights/`

**Component Structure:**
```
mfe-insights/src/
├── components/
│   ├── InsightsPage.tsx           # Main container
│   └── sections/
│       ├── TranscriptInputSection.tsx
│       ├── ParameterConfigSection.tsx    ⭐ Updated with EvaluationSelector
│       ├── ExperimentationSection.tsx    ⭐ Fixed API URL configuration
│       ├── ResultsSection.tsx
│       ├── TracesSection.tsx
│       └── HistorySection.tsx
├── services/
│   └── insightsService.ts         # API client with base URL
└── types/
    └── insights.ts                # TypeScript types
```

**Recent UI Improvements (v2.0):**

1. **EvaluationSelector Integration**
   - **Component:** `ParameterConfigSection.tsx`
   - **Change:** Replaced 2-column checkbox grid with shared `EvaluationSelector` dropdown
   - **Before:** Simple checkbox grid showing 2 evaluations per row
   - **After:** Advanced dropdown with table view, filters (category, source, tags), selected badges
   - **Benefits:** Consistent with Playground UX, better filtering, improved accessibility

2. **API URL Configuration Fix**
   - **Component:** `ExperimentationSection.tsx`
   - **Issue:** Missing `API_BASE_URL` causing fetch to webpack-dev-server instead of API server
   - **Error:** `SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON`
   - **Fix:** Added `const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';`
   - **Impact:** Models dropdown now fetches correctly from `/api/v1/call-insights/models/available`

3. **Design System Compliance**
   - **Background:** Changed from `bg-white` to `bg-neutral-50` (warm gray)
   - **Cards:** Using `rounded-2xl` with `border-neutral-100`
   - **Spacing:** Increased to `p-8` for main container, `gap-6` for sections
   - **Inputs:** All inputs use `h-12` (48px touch targets), `rounded-xl`, `border-neutral-200`
   - **Textareas:** Updated padding from `px-3 py-2` to `px-4 py-3`
   - **Focus States:** `ring-4 ring-[#FF385C]/10` for all interactive elements

4. **Form Field Spacing**
   - **Labels:** `text-sm font-semibold text-neutral-700 mb-2`
   - **Metric Cards:**
     - Label: `text-sm font-medium text-neutral-500 mb-2`
     - Value: `text-3xl font-bold text-neutral-800` (2.14x larger)
   - **Icon Containers:** `bg-neutral-50 p-3 rounded-xl`

**Evaluation Selection Workflow:**

```typescript
// ParameterConfigSection.tsx
import { EvaluationSelector } from '../../../../shared/components/forms/EvaluationSelector';

export const ParameterConfigSection: React.FC<Props> = ({ formState, setFormState }) => {
  const handleEvaluationChange = (ids: string[]) => {
    setFormState(prev => ({ ...prev, selectedEvaluations: ids }));
  };

  return (
    <div>
      {/* Other configuration sections */}

      <EvaluationSelector
        selectedEvaluationIds={formState.selectedEvaluations}
        onSelectionChange={handleEvaluationChange}
      />
    </div>
  );
};
```

**Filter Reset Behavior:**
When user clicks outside the evaluation dropdown:
1. Dropdown closes automatically
2. All filters reset to initial state (all categories, all sources, no tag filter)
3. User's selected evaluations remain preserved
4. Next time dropdown opens, full catalog is visible

**API Base URL Pattern:**
```typescript
// ExperimentationSection.tsx
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const response = await fetch(`${API_BASE_URL}/api/v1/call-insights/models/available`, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('promptforge_access_token')}`,
  },
});
```

**localStorage Keys:**
- `promptforge_access_token` - JWT access token for API authentication
- `promptforge_refresh_token` - JWT refresh token
- `promptforge_sidebar_collapsed` - Sidebar UI state

**Design System Alignment:**
All Insights components now follow the comprehensive design system documented in:
- `/ui-tier/DESIGN_SYSTEM.md` - Complete component specifications
- `/ui-tier/FORM_FIELD_SPECS.md` - Form field spacing formulas
- `/PromptForge_Build_Specs/Phase2_UI_Framework.md` - Framework standards

---

## 📈 8. Example Workflow

1. **User Input:**
   - Enters transcript + optional title
   - (Optional) Customizes DTA parameters
   - (Optional) Selects different models for each stage
   - (Optional) Provides custom system prompts
   - Selects evaluations to run

2. **Backend Processing:**
   - Stage 1: Fact Extraction (temp 0.25, gpt-4o-mini)
   - Stage 2: Reasoning & Insights (temp 0.65, gpt-4o-mini)
   - Stage 3: Summary Synthesis (temp 0.45, gpt-4o-mini)
   - Evaluations run on outputs (Faithfulness, Coherence, etc.)
   - All results saved to database

3. **Results Display:**
   - Summary, Insights, Facts displayed in tabs
   - 3 trace cards showing per-stage metrics
   - Evaluation results table
   - Total cost and token usage

4. **History:**
   - Analysis saved with all configuration
   - Searchable by title or content
   - Can load previous analysis to re-run with different settings

---

## 🎯 9. Current Status (October 2025)

**✅ Completed Features:**
- 3-stage DTA pipeline with customizable temperatures
- Model selection per stage (5 OpenAI models)
- Custom system prompts per stage
- History tracking with search
- Evaluation integration (6 frameworks supported)
- Full tracing and cost tracking
- Experimentation UI for A/B testing
- Organization-scoped API key management

**🚧 Future Enhancements:**
- Presidio PII redaction integration (currently placeholder)
- Batch processing for multiple transcripts
- Export to CSV/PDF
- Comparison view (side-by-side analysis)
- Real-time streaming responses
- Fine-tuning feedback loop
- Advanced analytics dashboard

---

## 📝 10. Testing

### API Tests
```bash
# Run full test suite
docker-compose exec api pytest tests/mfe_insights/test_call_insights_api.py -v

# Test custom prompts and models
docker-compose exec api pytest tests/mfe_insights/test_call_insights_api.py::TestCallInsightsAnalyze::test_analyze_with_custom_system_prompts_and_models -v
```

### Manual Testing
```bash
# Get available models
curl http://localhost:8000/api/v1/call-insights/models/available \
  -H "Authorization: Bearer $TOKEN"

# Run analysis with custom configuration
curl -X POST http://localhost:8000/api/v1/call-insights/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Hi, how can I help you today?...",
    "transcript_title": "Test Call - Customer Support",
    "system_prompts": {
      "stage1_fact_extraction": "You are a precise fact extractor.",
      "stage2_reasoning": "You are a strategic analyst.",
      "stage3_summary": "You are a concise summarizer."
    },
    "models": {
      "stage1_model": "gpt-4o-mini",
      "stage2_model": "gpt-4o",
      "stage3_model": "gpt-4o-mini"
    }
  }'
```

---

**Version:** 2.0
**Last Updated:** October 8, 2025
**Status:** ✅ Production Ready
