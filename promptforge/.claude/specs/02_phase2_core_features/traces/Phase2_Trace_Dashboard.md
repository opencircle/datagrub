
# 🎯 Claude Agent Prompt Definition – Trace Dashboard Experience

## Purpose
This prompt defines how Claude should design, build, and validate the **Trace Dashboard** experience for the PromptForge platform.  
The dashboard visualizes **LLM model invocation traces** and **evaluation metrics** across OpenAI, Anthropic Claude, and other vendors, providing a vendor-neutral, analytics-rich interface.

---

## 🧩 High-Level Objective
Create a modern, developer-friendly **trace monitoring dashboard** that allows users to:
1. View all model invocations in a **tabular trace list view**
2. Inspect details of any trace in a **modal popup**
3. Explore all evaluation metrics (trace-evals) for a given invocation
4. Compare traces for drift, regressions, or cost/performance variance

---

## 🧱 Design Requirements

### 1. Trace Table (Summary View)
- Displays paginated list of all recent model invocations.
- Columns include:
  - Trace ID
  - Timestamp (sortable)
  - Model Name (OpenAI, Claude, etc.)
  - Project Name
  - Prompt ID
  - User / Agent
  - Latency (s)
  - Input Tokens
  - Output Tokens
  - Cost (USD)
  - Status (Success, Error, Retry)
  - Evaluations Run (#)
  - Confidence / Quality Score

### 2. Trace Detail View (Popup / Side Panel)
When a user clicks a row, open a detail view containing:

#### Header Information
| Field | Example |
|-------|----------|
| Trace ID | tr_8f92a... |
| Model Provider | Anthropic |
| Model Version | claude-3.5-sonnet |
| Project | WealthAdvisorChatbot |
| Environment | Production |
| Invocation Type | ChatCompletion |

#### Prompt & Context
- Full input prompt text
- Context variables (e.g., user age, location, risk profile)
- LLM parameters (temperature, top_p, top_k, max_tokens)

#### Response Data
- Raw model output
- Parsed JSON (if schema validated)
- Tokens (input/output)
- Latency & Cost
- Retry count and guardrails applied

#### System Metadata
- API endpoint invoked
- Version tag
- Eval summary overview

---

## 📊 3. Trace-Eval Table (Evaluation Metrics)
Each trace may have multiple evaluations linked via `trace_id → trace_eval`.

| Attribute | Description | Example |
|------------|--------------|----------|
| Evaluation ID | Unique identifier | eval_92bcd |
| Evaluation Name | Groundedness / Faithfulness / Bias | Groundedness |
| Library | Evaluation library | Ragas, DeepEval, MLflow, etc. |
| Category (HHH) | Helpful / Honest / Harmless | Honest |
| Score | Standardized metric (0–1) | 0.87 |
| Threshold | Minimum passing score | 0.80 |
| Result | Pass / Fail | Pass |
| Confidence | Optional confidence rating | 0.93 |
| Execution Time (ms) | Evaluation runtime | 244 |
| Notes / Insights | Text feedback | “Output aligns with evidence.” |

---

## 🖥️ 4. UI/UX Requirements
- Built with **React + TailwindCSS + shadcn/ui components**.
- Paginated table view (default 25 rows/page).
- Client-side filters for:
  - Project, Model, Date Range, Status
- Lazy-loaded modals for trace details (for performance).
- Color-coded status indicators:
  - ✅ Success (Green)
  - ⚠️ Retry (Yellow)
  - ❌ Error (Red)
- Evaluation badges for Pass/Fail in eval summary.

---

## 🔁 5. Data Model Requirements

### Trace Schema
```json
{
  "trace_id": "tr_8f92a...",
  "timestamp": "2025-10-06T18:24:12Z",
  "model_name": "claude-3.5-sonnet",
  "provider": "Anthropic",
  "project_name": "WealthAdvisorChatbot",
  "prompt_id": "prompt_1023_finplan",
  "user_id": "advisor_agent",
  "latency_seconds": 3.21,
  "input_tokens": 823,
  "output_tokens": 192,
  "total_tokens": 1015,
  "cost_usd": 0.0135,
  "status": "Success",
  "eval_count": 4,
  "confidence": 0.89
}
```

**Token Tracking Architecture**:
- **Separate Token Fields**: Traces now store `input_tokens`, `output_tokens`, and `total_tokens` separately
- **Provider Integration**: Both OpenAI and Anthropic providers extract token counts from API responses
  - OpenAI: `usage.prompt_tokens` → `input_tokens`, `usage.completion_tokens` → `output_tokens`
  - Anthropic: `usage.input_tokens` → `input_tokens`, `usage.output_tokens` → `output_tokens`
- **Cost Calculation**: Costs are calculated separately for input and output tokens using provider-specific pricing
- **Implementation**: `ModelExecutionResult` class (app/services/model_provider.py:28-35) returns token breakdown

### Trace Eval Schema
```json
{
  "trace_eval_id": "eval_92bcd",
  "trace_id": "tr_8f92a...",
  "eval_name": "Groundedness",
  "library": "Ragas",
  "category": "Honest",
  "score": 0.87,
  "threshold": 0.8,
  "result": "Pass",
  "confidence": 0.93,
  "execution_time_ms": 244,
  "notes": "Output aligns with context evidence."
}
```

---

## 🔬 6. Evaluation Integration

### Playground Evaluation Workflow
When users invoke prompts in the playground, they can optionally select evaluations to run automatically on the response:

**Request Flow**:
1. User selects evaluations from the **EvaluationSelector** component
2. Playground sends `evaluation_ids` array in the execution request
3. Backend executes the prompt with the selected model
4. Backend automatically runs all selected evaluations on the trace
5. Evaluation results are stored in `trace_evaluations` table

**API Schema Extension**:
```python
class PlaygroundExecutionRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str]
    model: str
    parameters: PlaygroundParameters
    metadata: Optional[PlaygroundMetadata]
    evaluation_ids: Optional[list[str]]  # New field for evaluation integration
```

**Implementation Details** (app/api/v1/endpoints/playground.py:133-193):
- Evaluations execute asynchronously after prompt completion
- Each evaluation is fetched from `evaluation_catalog` table
- Access control: public evaluations or organization-owned evaluations only
- Execution via `EvaluationRegistry` with vendor-specific adapters
- Results stored in `TraceEvaluation` model with full metrics
- **Error Handling**: Evaluation failures log warnings but don't fail the prompt request

**EvaluationSelector UI Component**:
- **Location**: `ui-tier/mfe-playground/src/components/EvaluationSelector.tsx`
- **Features**:
  - Multi-select interface with checkbox controls
  - Comprehensive filtering: category, source, tags
  - Table view with columns: Name, Description, Category, Source, Tags, Type
  - Source-specific badge colors (vendor=blue, custom=purple, promptforge=pink, llm_judge=amber)
  - Empty states: loading skeleton, no evaluations, no filtered results
  - WCAG AAA accessibility (aria-labels, keyboard navigation, high contrast)
  - Clear filters button for quick reset

**Integration Points**:
- `PlaygroundEnhanced.tsx`: State management for `selectedEvaluationIds`
- `playgroundService.ts`: API client includes evaluation_ids in payload
- `TraceService.create_trace()`: Accepts and stores token breakdown and metadata
- `EvaluationRegistry.execute_evaluation()`: Handles vendor-agnostic evaluation execution

---

## ⚙️ 7. Technical Requirements
- Backend: **FastAPI**
- Database: **PostgreSQL**
- Caching: **Redis**
- Pagination handled via API query parameters (`page`, `limit`, `filters`)
- Traces and evaluations fetched asynchronously
- React Query or SWR for frontend caching and state management

---

## 🧪 8. Test Coverage

### Playground API Tests
**Location**: `api-tier/tests/mfe_playground/test_playground_api.py`

**Test Execution**:
- **Test Runner**: `api-tier/scripts/run_tests.sh`
- **Environment**: Docker-based testing with `TEST_DB_HOST=postgres`
- **Database**: Isolated PostgreSQL test database with automatic cleanup
- **Coverage**: 10 tests covering all playground endpoints

**Key Test Cases**:
1. **test_execute_prompt_with_evaluation** (lines 423-556):
   - Creates evaluation in catalog
   - Mocks model provider execution
   - Executes prompt with evaluation_ids
   - Verifies trace creation with token breakdown
   - Validates trace_evaluations table entries
   - Confirms evaluation results (score, passed, category, reason)
   - Tests error handling for failed evaluations

2. **Token Tracking Validation**:
   - Validates `input_tokens`, `output_tokens`, and `total_tokens` in trace records
   - Confirms cost calculation accuracy for both OpenAI and Anthropic models

3. **Integration Tests**:
   - End-to-end workflow: prompt execution → evaluation → result storage
   - Access control: public vs organization-owned evaluations
   - Error resilience: evaluation failures don't break prompt execution

**Test Results**: All 10 tests passing with no regressions

---

## 🔐 9. Security & Compliance
- All traces are tied to tenant workspace (RBAC enforced)
- PII redaction via **Microsoft Presidio**
- Audit trail for trace creation, evaluation, and deletion
- Compliance with SOC2, GDPR, and financial data privacy

---

## 🧠 10. Claude-Specific Agent Instructions
When executing this prompt, Claude should:
1. Build modular components for the trace dashboard.
2. Ensure schema adherence and API integration (mock/live).
3. Follow minimal modern UI like Airbnb or Linear.
4. Simulate data for demo purposes if live API not connected.
5. Generate reusable React components: `TraceTable`, `TraceDetailsModal`, `EvalTable`, `EvaluationSelector`.
6. **Token Tracking**: Always display input/output/total tokens separately for cost transparency
7. **Evaluation UX**: Provide clear evaluation selection interface with filtering and accessibility
8. **Error Resilience**: Handle evaluation failures gracefully without blocking prompt execution

---

## ✅ 11. Deliverables
1. React front-end for Trace Dashboard (componentized)
2. API endpoints for trace retrieval and eval details
3. Test dataset for trace/eval simulation
4. Example user interactions (click trace → open modal → view evals)
5. **EvaluationSelector component** with filtering and accessibility
6. **Token breakdown tracking** in ModelExecutionResult and TraceService
7. **Evaluation integration** in playground execution flow
8. **Comprehensive test coverage** including evaluation workflow tests

---

## 🧩 12. Success Criteria
- Pagination and filtering work seamlessly.
- UI is clean, performant, and responsive.
- Model-agnostic design supporting multiple LLM vendors.
- Evaluation summaries show actionable metrics.
- Trace audit trail is visible and queryable.
- **Token tracking provides granular input/output cost visibility**
- **Evaluation integration seamlessly connects playground → trace → results**
- **EvaluationSelector provides intuitive filtering and accessibility**
- **Test coverage validates all critical workflows with no regressions**

---

## 📝 13. Implementation Status

### ✅ Completed Features

**Token Tracking Enhancement**:
- Separate `input_tokens`, `output_tokens`, `total_tokens` fields in trace model
- Provider-specific token extraction (OpenAI and Anthropic)
- Accurate cost calculation based on input/output pricing
- `ModelExecutionResult` class updated with token breakdown
- `TraceService.create_trace()` accepts optional token parameters
- Implementation: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/services/model_provider.py:28-35, 149-159, 205-219`
- Implementation: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/services/trace_service.py:36-37, 99-100`

**Evaluation Integration in Playground**:
- `evaluation_ids` field added to `PlaygroundExecutionRequest` schema
- Automatic evaluation execution after prompt invocation
- Registry-based evaluation execution with vendor adapters
- Results stored in `trace_evaluations` table with full metrics
- Error handling: evaluation failures logged but don't fail request
- Access control: public evaluations + organization-owned evaluations
- Implementation: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/api/v1/endpoints/playground.py:43, 134-192`

**EvaluationSelector UI Component**:
- Multi-select interface with comprehensive filtering
- Filter controls: category dropdown, source dropdown, tags search, clear button
- Table view: Name, Description, Category, Source, Tags, Type columns
- Source-specific badge colors (vendor/custom/promptforge/llm_judge)
- Empty states: loading, no evaluations, no filtered results
- WCAG AAA accessibility compliance
- Implementation: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-playground/src/components/EvaluationSelector.tsx`

**Test Coverage**:
- `test_execute_prompt_with_evaluation`: Full workflow validation
- Docker-based test execution with isolated PostgreSQL database
- Token tracking validation in all provider tests
- Evaluation integration and error handling tests
- All 10 tests passing with no regressions
- Implementation: `/Users/rohitiyer/datagrub/promptforge/api-tier/tests/mfe_playground/test_playground_api.py:423-556`
- Test runner: `/Users/rohitiyer/datagrub/promptforge/api-tier/scripts/run_tests.sh`

### 🔄 In Progress: Parent-Child Trace Visualization

**Feature:** Enhanced Trace Dashboard with Parent-Child Relationship Visualization

**Status:** Design Complete, Ready for Implementation (Est. 8-10 days)

**Comprehensive Documentation:**
- **Analysis & Design:** `/Users/rohitiyer/datagrub/promptforge/.claude/context/ui_architect_analysis_parent_child_traces.json`
- **Visual Design Spec:** `/Users/rohitiyer/datagrub/promptforge/.claude/context/ui_architect_visual_design_spec.md`
- **Implementation Summary:** `/Users/rohitiyer/datagrub/promptforge/.claude/context/ui_architect_implementation_summary.md`

#### Feature Requirements

**1. Parent-Child Relationship Visualization:**
- **Expandable/Collapsible Rows:** Parent traces show expand icon (ChevronRight/Down)
- **Hierarchical Display:** Child traces appear indented under parent when expanded
- **Visual Indicators:**
  - Parent rows: Bold text, expand icon, aggregated metrics
  - Child rows: Indented (pl-12), lighter text, stage indicator
  - Normal traces: No expand icon, display as current implementation

**2. Trace Source Indicator:**
- **New "Source" Column:** Added after Request ID, before Project
- **Source Badges:**
  - 🔵 "Call Insights" (DTA pipeline traces) - `bg-blue-100 text-blue-800` with Workflow icon
  - 🟣 "Prompt Playground" (playground traces) - `bg-purple-100 text-purple-800` with Sparkles icon
  - ⚪ "Other" (fallback) - `bg-gray-100 text-gray-800`
- **Dropdown Filter:** In FilterBar - "All Sources", "Call Insights", "Prompt Playground"
- **API Parameter:** `source_filter` in GET /api/v1/traces

**3. Parent Trace Aggregation:**
- **Model Name:** Show first child's model OR "Multiple Models" (with tooltip listing all)
- **Total Tokens:** `∑ 4,700` (SUM of all children, blue semibold)
- **Total Cost:** `∑ $0.0141` (SUM of all children, blue semibold)
- **Avg Duration:** `Avg 850ms` (AVERAGE of children)
- **Child Count:** Display in trace name: "DTA Pipeline (3 stages)"

**4. Navigation Behavior:**
- **Expand Icon Click:** Toggle expansion (event.stopPropagation to prevent modal)
- **Parent Row Click:** Open parent trace detail modal with:
  - Aggregated metrics summary
  - Child traces section (clickable to view child details)
  - Link to each child trace
- **Child Row Click:** Open child trace detail modal with:
  - Link to parent trace
  - Stage information display
  - Individual child metrics
- **Default State:** Collapsed (children hidden)

#### Implementation Architecture

**Backend Changes:**

**API Schema Enhancement (`/api-tier/app/schemas/trace.py`):**
```python
# New Schema
class AggregatedTraceData(BaseModel):
    total_tokens: int
    total_cost: float
    model_names: List[str]
    avg_duration_ms: Optional[float] = None

# Enhanced TraceListItem
class TraceListItem(BaseModel):
    # ... existing fields ...

    # NEW FIELDS
    source: Optional[str] = None                          # From trace_metadata.source
    has_children: bool = False                            # Query for children
    child_count: Optional[int] = None                     # COUNT(children)
    children: Optional[List['TraceListItem']] = None      # Eager loaded children
    parent_trace_id: Optional[str] = None                 # From trace_metadata.parent_trace_id
    stage: Optional[str] = None                           # From trace_metadata.stage
    aggregated_data: Optional[AggregatedTraceData] = None # Calculated from children
```

**Query Logic (`/api-tier/app/api/v1/traces.py`):**
```python
# 1. Main query: Exclude child traces from top-level list
# WHERE NOT EXISTS (
#   SELECT 1 FROM traces t2
#   WHERE traces.trace_metadata->>'parent_trace_id' IS NOT NULL
# )

# 2. For each trace, determine if parent:
# SELECT COUNT(*) FROM traces
# WHERE trace_metadata->>'parent_trace_id' = parent_trace.id::text

# 3. If parent, query children and aggregate:
# SELECT
#   SUM(total_tokens) as total_tokens,
#   SUM(total_cost) as total_cost,
#   ARRAY_AGG(DISTINCT model_name) as model_names,
#   AVG(total_duration_ms) as avg_duration_ms
# FROM traces WHERE trace_metadata->>'parent_trace_id' = parent_id

# 4. Add source_filter parameter:
# WHERE trace_metadata->>'source' = source_filter (when provided)
```

**Database Indexes (New Alembic Migration):**
```sql
-- For parent-child queries
CREATE INDEX idx_trace_metadata_parent_trace_id
ON traces USING GIN ((trace_metadata->'parent_trace_id'));

-- For source filtering
CREATE INDEX idx_trace_metadata_source
ON traces USING GIN ((trace_metadata->'source'));
```

**Frontend Changes:**

**TypeScript Interfaces (`/ui-tier/shared/services/traceService.ts`):**
```typescript
export interface AggregatedTraceData {
  total_tokens: number;
  total_cost: number;
  model_names: string[];
  avg_duration_ms?: number;
}

export interface EnhancedTraceListItem extends TraceListItem {
  source?: string;
  has_children: boolean;
  child_count?: number;
  children?: EnhancedTraceListItem[];
  parent_trace_id?: string;
  stage?: string;
  aggregated_data?: AggregatedTraceData;
}
```

**New Component: SourceBadge (`/ui-tier/mfe-traces/src/components/SourceBadge.tsx`):**
```tsx
import { Workflow, Sparkles } from 'lucide-react';

const SourceBadge: React.FC<{ source?: string }> = ({ source }) => {
  const config = {
    call_insights: {
      text: 'Call Insights',
      icon: Workflow,
      className: 'bg-blue-100 text-blue-800 border-blue-200'
    },
    playground: {
      text: 'Prompt Playground',
      icon: Sparkles,
      className: 'bg-purple-100 text-purple-800 border-purple-200'
    }
  }[source] || {
    text: 'Other',
    icon: null,
    className: 'bg-gray-100 text-gray-800 border-gray-200'
  };

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.className}`}>
      {Icon && <Icon className="h-3 w-3" />}
      {config.text}
    </span>
  );
};
```

**Enhanced TracesTable (`/ui-tier/mfe-traces/src/components/TracesTable.tsx`):**
```tsx
const TracesTable: React.FC<Props> = ({ traces, ... }) => {
  const [expandedParents, setExpandedParents] = useState<Set<string>>(new Set());

  const toggleExpand = (traceId: string) => {
    setExpandedParents(prev => {
      const next = new Set(prev);
      next.has(traceId) ? next.delete(traceId) : next.add(traceId);
      return next;
    });
  };

  // Flatten traces: [parent, ...children (if expanded), nextParent, ...]
  const flattenedTraces = traces.flatMap(trace => {
    const rows = [trace];
    if (trace.has_children && expandedParents.has(trace.id) && trace.children) {
      rows.push(...trace.children);
    }
    return rows;
  });

  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className="w-10"></th> {/* Expand icon */}
          <th>Source</th>
          <th>Request ID</th>
          <th>Project</th>
          <th>Status</th>
          <th>Model</th>
          <th className="text-right">Tokens</th>
          <th className="text-right">Cost</th>
          <th className="text-right">Duration</th>
          <th className="text-right">Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {flattenedTraces.map(trace => (
          <TraceRow
            key={trace.id}
            trace={trace}
            isChild={!!trace.parent_trace_id}
            isExpanded={expandedParents.has(trace.id)}
            onToggleExpand={toggleExpand}
            onRowClick={onRowClick}
          />
        ))}
      </tbody>
    </table>
  );
};
```

**Enhanced FilterBar (`/ui-tier/mfe-traces/src/components/FilterBar.tsx`):**
```tsx
// Add source dropdown
<select
  value={sourceFilter}
  onChange={(e) => onSourceFilterChange(e.target.value)}
  className="w-48 px-3 py-2 border border-gray-300 rounded-lg..."
