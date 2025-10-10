"""
Call Insights API endpoints - 3-stage Dynamic Temperature Adjustment pipeline
"""

import time
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.call_insights import CallInsightsAnalysis
from app.models.model_provider import ModelProviderMetadata, ModelProviderConfig
from app.services.call_insights_service import CallInsightsService

router = APIRouter()


class StageParameters(BaseModel):
    """Parameters for a single DTA stage"""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)


class CallInsightsStageParams(BaseModel):
    """3-stage DTA parameters"""
    fact_extraction: Optional[StageParameters] = None
    reasoning: Optional[StageParameters] = None
    summary: Optional[StageParameters] = None


class CallInsightsSystemPrompts(BaseModel):
    """Custom system prompts for each DTA stage"""
    stage1_fact_extraction: Optional[str] = Field(None, description="System prompt for fact extraction stage")
    stage2_reasoning: Optional[str] = Field(None, description="System prompt for reasoning stage")
    stage3_summary: Optional[str] = Field(None, description="System prompt for summary stage")


class CallInsightsModels(BaseModel):
    """Model selection for each DTA stage"""
    stage1_model: Optional[str] = Field(None, description="Model for fact extraction (default: gpt-4o-mini)")
    stage2_model: Optional[str] = Field(None, description="Model for reasoning (default: gpt-4o-mini)")
    stage3_model: Optional[str] = Field(None, description="Model for summary (default: gpt-4o-mini)")


class CallInsightsAnalyzeRequest(BaseModel):
    """Request to analyze call transcript"""
    transcript: str = Field(..., min_length=100, max_length=100000, description="Call transcript text")
    transcript_title: Optional[str] = Field(None, max_length=500, description="Optional title for searchability")
    project_id: Optional[str] = Field(None, description="Project UUID to associate analysis with")
    stage_params: Optional[CallInsightsStageParams] = Field(None, description="Custom stage parameters")
    system_prompts: Optional[CallInsightsSystemPrompts] = Field(None, description="Custom system prompts for each stage")
    models: Optional[CallInsightsModels] = Field(None, description="Model selection for each stage")
    enable_pii_redaction: bool = Field(default=False, description="Enable PII redaction before LLM processing")
    evaluations: Optional[list[str]] = Field(None, description="Evaluation IDs to run on outputs")


class TraceMetadata(BaseModel):
    """Execution trace for a single stage"""
    trace_id: str
    stage: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_ms: float
    cost: float
    system_prompt: Optional[str] = None


class EvaluationMetric(BaseModel):
    """Evaluation result"""
    evaluation_name: str
    evaluation_uuid: str
    score: float
    passed: bool
    reason: str
    threshold: Optional[float] = None
    category: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    evaluation_cost: Optional[float] = None


class CallInsightsAnalyzeResponse(BaseModel):
    """Response from call insights analysis"""
    analysis_id: str
    project_id: Optional[str] = None
    summary: str
    insights: str
    facts: str
    pii_redacted: bool
    traces: list[TraceMetadata]
    evaluations: list[EvaluationMetric]
    total_tokens: int
    total_cost: float
    created_at: str


class CallInsightsHistoryItem(BaseModel):
    """Single history item in list view"""
    id: str
    transcript_title: Optional[str] = None
    transcript_preview: str  # First 200 chars of transcript
    project_id: Optional[str] = None
    total_tokens: int
    total_cost: float
    pii_redacted: bool
    created_at: str

    class Config:
        from_attributes = True


class CallInsightsHistoryResponse(BaseModel):
    """Full analysis from history"""
    id: str
    transcript_title: Optional[str] = None
    transcript_input: str
    summary_output: str
    insights_output: str
    facts_output: str
    pii_redacted: bool
    total_tokens: int
    total_cost: float
    project_id: Optional[str] = None
    # System prompts used
    system_prompt_stage1: Optional[str] = None
    system_prompt_stage2: Optional[str] = None
    system_prompt_stage3: Optional[str] = None
    # Models used for each stage
    model_stage1: Optional[str] = None
    model_stage2: Optional[str] = None
    model_stage3: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CallInsightsAnalyzeResponse)
