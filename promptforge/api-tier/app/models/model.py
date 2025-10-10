"""
AIModel and ModelProvider models
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class ModelProviderType(str, enum.Enum):
    """Supported model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class ModelProvider(BaseModel):
    """ModelProvider model - represents an AI model provider"""

    __tablename__ = "model_providers"

    name = Column(String(100), nullable=False, unique=True)
    provider_type = Column(SQLEnum(ModelProviderType), nullable=False)
    description = Column(Text)

    # Configuration
    api_base_url = Column(String(255))
    api_key_encrypted = Column(Text)  # Encrypted API key
    config = Column(JSON)  # Additional provider-specific config

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Relationships
    models = relationship("AIModel", back_populates="provider")


class AIModel(BaseModel):
    """AIModel model - represents a specific AI model"""

    __tablename__ = "ai_models"

    name = Column(String(100), nullable=False)
    model_id = Column(String(255), nullable=False)  # Provider's model identifier
    description = Column(Text)

    # Capabilities
    supports_streaming = Column(Boolean, default=False)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    max_context_length = Column(Integer)

    # Pricing (per 1M tokens)
    input_cost_per_million = Column(Float)
    output_cost_per_million = Column(Float)

    # Default parameters
    default_temperature = Column(Float, default=0.7)
    default_max_tokens = Column(Integer, default=1000)
    default_config = Column(JSON)  # Other default parameters

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)

    # Foreign Keys
    provider_id = Column(UUID(as_uuid=True), ForeignKey("model_providers.id"), nullable=False)

    # Relationships
    provider = relationship("ModelProvider", back_populates="models")
    traces = relationship("Trace", back_populates="model")
