"""
LLM Metadata Schema for Evaluation Tracking

This schema captures comprehensive LLM metrics when evaluations involve LLM invocations.
Based on industry standards from OpenAI, Anthropic, and LLM observability platforms.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class FinishReason(str, Enum):
    """LLM response completion reason"""
    STOP = "stop"  # Natural completion
    LENGTH = "length"  # Max tokens reached
    CONTENT_FILTER = "content_filter"  # Content policy violation
    TOOL_CALLS = "tool_calls"  # Function/tool call
    ERROR = "error"  # Error occurred
    TIMEOUT = "timeout"  # Request timeout


class LLMTokenUsage(BaseModel):
    """Token usage metrics"""

    input_tokens: Optional[int] = Field(None, description="Number of input/prompt tokens")
    output_tokens: Optional[int] = Field(None, description="Number of output/completion tokens")
    total_tokens: Optional[int] = Field(None, description="Total tokens (input + output)")

    # Cache metrics (for providers like Anthropic with prompt caching)
    cache_read_tokens: Optional[int] = Field(None, description="Tokens read from cache")
    cache_creation_tokens: Optional[int] = Field(None, description="Tokens written to cache")


class LLMCostMetrics(BaseModel):
    """Cost breakdown for LLM usage"""

    input_cost: Optional[float] = Field(None, description="Cost for input tokens (USD)")
    output_cost: Optional[float] = Field(None, description="Cost for output tokens (USD)")
    cache_read_cost: Optional[float] = Field(None, description="Cost for cache read tokens (USD)")
    cache_write_cost: Optional[float] = Field(None, description="Cost for cache write tokens (USD)")
    total_cost: Optional[float] = Field(None, description="Total cost (USD)")

    # Pricing info for reference
    input_price_per_1k: Optional[float] = Field(None, description="Input token price per 1K tokens")
    output_price_per_1k: Optional[float] = Field(None, description="Output token price per 1K tokens")


class LLMPerformanceMetrics(BaseModel):
    """Performance and latency metrics"""

    total_duration_ms: Optional[float] = Field(None, description="Total request duration (ms)")
    time_to_first_token_ms: Optional[float] = Field(None, description="Time to first token (ms)")
    tokens_per_second: Optional[float] = Field(None, description="Throughput (tokens/second)")

    # Queue and processing time breakdown
    queue_time_ms: Optional[float] = Field(None, description="Time spent in queue (ms)")
    processing_time_ms: Optional[float] = Field(None, description="Time spent processing (ms)")


class LLMRequestParameters(BaseModel):
    """LLM request configuration parameters"""

    model: Optional[str] = Field(None, description="Model name/version used")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    top_k: Optional[int] = Field(None, description="Top-K sampling parameter")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class LLMResponseMetadata(BaseModel):
    """LLM response metadata"""

    finish_reason: Optional[FinishReason] = Field(None, description="Why the generation stopped")
    model_version: Optional[str] = Field(None, description="Actual model version used by provider")
    request_id: Optional[str] = Field(None, description="Provider's request ID")
    system_fingerprint: Optional[str] = Field(None, description="System configuration fingerprint")


class LLMRateLimitInfo(BaseModel):
    """Rate limit information from provider"""

    # Requests
    requests_limit: Optional[int] = Field(None, description="Requests per minute limit")
    requests_remaining: Optional[int] = Field(None, description="Remaining requests")
    requests_reset_at: Optional[str] = Field(None, description="When request limit resets (ISO 8601)")

    # Tokens
    tokens_limit: Optional[int] = Field(None, description="Tokens per minute limit")
    tokens_remaining: Optional[int] = Field(None, description="Remaining tokens")
    tokens_reset_at: Optional[str] = Field(None, description="When token limit resets (ISO 8601)")


class LLMMetadata(BaseModel):
    """
    Comprehensive LLM metadata for evaluation tracking

    This schema captures all available metrics when evaluations involve LLM invocations,
    following industry standards from OpenAI, Anthropic, and observability platforms.
    """

    # Provider information
    provider: str = Field(..., description="LLM provider (openai, anthropic, azure, etc.)")
    provider_model: str = Field(..., description="Model identifier used by provider")

    # Token usage
    token_usage: Optional[LLMTokenUsage] = Field(None, description="Token usage metrics")

    # Cost metrics
    cost_metrics: Optional[LLMCostMetrics] = Field(None, description="Cost breakdown")

    # Performance metrics
    performance_metrics: Optional[LLMPerformanceMetrics] = Field(None, description="Performance and latency")

    # Request parameters
    request_parameters: Optional[LLMRequestParameters] = Field(None, description="Request configuration")

    # Response metadata
    response_metadata: Optional[LLMResponseMetadata] = Field(None, description="Response metadata")

    # Rate limit information
    rate_limit_info: Optional[LLMRateLimitInfo] = Field(None, description="Rate limit status")

    # Additional provider-specific data
    provider_specific: Optional[Dict[str, Any]] = Field(None, description="Provider-specific metrics")

    # Timestamps
    request_timestamp: Optional[str] = Field(None, description="When request was sent (ISO 8601)")
    response_timestamp: Optional[str] = Field(None, description="When response received (ISO 8601)")


class LLMMetadataFlat(BaseModel):
    """
    Flattened LLM metadata schema for backward compatibility

    This is a simplified version that can be used when full structured data is not needed.
    All nested objects from LLMMetadata are flattened to top-level fields.
    """

    # Provider
    provider: Optional[str] = None
    provider_model: Optional[str] = None
    model_version: Optional[str] = None

    # Token usage
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cache_read_tokens: Optional[int] = None
    cache_creation_tokens: Optional[int] = None

    # Cost
    input_cost: Optional[float] = None
    output_cost: Optional[float] = None
    total_cost: Optional[float] = None

    # Performance
    total_duration_ms: Optional[float] = None
    time_to_first_token_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None

    # Request parameters
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None

    # Response metadata
    finish_reason: Optional[str] = None
    request_id: Optional[str] = None

    # Timestamps
    request_timestamp: Optional[str] = None
    response_timestamp: Optional[str] = None