>
  <option value="">All Sources</option>
  <option value="call_insights">Call Insights</option>
  <option value="playground">Prompt Playground</option>
</select>
```

**Enhanced App.tsx (`/ui-tier/mfe-traces/src/App.tsx`):**
```tsx
const [sourceFilter, setSourceFilter] = useState('');

const { data } = useTraces({
  search: searchQuery || undefined,
  model: modelFilter || undefined,
  source_filter: sourceFilter || undefined, // NEW
  sort_by: sortColumnMap[sortColumn],
  sort_direction: sortDirection,
  page: currentPage,
  page_size: pageSize,
});
```

**Enhanced TraceDetailModal (`/ui-tier/mfe-traces/src/components/TraceDetailModal.tsx`):**
```tsx
// Header enhancement
<div className="flex items-center gap-3">
  <SourceBadge source={trace.source} />
  <span className="font-mono">{trace.trace_id}</span>
  <StatusIndicator status={trace.status} />
  {trace.has_children && (
    <span className="text-xs bg-gray-100 px-2 py-1 rounded">
      {trace.child_count} child traces
    </span>
  )}
</div>

// New section for parent traces: Child Traces
{trace.has_children && trace.children && (
  <Section title={`Child Traces (${trace.children.length})`} ...>
    {trace.children.map(child => (
      <div
        key={child.id}
        onClick={() => openChildDetail(child.id)}
        className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
      >
        <div className="flex justify-between">
          <span className="font-medium">{child.stage}</span>
          <span>{child.total_tokens} tokens • ${child.total_cost?.toFixed(4)}</span>
        </div>
      </div>
    ))}

    {/* Aggregation Summary */}
    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="text-sm font-medium text-blue-900">Total Aggregated Metrics</div>
      <div className="grid grid-cols-3 gap-4 mt-2">
        <div>Tokens: <strong>∑ {trace.aggregated_data?.total_tokens}</strong></div>
        <div>Cost: <strong>∑ ${trace.aggregated_data?.total_cost?.toFixed(4)}</strong></div>
        <div>Avg Duration: <strong>{trace.aggregated_data?.avg_duration_ms}ms</strong></div>
      </div>
    </div>
  </Section>
)}

