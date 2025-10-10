"""
Policy and PolicyViolation models
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class PolicySeverity(str, enum.Enum):
    """Policy severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyAction(str, enum.Enum):
    """Actions to take when policy is violated"""

    LOG = "log"
    WARN = "warn"
    BLOCK = "block"
    ALERT = "alert"


class Policy(BaseModel):
    """Policy model - defines governance rules"""

    __tablename__ = "policies"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    policy_type = Column(String(100), nullable=False)  # toxicity, pii, cost, latency, custom

    # Configuration
    rules = Column(JSON, nullable=False)  # Policy rules definition
    threshold = Column(JSON)  # Threshold values for detection
    severity = Column(SQLEnum(PolicySeverity), default=PolicySeverity.MEDIUM, nullable=False)
    action = Column(SQLEnum(PolicyAction), default=PolicyAction.WARN, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_enforced = Column(Boolean, default=False, nullable=False)

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="policies")
    violations = relationship("PolicyViolation", back_populates="policy", cascade="all, delete-orphan")


class PolicyViolation(BaseModel):
    """PolicyViolation model - records when a policy is violated"""

    __tablename__ = "policy_violations"

    violation_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(PolicySeverity), nullable=False)

    # Violation details
    detected_value = Column(JSON)  # What was detected
    threshold_value = Column(JSON)  # What the threshold was
    confidence_score = Column(Integer)  # 0-100

    # Context
    message = Column(Text)
    violation_metadata = Column(JSON)

    # Resolution
    status = Column(String(50), default="open")  # open, acknowledged, resolved, false_positive
    resolution_notes = Column(Text)
    resolved_at = Column(String(50))  # ISO timestamp
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Foreign Keys
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False)
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"))

    # Relationships
    policy = relationship("Policy", back_populates="violations")
    trace = relationship("Trace", back_populates="policy_violations")
    resolved_by_user = relationship("User")
