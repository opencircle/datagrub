"""
Model Provider Configuration Models

Stores encrypted API keys and configuration for model providers (OpenAI, Anthropic, etc.)
with organization and project-level scoping.
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ModelProviderConfig(Base):
    """
    Model provider API key and configuration storage

    Stores encrypted API keys and configuration for model providers at organization
    or project level. Supports multi-tenancy with RBAC.
    """

    __tablename__ = "model_provider_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Provider identification
    provider_name = Column(String(100), nullable=False)  # openai, anthropic, cohere, etc.
    provider_type = Column(String(50), nullable=False)   # llm, embedding, image, etc.
    display_name = Column(String(255))                    # User-friendly name

    # Encrypted credentials
    api_key_encrypted = Column(Text, nullable=False)      # Fernet encrypted API key
    api_key_hash = Column(String(128), nullable=False)    # SHA-256 hash for validation

    # Additional configuration (encrypted JSON)
    config_encrypted = Column(Text)                       # Encrypted JSON config

    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)           # Default provider for this type

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="model_provider_configs")
    project = relationship("Project", back_populates="model_provider_configs")
    creator = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            'organization_id',
            'project_id',
            'provider_name',
            'provider_type',
            name='uq_org_project_provider'
        ),
        CheckConstraint(
            "provider_type IN ('llm', 'embedding', 'image', 'audio', 'multimodal')",
            name='ck_provider_type'
        ),
        CheckConstraint(
            "provider_name != ''",
            name='ck_provider_name_not_empty'
        ),
    )

    def __repr__(self):
        return f"<ModelProviderConfig(id={self.id}, provider={self.provider_name}, org={self.organization_id})>"


class ModelProviderMetadata(Base):
    """
    Static metadata about supported model providers

    Read-only reference data seeded during deployment. Describes provider
    capabilities, required configuration fields, and validation rules.
    """

    __tablename__ = "model_provider_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Provider identification
    provider_name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Visual elements
    icon_url = Column(String(500))
    documentation_url = Column(String(500))

    # Configuration schema (JSONB for flexible querying)
    required_fields = Column(JSONB)  # [{name, type, label, placeholder, validation}, ...]
    optional_fields = Column(JSONB)
    default_config = Column(JSONB)

    # Capabilities
    capabilities = Column(JSONB)     # {streaming: true, functions: true, vision: false, ...}
    supported_models = Column(JSONB) # ["gpt-4", "gpt-3.5-turbo", ...]

    # Validation
    api_key_pattern = Column(String(255))  # Regex for API key format
    api_key_prefix = Column(String(20))    # e.g., "sk-" for OpenAI

    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ModelProviderMetadata(provider={self.provider_name}, type={self.provider_type})>"