// Header enhancement for child traces
{trace.parent_trace_id && (
  <div className="mt-2 text-sm">
    <span className="text-gray-600">Child of:</span>
    <button
      onClick={() => openParentDetail(trace.parent_trace_id)}
      className="ml-2 text-blue-600 hover:text-blue-800 underline font-mono"
    >
      {trace.parent_trace_id}
    </button>
  </div>
)}
{trace.stage && <div className="text-sm text-gray-500">{trace.stage}</div>}
```

#### Data Flow Example

**Call Insights Pipeline Execution:**
```json
// Parent Trace
{
  "id": "uuid-parent-123",
  "trace_id": "req_abc_parent",
  "name": "DTA Pipeline",
  "source": "call_insights",
  "has_children": true,
  "child_count": 3,
  "aggregated_data": {
    "total_tokens": 4700,
    "total_cost": 0.0141,
    "model_names": ["gpt-4o-mini"],
    "avg_duration_ms": 850
  },
  "children": [
    {
      "id": "uuid-child-1",
      "trace_id": "req_abc_stage1",
      "parent_trace_id": "uuid-parent-123",
      "stage": "Stage 1: Fact Extraction",
      "source": "call_insights",
      "model_name": "gpt-4o-mini",
      "total_tokens": 1500,
      "total_cost": 0.0045,
      "total_duration_ms": 1247
    },
    {
      "id": "uuid-child-2",
      "trace_id": "req_abc_stage2",
      "parent_trace_id": "uuid-parent-123",
      "stage": "Stage 2: Reasoning & Insights",
      "source": "call_insights",
      "model_name": "gpt-4o-mini",
      "total_tokens": 2000,
      "total_cost": 0.0060,
      "total_duration_ms": 892
    },
    {
      "id": "uuid-child-3",
      "trace_id": "req_abc_stage3",
      "parent_trace_id": "uuid-parent-123",
      "stage": "Stage 3: Summary Synthesis",
      "source": "call_insights",
      "model_name": "gpt-4o-mini",
      "total_tokens": 1200,
      "total_cost": 0.0036,
      "total_duration_ms": 412
    }
  ]
}
```

**UI Display:**
```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [v] │ 🔵 Call Insights │ req_abc_parent │ Project A │ ✅ │ gpt-4o-mini │ ∑ 4,700 │ ∑ $0.0141 │ Avg 850ms │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│     │                  │    ├─ req_abc_stage1                │ ✅ │ gpt-4o-mini │ 1,500 │ $0.0045 │ 1247ms │
│     │                  │    │  Stage 1: Fact Extraction                                         │
│     │                  │    ├─ req_abc_stage2                │ ✅ │ gpt-4o-mini │ 2,000 │ $0.0060 │ 892ms  │
│     │                  │    │  Stage 2: Reasoning & Insights                                    │
│     │                  │    └─ req_abc_stage3                │ ✅ │ gpt-4o-mini │ 1,200 │ $0.0036 │ 412ms  │
│     │                  │       Stage 3: Summary Synthesis                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Testing Strategy

