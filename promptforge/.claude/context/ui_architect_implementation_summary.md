# Parent-Child Trace View Enhancement - Implementation Summary

## Quick Reference

**Analysis Date:** 2025-10-08
**Feature:** Parent-Child Trace Relationship Visualization
**Status:** Ready for Implementation
**Estimated Effort:** 8-10 days (1.5-2 sprints)

---

## 1. Current State Analysis

### Existing Components
- **Trace List:** `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/TracesTable.tsx`
- **Trace App:** `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/App.tsx`
- **Trace Detail:** `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/TraceDetailModal.tsx`
- **API Endpoint:** `GET /api/v1/traces` (list) and `GET /api/v1/traces/{id}/detail`

### Existing Parent-Child Implementation
**Location:** `/Users/rohitiyer/datagrub/promptforge/api-tier/app/services/call_insights_service.py`

**How it works:**
1. Call Insights creates a **parent trace** for the DTA pipeline
2. Creates 3 **child traces** for each stage:
   - Stage 1: Fact Extraction
   - Stage 2: Reasoning & Insights
   - Stage 3: Summary Synthesis
3. Links via `trace_metadata`:
   - Parent: `{"source": "call_insights", "stage_count": 3}`
   - Child: `{"parent_trace_id": "<parent_id>", "stage": "Stage 1: ...", "source": "call_insights"}`

### Current Limitations
❌ No visualization of parent-child relationships
❌ No trace source indicator (Call Insights vs Playground)
❌ No parent trace aggregation (tokens, cost from children)
❌ No expandable rows for hierarchical data
❌ Child traces appear as separate entries in the list

---

## 2. Feature Requirements

### ✅ Parent-Child Visualization
- Expandable/collapsible rows for parent traces
- Child traces appear indented under parent when expanded
- Normal traces (no children) display as-is

### ✅ Trace Source Indicator
- New "Source" column with badges:
  - 🔵 "Call Insights" (DTA pipeline traces)
  - 🟣 "Prompt Playground" (playground execution traces)
  - ⚪ "Other" (fallback)
- Dropdown filter in FilterBar

### ✅ Parent Trace Aggregation
- **Model:** First child's model OR "Multiple Models"
- **Total Tokens:** SUM of all children (display: `∑ 12,500`)
- **Total Cost:** SUM of all children (display: `∑ $0.0141`)
- **Avg Duration:** AVG of all children (display: `Avg 850ms`)

### ✅ Navigation Behavior
- Click expand icon → Toggle expansion (children show/hide)
- Click parent row → Show parent trace detail modal
- Click child row → Show child trace detail modal
- Default state: Collapsed

---

## 3. Implementation Plan

### Phase 1: Backend (2-3 days)

**Files to Modify:**
1. `/Users/rohitiyer/datagrub/promptforge/api-tier/app/schemas/trace.py`
2. `/Users/rohitiyer/datagrub/promptforge/api-tier/app/api/v1/traces.py`

**Changes:**

**Step 1.1:** Create `AggregatedTraceData` schema
```python
class AggregatedTraceData(BaseModel):
    total_tokens: int
    total_cost: float
    model_names: List[str]
    avg_duration_ms: Optional[float] = None
```

**Step 1.2:** Enhance `TraceListItem` schema
```python
class TraceListItem(BaseModel):
    # ... existing fields ...

    # NEW FIELDS
    source: Optional[str] = None
    has_children: bool = False
    child_count: Optional[int] = None
    children: Optional[List['TraceListItem']] = None
    parent_trace_id: Optional[str] = None
    stage: Optional[str] = None
    aggregated_data: Optional[AggregatedTraceData] = None
```

**Step 1.3:** Update `list_traces` query logic
```python
# 1. Filter main query to exclude child traces
# WHERE NOT EXISTS (
#   SELECT 1 FROM traces t2
#   WHERE t2.trace_metadata->>'parent_trace_id' = traces.id::text
# )

# 2. For each trace, check if parent
# 3. If parent, query children and aggregate
# 4. Build hierarchical response
```

**Step 1.4:** Add `source_filter` parameter
```python
@router.get("", response_model=TraceListResponse)
async def list_traces(
    # ... existing params ...
    source_filter: Optional[str] = Query(None, description="Filter by source"),
):
    # Add WHERE clause: trace_metadata->>'source' = source_filter
```

