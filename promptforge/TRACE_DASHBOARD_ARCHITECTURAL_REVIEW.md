# Trace Dashboard Architectural Review
**Phase 2 - Trace Dashboard Experience**

**Review Date**: 2025-10-06
**Reviewers**: UX Specialist, UI Architect, API Architect
**Specification**: Phase2_Trace_Dashboard.md

---

## Executive Summary

This architectural review evaluates the Trace Dashboard specification against the existing PromptForge architecture, identifying gaps and providing actionable recommendations for implementation. The dashboard aims to provide vendor-neutral observability for LLM invocations across OpenAI, Anthropic Claude, and other providers.

**Key Findings**:
- **Database Schema**: Requires 8 new fields in Trace model + token tracking at span level
- **API Layer**: Need 1 new detail endpoint + enhanced list response with evaluation counts
- **UI Components**: Build 2 new components (TraceDetailModal, EvaluationResultsTable) + enhance existing TracesTable
- **Design System**: Current implementation already follows Airbnb-style minimalism; needs evaluation badge component
- **Performance**: Recommend Redis caching for trace details + React Query for client-side optimization

**Implementation Effort**: Medium (2-3 weeks for P0 features)

---

## 1. UX/Design Review (UX Specialist Perspective)

### 1.1 Design System Alignment

**Current State**: ✅ Strong foundation
- Existing components follow Airbnb-style minimalism:
  - **Colors**: Primary `#FF385C`, Neutral `#222222` (gray-700), Soft contrast
  - **Typography**: Clean sans-serif, consistent font weights (medium 500, semibold 600, bold 700)
  - **Spacing**: 8px grid system (p-2, p-3, p-4, p-6)
  - **Rounded corners**: 12-16px (`rounded-xl`, `rounded-2xl`)
  - **Shadows**: Soft shadows only (`shadow-sm`, `shadow-2xl`)

**Spec Compliance**: ⚠️ Needs refinement
- Spec requests "minimal modern UI like Airbnb or Linear" → **Already achieved**
- Color-coded status indicators specified → **Partially implemented** (success/error/timeout exist, needs "retry" status)

**Recommendations**:

1. **Status Indicator Enhancement**
   - Add "retry" status to existing `StatusIndicator.tsx`:
     ```typescript
     const config = {
       success: { color: 'text-green-700', bg: 'bg-green-50', label: 'Success', icon: '✓' },
       error: { color: 'text-red-700', bg: 'bg-red-50', label: 'Error', icon: '✗' },
       retry: { color: 'text-amber-700', bg: 'bg-amber-50', label: 'Retry', icon: '⟲' },
       timeout: { color: 'text-gray-700', bg: 'bg-gray-50', label: 'Timeout', icon: '⏱' },
     };
     ```

2. **Evaluation Badge Component**
   - Create `EvaluationBadge.tsx` following existing `Badge.tsx` pattern:
     - **Pass**: `variant="success"` (green)
     - **Fail**: `variant="error"` (red)
     - **Pending**: `variant="warning"` (yellow)
   - Size: `size="sm"` for inline display, `size="md"` for detail view

3. **Color Coding for HHH Categories**
   - **Helpful**: Blue (`bg-blue-100 text-blue-800`)
   - **Honest**: Purple (`bg-purple-100 text-purple-800`)
   - **Harmless**: Green (`bg-green-100 text-green-800`)
   - Consistent with existing evaluation card color scheme

### 1.2 Modal vs Side Panel Decision

**Spec Proposal**: "Detail view (Popup / Side Panel)"

**Analysis**:

| Criteria | Modal (Recommended) | Side Panel |
|----------|---------------------|------------|
| **Information Density** | High - Full screen for complex data | Medium - Constrained width |
| **Evaluation Table** | Better - More horizontal space for metrics | Limited - Requires scrolling |
| **User Context** | Clear focus - Dimmed backdrop | Subtle - Maintains table visibility |
| **Mobile Experience** | Native - Full screen on mobile | Awkward - Narrow on mobile |
| **Existing Pattern** | ✅ ProjectModal, PromptBuilderModal | ❌ None in codebase |

