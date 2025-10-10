"""
Model Provider Metadata Seed Script

Run with: python scripts/seed_model_providers.py
"""
import asyncio
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
                "options": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
                "default": "gpt-4-turbo"
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
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
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
                    "pattern": "^sk-ant-[A-Za-z0-9-_]{95}$",
                    "min_length": 100
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
                    "claude-3-5-sonnet-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                "default": "claude-3-5-sonnet-20241022"
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
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "api_key_pattern": "^sk-ant-[A-Za-z0-9-_]{95}$",
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
        "supported_models": [],
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
