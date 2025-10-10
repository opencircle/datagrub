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
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
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
        """Execute with OpenAI API"""
        api_key = await self._get_api_key("openai")

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": request.model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "top_p": request.top_p,
                },
                timeout=60.0,
            )

            # Calculate total duration including network
            total_duration_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

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
        """Execute with Anthropic API"""
        api_key = await self._get_api_key("anthropic")

        start_time = time.time()

        # Convert messages format (extract system prompt)
        system_prompt = None
        messages = []
        for msg in request.messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                messages.append(msg)

        async with httpx.AsyncClient() as client:
            payload: Dict[str, Any] = {
                "model": request.model,
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }

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
