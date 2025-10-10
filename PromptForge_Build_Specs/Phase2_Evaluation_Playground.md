# Evaluation Playground Dashboard Specification

**Status**: ✅ Partial Implementation (UI scaffold complete, API routes exist)
**Last Updated**: 2025-10-08
**Version**: 2.0
**Implementation Phase**: Phase 2 - Active Development

## Overview
The **Evaluation Playground** in PromptForge provides a unified interface to view, manage, and create evaluations for prompts and traces. It integrates with both **PromptForge-native**, **vendor**, and **custom** evaluations, ensuring full visibility and governance for model quality assurance.

### Current Implementation Status
- ✅ **UI Framework**: mfe-evaluations with results tab and catalog browser
- ✅ **Design System**: Claude.ai-inspired design with neutral-50 backgrounds, rounded-2xl cards, generous spacing (p-8, gap-6)
- ✅ **Shared EvaluationSelector**: Unified dropdown component used across Playground and Insights
- ✅ **API Routes**: Basic CRUD endpoints at `/api/v1/evaluations`
- ✅ **Evaluation Catalog**: Catalog browser with PromptForge, Vendor, and Custom evaluation support
- ✅ **Filter Reset Behavior**: Dropdown filters reset when clicking outside selection area
- ⚠️ **Custom Evaluations**: Create form needed
- ⚠️ **Execution Engine**: Run evaluation functionality incomplete
- ⚠️ **Trace Integration**: Linking evaluations to traces needs enhancement

---

## Shared Components

### Evaluation Selector Component

**Location**: `/ui-tier/shared/components/forms/EvaluationSelector.tsx`

**Status**: ✅ Implemented and integrated in Playground and Insights

**Purpose**: Provides a unified, accessible dropdown interface for selecting multiple evaluations with advanced filtering capabilities.

**Key Features**:
- **Dropdown Table View**: Displays evaluations in a structured table with columns for Name, Description, Category, Source, Tags, and Type
- **Multi-Select**: Checkbox-based selection with immediate visual feedback
- **Advanced Filters**:
  - Category dropdown (Accuracy, Safety, Compliance, etc.)
  - Source dropdown (Vendor, PromptForge, Custom, LLM Judge)
  - Tags search input (free-text filtering)
  - Clear Filters button shows count of active filters
- **Selected Badges**: Displays selected evaluations as removable badges above the dropdown
- **Click-Outside Behavior**: Automatically closes dropdown and resets filters when user clicks outside the selection area
- **Loading & Empty States**:
  - Loading spinner during API fetch
  - "No evaluations available" when catalog is empty
  - "No evaluations match your filters" with quick clear action
- **Accessibility**: Full keyboard navigation, ARIA labels, screen reader support, 44px touch targets

**Implementation Details**:
```typescript
import { EvaluationSelector } from '../../../shared/components/forms/EvaluationSelector';

const PlaygroundPage = () => {
  const [selectedEvaluationIds, setSelectedEvaluationIds] = useState<string[]>([]);

  return (
    <EvaluationSelector
      selectedEvaluationIds={selectedEvaluationIds}
      onSelectionChange={setSelectedEvaluationIds}
    />
  );
};
```

**Design System Compliance**:
- Neutral-50 page background (warm gray, not white)
- Border-neutral-200 for borders (soft, subtle)
- Primary #FF385C for selections and focus states
- h-10 (40px) for filter inputs, h-12 (48px) reserved for main inputs
- rounded-xl for inputs and buttons
- ring-4 with 10% opacity for focus states
- text-sm for filter labels and options
- Hover effects with transition-all duration-200

**Filter Reset Behavior**:
When a user:
1. Opens the dropdown
2. Applies filters (category, source, tags)
3. Clicks outside the dropdown

The component will:
- Close the dropdown
- Reset all filters to initial state (all categories, all sources, no tag filter)
- Preserve user's selected evaluations
- Clear the "Clear Filters" button

This ensures users always see the full evaluation catalog when re-opening the dropdown.

**Integration Points**:
- **Playground**: Used in `/mfe-playground/src/PlaygroundEnhanced.tsx` for optional evaluation selection during prompt execution
- **Insights**: Used in `/mfe-insights/src/components/sections/ParameterConfigSection.tsx` replacing the previous checkbox grid

