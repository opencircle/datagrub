# Evaluation Dashboard Enhancements - Implementation Plan

**Date**: 2025-10-09
**Priority**: P1 - User Experience Improvements
**Status**: 🚧 In Progress

---

## 🎯 Requirements

### 1. Trace Title Support
- [x] Add `title` field to Playground execution request
- [x] Update `trace_service.create_trace()` to accept title parameter
- [x] Implement fallback: title → project name → source
- [ ] Verify Call Insights uses `transcript_title` for trace name
- [ ] Update error trace creation in playground to pass title

### 2. Evaluation Table Enhancements

#### New Columns
- [ ] **Model Name** - Which model was evaluated
- [ ] **Prompt Title** - Title/name of the prompt that was executed
- [ ] **Timestamp** - When evaluation was run
- [ ] **Vendor Name** - Evaluation library (Ragas, DeepEval, PromptForge, etc.)
- [ ] **Category** - Evaluation category (Helpful, Honest, Harmless)

#### Sorting
- [ ] Default sort: Most recent evaluations first (ORDER BY created_at DESC)
- [ ] Allow sorting by: timestamp, score, evaluation name, category

#### Search Filters
- [ ] Filter by Prompt Title (text search)
- [ ] Filter by Model Name (dropdown)
- [ ] Filter by Vendor/Source (dropdown: PromptForge, Ragas, DeepEval, etc.)
- [ ] Filter by Category (dropdown: Helpful, Honest, Harmless)
- [ ] Filter by Status (Pass/Fail)
- [ ] Date range filter

### 3. Evaluation Detail Modal
- [ ] Click evaluation row → Open detail modal
- [ ] Show full evaluation results
- [ ] Show trace identifier (link to trace view)
- [ ] Show input/output data
- [ ] Show reasoning/explanation
- [ ] Show metadata (execution time, cost, tokens)

---

## 📋 Implementation Steps

### Step 1: ✅ Add Title to Playground (COMPLETED)

**Files Modified**:
- `app/api/v1/endpoints/playground.py` - Added `title` field to request
- `app/services/trace_service.py` - Added title parameter, fallback logic

**Logic**:
```python
# Title priority: user-provided > project name > source
trace_name = title or project.name or metadata.get("source", "playground")
```

### Step 2: Update Evaluation List API

**File**: `app/api/v1/evaluations.py`

**Current Endpoint**: `GET /api/v1/evaluations/list`

