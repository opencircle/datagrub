"""
Evaluation and EvaluationResult schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class EvaluationResultResponse(BaseModel):
    """Evaluation result response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evaluation_id: UUID
    test_name: str
    input_data: Dict[str, Any]
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    score: Optional[float] = None
    passed: bool = False
    latency_ms: Optional[float] = None
    token_count: Optional[int] = None
    cost: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime


class EvaluationListItem(BaseModel):
    """Evaluation list item for playground dashboard with enhanced fields"""

    id: UUID
    name: str
    description: Optional[str] = None
    type: str  # vendor | promptforge | custom
    status: str  # pending | running | completed | failed
    trace_id: UUID
    trace_identifier: str  # trace.trace_id for lookup
    project_id: Optional[UUID] = None

    # NEW P0 fields
    prompt_title: str  # trace.name (user title or project name)
    model: str  # trace.model_name from evaluation
    vendor_name: Optional[str] = None  # evaluation_catalog.vendor_name
    category: Optional[str] = None  # evaluation_catalog.category

    # Results
    avg_score: Optional[float] = None
    passed: Optional[bool] = None  # Added explicit pass/fail field
    total_tests: int = 0
    passed_tests: int = 0

    # Metrics
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_ms: float = 0.0
    created_at: datetime


class EvaluationListResponse(BaseModel):
    """Response schema for evaluation list endpoint"""

    evaluations: List[EvaluationListItem]
    total: int
    limit: int
    offset: int


class TraceMinimal(BaseModel):
    """Minimal trace information for evaluation detail"""

    id: UUID
    trace_id: str
    name: str
    status: str


class EvaluationDetailResponse(BaseModel):
    """Detailed evaluation view for modal (P1)"""

    id: UUID
    trace_id: UUID
    trace_identifier: str

    # Trace context
    prompt_title: str
    model_name: str
    project_name: str
    project_id: UUID
    created_at: datetime

    # Evaluation details
    evaluation_name: str
    evaluation_type: str  # llm_based, heuristic
    vendor_name: Optional[str] = None
    category: Optional[str] = None
    source: str  # PROMPTFORGE, VENDOR, CUSTOM
    description: Optional[str] = None

    # Results
    score: Optional[float] = None
    threshold: Optional[float] = None
    passed: Optional[bool] = None
    reason: Optional[str] = None
    explanation: Optional[str] = None

    # Execution metrics
    execution_time_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    evaluation_cost: Optional[float] = None

    # Full data for debugging
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    llm_metadata: Optional[Dict[str, Any]] = None

    # Trace link
    trace: TraceMinimal


class EvaluationBase(BaseModel):
    """Base evaluation schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    evaluation_type: str = Field(..., pattern="^(accuracy|toxicity|bias|custom)$")
    config: Optional[Dict[str, Any]] = None
    dataset_id: Optional[str] = None


class EvaluationCreate(EvaluationBase):
    """Evaluation creation schema"""

    project_id: UUID
    prompt_id: Optional[UUID] = None


class EvaluationUpdate(BaseModel):
    """Evaluation update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed)$")
    config: Optional[Dict[str, Any]] = None


class EvaluationResponse(EvaluationBase):
    """Evaluation response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    prompt_id: Optional[UUID] = None
    created_by: UUID
    status: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    avg_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    results: Optional[list[EvaluationResultResponse]] = None
