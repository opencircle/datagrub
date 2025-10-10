"""
Evaluation and EvaluationResult models
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Evaluation(BaseModel):
    """Evaluation model - represents an evaluation run"""

    __tablename__ = "evaluations"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    evaluation_type = Column(String(50), nullable=False)  # accuracy, toxicity, bias, custom
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed

    # Configuration
    config = Column(JSON)  # Evaluation parameters and criteria
    dataset_id = Column(String(255))  # Reference to evaluation dataset

    # Results summary
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    avg_score = Column(Float)

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="evaluations")
    prompt = relationship("Prompt", back_populates="evaluations")
    created_by_user = relationship("User", back_populates="created_evaluations")
    results = relationship("EvaluationResult", back_populates="evaluation", cascade="all, delete-orphan")


class EvaluationResult(BaseModel):
    """EvaluationResult model - individual test result within an evaluation"""

    __tablename__ = "evaluation_results"

    test_name = Column(String(255), nullable=False)
    input_data = Column(JSON, nullable=False)  # Input parameters for the test
    expected_output = Column(Text)
    actual_output = Column(Text)

    # Scoring
    score = Column(Float)  # 0.0 - 1.0
    passed = Column(Boolean, default=False)

    # Metrics
    latency_ms = Column(Float)
    token_count = Column(Integer)
    cost = Column(Float)

    # Additional details
    metrics = Column(JSON)  # Additional evaluation metrics
    error_message = Column(Text)

    # Foreign Keys
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id"), nullable=False)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="results")
