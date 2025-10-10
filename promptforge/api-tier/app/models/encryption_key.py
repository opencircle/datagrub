"""
Encryption Key Model

Stores encryption keys in the database for multi-stage support.
Each environment (dev, staging, prod) can have its own encryption key.
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class EncryptionKey(BaseModel):
    """
    Encryption key for provider API key encryption

    Supports multiple environments/stages with separate keys
    """
    __tablename__ = "encryption_keys"

    environment = Column(String(50), nullable=False, unique=True, index=True)
    # e.g., 'development', 'staging', 'production'

    key_value = Column(Text, nullable=False)
    # Base64-encoded Fernet key (44 characters)

    description = Column(Text)

    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_by = Column(UUID(as_uuid=True))
    rotated_at = Column(String)  # Track key rotation