**API Tests (`/api-tier/tests/api/v1/test_traces_parent_child.py`):**
```python
def test_list_traces_excludes_child_traces():
    """Child traces should not appear in main list"""

def test_parent_trace_has_children_flag():
    """Parent trace should have has_children=True"""

def test_parent_trace_aggregation():
    """Aggregated data should match sum/avg of children"""

def test_source_filter_call_insights():
    """source_filter='call_insights' returns only DTA pipeline traces"""

def test_source_filter_playground():
    """source_filter='playground' returns only playground traces"""
```

**UI Component Tests (`/ui-tier/mfe-traces/src/components/__tests__/TracesTable.test.tsx`):**
```typescript
describe('TracesTable - Parent-Child', () => {
  it('shows expand icon only for parent traces', () => { ... });
  it('toggles children visibility on expand click', () => { ... });
  it('displays aggregated data for parent traces', () => { ... });
  it('indents child traces with stage indicator', () => { ... });
  it('opens parent detail on parent row click', () => { ... });
  it('opens child detail on child row click', () => { ... });
  it('prevents modal when clicking expand icon', () => { ... });
});
```

**Integration Tests:**
- Execute Call Insights analysis (creates parent + 3 children)
- Verify trace list shows parent with children hidden
- Click expand → verify children appear
- Verify aggregations match calculations
- Click filter → verify correct traces shown
- Click parent → verify detail modal shows aggregated metrics
- Click child → verify detail modal shows parent link and stage

