"""
AIModel and ModelProvider schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.model import ModelProviderType


class ModelProviderBase(BaseModel):
    """Base model provider schema"""

    name: str = Field(..., min_length=1, max_length=100)
    provider_type: ModelProviderType
    description: Optional[str] = None
    api_base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_default: bool = False


class ModelProviderCreate(ModelProviderBase):
    """Model provider creation schema"""

    api_key: Optional[str] = None  # Will be encrypted before storage


class ModelProviderUpdate(BaseModel):
    """Model provider update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ModelProviderResponse(BaseModel):
    """Model provider response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    provider_type: ModelProviderType
    description: Optional[str] = None
    api_base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class AIModelBase(BaseModel):
    """Base AI model schema"""

    name: str = Field(..., min_length=1, max_length=100)
    model_id: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    max_context_length: Optional[int] = None
    input_cost_per_million: Optional[float] = None
    output_cost_per_million: Optional[float] = None
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    default_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_deprecated: bool = False


class AIModelCreate(AIModelBase):
    """AI model creation schema"""

    provider_id: UUID


class AIModelUpdate(BaseModel):
    """AI model update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    supports_streaming: Optional[bool] = None
    supports_function_calling: Optional[bool] = None
    supports_vision: Optional[bool] = None
    max_context_length: Optional[int] = None
    input_cost_per_million: Optional[float] = None
    output_cost_per_million: Optional[float] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    default_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_deprecated: Optional[bool] = None


class AIModelResponse(AIModelBase):
    """AI model response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider_id: UUID
    created_at: datetime
    updated_at: datetime
