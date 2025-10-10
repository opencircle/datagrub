"""
Call Insights Analysis Model - Stores completed DTA pipeline results
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class CallInsightsAnalysis(Base):
    """
    Call Insights Analysis - 3-stage DTA pipeline results

    Stores completed analyses for history lookup and reuse.
    Each analysis includes transcript, all 3 stage outputs, traces, and evaluation results.
    """
    __tablename__ = "call_insights_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)

    # Input
    transcript_title = Column(String(500), nullable=True, index=True)  # NEW: Searchable title
    transcript_input = Column(Text, nullable=False)

    # System Prompts (custom prompts for each stage)
    system_prompt_stage1 = Column(Text, nullable=True)  # Fact extraction system prompt
    system_prompt_stage2 = Column(Text, nullable=True)  # Reasoning system prompt
    system_prompt_stage3 = Column(Text, nullable=True)  # Summary system prompt

    # Outputs from 3 stages
    facts_output = Column(Text, nullable=False)  # Stage 1
    insights_output = Column(Text, nullable=False)  # Stage 2
    summary_output = Column(Text, nullable=False)  # Stage 3

    # Configuration
    pii_redacted = Column(Boolean, default=False, nullable=False)
    stage_params = Column(JSONB, nullable=True)  # Custom parameters if used

    # Models used for each stage (for experimentation tracking)
    model_stage1 = Column(String(100), nullable=True, default="gpt-4o-mini")
    model_stage2 = Column(String(100), nullable=True, default="gpt-4o-mini")
    model_stage3 = Column(String(100), nullable=True, default="gpt-4o-mini")

    # Parent trace reference (links to traces table)
    parent_trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=True)

    # Metrics
    total_tokens = Column(Integer, nullable=False, default=0)
    total_cost = Column(Float, nullable=False, default=0.0)
    total_duration_ms = Column(Float, nullable=True)

    # Metadata
    analysis_metadata = Column(JSONB, nullable=True)  # Additional analysis metadata

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="call_insights_analyses")
    user = relationship("User", back_populates="call_insights_analyses")
    project = relationship("Project", back_populates="call_insights_analyses")
    parent_trace = relationship("Trace", foreign_keys=[parent_trace_id])

    def __repr__(self):
        return f"<CallInsightsAnalysis(id={self.id}, title={self.transcript_title}, created_at={self.created_at})>"