#### Implementation Timeline

**Phase 1: Backend (2-3 days)**
- Create AggregatedTraceData schema
- Enhance TraceListItem schema with new fields
- Update list_traces query logic for parent-child detection
- Add source_filter parameter
- Create database indexes
- Write API tests

**Phase 2: Frontend (3-4 days)**
- Update TypeScript interfaces
- Create SourceBadge component
- Add source filter to FilterBar
- Implement expandable rows in TracesTable
- Update TraceDetailModal for parent/child views
- Update App.tsx state management
- Write UI component tests

**Phase 3: Testing & QA (2 days)**
- Run automated test suite
- Manual testing of all interactions
- Accessibility testing (keyboard, screen reader)
- Responsive design testing
- Bug fixes

**Phase 4: Documentation (1 day)**
- Update API documentation
- Create developer guide for parent-child traces
- Add screenshots/wireframes to docs

**Total Estimated Effort:** 8-10 days (1.5-2 sprints)

#### Success Metrics
- ✅ Parent traces show expand/collapse icon
- ✅ Children appear indented when parent expanded
- ✅ Source badges display correctly (Call Insights, Playground, Other)
- ✅ Aggregated metrics accurate (tokens, cost, avg duration)
- ✅ Navigation works (parent detail, child detail, expand/collapse)
- ✅ Source filtering works correctly
- ✅ Accessible (WCAG AA compliant)
- ✅ Page load time < 2 seconds (with 20 parent traces)
- ✅ No regressions in existing functionality

