"""
Evaluation endpoints - queries trace_evaluations table for evaluation results
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.evaluation_catalog import TraceEvaluation, EvaluationCatalog
from app.models.user import User
from app.models.trace import Trace
from app.models.project import Project
from app.schemas.evaluation import (
    EvaluationListResponse,
    EvaluationListItem,
    EvaluationDetailResponse,
    TraceMinimal,
)
from app.schemas.evaluation_execution import (
    EvaluationRunRequest,
    EvaluationRunResult,
)
from app.api.dependencies import get_current_active_user
from app.services.evaluation_execution_service import EvaluationExecutionService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list", response_model=EvaluationListResponse)
async def list_evaluation_results(
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    trace_id: Optional[UUID] = Query(None, description="Filter by trace ID"),
    name: Optional[str] = Query(None, description="Filter by evaluation name (fuzzy search)"),
    type: Optional[str] = Query(None, description="Filter by type (vendor | promptforge | custom)"),
    model: Optional[str] = Query(None, description="Filter by model name"),

    # P0: New filters
    prompt_title: Optional[str] = Query(None, description="Filter by prompt title (fuzzy search)"),
    vendor: Optional[str] = Query(None, description="Filter by vendor name"),
    category: Optional[str] = Query(None, description="Filter by category (Helpful, Honest, Harmless)"),
    status_filter: Optional[str] = Query(None, description="Filter by status (pass, fail)"),

    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),

    # P0: Sorting
    sort_by: str = Query("timestamp", description="Sort by: timestamp, score, evaluation_name, category"),
    sort_direction: str = Query("desc", description="Sort direction: asc, desc"),

    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List evaluation results with enhanced filtering and sorting (P0/P1)

    Returns evaluations with trace context (prompt title, model, vendor, category)
    Supports filtering by prompt title, vendor, category, and status
    Default sort: Most recent evaluations first
    """
    # Build query with trace and project joins
    query = (
        select(
            TraceEvaluation.id,
            EvaluationCatalog.name,
            EvaluationCatalog.description,
            EvaluationCatalog.source.label("type"),
            TraceEvaluation.status,
            TraceEvaluation.trace_id,
            TraceEvaluation.score,
            TraceEvaluation.passed,
            TraceEvaluation.total_tokens,
            TraceEvaluation.evaluation_cost.label("total_cost"),
            TraceEvaluation.execution_time_ms.label("duration_ms"),
            TraceEvaluation.model_used.label("model"),
            TraceEvaluation.created_at,
            # P0: New fields from trace and catalog
            Trace.trace_id.label("trace_identifier"),
            Trace.name.label("prompt_title"),
            Trace.model_name,
            EvaluationCatalog.vendor_name,
            EvaluationCatalog.category,
            Project.id.label("project_id"),
        )
        .join(EvaluationCatalog, TraceEvaluation.evaluation_catalog_id == EvaluationCatalog.id)
        .join(Trace, TraceEvaluation.trace_id == Trace.id)
        .join(Project, Trace.project_id == Project.id)
    )

    # Apply filters
    filters = []

    # Multi-tenant isolation: Only show evaluations from user's organization
    filters.append(Project.organization_id == current_user.organization_id)

    # Organization-scoped evaluations: show public or org-owned evaluation definitions
    org_filter = or_(
        EvaluationCatalog.is_public == True,
        EvaluationCatalog.organization_id == current_user.organization_id
    )
    filters.append(org_filter)

    # Existing filters
    if trace_id:
        filters.append(TraceEvaluation.trace_id == trace_id)

    if name:
        filters.append(EvaluationCatalog.name.ilike(f"%{name}%"))

    if type:
        filters.append(EvaluationCatalog.source == type)

    if model:
        filters.append(TraceEvaluation.model_used == model)

    # P0: New filters
    if prompt_title:
        filters.append(Trace.name.ilike(f"%{prompt_title}%"))

    if vendor:
        filters.append(EvaluationCatalog.vendor_name == vendor)

    if category:
        filters.append(EvaluationCatalog.category == category)

    if status_filter:
        if status_filter.lower() == "pass":
            filters.append(TraceEvaluation.passed == True)
        elif status_filter.lower() == "fail":
            filters.append(TraceEvaluation.passed == False)

    # Date filters
    if created_after:
        filters.append(TraceEvaluation.created_at >= created_after)

    if created_before:
        filters.append(TraceEvaluation.created_at <= created_before)

    # Apply all filters
    if filters:
        query = query.where(and_(*filters))

    # Get total count
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # P0: Apply sorting (default: most recent first)
    from sqlalchemy import asc, desc

    sort_column_map = {
        "timestamp": TraceEvaluation.created_at,
        "score": TraceEvaluation.score,
        "evaluation_name": EvaluationCatalog.name,
        "category": EvaluationCatalog.category,
        "prompt_title": Trace.name,
        "model": Trace.model_name,
    }
    sort_column = sort_column_map.get(sort_by, TraceEvaluation.created_at)

    if sort_direction.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))  # Default: most recent first

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # Build response with enhanced fields
    evaluations = [
        EvaluationListItem(
            id=row.id,
            name=row.name,
            description=row.description,
            type=row.type,
            status=row.status,
            trace_id=row.trace_id,
            trace_identifier=row.trace_identifier,  # P0: trace.trace_id
            project_id=row.project_id,  # P0: Now available
            # P0: New fields
            prompt_title=row.prompt_title or "Untitled",
            model=row.model or row.model_name or "unknown",
            vendor_name=row.vendor_name,
            category=row.category,
            # Results
            avg_score=row.score,
            passed=row.passed,  # P0: Explicit pass/fail
            total_tests=1 if row.passed is not None else 0,
            passed_tests=1 if row.passed else 0,
            # Metrics
            total_tokens=row.total_tokens or 0,
            total_cost=float(row.total_cost or 0.0),
            duration_ms=float(row.duration_ms or 0.0),
            created_at=row.created_at,
        )
        for row in rows
    ]

    return EvaluationListResponse(
        evaluations=evaluations,
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.post("/run", response_model=List[EvaluationRunResult])
async def run_evaluations(
    request: EvaluationRunRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute evaluations on a trace

    This endpoint runs one or more evaluations on a specified trace and returns the results.
    Each evaluation execution creates a child trace and stores the result in trace_evaluations.
    """
    try:
        # Create execution service
        execution_service = EvaluationExecutionService(
            db=db,
            organization_id=current_user.organization_id
        )

        # Run evaluations
        results = await execution_service.run_evaluations(
            evaluation_ids=request.evaluation_ids,
            trace_id=request.trace_id,
            user_id=current_user.id,
            model_override=request.model_override,
        )

        # Convert to response schema
        return [
            EvaluationRunResult(
                evaluation_id=result["evaluation_id"],
                evaluation_name=result["evaluation_name"],
                trace_id=result["trace_id"],
                score=result.get("score"),
                passed=result.get("passed"),
                reason=result.get("reason"),
                metadata=result.get("metadata", {}),
                status=result.get("status", "completed"),
                error_message=result.get("error_message"),
            )
            for result in results
        ]

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error running evaluations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing evaluations: {str(e)}",
        )


@router.get("/{evaluation_id}/detail", response_model=EvaluationDetailResponse)
async def get_evaluation_detail(
    evaluation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed evaluation information with trace context (P1)

    Returns comprehensive evaluation details including:
    - Full trace context (prompt title, model, project)
    - Evaluation results (score, pass/fail, reasoning)
    - Execution metrics (tokens, cost, duration)
    - Input/output data for debugging
    - Link to associated trace for navigation
    """
    # Build query with all necessary joins
    query = (
        select(
            TraceEvaluation,
            EvaluationCatalog,
            Trace,
            Project.name.label("project_name"),
            Project.id.label("project_id"),
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
            detail="Evaluation not found or access denied"
        )

    trace_eval, eval_catalog, trace, project_name, project_id = row

    return EvaluationDetailResponse(
        id=trace_eval.id,
        trace_id=trace.id,
        trace_identifier=trace.trace_id,
        # Trace context
        prompt_title=trace.name,
        model_name=trace.model_name or "unknown",
        project_name=project_name,
        project_id=project_id,
        created_at=trace_eval.created_at,
        # Evaluation details
        evaluation_name=eval_catalog.name,
        evaluation_type=eval_catalog.evaluation_type or "unknown",
        vendor_name=eval_catalog.vendor_name,
        category=eval_catalog.category,
        source=eval_catalog.source.value if eval_catalog.source else "UNKNOWN",
        description=eval_catalog.description,
        # Results
        score=trace_eval.score,
        threshold=None,  # Threshold is stored in default_config JSON if applicable
        passed=trace_eval.passed,
        reason=trace_eval.reason,
        explanation=None,  # Additional explanation can be in details JSON if needed
        # Execution metrics
        execution_time_ms=trace_eval.execution_time_ms,
        input_tokens=trace_eval.input_tokens,
        output_tokens=trace_eval.output_tokens,
        total_tokens=trace_eval.total_tokens,
        evaluation_cost=trace_eval.evaluation_cost,
        # Full data for debugging (input/output stored in trace, not trace_evaluation)
        input_data=trace.input_data if trace else None,
        output_data=trace.output_data if trace else None,
        llm_metadata=trace_eval.llm_metadata,
        # Trace link
        trace=TraceMinimal(
            id=trace.id,
            trace_id=trace.trace_id,
            name=trace.name,
            status=trace.status,
        ),
    )
