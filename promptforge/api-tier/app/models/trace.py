"""
Trace and Span models for observability
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Trace(BaseModel):
    """Trace model - represents a full execution trace"""

    __tablename__ = "traces"

    trace_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="success")  # success, error, timeout, retry

    # Execution details
    input_data = Column(JSON)
    output_data = Column(JSON)
    trace_metadata = Column(JSON)

    # Performance metrics
    total_duration_ms = Column(Float)
    input_tokens = Column(Integer, nullable=True)  # P0: Input tokens for trace
    output_tokens = Column(Integer, nullable=True)  # P0: Output tokens for trace
    total_tokens = Column(Integer)
    total_cost = Column(Float)

    # Denormalized model information (for faster queries)
    model_name = Column(String(100), nullable=True)  # P0: Denormalized from AIModel
    provider = Column(String(100), nullable=True)  # P0: Denormalized from ModelProvider

    # Environment and retry tracking
    environment = Column(String(50), nullable=True, index=True)  # P1: production, staging, development
    retry_count = Column(Integer, default=0, nullable=False)  # P1: Number of retries

    # User tracking
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # P0: User who triggered trace

    # Error tracking
    error_message = Column(Text)
    error_type = Column(String(100))

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    prompt_version_id = Column(UUID(as_uuid=True), ForeignKey("prompt_versions.id"))
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"))

    # Relationships
    project = relationship("Project", back_populates="traces")
    prompt_version = relationship("PromptVersion", back_populates="traces")
    model = relationship("AIModel", back_populates="traces")
    user = relationship("User", foreign_keys=[user_id], backref="traces")
    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")
    policy_violations = relationship("PolicyViolation", back_populates="trace")
    trace_evaluations = relationship("TraceEvaluation", back_populates="trace", cascade="all, delete-orphan")


class Span(BaseModel):
    """Span model - represents a step within a trace"""

    __tablename__ = "spans"

    span_id = Column(String(255), nullable=False, unique=True, index=True)
    parent_span_id = Column(String(255), index=True)  # For nested spans
    name = Column(String(255), nullable=False)
    span_type = Column(String(50))  # llm, retrieval, tool, chain

    # Timing
    start_time = Column(Float, nullable=False)  # Unix timestamp
    end_time = Column(Float)
    duration_ms = Column(Float)

    # Span data
    input_data = Column(JSON)
    output_data = Column(JSON)
    span_metadata = Column(JSON)

    # LLM-specific fields
    model_name = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    temperature = Column(Float)
    max_tokens = Column(Integer)

    # Status
    status = Column(String(50), default="success")
    error_message = Column(Text)

    # Foreign Keys
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=False)

    # Relationships
    trace = relationship("Trace", back_populates="spans")
