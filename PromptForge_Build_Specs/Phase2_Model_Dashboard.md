# Phase 2: Model Dashboard - Complete Specification

**Version:** 2.0 (Consolidated)
**Date:** October 9, 2025
**Status:** 🔧 **IMPLEMENTATION READY**
**Consolidates:** MODEL_PROVIDER_CONFIGURATION_SPEC.md + Phase2_Model_Dashboard.md

---

## Overview

The **Model Dashboard** in PromptForge provides administrators and developers with a unified interface to:
- Manage AI model providers (OpenAI, Anthropic, etc.)
- Securely store and manage API keys at organization and project levels
- Register model configurations with encryption at rest
- Analyze model usage across the platform
- Support **SaaS isolation**, **SOC2 compliance**, and centralized **model governance**

### Key Requirements

1. **Multi-Tenant Secure Storage** - Organization and project-level API key management
2. **Vendor-Neutral API** - Generic interface supporting all model providers
3. **Encryption at Rest** - Secure storage of API keys using Fernet encryption
4. **RBAC Integration** - Permission-based access to sensitive configurations
5. **UI-Friendly Metadata** - Provider capabilities, required fields, validation rules
6. **Audit Trail** - Track key creation, updates, rotation, and usage
7. **Backward Compatibility** - Maintain support for existing organization secrets (e.g., OpenAI keys)

---

## Database Schema Design

### Table: `model_provider_configs`

Stores model provider API keys and configuration per organization/project.

```sql
CREATE TABLE model_provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,  -- NULL for org-level

    -- Provider identification
    provider_name VARCHAR(100) NOT NULL,  -- openai, anthropic, cohere, etc.
    provider_type VARCHAR(50) NOT NULL,   -- llm, embedding, image, etc.
    display_name VARCHAR(255),            -- User-friendly name

    -- API credentials (encrypted)
    api_key_encrypted TEXT NOT NULL,      -- Encrypted API key
    api_key_hash VARCHAR(128) NOT NULL,   -- SHA-256 hash for validation (non-reversible)

    -- Additional configuration (encrypted JSON)
    config_encrypted TEXT,                -- Encrypted JSON: {api_base, version, etc.}

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,     -- Default provider for this type

    -- Usage tracking
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,

    -- Audit
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Constraints
    UNIQUE(organization_id, project_id, provider_name, provider_type),
    CHECK (provider_name != ''),
    CHECK (provider_type IN ('llm', 'embedding', 'image', 'audio', 'multimodal'))
);

CREATE INDEX idx_model_provider_org ON model_provider_configs(organization_id);
CREATE INDEX idx_model_provider_project ON model_provider_configs(organization_id, project_id);
CREATE INDEX idx_model_provider_active ON model_provider_configs(organization_id, is_active);
```

### Table: `model_provider_metadata`

Static metadata about supported providers (read-only, seeded data).

```sql
CREATE TABLE model_provider_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Provider identification
    provider_name VARCHAR(100) UNIQUE NOT NULL,  -- openai, anthropic, etc.
    provider_type VARCHAR(50) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Visual
    icon_url VARCHAR(500),
    documentation_url VARCHAR(500),

    -- Configuration schema (JSON)
    required_fields JSONB,  -- [{name, type, label, placeholder, validation}, ...]
    optional_fields JSONB,
    default_config JSONB,

    -- Capabilities
    capabilities JSONB,  -- {streaming: true, functions: true, vision: false, ...}
    supported_models JSONB,  -- ["gpt-4", "gpt-3.5-turbo", ...]

    -- Validation
    api_key_pattern VARCHAR(255),  -- Regex for API key format
    api_key_prefix VARCHAR(20),    -- e.g., "sk-" for OpenAI

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_provider_meta_type ON model_provider_metadata(provider_type);
CREATE INDEX idx_provider_meta_active ON model_provider_metadata(is_active);
```

---

## API Design - Vendor Neutral

### Endpoints

#### 1. List Supported Providers (Public Metadata)

```http
GET /api/v1/model-providers/catalog
```

