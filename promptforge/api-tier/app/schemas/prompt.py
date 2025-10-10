"""
Prompt and PromptVersion schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class PromptVersionBase(BaseModel):
    """Base prompt version schema"""

    template: str = Field(..., min_length=1)
    system_message: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    model_config_data: Optional[Dict[str, Any]] = Field(None, alias="model_config")
    tags: Optional[List[str]] = None


class PromptVersionCreate(PromptVersionBase):
    """Prompt version creation schema"""

    pass


class PromptVersionResponse(PromptVersionBase):
    """Prompt version response schema"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    version_number: int
    prompt_id: UUID
    avg_latency_ms: Optional[float] = None
    avg_cost: Optional[float] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


class PromptBase(BaseModel):
    """Base prompt schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="draft", pattern="^(draft|active|archived)$")


class PromptCreate(PromptBase):
    """Prompt creation schema"""

    project_id: UUID
    initial_version: PromptVersionCreate


class PromptUpdate(BaseModel):
    """Prompt update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|active|archived)$")


class PromptResponse(PromptBase):
    """Prompt response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    created_by: UUID
    current_version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    current_version: Optional[PromptVersionResponse] = None
