"""
Playground API endpoints - Live prompt execution with model integration
"""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.model_provider import ModelProviderService, ModelExecutionRequest
from app.services.trace_service import TraceService

router = APIRouter()


class PlaygroundParameters(BaseModel):
    """Playground execution parameters"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=4000)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=40, ge=1, le=100)


class PlaygroundMetadata(BaseModel):
    """Optional metadata for tracing"""
    intent: Optional[str] = None
    tone: Optional[str] = None
    prompt_id: Optional[str] = None


class PlaygroundExecutionRequest(BaseModel):
    """Request to execute a prompt"""
    title: Optional[str] = Field(None, description="Title for this execution (defaults to project name)")
    prompt: str = Field(..., min_length=1, description="User prompt to execute")
    system_prompt: Optional[str] = Field(None, description="System prompt (optional)")
    model: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-opus')")
    parameters: PlaygroundParameters
    metadata: Optional[PlaygroundMetadata] = None
    evaluation_ids: Optional[list[str]] = Field(None, description="List of evaluation IDs to run after execution")


class PlaygroundMetrics(BaseModel):
    """Execution metrics"""
    latency_ms: float
    tokens_used: int
    cost: float


class PlaygroundExecutionResponse(BaseModel):
    """Response from prompt execution"""
    response: str
    metrics: PlaygroundMetrics
    trace_id: str
    model: str
    timestamp: str


@router.post("/execute", response_model=PlaygroundExecutionResponse)
async def execute_prompt(
    request: PlaygroundExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a prompt using live model API

    This endpoint:
    1. Looks up the organization's model API key
    2. Executes the prompt against the actual model provider
    3. Traces the execution for observability
    4. Returns the response with metrics
    """
    start_time = time.time()
    trace_id = str(uuid.uuid4())

    try:
        # Initialize services
        model_service = ModelProviderService(db, current_user.organization_id)
        trace_service = TraceService(db)

        # Prepare execution request
        execution_request = ModelExecutionRequest(
            model=request.model,
            messages=[
                {"role": "system", "content": request.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": request.prompt},
            ],
            temperature=request.parameters.temperature,
            max_tokens=request.parameters.max_tokens,
            top_p=request.parameters.top_p,
            top_k=request.parameters.top_k,
        )

        # Execute prompt with model provider
        # This will automatically look up the API key from organization context
        execution_result = await model_service.execute(execution_request)

        # Use provider duration if available, otherwise use total duration from model service
        # Provider duration is more accurate (e.g., openai-processing-ms header)
        latency_ms = execution_result.provider_duration_ms or execution_result.total_duration_ms or (time.time() - start_time) * 1000

        # Create trace record for observability
        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(current_user.id),
            organization_id=current_user.organization_id,
            prompt_id=request.metadata.prompt_id if request.metadata else None,
            model=request.model,
            input_prompt=request.prompt,
            system_prompt=request.system_prompt,
            output_response=execution_result.response,
            latency_ms=latency_ms,
            tokens_used=execution_result.tokens_used,
            cost=execution_result.cost,
            input_tokens=execution_result.input_tokens,
            output_tokens=execution_result.output_tokens,
            title=request.title,  # Pass title for trace name
            parameters={
                "temperature": request.parameters.temperature,
                "max_tokens": request.parameters.max_tokens,
                "top_p": request.parameters.top_p,
                "top_k": request.parameters.top_k,
            },
            metadata={
                "intent": request.metadata.intent if request.metadata else None,
                "tone": request.metadata.tone if request.metadata else None,
                "source": "playground",
            },
        )

        # Execute evaluations if specified
        if request.evaluation_ids:
            from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation
            from app.evaluations.registry import registry
            from app.evaluations.base import EvaluationRequest
            from sqlalchemy import select

            for evaluation_id in request.evaluation_ids:
                try:
                    # Get evaluation from catalog
                    eval_query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
                    eval_result = await db.execute(eval_query)
                    evaluation = eval_result.scalar_one_or_none()

                    if not evaluation:
                        continue

                    # Check access
                    if not evaluation.is_public and evaluation.organization_id != current_user.organization_id:
                        continue

                    # Build evaluation request with organization context
                    eval_request = EvaluationRequest(
                        trace_id=trace.id,
                        input_data={"prompt": request.prompt, "system_prompt": request.system_prompt},
                        output_data={"response": execution_result.response},
                        metadata={
                            "model": "gpt-4o-mini",  # Always use cost-effective model for evaluations
                            "organization_id": str(current_user.organization_id),
                            "project_id": str(trace.project_id) if trace.project_id else None,
                        },
                        config=evaluation.default_config or {},
                        db_session=db,  # Pass db session for API key retrieval
                    )

                    # Execute evaluation via registry
                    eval_result_data = await registry.execute_evaluation(
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
                        score=eval_result_data.score,
                        passed=eval_result_data.passed,
                        category=eval_result_data.category,
                        reason=eval_result_data.reason,
                        details=eval_result_data.details,
                        suggestions=eval_result_data.suggestions,
                        execution_time_ms=eval_result_data.execution_time_ms,
                        model_used=eval_result_data.model_used,
                        # LLM metrics
                        input_tokens=eval_result_data.input_tokens,
                        output_tokens=eval_result_data.output_tokens,
                        total_tokens=eval_result_data.total_tokens,
                        evaluation_cost=eval_result_data.evaluation_cost,
                        # Metadata
                        vendor_metrics=eval_result_data.vendor_metrics,
                        llm_metadata=eval_result_data.llm_metadata,
                        # Config and status
                        config=eval_request.config,
                        status=eval_result_data.status,
                        error_message=eval_result_data.error,
                    )

                    db.add(trace_eval)
                    await db.commit()

                except Exception as e:
                    # Log error but don't fail the entire request
                    print(f"[WARN] Failed to execute evaluation {evaluation_id}: {e}")

        return PlaygroundExecutionResponse(
            response=execution_result.response,
            metrics=PlaygroundMetrics(
                latency_ms=latency_ms,
                tokens_used=execution_result.tokens_used,
                cost=execution_result.cost,
            ),
            trace_id=trace_id,
            model=request.model,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    except Exception as e:
        # Calculate duration even on failure (critical for accounting)
        error_duration_ms = (time.time() - start_time) * 1000

        # Create error trace record (REQUIRED for billing/accounting)
        try:
            trace_service = TraceService(db)
            await trace_service.create_trace(
                trace_id=trace_id,
                user_id=str(current_user.id),
                organization_id=current_user.organization_id,
                prompt_id=request.metadata.prompt_id if request.metadata else None,
                model=request.model,
                input_prompt=request.prompt,
                system_prompt=request.system_prompt,
                output_response="",  # No response on error
                latency_ms=error_duration_ms,
                tokens_used=0,  # No tokens consumed on error
                cost=0.0,  # No cost on error
                input_tokens=None,
                output_tokens=None,
                status="error",
                error_message=str(e),
                error_type=type(e).__name__,
                title=request.title,  # Pass title for error traces too
                parameters={
                    "temperature": request.parameters.temperature,
                    "max_tokens": request.parameters.max_tokens,
                    "top_p": request.parameters.top_p,
                    "top_k": request.parameters.top_k,
                },
                metadata={
                    "intent": request.metadata.intent if request.metadata else None,
                    "tone": request.metadata.tone if request.metadata else None,
                    "source": "playground",
                },
            )
        except Exception as trace_error:
            # Log but don't fail the request if trace creation fails
            print(f"[ERROR] Failed to create error trace: {trace_error}")

        # Return user-friendly error message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute prompt: {str(e)}",
        )
