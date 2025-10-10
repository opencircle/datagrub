"""
Models API Endpoints

Provides aggregated view of available models across all configured providers.
Shows which models are available, their usage statistics, and performance metrics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.model_provider import ModelProviderConfig, ModelProviderMetadata
from app.models.trace import Trace
from app.models.project import Project
from app.api.dependencies import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

router = APIRouter()


# Schemas for /available endpoint
class AvailableModelResponse(BaseModel):
    """Available model for organization (used by dropdowns)"""
    model_id: str = Field(..., description="Model identifier (e.g., 'gpt-4o-mini')")
    display_name: str = Field(..., description="Human-readable model name")
    provider: str = Field(..., description="Model provider (e.g., 'OpenAI')")
    description: Optional[str] = Field(None, description="Model description")
    input_cost: float = Field(..., description="Cost per 1K input tokens")
    output_cost: float = Field(..., description="Cost per 1K output tokens")
    context_window: Optional[int] = Field(None, description="Maximum context window size")


class ModelInfo(BaseModel):
    """Information about a specific model"""
    model_id: str
    model_name: str
    provider_name: str
    provider_display_name: str
    provider_config_id: Optional[str] = None
    context_window: Optional[int] = None
    supports_functions: Optional[bool] = None
    capabilities: List[str] = []
    is_available: bool = True  # Based on having active config


class ModelUsageStats(BaseModel):
    """Usage statistics for a model"""
    model_name: str
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 0.0
    avg_latency_ms: Optional[float] = None
    total_tokens: int = 0
    total_cost: float = 0.0
    last_used: Optional[datetime] = None


class ModelAnalytics(BaseModel):
    """Analytics for models"""
    total_models_available: int
    total_requests_7d: int
    total_cost_7d: float
    avg_success_rate: float
    most_used_model: Optional[str] = None
    top_models: List[ModelUsageStats] = []


class ModelsListResponse(BaseModel):
    """Response for models list"""
    models: List[ModelInfo]
    total: int


class ModelsAnalyticsResponse(BaseModel):
    """Response for models analytics"""
    analytics: ModelAnalytics
    by_model: List[ModelUsageStats]
    total: int


@router.get("/available", response_model=List[AvailableModelResponse])
async def get_available_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    from sqlalchemy import and_

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


@router.get("/", response_model=ModelsListResponse)
async def list_models(
    provider_name: Optional[str] = Query(None, description="Filter by provider"),
    available_only: bool = Query(True, description="Show only available models"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all available models across configured providers

    Returns models from:
    1. Provider metadata (catalog of all possible models)
    2. Filtered by active provider configurations (user has API key)
    """
    # Get all provider metadata
    metadata_query = select(ModelProviderMetadata).where(
        ModelProviderMetadata.is_active == True
    )

    if provider_name:
        metadata_query = metadata_query.where(
            ModelProviderMetadata.provider_name == provider_name
        )

    metadata_result = await db.execute(metadata_query)
    all_metadata = metadata_result.scalars().all()

    # Get active provider configs for current user's org
    config_query = select(ModelProviderConfig).where(
        ModelProviderConfig.organization_id == current_user.organization_id,
        ModelProviderConfig.is_active == True
    )

    if provider_name:
        config_query = config_query.where(
            ModelProviderConfig.provider_name == provider_name
        )

    config_result = await db.execute(config_query)
    active_configs = {
        (c.provider_name, c.provider_type): c.id
        for c in config_result.scalars().all()
    }

    # Build model list
    models = []
    for metadata in all_metadata:
        # Check if this provider is configured
        is_available = (metadata.provider_name, metadata.provider_type) in active_configs
        config_id = active_configs.get((metadata.provider_name, metadata.provider_type))

        if available_only and not is_available:
            continue

        # Extract models from metadata
        supported_models = metadata.supported_models or []

        for model in supported_models:
            models.append(ModelInfo(
                model_id=model.get('model_id', ''),
                model_name=model.get('model_name', ''),
                provider_name=metadata.provider_name,
                provider_display_name=metadata.display_name,
                provider_config_id=str(config_id) if config_id else None,
                context_window=model.get('context_window'),
                supports_functions=model.get('supports_functions'),
                capabilities=metadata.capabilities or [],
                is_available=is_available
            ))

    return ModelsListResponse(
        models=models,
        total=len(models)
    )


