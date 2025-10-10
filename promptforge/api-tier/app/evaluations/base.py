"""
Base classes and interfaces for the Evaluation Abstraction Layer (EAL)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from uuid import UUID
from app.models.evaluation_catalog import EvaluationSource, EvaluationType, EvaluationCategory


@dataclass
class EvaluationRequest:
    """
    Request object for running an evaluation

    Contains all the information needed to execute an evaluation on a trace.
    """
    trace_id: UUID
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

    # Trace context
    trace_metadata: Optional[Dict[str, Any]] = None
    spans: Optional[List[Dict[str, Any]]] = None

    # Model context
    model_name: Optional[str] = None
    prompt_template: Optional[str] = None
    prompt_variables: Optional[Dict[str, Any]] = None

    # Database session for adapter queries (API keys, configs)
    db_session: Optional[Any] = None


@dataclass
class EvaluationResult:
    """
    Result object returned by an evaluation

    Standardized result format across all evaluation sources.
    """
    # Core results
    score: Optional[float] = None  # For METRIC type (0.0-1.0)
    passed: Optional[bool] = None  # For VALIDATOR type
    category: Optional[str] = None  # For CLASSIFIER type
    reason: Optional[str] = None  # Explanation of the result

    # Detailed analysis
    details: Optional[Dict[str, Any]] = None  # Additional metrics and data
    suggestions: Optional[List[str]] = None  # Improvement suggestions

    # Execution metadata
    execution_time_ms: Optional[float] = None
    model_used: Optional[str] = None  # For LLM-as-Judge

    # LLM Cost Tracking (for LLM-based evaluations)
    input_tokens: Optional[int] = None  # Input tokens used by evaluation LLM
    output_tokens: Optional[int] = None  # Output tokens used by evaluation LLM
    total_tokens: Optional[int] = None  # Total tokens (input + output)
    evaluation_cost: Optional[float] = None  # Cost of running the evaluation

    # Vendor-Specific Metrics
    vendor_metrics: Optional[Dict[str, Any]] = None  # Vendor-specific metrics (deprecated - use llm_metadata)
    llm_metadata: Optional[Dict[str, Any]] = None  # Comprehensive LLM metadata (tokens, costs, performance, etc.)

    # Error handling
    error: Optional[str] = None
    status: str = "completed"  # completed, failed


@dataclass
class EvaluationMetadata:
    """
    Metadata about an evaluation

    Used for listing and discovering available evaluations.
    """
    uuid: str  # Unique identifier for the evaluation
    name: str
    description: str
    source: EvaluationSource
    evaluation_type: EvaluationType
    category: EvaluationCategory

    # Configuration
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None

    # Access control
    is_public: bool = False
    organization_id: Optional[UUID] = None
    project_id: Optional[UUID] = None

    # Metadata
    version: str = "1.0.0"
    tags: Optional[List[str]] = None


class EvaluationAdapter(ABC):
    """
    Abstract base class for all evaluation adapters

    This defines the contract that all evaluation adapters must implement,
    regardless of whether they are vendor, custom, PromptForge, or LLM-judge evaluations.
    """

    def __init__(self, source: EvaluationSource):
        """
        Initialize the adapter

        Args:
            source: The source type of this adapter
        """
        self.source = source

    @abstractmethod
    async def list_evaluations(
        self,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> List[EvaluationMetadata]:
        """
        List all available evaluations from this adapter

        Args:
            organization_id: Filter by organization (for custom evaluations)
            project_id: Filter by project (for custom evaluations)

        Returns:
            List of evaluation metadata objects
        """
        pass

    @abstractmethod
    async def get_evaluation(self, evaluation_uuid: str) -> Optional[EvaluationMetadata]:
        """
        Get metadata for a specific evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation

        Returns:
            Evaluation metadata or None if not found
        """
        pass

    @abstractmethod
    async def execute(
        self,
        evaluation_uuid: str,
        request: EvaluationRequest
    ) -> EvaluationResult:
        """
        Execute an evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation
            request: Evaluation request containing trace data

        Returns:
            Evaluation result
        """
        pass

    @abstractmethod
    async def validate_config(
        self,
        evaluation_uuid: str,
        config: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate configuration for an evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    def get_source(self) -> EvaluationSource:
        """Get the source type of this adapter"""
        return self.source

    async def supports_evaluation(self, evaluation_uuid: str) -> bool:
        """
        Check if this adapter supports a specific evaluation

        Args:
            evaluation_uuid: Unique identifier for the evaluation

        Returns:
            True if this adapter can execute the evaluation
        """
        metadata = await self.get_evaluation(evaluation_uuid)
        return metadata is not None