**Recommendation**: **Modal with full-screen option**
- Use existing modal pattern from `ProjectModal.tsx`
- Add "Expand" button for full-screen view (for long prompts/responses)
- Ensure keyboard navigation (Esc to close, Tab for focus management)
- WCAG AAA: `backdrop-blur-sm` with `bg-black/50` (7:1 contrast ratio)

### 1.3 Information Hierarchy

**Spec Requirements**: Display trace header, prompt/context, response, evaluations

**Recommended Layout** (Mobile-first, Progressive Disclosure):

```
┌─────────────────────────────────────────────┐
│ Modal Header (Fixed)                        │
│ Trace ID: tr_8f92a | Model: claude-3.5     │
│ [Expand] [Copy] [Close]                     │
├─────────────────────────────────────────────┤
│ Scrollable Content                          │
│                                             │
│ ▼ Overview (Always Expanded)               │
│   Status • Latency • Cost • Tokens         │
│   Project • Environment • Timestamp        │
│                                             │
│ ▼ Prompt & Context (Collapsible)           │
│   [Syntax-highlighted prompt text]          │
│   Parameters: temp=0.7, max_tokens=1024    │
│                                             │
│ ▼ Response (Collapsible)                   │
│   [Syntax-highlighted response]             │
│   Output tokens: 192                        │
│                                             │
│ ▼ Evaluations (Expanded by default)        │
│   [Table: Eval Name | Score | Result]      │
│   Pass: 3 | Fail: 1 | Avg Score: 0.82     │
│                                             │
│ ▼ System Metadata (Collapsed by default)   │
│   API endpoint, version, retry count       │
└─────────────────────────────────────────────┘
```

**Accessibility**:
- All sections keyboard-navigable (Tab, Space/Enter to expand/collapse)
- Screen reader announcements for expanded/collapsed states
- Focus management: Return focus to table row on close
- Color + icon + text for status (not color alone)

### 1.4 Visual Density & Readability

**Spec Request**: "Comprehensive data in modal"

**Balancing Density**:
1. **Use Collapsible Sections** (reduce initial cognitive load)
2. **Syntax Highlighting** (Prism.js or highlight.js for JSON/prompts)
3. **Tabular Nums** (`tabular-nums` class for metrics alignment)
4. **Generous Whitespace** (follow existing 8px grid: p-4, p-6)
5. **Truncation with Tooltips** (Long strings → `line-clamp-2` + hover tooltip)

**Font Sizes**:
- **Headers**: `text-2xl` (24px) for modal title
- **Section Labels**: `text-sm font-semibold` (14px)
- **Body Text**: `text-sm` (14px) for readability
- **Code/Monospace**: `text-xs font-mono` (12px) for trace IDs, JSON

---

## 2. Database Schema Enhancements (API Architect Perspective)

### 2.1 Gap Analysis

| Spec Field | Current Trace Model | Current Span Model | Gap | Priority |
|------------|---------------------|-------------------|-----|----------|
| `trace_id` | ✅ `trace_id` (String) | - | - | - |
| `timestamp` | ✅ `created_at` (DateTime) | - | - | - |
| `model_name` | ⚠️ Via `model_id` FK | ✅ `model_name` (String) | Need denormalized field | **P0** |
| `provider` | ❌ Not stored | ❌ Not stored | **Missing** | **P0** |
| `project_name` | ✅ Via `project_id` FK | - | - | - |
| `prompt_id` | ✅ `prompt_version_id` FK | - | - | - |
| `user_id` | ❌ Not stored | ❌ Not stored | **Missing** | **P0** |
| `latency_seconds` | ✅ `total_duration_ms` (Float) | ✅ `duration_ms` (Float) | - | - |
| `input_tokens` | ❌ Not at trace level | ✅ `prompt_tokens` (Int) | Need aggregate | **P0** |
| `output_tokens` | ❌ Not at trace level | ✅ `completion_tokens` (Int) | Need aggregate | **P0** |
| `cost_usd` | ✅ `total_cost` (Float) | - | - | - |
| `status` | ✅ `status` (String) | ✅ `status` (String) | - | - |
| `eval_count` | ❌ Not stored | - | **Missing** (computed) | **P1** |
| `confidence` | ❌ Not stored | - | **Missing** | **P2** |
| `environment` | ❌ Not stored | - | **Missing** | **P1** |
| `invocation_type` | ❌ Not stored | - | **Missing** | **P2** |
| `retry_count` | ❌ Not stored | - | **Missing** | **P1** |

