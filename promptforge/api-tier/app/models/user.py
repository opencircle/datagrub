"""
User and Organization models
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Organization(BaseModel):
    """Organization model"""

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000))

    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    model_provider_configs = relationship("ModelProviderConfig", back_populates="organization")
    call_insights_analyses = relationship("CallInsightsAnalysis", back_populates="organization")
    insight_comparisons = relationship("InsightComparison", back_populates="organization")


class User(BaseModel):
    """User model"""

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.DEVELOPER, nullable=False)

    # Foreign Keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_projects = relationship("Project", back_populates="created_by_user")
    created_prompts = relationship("Prompt", back_populates="created_by_user")
    call_insights_analyses = relationship("CallInsightsAnalysis", back_populates="user")
    insight_comparisons = relationship("InsightComparison", back_populates="user")
