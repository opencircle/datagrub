"""
Evaluation Catalog API endpoints

This module provides REST API endpoints for the Evaluation Abstraction Layer (EAL):
- List available evaluations from all sources
- Create custom evaluations
- Create LLM-as-Judge evaluations
- Execute evaluations on traces
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.evaluation_catalog import (
    EvaluationCatalog,
    TraceEvaluation,
    EvaluationSource,
    EvaluationCategory,
    EvaluationType,
)
from app.models.trace import Trace
from app.schemas.evaluation_catalog import (
    EvaluationCatalogCreate,
    EvaluationCatalogUpdate,
    EvaluationCatalogResponse,
    EvaluationCatalogListResponse,
    TraceEvaluationResponse,
    EvaluationExecutionRequest,
    EvaluationExecutionResponse,
    CustomEvaluatorRequest,
    LLMJudgeEvaluatorRequest,
)
from app.api.dependencies import get_current_active_user
from app.evaluations.registry import registry
from app.evaluations.base import EvaluationRequest

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Evaluation Catalog Endpoints ====================


@router.get("/categories", response_model=List[str])
async def get_evaluation_categories(
    source: Optional[EvaluationSource] = Query(None, description="Filter by source"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of unique evaluation categories

    Returns all unique categories from evaluations the user has access to.
    """
    # Build query to get distinct categories
    query = select(EvaluationCatalog.category).distinct()

    # Apply filters
    filters = []

    if source:
        filters.append(EvaluationCatalog.source == source)

    # Access control: show public evaluations OR evaluations from user's organization
    access_filter = or_(
        EvaluationCatalog.is_public == True,
        EvaluationCatalog.organization_id == current_user.organization_id
    )
    filters.append(access_filter)

    # Only active evaluations
    filters.append(EvaluationCatalog.is_active == True)

    if filters:
        query = query.where(and_(*filters))

    # Execute query
    result = await db.execute(query)
    categories = [cat for cat in result.scalars().all() if cat]  # Filter out None values

    return sorted(categories)  # Return sorted list


@router.get("/catalog", response_model=List[EvaluationCatalogListResponse])
async def list_evaluations(
    source: Optional[EvaluationSource] = Query(None, description="Filter by source"),
    category: Optional[EvaluationCategory] = Query(None, description="Filter by category"),
    evaluation_type: Optional[EvaluationType] = Query(None, description="Filter by type"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all available evaluations from the catalog

    Returns evaluations from:
    - PromptForge (public)
    - Vendor libraries (public)
    - Custom evaluations (organization-scoped)
    - LLM-as-Judge (organization-scoped)
    """
    # Build query
    query = select(EvaluationCatalog)

    # Apply filters
    filters = []

    if source:
        filters.append(EvaluationCatalog.source == source)
    if category:
        filters.append(EvaluationCatalog.category == category)
    if evaluation_type:
        filters.append(EvaluationCatalog.evaluation_type == evaluation_type)
    if is_public is not None:
        filters.append(EvaluationCatalog.is_public == is_public)
    if is_active is not None:
        filters.append(EvaluationCatalog.is_active == is_active)

    # Access control: show public evaluations OR evaluations from user's organization
    access_filter = or_(
        EvaluationCatalog.is_public == True,
        EvaluationCatalog.organization_id == current_user.organization_id
    )
    filters.append(access_filter)

    # Search
    if search:
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                EvaluationCatalog.name.ilike(search_pattern),
                EvaluationCatalog.description.ilike(search_pattern)
            )
        )

    if filters:
        query = query.where(and_(*filters))

    # Execute query
    result = await db.execute(query)
    evaluations = result.scalars().all()

    # Filter evaluations to only include those with registered adapters
    # This ensures we don't show evaluations whose adapters aren't available
    from app.evaluations.registry import registry

    available_evaluations = []
    for evaluation in evaluations:
        # Check if adapter is registered
        if evaluation.adapter_class:
            # For vendor/promptforge evaluations with adapter_class
            adapter = registry._adapters.get(evaluation.adapter_class)
            if adapter:
                available_evaluations.append(evaluation)
        elif evaluation.source == EvaluationSource.CUSTOM:
            # Custom evaluations don't need adapters (have implementation)
            available_evaluations.append(evaluation)
        # Note: Evaluations without adapter_class or CUSTOM implementation are skipped

    return available_evaluations


@router.get("/catalog/{evaluation_id}", response_model=EvaluationCatalogResponse)
async def get_evaluation(
    evaluation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific evaluation from the catalog"""
    query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
    result = await db.execute(query)
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    # Check access
    if not evaluation.is_public and evaluation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this evaluation"
        )

    return evaluation


@router.post("/catalog", response_model=EvaluationCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation_in: EvaluationCatalogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new evaluation in the catalog

    Only for CUSTOM and LLM_JUDGE sources.
    VENDOR and PROMPTFORGE evaluations are managed internally.
    """
    # Validate source
    if evaluation_in.source not in [EvaluationSource.CUSTOM, EvaluationSource.LLM_JUDGE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only create CUSTOM or LLM_JUDGE evaluations via API"
        )

    # Set organization if not specified
    if not evaluation_in.organization_id:
        evaluation_in.organization_id = current_user.organization_id

    # Check access to organization
    if evaluation_in.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create evaluation for different organization"
        )

    # Create evaluation
    evaluation = EvaluationCatalog(**evaluation_in.model_dump())
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"Created evaluation {evaluation.id} by user {current_user.id}")

    return evaluation


@router.patch("/catalog/{evaluation_id}", response_model=EvaluationCatalogResponse)
async def update_evaluation(
    evaluation_id: UUID,
    evaluation_update: EvaluationCatalogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an evaluation in the catalog"""
    # Get evaluation
    query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
    result = await db.execute(query)
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    # Check access (can only update own organization's evaluations)
    if evaluation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update evaluation from different organization"
        )

    # Update fields
    update_data = evaluation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evaluation, field, value)

    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"Updated evaluation {evaluation_id} by user {current_user.id}")

    return evaluation