**Required Changes**:
```python
@router.get("/list", response_model=EvaluationListResponse)
async def list_evaluations(
    # Existing filters
    project_id: Optional[str] = None,
    status: Optional[str] = None,  # pass, fail

    # NEW filters
    prompt_title: Optional[str] = None,  # Text search on trace.name
    model_name: Optional[str] = None,    # Filter by trace.model_name
    vendor: Optional[str] = None,         # Filter by evaluation.vendor_name
    category: Optional[str] = None,       # Filter by evaluation.category
    start_date: Optional[str] = None,     # ISO timestamp
    end_date: Optional[str] = None,       # ISO timestamp

    # Sorting
    sort_by: str = "timestamp",  # timestamp, score, evaluation_name, category
    sort_direction: str = "desc",  # asc, desc

    # Pagination
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List trace evaluations with enhanced filtering and sorting

    Returns evaluations with:
    - Trace title (from trace.name)
    - Model name (from trace.model_name)
    - Timestamp (trace_evaluation.created_at)
    - Vendor name (evaluation_catalog.vendor_name)
    - Category (evaluation_catalog.category)
    """

    # Build query with joins
    query = (
        select(
            TraceEvaluation.id,
            TraceEvaluation.trace_id,
            TraceEvaluation.score,
            TraceEvaluation.passed,
            TraceEvaluation.reason,
            TraceEvaluation.execution_time_ms,
            TraceEvaluation.created_at,
            TraceEvaluation.status,
            EvaluationCatalog.name.label("evaluation_name"),
            EvaluationCatalog.vendor_name,
            EvaluationCatalog.category,
            EvaluationCatalog.source,
            Trace.name.label("prompt_title"),  # NEW
            Trace.model_name,                   # NEW
            Trace.trace_id.label("trace_identifier"),
        )
        .join(EvaluationCatalog, TraceEvaluation.evaluation_catalog_id == EvaluationCatalog.id)
        .join(Trace, TraceEvaluation.trace_id == Trace.id)
        .join(Project, Trace.project_id == Project.id)
        .where(Project.organization_id == current_user.organization_id)
    )

    # Apply filters
    if prompt_title:
        query = query.where(Trace.name.ilike(f"%{prompt_title}%"))

    if model_name:
        query = query.where(Trace.model_name == model_name)

    if vendor:
        query = query.where(EvaluationCatalog.vendor_name == vendor)

    if category:
        query = query.where(EvaluationCatalog.category == category)

    if status:
        if status == "pass":
            query = query.where(TraceEvaluation.passed == True)
        elif status == "fail":
            query = query.where(TraceEvaluation.passed == False)

    if start_date:
        query = query.where(TraceEvaluation.created_at >= start_date)

    if end_date:
        query = query.where(TraceEvaluation.created_at <= end_date)

    # Apply sorting
    sort_column_map = {
        "timestamp": TraceEvaluation.created_at,
        "score": TraceEvaluation.score,
        "evaluation_name": EvaluationCatalog.name,
        "category": EvaluationCatalog.category,
    }
    sort_column = sort_column_map.get(sort_by, TraceEvaluation.created_at)

    if sort_direction == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))  # Default: most recent first

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    evaluations = [
        EvaluationListItem(
            id=row.id,
            trace_id=row.trace_id,
            trace_identifier=row.trace_identifier,
            prompt_title=row.prompt_title,  # NEW
            model_name=row.model_name,       # NEW
            evaluation_name=row.evaluation_name,
            vendor_name=row.vendor_name,     # NEW
            category=row.category,            # NEW
            score=row.score,
            passed=row.passed,
            reason=row.reason,
            execution_time_ms=row.execution_time_ms,
            status=row.status,
            created_at=row.created_at,       # NEW
        )
        for row in rows
    ]

    return EvaluationListResponse(
        evaluations=evaluations,
        total=total,
        limit=limit,
        offset=offset,
    )
```

### Step 3: Update Evaluation Response Schemas

**File**: `app/schemas/evaluation.py`

```python
class EvaluationListItem(BaseModel):
    """Evaluation list item with enhanced fields"""
    id: UUID
    trace_id: UUID
    trace_identifier: str  # trace.trace_id for lookup

    # NEW FIELDS
    prompt_title: str  # trace.name (user title or project name)
    model_name: Optional[str]  # trace.model_name
    vendor_name: Optional[str]  # evaluation_catalog.vendor_name
    category: Optional[str]  # evaluation_catalog.category
    created_at: datetime  # timestamp for sorting

    # EXISTING FIELDS
    evaluation_name: str
    score: Optional[float]
    passed: Optional[bool]
    reason: Optional[str]
    execution_time_ms: Optional[float]
    status: str  # completed, failed, pending

class EvaluationDetailResponse(BaseModel):
    """Detailed evaluation view for modal"""
    id: UUID
    trace_id: UUID
    trace_identifier: str

    # Trace context
    prompt_title: str
    model_name: str
    project_name: str
    created_at: datetime

    # Evaluation details
    evaluation_name: str
    evaluation_type: str  # llm_based, heuristic
    vendor_name: str
    category: str
    source: str  # PROMPTFORGE, VENDOR, CUSTOM

    # Results
    score: Optional[float]
    threshold: Optional[float]
    passed: Optional[bool]
    reason: Optional[str]
    explanation: Optional[str]

    # Execution metrics
    execution_time_ms: float
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    evaluation_cost: Optional[float]

    # Full data for debugging
    input_data: Optional[Dict]
    output_data: Optional[Dict]
    llm_metadata: Optional[Dict]

    # Trace link
    trace: Optional[TraceMinimal]  # Minimal trace info for navigation
```