**Migration from Checkbox Grid** (Insights):
```typescript
// Before (checkbox grid - removed)
<div className="grid grid-cols-2 gap-3">
  {availableEvaluations.map((evaluation) => (
    <label key={evaluation.id}>
      <input type="checkbox" checked={selected.includes(evaluation.id)} />
      <div>{evaluation.name}</div>
    </label>
  ))}
</div>

// After (shared dropdown)
<EvaluationSelector
  selectedEvaluationIds={formState.selectedEvaluations}
  onSelectionChange={handleEvaluationChange}
/>
```

**Benefits**:
- ✅ Consistent UX across Playground and Insights
- ✅ Single source of truth for evaluation selection logic
- ✅ Better filtering and search capabilities
- ✅ Improved accessibility (WCAG AAA compliant)
- ✅ Easier to maintain and enhance
- ✅ Self-contained data fetching (no prop drilling)

---

## 1. Evaluation List View

### Description
Displays the most recent evaluations run across prompts, playgrounds, and insights.

### Features
- **Table View** listing last 20 evaluations (default).
- **Pagination** controls to retrieve additional records.
- **Search Filters**:
  - `trace_id`
  - `evaluation name`
  - `type` (vendor / promptforge / custom)
  - `model` (e.g., GPT-4o, Claude-3, Qwen2.5)

### Table Columns
| Field | Description |
|--------|--------------|
| **Name** | Display name of the evaluation |
| **Description** | Short description or purpose |
| **Type** | Evaluation category (vendor / promptforge / custom) |
| **Tokens** | Number of tokens processed |
| **Cost ($)** | Approximate evaluation cost |
| **Time Taken (ms)** | Execution time |
| **Model** | Model used for the evaluation |
| **Created At** | Timestamp of evaluation run |

### Behavior
- Evaluations generated from **Prompt Playground** or **Insights** automatically appear here.
- Pagination defaults to 20 rows per page.
- Search dynamically filters results by name, trace_id, or model.

---

## 2. Custom Evaluation Tab

### Description
Lists custom evaluations available in the current organization’s workspace.

### Features
- **Table View** showing top 20 custom evaluations.
- **Pagination** to fetch additional definitions.
- **Search Filters** by name, description, and category.
- **RBAC** enforced — organization users can only view their evaluations.

### Table Columns
| Field | Description |
|--------|--------------|
| **Name** | Custom evaluation name |
| **Category** | Functional grouping (e.g., tone, accuracy, bias) |
| **Model Input** | How to access the model's input (use `{{model_input}}`) |
| **Model Output** | How to access the model's output (use `{{model_output}}`) |
| **Evaluation System Prompt** | System prompt that evaluates model input/output after invocation |
| **Model** | LLM model used for running the evaluation |
| **Created By** | Owner or creator |
| **Last Updated** | Timestamp |

---

## 3. Create New Custom Evaluation

### Description
Allows developers to create new evaluation definitions that run **after model invocation** to assess the model's input and output. Custom evaluations become available platform-wide for their organization.

**Evaluation Flow**: Model invocation → Evaluation receives {{model_input}} and {{model_output}} → Returns score (0-1) and pass/fail

### Inputs
| Field | Type | Description |
|--------|------|-------------|
| **Name** | Text | Name of evaluation |
| **Category** | Dropdown | (e.g., accuracy, groundedness, safety, compliance) |
| **Model Input** | TextArea | Defines how to access the model's input (use `{{model_input}}` or custom variables) |
| **Model Output** | TextArea | Defines how to access the model's output (use `{{model_output}}` or define schema) |
| **Evaluation System Prompt** | TextArea | System prompt that evaluates model input/output after invocation, returns score (0-1) and pass/fail |
| **Model** | Dropdown | LLM to use for running evaluation (default: `gpt-4o-mini`) |

### Behavior
- Upon creation, evaluation definition is stored in **Evaluations Catalog**.
- New evaluations appear in the **Custom Evaluation** tab and become selectable in **Prompt Playground** and **Insights**.
- Evaluations run **after** the model produces output, receiving both input and output for assessment.
- Each evaluation adheres to a **standardized schema** and logging format for trace consistency.

---

## 4. Evaluation Execution and Tracing

### Description
All evaluations follow a unified **evaluation pipeline** to ensure traceability and standardized reporting.

### Execution Flow
1. Triggered from **Prompt Playground**, **Insights**, or API.
2. Evaluation runs via selected model (PromptForge / Vendor / Custom).
3. Standard trace record created in `trace_eval` collection.