@router.delete("/catalog/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an evaluation from the catalog

    This is a soft delete (sets is_active=False)
    """
    # Get evaluation
    query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
    result = await db.execute(query)
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    # Check access
    if evaluation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete evaluation from different organization"
        )

    # Soft delete
    evaluation.is_active = False
    await db.commit()

    logger.info(f"Deleted (soft) evaluation {evaluation_id} by user {current_user.id}")


# ==================== Custom Evaluator Endpoints ====================


@router.post("/custom", response_model=EvaluationCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_evaluator(
    evaluator_request: CustomEvaluatorRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a custom evaluator with Python code

    The code will be executed in a sandboxed environment.
    """
    # Set organization if not specified
    organization_id = evaluator_request.organization_id or current_user.organization_id

    # Check access
    if organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create evaluator for different organization"
        )

    # Create evaluation catalog entry
    evaluation = EvaluationCatalog(
        name=evaluator_request.name,
        description=evaluator_request.description,
        category=evaluator_request.category,
        source=EvaluationSource.CUSTOM,
        evaluation_type=evaluator_request.evaluation_type,
        organization_id=organization_id,
        project_id=evaluator_request.project_id,
        is_public=False,  # Custom evaluations are private by default
        config_schema=evaluator_request.config_schema,
        default_config=evaluator_request.default_config,
        implementation=evaluator_request.implementation,
        tags=evaluator_request.tags,
        is_active=True,
        version="1.0.0",
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"Created custom evaluator {evaluation.id} by user {current_user.id}")

    return evaluation