---

## 12. Implementation Status (October 2025)

### ✅ Completed - Phase 1: Backend Implementation

**API Schema Changes** (`api-tier/app/schemas/trace.py`):
- ✅ Created `AggregatedTraceData` schema with `total_tokens`, `total_cost`, `model_names`, `avg_duration_ms`
- ✅ Enhanced `TraceListItem` with 7 new fields:
  - `source`: Trace source (Call Insights, Playground, Other)
  - `has_children`: Boolean flag for parent traces
  - `child_count`: Number of child traces
  - `children`: List of nested TraceListItem objects
  - `parent_trace_id`: Parent trace ID for child traces
  - `stage`: Stage name for child traces (e.g., "fact_extraction")
  - `aggregated_data`: Aggregated metrics for parent traces

**API Endpoint Updates** (`api-tier/app/api/v1/traces.py`):
- ✅ Updated `list_traces` endpoint to filter out child traces from top-level results
- ✅ Added `source_filter` query parameter (Call Insights, Playground, Other)
- ✅ Implemented child trace querying for each parent
- ✅ Added aggregation logic:
  - Sum of `total_tokens` and `total_cost` from children
  - List of unique `model_names` from children
  - Average `total_duration_ms` from children
- ✅ Hierarchical response structure with nested children

**Database Query Optimization**:
- ✅ Added filter for parent traces: `WHERE trace_metadata->>'parent_trace_id' IS NULL`
- ✅ Added JSON metadata querying for source extraction
- ✅ Source filtering using JSONB operators