**Response:**
```json
{
  "providers": [
    {
      "provider_name": "openai",
      "provider_type": "llm",
      "display_name": "OpenAI",
      "description": "OpenAI GPT models for text generation",
      "icon_url": "https://cdn.promptforge.com/icons/openai.svg",
      "documentation_url": "https://platform.openai.com/docs",
      "capabilities": {
        "streaming": true,
        "function_calling": true,
        "vision": true,
        "json_mode": true
      },
      "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
      "required_fields": [
        {
          "name": "api_key",
          "type": "password",
          "label": "API Key",
          "placeholder": "sk-...",
          "validation": {
            "pattern": "^sk-[A-Za-z0-9]{32,}$",
            "required": true
          }
        }
      ],
      "optional_fields": [
        {
          "name": "organization_id",
          "type": "string",
          "label": "Organization ID (optional)",
          "placeholder": "org-..."
        },
        {
          "name": "api_base",
          "type": "url",
          "label": "Custom API Base URL",
          "placeholder": "https://api.openai.com/v1"
        }
      ]
    },
    {
      "provider_name": "anthropic",
      "provider_type": "llm",
      "display_name": "Anthropic",
      "description": "Claude AI models",
      "required_fields": [
        {
          "name": "api_key",
          "type": "password",
          "label": "API Key",
          "placeholder": "sk-ant-...",
          "validation": {
            "pattern": "^sk-ant-[A-Za-z0-9-_]{30,}$",
            "required": true
          }
        }
      ]
    }
  ]
}
```

#### 2. Create Provider Configuration

```http
POST /api/v1/model-providers/configs
Authorization: Bearer {token}
```

**Request:**
```json
{
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Production OpenAI",
  "project_id": "uuid-optional",  // NULL for org-level
  "api_key": "sk-proj-...",
  "config": {
    "organization_id": "org-acme",
    "api_base": "https://api.openai.com/v1",
    "default_model": "gpt-4-turbo",
    "max_tokens": 4096
  },
  "is_default": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Production OpenAI",
  "project_id": null,
  "is_active": true,
  "is_default": true,
  "api_key_masked": "sk-proj-...xyz",
  "config": {
    "organization_id": "org-acme",
    "api_base": "https://api.openai.com/v1",
    "default_model": "gpt-4-turbo",
    "max_tokens": 4096
  },
  "created_at": "2025-10-09T12:00:00Z"
}
```

#### 3. List Configurations (for Organization/Project)

```http
GET /api/v1/model-providers/configs
  ?project_id={uuid-optional}
  &provider_type={llm|embedding}
  &is_active=true
Authorization: Bearer {token}
```

**Response:**
```json
{
  "configs": [
    {
      "id": "uuid",
      "provider_name": "openai",
      "provider_type": "llm",
      "display_name": "Production OpenAI",
      "is_active": true,
      "is_default": true,
      "api_key_masked": "sk-proj-...xyz",
      "config": {
        "organization_id": "org-acme",
        "default_model": "gpt-4-turbo"
      },
      "last_used_at": "2025-10-09T11:30:00Z",
      "usage_count": 142,
      "created_at": "2025-10-01T10:00:00Z"
    }
  ]
}
```

#### 4. Get Single Configuration

```http
GET /api/v1/model-providers/configs/{config_id}
Authorization: Bearer {token}
```

**Response:** Same as create response (API key masked)

#### 5. Update Configuration

```http
PUT /api/v1/model-providers/configs/{config_id}
Authorization: Bearer {token}
```

**Request:**
```json
{
  "display_name": "Updated OpenAI",
  "api_key": "sk-proj-new...",  // Optional - only if rotating
  "config": {
    "default_model": "gpt-4o"
  },
  "is_active": true,
  "is_default": false
}
```

#### 6. Delete Configuration

```http
DELETE /api/v1/model-providers/configs/{config_id}
Authorization: Bearer {token}
```

#### 7. Test Configuration

```http
POST /api/v1/model-providers/configs/{config_id}/test
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "provider": "openai",
  "test_result": {
    "connection": "successful",
    "models_available": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
    "latency_ms": 245
  }
}
```

#### 8. Get Models List

```http
GET /api/v1/models
  ?provider={provider_name}
  &type={text|code|vision|multimodal}
  &page=1
  &page_size=20
Authorization: Bearer {token}
```

**Response:**
```json
{
  "models": [
    {
      "model_id": "claude-3-opus",
      "provider": "Anthropic",
      "type": "text",
      "context_length": 200000,
      "latency_ms": 820,
      "cost_usd_per_1k": 0.015,
      "last_used": "2025-10-09T13:05:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

#### 9. Get Model Analytics

```http
GET /api/v1/models/analytics
  ?start_date={ISO-8601}
  &end_date={ISO-8601}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "top_models": [
    {
      "model_name": "gpt-4-turbo",
      "provider": "OpenAI",
      "total_tokens": 5234567,
      "total_cost": 78.52,
      "avg_latency_ms": 342,
      "eval_count": 1523
    }
  ],
  "cost_breakdown": {
    "openai": 78.52,
    "anthropic": 45.33
  },
  "usage_over_time": [
    {
      "date": "2025-10-01",
      "tokens": 123456,
      "cost": 1.85
    }
  ]
}
```

---

## Encryption Strategy

### Fernet Encryption (Symmetric)

```python
from cryptography.fernet import Fernet
import base64
import hashlib

