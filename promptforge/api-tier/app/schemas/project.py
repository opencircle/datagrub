"""
Project schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|archived|draft)$")


class ProjectCreate(ProjectBase):
    """Project creation schema"""

    organization_id: UUID


class ProjectUpdate(BaseModel):
    """Project update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|draft)$")


class ProjectResponse(ProjectBase):
    """Project response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
