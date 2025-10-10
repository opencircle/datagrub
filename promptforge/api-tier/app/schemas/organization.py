"""
Organization schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""

    pass


class OrganizationUpdate(BaseModel):
    """Organization update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
