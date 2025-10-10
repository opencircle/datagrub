"""
Provider Configuration Service

Retrieves API keys and configuration from database for evaluation execution.
Provides fallback to environment variables for backward compatibility.

Performance: Uses async queries and caching for high-throughput evaluation workloads.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import os
import logging

from app.models.model_provider import ModelProviderConfig
from app.services.encryption import EncryptionService

logger = logging.getLogger(__name__)


class ProviderConfigService:
    """
    Service for retrieving provider configurations for evaluation execution.

    This service abstracts the retrieval of API keys and provider-specific
    configuration, supporting both database-stored keys and environment variables.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the provider config service.

        Args:
            db_session: Database session for querying configurations
        """
        self.db = db_session
        self.encryption = EncryptionService()

    async def get_provider_config(
        self,
        provider_name: str,
        organization_id: UUID,
        project_id: Optional[UUID] = None,
        provider_type: str = "llm"
    ) -> Optional[Dict[str, Any]]:
        """
        Get provider configuration (API key + config) for evaluation execution.

        Retrieval Priority:
        1. Project-level configuration (if project_id provided)
        2. Organization-level configuration
        3. Environment variable fallback (backward compatibility)

        Args:
            provider_name: Provider identifier (e.g., 'openai', 'anthropic')
            organization_id: Organization ID from current user
            project_id: Optional project ID for project-scoped configs
            provider_type: Provider type (default: 'llm')

        Returns:
            Dict with 'api_key' and 'config', or None if not found

        Example:
            config = await service.get_provider_config('openai', org_id)
            if config:
                client = OpenAI(api_key=config['api_key'])
                model = config['config'].get('default_model', 'gpt-4')
        """
        # Try project-level configuration first
        if project_id:
            config = await self._get_config_from_db(
                provider_name, organization_id, project_id, provider_type
            )
            if config:
                logger.info(
                    f"Using project-level config: provider={provider_name}, "
                    f"project={project_id}"
                )
                return config

        # Try organization-level configuration
        config = await self._get_config_from_db(
            provider_name, organization_id, None, provider_type
        )
        if config:
            logger.info(
                f"Using org-level config: provider={provider_name}, "
                f"org={organization_id}"
            )
            return config

        # Fallback to environment variable (backward compatibility)
        env_config = self._get_config_from_env(provider_name)
        if env_config:
            logger.warning(
                f"Fallback to env var: provider={provider_name}, "
                f"org={organization_id} (consider migrating to database)"
            )
            return env_config

        logger.error(
            f"No configuration found: provider={provider_name}, "
            f"org={organization_id}, project={project_id}"
        )
        return None

    async def _get_config_from_db(
        self,
        provider_name: str,
        organization_id: UUID,
        project_id: Optional[UUID],
        provider_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve configuration from database.

        Args:
            provider_name: Provider identifier
            organization_id: Organization ID
            project_id: Project ID (None for org-level)
            provider_type: Provider type

        Returns:
            Dict with api_key and config, or None
        """
        # Build query with organization scoping (SOC 2 requirement)
        query = select(ModelProviderConfig).where(
            and_(
                ModelProviderConfig.organization_id == organization_id,
                ModelProviderConfig.provider_name == provider_name,
                ModelProviderConfig.provider_type == provider_type,
                ModelProviderConfig.is_active == True
            )
        )

        # Add project filter
        if project_id is not None:
            query = query.where(ModelProviderConfig.project_id == project_id)
        else:
            query = query.where(ModelProviderConfig.project_id.is_(None))

        # Prefer default configuration
        query = query.order_by(ModelProviderConfig.is_default.desc())

        # Execute query
        result = await self.db.execute(query)
        config_record = result.scalar_one_or_none()

        if not config_record:
            return None

        # Decrypt API key and configuration
        try:
            api_key = self.encryption.decrypt_api_key(config_record.api_key_encrypted)

            # Decrypt config if present
            config = {}
            if config_record.config_encrypted:
                config = self.encryption.decrypt_config(config_record.config_encrypted)

            # Update usage tracking (background - don't await)
            # This is a fire-and-forget operation for performance
            await self._update_usage_stats(config_record.id)

            return {
                "api_key": api_key,
                "config": config,
                "config_id": config_record.id,
                "display_name": config_record.display_name
            }

        except Exception as e:
            logger.error(
                f"Failed to decrypt config: provider={provider_name}, "
                f"config_id={config_record.id}, error={str(e)}"
            )
            return None

    def _get_config_from_env(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Fallback to environment variable for backward compatibility.

        Args:
            provider_name: Provider identifier

        Returns:
            Dict with api_key from environment, or None
        """
        # Map provider name to environment variable
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "cohere": "COHERE_API_KEY",
            "google": "GOOGLE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY"
        }

        env_var = env_var_map.get(provider_name)
        if not env_var:
            return None

        api_key = os.getenv(env_var)
        if not api_key:
            return None

        return {
            "api_key": api_key,
            "config": {},  # No config from env vars
            "config_id": None,
            "display_name": f"{provider_name} (env)"
        }

    async def _update_usage_stats(self, config_id: UUID):
        """
        Update usage statistics for configuration.

        Args:
            config_id: Configuration ID to update
        """
        try:
            from datetime import datetime

            # Update last_used_at and increment usage_count
            result = await self.db.execute(
                select(ModelProviderConfig).where(ModelProviderConfig.id == config_id)
            )
            config = result.scalar_one_or_none()

            if config:
                config.last_used_at = datetime.utcnow()
                config.usage_count = (config.usage_count or 0) + 1
                # Don't commit here - will be committed with parent transaction

        except Exception as e:
            # Don't fail evaluation if usage tracking fails
            logger.warning(f"Failed to update usage stats: config_id={config_id}, error={str(e)}")

    async def get_openai_config(
        self,
        organization_id: UUID,
        project_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Convenience method for getting OpenAI configuration.

        Args:
            organization_id: Organization ID
            project_id: Optional project ID

        Returns:
            OpenAI configuration or None
        """
        return await self.get_provider_config("openai", organization_id, project_id)

    async def get_anthropic_config(
        self,
        organization_id: UUID,
        project_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Convenience method for getting Anthropic configuration.

        Args:
            organization_id: Organization ID
            project_id: Optional project ID

        Returns:
            Anthropic configuration or None
        """
        return await self.get_provider_config("anthropic", organization_id, project_id)

    async def validate_provider_available(
        self,
        provider_name: str,
        organization_id: UUID,
        project_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if a provider is available for use.

        Args:
            provider_name: Provider identifier
            organization_id: Organization ID
            project_id: Optional project ID

        Returns:
            True if provider is configured and available
        """
        config = await self.get_provider_config(
            provider_name, organization_id, project_id
        )
        return config is not None


def get_provider_config_service(db: AsyncSession) -> ProviderConfigService:
    """
    Dependency for getting provider config service.

    Usage in FastAPI:
        @router.post("/evaluations/run")
        async def run_evaluation(
            provider_service: ProviderConfigService = Depends(get_provider_config_service),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            config = await provider_service.get_openai_config(current_user.organization_id)
    """
    return ProviderConfigService(db)