class ModelProviderEncryption:
    """Encryption service for model provider API keys"""

    def __init__(self, encryption_key: str):
        # Derive Fernet key from encryption_key
        key_bytes = encryption_key.encode()
        hashed = hashlib.sha256(key_bytes).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(hashed))

    def encrypt_api_key(self, api_key: str) -> tuple[str, str]:
        """
        Encrypt API key and generate hash

        Returns:
            (encrypted_key, key_hash)
        """
        encrypted = self.fernet.encrypt(api_key.encode()).decode()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return encrypted, key_hash

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()

    def mask_api_key(self, api_key: str, show_chars: int = 3) -> str:
        """
        Mask API key for display

        Example: sk-proj-abc...xyz
        """
        if len(api_key) <= show_chars * 2:
            return "*" * len(api_key)

        prefix = api_key[:show_chars + api_key.find('-') + 1] if '-' in api_key else api_key[:show_chars]
        suffix = api_key[-show_chars:]
        return f"{prefix}...{suffix}"
```

### Configuration in Settings

```python
# app/core/config.py

class Settings(BaseSettings):
    # ...existing settings...

    # Model Provider Encryption
    MODEL_PROVIDER_ENCRYPTION_KEY: str = Field(
        ...,
        description="Encryption key for model provider API keys (32+ chars)"
    )

    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Permission Model

### Required Permissions

```python
class ModelProviderPermissions:
    """RBAC permissions for model provider management"""

    # View configurations (masked API keys)
    VIEW_MODEL_CONFIGS = "model_providers:view"

    # Create new configurations
    CREATE_MODEL_CONFIGS = "model_providers:create"

    # Update existing configurations (including API key rotation)
    UPDATE_MODEL_CONFIGS = "model_providers:update"

    # Delete configurations
    DELETE_MODEL_CONFIGS = "model_providers:delete"

    # View actual API keys (super sensitive)
    VIEW_API_KEYS = "model_providers:view_keys"

    # Test configurations
    TEST_MODEL_CONFIGS = "model_providers:test"
```

### Permission Matrix

| Role | View | Create | Update | Delete | View Keys | Test |
|------|------|--------|--------|--------|-----------|------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Developer** | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Viewer** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## UI/UX Design

### Provider List View

```
┌─────────────────────────────────────────────────────────────┐
│ Model Providers                          [+ Add Provider]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Provider    Display Name          API Key       Status      │
│  ─────────   ──────────────────   ──────────    ─────────   │
│  [OpenAI]    Production OpenAI    sk-...xyz     ✓ Active    │
│  [Anthropic] Claude Dev            sk-ant-...    ✓ Active    │
│  [Cohere]    Embeddings            co-...abc     ○ Inactive  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Add Provider Modal

**Component Structure:**
```typescript
interface ProviderConfigFormProps {
  provider: ProviderMetadata;
  existingConfig?: ModelProviderConfig;
  onSave: (config: ConfigData) => Promise<void>;
}

