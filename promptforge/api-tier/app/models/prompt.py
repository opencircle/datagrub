"""
Prompt and PromptVersion models
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Prompt(BaseModel):
    """Prompt model - represents a prompt template"""

    __tablename__ = "prompts"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # chatbot, completion, classification, etc.
    status = Column(String(50), default="draft", nullable=False)  # draft, active, archived

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("prompt_versions.id", use_alter=True, name='fk_prompt_current_version'))

    # Relationships
    project = relationship("Project", back_populates="prompts")
    created_by_user = relationship("User", back_populates="created_prompts")
    versions = relationship("PromptVersion", back_populates="prompt", foreign_keys="PromptVersion.prompt_id", cascade="all, delete-orphan")
    current_version = relationship("PromptVersion", foreign_keys=[current_version_id], post_update=True)


class PromptVersion(BaseModel):
    """PromptVersion model - represents a version of a prompt"""

    __tablename__ = "prompt_versions"

    version_number = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    system_message = Column(Text)
    variables = Column(JSON)  # JSON schema for variables
    model_config = Column(JSON)  # temperature, max_tokens, etc.
    tags = Column(JSON)  # Array of tags

    # Performance metrics
    avg_latency_ms = Column(Float)
    avg_cost = Column(Float)
    usage_count = Column(Integer, default=0)

    # Foreign Keys
    prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=False)

    # Relationships
    prompt = relationship("Prompt", back_populates="versions", foreign_keys=[prompt_id])
    traces = relationship("Trace", back_populates="prompt_version")