### 2.2 Recommended Schema Updates

#### 2.2.1 Trace Model Additions (P0 - Required for MVP)

```python
# app/models/trace.py

class Trace(BaseModel):
    __tablename__ = "traces"

    # ... existing fields ...

    # NEW FIELDS (P0)
    model_name = Column(String(100), index=True)  # Denormalized for query performance
    provider = Column(String(50), index=True)     # openai, anthropic, etc.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    input_tokens = Column(Integer)                # Aggregated from spans
    output_tokens = Column(Integer)               # Aggregated from spans

    # NEW FIELDS (P1 - Important but can be phased)
    environment = Column(String(50), default="production")  # dev, staging, production
    retry_count = Column(Integer, default=0)

    # NEW FIELDS (P2 - Nice to have)
    invocation_type = Column(String(50))          # chat_completion, completion, embedding
    confidence_score = Column(Float)              # Aggregated from evaluations

    # NEW RELATIONSHIP
    user = relationship("User", backref="traces")
```

**Rationale**:
- `model_name` + `provider`: Denormalized for filter performance (avoid JOIN on every list query)
- `user_id`: Required for "User / Agent" column in spec
- `input_tokens` / `output_tokens`: Aggregated at trace level for dashboard display (calculated from spans during trace creation)
- `environment`: Critical for filtering prod vs dev traces
- `retry_count`: Important for reliability analytics

#### 2.2.2 TraceEvaluation Model Enhancements

**Current State**: ✅ Already has required fields
- `score`, `passed`, `reason`, `execution_time_ms` → All present

**Additional Index Recommendation**:
```python
# app/models/evaluation_catalog.py

class TraceEvaluation(BaseModel):
    # ... existing fields ...

    # ADD COMPOSITE INDEX for dashboard queries
    __table_args__ = (
        Index('idx_trace_eval_lookup', 'trace_id', 'evaluation_catalog_id'),
        Index('idx_trace_eval_performance', 'trace_id', 'passed', 'score'),
    )
```

### 2.3 Migration Strategy

**Approach**: Additive schema changes (non-breaking)

1. **Add new nullable columns** with defaults
2. **Backfill existing data** (batch update):
   ```sql
   -- Backfill model_name from AIModel join
   UPDATE traces t
   SET model_name = m.name, provider = m.provider
   FROM ai_models m
   WHERE t.model_id = m.id AND t.model_name IS NULL;

   -- Backfill token aggregates from spans
   UPDATE traces t
   SET
     input_tokens = COALESCE((SELECT SUM(prompt_tokens) FROM spans WHERE trace_id = t.id), 0),
     output_tokens = COALESCE((SELECT SUM(completion_tokens) FROM spans WHERE trace_id = t.id), 0)
   WHERE t.input_tokens IS NULL;
   ```
3. **Make columns non-nullable** after backfill (P0 fields only)

**Risk Assessment**:
- **Low Risk**: Additive changes, existing queries unaffected
- **Performance Impact**: Minimal (new indexes improve query speed)
- **Data Integrity**: Backfill script required for existing traces

---

## 3. API Enhancements (API Architect Perspective)

### 3.1 Existing Endpoints Evaluation

**Current Trace API** (`/app/api/v1/traces.py`):

| Endpoint | Status | Spec Alignment |
|----------|--------|----------------|
| `GET /api/v1/traces` | ✅ Implemented | ✅ Supports search, filters, sorting, pagination |
| `GET /api/v1/traces/{id}` | ✅ Implemented | ⚠️ Missing evaluations in response |
| `POST /api/v1/traces` | ✅ Implemented | ✅ Creates trace with spans |
| `DELETE /api/v1/traces/{id}` | ✅ Implemented | ✅ Organization-scoped deletion |

**Gap**: Detail endpoint doesn't include evaluations

### 3.2 New/Enhanced Endpoints

#### 3.2.1 Enhanced Trace Detail Endpoint (P0)

**Current**:
```python
@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: UUID, include_spans: bool = True)
```