@router.get("/analytics", response_model=ModelsAnalyticsResponse)
async def get_models_analytics(
    days: int = Query(7, ge=1, le=90, description="Number of days for analytics"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get analytics for model usage

    Aggregates data from traces to show:
    - Total requests per model
    - Success rates
    - Average latency
    - Token usage and costs
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get all traces for user's organization in date range
    # Join with Project to filter by organization
    traces_query = (
        select(Trace)
        .join(Project, Trace.project_id == Project.id)
        .where(
            Project.organization_id == current_user.organization_id,
            Trace.created_at >= start_date
        )
    )

    traces_result = await db.execute(traces_query)
    traces = traces_result.scalars().all()

    # Aggregate by model
    model_stats = {}

    for trace in traces:
        # Extract model info from trace (use denormalized fields)
        model_name = trace.model_name or 'unknown'
        provider_name = trace.provider or 'unknown'

        key = (model_name, provider_name)

        if key not in model_stats:
            model_stats[key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'latencies': [],
                'total_tokens': 0,
                'total_cost': 0.0,
                'last_used': None
            }

        stats = model_stats[key]
        stats['total_requests'] += 1

        # Success/failure
        if trace.status == 'success':
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1

        # Latency
        if trace.total_duration_ms:
            stats['latencies'].append(trace.total_duration_ms)

        # Tokens
        if trace.total_tokens:
            stats['total_tokens'] += trace.total_tokens

        # Cost
        if trace.total_cost:
            stats['total_cost'] += trace.total_cost

        # Last used
        if not stats['last_used'] or trace.created_at > stats['last_used']:
            stats['last_used'] = trace.created_at

    # Build response
    by_model = []
    total_requests = 0
    total_cost = 0.0
    success_rates = []

    for (model_name, provider_name), stats in model_stats.items():
        success_rate = (
            stats['successful_requests'] / stats['total_requests'] * 100
            if stats['total_requests'] > 0 else 0.0
        )

        avg_latency = (
            sum(stats['latencies']) / len(stats['latencies'])
            if stats['latencies'] else None
        )

        by_model.append(ModelUsageStats(
            model_name=model_name,
            provider_name=provider_name,
            total_requests=stats['total_requests'],
            successful_requests=stats['successful_requests'],
            failed_requests=stats['failed_requests'],
            success_rate=round(success_rate, 2),
            avg_latency_ms=round(avg_latency, 2) if avg_latency else None,
            total_tokens=stats['total_tokens'],
            total_cost=round(stats['total_cost'], 2),
            last_used=stats['last_used']
        ))

        total_requests += stats['total_requests']
        total_cost += stats['total_cost']
        success_rates.append(success_rate)

    # Sort by usage
    by_model.sort(key=lambda x: x.total_requests, reverse=True)

    # Calculate overall analytics
    most_used_model = by_model[0].model_name if by_model else None
    avg_success_rate = (
        sum(success_rates) / len(success_rates)
        if success_rates else 0.0
    )

    # Get total available models count
    metadata_count = await db.execute(
        select(func.count()).select_from(ModelProviderMetadata).where(
            ModelProviderMetadata.is_active == True
        )
    )
    total_models = metadata_count.scalar() or 0

    analytics = ModelAnalytics(
        total_models_available=total_models,
        total_requests_7d=total_requests,
        total_cost_7d=round(total_cost, 2),
        avg_success_rate=round(avg_success_rate, 2),
        most_used_model=most_used_model,
        top_models=by_model[:10]  # Top 10
    )

    return ModelsAnalyticsResponse(
        analytics=analytics,
        by_model=by_model,
        total=len(by_model)
    )
