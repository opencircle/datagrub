"""
Evaluation execution schemas for running evaluations on traces
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class EvaluationRunRequest(BaseModel):
    """Request schema for running evaluations on a trace"""

    evaluation_ids: List[UUID] = Field(..., min_length=1, description="List of evaluation IDs to run")
    trace_id: UUID = Field(..., description="ID of the trace to evaluate")
    model_override: Optional[str] = Field(None, description="Override model for evaluation execution")


class EvaluationRunResult(BaseModel):
    """Result schema for a single evaluation run"""

    evaluation_id: UUID
    evaluation_name: str
    trace_id: UUID  # child trace created for this evaluation
    score: Optional[float] = None
    passed: Optional[bool] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)  # tokens, cost, duration, model
    status: str = "completed"  # completed | failed
    error_message: Optional[str] = None


class CustomEvaluationCreate(BaseModel):
    """Schema for creating a custom evaluation"""

    name: str = Field(..., min_length=3, max_length=255, description="Name of the evaluation")
    category: str = Field(..., min_length=1, max_length=100, description="Category (accuracy, groundedness, etc.)")
    description: Optional[str] = Field(None, description="Description of what this evaluation does")
    prompt_input: str = Field(..., min_length=10, description="Prompt template for input evaluation")
    prompt_output: str = Field(..., min_length=10, description="Prompt template for output evaluation")
    system_prompt: str = Field(..., min_length=10, description="System prompt for evaluation logic")
    model: str = Field(default="gpt-4o-mini", description="Model to use for evaluation")


class CustomEvaluationResponse(BaseModel):
    """Response schema for created custom evaluation"""

    id: UUID
    name: str
    category: str
    description: Optional[str] = None
    source: str  # = "custom"
    created_by: UUID
    created_at: datetime
