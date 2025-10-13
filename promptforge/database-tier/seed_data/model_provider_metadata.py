"""
Model Provider Metadata Seed Data

This script seeds the model_provider_metadata table with supported providers.
Metadata includes configuration fields, capabilities, and supported models for UI rendering.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add api-tier to path for imports
current_dir = Path(__file__).resolve().parent
api_tier_path = current_dir.parent.parent / "api-tier"
sys.path.insert(0, str(api_tier_path))

# Set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = str(api_tier_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import uuid
from datetime import datetime

from app.core.config import settings
from app.models.model_provider import ModelProviderMetadata


# Provider metadata catalog
PROVIDER_METADATA = [
    {
        "provider_name": "openai",
        "provider_type": "llm",
        "display_name": "OpenAI",
        "description": "OpenAI GPT models for text generation, chat, and embeddings",
        "icon_url": "https://cdn.promptforge.com/icons/openai.svg",
        "documentation_url": "https://platform.openai.com/docs",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "placeholder": "sk-proj-...",
                "help_text": "Your OpenAI API key from https://platform.openai.com/api-keys",
                "required": True,
                "validation": {
                    "pattern": "^sk-(proj-)?[A-Za-z0-9]{20,}$",
                    "min_length": 20
                }
            }
        ],
        "optional_fields": [
            {
                "name": "organization_id",
                "type": "string",
                "label": "Organization ID",
                "placeholder": "org-...",
                "help_text": "Optional organization ID for multi-org accounts"
            },
            {
                "name": "base_url",
                "type": "url",
                "label": "Base URL",
                "placeholder": "https://api.openai.com/v1",
                "help_text": "Custom API endpoint (for Azure OpenAI or proxies)",
                "default": "https://api.openai.com/v1"
            },
            {
                "name": "default_model",
                "type": "select",
                "label": "Default Model",
                "options": [
                    "gpt-5",
                    "gpt-5-mini",
                    "gpt-5-nano",
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-4",
                    "gpt-3.5-turbo"
                ],
                "default": "gpt-4o",
                "model_display_names": {
                    "gpt-5": "GPT-5",
                    "gpt-5-mini": "GPT-5 Mini",
                    "gpt-5-nano": "GPT-5 Nano",
                    "gpt-4.1": "GPT-4.1",
                    "gpt-4.1-mini": "GPT-4.1 Mini",
                    "gpt-4o": "GPT-4o",
                    "gpt-4o-mini": "GPT-4o Mini",
                    "gpt-4-turbo": "GPT-4 Turbo",
                    "gpt-4": "GPT-4",
                    "gpt-3.5-turbo": "GPT-3.5 Turbo"
                },
                "pricing": {
                    "gpt-5": {"input": 0.02, "output": 0.06, "description": "Most advanced reasoning and generation"},
                    "gpt-5-mini": {"input": 0.004, "output": 0.012, "description": "Balanced performance and cost"},
                    "gpt-5-nano": {"input": 0.0001, "output": 0.0004, "description": "Ultra-fast and economical"},
                    "gpt-4.1": {"input": 0.01, "output": 0.03, "description": "Latest flagship with 1M context"},
                    "gpt-4.1-mini": {"input": 0.002, "output": 0.006, "description": "Fast and efficient"},
                    "gpt-4o": {"input": 0.005, "output": 0.015, "description": "Multimodal flagship"},
                    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "description": "Cost-effective multimodal"},
                    "gpt-4-turbo": {"input": 0.01, "output": 0.03, "description": "Optimized GPT-4"},
                    "gpt-4": {"input": 0.03, "output": 0.06, "description": "Legacy high-performance"},
                    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002, "description": "Fast and economical"}
                },
                "context_windows": {
                    "gpt-5": 2000000,
                    "gpt-5-mini": 1000000,
                    "gpt-5-nano": 256000,
                    "gpt-4.1": 1000000,
                    "gpt-4.1-mini": 1000000,
                    "gpt-4o": 128000,
                    "gpt-4o-mini": 128000,
                    "gpt-4-turbo": 128000,
                    "gpt-4": 8192,
                    "gpt-3.5-turbo": 16384
                },
                "parameter_compatibility": {
                    "gpt-5": {
                        "max_tokens_param": "max_completion_tokens",
                        "supports_response_format": True,
                        "api_version": "2024-02-01",
                        "supported_params": ["temperature", "top_p", "max_completion_tokens"],
                        "default_overrides": {},
                        "notes": "Full parameter support"
                    },
                    "gpt-5-mini": {
                        "max_tokens_param": "max_completion_tokens",
                        "supports_response_format": True,
                        "api_version": "2024-02-01",
                        "supported_params": ["temperature", "top_p", "max_completion_tokens"],
                        "default_overrides": {},
                        "notes": "Full parameter support"
                    },
                    "gpt-5-nano": {
                        "max_tokens_param": "max_completion_tokens",
                        "supports_response_format": True,
                        "api_version": "2024-02-01",
                        "supported_params": ["max_completion_tokens"],
                        "default_overrides": {"temperature": 1.0},
                        "notes": "Always uses temperature=1.0, does not support top_p"
                    },
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
                    "gpt-4-turbo": {
                        "max_tokens_param": "max_tokens",
                        "supports_response_format": True,
                        "api_version": "2023-12-01",
                        "supported_params": ["temperature", "top_p", "max_tokens"],
                        "default_overrides": {}
                    },
                    "gpt-4": {
                        "max_tokens_param": "max_tokens",
                        "supports_response_format": False,
                        "api_version": "2023-12-01",
                        "supported_params": ["temperature", "top_p", "max_tokens"],
                        "default_overrides": {}
                    },
                    "gpt-3.5-turbo": {
                        "max_tokens_param": "max_tokens",
                        "supports_response_format": False,
                        "api_version": "2023-12-01",
                        "supported_params": ["temperature", "top_p", "max_tokens"],
                        "default_overrides": {}
                    }
                }
            },
            {
                "name": "max_tokens",
                "type": "number",
                "label": "Max Tokens",
                "placeholder": "4096",
                "default": 4096
            }
        ],
        "capabilities": {
            "streaming": True,
            "function_calling": True,
            "vision": True,
            "json_mode": True,
            "embeddings": True,
            "async": True
        },
        "supported_models": [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ],
        "api_key_pattern": "^sk-(proj-)?[A-Za-z0-9]{20,}$",
        "api_key_prefix": "sk-"
    },
    {
        "provider_name": "anthropic",
        "provider_type": "llm",
        "display_name": "Anthropic",
        "description": "Anthropic Claude models for advanced reasoning and analysis",
        "icon_url": "https://cdn.promptforge.com/icons/anthropic.svg",
        "documentation_url": "https://docs.anthropic.com",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "placeholder": "sk-ant-...",
                "help_text": "Your Anthropic API key from https://console.anthropic.com",
                "required": True,
                "validation": {
                    "pattern": "^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$",
                    "min_length": 102
                }
            }
        ],
        "optional_fields": [
            {
                "name": "base_url",
                "type": "url",
                "label": "Base URL",
                "placeholder": "https://api.anthropic.com",
                "default": "https://api.anthropic.com"
            },
            {
                "name": "default_model",
                "type": "select",
                "label": "Default Model",
                "options": [
                    "claude-sonnet-4-5-20250929",
                    "claude-opus-4-1-20250805",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                "default": "claude-sonnet-4-5-20250929",
                "model_display_names": {
                    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
                    "claude-opus-4-1-20250805": "Claude Opus 4.1",
                    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
                    "claude-3-5-haiku-20241022": "Claude 3.5 Haiku",
                    "claude-3-opus-20240229": "Claude 3 Opus",
                    "claude-3-sonnet-20240229": "Claude 3 Sonnet",
                    "claude-3-haiku-20240307": "Claude 3 Haiku"
                },
                "pricing": {
                    "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015, "description": "Highest intelligence"},
                    "claude-opus-4-1-20250805": {"input": 0.015, "output": 0.075, "description": "Advanced reasoning"},
                    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015, "description": "Balanced performance"},
                    "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004, "description": "Fast and cost-effective"},
                    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075, "description": "Powerful reasoning"},
                    "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015, "description": "Balanced"},
                    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125, "description": "Ultra fast"}
                },
                "context_windows": {
                    "claude-sonnet-4-5-20250929": 200000,
                    "claude-opus-4-1-20250805": 200000,
                    "claude-3-5-sonnet-20241022": 200000,
                    "claude-3-5-haiku-20241022": 200000,
                    "claude-3-opus-20240229": 200000,
                    "claude-3-sonnet-20240229": 200000,
                    "claude-3-haiku-20240307": 200000
                }
            },
            {
                "name": "max_tokens",
                "type": "number",
                "label": "Max Tokens",
                "placeholder": "4096",
                "default": 4096
            }
        ],
        "capabilities": {
            "streaming": True,
            "function_calling": True,
            "vision": True,
            "json_mode": False,
            "embeddings": False,
            "async": True
        },
        "supported_models": [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-1-20250805",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "api_key_pattern": "^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$",
        "api_key_prefix": "sk-ant-"
    },
    {
        "provider_name": "cohere",
        "provider_type": "llm",
        "display_name": "Cohere",
        "description": "Cohere language models for generation, classification, and embeddings",
        "icon_url": "https://cdn.promptforge.com/icons/cohere.svg",
        "documentation_url": "https://docs.cohere.com",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "placeholder": "Your Cohere API key",
                "help_text": "Get your API key from https://dashboard.cohere.com",
                "required": True,
                "validation": {
                    "min_length": 32
                }
            }
        ],
        "optional_fields": [
            {
                "name": "default_model",
                "type": "select",
                "label": "Default Model",
                "options": ["command-r-plus", "command-r", "command"],
                "default": "command-r-plus"
            }
        ],
        "capabilities": {
            "streaming": True,
            "function_calling": True,
            "vision": False,
            "json_mode": False,
            "embeddings": True,
            "async": True
        },
        "supported_models": [
            "command-r-plus",
            "command-r",
            "command",
            "embed-english-v3.0",
            "embed-multilingual-v3.0"
        ],
        "api_key_pattern": None,
        "api_key_prefix": None
    },
    {
        "provider_name": "google",
        "provider_type": "llm",
        "display_name": "Google AI (Gemini)",
        "description": "Google's Gemini models for multimodal AI",
        "icon_url": "https://cdn.promptforge.com/icons/google.svg",
        "documentation_url": "https://ai.google.dev/docs",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "placeholder": "Your Google AI API key",
                "help_text": "Get your API key from https://makersuite.google.com",
                "required": True
            }
        ],
        "optional_fields": [
            {
                "name": "default_model",
                "type": "select",
                "label": "Default Model",
                "options": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
                "default": "gemini-1.5-pro"
            }
        ],
        "capabilities": {
            "streaming": True,
            "function_calling": True,
            "vision": True,
            "json_mode": True,
            "embeddings": True,
            "async": True
        },
        "supported_models": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "text-embedding-004"
        ],
        "api_key_pattern": None,
        "api_key_prefix": None
    },
    {
        "provider_name": "azure_openai",
        "provider_type": "llm",
        "display_name": "Azure OpenAI",
        "description": "OpenAI models hosted on Microsoft Azure",
        "icon_url": "https://cdn.promptforge.com/icons/azure.svg",
        "documentation_url": "https://learn.microsoft.com/azure/ai-services/openai",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Key",
                "placeholder": "Your Azure OpenAI API key",
                "required": True
            },
            {
                "name": "endpoint",
                "type": "url",
                "label": "Endpoint",
                "placeholder": "https://your-resource.openai.azure.com",
                "required": True
            },
            {
                "name": "api_version",
                "type": "string",
                "label": "API Version",
                "placeholder": "2024-02-01",
                "default": "2024-02-01",
                "required": True
            }
        ],
        "optional_fields": [
            {
                "name": "deployment_name",
                "type": "string",
                "label": "Deployment Name",
                "placeholder": "gpt-4-deployment"
            }
        ],
        "capabilities": {
            "streaming": True,
            "function_calling": True,
            "vision": True,
            "json_mode": True,
            "embeddings": True,
            "async": True
        },
        "supported_models": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-35-turbo",
            "text-embedding-ada-002"
        ],
        "api_key_pattern": None,
        "api_key_prefix": None
    },
    {
        "provider_name": "huggingface",
        "provider_type": "llm",
        "display_name": "HuggingFace",
        "description": "HuggingFace Inference API for open-source models",
        "icon_url": "https://cdn.promptforge.com/icons/huggingface.svg",
        "documentation_url": "https://huggingface.co/docs/api-inference",
        "required_fields": [
            {
                "name": "api_key",
                "type": "password",
                "label": "API Token",
                "placeholder": "hf_...",
                "help_text": "Your HuggingFace API token",
                "required": True,
                "validation": {
                    "pattern": "^hf_[A-Za-z0-9]{30,}$"
                }
            }
        ],
        "optional_fields": [
            {
                "name": "model_id",
                "type": "string",
                "label": "Model ID",
                "placeholder": "meta-llama/Llama-2-70b-chat-hf"
            }
        ],
        "capabilities": {
            "streaming": False,
            "function_calling": False,
            "vision": False,
            "json_mode": False,
            "embeddings": True,
            "async": True
        },
        "supported_models": [],  # Dynamic based on user's model_id
        "api_key_pattern": "^hf_[A-Za-z0-9]{30,}$",
        "api_key_prefix": "hf_"
    }
]


async def seed_provider_metadata():
    """Seed the model_provider_metadata table"""

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n🌱 Seeding model provider metadata...")

        for provider_data in PROVIDER_METADATA:
            # Check if provider already exists
            result = await session.execute(
                select(ModelProviderMetadata).where(
                    ModelProviderMetadata.provider_name == provider_data["provider_name"]
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⚠️  Provider '{provider_data['provider_name']}' already exists, updating...")
                # Update existing
                for key, value in provider_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                print(f"✅ Creating provider '{provider_data['provider_name']}'...")
                # Create new
                provider = ModelProviderMetadata(
                    id=uuid.uuid4(),
                    **provider_data,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(provider)

        await session.commit()
        print("\n✅ Model provider metadata seeded successfully!")

        # Print summary
        result = await session.execute(select(ModelProviderMetadata))
        all_providers = result.scalars().all()
        print(f"\n📊 Total providers in catalog: {len(all_providers)}")
        for provider in all_providers:
            print(f"  - {provider.display_name} ({provider.provider_name})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_provider_metadata())