**Enhanced** (includes evaluations):
```python
@router.get("/{trace_id}/detail", response_model=TraceDetailResponse)
async def get_trace_detail(
    trace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive trace details with spans, evaluations, and metadata.
    Optimized for dashboard modal view.
    """
    query = (
        select(Trace)
        .where(Trace.id == trace_id)
        .options(
            selectinload(Trace.spans),
            selectinload(Trace.trace_evaluations).selectinload(
                TraceEvaluation.evaluation_catalog_entry
            ),
            selectinload(Trace.project),
            selectinload(Trace.model),
            selectinload(Trace.prompt_version),
            selectinload(Trace.user),
        )
        .join(Project, Trace.project_id == Project.id)
        .where(Project.organization_id == current_user.organization_id)
    )

    result = await db.execute(query)
    trace = result.scalar_one_or_none()

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    return trace
```

**New Schema** (`app/schemas/trace.py`):
```python
class EvaluationResultItem(BaseModel):
    """Evaluation result for trace detail view"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    eval_name: str                          # From evaluation_catalog_entry.name
    library: Optional[str]                  # From evaluation_catalog_entry (Ragas, DeepEval, etc.)
    category: str                           # From evaluation_catalog_entry.category
    score: Optional[float]                  # 0.0-1.0
    passed: Optional[bool]                  # Pass/Fail for validators
    result_category: Optional[str]          # For classifiers
    reason: Optional[str]                   # Explanation
    execution_time_ms: Optional[float]      # Eval runtime
    threshold: Optional[float]              # From config (if applicable)
    confidence: Optional[float]             # Confidence in result
    status: str                             # completed, failed, pending

class TraceDetailResponse(TraceResponse):
    """Comprehensive trace detail response for modal view"""

    # Include all TraceResponse fields plus:
    project: Optional[ProjectResponse]      # Full project object
    model: Optional[AIModelResponse]        # Full model object (with provider)
    prompt_version: Optional[PromptVersionResponse]  # Full prompt object
    user: Optional[UserResponse]            # User who triggered trace
    evaluations: list[EvaluationResultItem] # All evaluations for this trace

    # Computed fields
    eval_summary: Dict[str, Any]            # { passed: 3, failed: 1, avg_score: 0.82 }
```

**Response Example**:
```json
{
  "id": "uuid-123",
  "trace_id": "tr_8f92a",
  "name": "chat_completion_request",
  "status": "success",
  "model_name": "claude-3.5-sonnet",
  "provider": "anthropic",
  "input_tokens": 823,
  "output_tokens": 192,
  "total_duration_ms": 3210,
  "total_cost": 0.0135,
  "environment": "production",
  "retry_count": 0,
  "created_at": "2025-10-06T18:24:12Z",

  "project": {
    "id": "uuid-456",
    "name": "WealthAdvisorChatbot",
    "organization_id": "uuid-789"
  },

  "user": {
    "id": "uuid-101",
    "email": "advisor_agent@example.com"
  },

  "spans": [
    {
      "span_id": "span_abc",
      "name": "llm_call",
      "span_type": "llm",
      "model_name": "claude-3.5-sonnet",
      "prompt_tokens": 823,
      "completion_tokens": 192,
      "duration_ms": 3100,
      "temperature": 0.7,
      "input_data": { "prompt": "..." },
      "output_data": { "response": "..." }
    }
  ],

  "evaluations": [
    {
      "id": "uuid-202",
      "eval_name": "Groundedness",
      "library": "Ragas",
      "category": "quality",
      "score": 0.87,
      "passed": true,
      "reason": "Output aligns with context evidence.",
      "execution_time_ms": 244,
      "threshold": 0.8,
      "status": "completed"
    },
    {
      "id": "uuid-203",
      "eval_name": "Faithfulness",
      "library": "Ragas",
      "category": "quality",
      "score": 0.93,
      "passed": true,
      "execution_time_ms": 312,
      "status": "completed"
    }
  ],

  "eval_summary": {
    "total": 4,
    "passed": 3,
    "failed": 1,
    "pending": 0,
    "avg_score": 0.82,
    "pass_rate": 0.75
  }
}
```

#### 3.2.2 Enhanced List Endpoint (P1)

**Current**: Returns `TraceListItem` with basic fields

**Enhancement**: Add `eval_count` as computed field

