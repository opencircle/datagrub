"""
Trace endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.trace import Trace, Span
from app.models.project import Project
from app.models.model import AIModel
from app.models.user import User
from app.models.evaluation_catalog import TraceEvaluation, EvaluationCatalog
from app.schemas.trace import (
    TraceCreate,
    TraceResponse,
    SpanCreate,
    TraceListResponse,
    TraceListItem,
    TraceDetailResponse,
    EvaluationResultItem,
)
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def create_trace(
    trace_in: TraceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new trace with spans (organization scoped)
    """
    # Verify project belongs to user's organization
    project_query = (
        select(Project)
        .where(Project.id == trace_in.project_id)
        .where(Project.organization_id == current_user.organization_id)
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied",
        )

    # Create trace
    trace_data = trace_in.model_dump(exclude={"spans"})
    trace = Trace(**trace_data)

    db.add(trace)
    await db.flush()

    # Create spans if provided
    if trace_in.spans:
        for span_data in trace_in.spans:
            span = Span(
                **span_data.model_dump(),
                trace_id=trace.id,
            )
            db.add(span)

    await db.commit()

    # Refresh with spans loaded
    await db.refresh(trace)
    query = select(Trace).where(Trace.id == trace.id).options(selectinload(Trace.spans))
    result = await db.execute(query)
    trace = result.scalar_one()

    return trace


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: UUID,
    include_spans: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get trace by ID (organization scoped)
    """
    query = (
        select(Trace)
        .join(Project, Trace.project_id == Project.id)
        .where(Trace.id == trace_id)
        .where(Project.organization_id == current_user.organization_id)
    )

    if include_spans:
        query = query.options(selectinload(Trace.spans))

    result = await db.execute(query)
    trace = result.scalar_one_or_none()

    if trace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found",
        )

    return trace


@router.get("/{trace_id}/detail", response_model=TraceDetailResponse)
async def get_trace_detail(
    trace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive trace details with evaluations, spans, and metadata
    (organization scoped)
    """
    # Build query with all necessary joins and eager loading
    query = (
        select(
            Trace.id,
            Trace.trace_id,
            Trace.name,
            Trace.status,
            Trace.project_id,
            Trace.prompt_version_id,
            Trace.model_id,
            Trace.model_name,
            Trace.provider,
            Trace.user_id,
            Trace.environment,
            Trace.input_data,
            Trace.output_data,
            Trace.trace_metadata,
            Trace.total_duration_ms,
            Trace.input_tokens,
            Trace.output_tokens,
            Trace.total_tokens,
            Trace.total_cost,
            Trace.retry_count,
            Trace.error_message,
            Trace.error_type,
            Trace.created_at,
            Trace.updated_at,
            Project.name.label("project_name"),
            User.email.label("user_email"),
        )
        .join(Project, Trace.project_id == Project.id)
        .outerjoin(User, Trace.user_id == User.id)
        .where(Trace.id == trace_id)
        .where(Project.organization_id == current_user.organization_id)
    )

    result = await db.execute(query)
    row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found",
        )

    # Load spans
    spans_query = (
        select(Span)
        .where(Span.trace_id == row.id)
        .order_by(Span.start_time)
    )
    spans_result = await db.execute(spans_query)
    spans = spans_result.scalars().all()

    # Load evaluations with catalog information
    evals_query = (
        select(
            TraceEvaluation.id,
            EvaluationCatalog.name.label("evaluation_name"),
            EvaluationCatalog.source.label("evaluation_source"),
            EvaluationCatalog.evaluation_type.label("evaluation_type"),
            EvaluationCatalog.category,
            EvaluationCatalog.vendor_name,
            TraceEvaluation.score,
            TraceEvaluation.passed,
            TraceEvaluation.category.label("category_result"),
            TraceEvaluation.reason,
            TraceEvaluation.execution_time_ms,
            TraceEvaluation.input_tokens,
            TraceEvaluation.output_tokens,
            TraceEvaluation.total_tokens,
            TraceEvaluation.evaluation_cost,
            TraceEvaluation.llm_metadata,
            TraceEvaluation.status,
        )
        .join(EvaluationCatalog, TraceEvaluation.evaluation_catalog_id == EvaluationCatalog.id)
        .where(TraceEvaluation.trace_id == row.id)
        .order_by(EvaluationCatalog.category, EvaluationCatalog.name)
    )
    evals_result = await db.execute(evals_query)
    eval_rows = evals_result.all()

    # Convert evaluation rows to EvaluationResultItem objects
    evaluations = [
        EvaluationResultItem(
            id=eval_row.id,
            evaluation_name=eval_row.evaluation_name,
            evaluation_source=eval_row.evaluation_source,
            evaluation_type=eval_row.evaluation_type,
            category=eval_row.category,
            vendor_name=eval_row.vendor_name,
            score=eval_row.score,
            passed=eval_row.passed,
            category_result=eval_row.category_result,
            reason=eval_row.reason,
            execution_time_ms=eval_row.execution_time_ms,
            input_tokens=eval_row.input_tokens,
            output_tokens=eval_row.output_tokens,
            total_tokens=eval_row.total_tokens,
            evaluation_cost=eval_row.evaluation_cost,
            llm_metadata=eval_row.llm_metadata,
            status=eval_row.status,
        )
        for eval_row in eval_rows
    ]

    # Load child traces (for multi-stage workflows)
    from app.schemas.trace import ChildTraceItem
    children_query = (
        select(
            Trace.id,
            Trace.trace_id,
            Trace.status,
            Trace.model_name,
            Trace.provider,
            Trace.input_data,
            Trace.output_data,
            Trace.total_duration_ms,
            Trace.input_tokens,
            Trace.output_tokens,
            Trace.total_tokens,
            Trace.total_cost,
            Trace.trace_metadata,
            Trace.created_at,
        )
        .where(Trace.trace_metadata.op('->>')('parent_trace_id') == row.trace_id)
        .order_by(Trace.created_at)
    )
    children_result = await db.execute(children_query)
    child_rows = children_result.all()

    # Convert child rows to ChildTraceItem objects
    children = [
        ChildTraceItem(
            id=child_row.id,
            trace_id=child_row.trace_id,
            stage=child_row.trace_metadata.get("stage") if child_row.trace_metadata else None,
            status=child_row.status,
            model_name=child_row.model_name,
            provider=child_row.provider,
            input_data=child_row.input_data,
            output_data=child_row.output_data,
            total_duration_ms=child_row.total_duration_ms,
            input_tokens=child_row.input_tokens,
            output_tokens=child_row.output_tokens,
            total_tokens=child_row.total_tokens,
            total_cost=child_row.total_cost,
            created_at=child_row.created_at,
        )
        for child_row in child_rows
    ]

    # Build TraceDetailResponse
    trace_detail = TraceDetailResponse(
        id=row.id,
        trace_id=row.trace_id,
        name=row.name,
        status=row.status,
        project_id=row.project_id,
        project_name=row.project_name,
        prompt_version_id=row.prompt_version_id,
        model_id=row.model_id,
        model_name=row.model_name,
        provider=row.provider,
        user_id=row.user_id,
        user_email=row.user_email,
        environment=row.environment,
        input_data=row.input_data,
        output_data=row.output_data,
        trace_metadata=row.trace_metadata,
        total_duration_ms=row.total_duration_ms,
        input_tokens=row.input_tokens,
        output_tokens=row.output_tokens,
        total_tokens=row.total_tokens,
        total_cost=row.total_cost,
        retry_count=row.retry_count,
        error_message=row.error_message,
        error_type=row.error_type,
        created_at=row.created_at,
        updated_at=row.updated_at,
        spans=spans,
        evaluations=evaluations,
        children=children if children else None,
    )

    return trace_detail


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trace(
    trace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete trace (organization scoped)
    """
    query = (
        select(Trace)
        .join(Project, Trace.project_id == Project.id)
        .where(Trace.id == trace_id)
        .where(Project.organization_id == current_user.organization_id)
    )

    result = await db.execute(query)
    trace = result.scalar_one_or_none()

    if trace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found",
        )

    await db.delete(trace)
    await db.commit()


@router.get("", response_model=TraceListResponse)
async def list_traces(
    search: Optional[str] = Query(None, description="Search by trace_id, project name, or user email"),
    model: Optional[str] = Query(None, description="Filter by model name"),
    status_filter: Optional[str] = Query(None, description="Filter by status (success, error, timeout)"),
    source_filter: Optional[str] = Query(None, description="Filter by trace source (Call Insights, Playground, Other)"),
    sort_by: Optional[str] = Query("timestamp", description="Sort by: requestId, status, duration, timestamp"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List traces with search, filters, sorting, and pagination.
    Only returns traces from projects in the user's organization.

    Supports parent-child trace relationships:
    - Parent traces are shown with aggregated data from children
    - Child traces are nested under parents
    - Source filtering (Call Insights, Playground, Other)
    """
    # Base query with joins to get related data - ONLY parent traces (no parent_trace_id in metadata)
    # Using PostgreSQL JSONB operator: ? checks for key existence
    query = (
        select(
            Trace.id,
            Trace.trace_id,
            Trace.name,
            Trace.status,
            Trace.model_name,
            Trace.provider,
            Trace.input_tokens,
            Trace.output_tokens,
            Trace.total_tokens,
            Trace.total_duration_ms,
            Trace.total_cost,
            Trace.environment,
            Trace.retry_count,
            Trace.trace_metadata,
            Trace.created_at,
            Project.name.label("project_name"),
            AIModel.name.label("ai_model_name"),
            User.email.label("user_email"),
        )
        .join(Project, Trace.project_id == Project.id)
        .outerjoin(AIModel, Trace.model_id == AIModel.id)
        .outerjoin(User, Project.created_by == User.id)
        .where(Project.organization_id == current_user.organization_id)
        # Filter out child traces - only show parent traces or standalone traces
        .where(
            or_(
                Trace.trace_metadata.is_(None),
                Trace.trace_metadata.op('->>')('parent_trace_id').is_(None),
            )
        )
    )

    # Apply search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Trace.trace_id).like(search_term),
                func.lower(Project.name).like(search_term),
                func.lower(User.email).like(search_term),
            )
        )

    # Apply model filter
    if model:
        query = query.where(
            or_(
                func.lower(AIModel.name).like(f"%{model.lower()}%"),
                func.lower(Trace.model_name).like(f"%{model.lower()}%"),
            )
        )

    # Apply status filter
    if status_filter:
        query = query.where(Trace.status == status_filter)

    # Apply source filter
    if source_filter:
        if source_filter == "Other":
            # Other = no metadata or no source field
            query = query.where(
                or_(
                    Trace.trace_metadata.is_(None),
                    Trace.trace_metadata.op('->>')('source').is_(None),
                )
            )
        else:
            # Specific source (Call Insights, Playground)
            query = query.where(
                Trace.trace_metadata.op('->>')('source') == source_filter
            )

    # Count total results before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    sort_column_map = {
        "requestId": Trace.trace_id,
        "status": Trace.status,
        "duration": Trace.total_duration_ms,
        "timestamp": Trace.created_at,
    }
    sort_column = sort_column_map.get(sort_by, Trace.created_at)

    if sort_direction.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # If no parent traces, return empty
    if not rows:
        return TraceListResponse(
            traces=[],
            total=total,
            page=page,
            page_size=page_size,
        )

    # Collect all parent trace_ids for efficient child query
    parent_trace_ids = [row.trace_id for row in rows]

    # Single query to fetch ALL children for all parent traces on this page
    # This eliminates the N+1 query pattern
    children_query = (
        select(
            Trace.id,
            Trace.trace_id,
            Trace.name,
            Trace.status,
            Trace.model_name,
            Trace.provider,
            Trace.input_tokens,
            Trace.output_tokens,
            Trace.total_tokens,
            Trace.total_duration_ms,
            Trace.total_cost,
            Trace.environment,
            Trace.retry_count,
            Trace.trace_metadata,
            Trace.created_at,
        )
        .where(Trace.trace_metadata.op('->>')('parent_trace_id').in_(parent_trace_ids))
        .order_by(Trace.trace_metadata.op('->>')('parent_trace_id'), Trace.created_at)
    )
    children_result = await db.execute(children_query)
    all_child_rows = children_result.all()

    # Group children by parent_trace_id for O(1) lookup
    children_by_parent = {}
    for child_row in all_child_rows:
        child_metadata = child_row.trace_metadata or {}
        parent_id = child_metadata.get("parent_trace_id")
        if parent_id:
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(child_row)

    # Build TraceListItem objects with parent-child relationships
    traces = []
    for row in rows:
        # Extract source from metadata
        metadata = row.trace_metadata or {}
        source = metadata.get("source", "Other")

        # Get children for this parent from pre-fetched data
        child_rows = children_by_parent.get(row.trace_id, [])

        # Build child trace items
        children = []
        for child_row in child_rows:
            child_metadata = child_row.trace_metadata or {}
            child_item = TraceListItem(
                id=child_row.id,
                trace_id=child_row.trace_id,
                project_name=row.project_name,  # Inherit from parent
                status=child_row.status,
                model_name=child_row.model_name or row.ai_model_name,
                provider=child_row.provider,
                input_tokens=child_row.input_tokens or 0,
                output_tokens=child_row.output_tokens or 0,
                total_tokens=child_row.total_tokens or 0,
                total_duration_ms=child_row.total_duration_ms,
                total_cost=child_row.total_cost or 0.0,
                environment=child_row.environment,
                retry_count=child_row.retry_count,
                created_at=child_row.created_at,
                user_email=row.user_email,
                source=child_metadata.get("source", "Other"),
                has_children=False,
                child_count=0,
                children=[],
                parent_trace_id=row.trace_id,
                stage=child_metadata.get("stage"),
                aggregated_data=None,
            )
            children.append(child_item)

        # Calculate aggregated data if there are children
        aggregated_data = None
        if children:
            total_tokens_sum = sum(c.total_tokens or 0 for c in children)
            total_cost_sum = sum(c.total_cost or 0.0 for c in children)
            model_names = list(set(c.model_name for c in children if c.model_name))
            durations = [c.total_duration_ms for c in children if c.total_duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else None

            aggregated_data = {
                "total_tokens": total_tokens_sum,
                "total_cost": total_cost_sum,
                "model_names": model_names,
                "avg_duration_ms": avg_duration,
            }

        # Create parent trace item
        trace_item = TraceListItem(
            id=row.id,
            trace_id=row.trace_id,
            project_name=row.project_name,
            status=row.status,
            model_name=row.model_name or row.ai_model_name,
            provider=row.provider,
            input_tokens=row.input_tokens or 0,
            output_tokens=row.output_tokens or 0,
            total_tokens=row.total_tokens or 0,
            total_duration_ms=row.total_duration_ms,
            total_cost=row.total_cost or 0.0,
            environment=row.environment,
            retry_count=row.retry_count,
            created_at=row.created_at,
            user_email=row.user_email,
            source=source,
            has_children=len(children) > 0,
            child_count=len(children),
            children=children,
            parent_trace_id=None,
            stage=None,
            aggregated_data=aggregated_data,
        )
        traces.append(trace_item)

    return TraceListResponse(
        traces=traces,
        total=total,
        page=page,
        page_size=page_size,
    )