**Step 1.5:** Create database indexes
```sql
-- New migration file
CREATE INDEX idx_trace_metadata_parent_trace_id
ON traces USING GIN ((trace_metadata->'parent_trace_id'));

CREATE INDEX idx_trace_metadata_source
ON traces USING GIN ((trace_metadata->'source'));
```

---

### Phase 2: Frontend (3-4 days)

**Files to Modify:**
1. `/Users/rohitiyer/datagrub/promptforge/ui-tier/shared/services/traceService.ts`
2. `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/TracesTable.tsx`
3. `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/FilterBar.tsx`
4. `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/App.tsx`
5. `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/TraceDetailModal.tsx`

**Files to Create:**
6. `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/SourceBadge.tsx`

**Step 2.1:** Update TypeScript interfaces
```typescript
// traceService.ts
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

**Step 2.2:** Create `SourceBadge` component
```tsx
// SourceBadge.tsx
import { Workflow, Sparkles } from 'lucide-react';

const SourceBadge: React.FC<{ source?: string }> = ({ source }) => {
  const config = {
    call_insights: { text: 'Call Insights', icon: Workflow, className: 'bg-blue-100 text-blue-800' },
    playground: { text: 'Prompt Playground', icon: Sparkles, className: 'bg-purple-100 text-purple-800' },
  }[source] || { text: 'Other', icon: null, className: 'bg-gray-100 text-gray-800' };

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.className}`}>
      {Icon && <Icon className="h-3 w-3" />}
      {config.text}
    </span>
  );
};
```

**Step 2.3:** Add source filter to `FilterBar`
```tsx
// FilterBar.tsx - add new dropdown
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

**Step 2.4:** Update `App.tsx` with source filter state
```tsx
const [sourceFilter, setSourceFilter] = useState('');

const { data } = useTraces({
  // ... existing params
  source_filter: sourceFilter || undefined,
});

<FilterBar
  // ... existing props
  sourceFilter={sourceFilter}
  onSourceFilterChange={setSourceFilter}
/>
```

**Step 2.5:** Implement expandable rows in `TracesTable`
```tsx
const [expandedParents, setExpandedParents] = useState<Set<string>>(new Set());

const toggleExpand = (traceId: string) => {
  setExpandedParents(prev => {
    const next = new Set(prev);
    next.has(traceId) ? next.delete(traceId) : next.add(traceId);
    return next;
  });
};

// Flatten traces with children for rendering
const flattenedTraces = traces.flatMap(trace => {
  const rows = [trace];
  if (trace.has_children && expandedParents.has(trace.id) && trace.children) {
    rows.push(...trace.children);
  }
  return rows;
});

// Render rows
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
```

**Step 2.6:** Update `TraceDetailModal`
- Add source badge to header
- Show child traces section if `has_children=true`
- Show parent trace link if `parent_trace_id` exists
- Display stage information for child traces
- Show aggregated metrics for parent traces

---

### Phase 3: Testing (2 days)

**API Tests:**
```python
# test_traces_parent_child.py
def test_list_traces_with_parent_child():
    # Create parent trace
    # Create 3 child traces
    # Assert parent.has_children == True
    # Assert parent.child_count == 3
    # Assert parent.aggregated_data.total_tokens == sum(children.total_tokens)
    # Assert children not in main trace list