### ✅ Completed - Phase 2: Frontend Implementation

**TypeScript Interface Updates** (`ui-tier/shared/services/traceService.ts`):
- ✅ Added `AggregatedTraceData` interface
- ✅ Enhanced `TraceListItem` interface with parent-child fields
- ✅ Added `source_filter` parameter to `getTraces()` method

**New Components**:
- ✅ **SourceBadge** (`ui-tier/mfe-traces/src/components/SourceBadge.tsx`):
  - Blue badge for Call Insights (Layers icon)
  - Purple badge for Playground (FlaskConical icon)
  - Gray badge for Other (HelpCircle icon)

**Updated Components**:
- ✅ **TracesTable** (`ui-tier/mfe-traces/src/components/TracesTable.tsx`):
  - Expandable row functionality with state management
  - Chevron icons (ChevronRight → ChevronDown)
  - Child row rendering with indentation (24px per depth level)
  - Stage indicators for child traces
  - Aggregated data display with symbols (∑ for sum, Ø for average)
  - Model name handling (shows first model + count of additional)
  - Added Tokens and Cost columns
  - Updated column header to "Status / Source"

- ✅ **FilterBar** (`ui-tier/mfe-traces/src/components/FilterBar.tsx`):
  - Added source filter dropdown
  - Options: All Sources, Call Insights, Playground, Other

