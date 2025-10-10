"""
Policy and PolicyViolation schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.policy import PolicySeverity, PolicyAction


class PolicyBase(BaseModel):
    """Base policy schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    policy_type: str = Field(..., max_length=100)
    rules: Dict[str, Any]
    threshold: Optional[Dict[str, Any]] = None
    severity: PolicySeverity = PolicySeverity.MEDIUM
    action: PolicyAction = PolicyAction.WARN
    is_active: bool = True
    is_enforced: bool = False


class PolicyCreate(PolicyBase):
    """Policy creation schema"""

    project_id: UUID


class PolicyUpdate(BaseModel):
    """Policy update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    threshold: Optional[Dict[str, Any]] = None
    severity: Optional[PolicySeverity] = None
    action: Optional[PolicyAction] = None
    is_active: Optional[bool] = None
    is_enforced: Optional[bool] = None


class PolicyResponse(PolicyBase):
    """Policy response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime


class PolicyViolationResponse(BaseModel):
    """Policy violation response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    policy_id: UUID
    trace_id: Optional[UUID] = None
    violation_type: str
    severity: PolicySeverity
    detected_value: Optional[Dict[str, Any]] = None
    threshold_value: Optional[Dict[str, Any]] = None
    confidence_score: Optional[int] = None
    message: Optional[str] = None
    violation_metadata: Optional[Dict[str, Any]] = None
    status: str
    resolution_notes: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
