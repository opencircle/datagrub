"""
Prompt endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.prompt import Prompt, PromptVersion
from app.models.user import User
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse, PromptVersionCreate, PromptVersionResponse
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_in: PromptCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new prompt with initial version
    """
    # Create prompt
    prompt_data = prompt_in.model_dump(exclude={"initial_version"})
    prompt = Prompt(
        **prompt_data,
        created_by=current_user.id,
    )

    db.add(prompt)
    await db.flush()

    # Create initial version
    version = PromptVersion(
        **prompt_in.initial_version.model_dump(),
        prompt_id=prompt.id,
        version_number=1,
    )

    db.add(version)
    await db.flush()

    # Set current version
    prompt.current_version_id = version.id

    await db.commit()
    await db.refresh(prompt)

    return prompt


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get prompt by ID

    SOC 2 Requirement: Multi-tenant isolation - only show prompts from user's organization
    """
    from app.models.project import Project

    # Join with Project to verify organization access
    result = await db.execute(
        select(Prompt)
        .join(Project, Prompt.project_id == Project.id)
        .where(Prompt.id == prompt_id)
        .where(Project.organization_id == current_user.organization_id)
        .options(selectinload(Prompt.current_version))
    )
    prompt = result.scalar_one_or_none()

    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    return prompt


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_update: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update prompt metadata
    """
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()

    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    update_data = prompt_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    await db.commit()
    await db.refresh(prompt)

    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete prompt
    """
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()

    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    await db.delete(prompt)
    await db.commit()


@router.get("", response_model=List[PromptResponse])
async def list_prompts(
    project_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List prompts scoped to user's organization

    SOC 2 Requirement: Multi-tenant isolation - only show prompts from user's organization
    """
    from app.models.project import Project

    # Join with Project to filter by organization
    query = (
        select(Prompt)
        .join(Project, Prompt.project_id == Project.id)
        .where(Project.organization_id == current_user.organization_id)
        .options(selectinload(Prompt.current_version))
    )

    if project_id:
        query = query.where(Prompt.project_id == project_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    prompts = result.scalars().all()

    return prompts


@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_version(
    prompt_id: UUID,
    version_in: PromptVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new version of a prompt
    """
    # Get prompt
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    prompt = result.scalar_one_or_none()

    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found",
        )

    # Get latest version number
    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
    )
    latest_version = result.first()
    new_version_number = (latest_version[0].version_number + 1) if latest_version else 1

    # Create new version
    version = PromptVersion(
        **version_in.model_dump(),
        prompt_id=prompt_id,
        version_number=new_version_number,
    )

    db.add(version)
    await db.flush()

    # Update current version
    prompt.current_version_id = version.id

    await db.commit()
    await db.refresh(version)

    return version


@router.get("/{prompt_id}/versions", response_model=List[PromptVersionResponse])
async def list_prompt_versions(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all versions of a prompt
    """
    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
    )
    versions = result.scalars().all()

    return versions
