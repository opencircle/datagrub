"""
Model Catalog Service - Lookup and manage model versions

Provides methods to:
- Resolve friendly model names to exact API versions
- List available models for UI display
- Manage model lifecycle (deprecation, recommendations)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.model_catalog import ModelCatalog


class ModelCatalogService:
    """Service for managing and looking up models from the catalog"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._cache: Dict[str, str] = {}  # Cache friendly_name -> api_version

    async def get_model_version(self, model_name: str) -> str:
        """
        Get exact API version for a user-friendly model name

        Args:
            model_name: Friendly name (e.g., "claude-sonnet-4.5", "gpt-4o")

        Returns:
            Exact API version (e.g., "claude-sonnet-4-5-20250929", "gpt-4o-2024-08-06")

        Raises:
            ValueError: If model not found or inactive
        """
        # Check cache
        if model_name in self._cache:
            return self._cache[model_name]

        # Query database
        stmt = select(ModelCatalog).where(
            ModelCatalog.model_name == model_name,
            ModelCatalog.is_active == True
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Model not found or inactive: {model_name}")

        # Cache result
        self._cache[model_name] = model.model_version
        return model.model_version

    async def get_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete model details for a friendly name

        Returns:
            Dict with model details or None if not found
        """
        stmt = select(ModelCatalog).where(ModelCatalog.model_name == model_name)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return {
            "id": str(model.id),
            "model_name": model.model_name,
            "model_version": model.model_version,
            "provider_name": model.provider_name,
            "model_family": model.model_family,
            "display_name": model.display_name,
            "description": model.description,
            "context_window": model.context_window,
            "capabilities": model.capabilities,
            "pricing": model.pricing,
            "is_active": model.is_active,
            "is_deprecated": model.is_deprecated,
            "is_recommended": model.is_recommended,
            "release_date": model.release_date.isoformat() if model.release_date else None,
            "documentation_url": model.documentation_url,
        }

    async def list_active_models(
        self,
        provider_name: Optional[str] = None,
        model_family: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all active models, optionally filtered by provider or family

        Args:
            provider_name: Filter by provider (openai, anthropic, etc.)
            model_family: Filter by family (gpt-4, claude-4, etc.)

        Returns:
            List of model details sorted by recommendation and release date
        """
        stmt = select(ModelCatalog).where(ModelCatalog.is_active == True)

        if provider_name:
            stmt = stmt.where(ModelCatalog.provider_name == provider_name)

        if model_family:
            stmt = stmt.where(ModelCatalog.model_family == model_family)

        # Sort: recommended first, then by release date (newest first)
        stmt = stmt.order_by(
            ModelCatalog.is_recommended.desc(),
            ModelCatalog.release_date.desc()
        )

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": str(model.id),
                "model_name": model.model_name,
                "model_version": model.model_version,
                "provider_name": model.provider_name,
                "model_family": model.model_family,
                "display_name": model.display_name,
                "description": model.description,
                "context_window": model.context_window,
                "capabilities": model.capabilities,
                "pricing": model.pricing,
                "is_recommended": model.is_recommended,
                "release_date": model.release_date.isoformat() if model.release_date else None,
            }
            for model in models
        ]