```python
# In list_traces endpoint, add to SELECT:
query = select(
    Trace.id,
    Trace.trace_id,
    # ... existing fields ...
    func.count(TraceEvaluation.id).label("eval_count")
).outerjoin(TraceEvaluation, TraceEvaluation.trace_id == Trace.id)
.group_by(Trace.id, ...)
```

**Updated Schema**:
```python
class TraceListItem(BaseModel):
    # ... existing fields ...
    eval_count: int = 0  # Number of evaluations run
```

### 3.3 Performance Optimization Strategy

#### 3.3.1 Database Query Optimization

**Problem**: Detail endpoint loads 5+ relationships (N+1 query risk)

**Solution**: Use `selectinload` for eager loading (already in enhanced endpoint)

**Additional Optimizations**:
1. **Materialized View** (P2 - For analytics):
   ```sql
   CREATE MATERIALIZED VIEW trace_dashboard_summary AS
   SELECT
     t.id,
     t.trace_id,
     t.model_name,
     t.provider,
     t.status,
     t.total_duration_ms,
     t.total_cost,
     t.input_tokens,
     t.output_tokens,
     t.created_at,
     p.name as project_name,
     u.email as user_email,
     COUNT(te.id) as eval_count,
     AVG(te.score) as avg_eval_score,
     SUM(CASE WHEN te.passed = true THEN 1 ELSE 0 END) as evals_passed
   FROM traces t
   JOIN projects p ON t.project_id = p.id
   LEFT JOIN users u ON t.user_id = u.id
   LEFT JOIN trace_evaluations te ON te.trace_id = t.id
   GROUP BY t.id, p.id, u.id
   WITH DATA;

   -- Refresh every 5 minutes
   CREATE INDEX idx_trace_summary_org ON trace_dashboard_summary (organization_id, created_at DESC);
   ```

2. **Redis Caching** (P1):
   ```python
   # Cache trace detail for 5 minutes
   cache_key = f"trace:detail:{trace_id}"
   cached = await redis.get(cache_key)
   if cached:
       return TraceDetailResponse.parse_raw(cached)

   # ... fetch from DB ...

   await redis.setex(cache_key, 300, trace_detail.json())
   ```

#### 3.3.2 Pagination Strategy

**Spec**: "Paginated table view (default 25 rows/page)"

**Current**: ✅ Already implemented (page, page_size params)

**Recommendation**: Add cursor-based pagination for large datasets (P2)
```python
# For very large trace sets (>100k traces), add cursor option:
@router.get("")
async def list_traces(
    cursor: Optional[str] = None,  # Base64-encoded (timestamp, id)
    page_size: int = 25,
    # ... other params ...
):
    if cursor:
        # Decode cursor to (timestamp, id)
        # Use WHERE (created_at, id) < (cursor_ts, cursor_id)
        # More efficient than OFFSET for deep pagination
```

---

## 4. UI Component Architecture (UI Architect Perspective)

### 4.1 Component Breakdown

#### 4.1.1 Existing Components (Reuse)

| Component | Path | Status | Usage |
|-----------|------|--------|-------|
| `TracesTable` | `mfe-traces/src/components/TracesTable.tsx` | ✅ Ready | List view (needs minor enhancements) |
| `StatusIndicator` | `mfe-traces/src/components/StatusIndicator.tsx` | ⚠️ Enhance | Add "retry" status |
| `FilterBar` | `mfe-traces/src/components/FilterBar.tsx` | ⚠️ Enhance | Add date range, status filters |
| `Pagination` | `mfe-traces/src/components/Pagination.tsx` | ✅ Ready | Already supports page/page_size |
| `Badge` | `shared/components/core/Badge.tsx` | ✅ Ready | Evaluation results, categories |

#### 4.1.2 New Components (Build)

**P0 Components** (Required for MVP):

1. **TraceDetailModal** (`mfe-traces/src/components/TraceDetailModal.tsx`)
   - **Props**:
     ```typescript
     interface TraceDetailModalProps {
       traceId: string;
       isOpen: boolean;
       onClose: () => void;
     }
     ```
   - **Features**:
     - Lazy load trace detail on open (React Query)
     - Collapsible sections (Overview, Prompt, Response, Evaluations, Metadata)
     - Syntax highlighting for JSON (Prism.js)
     - Copy buttons for trace ID, prompt, response
     - Keyboard navigation (Esc to close, Tab for sections)
   - **Design Pattern**: Follow `ProjectModal.tsx` structure
   - **Accessibility**: WCAG AAA (focus trap, screen reader labels, keyboard nav)

