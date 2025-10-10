"""
API dependencies for authentication and authorization

SOC 2 Compliance: Validates organization_id from JWT claims for multi-tenant isolation
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from sqlalchemy import select

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token

    SOC 2 Requirement: Validates organization_id claim for stateless multi-tenant isolation
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id: str = payload.get("sub")
    org_id: str = payload.get("organization_id")  # SOC 2: Validate organization from token

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    # SOC 2 Security Control: Validate organization_id from token matches user's organization
    # This prevents token replay attacks across organizations
    if org_id and str(user.organization_id) != org_id:
        logger.error(
            f"Organization mismatch: token={org_id}, user={user.organization_id}, "
            f"user_id={user.id}, email={user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization mismatch detected",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control

    SOC 2 Requirement: RBAC enforced on all sensitive operations

    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            pass

    Args:
        required_role: Minimum role required (VIEWER < DEVELOPER < ADMIN)

    Returns:
        Dependency function that validates user role
    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        # Role hierarchy: VIEWER(0) < DEVELOPER(1) < ADMIN(2)
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.DEVELOPER: 1,
            UserRole.ADMIN: 2,
        }

        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role, 999)

        if user_role_level < required_role_level:
            logger.warning(
                f"Insufficient permissions: user={current_user.email}, "
                f"role={current_user.role.value}, required={required_role.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. {required_role.value} role required.",
            )

        return current_user

    return check_role
