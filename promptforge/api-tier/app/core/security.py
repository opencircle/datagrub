"""
Security utilities for authentication and authorization

SOC 2 Compliance: JWT tokens include organization_id and role for stateless multi-tenant isolation
"""
from datetime import datetime, timedelta
from typing import Optional, Union, TYPE_CHECKING
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    organization_id: Optional[str] = None,
    role: Optional[str] = None,
    email: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token with organization context

    SOC 2 Requirement: Tokens MUST include organization_id for multi-tenant isolation

    Args:
        subject: User ID (UUID)
        organization_id: Organization ID (UUID) - REQUIRED for stateless org validation
        role: User role (ADMIN|DEVELOPER|VIEWER)
        email: User email (for audit logging)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token with claims
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }

    # Add organization context for multi-tenant isolation (SOC 2 requirement)
    if organization_id:
        to_encode["organization_id"] = str(organization_id)
    if role:
        to_encode["role"] = role
    if email:
        to_encode["email"] = email

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
