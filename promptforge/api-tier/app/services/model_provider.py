"""
Model Provider Service - Handles execution with various AI model providers
Automatically looks up API keys from organization context
"""

import os
import time
import httpx
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import Organization
from app.models.model_provider import ModelProviderConfig
from app.services.encryption import get_encryption_service


class ModelExecutionRequest(BaseModel):
    """Request to execute a model"""
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 500
    top_p: float = 0.9
    top_k: Optional[int] = None  # Not supported by OpenAI/Claude, kept for compatibility
    reasoning_effort: Optional[str] = None  # GPT-5 only: "minimal", "low", "medium", "high"


class ModelExecutionResult(BaseModel):
    """Result from model execution"""
    response: str
    input_tokens: int
    output_tokens: int
    tokens_used: int
    cost: float
    provider_duration_ms: Optional[float] = None  # Duration from provider (e.g., openai-processing-ms)
    total_duration_ms: Optional[float] = None  # Total client-side duration including network


class ModelProviderService:
    """
    Service for executing prompts with various AI model providers
    Automatically retrieves API keys from organization settings
    """

    # Cost per 1K tokens (approximate, should be loaded from config)
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        # GPT-5 family - Frontier reasoning models (costs per 1M tokens from OpenAI pricing)
        "gpt-5": {"input": 0.00125, "output": 0.01},      # $1.25/1M input, $10/1M output
        "gpt-5-mini": {"input": 0.00025, "output": 0.002},  # $0.25/1M input, $2/1M output
        "gpt-5-nano": {"input": 0.00005, "output": 0.0004},  # $0.05/1M input, $0.40/1M output
        "gpt-4.1": {"input": 0.01, "output": 0.03},
        "gpt-4.1-mini": {"input": 0.002, "output": 0.006},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-sonnet-4.5": {"input": 0.003, "output": 0.015},  # Claude Sonnet 4.5 (default judge model)
    }

    # Model parameter compatibility mapping
    # Defines which parameter names to use for different model families
    MODEL_PARAMETER_COMPATIBILITY = {
        # GPT-5 family - OpenAI's frontier reasoning models
        # IMPORTANT: GPT-5 models only support temperature=1.0 (enforced by OpenAI API)
        # REASONING_EFFORT: Controls thinking time (minimal, low, medium, high)
        #   - minimal: Fast responses, minimal reasoning (best for extraction, formatting, classification)
        #   - low: Faster with less thinking
        #   - medium: Default balanced reasoning (RECOMMENDED for comparisons)
        #   - high: Maximum quality with extended reasoning (best for complex analysis)
        "gpt-5": {
            "max_tokens_param": "max_completion_tokens",
            "supports_response_format": True,
            "api_version": "2024-02-01",
            "supported_params": ["max_completion_tokens", "reasoning_effort"],
            "default_overrides": {"temperature": 1.0},  # Always uses temperature=1.0
            "reasoning_effort_values": ["minimal", "low", "medium", "high"],
            "default_reasoning_effort": "medium"  # Recommended default
        },
        "gpt-5-mini": {
            "max_tokens_param": "max_completion_tokens",
            "supports_response_format": True,
            "api_version": "2024-02-01",
            "supported_params": ["max_completion_tokens", "reasoning_effort"],
            "default_overrides": {"temperature": 1.0},  # Always uses temperature=1.0
            "reasoning_effort_values": ["minimal", "low", "medium", "high"],
            "default_reasoning_effort": "medium"  # Recommended default
        },
        "gpt-5-nano": {
            "max_tokens_param": "max_completion_tokens",
            "supports_response_format": True,
            "api_version": "2024-02-01",
            "supported_params": ["max_completion_tokens", "reasoning_effort"],
            "default_overrides": {"temperature": 1.0},  # Always uses temperature=1.0
            "reasoning_effort_values": ["minimal", "low", "medium", "high"],
            "default_reasoning_effort": "low"  # Nano is optimized for speed
        },
        # GPT-4.1 family uses new parameter names
        "gpt-4.1": {
            "max_tokens_param": "max_completion_tokens",
            "supports_response_format": True,
            "api_version": "2024-02-01",
            "supported_params": ["temperature", "top_p", "max_completion_tokens"],
            "default_overrides": {}
        },
        "gpt-4.1-mini": {
            "max_tokens_param": "max_completion_tokens",
            "supports_response_format": True,
            "api_version": "2024-02-01",
            "supported_params": ["temperature", "top_p", "max_completion_tokens"],
            "default_overrides": {}
        },
        # GPT-4o family uses legacy parameter names
        "gpt-4o": {
            "max_tokens_param": "max_tokens",
            "supports_response_format": True,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        },
        "gpt-4o-mini": {
            "max_tokens_param": "max_tokens",
            "supports_response_format": True,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        },
        # Legacy GPT-4 family
        "gpt-4": {
            "max_tokens_param": "max_tokens",
            "supports_response_format": False,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        },
        "gpt-4-turbo": {
            "max_tokens_param": "max_tokens",
            "supports_response_format": True,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        },
        # GPT-3.5 family
        "gpt-3.5-turbo": {
            "max_tokens_param": "max_tokens",
            "supports_response_format": False,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        },
        # Anthropic Claude family - IMPORTANT: Cannot use temperature AND top_p together
        "claude-": {  # Matches all claude- models
            "max_tokens_param": "max_tokens",
            "supports_response_format": False,
            "api_version": "2023-06-01",
            "supported_params": ["temperature", "max_tokens"],  # Only temperature, NOT top_p
            "default_overrides": {},
            "mutually_exclusive": ["temperature", "top_p"],  # Can only use ONE
            "preferred_param": "temperature"  # Use temperature by default
        }
    }

    @classmethod
    def _get_model_compatibility(cls, model: str) -> Dict[str, Any]:
        """
        Get parameter compatibility settings for a model
        Uses exact match first, then prefix matching for versioned models
        """
        # Try exact match first
        if model in cls.MODEL_PARAMETER_COMPATIBILITY:
            return cls.MODEL_PARAMETER_COMPATIBILITY[model]

        # Try prefix matching for versioned models (e.g., gpt-4-turbo-2024-04-09)
        model_lower = model.lower()
        for model_prefix, config in cls.MODEL_PARAMETER_COMPATIBILITY.items():
            if model_lower.startswith(model_prefix):
                return config

        # Default to legacy parameters for unknown models
        return {
            "max_tokens_param": "max_tokens",
            "supports_response_format": False,
            "api_version": "2023-12-01",
            "supported_params": ["temperature", "top_p", "max_tokens"],
            "default_overrides": {}
        }

    def __init__(self, db: AsyncSession, organization_id: str):
        self.db = db
        self.organization_id = organization_id
        self._api_keys: Dict[str, str] = {}

    async def _get_api_key(self, provider: str) -> str:
        """
        Get API key for provider from organization's ModelProviderConfig
        Falls back to environment variables for development
        """
        # Check cache
        if provider in self._api_keys:
            return self._api_keys[provider]

        # Query ModelProviderConfig for this organization and provider
        result = await self.db.execute(
            select(ModelProviderConfig).where(
                ModelProviderConfig.organization_id == self.organization_id,
                ModelProviderConfig.provider_name == provider,
                ModelProviderConfig.is_active == True
            )
        )
        config = result.scalar_one_or_none()

        if config:
            # Decrypt the API key using encryption service
            encryption_service = get_encryption_service()
            try:
                api_key = encryption_service.decrypt_api_key(config.api_key_encrypted)
                self._api_keys[provider] = api_key
                return api_key
            except Exception as e:
                raise ValueError(f"Failed to decrypt API key for provider {provider}: {str(e)}")

        # Fallback to environment variables (development only)
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        if api_key:
            self._api_keys[provider] = api_key
            return api_key

        raise ValueError(f"No API key configured for provider: {provider}")

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name"""
        model_lower = model.lower()
        if "gpt" in model_lower or "openai" in model_lower:
            return "openai"
        elif "claude" in model_lower or "anthropic" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower or "palm" in model_lower:
            return "google"
        else:
            raise ValueError(f"Unknown model provider for model: {model}")

    async def execute(self, request: ModelExecutionRequest) -> ModelExecutionResult:
        """Execute prompt with appropriate model provider"""
        provider = self._detect_provider(request.model)

        if provider == "openai":
            return await self._execute_openai(request)
        elif provider == "anthropic":
            return await self._execute_anthropic(request)
        else:
            raise ValueError(f"Provider not supported: {provider}")

    async def _execute_openai(self, request: ModelExecutionRequest) -> ModelExecutionResult:
        """Execute with OpenAI API using model-specific parameter compatibility"""
        api_key = await self._get_api_key("openai")

        start_time = time.time()

        # Get model-specific compatibility settings
        compatibility = self._get_model_compatibility(request.model)

        # Build base payload
        payload = {
            "model": request.model,
            "messages": request.messages,
        }

        # Get supported parameters and overrides for this model
        supported_params = compatibility.get("supported_params", ["temperature", "top_p", "max_tokens"])
        default_overrides = compatibility.get("default_overrides", {})
        max_tokens_param = compatibility["max_tokens_param"]

        # Apply default overrides first (e.g., gpt-5-nano always uses temperature=1)
        for param, value in default_overrides.items():
            payload[param] = value

        # Add request parameters only if supported by the model
        if "temperature" in supported_params and "temperature" not in default_overrides:
            payload["temperature"] = request.temperature

        if "top_p" in supported_params and "top_p" not in default_overrides:
            payload["top_p"] = request.top_p

        # Add max_tokens using model-specific parameter name
        if max_tokens_param in supported_params:
            payload[max_tokens_param] = request.max_tokens

        # Add reasoning_effort for GPT-5 models if supported
        if "reasoning_effort" in supported_params:
            if request.reasoning_effort:
                # Validate reasoning_effort value
                valid_values = compatibility.get("reasoning_effort_values", [])
                if request.reasoning_effort in valid_values:
                    payload["reasoning_effort"] = request.reasoning_effort
                else:
                    # Use default if invalid value provided
                    default_effort = compatibility.get("default_reasoning_effort", "medium")
                    payload["reasoning_effort"] = default_effort
            else:
                # Use default reasoning_effort if not specified
                default_effort = compatibility.get("default_reasoning_effort")
                if default_effort:
                    payload["reasoning_effort"] = default_effort

        # Determine timeout based on model (GPT-5 models with reasoning need more time)
        # GPT-5 with medium/high reasoning can take 2-3 minutes per request
        timeout_seconds = 300.0 if request.model.startswith("gpt-5") else 60.0

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout_seconds,
            )

            # Calculate total duration including network
            total_duration_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                error_details = response.text
                # Log the payload for debugging
                import json
                print(f"[ERROR] OpenAI API request failed with status {response.status_code}")
                print(f"[ERROR] Model: {request.model}")
                print(f"[ERROR] Payload: {json.dumps(payload, indent=2)}")
                print(f"[ERROR] Response: {error_details}")
                raise Exception(f"OpenAI API error: {error_details}")

            # Extract provider processing time from headers
            provider_duration_ms = None
            openai_processing_header = response.headers.get("openai-processing-ms")
            if openai_processing_header:
                try:
                    provider_duration_ms = float(openai_processing_header)
                except (ValueError, TypeError):
                    pass

            # Also check x-envoy-upstream-service-time (alternative timing header)
            if not provider_duration_ms:
                envoy_time_header = response.headers.get("x-envoy-upstream-service-time")
                if envoy_time_header:
                    try:
                        provider_duration_ms = float(envoy_time_header)
                    except (ValueError, TypeError):
                        pass

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data["usage"]["total_tokens"]

            # Calculate cost
            cost_config = self.MODEL_COSTS.get(request.model, {"input": 0.01, "output": 0.03})
            input_tokens = data["usage"]["prompt_tokens"]
            output_tokens = data["usage"]["completion_tokens"]
            cost = (
                (input_tokens / 1000) * cost_config["input"] +
                (output_tokens / 1000) * cost_config["output"]
            )

            return ModelExecutionResult(
                response=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                tokens_used=tokens_used,
                cost=cost,
                provider_duration_ms=provider_duration_ms,
                total_duration_ms=total_duration_ms,
            )

    async def _execute_anthropic(self, request: ModelExecutionRequest) -> ModelExecutionResult:
        """Execute with Anthropic API using parameter compatibility"""
        api_key = await self._get_api_key("anthropic")

        start_time = time.time()

        # Get model-specific compatibility settings
        compatibility = self._get_model_compatibility(request.model)

        # Convert messages format (extract system prompt)
        system_prompt = None
        messages = []
        for msg in request.messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                messages.append(msg)

        async with httpx.AsyncClient() as client:
            # Build base payload
            payload: Dict[str, Any] = {
                "model": request.model,
                "messages": messages,
                "max_tokens": request.max_tokens,
            }

            # Get supported parameters
            supported_params = compatibility.get("supported_params", ["temperature", "max_tokens"])

            # Anthropic constraint: temperature and top_p are mutually exclusive
            # Use only temperature (preferred parameter for judge model evaluations)
            if "temperature" in supported_params:
                payload["temperature"] = request.temperature
            # Do NOT add top_p for Anthropic models (causes API error)

            if system_prompt:
                payload["system"] = system_prompt

            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60.0,
            )

            # Calculate total duration including network
            total_duration_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.text}")

            # Claude API does not provide processing time headers
            # We use client-side timing as the best available metric
            provider_duration_ms = None

            data = response.json()
            content = data["content"][0]["text"]
            input_tokens = data["usage"]["input_tokens"]
            output_tokens = data["usage"]["output_tokens"]
            tokens_used = input_tokens + output_tokens

            # Calculate cost
            cost_config = self.MODEL_COSTS.get(request.model, {"input": 0.003, "output": 0.015})
            cost = (
                (input_tokens / 1000) * cost_config["input"] +
                (output_tokens / 1000) * cost_config["output"]
            )

            return ModelExecutionResult(
                response=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                tokens_used=tokens_used,
                cost=cost,
                provider_duration_ms=provider_duration_ms,
                total_duration_ms=total_duration_ms,
            )