### Trace Record Schema
| Field | Type | Description |
|--------|------|-------------|
| **trace_id** | UUID | Unique identifier for the run |
| **evaluation_id** | UUID | Linked evaluation definition |
| **type** | Enum | vendor / promptforge / custom |
| **tokens_used** | Integer | Token count |
| **cost_usd** | Float | Approximate cost |
| **time_taken_ms** | Integer | Duration |
| **model** | String | Model used |
| **input_reference** | String | Hash of evaluated input |
| **output_reference** | String | Hash of generated output |
| **created_at** | Timestamp | Run timestamp |

---

## 5. Security and Data Isolation

- Evaluations are **organization-scoped** — only visible to users within the same workspace.
- All traces and logs are stored under **tenant-specific namespaces** for compliance isolation.
- Audit events recorded for all evaluation CRUD operations.

---

## 6. Integration and API

- **GET /evaluations** → Retrieve evaluation list (supports pagination, filters).
- **POST /evaluations/custom** → Create new custom evaluation.
- **GET /evaluations/custom** → List custom evaluations.
- **POST /evaluations/run** → Run an evaluation manually.
- **GET /traces/evaluations** → Retrieve evaluations by trace ID.

All endpoints require authentication via **API key** or **JWT bearer token**.

---

## 7. Example Evaluation Record (JSON)

```json
{
  "trace_id": "a74b9b6d-91f3-4e8d-9db0-3c9e09b3b624",
  "evaluation_id": "c19ac247-55df-4f71-bd77-efb9b1af5cc4",
  "name": "Groundedness Check",
  "description": "Validates factual grounding of model output against retrieved context.",
  "type": "promptforge",
  "tokens_used": 1420,
  "cost_usd": 0.021,
  "time_taken_ms": 856,
  "model": "gpt-4o-mini",
  "created_at": "2025-10-08T13:32:00Z"
}
```

---

## 8. UI Behavior Summary

| Component | Action | Result |
|------------|---------|---------|
| Search bar | Enter query or trace_id | Filter evaluations dynamically |
| Pagination | Navigate pages | Fetch more results via API |
| “+ Create Custom Evaluation” | Opens modal | Create new evaluation definition |
| Evaluation Row | Click | Opens evaluation detail modal (metadata + trace list) |
| Custom Evaluation Tab | View | Lists all custom evaluations for organization |

---

## 9. Audit and Governance

- Each evaluation creation, modification, or deletion emits an **audit event** stored in `audit_logs`.
- Logs include user ID, timestamp, IP, and operation type.
- Full trace-to-evaluation linkage ensures **compliance-grade traceability**.

---

## 10. Deployment Notes

- **Microfrontend**: `mfe-evaluations`
- **API routes**: `/api/v1/evaluations` and `/api/v1/evaluation-catalog`
- **Integrated frameworks**:
  - DeepEval (3.6.2)
  - Ragas (0.3.6)
  - MLflow (3.4.0)
  - Deepchecks LLM
  - Arize Phoenix
- **Design system**: Airbnb-inspired with #FF385C primary, neutral grays, rounded-xl corners
- **Responsive design**: Desktop/tablet optimized
- **RBAC**: Organization-scoped with user permissions
- **Database**: PostgreSQL with `evaluations`, `evaluation_catalog`, and `trace_evaluations` tables

---

## 11. Technology Stack

### Frontend (`mfe-evaluations`)
- **Framework**: React 18 + TypeScript
- **Build**: Webpack 5 + Module Federation
- **State Management**: React Query for server state
- **Styling**: Tailwind CSS with custom design tokens
- **Icons**: Lucide React
- **Animation**: Framer Motion
- **UI Components**: Shared component library (`/shared/components`)

### Backend (`/api/v1/evaluations`, `/api/v1/evaluation-catalog`)
- **Framework**: FastAPI + Python 3.11
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL
- **Auth**: JWT bearer tokens
- **Evaluation Engines**:
  - PromptForge adapter (6 built-in evaluations)
  - DeepEval adapter
  - Ragas adapter
  - MLflow adapter
  - Deepchecks adapter
  - Arize Phoenix adapter

### Database Schema
**Tables**:
- `evaluations` - Evaluation run history
- `evaluation_catalog` - Available evaluation definitions
- `trace_evaluations` - Link between traces and evaluation results
- `custom_evaluations` - User-created custom evaluation definitions

---

## 12. Implementation Priorities

### Phase 1: Foundation (Current)
- ✅ Basic UI structure with tabs
- ✅ Evaluation catalog browser
- ✅ Stats dashboard
- ✅ Mock data support for development

