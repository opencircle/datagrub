"""
Insight Comparison API endpoints - Compare two Call Insights analyses with blind judge evaluation
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.insight_comparison_service import InsightComparisonService
from app.schemas.insight_comparison import (
    CreateComparisonRequest,
    ComparisonResponse,
    ComparisonListItem,
    ComparisonListResponse,
    StageComparisonResult,
    AnalysisSummary,
    ComparisonError,
    JudgeTraceMetadata,
)

router = APIRouter()


@router.post("/comparisons", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
async def create_comparison(
    request: CreateComparisonRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new blind comparison between two Call Insights analyses

    This endpoint:
    1. Validates that both analyses exist and belong to the same organization
    2. Verifies both analyses used the same transcript (required for fair comparison)
    3. Executes blind evaluation with judge model:
       - Stage 1: Compare fact extraction quality
       - Stage 2: Compare reasoning and insights quality
       - Stage 3: Compare summary quality
       - Overall: Determine winner with cost-benefit analysis
    4. Creates trace for judge model invocation
    5. Saves comparison results to database
    6. Returns detailed comparison with per-stage scores and reasoning

    The judge model:
    - Does NOT know which AI model produced which output (blind evaluation)
    - Evaluates on 5 criteria: groundedness, faithfulness, completeness, clarity, accuracy
    - Provides scores (0.0-1.0) and detailed reasoning for each stage
    - Includes cost-benefit analysis in overall verdict

    Returns:
        ComparisonResponse with complete results including:
        - Overall winner ('A', 'B', or 'tie')
        - Per-stage results with scores and reasoning
        - Cost comparison and quality improvement metrics
        - Judge model trace metadata
    """
    try:
        # Initialize service
        comparison_service = InsightComparisonService(db, current_user.organization_id)

        # Create comparison
        result = await comparison_service.create_comparison(
            analysis_a_id=request.analysis_a_id,
            analysis_b_id=request.analysis_b_id,
            user_id=str(current_user.id),
            judge_model=request.judge_model or "claude-sonnet-4-5-20250929",
            judge_temperature=request.judge_temperature if request.judge_temperature is not None else 0.0,
            judge_reasoning_effort=request.judge_reasoning_effort,
            evaluation_criteria=request.evaluation_criteria,
        )

        # Convert to response schema
        return ComparisonResponse(
            id=result["comparison_id"],
            organization_id=str(current_user.organization_id),
            user_id=str(current_user.id),
            analysis_a=AnalysisSummary(**result["analysis_a"]),
            analysis_b=AnalysisSummary(**result["analysis_b"]),
            judge_model=request.judge_model or "claude-sonnet-4-5-20250929",
            evaluation_criteria=request.evaluation_criteria or [
                "groundedness", "faithfulness", "completeness", "clarity", "accuracy"
            ],
            overall_winner=result["overall_winner"],
            overall_reasoning=result["overall_reasoning"],
            stage_results=[
                StageComparisonResult(**stage_result)
                for stage_result in result["stage_results"]
            ],
            judge_trace=JudgeTraceMetadata(**result["judge_trace"]),
            created_at=result.get("created_at", ""),
        )

    except ValueError as e:
        # Handle validation errors (analyses not found, different orgs, different transcripts, duplicates)
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        elif "different organizations" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        elif "different transcripts" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
        elif "already exists" in str(e).lower():
            # Duplicate comparison - return 409 Conflict with existing comparison ID
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"[ERROR] Comparison creation failed:")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception message: {str(e)}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()

        # Handle duplicate comparison (unique constraint violation)
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Comparison already exists for these analyses with this judge model",
            )

        # Generic error handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comparison: {str(e)}",
        )


@router.get("/comparisons", response_model=ComparisonListResponse)
async def list_comparisons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all comparisons for the current organization

    Returns paginated list of comparisons with summary information:
    - Analysis titles
    - Models used for each analysis
    - Judge model used
    - Overall winner
    - Cost and quality metrics
    - Creation timestamp

    Pagination:
    - Default: 20 items per page
    - Maximum: 100 items per page
    - Use `skip` and `limit` for pagination

    Returns:
        ComparisonListResponse with list of comparisons and pagination metadata
    """
    try:
        # Initialize service
        comparison_service = InsightComparisonService(db, current_user.organization_id)

        # Get comparisons with pagination
        result = await comparison_service.list_comparisons(
            skip=skip,
            limit=limit,
        )

        # Convert to response schema
        return ComparisonListResponse(
            comparisons=[
                ComparisonListItem(**item)
                for item in result["comparisons"]
            ],
            pagination=result["pagination"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list comparisons: {str(e)}",
        )


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(
    comparison_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed comparison results by ID

    Returns complete comparison including:
    - Full analysis summaries for both analyses
    - Per-stage scores and detailed reasoning
    - Overall winner with cost-benefit analysis
    - Judge model trace metadata
    - All evaluation criteria used

    Args:
        comparison_id: UUID of the comparison

    Returns:
        ComparisonResponse with complete comparison data
    """
    try:
        # Initialize service
        comparison_service = InsightComparisonService(db, current_user.organization_id)

        # Get comparison
        result = await comparison_service.get_comparison(comparison_id)

        # Convert to response schema
        return ComparisonResponse(
            id=result["id"],
            organization_id=result["organization_id"],
            user_id=result["user_id"],
            analysis_a=AnalysisSummary(**result["analysis_a"]),
            analysis_b=AnalysisSummary(**result["analysis_b"]),
            judge_model=result["judge_model"],
            evaluation_criteria=result["evaluation_criteria"],
            overall_winner=result["overall_winner"],
            overall_reasoning=result["overall_reasoning"],
            stage_results=[
                StageComparisonResult(**stage_result)
                for stage_result in result["stage_results"]
            ],
            judge_trace=JudgeTraceMetadata(**result["judge_trace"]),
            created_at=result["created_at"],
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        elif "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comparison: {str(e)}",
        )


@router.delete("/comparisons/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comparison(
    comparison_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a comparison by ID

    This permanently removes the comparison record. The original analyses
    are not affected.

    Args:
        comparison_id: UUID of the comparison to delete

    Returns:
        204 No Content on success
    """
    try:
        # Initialize service
        comparison_service = InsightComparisonService(db, current_user.organization_id)

        # Delete comparison
        await comparison_service.delete_comparison(comparison_id)

        return None  # 204 No Content

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        elif "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comparison: {str(e)}",
        )