```

**UI Component Tests:**
```typescript
// TracesTable.test.tsx
describe('TracesTable - Parent-Child', () => {
  it('shows expand icon for parent traces', () => { ... });
  it('toggles children visibility on expand click', () => { ... });
  it('displays aggregated data for parent traces', () => { ... });
  it('indents child traces correctly', () => { ... });
});
```

**Integration Tests:**
- Execute Call Insights analysis
- Verify UI displays parent with expandable children
- Verify aggregations match backend calculations
- Verify filtering by source works correctly

---

### Phase 4: Documentation (1 day)

**Update:**
1. `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_Trace_Dashboard.md`
   - Add Parent-Child Visualization section
   - Document trace source field
   - Document aggregation logic

2. Create developer guide:
   - How to create parent-child traces
   - Metadata structure requirements
   - Best practices

---

## 4. Key Design Decisions

### ✅ Eager Load Children (Not Lazy Load)
**Decision:** Include children in initial API response
**Rationale:** Better UX, minimal performance impact for typical datasets
**Alternative:** Lazy load endpoint `GET /api/v1/traces/{parent_id}/children` (future optimization)

### ✅ Custom Table (Not TanStack Table)
**Decision:** Enhance existing custom table implementation
**Rationale:** Consistency with codebase, no new dependencies, full control
**Alternative:** TanStack Table v8 (requires significant refactoring)

### ✅ JSON Metadata (No Schema Changes)
**Decision:** Use existing `trace_metadata` JSON field
**Rationale:** No database migrations needed, flexible structure
**Optimization:** Add GIN indexes on JSON fields for performance

### ✅ Source Detection from Metadata
**Decision:** Extract source from `trace_metadata.source`
**Mapping:**
- `call_insights` → "Call Insights" (blue badge)
- `playground` → "Prompt Playground" (purple badge)
- Other/null → "Other" (gray badge)

---

## 5. Visual Design Summary

### Table Columns (Enhanced)
```
| [±] | Source | Request ID | Project | Status | Model | Tokens | Cost | Duration | Timestamp |
```

### Parent Row Example
```
[v] [🔵 Call Insights] req_123... | Project A | ✅ Success | gpt-4o-mini | ∑ 4,700 | ∑ $0.0141 | Avg 850ms | ...
  ├── [Empty] [Empty] child_1... | Project A | ✅ Success | gpt-4o-mini | 1,500 | $0.0045 | 1247ms | ...
  │                    Stage 1: Fact Extraction
  ├── [Empty] [Empty] child_2... | Project A | ✅ Success | gpt-4o-mini | 2,000 | $0.0060 | 892ms | ...
  │                    Stage 2: Reasoning & Insights
  └── [Empty] [Empty] child_3... | Project A | ✅ Success | gpt-4o-mini | 1,200 | $0.0036 | 756ms | ...
                       Stage 3: Summary Synthesis
```

### Source Badges
- 🔵 **Call Insights** - `bg-blue-100 text-blue-800` with Workflow icon
- 🟣 **Prompt Playground** - `bg-purple-100 text-purple-800` with Sparkles icon
- ⚪ **Other** - `bg-gray-100 text-gray-800` (no icon)

### Aggregation Indicators
- Total Tokens: `∑ 4,700` (blue, semibold)
- Total Cost: `∑ $0.0141` (blue, semibold)
- Avg Duration: `Avg 850ms` (normal weight)

---

## 6. Data Flow

### API Request → Response
```
GET /api/v1/traces?source_filter=call_insights

