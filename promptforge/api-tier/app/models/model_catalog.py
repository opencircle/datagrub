"""
Model Catalog - Maps user-friendly model names to exact API versions

This table provides a single source of truth for model version management:
- UI uses friendly names (e.g., "claude-sonnet-4.5", "gpt-4o")
- API uses exact versions (e.g., "claude-sonnet-4-5-20250929", "gpt-4o-2024-08-06")
- Allows updating model versions without changing application code
"""

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.core.database import Base


class ModelCatalog(Base):
    """
    Catalog of available AI models with version mapping

    Maps user-friendly model names to exact API model identifiers.
    Enables version management and model lifecycle tracking.
    """

    __tablename__ = "model_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Model identification
    model_name = Column(String(100), unique=True, nullable=False, index=True)  # Friendly name (UI)
    model_version = Column(String(200), nullable=False)  # Exact API identifier

    # Provider
    provider_name = Column(String(100), nullable=False, index=True)  # openai, anthropic, google
    model_family = Column(String(100), nullable=False)  # gpt-4, claude-3, claude-4, gemini

    # Display information
    display_name = Column(String(255), nullable=False)  # "Claude Sonnet 4.5"
    description = Column(Text)

    # Capabilities and metadata
    context_window = Column(JSON)  # {"input": 200000, "output": 8192}
    capabilities = Column(JSON)  # ["text", "vision", "function_calling", "json_mode"]

    # Pricing (per 1M tokens)
    pricing = Column(JSON)  # {"input": 3.0, "output": 15.0, "currency": "USD"}

    # Status and lifecycle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deprecated = Column(Boolean, default=False, nullable=False)
    is_recommended = Column(Boolean, default=False, nullable=False)  # Highlight in UI

    # Release information
    release_date = Column(DateTime)
    deprecation_date = Column(DateTime, nullable=True)

    # Metadata
    notes = Column(Text)  # Internal notes about the model
    documentation_url = Column(String(500))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("model_name != ''", name='ck_model_name_not_empty'),
        CheckConstraint("model_version != ''", name='ck_model_version_not_empty'),
        CheckConstraint("provider_name IN ('openai', 'anthropic', 'google', 'cohere', 'mistral')", name='ck_provider_name'),
    )

    def __repr__(self):
        return f"<ModelCatalog(name={self.model_name}, version={self.model_version}, provider={self.provider_name})>"