### Step 4: Add Evaluation Detail Endpoint

**File**: `app/api/v1/evaluations.py`

```python
@router.get("/{evaluation_id}/detail", response_model=EvaluationDetailResponse)
async def get_evaluation_detail(
    evaluation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed evaluation information with trace context
    """
    query = (
        select(
            TraceEvaluation,
            EvaluationCatalog,
            Trace,
            Project.name.label("project_name"),
        )
        .join(EvaluationCatalog, TraceEvaluation.evaluation_catalog_id == EvaluationCatalog.id)
        .join(Trace, TraceEvaluation.trace_id == Trace.id)
        .join(Project, Trace.project_id == Project.id)
        .where(TraceEvaluation.id == evaluation_id)
        .where(Project.organization_id == current_user.organization_id)
    )

    result = await db.execute(query)
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    trace_eval, eval_catalog, trace, project_name = row

    return EvaluationDetailResponse(
        id=trace_eval.id,
        trace_id=trace.id,
        trace_identifier=trace.trace_id,
        prompt_title=trace.name,
        model_name=trace.model_name,
        project_name=project_name,
        created_at=trace_eval.created_at,
        evaluation_name=eval_catalog.name,
        evaluation_type=eval_catalog.evaluation_type,
        vendor_name=eval_catalog.vendor_name,
        category=eval_catalog.category,
        source=eval_catalog.source,
        score=trace_eval.score,
        threshold=eval_catalog.default_threshold,
        passed=trace_eval.passed,
        reason=trace_eval.reason,
        explanation=trace_eval.explanation,
        execution_time_ms=trace_eval.execution_time_ms,
        input_tokens=trace_eval.input_tokens,
        output_tokens=trace_eval.output_tokens,
        total_tokens=trace_eval.total_tokens,
        evaluation_cost=trace_eval.evaluation_cost,
        input_data=trace_eval.input_data,
        output_data=trace_eval.output_data,
        llm_metadata=trace_eval.llm_metadata,
        trace=TraceMinimal(
            id=trace.id,
            trace_id=trace.trace_id,
            name=trace.name,
            status=trace.status,
        ),
    )
```

---

## 🧪 Test Cases

### File: `tests/test_evaluation_enhancements.py`