### Phase 2: Core Features (In Progress)
- 🔄 Custom evaluation creation form
- 🔄 Evaluation execution engine
- 🔄 Real-time status updates
- 🔄 Filtering and search
- 🔄 Pagination for large datasets

### Phase 3: Advanced Features (Planned)
- ⏳ Evaluation comparison view
- ⏳ Historical trend charts
- ⏳ Export evaluation results
- ⏳ Scheduled evaluation runs
- ⏳ Evaluation templates library

---

## 13. Integration Points

### With Prompt Playground
- Users can select evaluations from catalog when executing prompts
- Evaluation results automatically link to prompt execution traces
- Results appear in both Playground and Evaluations dashboard

### With Deep Insights (Call Analysis)
- Insights pipeline can run evaluations on Stage 2 and Stage 3 outputs
- Evaluation results stored with insight analysis traces
- Metrics like faithfulness, coherence, and conciseness tracked per insight

### With Traces Dashboard
- All evaluations create trace records for observability
- Trace metadata includes evaluation type, model, cost, and duration
- Parent-child trace relationships for multi-stage evaluations

---

## 14. Design System Reference

Following PromptForge's Airbnb-inspired design language:

**Colors**:
- Primary: `#FF385C` (vibrant red)
- Secondary: `#0066FF` (bright blue)
- Success: `#00A699` (teal)
- Warning: `#FFB400` (amber)
- Error: `#C13515` (dark red)
- Neutral: `#222222`, `#717171`, `#F7F7F7`

**Typography**:
- Font: Inter/Cereal
- Scale: 12px, 14px, 16px, 18px, 24px, 32px, 48px

**Spacing**:
- 8px grid: 0, 8, 16, 24, 32, 48, 64, 96

**Components**:
- Border radius: 12-16px for cards
- Shadows: Soft only (0 2px 8px rgba(0,0,0,0.08))
- Transitions: 200ms ease for hover states

---

## 15. API Implementation Details

### 15.1 Evaluation List Endpoint

**Endpoint**: `GET /api/v1/evaluations/list`

**Query Parameters**:
- `limit` (int, default: 20, max: 100) - Number of results to return
- `offset` (int, default: 0) - Offset for pagination
- `trace_id` (UUID, optional) - Filter by specific trace
- `name` (string, optional) - Fuzzy search on evaluation name
- `type` (string, optional) - Filter by type: `vendor` | `promptforge` | `custom`
- `model` (string, optional) - Filter by model name
- `created_after` (datetime, optional) - Filter by creation date (after)
- `created_before` (datetime, optional) - Filter by creation date (before)

**Response**: `EvaluationListResponse`
```json
{
  "evaluations": [
    {
      "id": "uuid",
      "name": "Faithfulness Check",
      "description": "Validates factual accuracy",
      "type": "promptforge",
      "status": "completed",
      "trace_id": "uuid",
      "project_id": "uuid",
      "model": "gpt-4o-mini",
      "avg_score": 0.85,
      "total_tests": 1,
      "passed_tests": 1,
      "total_tokens": 450,
      "total_cost": 0.0023,
      "duration_ms": 856.3,
      "created_at": "2025-10-08T19:00:00Z"
    }
  ],
  "total": 156,
  "limit": 20,
  "offset": 0
}
```