// Example: OpenAI Configuration
{
  provider: "openai",
  fields: [
    {
      name: "api_key",
      type: "password",
      label: "OpenAI API Key",
      placeholder: "sk-proj-...",
      required: true,
      helpText: "Get your API key from platform.openai.com",
      validation: {
        pattern: /^sk-[A-Za-z0-9]{32,}$/,
        message: "Invalid OpenAI API key format"
      }
    },
    {
      name: "organization_id",
      type: "text",
      label: "Organization ID (Optional)",
      placeholder: "org-...",
      required: false
    },
    {
      name: "default_model",
      type: "select",
      label: "Default Model",
      options: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
      default: "gpt-4-turbo"
    }
  ]
}
```

### Model List View

**Table Columns:**
| Field | Description |
|--------|--------------|
| **Model Name** | Model ID (e.g., claude-3-opus) |
| **Provider** | Source provider |
| **Type** | Text / Code / Vision / Multimodal |
| **Context Length** | Max tokens |
| **Latency (ms)** | Avg latency |
| **Cost ($/1K tokens)** | Estimated usage cost |
| **Last Used** | Timestamp from traces |

**Features:**
- Search by model name
- Filter by provider, type
- Sort by any column
- Pagination (20 per page)

### Model Analytics Tab

**Charts:**
1. **Top Models by Token Usage** — Bar chart
2. **Cost Breakdown by Model** — Pie chart
3. **Latency Over Time** — Line chart

**Data Source:**
Aggregated from trace logs and evaluation metrics.

---

## Security Considerations

### 1. Encryption at Rest
- ✅ API keys encrypted using Fernet (AES-128)
- ✅ Encryption key stored in environment variable
- ✅ Keys never stored in plaintext

### 2. API Key Masking
- ✅ API keys masked in all API responses
- ✅ Only show prefix and suffix (e.g., `sk-proj-...xyz`)
- ✅ Full keys only available via dedicated endpoint with elevated permissions

### 3. Audit Trail
- ✅ Track who created/updated configurations
- ✅ Track last usage time and count
- ✅ Log all API key rotations

### 4. Key Rotation
- ✅ Support updating API keys without breaking existing configs
- ✅ Validate new keys before saving
- ✅ Optional: Store previous key hash for rotation detection

### 5. Scope Isolation
- ✅ Organization-level configs (shared across projects)
- ✅ Project-level configs (project-specific)
- ✅ Project configs override org configs

---

## Migration Path & Backward Compatibility

### Phase 1: Environment Variables → Database

**Current State:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Future State:**
```sql
INSERT INTO model_provider_configs (provider_name, api_key_encrypted, ...)
VALUES ('openai', encrypt('sk-...'), ...);
```

### Backward Compatibility Strategy

**Critical Requirement:** Maintain support for existing organization secrets (e.g., OpenAI keys) that are currently running multiple prompts and insights.

```python
def get_api_key(provider: str, org_id: UUID, project_id: Optional[UUID] = None):
    """
    Get API key with fallback hierarchy:
    1. Try database (project-specific)
    2. Try database (org-level)
    3. Fallback to environment variable (backward compatibility)
    """
    # 1. Try database (project-specific)
    if project_id:
        config = get_config(org_id, project_id, provider)
        if config:
            return decrypt(config.api_key_encrypted)

    # 2. Try database (org-level)
    config = get_config(org_id, None, provider)
    if config:
        return decrypt(config.api_key_encrypted)

    # 3. Fallback to environment variable (backward compatibility)
    env_key = os.getenv(f"{provider.upper()}_API_KEY")
    if env_key:
        logger.warning(
            f"Using environment variable for {provider}. "
            f"Migrate to database for better security."
        )
        return env_key

    raise ValueError(f"No API key found for provider: {provider}")
```

**Migration Steps:**
1. ✅ Deploy new model provider tables
2. ✅ Seed provider metadata
3. ✅ Keep environment variables in place
4. ✅ Add UI for users to migrate keys to database
5. ✅ Monitor usage of environment vs database keys
6. 🔜 Deprecate environment variables after 90 days

---

## Testing Strategy

### Unit Tests
- ✅ Encryption/decryption
- ✅ API key masking
- ✅ Validation rules
- ✅ Permission checks

### Integration Tests
- ✅ CRUD operations
- ✅ Multi-tenancy isolation
- ✅ Default provider selection
- ✅ API key rotation
- ✅ Backward compatibility with environment variables

### End-to-End Tests
- ✅ Provider configuration workflow
- ✅ Multiple providers
- ✅ Project vs org-level configs
- ✅ Existing prompts continue to work with environment keys

---

## Deployment Checklist

### Database
1. ✅ Create Alembic migration for model provider tables
2. ✅ Run migration in development environment
3. ✅ Seed provider metadata (OpenAI, Anthropic, etc.)
4. ✅ Verify backward compatibility with existing secrets

### API
1. ✅ Implement encryption service
2. ✅ Implement API endpoints
3. ✅ Add RBAC permissions
4. ✅ Test with existing environment variables
5. ✅ Test API key rotation

### UI
1. ✅ Create mfe-models micro-frontend
2. ✅ Implement Provider List view
3. ✅ Implement Add/Edit Provider modal
4. ✅ Implement Model List view
5. ✅ Implement Model Analytics tab
6. ✅ Integrate into shell application

### Testing
1. ✅ Run full test suite
2. ✅ Verify backward compatibility
3. ✅ Test encryption/decryption
4. ✅ Test RBAC permissions
5. ✅ E2E testing with real providers

---

## Next Steps

1. ✅ Create Alembic migration
2. ✅ Implement SQLAlchemy models
3. ✅ Create encryption service
4. ✅ Implement API endpoints
5. ✅ Seed provider metadata
6. ✅ Add RBAC permissions
7. ✅ Build UI components
8. ✅ Test with existing organization secrets
9. ✅ Deploy to staging
10. ✅ Production rollout

---

**Specification Version:** 2.0 (Consolidated)
**Date:** October 9, 2025
**Status:** Implementation Ready
**Backward Compatibility:** ✅ Maintained