```python
import pytest
from datetime import datetime, timedelta

class TestEvaluationEnhancements:
    """Test suite for evaluation dashboard enhancements"""

    @pytest.mark.asyncio
    async def test_evaluation_list_includes_prompt_title(self, client, auth_headers):
        """Test that evaluation list includes prompt title"""
        response = await client.get(
            "/api/v1/evaluations/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        for eval_item in data["evaluations"]:
            assert "prompt_title" in eval_item
            assert "model_name" in eval_item
            assert "vendor_name" in eval_item
            assert "category" in eval_item
            assert "created_at" in eval_item

    @pytest.mark.asyncio
    async def test_evaluation_list_sorted_by_timestamp_desc(self, client, auth_headers):
        """Test that evaluations are sorted by most recent first"""
        response = await client.get(
            "/api/v1/evaluations/list?sort_by=timestamp&sort_direction=desc",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # Verify descending order
        timestamps = [eval["created_at"] for eval in data["evaluations"]]
        assert timestamps == sorted(timestamps, reverse=True)

    @pytest.mark.asyncio
    async def test_evaluation_filter_by_prompt_title(self, client, auth_headers):
        """Test filtering evaluations by prompt title"""
        response = await client.get(
            "/api/v1/evaluations/list?prompt_title=Customer Support",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        for eval_item in data["evaluations"]:
            assert "Customer Support" in eval_item["prompt_title"]

    @pytest.mark.asyncio
    async def test_evaluation_filter_by_vendor(self, client, auth_headers):
        """Test filtering evaluations by vendor name"""
        response = await client.get(
            "/api/v1/evaluations/list?vendor=Ragas",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        for eval_item in data["evaluations"]:
            assert eval_item["vendor_name"] == "Ragas"

    @pytest.mark.asyncio
    async def test_evaluation_detail_includes_trace_info(self, client, auth_headers, test_evaluation_id):
        """Test that evaluation detail includes trace information"""
        response = await client.get(
            f"/api/v1/evaluations/{test_evaluation_id}/detail",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert "trace_identifier" in data
        assert "prompt_title" in data
        assert "trace" in data
        assert data["trace"]["trace_id"] is not None

    @pytest.mark.asyncio
    async def test_playground_with_title_creates_named_trace(self, client, auth_headers):
        """Test that playground execution with title creates properly named trace"""
        response = await client.post(
            "/api/v1/playground/execute",
            headers=auth_headers,
            json={
                "title": "My Custom Test",
                "prompt": "Say hello",
                "model": "gpt-4o-mini",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 50,
                    "top_p": 1.0
                }
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Verify trace was created with custom title
        trace_id = data["trace_id"]
        trace_response = await client.get(
            f"/api/v1/traces/{trace_id}",
            headers=auth_headers
        )
        trace_data = trace_response.json()
        assert trace_data["name"] == "My Custom Test"

    @pytest.mark.asyncio
    async def test_playground_without_title_uses_project_name(self, client, auth_headers):
        """Test that playground without title defaults to project name"""
        response = await client.post(
            "/api/v1/playground/execute",
            headers=auth_headers,
            json={
                "prompt": "Say hello",
                "model": "gpt-4o-mini",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 50,
                    "top_p": 1.0
                }
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Verify trace uses project name as fallback
        trace_id = data["trace_id"]
        trace_response = await client.get(
            f"/api/v1/traces/{trace_id}",
            headers=auth_headers
        )
        trace_data = trace_response.json()
        assert trace_data["name"] != ""  # Should have a name
        assert trace_data["name"] != "playground"  # Should not be generic
```

---

## 📊 Build Specification Updates

**File**: `/Users/rohitiyer/datagrub/PromptForge_Build_Specs/Phase2_Evaluation_Dashboard.md` (NEW)

Content will be created separately with complete UI/UX specifications.

---

## 📁 Files to Modify

### Backend
1. ✅ `app/api/v1/endpoints/playground.py` - Add title field
2. ✅ `app/services/trace_service.py` - Handle title with fallback
3. [ ] `app/api/v1/evaluations.py` - Enhanced list endpoint with filters
4. [ ] `app/api/v1/evaluations.py` - New detail endpoint
5. [ ] `app/schemas/evaluation.py` - Updated response models
6. [ ] `tests/test_evaluation_enhancements.py` - Comprehensive tests

### Frontend
7. [ ] `ui-tier/shared/services/evaluationService.ts` - API client methods
8. [ ] `ui-tier/mfe-evaluations/src/components/EvaluationTable.tsx` - Enhanced table
9. [ ] `ui-tier/mfe-evaluations/src/components/EvaluationDetailModal.tsx` - Detail view
10. [ ] `ui-tier/mfe-evaluations/src/components/EvaluationFilters.tsx` - Filter UI
11. [ ] `ui-tier/mfe-playground/src/components/PlaygroundForm.tsx` - Add title input

---

## Status Summary

- ✅ **Step 1**: Playground title support - COMPLETED
- 🚧 **Step 2**: Evaluation API enhancements - IN PROGRESS
- ⏳ **Step 3**: Response schemas - PENDING
- ⏳ **Step 4**: Detail endpoint - PENDING
- ⏳ **Step 5**: Test cases - PENDING
- ⏳ **Step 6**: Build specification - PENDING
- ⏳ **Step 7**: Frontend implementation - PENDING

**Next Action**: Continue with Step 2 (Evaluation API enhancements)