**Implementation**:
- File: `api-tier/app/api/v1/evaluations.py:119-233`
- Joins `trace_evaluations` with `evaluation_catalog`
- Organization-scoped filtering (user's org + public evaluations)
- Supports fuzzy search on evaluation name (ILIKE)
- Orders by `created_at DESC`

### 15.2 Evaluation Execution Endpoint

**Endpoint**: `POST /api/v1/evaluations/run`

**Request**: `EvaluationRunRequest`
```json
{
  "evaluation_ids": ["uuid1", "uuid2"],
  "trace_id": "uuid",
  "model_override": "gpt-4o"  // optional
}
```

**Response**: `List[EvaluationRunResult]`
```json
[
  {
    "evaluation_id": "uuid1",
    "evaluation_name": "Faithfulness Check",
    "trace_id": "child-trace-uuid",
    "score": 0.85,
    "passed": true,
    "reason": "Output is factually grounded in the input context.",
    "status": "completed",
    "error_message": null,
    "metadata": {
      "model": "gpt-4o-mini",
      "tokens": 450,
      "cost": 0.0023,
      "duration_ms": 856.3
    }
  }
]
```

**Implementation**:
- File: `api-tier/app/api/v1/evaluations.py:236-289`
- Service: `api-tier/app/services/evaluation_execution_service.py`
- Schema: `api-tier/app/schemas/evaluation_execution.py`

**Execution Flow**:
1. Fetch parent trace input/output from database
2. For each evaluation:
   - Load evaluation definition from catalog
   - Execute via appropriate adapter (PromptForge/Vendor/Custom)
   - Create child trace for evaluation execution
   - Store result in `trace_evaluations` table
3. Return evaluation results with scores, pass/fail, reasons

**Trace Integration**:
- Each evaluation creates a child trace under the parent trace
- Trace metadata includes: `evaluation_id`, `type`, `model`, `tokens`, `cost`, `duration`
- Parent-child relationships maintained for observability

### 15.3 Custom Evaluation Creation

**Endpoint**: `POST /api/v1/evaluation-catalog/custom`

**Concept**: Custom evaluations run **after model invocation** to assess the model's input and output.

**Request**: `CustomEvaluationCreate`
```json
{
  "name": "Custom Tone Analysis",
  "category": "tone",
  "description": "Analyzes tone and sentiment of model responses",
  "prompt_input": "{{model_input}}",
  "prompt_output": "{{model_output}}",
  "system_prompt": "You are an expert evaluator. Analyze the model's input and output to assess tone consistency.\n\nModel Input: {{model_input}}\nModel Output: {{model_output}}\n\nReturn a JSON with:\n- score: float 0-1 (1 = perfect tone)\n- passed: boolean (true if score >= 0.7)\n- reason: explanation of the assessment",
  "model": "gpt-4o-mini"
}
```

**Response**: `CustomEvaluationResponse`
```json
{
  "id": "uuid",
  "name": "Custom Tone Analysis",
  "category": "tone",
  "description": "Analyzes tone and sentiment of model responses",
  "source": "custom",
  "created_by": "user-uuid",
  "created_at": "2025-10-08T19:00:00Z"
}
```

**Terminology**:
- `prompt_input`: Defines how to access the model's input (use `{{model_input}}`)
- `prompt_output`: Defines how to access the model's output (use `{{model_output}}`)
- `system_prompt`: Evaluation logic that runs after model invocation, receives model input/output

**Implementation**:
- File: `api-tier/app/api/v1/evaluation_catalog.py`
- Stores in `evaluation_catalog` table with `source='custom'`
- Organization-scoped (only visible to user's organization)
- Validation: Name (3-255 chars), prompts (min 10 chars)

### 15.4 Database Schema

**Table: `trace_evaluations`**
```sql
CREATE TABLE trace_evaluations (
    id UUID PRIMARY KEY,
    trace_id UUID NOT NULL REFERENCES traces(id),
    evaluation_catalog_id UUID NOT NULL REFERENCES evaluation_catalog(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),

    -- Evaluation Results
    score FLOAT,
    passed BOOLEAN,
    category VARCHAR(255),
    reason TEXT,

    -- Execution Metadata
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    model_used VARCHAR(100),
    execution_time_ms FLOAT,
    config JSON,

    -- Cost Tracking
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    evaluation_cost DECIMAL(10,6),

    -- Detailed Metrics
    llm_metadata JSONB,      -- Comprehensive LLM metrics
    vendor_metrics JSONB,    -- Vendor-specific metrics
    details JSON,
    suggestions JSON,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
- `idx_trace_eval_trace` ON `trace_id`
- `idx_trace_eval_org` ON `organization_id`
- `idx_trace_eval_catalog` ON `evaluation_catalog_id`
- `idx_trace_eval_created` ON `created_at DESC`
- `idx_trace_eval_model` ON `model_used`
- `idx_trace_eval_org_created` ON `organization_id, created_at DESC` (composite)
- `idx_trace_eval_vendor_metrics` ON `vendor_metrics` (GIN)
- `idx_trace_eval_llm_metadata` ON `llm_metadata` (GIN)

**Table: `evaluation_catalog`**
```sql
CREATE TABLE evaluation_catalog (
    id UUID PRIMARY KEY,

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category ENUM(EvaluationCategory) NOT NULL,

    -- Source and Type
    source ENUM(EvaluationSource) NOT NULL,  -- vendor, custom, promptforge, llm_judge
    evaluation_type ENUM(EvaluationType) NOT NULL,  -- metric, validator, classifier, judge

    -- Multi-tenancy
    organization_id UUID REFERENCES organizations(id),
    project_id UUID REFERENCES projects(id),
    is_public BOOLEAN DEFAULT FALSE,

    -- Configuration
    config_schema JSON,
    default_config JSON,

    -- Implementation Details
    implementation TEXT,
    adapter_class VARCHAR(255),
    adapter_evaluation_id VARCHAR(255),
    vendor_name VARCHAR(100),

    -- LLM-as-Judge Fields
    llm_criteria TEXT,
    llm_model VARCHAR(100),
    llm_system_prompt TEXT,

    -- Custom Evaluation Fields
    prompt_input TEXT,              -- Input template with {{variables}}
    prompt_output TEXT,             -- Expected output schema
    custom_system_prompt TEXT,      -- System prompt for custom evals
    created_by UUID REFERENCES users(id),

    -- Metadata
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT TRUE,
    tags JSON,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes on evaluation_catalog**:
- `idx_eval_catalog_name` ON `name`
- `idx_eval_catalog_category` ON `category`
- `idx_eval_catalog_source` ON `source`
- `idx_eval_catalog_evaluation_type` ON `evaluation_type`
- `idx_eval_catalog_org` ON `organization_id`
- `idx_eval_catalog_project` ON `project_id`
- `idx_eval_catalog_is_public` ON `is_public`
- `idx_eval_catalog_is_active` ON `is_active`
- `idx_eval_catalog_vendor_name` ON `vendor_name`
- `idx_eval_catalog_created_by` ON `created_by`
- `idx_eval_catalog_adapter_eval_id` ON `adapter_evaluation_id`

### 15.5 Component Implementation

**UI Components Created**:

1. **CreateCustomEvaluationModal**
   - File: `ui-tier/mfe-evaluations/src/components/CustomEvaluationForm/CreateCustomEvaluationModal.tsx`
   - Form with validation for name, category, description, prompts, model
   - Follows Airbnb design system with #FF385C primary color
   - WCAG AAA accessible with proper focus management

2. **FilterBar**
   - File: `ui-tier/mfe-evaluations/src/components/EvaluationList/FilterBar.tsx`
   - Search input with 500ms debounce
   - Type, Model, Date range filters
   - Responsive design (stacks on mobile)

3. **Pagination**
   - File: `ui-tier/mfe-evaluations/src/components/EvaluationList/Pagination.tsx`
   - Previous/Next navigation
   - Rows per page selector (10, 20, 50, 100)
   - Results count display

4. **EvaluationDetailModal**
   - File: `ui-tier/mfe-evaluations/src/components/EvaluationDetail/EvaluationDetailModal.tsx`
   - Score visualization with color-coded progress bar
   - Input/output comparison
   - Metadata display (tokens, cost, duration)
   - View Trace and Rerun buttons

**Service Layer**:
- File: `ui-tier/shared/services/evaluationService.ts`
- Methods:
  - `getEvaluations(filters)` - Fetch filtered evaluation list
  - `createCustomEvaluation(data)` - Create custom evaluation
  - `runEvaluations({ evaluation_ids, trace_id, model_override })` - Execute evaluations

**Type Definitions**:
- File: `ui-tier/mfe-evaluations/src/types/customEvaluation.ts`
- Interfaces: `CustomEvaluationCreate`, `EvaluationFilters`, `EvaluationResultDetailed`

### 15.6 Integration Points

**App.tsx Updates**:
- Added state for modal visibility, filters, pagination, selected evaluation
- Integrated all new components (CreateCustomEvaluationModal, FilterBar, Pagination, EvaluationDetailModal)
- Event handlers for create, filter, page change, evaluation click, view trace, rerun
- "+ Create Custom Evaluation" button on catalog tab

**Current Implementation Status**:
- ✅ GET /evaluations/list with filtering and pagination
- ✅ POST /evaluations/run execution engine
- ✅ POST /evaluation-catalog/custom creation
- ✅ Custom evaluation form modal
- ✅ Filter bar with search and dropdowns
- ✅ Pagination controls
- ✅ Evaluation detail modal
- ✅ Trace integration with child traces
- ✅ App.tsx integration complete

---

**Filename:** `Phase2_Evaluation_Playground.md`
**Module:** `mfe-evaluations`
**Purpose:** Standardize management, visibility, and execution of evaluation workflows in PromptForge.
**Dependencies**: Phase2_UI_Framework.md, Phase2_APIs.md, Phase2_Evaluation_Framework.md
**Last Implementation Update**: 2025-10-08 19:30 (UI + API implementation complete)
