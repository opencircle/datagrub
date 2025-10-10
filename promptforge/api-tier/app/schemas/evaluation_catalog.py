"""
Evaluation Catalog and Trace Evaluation schemas for EAL
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.models.evaluation_catalog import EvaluationSource, EvaluationType, EvaluationCategory


# ==================== Evaluation Catalog Schemas ====================


class EvaluationCatalogBase(BaseModel):
    """Base evaluation catalog schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the evaluation")
    description: Optional[str] = Field(None, description="Detailed description of what this evaluation measures")
    category: EvaluationCategory = Field(..., description="Category of the evaluation")
    source: EvaluationSource = Field(..., description="Source of the evaluation")
    evaluation_type: EvaluationType = Field(..., description="Type of evaluation (metric, validator, etc.)")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for configuration parameters")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration values")
    tags: Optional[List[str]] = Field(None, description="Tags for search and filtering")


class EvaluationCatalogCreate(EvaluationCatalogBase):
    """Schema for creating a new evaluation in the catalog"""

    organization_id: Optional[UUID] = Field(None, description="Organization ID for custom evaluations")
    project_id: Optional[UUID] = Field(None, description="Project ID for project-scoped evaluations")
    is_public: bool = Field(False, description="Whether this evaluation is public (PromptForge evaluations)")

    # Implementation fields
    implementation: Optional[str] = Field(None, description="Python code for custom evaluations")
    adapter_class: Optional[str] = Field(None, description="Adapter class name for vendor evaluations")
    vendor_name: Optional[str] = Field(None, description="Display name of vendor (e.g., DeepEval, Ragas, MLflow)")

    # LLM-as-Judge specific
    llm_criteria: Optional[str] = Field(None, description="Evaluation criteria for LLM judge")
    llm_model: Optional[str] = Field(None, description="Model to use for LLM judge (e.g., gpt-4)")
    llm_system_prompt: Optional[str] = Field(None, description="System prompt for LLM judge")

    version: str = Field("1.0.0", description="Version of the evaluation")


class EvaluationCatalogUpdate(BaseModel):
    """Schema for updating an evaluation in the catalog"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[EvaluationCategory] = None
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    implementation: Optional[str] = None
    llm_criteria: Optional[str] = None
    llm_model: Optional[str] = None
    llm_system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None


class EvaluationCatalogResponse(EvaluationCatalogBase):
    """Schema for evaluation catalog response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    is_public: bool
    implementation: Optional[str] = None
    adapter_class: Optional[str] = None
    vendor_name: Optional[str] = None
    llm_criteria: Optional[str] = None
    llm_model: Optional[str] = None
    llm_system_prompt: Optional[str] = None
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EvaluationCatalogListResponse(BaseModel):
    """Schema for listing evaluations from the catalog"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    category: EvaluationCategory
    source: EvaluationSource
    evaluation_type: EvaluationType
    is_public: bool
    is_active: bool
    tags: Optional[List[str]] = None
    version: str


# ==================== Trace Evaluation Schemas ====================


class TraceEvaluationBase(BaseModel):
    """Base trace evaluation schema"""

    trace_id: UUID = Field(..., description="ID of the trace being evaluated")
    evaluation_catalog_id: UUID = Field(..., description="ID of the evaluation from the catalog")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration used for this evaluation run")


class TraceEvaluationCreate(TraceEvaluationBase):
    """Schema for creating a trace evaluation"""

    pass


class TraceEvaluationResult(BaseModel):
    """Schema for trace evaluation result (returned by adapters)"""

    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Numeric score (0.0-1.0) for metrics")
    passed: Optional[bool] = Field(None, description="Pass/fail result for validators")
    category: Optional[str] = Field(None, description="Category result for classifiers")
    reason: Optional[str] = Field(None, description="Explanation of the result")
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed metrics and analysis")
    suggestions: Optional[List[str]] = Field(None, description="Improvement suggestions")
    execution_time_ms: Optional[float] = Field(None, description="Time taken to run evaluation")
    model_used: Optional[str] = Field(None, description="Model used (for LLM-as-Judge)")


class TraceEvaluationResponse(TraceEvaluationBase):
    """Schema for trace evaluation response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    score: Optional[float] = None
    passed: Optional[bool] = None
    category: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    execution_time_ms: Optional[float] = None
    model_used: Optional[str] = None

    # Token and cost tracking
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    evaluation_cost: Optional[float] = None
    vendor_metrics: Optional[Dict[str, Any]] = None

    # Comprehensive LLM metadata
    llm_metadata: Optional[Dict[str, Any]] = Field(None, description="Comprehensive LLM metrics")

    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ==================== Evaluation Execution Schemas ====================


class EvaluationExecutionRequest(BaseModel):
    """Schema for executing evaluations on a trace"""

    trace_id: UUID = Field(..., description="ID of the trace to evaluate")
    evaluation_ids: List[UUID] = Field(..., min_length=1, description="List of evaluation catalog IDs to run")
    config_overrides: Optional[Dict[UUID, Dict[str, Any]]] = Field(
        None,
        description="Configuration overrides per evaluation (keyed by evaluation_catalog_id)"
    )


class EvaluationExecutionResponse(BaseModel):
    """Schema for evaluation execution response"""

    trace_id: UUID
    total_evaluations: int
    successful_evaluations: int
    failed_evaluations: int
    results: List[TraceEvaluationResponse]
    errors: Optional[List[Dict[str, Any]]] = None


# ==================== Custom Evaluator Schema ====================


class CustomEvaluatorRequest(BaseModel):
    """Schema for creating a custom evaluator"""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the custom evaluator")
    description: str = Field(..., description="Description of what the evaluator does")
    category: EvaluationCategory = Field(..., description="Category of the evaluation")
    evaluation_type: EvaluationType = Field(..., description="Type of evaluation")
    implementation: str = Field(..., description="Python code implementing the evaluator")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Configuration schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration")
    organization_id: Optional[UUID] = Field(None, description="Organization scope (optional)")
    project_id: Optional[UUID] = Field(None, description="Project scope (optional)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


# ==================== LLM-as-Judge Schema ====================


class LLMJudgeEvaluatorRequest(BaseModel):
    """Schema for creating an LLM-as-Judge evaluator"""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the LLM judge evaluator")
    description: str = Field(..., description="Description of what the judge evaluates")
    category: EvaluationCategory = Field(..., description="Category of the evaluation")
    llm_criteria: str = Field(..., description="Detailed criteria for the LLM to judge against")
    llm_model: str = Field("gpt-4", description="Model to use (gpt-4, claude-3-opus, etc.)")
    llm_system_prompt: Optional[str] = Field(None, description="Custom system prompt for the LLM")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="Additional configuration schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration")
    organization_id: Optional[UUID] = Field(None, description="Organization scope (optional)")
    project_id: Optional[UUID] = Field(None, description="Project scope (optional)")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


# ==================== Filter and Query Schemas ====================


class EvaluationCatalogFilter(BaseModel):
    """Schema for filtering evaluations in the catalog"""

    source: Optional[EvaluationSource] = Field(None, description="Filter by source")
    category: Optional[EvaluationCategory] = Field(None, description="Filter by category")
    evaluation_type: Optional[EvaluationType] = Field(None, description="Filter by evaluation type")
    organization_id: Optional[UUID] = Field(None, description="Filter by organization")
    project_id: Optional[UUID] = Field(None, description="Filter by project")
    is_public: Optional[bool] = Field(None, description="Filter by public/private")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (AND logic)")
    search: Optional[str] = Field(None, description="Search in name and description")