2. **EvaluationResultsTable** (`mfe-traces/src/components/EvaluationResultsTable.tsx`)
   - **Props**:
     ```typescript
     interface EvaluationResultsTableProps {
       evaluations: EvaluationResultItem[];
       compact?: boolean; // For modal vs full-page view
     }
     ```
   - **Columns**:
     - Evaluation Name
     - Library (DeepEval, Ragas, etc.)
     - Category (HHH badge)
     - Score (0.00 - 1.00, color-coded: >0.8 green, 0.5-0.8 yellow, <0.5 red)
     - Result (Pass/Fail badge)
     - Execution Time (ms)
     - Reason (truncated, tooltip on hover)
   - **Features**:
     - Sortable columns (score, execution time)
     - Filter by category, result
     - Export to CSV (P2)

**P1 Components** (Important):

3. **TraceComparisonView** (`mfe-traces/src/components/TraceComparisonView.tsx`)
   - Side-by-side comparison of 2-4 traces
   - Diff highlighting for prompts/responses
   - Evaluation score deltas

4. **EvaluationBadge** (`shared/components/core/EvaluationBadge.tsx`)
   - Reusable badge for Pass/Fail/Pending states
   - Consistent with design system

**P2 Components** (Nice-to-have):

5. **TraceChart** (Analytics view with ApexCharts)
6. **CostBreakdown** (Cost per model, per project)

### 4.2 State Management

**Approach**: React Query for server state + Local state for UI

```typescript
// mfe-traces/src/hooks/useTraceDetail.ts
import { useQuery } from '@tanstack/react-query';

interface TraceDetailResponse {
  // ... (matches API schema)
}

export function useTraceDetail(traceId: string | null, isOpen: boolean) {
  return useQuery<TraceDetailResponse>({
    queryKey: ['trace', traceId, 'detail'],
    queryFn: async () => {
      const response = await fetch(`/api/v1/traces/${traceId}/detail`);
      if (!response.ok) throw new Error('Failed to fetch trace');
      return response.json();
    },
    enabled: isOpen && !!traceId, // Only fetch when modal is open
    staleTime: 5 * 60 * 1000,     // Cache for 5 minutes
    retry: 2,
  });
}
```

**Benefits**:
- Automatic caching (no duplicate requests)
- Background refetching (keep data fresh)
- Optimistic updates (for future trace editing)
- Loading/error states managed by React Query

### 4.3 Data Fetching Strategy

**Pattern**: Lazy load detail, eager load list

```typescript
// TraceList.tsx (existing)
const { data: traces, isLoading } = useTraces(filters); // List endpoint

// TraceDetailModal.tsx (new)
const { data: traceDetail, isLoading, error } = useTraceDetail(traceId, isOpen);

// Only fetch detail when modal opens:
<TracesTable onRowClick={(id) => {
  setSelectedTraceId(id);
  setModalOpen(true); // Triggers useTraceDetail fetch
}} />
```

**Cache Strategy**:
- **List**: Refetch on filter change, invalidate on trace creation/deletion
- **Detail**: Cache for 5 minutes, invalidate on trace update

### 4.4 Component Reusability

**Cross-MFE Sharing**:
- `Badge`, `EvaluationBadge` → Move to `/shared/components/core/`
- `TraceDetailModal` → Specific to `mfe-traces`
- `EvaluationResultsTable` → Potentially reused in `mfe-evaluations` (create trace)

**Design Token Consistency**:
```typescript
// shared/theme/tokens.ts
export const traceStatusColors = {
  success: 'text-green-700 bg-green-50',
  error: 'text-red-700 bg-red-50',
  retry: 'text-amber-700 bg-amber-50',
  timeout: 'text-gray-700 bg-gray-50',
} as const;

export const evaluationResultColors = {
  pass: 'success',  // Maps to Badge variant
  fail: 'error',
  pending: 'warning',
} as const;
```

---

## 5. Gap Analysis Table

