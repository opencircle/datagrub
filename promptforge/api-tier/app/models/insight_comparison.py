"""
Insight Comparison Model - Stores blind comparison results between two insight analyses
"""
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class InsightComparison(Base):
    """
    Insight Comparison - Blind evaluation of two insight analyses using a judge model

    Enables organizations to compare AI model outputs (e.g., GPT-4o vs GPT-4o-mini)
    to make data-driven decisions about model selection and cost optimization.

    Key Features:
    - Blind evaluation (judge doesn't know which model is which)
    - Per-stage comparison (Stage 1 Facts, Stage 2 Insights, Stage 3 Summary)
    - Overall winner determination with cost-benefit analysis
    - Judge model traceability
    """
    __tablename__ = "insight_comparisons"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization & User (RBAC)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Analyses Being Compared
    analysis_a_id = Column(
        UUID(as_uuid=True),
        ForeignKey("call_insights_analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    analysis_b_id = Column(
        UUID(as_uuid=True),
        ForeignKey("call_insights_analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Judge Configuration
    judge_model = Column(String(100), nullable=False, default="claude-sonnet-4-5-20250929")  # Exact API version
    judge_model_version = Column(String(200), nullable=True)  # Exact API version (kept for historical compatibility)
    evaluation_criteria = Column(JSONB, nullable=False)  # ["groundedness", "clarity", etc.]

    # Overall Results
    overall_winner = Column(String(1), nullable=True)  # 'A', 'B', or 'tie'
    overall_reasoning = Column(Text, nullable=False)

    # Stage 1: Fact Extraction
    stage1_winner = Column(String(1), nullable=True)  # 'A', 'B', or 'tie'
    stage1_scores = Column(JSONB, nullable=True)  # {"A": {...}, "B": {...}}
    stage1_reasoning = Column(Text, nullable=True)

    # Stage 2: Reasoning & Insights
    stage2_winner = Column(String(1), nullable=True)
    stage2_scores = Column(JSONB, nullable=True)
    stage2_reasoning = Column(Text, nullable=True)

    # Stage 3: Summary Synthesis
    stage3_winner = Column(String(1), nullable=True)
    stage3_scores = Column(JSONB, nullable=True)
    stage3_reasoning = Column(Text, nullable=True)

    # Judge Trace (links to traces table for judge model invocation)
    judge_trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=True)

    # Metadata (judge tokens, cost, duration, etc.)
    comparison_metadata = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        # Winner values must be 'A', 'B', or 'tie'
        CheckConstraint(
            "overall_winner IN ('A', 'B', 'tie')",
            name="ck_overall_winner_valid"
        ),
        CheckConstraint(
            "stage1_winner IN ('A', 'B', 'tie')",
            name="ck_stage1_winner_valid"
        ),
        CheckConstraint(
            "stage2_winner IN ('A', 'B', 'tie')",
            name="ck_stage2_winner_valid"
        ),
        CheckConstraint(
            "stage3_winner IN ('A', 'B', 'tie')",
            name="ck_stage3_winner_valid"
        ),
        # Prevent duplicate comparisons (same analyses + judge + criteria = one comparison)
        UniqueConstraint(
            'analysis_a_id',
            'analysis_b_id',
            'judge_model',
            # Note: JSONB can't be in unique constraint, so we'll handle criteria deduplication in service layer
            name='uq_comparison'
        ),
    )

    # Relationships
    organization = relationship("Organization", back_populates="insight_comparisons")
    user = relationship("User", back_populates="insight_comparisons")
    analysis_a = relationship(
        "CallInsightsAnalysis",
        foreign_keys=[analysis_a_id],
        backref="comparisons_as_a"
    )
    analysis_b = relationship(
        "CallInsightsAnalysis",
        foreign_keys=[analysis_b_id],
        backref="comparisons_as_b"
    )
    judge_trace = relationship("Trace", foreign_keys=[judge_trace_id])

    def __repr__(self):
        return (
            f"<InsightComparison(id={self.id}, "
            f"winner={self.overall_winner}, "
            f"judge={self.judge_model}, "
            f"created_at={self.created_at})>"
        )

    def to_dict(self):
        """Convert comparison to dictionary for API responses"""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "user_id": str(self.user_id),
            "analysis_a_id": str(self.analysis_a_id),
            "analysis_b_id": str(self.analysis_b_id),
            "judge_model": self.judge_model,
            "evaluation_criteria": self.evaluation_criteria,
            "overall_winner": self.overall_winner,
            "overall_reasoning": self.overall_reasoning,
            "stage1_winner": self.stage1_winner,
            "stage1_scores": self.stage1_scores,
            "stage1_reasoning": self.stage1_reasoning,
            "stage2_winner": self.stage2_winner,
            "stage2_scores": self.stage2_scores,
            "stage2_reasoning": self.stage2_reasoning,
            "stage3_winner": self.stage3_winner,
            "stage3_scores": self.stage3_scores,
            "stage3_reasoning": self.stage3_reasoning,
            "judge_trace_id": str(self.judge_trace_id) if self.judge_trace_id else None,
            "comparison_metadata": self.comparison_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
