"""
Pydantic schemas for Insight Comparison API
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Stage-level comparison schemas
# ============================================================================

class StageScores(BaseModel):
    """Scores for a single model in a single stage"""
    groundedness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Factual grounding score")
    faithfulness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Faithfulness to source score")
    completeness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Completeness score")
    clarity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Clarity and coherence score")
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Factual accuracy score")


class StageComparisonScores(BaseModel):
    """Comparison scores for both models in a stage"""
    A: StageScores = Field(..., description="Scores for Model A")
    B: StageScores = Field(..., description="Scores for Model B")


class StageComparisonResult(BaseModel):
    """Result for a single stage comparison"""
    stage: str = Field(..., description="Stage name (e.g., 'Stage 1: Fact Extraction')")
    winner: str = Field(..., description="Winner: 'A', 'B', or 'tie'")
    scores: StageComparisonScores = Field(..., description="Scores for both models")
    reasoning: str = Field(..., description="Judge's reasoning for this stage")


# ============================================================================
# Analysis summary schemas (for comparison selection)
# ============================================================================

class AnalysisSummary(BaseModel):
    """Summary of an analysis for comparison selection"""
    id: str = Field(..., description="Analysis UUID")
    transcript_title: Optional[str] = Field(None, description="Transcript title")
    model_stage1: Optional[str] = Field(None, description="Model used for stage 1")
    model_stage2: Optional[str] = Field(None, description="Model used for stage 2")
    model_stage3: Optional[str] = Field(None, description="Model used for stage 3")
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost in USD")
    created_at: str = Field(..., description="ISO8601 timestamp")


# ============================================================================
# Request schemas
# ============================================================================

class CreateComparisonRequest(BaseModel):
    """Request to create a new comparison"""
    analysis_a_id: str = Field(..., description="First analysis UUID")
    analysis_b_id: str = Field(..., description="Second analysis UUID")
    judge_model: Optional[str] = Field(
        "claude-sonnet-4-5-20250929",
        description="Judge model to use (exact API version, default: claude-sonnet-4-5-20250929)"
    )
    judge_temperature: Optional[float] = Field(
        0.0,
        ge=0.0,
        le=2.0,
        description=(
            "Temperature for judge model evaluation (default: 0.0 for deterministic evaluation). "
            "0.0 = fully deterministic (recommended for consistent A/B testing), "
            "0.3-0.5 = slightly varied responses with nuanced reasoning, "
            "0.7-1.0 = more creative/varied but less consistent (not recommended for comparisons). "
            "NOTE: GPT-5 models only support temperature=1.0 (enforced automatically)"
        )
    )
    judge_reasoning_effort: Optional[str] = Field(
        "medium",
        description=(
            "GPT-5 only - controls thinking time (default: medium, RECOMMENDED for comparisons). "
            "• minimal = Fast responses, minimal reasoning (extraction, formatting, classification) "
            "• low = Faster with less thinking "
            "• medium = Balanced reasoning (RECOMMENDED for comparisons) "
            "• high = Maximum quality with extended reasoning (complex analysis) "
            "NOTE: Only applicable to gpt-5, gpt-5-mini, gpt-5-nano models. Ignored for other models."
        )
    )
    evaluation_criteria: Optional[List[str]] = Field(
        ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"],
        description="Criteria to evaluate (default: all 5)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_a_id": "550e8400-e29b-41d4-a716-446655440000",
                "analysis_b_id": "550e8400-e29b-41d4-a716-446655440001",
                "judge_model": "claude-sonnet-4-5-20250929",
                "judge_temperature": 0.0,
                "evaluation_criteria": [
                    "groundedness",
                    "faithfulness",
                    "completeness",
                    "clarity",
                    "accuracy"
                ]
            }
        }


# ============================================================================
# Response schemas
# ============================================================================

class JudgeTraceMetadata(BaseModel):
    """Metadata about the judge model invocation"""
    trace_id: Optional[str] = Field(None, description="Trace UUID for judge invocation")
    model: str = Field(..., description="Judge model used")
    total_tokens: int = Field(..., description="Total tokens used by judge")
    cost: float = Field(..., description="Cost of judge invocation in USD")
    duration_ms: float = Field(..., description="Judge invocation duration in milliseconds")


class ComparisonResponse(BaseModel):
    """Full comparison result"""
    # Basic info
    id: str = Field(..., description="Comparison UUID")
    organization_id: str = Field(..., description="Organization UUID")
    user_id: str = Field(..., description="User UUID")

    # Analyses being compared
    analysis_a: AnalysisSummary = Field(..., description="First analysis summary")
    analysis_b: AnalysisSummary = Field(..., description="Second analysis summary")

    # Judge configuration
    judge_model: str = Field(..., description="Judge model used")
    evaluation_criteria: List[str] = Field(..., description="Criteria evaluated")

    # Overall results
    overall_winner: str = Field(..., description="Overall winner: 'A', 'B', or 'tie'")
    overall_reasoning: str = Field(..., description="Judge's overall reasoning with cost-benefit analysis")

    # Per-stage results
    stage_results: List[StageComparisonResult] = Field(..., description="Results for each stage")

    # Judge trace
    judge_trace: JudgeTraceMetadata = Field(..., description="Judge model invocation metadata")

    # Timestamps
    created_at: str = Field(..., description="ISO8601 timestamp of comparison creation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "organization_id": "770e8400-e29b-41d4-a716-446655440000",
                "user_id": "880e8400-e29b-41d4-a716-446655440000",
                "analysis_a": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "transcript_title": "Customer Call - Q3 2025",
                    "model_stage1": "gpt-4o-mini",
                    "model_stage2": "gpt-4o-mini",
                    "model_stage3": "gpt-4o-mini",
                    "total_tokens": 3500,
                    "total_cost": 0.0012,
                    "created_at": "2025-10-10T14:20:00Z"
                },
                "analysis_b": {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "transcript_title": "Customer Call - Q3 2025",
                    "model_stage1": "gpt-4o",
                    "model_stage2": "gpt-4o",
                    "model_stage3": "gpt-4o",
                    "total_tokens": 3600,
                    "total_cost": 0.0180,
                    "created_at": "2025-10-10T14:25:00Z"
                },
                "judge_model": "claude-sonnet-4.5",
                "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"],
                "overall_winner": "B",
                "overall_reasoning": "Model B (gpt-4o) provided more grounded and complete analysis with 15% better scores across key metrics...",
                "stage_results": [
                    {
                        "stage": "Stage 1: Fact Extraction",
                        "winner": "B",
                        "scores": {
                            "A": {
                                "groundedness": 0.82,
                                "faithfulness": 0.85,
                                "completeness": 0.78,
                                "clarity": 0.88,
                                "accuracy": 0.80
                            },
                            "B": {
                                "groundedness": 0.95,
                                "faithfulness": 0.93,
                                "completeness": 0.90,
                                "clarity": 0.89,
                                "accuracy": 0.94
                            }
                        },
                        "reasoning": "Model B extracted more comprehensive facts with higher accuracy..."
                    }
                ],
                "judge_trace": {
                    "trace_id": "990e8400-e29b-41d4-a716-446655440000",
                    "model": "claude-sonnet-4.5",
                    "total_tokens": 8500,
                    "cost": 0.0255,
                    "duration_ms": 4200
                },
                "created_at": "2025-10-10T14:30:00Z"
            }
        }


class ComparisonListItem(BaseModel):
    """Comparison summary for list view with enhanced details"""
    id: str = Field(..., description="Comparison UUID")
    analysis_a_title: Optional[str] = Field(None, description="Title of first analysis")
    analysis_b_title: Optional[str] = Field(None, description="Title of second analysis")
    model_a_summary: str = Field(..., description="Summary of models used in A (e.g., 'gpt-4o-mini (all stages)')")
    model_b_summary: str = Field(..., description="Summary of models used in B")
    # Model details for A
    model_a_stage1: Optional[str] = Field(None, description="Model A stage 1")
    model_a_stage2: Optional[str] = Field(None, description="Model A stage 2")
    model_a_stage3: Optional[str] = Field(None, description="Model A stage 3")
    params_a: Optional[Dict] = Field(None, description="Model A parameters (temperature, top_p, max_tokens)")
    # Model details for B
    model_b_stage1: Optional[str] = Field(None, description="Model B stage 1")
    model_b_stage2: Optional[str] = Field(None, description="Model B stage 2")
    model_b_stage3: Optional[str] = Field(None, description="Model B stage 3")
    params_b: Optional[Dict] = Field(None, description="Model B parameters (temperature, top_p, max_tokens)")
    # Cost and tokens
    cost_a: float = Field(..., description="Model A total cost")
    cost_b: float = Field(..., description="Model B total cost")
    tokens_a: int = Field(..., description="Model A total tokens")
    tokens_b: int = Field(..., description="Model B total tokens")
    # Comparison results
    judge_model: str = Field(..., description="Judge model used")
    overall_winner: str = Field(..., description="Winner: 'A', 'B', or 'tie'")
    cost_difference: str = Field(..., description="Cost difference formatted (e.g., '+$0.015' or '-$0.005')")
    quality_improvement: str = Field(..., description="Quality improvement percentage (e.g., '+15%' or '-5%')")
    created_at: str = Field(..., description="ISO8601 timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "analysis_a_title": "Customer Call - Q3 2025",
                "analysis_b_title": "Customer Call - Q3 2025",
                "model_a_summary": "gpt-4o-mini (all stages)",
                "model_b_summary": "gpt-4o (all stages)",
                "judge_model": "claude-sonnet-4.5",
                "overall_winner": "B",
                "cost_difference": "+$0.015",
                "quality_improvement": "+15%",
                "created_at": "2025-10-10T14:30:00Z"
            }
        }


class ComparisonListResponse(BaseModel):
    """Paginated list of comparisons"""
    comparisons: List[ComparisonListItem] = Field(..., description="List of comparisons")
    pagination: Dict[str, int] = Field(..., description="Pagination info")

    class Config:
        json_schema_extra = {
            "example": {
                "comparisons": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440000",
                        "analysis_a_title": "Customer Call - Q3 2025",
                        "analysis_b_title": "Customer Call - Q3 2025",
                        "model_a_summary": "gpt-4o-mini (all stages)",
                        "model_b_summary": "gpt-4o (all stages)",
                        "judge_model": "claude-sonnet-4.5",
                        "overall_winner": "B",
                        "cost_difference": "+$0.015",
                        "quality_improvement": "+15%",
                        "created_at": "2025-10-10T14:30:00Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 45,
                    "total_pages": 3
                }
            }
        }


# ============================================================================
# Error response schemas
# ============================================================================

class ComparisonError(BaseModel):
    """Error response for comparison operations"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "DIFFERENT_TRANSCRIPTS",
                "message": "Cannot compare analyses with different transcripts",
                "details": {
                    "analysis_a_transcript_length": 5000,
                    "analysis_b_transcript_length": 8000
                }
            }
        }