| Requirement | Current State | Spec Requirement | Recommended Solution | Priority |
|-------------|---------------|------------------|----------------------|----------|
| **Database** |
| Model name at trace level | Via FK join | Denormalized for performance | Add `model_name` column | **P0** |
| Provider name | Not stored | openai, anthropic, etc. | Add `provider` column | **P0** |
| User ID | Not stored | Link to user/agent | Add `user_id` FK | **P0** |
| Input/output tokens | At span level only | Aggregated at trace | Add computed columns | **P0** |
| Environment | Not stored | dev/staging/prod | Add `environment` column | **P1** |
| Retry count | Not stored | Track retries | Add `retry_count` column | **P1** |
| Confidence score | Not stored | Aggregated from evals | Add `confidence_score` column | **P2** |
| **API** |
| Trace detail with evals | Missing evaluations | Include eval results | New `/traces/{id}/detail` endpoint | **P0** |
| Eval count in list | Not computed | Show count in table | Add computed field to list query | **P1** |
| Performance optimization | No caching | Fast modal load | Redis cache for detail | **P1** |
| Cursor pagination | Offset-based only | Support large datasets | Add cursor option | **P2** |
| **UI** |
| Trace detail modal | Not implemented | Full trace info + evals | Build `TraceDetailModal.tsx` | **P0** |
| Evaluation table | Not implemented | Show eval results | Build `EvaluationResultsTable.tsx` | **P0** |
| Retry status | Only success/error/timeout | Add retry indicator | Enhance `StatusIndicator.tsx` | **P0** |
| Collapsible sections | Not in trace UI | Reduce info overload | Add Accordion component | **P0** |
| Syntax highlighting | Not implemented | Readable JSON/code | Integrate Prism.js | **P1** |
| Evaluation badges | Generic Badge | Pass/Fail/Pending | Build `EvaluationBadge.tsx` | **P1** |
| Date range filter | Not in FilterBar | Filter by time | Enhance `FilterBar.tsx` | **P1** |
| Trace comparison | Not implemented | Compare 2+ traces | Build `TraceComparisonView.tsx` | **P2** |
| Export to CSV | Not implemented | Download trace data | Add export button | **P2** |

---

## 6. Implementation Priority Matrix

### P0: Must-Have for MVP (2 weeks)

**Database**:
- [ ] Add `model_name`, `provider`, `user_id`, `input_tokens`, `output_tokens` to Trace model
- [ ] Create migration script with backfill logic
- [ ] Add composite index on `trace_evaluations` (trace_id, passed, score)

**API**:
- [ ] Create `/traces/{id}/detail` endpoint with evaluations
- [ ] Add `TraceDetailResponse` schema
- [ ] Add `EvaluationResultItem` schema

**UI**:
- [ ] Build `TraceDetailModal.tsx` (collapsible sections, copy buttons, keyboard nav)
- [ ] Build `EvaluationResultsTable.tsx` (sortable, filterable)
- [ ] Enhance `StatusIndicator.tsx` (add "retry" status)
- [ ] Add `useTraceDetail` React Query hook
- [ ] Wire up modal open/close to table row clicks

**Time Estimate**: 10 days (1 backend, 1 frontend dev)

### P1: Important (1 week)

**Database**:
- [ ] Add `environment`, `retry_count` columns
- [ ] Optimize list query with denormalized fields

**API**:
- [ ] Add `eval_count` to list response
- [ ] Implement Redis caching for trace detail

**UI**:
- [ ] Build `EvaluationBadge.tsx` component
- [ ] Enhance `FilterBar.tsx` (date range, status filter, environment)
- [ ] Add syntax highlighting (Prism.js)
- [ ] Improve evaluation table with category filters

**Time Estimate**: 5 days

### P2: Nice-to-Have (2+ weeks)

**Database**:
- [ ] Add `confidence_score`, `invocation_type` columns
- [ ] Create materialized view for analytics

**API**:
- [ ] Implement cursor-based pagination
- [ ] Add trace comparison endpoint

**UI**:
- [ ] Build `TraceComparisonView.tsx`
- [ ] Add CSV export functionality
- [ ] Build `TraceChart.tsx` (analytics)
- [ ] Full-screen modal mode

**Time Estimate**: 10+ days

---