- ✅ **App** (`ui-tier/mfe-traces/src/App.tsx`):
  - Added `sourceFilter` state
  - Passed `source_filter` to `useTraces` hook
  - Updated FilterBar props
  - Updated empty state message to include source filter

### ✅ Completed - Phase 3: Testing

**API Tests** (`api-tier/tests/test_trace_parent_child.py`):
- ✅ `test_list_traces_with_parent_child_hierarchy`: Validates parent trace with 3 children, aggregation logic
- ✅ `test_list_traces_with_source_filter`: Tests filtering by Call Insights, Playground, Other
- ✅ `test_list_traces_excludes_child_traces`: Ensures child traces don't appear at top level
- ✅ `test_list_traces_standalone_trace`: Validates standalone trace without children
- ✅ `test_trace_detail_shows_correct_evaluations`: Confirms parent has evaluations, child has none

**Test Coverage**:
- Hierarchical data structure validation
- Aggregation calculations (sum, average)
- Source filtering (all 3 sources)
- Parent-child relationship integrity
- Standalone trace handling

### 📋 Remaining - Phase 4: Documentation & QA

**Pending Manual Testing**:
- [ ] End-to-end testing with real Call Insights data
- [ ] Accessibility testing (keyboard navigation, screen readers)
- [ ] Responsive design testing (tablet, mobile)
- [ ] Performance testing with 50+ parent traces

**Pending Documentation**:
- [ ] Add API endpoint documentation with examples
- [ ] Create developer guide for adding new trace sources
- [ ] Add screenshots/wireframes to this spec
- [ ] Update README with parent-child trace architecture

---

### 🔄 Pending Features (Post Parent-Child Implementation)
- Trace comparison functionality for drift detection
- Advanced filtering and search across traces
- Cost analytics and visualization
- Performance metrics dashboard
- Multi-level trace hierarchy (nested parent-child)
- Visual timeline/graph view of parent-child execution

---