Response:
{
  "traces": [
    {
      "id": "uuid-123",
      "trace_id": "req_abc",
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
          "parent_trace_id": "uuid-123",
          "stage": "Stage 1: Fact Extraction",
          "total_tokens": 1500,
          "total_cost": 0.0045,
          ...
        },
        { ... child 2 ... },
        { ... child 3 ... }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### UI State Flow
```
1. User opens Traces page
   → useTraces() fetches data
   → Receives enhanced TraceListResponse with children

2. User sees parent trace with expand icon
   → Click expand icon
   → toggleExpand(traceId) updates expandedParents Set
   → Component re-renders
   → Children rows appear with indentation

3. User clicks child row
   → onRowClick(childTraceId) fires
   → TraceDetailModal opens with child data
   → Shows parent trace link and stage info
```

---

## 7. Testing Checklist

### Backend Tests ✅
- [ ] Parent trace with children returns correct structure
- [ ] Child traces excluded from main list
- [ ] Aggregated data calculated correctly (tokens, cost, avg duration)
- [ ] Source filter works (`call_insights`, `playground`)
- [ ] Normal traces (no children) still work
- [ ] Database indexes improve query performance

### Frontend Tests ✅
- [ ] Expand icon shows only for parent traces
- [ ] Click expand toggles children visibility
- [ ] Child rows indented and show stage info
- [ ] Source badges render correctly
- [ ] Parent row shows aggregated data
- [ ] Child row shows actual data
- [ ] Click parent row → parent detail modal
- [ ] Click child row → child detail modal
- [ ] Click expand icon → prevents modal opening
- [ ] Source filter dropdown filters traces
- [ ] Keyboard navigation works (Tab, Enter, Arrow keys)
- [ ] Screen reader announces correctly

### Integration Tests ✅
- [ ] Call Insights creates parent + 3 children
- [ ] Parent-child relationship displays in UI
- [ ] Expansion/collapse works smoothly
- [ ] Detail modals show correct data
- [ ] Filtering and pagination work with parent-child traces

---

## 8. Success Criteria

### ✅ Functional Requirements
- Parent traces show expand/collapse icon
- Children appear indented under parent when expanded
- Source badges display correctly (Call Insights, Playground, Other)
- Aggregated metrics accurate (tokens, cost, avg duration)
- Detail modals work for both parent and child traces
- Filtering by source works correctly

### ✅ Non-Functional Requirements
- Page load time < 2 seconds (with 20 parent traces)
- Expansion animation smooth (< 200ms)
- Accessible (WCAG AA compliant)
- Responsive (desktop, tablet, mobile)
- No regressions in existing functionality

### ✅ User Experience
- Intuitive parent-child visualization
- Clear source identification
- Easy navigation between parent and child details
- Aggregated metrics provide quick insights
- No confusion between parent and child traces

---

## 9. Rollout Plan

### Phase 1: Development (Week 1)
- Backend implementation (Days 1-3)
- Frontend implementation (Days 3-5)

### Phase 2: Testing (Week 2)
- Automated tests (Days 1-2)
- Manual QA testing (Days 3-4)
- Bug fixes (Day 5)

### Phase 3: Deployment (Week 3)
- Deploy to staging (Day 1)
- Stakeholder review (Days 2-3)
- Deploy to production (Day 4)
- Monitor and iterate (Day 5)

---

## 10. Future Enhancements

### 🔮 Phase 2 (Post-MVP)
1. **Multi-level Hierarchy:** Support child traces as parents (nested expansion)
2. **Bulk Actions:** Collapse/expand all, delete parent with children
3. **Comparison View:** Compare child traces side-by-side
4. **Export:** Export parent with all children to CSV/JSON
5. **Lazy Loading:** Fetch children on-demand for large datasets
6. **Advanced Filters:** Filter by stage, model used in children, cost range

### 🔮 Long-term
- Visual timeline/graph view of parent-child execution flow
- Cost breakdown by stage in chart format
- Performance analytics across stages
- Custom stage configuration for pipelines

---

## 11. Quick Start Commands

### Run Backend Tests
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
pytest tests/api/v1/test_traces_parent_child.py -v
```

### Run Frontend Dev Server
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces
npm start
```

### Create Database Migration
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
alembic revision -m "add_trace_metadata_indexes"
```

### Run Full Test Suite
```bash
# Backend
cd /Users/rohitiyer/datagrub/promptforge/api-tier
./scripts/run_tests.sh

# Frontend
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces
npm test
```

---

## 12. Key Files Reference

### Backend
```
api-tier/
├── app/
│   ├── schemas/trace.py              # Add AggregatedTraceData, enhance TraceListItem
│   ├── api/v1/traces.py              # Update list_traces logic, add source_filter
│   └── models/trace.py               # (No changes - already has trace_metadata)
├── alembic/versions/
│   └── xxxx_add_trace_metadata_indexes.py  # NEW: Create indexes
└── tests/
    └── api/v1/
        └── test_traces_parent_child.py     # NEW: Test parent-child logic
```

### Frontend
```
ui-tier/
├── shared/services/
│   └── traceService.ts               # Add EnhancedTraceListItem, AggregatedTraceData
└── mfe-traces/src/
    ├── components/
    │   ├── TracesTable.tsx           # Add expandable rows, aggregation display
    │   ├── FilterBar.tsx             # Add source dropdown
    │   ├── TraceDetailModal.tsx      # Add parent/child sections
    │   └── SourceBadge.tsx           # NEW: Source badge component
    ├── App.tsx                       # Add sourceFilter state
    └── __tests__/
        └── TracesTable.test.tsx      # NEW: Test expandable behavior
```

---

## 13. Contacts & Resources

### Documentation
- Full Analysis: `/Users/rohitiyer/datagrub/promptforge/.claude/context/ui_architect_analysis_parent_child_traces.json`
- Visual Design: `/Users/rohitiyer/datagrub/promptforge/.claude/context/ui_architect_visual_design_spec.md`
- Build Spec: `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_Trace_Dashboard.md`

### Related Features
- Call Insights Service: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/services/call_insights_service.py`
- Trace Service: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/services/trace_service.py`

---

**Last Updated:** 2025-10-08
**Status:** ✅ Ready for Implementation
**Next Action:** Review with team and begin Phase 1 (Backend)
