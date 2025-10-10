"""
Policy endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.policy import Policy, PolicyViolation
from app.models.user import User
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse, PolicyViolationResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new policy
    """
    policy = Policy(**policy_in.model_dump())

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    return policy


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get policy by ID
    """
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    return policy


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: UUID,
    policy_update: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update policy
    """
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    update_data = policy_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    await db.commit()
    await db.refresh(policy)

    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete policy
    """
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    await db.delete(policy)
    await db.commit()


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    project_id: UUID = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List policies
    """
    query = select(Policy)

    if project_id:
        query = query.where(Policy.project_id == project_id)

    if is_active is not None:
        query = query.where(Policy.is_active == is_active)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    policies = result.scalars().all()

    return policies


@router.get("/{policy_id}/violations", response_model=List[PolicyViolationResponse])
async def list_policy_violations(
    policy_id: UUID,
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List violations for a specific policy
    """
    query = select(PolicyViolation).where(PolicyViolation.policy_id == policy_id)

    if status_filter:
        query = query.where(PolicyViolation.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(PolicyViolation.created_at.desc())
    result = await db.execute(query)
    violations = result.scalars().all()

    return violations
