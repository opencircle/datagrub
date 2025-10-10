"""
Evaluation Registry - Central registry for all evaluation adapters
"""
from typing import Dict, List, Optional
from uuid import UUID
import logging

from app.models.evaluation_catalog import EvaluationSource
from app.evaluations.base import (
    EvaluationAdapter,
    EvaluationRequest,
    EvaluationResult,
    EvaluationMetadata,
)

logger = logging.getLogger(__name__)


class EvaluationRegistry:
    """
    Central registry for all evaluation adapters

    This singleton class manages all registered evaluation adapters and
    provides a unified interface for discovering and executing evaluations.

    Supports multiple adapters per source (e.g., multiple vendor libraries).
    """

    _instance = None
    _adapters: Dict[str, EvaluationAdapter] = {}  # Changed to use adapter class name as key
    _adapters_by_source: Dict[EvaluationSource, List[EvaluationAdapter]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry"""
        if not hasattr(self, '_initialized'):
            self._adapters = {}
            self._adapters_by_source = {}
            self._initialized = True
            logger.info("Initialized EvaluationRegistry")

    def register_adapter(self, source: EvaluationSource, adapter: EvaluationAdapter, adapter_name: Optional[str] = None) -> None:
        """
        Register an evaluation adapter

        Args:
            source: Source type of the adapter
            adapter: Adapter instance to register
            adapter_name: Optional name/key for the adapter (defaults to class name)
        """
        # Use adapter class name as key if not provided
        if adapter_name is None:
            adapter_name = adapter.__class__.__name__

        # Register by adapter name (primary key)
        if adapter_name in self._adapters:
            logger.warning(f"Overwriting existing adapter: {adapter_name}")

        self._adapters[adapter_name] = adapter

        # Also register by source for lookups
        if source not in self._adapters_by_source:
            self._adapters_by_source[source] = []

        # Remove old instance of same adapter class if exists
        self._adapters_by_source[source] = [
            a for a in self._adapters_by_source[source]
            if a.__class__.__name__ != adapter_name
        ]
        self._adapters_by_source[source].append(adapter)

        logger.info(f"Registered {adapter_name} for source: {source}")

    def get_adapter(self, source: EvaluationSource) -> Optional[EvaluationAdapter]:
        """
        Get first adapter by source type (for backward compatibility)

        Args:
            source: Source type to retrieve

        Returns:
            First adapter instance for source or None if not found
        """
        adapters = self._adapters_by_source.get(source, [])
        return adapters[0] if adapters else None

    def get_adapter_by_name(self, adapter_name: str) -> Optional[EvaluationAdapter]:
        """
        Get an adapter by its class name

        Args:
            adapter_name: Name/class of the adapter

        Returns:
            Adapter instance or None if not found
        """
        return self._adapters.get(adapter_name)

    def get_adapters_by_source(self, source: EvaluationSource) -> List[EvaluationAdapter]:
        """
        Get all adapters for a source type

        Args:
            source: Source type to retrieve

        Returns:
            List of adapter instances for the source
        """
        return self._adapters_by_source.get(source, [])

    def list_sources(self) -> List[EvaluationSource]:
        """
        List all registered sources

        Returns:
            List of registered evaluation sources
        """
        return list(self._adapters.keys())

    async def list_all_evaluations(
        self,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        source_filter: Optional[EvaluationSource] = None
    ) -> List[EvaluationMetadata]:
        """
        List all available evaluations from all adapters

        Args:
            organization_id: Filter by organization
            project_id: Filter by project
            source_filter: Filter by specific source

        Returns:
            Combined list of all evaluations
        """
        all_evaluations = []

        # Filter adapters if source specified
        adapters = self._adapters.items()
        if source_filter:
            adapter = self._adapters.get(source_filter)
            if adapter:
                adapters = [(source_filter, adapter)]
            else:
                return []

        # Collect evaluations from all adapters
        for source, adapter in adapters:
            try:
                evaluations = await adapter.list_evaluations(
                    organization_id=organization_id,
                    project_id=project_id
                )
                all_evaluations.extend(evaluations)
            except Exception as e:
                logger.error(f"Error listing evaluations from {source}: {e}")
                # Continue with other adapters

        return all_evaluations

    async def get_evaluation(self, evaluation_uuid: str) -> Optional[EvaluationMetadata]:
        """
        Get metadata for a specific evaluation

        Searches across all registered adapters.

        Args:
            evaluation_uuid: Unique identifier for the evaluation

        Returns:
            Evaluation metadata or None if not found
        """
        for adapter in self._adapters.values():
            try:
                metadata = await adapter.get_evaluation(evaluation_uuid)
                if metadata:
                    return metadata
            except Exception as e:
                logger.error(f"Error getting evaluation {evaluation_uuid}: {e}")

        return None

    async def execute_evaluation(
        self,
        evaluation_uuid: str,
        request: EvaluationRequest,
        adapter_class: Optional[str] = None,
        source: Optional[EvaluationSource] = None
    ) -> EvaluationResult:
        """
        Execute an evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation
            request: Evaluation request
            adapter_class: Optional adapter class name from database
            source: Optional source hint to speed up lookup

        Returns:
            Evaluation result

        Raises:
            ValueError: If evaluation not found or adapter not available
        """
        # Try adapter_class first (from database)
        if adapter_class:
            adapter = self._adapters.get(adapter_class)
            if adapter:
                try:
                    return await adapter.execute(evaluation_uuid, request)
                except Exception as e:
                    logger.error(f"Error executing with {adapter_class}: {e}")
                    # Fall through to search other adapters

        # Try specified source
        if source:
            adapters = self._adapters_by_source.get(source, [])
            for adapter in adapters:
                try:
                    if await adapter.supports_evaluation(evaluation_uuid):
                        return await adapter.execute(evaluation_uuid, request)
                except Exception as e:
                    logger.error(f"Error checking adapter support: {e}")

        # Search all adapters
        for adapter in self._adapters.values():
            try:
                if await adapter.supports_evaluation(evaluation_uuid):
                    return await adapter.execute(evaluation_uuid, request)
            except Exception as e:
                logger.error(f"Error checking adapter support: {e}")

        # Not found
        raise ValueError(f"No adapter found for evaluation: {evaluation_uuid}")

    async def execute_multiple_evaluations(
        self,
        evaluation_uuids: List[str],
        request: EvaluationRequest
    ) -> Dict[str, EvaluationResult]:
        """
        Execute multiple evaluations on the same trace

        Args:
            evaluation_uuids: List of evaluation identifiers
            request: Evaluation request (same for all)

        Returns:
            Dictionary mapping evaluation_uuid to result
        """
        results = {}

        for evaluation_uuid in evaluation_uuids:
            try:
                result = await self.execute_evaluation(evaluation_uuid, request)
                results[evaluation_uuid] = result
            except Exception as e:
                logger.error(f"Error executing evaluation {evaluation_uuid}: {e}")
                results[evaluation_uuid] = EvaluationResult(
                    status="failed",
                    error=str(e)
                )

        return results

    async def validate_config(
        self,
        evaluation_uuid: str,
        config: Dict,
        source: Optional[EvaluationSource] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate configuration for an evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation
            config: Configuration to validate
            source: Optional source hint

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Try specified source first
        if source:
            adapter = self._adapters.get(source)
            if adapter and await adapter.supports_evaluation(evaluation_uuid):
                return await adapter.validate_config(evaluation_uuid, config)

        # Search all adapters
        for adapter in self._adapters.values():
            try:
                if await adapter.supports_evaluation(evaluation_uuid):
                    return await adapter.validate_config(evaluation_uuid, config)
            except Exception as e:
                logger.error(f"Error validating config: {e}")

        return False, f"No adapter found for evaluation: {evaluation_uuid}"

    def clear(self) -> None:
        """Clear all registered adapters (mainly for testing)"""
        self._adapters.clear()
        logger.info("Cleared all registered adapters")


# Global registry instance
registry = EvaluationRegistry()
