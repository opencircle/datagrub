"""
Pydantic schemas for Model Provider Configuration API
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import re


class ModelProviderConfigBase(BaseModel):
    """Base schema for model provider configuration"""
    provider_name: str = Field(..., min_length=1, max_length=100, description="Provider identifier (e.g., 'openai', 'anthropic')")
    provider_type: str = Field(..., description="Provider type: llm, embedding, image, audio, multimodal")
    display_name: Optional[str] = Field(None, max_length=255, description="User-friendly display name")
    project_id: Optional[UUID] = Field(None, description="Project ID (null for organization-level)")
    is_active: bool = Field(True, description="Whether this configuration is active")
    is_default: bool = Field(False, description="Whether this is the default provider for this type")

    @field_validator('provider_type')
    @classmethod
    def validate_provider_type(cls, v):
        valid_types = {'llm', 'embedding', 'image', 'audio', 'multimodal'}
        if v not in valid_types:
            raise ValueError(f"provider_type must be one of: {', '.join(valid_types)}")
        return v


class ModelProviderConfigCreate(ModelProviderConfigBase):
    """Schema for creating a new model provider configuration"""
    api_key: str = Field(..., min_length=8, description="API key (will be encrypted)")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional configuration (will be encrypted)")

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or v.isspace():
            raise ValueError("API key cannot be empty or whitespace")
        return v


class ModelProviderConfigUpdate(BaseModel):
    """Schema for updating a model provider configuration"""
    display_name: Optional[str] = Field(None, max_length=255)
    api_key: Optional[str] = Field(None, min_length=8, description="New API key for rotation")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration to merge/replace")
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if v is not None and (not v or v.isspace()):
            raise ValueError("API key cannot be empty or whitespace")
        return v


class ModelProviderConfigResponse(ModelProviderConfigBase):
    """Schema for model provider configuration responses"""
    id: UUID
    organization_id: UUID
    api_key_masked: str = Field(..., description="Masked API key (e.g., 'sk-proj-...xyz')")
    config: Dict[str, Any] = Field(default_factory=dict, description="Decrypted configuration")
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "project_id": None,
                "provider_name": "openai",
                "provider_type": "llm",
                "display_name": "Oiiro OpenAI Production",
                "api_key_masked": "sk-proj-...xyz",
                "config": {
                    "organization_id": "org-oiiro",
                    "default_model": "gpt-4-turbo",
                    "max_tokens": 4096
                },
                "is_active": True,
                "is_default": True,
                "last_used_at": "2025-10-05T12:30:00Z",
                "usage_count": 142,
                "created_at": "2025-10-05T10:00:00Z",
                "updated_at": "2025-10-05T12:00:00Z"
            }
        }
    }


class ProviderFieldSchema(BaseModel):
    """Schema for provider configuration field metadata"""
    name: str
    type: str = Field(..., description="Field type: string, password, url, select, number, boolean")
    label: str
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    required: bool = False
    validation: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None  # For select fields
    default: Optional[Any] = None


class ProviderMetadataResponse(BaseModel):
    """Schema for provider metadata (catalog)"""
    provider_name: str
    provider_type: str
    display_name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    documentation_url: Optional[str] = None
    required_fields: List[ProviderFieldSchema] = Field(default_factory=list)
    optional_fields: List[ProviderFieldSchema] = Field(default_factory=list)
    capabilities: Dict[str, bool] = Field(default_factory=dict)
    supported_models: List[str] = Field(default_factory=list)
    api_key_pattern: Optional[str] = None
    api_key_prefix: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "provider_name": "openai",
                "provider_type": "llm",
                "display_name": "OpenAI",
                "description": "OpenAI GPT models for text generation",
                "icon_url": "https://cdn.promptforge.com/icons/openai.svg",
                "documentation_url": "https://platform.openai.com/docs",
                "required_fields": [
                    {
                        "name": "api_key",
                        "type": "password",
                        "label": "API Key",
                        "placeholder": "sk-proj-...",
                        "required": True,
                        "validation": {
                            "pattern": "^sk-[A-Za-z0-9]{32,}$"
                        }
                    }
                ],
                "optional_fields": [
                    {
                        "name": "organization_id",
                        "type": "string",
                        "label": "Organization ID",
                        "placeholder": "org-..."
                    }
                ],
                "capabilities": {
                    "streaming": True,
                    "function_calling": True,
                    "vision": True,
                    "json_mode": True
                },
                "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "api_key_pattern": "^sk-[A-Za-z0-9]{32,}$",
                "api_key_prefix": "sk-"
            }
        }
    }


class ProviderTestRequest(BaseModel):
    """Schema for testing a provider configuration"""
    test_model: Optional[str] = Field(None, description="Specific model to test (uses default if not provided)")


class ProviderTestResponse(BaseModel):
    """Schema for provider test results"""
    success: bool
    provider: str
    test_result: Dict[str, Any]
    error: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "provider": "openai",
                "test_result": {
                    "connection": "successful",
                    "models_available": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "latency_ms": 245,
                    "organization": "org-oiiro"
                }
            }
        }
    }


class ModelProviderConfigListResponse(BaseModel):
    """Schema for listing multiple configurations"""
    configs: List[ModelProviderConfigResponse]
    total: int = Field(..., description="Total number of configurations")


class ProviderMetadataListResponse(BaseModel):
    """Schema for listing provider metadata"""
    providers: List[ProviderMetadataResponse]
    total: int = Field(..., description="Total number of providers")
