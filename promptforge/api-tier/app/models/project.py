"""
Project model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Project(BaseModel):
    """Project model"""

    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active", nullable=False)  # active, archived, draft

    # Foreign Keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    created_by_user = relationship("User", back_populates="created_projects")
    prompts = relationship("Prompt", back_populates="project", cascade="all, delete-orphan")
    traces = relationship("Trace", back_populates="project", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="project", cascade="all, delete-orphan")
    model_provider_configs = relationship("ModelProviderConfig", back_populates="project", cascade="all, delete-orphan")
    call_insights_analyses = relationship("CallInsightsAnalysis", back_populates="project", cascade="all, delete-orphan")
