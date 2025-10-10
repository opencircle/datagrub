"""
Trace and Span schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class SpanBase(BaseModel):
    """Base span schema"""

    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    span_type: Optional[str] = None
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    span_metadata: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None


class SpanCreate(SpanBase):
    """Span creation schema"""

    pass


class SpanResponse(SpanBase):
    """Span response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trace_id: UUID
    created_at: datetime


class TraceBase(BaseModel):
    """Base trace schema"""

    trace_id: str
    name: str
    status: str = "success"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    trace_metadata: Optional[Dict[str, Any]] = None
    total_duration_ms: Optional[float] = Field(None, ge=0, description="Duration in milliseconds (must be >= 0)")
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    error_type: Optional[str] = None


class TraceCreate(TraceBase):
    """Trace creation schema"""

    project_id: UUID
    prompt_version_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    spans: Optional[list[SpanCreate]] = None


class TraceResponse(TraceBase):
    """Trace response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    prompt_version_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    spans: Optional[list[SpanResponse]] = None


class AggregatedTraceData(BaseModel):
    """Aggregated data for parent traces with children"""

    total_tokens: int = Field(..., description="Sum of all child trace tokens")
    total_cost: float = Field(..., description="Sum of all child trace costs")
    model_names: List[str] = Field(default_factory=list, description="List of unique models used by children")
    avg_duration_ms: Optional[float] = Field(None, description="Average duration of children")


class TraceListItem(BaseModel):
    """Trace list item with joined data for UI"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trace_id: str  # requestId in UI
    project_name: str
    status: str
    model_name: Optional[str] = None
    provider: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    total_duration_ms: Optional[float] = None
    total_cost: Optional[float] = None
    environment: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    user_email: Optional[str] = None

    # Parent-child trace enhancement fields
    source: str = Field(default="Other", description="Trace source: Call Insights, Playground, Other")
    has_children: bool = Field(default=False, description="Whether this trace has child traces")
    child_count: int = Field(default=0, description="Number of child traces")
    children: List['TraceListItem'] = Field(default_factory=list, description="Child traces if parent")
    parent_trace_id: Optional[str] = Field(None, description="Parent trace ID if this is a child")
    stage: Optional[str] = Field(None, description="Stage name if this is a child trace")
    aggregated_data: Optional[AggregatedTraceData] = Field(None, description="Aggregated data for parent traces")


class TraceListResponse(BaseModel):
    """Paginated trace list response"""

    traces: list[TraceListItem]
    total: int
    page: int
    page_size: int


class EvaluationResultItem(BaseModel):
    """Evaluation result for trace detail view"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evaluation_name: str
    evaluation_source: str  # vendor, custom, promptforge, llm_judge
    evaluation_type: str  # metric, validator, classifier, judge
    category: str
    vendor_name: Optional[str] = None  # Display name of vendor (DeepEval, Ragas, etc.)
    score: Optional[float] = None
    passed: Optional[bool] = None
    category_result: Optional[str] = None
    reason: Optional[str] = None
    execution_time_ms: Optional[float] = None

    # Token and cost tracking
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    evaluation_cost: Optional[float] = None

    # Comprehensive LLM metadata
    llm_metadata: Optional[Dict[str, Any]] = None

    status: str = "completed"


class ChildTraceItem(BaseModel):
    """Child trace item for detail view - shows stage information"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trace_id: str
    stage: Optional[str] = None
    status: str
    model_name: Optional[str] = None
    provider: Optional[str] = None

    # Input and output for viewing system prompts
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None

    # Performance metrics
    total_duration_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None

    created_at: datetime


class TraceDetailResponse(BaseModel):
    """Comprehensive trace detail response with evaluations, spans, and metadata"""

    model_config = ConfigDict(from_attributes=True)

    # Basic trace information
    id: UUID
    trace_id: str
    name: str
    status: str

    # Project and model information
    project_id: UUID
    project_name: str
    prompt_version_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None

    # User and environment
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    environment: Optional[str] = None

    # Input and output
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    trace_metadata: Optional[Dict[str, Any]] = None

    # Performance metrics
    total_duration_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    retry_count: int = 0

    # Error tracking
    error_message: Optional[str] = None
    error_type: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Related data
    spans: Optional[list[SpanResponse]] = None
    evaluations: Optional[list[EvaluationResultItem]] = None
    children: Optional[list[ChildTraceItem]] = None
