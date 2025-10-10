"""
AI Model and Provider endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.model import AIModel, ModelProvider
from app.models.model_provider import ModelProviderMetadata, ModelProviderConfig
from app.models.user import User
from app.schemas.model import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    ModelProviderCreate,
    ModelProviderUpdate,
    ModelProviderResponse,
)
from app.api.dependencies import get_current_active_user

router = APIRouter()


# Schema for available models (organization-scoped)
class AvailableModelResponse(BaseModel):
    """Available model for organization"""
    model_id: str = Field(..., description="Model identifier (e.g., 'gpt-4o-mini')")
    display_name: str = Field(..., description="Human-readable model name")
    provider: str = Field(..., description="Model provider (e.g., 'OpenAI')")
    description: Optional[str] = Field(None, description="Model description")
    input_cost: float = Field(..., description="Cost per 1K input tokens")
    output_cost: float = Field(..., description="Cost per 1K output tokens")
    context_window: Optional[int] = Field(None, description="Maximum context window size")


@router.get("/available", response_model=List[AvailableModelResponse])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of available models for the current user's organization

    Only returns models from providers that the organization has configured
    API keys for. This ensures users only see models they can actually use.

    This endpoint is used by:
    - Playground model selection
    - Insights multi-stage model selection
    - Custom evaluation model selection

    Response includes:
    - Model identifiers
    - Display names
    - Cost information (from database metadata)
    - Context window sizes
    """
    # First, get the list of configured providers for this organization
    configured_providers_result = await db.execute(
        select(ModelProviderConfig.provider_name).where(
            and_(
                ModelProviderConfig.organization_id == current_user.organization_id,
                ModelProviderConfig.is_active == True
            )
        ).distinct()
    )
    configured_provider_names = {row[0] for row in configured_providers_result.all()}

    # If no providers configured, return empty list
    if not configured_provider_names:
        return []

    # Query ModelProviderMetadata for active LLM providers that are configured
    result = await db.execute(
        select(ModelProviderMetadata).where(
            and_(
                ModelProviderMetadata.provider_type == "llm",
                ModelProviderMetadata.is_active == True,
                ModelProviderMetadata.provider_name.in_(configured_provider_names)
            )
        )
    )
    providers = result.scalars().all()

    available_models = []

    for provider in providers:
        # Extract model options from optional_fields
        if not provider.optional_fields:
            continue

        # Find the default_model field which contains model options
        for field in provider.optional_fields:
            if field.get("name") == "default_model":
                model_options = field.get("options", [])
                pricing = field.get("pricing", {})
                context_windows = field.get("context_windows", {})

                # Create AvailableModelResponse for each model option
                for model_id in model_options:
                    model_pricing = pricing.get(model_id, {})

                    available_models.append(
                        AvailableModelResponse(
                            model_id=model_id,
                            display_name=field.get("model_display_names", {}).get(model_id, model_id),
                            provider=provider.display_name,
                            description=model_pricing.get("description", ""),
                            input_cost=model_pricing.get("input", 0.01),
                            output_cost=model_pricing.get("output", 0.03),
                            context_window=context_windows.get(model_id, 128000),
                        )
                    )

    return available_models


# Model Provider endpoints
@router.post("/providers", response_model=ModelProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_in: ModelProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new model provider
    """
    # Check if name already exists
    result = await db.execute(select(ModelProvider).where(ModelProvider.name == provider_in.name))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider name already exists",
        )

    provider_data = provider_in.model_dump(exclude={"api_key"})

    # TODO: Encrypt api_key before storing
    if provider_in.api_key:
        provider_data["api_key_encrypted"] = provider_in.api_key  # Should be encrypted

    provider = ModelProvider(**provider_data)

    db.add(provider)
    await db.commit()
    await db.refresh(provider)

    return provider


@router.get("/providers/{provider_id}", response_model=ModelProviderResponse)
async def get_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get model provider by ID
    """
    result = await db.execute(select(ModelProvider).where(ModelProvider.id == provider_id))
    provider = result.scalar_one_or_none()

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return provider


@router.get("/providers", response_model=List[ModelProviderResponse])
async def list_providers(
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List model providers
    """
    query = select(ModelProvider)

    if is_active is not None:
        query = query.where(ModelProvider.is_active == is_active)

    result = await db.execute(query)
    providers = result.scalars().all()

    return providers


# AI Model endpoints
@router.post("", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_in: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new AI model
    """
    model = AIModel(**model_in.model_dump())

    db.add(model)
    await db.commit()
    await db.refresh(model)

    return model


@router.get("/{model_id}", response_model=AIModelResponse)
async def get_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get AI model by ID
    """
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    return model


@router.patch("/{model_id}", response_model=AIModelResponse)
async def update_model(
    model_id: UUID,
    model_update: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update AI model
    """
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    update_data = model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)

    await db.commit()
    await db.refresh(model)

    return model


@router.get("", response_model=List[AIModelResponse])
async def list_models(
    provider_id: UUID = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List AI models
    """
    query = select(AIModel)

    if provider_id:
        query = query.where(AIModel.provider_id == provider_id)

    if is_active is not None:
        query = query.where(AIModel.is_active == is_active)

    result = await db.execute(query)
    models = result.scalars().all()

    return models