## 7. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Performance Degradation** | 🟡 Medium | - Add Redis caching (P1)<br>- Use selectinload for eager loading<br>- Monitor query execution time |
| **Schema Migration Failure** | 🟡 Medium | - Additive changes only (non-breaking)<br>- Test backfill script on staging<br>- Rollback plan ready |
| **Modal UX Complexity** | 🟢 Low | - Follow existing ProjectModal pattern<br>- User testing with collapsible sections<br>- Clear visual hierarchy |
| **Token Aggregation Accuracy** | 🟢 Low | - Unit tests for aggregation logic<br>- Validate against existing span data |
| **Evaluation Load Time** | 🟡 Medium | - Lazy load evaluations (only on modal open)<br>- Cache detail response for 5 minutes |
| **Accessibility Compliance** | 🟢 Low | - Reuse existing accessible patterns<br>- Keyboard nav testing<br>- Screen reader testing |
| **Mobile Experience** | 🟢 Low | - Modal full-screen on mobile<br>- Responsive table with horizontal scroll |

**Legend**: 🔴 High | 🟡 Medium | 🟢 Low

---

## 8. Recommendations Summary

### 8.1 Database

1. **Add 5 critical fields** to Trace model: `model_name`, `provider`, `user_id`, `input_tokens`, `output_tokens`
2. **Backfill existing data** before making fields non-nullable
3. **Add composite indexes** for performance: `(trace_id, evaluation_catalog_id)`, `(trace_id, passed, score)`

### 8.2 API

1. **Create new detail endpoint**: `/api/v1/traces/{id}/detail` with all relationships (spans, evaluations, project, user)
2. **Enhance list endpoint**: Add `eval_count` computed field
3. **Implement Redis caching**: Cache detail response for 5 minutes (reduces DB load)

### 8.3 UI

1. **Build 2 core components**:
   - `TraceDetailModal.tsx`: Follow ProjectModal pattern, collapsible sections, WCAG AAA
   - `EvaluationResultsTable.tsx`: Sortable, filterable, color-coded scores
2. **Enhance existing**:
   - `StatusIndicator`: Add "retry" status
   - `FilterBar`: Add date range, environment filters
3. **Use React Query**: Lazy load detail, cache for 5 minutes, automatic refetching

### 8.4 Design System

1. **Status colors**: success (green), error (red), retry (amber), timeout (gray)
2. **Evaluation badges**: Pass (green), Fail (red), Pending (yellow)
3. **HHH category colors**: Helpful (blue), Honest (purple), Harmless (green)
4. **Modal pattern**: Full-screen option, backdrop blur, keyboard nav (Esc, Tab)

---

## 9. Next Steps

### Immediate Actions (This Sprint)

1. **API Architect**: Create DB migration for P0 fields + detail endpoint
2. **UI Architect**: Build `TraceDetailModal` with mock data
3. **UX Specialist**: Review modal design with stakeholders

### Short-Term (Next Sprint)

1. **Backend**: Implement Redis caching, add eval_count to list
2. **Frontend**: Build `EvaluationResultsTable`, enhance FilterBar
3. **QA**: Integration tests for detail endpoint, E2E tests for modal

### Long-Term (Phase 3)

1. **Analytics**: Materialized views, trace comparison
2. **Export**: CSV download, API for bulk export
3. **Monitoring**: Track query performance, cache hit rates

---

## 10. Conclusion

The Trace Dashboard specification is **well-aligned** with the existing architecture and design system. The primary gaps are:

1. **Database**: Need 5 new fields on Trace model (P0) + 2 additional (P1)
2. **API**: Need 1 new detail endpoint with eager-loaded evaluations (P0)
3. **UI**: Need 2 new components (TraceDetailModal, EvaluationResultsTable) (P0)

**Overall Assessment**: ✅ **Feasible within 2-3 weeks** for P0 features.

The existing foundation (TracesTable, StatusIndicator, Badge, React Query setup) provides a strong base. The recommended approach follows established patterns (ProjectModal for modals, Badge for status indicators, React Query for state management), ensuring consistency and maintainability.

**Recommended Approach**: Phased rollout (P0 → P1 → P2) to deliver value incrementally while managing risk.

---

**Review Status**: ✅ Complete
**Document Version**: 1.0
**Last Updated**: 2025-10-06