async def analyze_call_transcript(
    request: CallInsightsAnalyzeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze call transcript with 3-stage Dynamic Temperature Adjustment pipeline

    This endpoint:
    1. Optionally redacts PII using Presidio (if enabled)
    2. Executes Stage 1: Fact Extraction (temperature 0.25, top_p 0.95)
    3. Executes Stage 2: Reasoning & Insights (temperature 0.65, top_p 0.95)
    4. Executes Stage 3: Summary Synthesis (temperature 0.45, top_p 0.95)
    5. Creates parent trace + 3 child traces
    6. Runs configured evaluations on outputs
    7. Returns summary, insights, facts with full trace and evaluation data
    """
    start_time = time.time()

    try:
        # Initialize service
        insights_service = CallInsightsService(db, current_user.organization_id)

        # Execute 3-stage analysis
        result = await insights_service.analyze_transcript(
            transcript=request.transcript,
            transcript_title=request.transcript_title,
            user_id=str(current_user.id),
            project_id=request.project_id,
            enable_pii_redaction=request.enable_pii_redaction,
            stage_params={
                "fact_extraction": request.stage_params.fact_extraction.model_dump() if request.stage_params and request.stage_params.fact_extraction else None,
                "reasoning": request.stage_params.reasoning.model_dump() if request.stage_params and request.stage_params.reasoning else None,
                "summary": request.stage_params.summary.model_dump() if request.stage_params and request.stage_params.summary else None,
            } if request.stage_params else {},
            system_prompts={
                "stage1": request.system_prompts.stage1_fact_extraction if request.system_prompts else None,
                "stage2": request.system_prompts.stage2_reasoning if request.system_prompts else None,
                "stage3": request.system_prompts.stage3_summary if request.system_prompts else None,
            },
            models={
                "stage1": request.models.stage1_model if request.models else None,
                "stage2": request.models.stage2_model if request.models else None,
                "stage3": request.models.stage3_model if request.models else None,
            },
            evaluation_ids=request.evaluations or [],
        )

        # Convert traces to API format
        traces = [
            TraceMetadata(
                trace_id=trace["trace_id"],
                stage=trace["stage"],
                model=trace["model"],
                temperature=trace["temperature"],
                top_p=trace["top_p"],
                max_tokens=trace["max_tokens"],
                input_tokens=trace["input_tokens"],
                output_tokens=trace["output_tokens"],
                total_tokens=trace["total_tokens"],
                duration_ms=trace["duration_ms"],
                cost=trace["cost"],
                system_prompt=trace.get("system_prompt"),  # Include custom system prompt
            )
            for trace in result["traces"]
        ]

        # Convert evaluations to API format
        evaluations = [
            EvaluationMetric(
                evaluation_name=eval["evaluation_name"],
                evaluation_uuid=eval["evaluation_uuid"],
                score=eval["score"],
                passed=eval["passed"],
                reason=eval["reason"],
                threshold=eval.get("threshold"),
                category=eval.get("category"),
                input_tokens=eval.get("input_tokens"),
                output_tokens=eval.get("output_tokens"),
                total_tokens=eval.get("total_tokens"),
                evaluation_cost=eval.get("evaluation_cost"),
            )
            for eval in result["evaluations"]
        ]

        return CallInsightsAnalyzeResponse(
            analysis_id=result["analysis_id"],  # Use database ID from service
            project_id=request.project_id,
            summary=result["summary"],
            insights=result["insights"],
            facts=result["facts"],
            pii_redacted=result["pii_redacted"],
            traces=traces,
            evaluations=evaluations,
            total_tokens=result["total_tokens"],
            total_cost=result["total_cost"],
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze call transcript: {str(e)}",
        )


@router.get("/history", response_model=List[CallInsightsHistoryItem])
async def get_analysis_history(
    project_id: Optional[str] = Query(None, description="Filter by project UUID"),
    search: Optional[str] = Query(None, description="Search in title or transcript text"),
    limit: int = Query(10, ge=1, le=100, description="Max number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get call insights analysis history

    Returns list of previous analyses with:
    - Optional filtering by project ID
    - Optional search in title or transcript text
    - Pagination support
    - Organization-scoped (only user's org)
    """
    # Build query
    query = select(CallInsightsAnalysis).where(
        CallInsightsAnalysis.organization_id == current_user.organization_id
    )

    # Apply filters
    if project_id:
        query = query.where(CallInsightsAnalysis.project_id == project_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                CallInsightsAnalysis.transcript_title.ilike(search_pattern),
                CallInsightsAnalysis.transcript_input.ilike(search_pattern)
            )
        )

    # Order by most recent first
    query = query.order_by(CallInsightsAnalysis.created_at.desc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    analyses = result.scalars().all()

    # Convert to response format with preview
    return [
        CallInsightsHistoryItem(
            id=str(analysis.id),
            transcript_title=analysis.transcript_title,
            transcript_preview=analysis.transcript_input[:200] + "..." if len(analysis.transcript_input) > 200 else analysis.transcript_input,
            project_id=str(analysis.project_id) if analysis.project_id else None,
            total_tokens=analysis.total_tokens,
            total_cost=analysis.total_cost,
            pii_redacted=analysis.pii_redacted,
            created_at=analysis.created_at.isoformat(),
        )
        for analysis in analyses
    ]


class AvailableModel(BaseModel):
    """Available model configuration"""
    model_id: str = Field(..., description="Model identifier (e.g., 'gpt-4o-mini')")
    display_name: str = Field(..., description="Human-readable model name")
    provider: str = Field(..., description="Model provider (e.g., 'OpenAI')")
    description: Optional[str] = Field(None, description="Model description")
    input_cost: float = Field(..., description="Cost per 1K input tokens")
    output_cost: float = Field(..., description="Cost per 1K output tokens")
    context_window: Optional[int] = Field(None, description="Maximum context window size")


@router.get("/models/available", response_model=List[AvailableModel])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of available models for the current user's organization

    Only returns models from providers that the organization has configured
    API keys for. This ensures users only see models they can actually use.

    Response includes:
    - Model identifiers
    - Display names
    - Cost information (from database metadata)
    - Context window sizes
    """
    # First, get the list of configured providers for this organization
    configured_providers_result = await db.execute(
        select(ModelProviderConfig.provider_name).where(
            and_(
                ModelProviderConfig.organization_id == current_user.organization_id,
                ModelProviderConfig.is_active == True
            )
        ).distinct()
    )
    configured_provider_names = {row[0] for row in configured_providers_result.all()}

    # If no providers configured, return empty list
    if not configured_provider_names:
        return []

    # Query ModelProviderMetadata for active LLM providers that are configured
    result = await db.execute(
        select(ModelProviderMetadata).where(
            and_(
                ModelProviderMetadata.provider_type == "llm",
                ModelProviderMetadata.is_active == True,
                ModelProviderMetadata.provider_name.in_(configured_provider_names)
            )
        )
    )
    providers = result.scalars().all()

    available_models = []

    for provider in providers:
        # Extract model options from optional_fields
        # Structure: optional_fields = [{"name": "default_model", "options": ["gpt-4", ...], "pricing": {...}, "context_windows": {...}}]
        if not provider.optional_fields:
            continue

        # Find the default_model field which contains model options
        for field in provider.optional_fields:
            if field.get("name") == "default_model":
                model_options = field.get("options", [])
                pricing = field.get("pricing", {})
                context_windows = field.get("context_windows", {})

                # Create AvailableModel for each model option
                for model_id in model_options:
                    model_pricing = pricing.get(model_id, {})

                    available_models.append(
                        AvailableModel(
                            model_id=model_id,
                            display_name=field.get("model_display_names", {}).get(model_id, model_id),
                            provider=provider.display_name,
                            description=model_pricing.get("description", ""),
                            input_cost=model_pricing.get("input", 0.01),
                            output_cost=model_pricing.get("output", 0.03),
                            context_window=context_windows.get(model_id, 128000),
                        )
                    )

    return available_models


@router.get("/{analysis_id}", response_model=CallInsightsHistoryResponse)
async def get_analysis_by_id(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific analysis by ID

    Returns full analysis including:
    - Complete transcript
    - All 3 stage outputs (facts, insights, summary)
    - Metrics and metadata
    """
    # Get analysis
    query = select(CallInsightsAnalysis).where(
        and_(
            CallInsightsAnalysis.id == analysis_id,
            CallInsightsAnalysis.organization_id == current_user.organization_id
        )
    )
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return CallInsightsHistoryResponse(
        id=str(analysis.id),
        transcript_title=analysis.transcript_title,
        transcript_input=analysis.transcript_input,
        summary_output=analysis.summary_output,
        insights_output=analysis.insights_output,
        facts_output=analysis.facts_output,
        pii_redacted=analysis.pii_redacted,
        total_tokens=analysis.total_tokens,
        total_cost=analysis.total_cost,
        project_id=str(analysis.project_id) if analysis.project_id else None,
        system_prompt_stage1=analysis.system_prompt_stage1,
        system_prompt_stage2=analysis.system_prompt_stage2,
        system_prompt_stage3=analysis.system_prompt_stage3,
        model_stage1=analysis.model_stage1,
        model_stage2=analysis.model_stage2,
        model_stage3=analysis.model_stage3,
        created_at=analysis.created_at.isoformat(),
    )