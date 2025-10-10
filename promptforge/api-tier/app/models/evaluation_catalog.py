"""
Evaluation Catalog and Trace Evaluation models for EAL (Evaluation Abstraction Layer)
"""
import enum
from sqlalchemy import Column, String, Text, ForeignKey, Float, Integer, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import BaseModel


class EvaluationSource(str, enum.Enum):
    """Source of the evaluation"""
    VENDOR = "vendor"              # Third-party evaluation library (DeepEval, Ragas, etc.)
    CUSTOM = "custom"              # Client-specific custom evaluation
    PROMPTFORGE = "promptforge"    # PromptForge platform-provided evaluation
    LLM_JUDGE = "llm_judge"        # LLM-as-Judge evaluation


class EvaluationType(str, enum.Enum):
    """Type of evaluation"""
    METRIC = "metric"              # Quantitative score (0.0-1.0)
    VALIDATOR = "validator"        # Pass/fail boolean check
    CLASSIFIER = "classifier"      # Categorization/classification
    JUDGE = "judge"                # Subjective LLM-based assessment


class EvaluationCategory(str, enum.Enum):
    """Category of evaluation"""
    QUALITY = "quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SAFETY = "safety"
    BIAS = "bias"
    BUSINESS_RULES = "business_rules"
    CUSTOM = "custom"


class EvaluationCatalog(BaseModel):
    """
    Evaluation Catalog - Registry of all available evaluations

    This table stores metadata about all available evaluations from:
    - Third-party vendors (DeepEval, Ragas, MLflow, etc.)
    - Custom client evaluations (business rules, validators)
    - PromptForge proprietary evaluations
    - LLM-as-Judge evaluations
    """

    __tablename__ = "evaluation_catalog"

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(EvaluationCategory), nullable=False, index=True)

    # Source and Type
    source = Column(SQLEnum(EvaluationSource), nullable=False, index=True)
    evaluation_type = Column(SQLEnum(EvaluationType), nullable=False, index=True)

    # Multi-tenancy and Access Control
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    is_public = Column(Boolean, default=False, nullable=False, index=True)

    # Configuration
    config_schema = Column(JSON)  # JSON schema for configuration parameters
    default_config = Column(JSON)  # Default configuration values

    # Implementation Details
    implementation = Column(Text, nullable=True)  # Python code for CUSTOM evaluations
    adapter_class = Column(String(255), nullable=True)  # Adapter class name for VENDOR evaluations
    adapter_evaluation_id = Column(String(255), nullable=True, index=True)  # Adapter's internal evaluation ID
    vendor_name = Column(String(100), nullable=True, index=True)  # Display name of vendor (DeepEval, Ragas, etc.)

    # LLM-as-Judge Specific
    llm_criteria = Column(Text, nullable=True)  # Evaluation criteria for LLM judge
    llm_model = Column(String(100), nullable=True)  # Model to use (gpt-4, claude-3, etc.)
    llm_system_prompt = Column(Text, nullable=True)  # System prompt for LLM judge

    # Custom Evaluation Fields (added in migration k7i1j2k3l4m5)
    # These fields define how the evaluation accesses and assesses model input/output AFTER invocation
    prompt_input = Column(Text, nullable=True)  # Model input definition: how to access model's input (use {{model_input}})
    prompt_output = Column(Text, nullable=True)  # Model output definition: how to access model's output (use {{model_output}})
    custom_system_prompt = Column(Text, nullable=True)  # Evaluation system prompt: evaluates model input/output, returns score and pass/fail
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # User who created this custom evaluation

    # Metadata
    version = Column(String(50), default="1.0.0")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    tags = Column(JSON)  # Array of string tags for search/filtering

    # Relationships
    organization = relationship("Organization", backref="evaluation_catalog")
    project = relationship("Project", backref="evaluation_catalog")
    creator = relationship("User", backref="created_catalog_evaluations")
    trace_evaluations = relationship("TraceEvaluation", back_populates="evaluation_catalog_entry", cascade="all, delete-orphan")


class TraceEvaluation(BaseModel):
    """
    Trace Evaluation - Links traces to evaluation results

    This table stores the results of running evaluations on specific traces.
    It serves as the linkage between traces and the evaluation catalog.
    """

    __tablename__ = "trace_evaluations"

    # Foreign Keys
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=False, index=True)
    evaluation_catalog_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_catalog.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)  # Multi-tenant isolation (added in k7i1j2k3l4m5)

    # Evaluation Results
    score = Column(Float, nullable=True)  # Numeric score (0.0-1.0) for METRIC type
    passed = Column(Boolean, nullable=True)  # Pass/fail for VALIDATOR type
    category = Column(String(255), nullable=True)  # Category result for CLASSIFIER type
    reason = Column(Text, nullable=True)  # Explanation of the result

    # Detailed Results
    details = Column(JSON)  # Detailed metrics and analysis
    suggestions = Column(JSON)  # Array of improvement suggestions

    # Execution Metadata
    execution_time_ms = Column(Float)  # Time taken to run evaluation
    model_used = Column(String(100), nullable=True)  # Model used (for LLM-as-Judge)
    config = Column(JSON)  # Configuration used for this evaluation run

    # LLM Cost Tracking (for LLM-based evaluations)
    input_tokens = Column(Integer, nullable=True)  # Input tokens used by evaluation LLM
    output_tokens = Column(Integer, nullable=True)  # Output tokens used by evaluation LLM
    total_tokens = Column(Integer, nullable=True)  # Total tokens (input + output)
    evaluation_cost = Column(Float, nullable=True)  # Cost of running the evaluation

    # Vendor-Specific Metrics
    vendor_metrics = Column(JSON, nullable=True)  # Vendor-specific metrics as JSON

    # Comprehensive LLM Metadata (for detailed tracking of LLM-based evaluations)
    llm_metadata = Column(JSONB, nullable=True)  # Comprehensive LLM metrics (tokens, cost, latency, params, etc.)

    # Error Handling
    status = Column(String(50), default="completed", nullable=False)  # completed, failed, pending
    error_message = Column(Text, nullable=True)

    # Relationships
    trace = relationship("Trace", back_populates="trace_evaluations")
    evaluation_catalog_entry = relationship("EvaluationCatalog", back_populates="trace_evaluations")
    organization = relationship("Organization", backref="trace_evaluations")
