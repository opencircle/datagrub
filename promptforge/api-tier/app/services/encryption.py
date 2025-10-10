"""
Encryption Service for Sensitive Data

Provides encryption/decryption for model provider API keys and sensitive configuration
using Fernet (symmetric encryption with AES-128).

The encryption key is stored in the database (encryption_keys table) for multi-stage
support (development, staging, production). Falls back to settings if DB is unavailable.
"""
from cryptography.fernet import Fernet
import base64
import hashlib
import json
from typing import Optional, Dict, Any, Tuple
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_encryption_key_from_db() -> Optional[str]:
    """
    Load encryption key from database based on current environment

    Priority:
    1. PROMPTFORGE_ENV environment variable (development, staging, production)
    2. Default to 'development'

    Returns:
        Encryption key from database, or None if not found
    """
    try:
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session

        # Get environment (default: development)
        environment = os.getenv('PROMPTFORGE_ENV', 'development')

        # Create connection to database
        engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))

        with Session(engine) as session:
            # Query encryption key
            from sqlalchemy import Table, Column, String, Text, Boolean, MetaData
            from sqlalchemy.dialects.postgresql import UUID

            metadata = MetaData()
            encryption_keys = Table(
                'encryption_keys',
                metadata,
                Column('id', UUID(as_uuid=True), primary_key=True),
                Column('environment', String(50)),
                Column('key_value', Text),
                Column('is_active', Boolean),
            )

            stmt = select(encryption_keys.c.key_value).where(
                encryption_keys.c.environment == environment,
                encryption_keys.c.is_active == True
            )

            result = session.execute(stmt).first()

            if result:
                logger.info(f"Loaded encryption key from database for environment: {environment}")
                return result[0]
            else:
                logger.warning(f"No encryption key found for environment: {environment}")
                return None

    except Exception as e:
        logger.warning(f"Failed to load encryption key from database: {e}")
        return None


class EncryptionService:
    """
    Symmetric encryption service using Fernet (AES-128)

    Features:
    - Encrypt/decrypt API keys
    - Encrypt/decrypt JSON configuration
    - Generate non-reversible hashes for validation
    - Mask sensitive values for display
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service

        Args:
            encryption_key: Base64-encoded Fernet key (32 bytes after decoding)
                           If None, tries to load from database based on PROMPTFORGE_ENV,
                           then falls back to settings.MODEL_PROVIDER_ENCRYPTION_KEY
        """
        # Priority:
        # 1. Explicitly provided key
        # 2. Database (based on PROMPTFORGE_ENV)
        # 3. Settings (backward compatibility)
        if encryption_key:
            key = encryption_key
        else:
            key = get_encryption_key_from_db() or settings.MODEL_PROVIDER_ENCRYPTION_KEY

        if not key:
            raise ValueError(
                "Encryption key not configured. Either set PROMPTFORGE_ENV and add key to database, "
                "or set MODEL_PROVIDER_ENCRYPTION_KEY in settings"
            )

        # If key is not already a valid Fernet key, derive one from it
        try:
            self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # Derive Fernet key from arbitrary string
            key_bytes = key.encode() if isinstance(key, str) else key
            hashed = hashlib.sha256(key_bytes).digest()
            fernet_key = base64.urlsafe_b64encode(hashed)
            self.fernet = Fernet(fernet_key)

        logger.info("Encryption service initialized")

    def encrypt_api_key(self, api_key: str) -> Tuple[str, str]:
        """
        Encrypt API key and generate validation hash

        Args:
            api_key: Plain text API key

        Returns:
            (encrypted_key, key_hash)
            - encrypted_key: Fernet-encrypted key (base64 string)
            - key_hash: SHA-256 hash for validation (hex string)
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        # Encrypt
        encrypted = self.fernet.encrypt(api_key.encode()).decode('utf-8')

        # Hash (non-reversible for validation)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return encrypted, key_hash

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key

        Args:
            encrypted_key: Fernet-encrypted key (base64 string)

        Returns:
            Plain text API key

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        if not encrypted_key:
            raise ValueError("Encrypted key cannot be empty")

        decrypted = self.fernet.decrypt(encrypted_key.encode()).decode('utf-8')
        return decrypted

    def encrypt_config(self, config: Dict[str, Any]) -> str:
        """
        Encrypt JSON configuration

        Args:
            config: Configuration dictionary

        Returns:
            Encrypted configuration (base64 string)
        """
        if not config:
            return ""

        # Serialize to JSON
        config_json = json.dumps(config, sort_keys=True)

        # Encrypt
        encrypted = self.fernet.encrypt(config_json.encode()).decode('utf-8')

        return encrypted

    def decrypt_config(self, encrypted_config: str) -> Dict[str, Any]:
        """
        Decrypt JSON configuration

        Args:
            encrypted_config: Encrypted configuration (base64 string)

        Returns:
            Configuration dictionary
        """
        if not encrypted_config:
            return {}

        # Decrypt
        decrypted = self.fernet.decrypt(encrypted_config.encode()).decode('utf-8')

        # Parse JSON
        config = json.loads(decrypted)

        return config

    def mask_api_key(self, api_key: str, show_chars: int = 3) -> str:
        """
        Mask API key for display

        Args:
            api_key: Plain text API key
            show_chars: Number of characters to show at start and end

        Returns:
            Masked API key (e.g., "sk-proj-...xyz")

        Examples:
            >>> mask_api_key("sk-proj-abc123xyz789", show_chars=3)
            "sk-proj-...789"

            >>> mask_api_key("sk-ant-api03-abc123", show_chars=3)
            "sk-ant-api03-...123"
        """
        if not api_key:
            return ""

        if len(api_key) <= show_chars * 2:
            return "*" * len(api_key)

        # Find prefix (include up to last dash if exists)
        if '-' in api_key:
            # Find the last dash position in first half
            prefix_end = api_key.rfind('-', 0, len(api_key) // 2)
            if prefix_end > 0:
                prefix = api_key[:prefix_end + 1]
            else:
                prefix = api_key[:show_chars]
        else:
            prefix = api_key[:show_chars]

        # Suffix
        suffix = api_key[-show_chars:]

        return f"{prefix}...{suffix}"

    def validate_api_key_hash(self, api_key: str, stored_hash: str) -> bool:
        """
        Validate API key against stored hash

        Args:
            api_key: Plain text API key
            stored_hash: SHA-256 hash from database

        Returns:
            True if hash matches
        """
        if not api_key or not stored_hash:
            return False

        computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return computed_hash == stored_hash

    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generate a new Fernet encryption key

        Returns:
            Base64-encoded Fernet key (44 characters)

        Example:
            >>> key = EncryptionService.generate_encryption_key()
            >>> print(key)
            'xN8vF2...=' # 44 characters
        """
        return Fernet.generate_key().decode('utf-8')


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get global encryption service instance (singleton)

    Returns:
        EncryptionService instance
    """
    global _encryption_service

    if _encryption_service is None:
        _encryption_service = EncryptionService()

    return _encryption_service