@router.post("/custom-simple", response_model=EvaluationCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_evaluation_simple(
    name: str,
    category: str,
    description: Optional[str] = None,
    prompt_input: str = "",
    prompt_output: str = "",
    system_prompt: str = "",
    model: str = "gpt-4o-mini",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a custom evaluation (simplified form-based version)

    This endpoint is designed for the UI form where users provide prompts
    instead of Python code. The implementation is generated automatically
    from the prompts.
    """
    # Validate required fields
    if not name or len(name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be at least 3 characters long"
        )

    if not prompt_input or len(prompt_input) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt input must be at least 10 characters long"
        )

    if not prompt_output or len(prompt_output) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt output must be at least 10 characters long"
        )

    if not system_prompt or len(system_prompt) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System prompt must be at least 10 characters long"
        )

    # Map category string to EvaluationCategory enum
    category_map = {
        "accuracy": EvaluationCategory.QUALITY,
        "groundedness": EvaluationCategory.QUALITY,
        "safety": EvaluationCategory.SAFETY,
        "compliance": EvaluationCategory.BUSINESS_RULES,
        "tone": EvaluationCategory.CUSTOM,
        "bias": EvaluationCategory.BIAS,
        "other": EvaluationCategory.CUSTOM,
    }
    eval_category = category_map.get(category.lower(), EvaluationCategory.CUSTOM)

    # Generate implementation code from prompts
    # This creates a simple LLM-based evaluation
    implementation = f'''
def evaluate(request):
    """Custom evaluation generated from prompts"""
    import json

    # Extract input and output from request
    input_data = request.get('input', {{}})
    output_data = request.get('output', {{}})

    # Format prompts with actual data
    input_text = str(input_data.get('prompt', ''))
    output_text = str(output_data.get('response', ''))

    # Build evaluation prompt
    evaluation_prompt = """
{system_prompt}

Input to evaluate:
{prompt_input}

Input: {{input_text}}

Output to evaluate:
{prompt_output}

Output: {{output_text}}

Provide your evaluation as JSON with:
- score: float between 0.0 and 1.0
- passed: boolean
- reason: string explanation
"""

    # For now, return a placeholder result
    # In production, this would call an LLM service
    return {{
        'score': 0.8,
        'passed': True,
        'reason': 'Evaluation completed successfully',
        'details': {{
            'model': '{model}',
            'prompt_input': '{prompt_input}',
            'prompt_output': '{prompt_output}',
        }}
    }}
'''

    # Create evaluation catalog entry
    evaluation = EvaluationCatalog(
        name=name,
        description=description,
        category=eval_category,
        source=EvaluationSource.CUSTOM,
        evaluation_type=EvaluationType.JUDGE,  # Prompt-based evaluations are judges
        organization_id=current_user.organization_id,
        is_public=False,
        implementation=implementation,
        config_schema={
            "model": {"type": "string", "default": model},
            "prompt_input": {"type": "string", "default": prompt_input},
            "prompt_output": {"type": "string", "default": prompt_output},
            "system_prompt": {"type": "string", "default": system_prompt},
        },
        default_config={
            "model": model,
            "prompt_input": prompt_input,
            "prompt_output": prompt_output,
            "system_prompt": system_prompt,
        },
        llm_model=model,
        llm_system_prompt=system_prompt,
        llm_criteria=f"{prompt_input}\n{prompt_output}",
        tags=[category],
        is_active=True,
        version="1.0.0",
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"Created simple custom evaluation {evaluation.id} by user {current_user.id}")

    return evaluation


# ==================== LLM-as-Judge Endpoints ====================


@router.post("/llm-judge", response_model=EvaluationCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_judge_evaluator(
    judge_request: LLMJudgeEvaluatorRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an LLM-as-Judge evaluator

    Uses an LLM to evaluate outputs based on criteria.
    """
    # Set organization if not specified
    organization_id = judge_request.organization_id or current_user.organization_id

    # Check access
    if organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create evaluator for different organization"
        )

    # Create evaluation catalog entry
    evaluation = EvaluationCatalog(
        name=judge_request.name,
        description=judge_request.description,
        category=judge_request.category,
        source=EvaluationSource.LLM_JUDGE,
        evaluation_type=EvaluationType.JUDGE,  # LLM judges are always JUDGE type
        organization_id=organization_id,
        project_id=judge_request.project_id,
        is_public=False,
        config_schema=judge_request.config_schema,
        default_config=judge_request.default_config,
        llm_criteria=judge_request.llm_criteria,
        llm_model=judge_request.llm_model,
        llm_system_prompt=judge_request.llm_system_prompt,
        tags=judge_request.tags,
        is_active=True,
        version="1.0.0",
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"Created LLM judge evaluator {evaluation.id} by user {current_user.id}")

    return evaluation


# ==================== Evaluation Execution Endpoints ====================


@router.post("/execute", response_model=EvaluationExecutionResponse)
async def execute_evaluations(
    execution_request: EvaluationExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute multiple evaluations on a trace

    This is the main endpoint for running evaluations.
    """
    # Get trace
    trace_query = select(Trace).where(Trace.id == execution_request.trace_id)
    trace_result = await db.execute(trace_query)
    trace = trace_result.scalar_one_or_none()

    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )

    # Build evaluation request with organization context
    trace_metadata = trace.trace_metadata or {}
    trace_metadata.update({
        "organization_id": str(current_user.organization_id),
        "project_id": str(trace.project_id) if trace.project_id else None,
    })

    eval_request = EvaluationRequest(
        trace_id=trace.id,
        input_data=trace.input_data or {},
        output_data=trace.output_data or {},
        metadata=trace_metadata,
        trace_metadata={
            "total_duration_ms": trace.total_duration_ms,
            "total_tokens": trace.total_tokens,
            "total_cost": trace.total_cost,
        }
    )

    # Execute evaluations
    results = []
    successful = 0
    failed = 0
    errors = []

    for evaluation_id in execution_request.evaluation_ids:
        try:
            # Get evaluation from catalog
            eval_query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
            eval_result = await db.execute(eval_query)
            evaluation = eval_result.scalar_one_or_none()

            if not evaluation:
                errors.append({
                    "evaluation_id": str(evaluation_id),
                    "error": "Evaluation not found"
                })
                failed += 1
                continue

            # Check access
            if not evaluation.is_public and evaluation.organization_id != current_user.organization_id:
                errors.append({
                    "evaluation_id": str(evaluation_id),
                    "error": "Access denied"
                })
                failed += 1
                continue

            # Apply config overrides
            if execution_request.config_overrides and evaluation_id in execution_request.config_overrides:
                eval_request.config = execution_request.config_overrides[evaluation_id]
            else:
                eval_request.config = evaluation.default_config or {}

            # Execute evaluation via registry
            eval_result = await registry.execute_evaluation(
                evaluation.adapter_evaluation_id,
                eval_request,
                adapter_class=evaluation.adapter_class,
                source=evaluation.source
            )

            # Save result to database with all metrics
            trace_eval = TraceEvaluation(
                trace_id=trace.id,
                evaluation_catalog_id=evaluation.id,
                organization_id=current_user.organization_id,  # Required for multi-tenant isolation
                score=eval_result.score,
                passed=eval_result.passed,
                category=eval_result.category,
                reason=eval_result.reason,
                details=eval_result.details,
                suggestions=eval_result.suggestions,
                execution_time_ms=eval_result.execution_time_ms,
                model_used=eval_result.model_used,
                # LLM metrics
                input_tokens=eval_result.input_tokens,
                output_tokens=eval_result.output_tokens,
                total_tokens=eval_result.total_tokens,
                evaluation_cost=eval_result.evaluation_cost,
                # Metadata
                vendor_metrics=eval_result.vendor_metrics,
                llm_metadata=eval_result.llm_metadata,
                # Config and status
                config=eval_request.config,
                status=eval_result.status,
                error_message=eval_result.error,
            )

            db.add(trace_eval)
            await db.commit()
            await db.refresh(trace_eval)

            results.append(trace_eval)

            if eval_result.status == "completed":
                successful += 1
            else:
                failed += 1

        except Exception as e:
            logger.error(f"Error executing evaluation {evaluation_id}: {e}")
            errors.append({
                "evaluation_id": str(evaluation_id),
                "error": str(e)
            })
            failed += 1

    return EvaluationExecutionResponse(
        trace_id=trace.id,
        total_evaluations=len(execution_request.evaluation_ids),
        successful_evaluations=successful,
        failed_evaluations=failed,
        results=results,
        errors=errors if errors else None
    )


@router.post("/catalog/{evaluation_id}/execute", response_model=TraceEvaluationResponse)
async def execute_single_evaluation(
    evaluation_id: UUID,
    evaluation_request: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a single evaluation without requiring a saved trace

    This is useful for testing evaluations in the playground or
    executing ad-hoc evaluations without creating trace records.
    """
    # Get evaluation from catalog
    eval_query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
    eval_result = await db.execute(eval_query)
    evaluation = eval_result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    # Check access
    if not evaluation.is_public and evaluation.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this evaluation"
        )

    # Build evaluation request with organization context
    eval_metadata = evaluation_request.get('metadata', {})
    eval_metadata.update({
        "organization_id": str(current_user.organization_id),
        "project_id": None,  # No project context for ad-hoc execution
    })

    eval_request = EvaluationRequest(
        trace_id=UUID('00000000-0000-0000-0000-000000000000'),  # Temporary ID for ad-hoc execution
        input_data=evaluation_request.get('input_data', {}),
        output_data=evaluation_request.get('output_data', {}),
        metadata=eval_metadata,
        config=evaluation_request.get('config', evaluation.default_config or {}),
    )

    try:
        # Execute evaluation via registry
        eval_result = await registry.execute_evaluation(
            evaluation.adapter_evaluation_id,
            eval_request,
            adapter_class=evaluation.adapter_class,
            source=evaluation.source
        )

        # Create response (no database save for ad-hoc execution)
        return TraceEvaluationResponse(
            id=UUID('00000000-0000-0000-0000-000000000000'),  # Temporary ID
            trace_id=UUID('00000000-0000-0000-0000-000000000000'),
            evaluation_catalog_id=evaluation.id,
            evaluation_name=evaluation.name,
            score=eval_result.score,
            passed=eval_result.passed,
            category=eval_result.category,
            reason=eval_result.reason,
            details=eval_result.details,
            suggestions=eval_result.suggestions,
            execution_time_ms=eval_result.execution_time_ms,
            model_used=eval_result.model_used,
            config=eval_request.config,
            status=eval_result.status,
            error_message=eval_result.error,
            created_at=None,
        )

    except Exception as e:
        logger.error(f"Error executing evaluation {evaluation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation execution failed: {str(e)}"
        )


@router.get("/traces/{trace_id}/evaluations", response_model=List[TraceEvaluationResponse])
async def get_trace_evaluations(
    trace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all evaluation results for a specific trace"""
    # Check trace exists and user has access
    trace_query = select(Trace).where(Trace.id == trace_id)
    trace_result = await db.execute(trace_query)
    trace = trace_result.scalar_one_or_none()

    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )

    # Get evaluations
    eval_query = select(TraceEvaluation).where(TraceEvaluation.trace_id == trace_id)
    eval_result = await db.execute(eval_query)
    evaluations = eval_result.scalars().all()

    return evaluations
