# PromptForge API Reference

**Version**: 1.0
**Base URL**: `/api/v1`
**Last Updated**: 2025-10-12

## Table of Contents

1. [Authentication](#authentication)
2. [Core Resources](#core-resources)
3. [Advanced Features](#advanced-features)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Best Practices](#best-practices)

---

## Authentication

All API endpoints (except authentication endpoints) require JWT Bearer token authentication.

### Login

**Endpoint**: `POST /api/v1/auth/login`

**Description**: Authenticate user and receive JWT tokens.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `401 Unauthorized`: Inactive user

**Security Notes**:
- Access token expires in 30 minutes (configurable)
- Refresh token expires in 7 days (configurable)
- Tokens include organization context for SOC 2 compliance

### Refresh Token

**Endpoint**: `POST /api/v1/auth/refresh`

**Description**: Obtain new access and refresh tokens using a valid refresh token.

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token
- `401 Unauthorized`: Invalid or inactive user

### Using Authentication

Include the access token in the `Authorization` header for all authenticated requests:

```bash
curl -H "Authorization: Bearer <access_token>" \
  https://api.promptforge.com/api/v1/projects
```

---

## Core Resources

### Organizations

#### Get Current Organization

**Endpoint**: `GET /api/v1/organizations/me`

**Description**: Retrieve the current user's organization details.

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corp",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Authentication**: Required
**Rate Limit**: 100 requests/minute

---

### Projects

Projects are containers for prompts, traces, and evaluations. All projects are organization-scoped.

#### Create Project

**Endpoint**: `POST /api/v1/projects`

**Description**: Create a new project within the current user's organization.

**Request Body**:
```json
{
  "name": "Customer Support Bot",
  "description": "AI-powered customer support automation",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active"
}
```

**Response**: `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Customer Support Bot",
  "description": "AI-powered customer support automation",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "created_by": "770e8400-e29b-41d4-a716-446655440002",
  "created_at": "2025-01-20T14:22:00Z",
  "updated_at": "2025-01-20T14:22:00Z"
}
```

**Error Responses**:
- `403 Forbidden`: Attempting to create project for different organization
- `422 Unprocessable Entity`: Invalid request body

#### Get Project

**Endpoint**: `GET /api/v1/projects/{project_id}`

**Description**: Retrieve a project by ID. Users can only access projects within their organization.

**Path Parameters**:
- `project_id` (UUID): Project identifier

**Response**: `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Customer Support Bot",
  "description": "AI-powered customer support automation",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "created_by": "770e8400-e29b-41d4-a716-446655440002",
  "created_at": "2025-01-20T14:22:00Z",
  "updated_at": "2025-01-20T14:22:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Project not found or access denied

#### Update Project

**Endpoint**: `PATCH /api/v1/projects/{project_id}`

**Description**: Update project metadata. Only updatable fields are modified.

**Request Body** (all fields optional):
```json
{
  "name": "Enhanced Support Bot",
  "description": "AI-powered support with sentiment analysis",
  "status": "active"
}
```

**Response**: `200 OK` (same as Get Project)

**Error Responses**:
- `404 Not Found`: Project not found or access denied

#### Delete Project

**Endpoint**: `DELETE /api/v1/projects/{project_id}`

**Description**: Permanently delete a project and all associated prompts, traces, and evaluations (cascade delete).

**Response**: `204 No Content`

**Error Responses**:
- `404 Not Found`: Project not found or access denied

**Warning**: This operation is irreversible. All child resources will be deleted.

#### List Projects

**Endpoint**: `GET /api/v1/projects`

**Description**: List all projects for the current organization with pagination and filtering.

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100, max: 100): Number of records to return
- `status_filter` (string, optional): Filter by status

**Response**: `200 OK`
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Customer Support Bot",
    "description": "AI-powered customer support automation",
    "organization_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "active",
    "created_by": "770e8400-e29b-41d4-a716-446655440002",
    "created_at": "2025-01-20T14:22:00Z",
    "updated_at": "2025-01-20T14:22:00Z"
  }
]
```

---

### Model Providers

Manage AI model provider configurations with encrypted API keys.

#### List Provider Catalog

**Endpoint**: `GET /api/v1/model-providers/catalog`

**Description**: Get list of all supported model providers with metadata and configuration requirements.

**Query Parameters**:
- `provider_type` (string, optional): Filter by provider type (e.g., "llm", "embedding")
- `is_active` (boolean, default: true): Filter by active status

**Response**: `200 OK`
```json
{
  "providers": [
    {
      "provider_name": "openai",
      "provider_type": "llm",
      "display_name": "OpenAI",
      "description": "OpenAI GPT models",
      "is_active": true,
      "required_fields": ["api_key"],
      "optional_fields": [
        {
          "name": "default_model",
          "type": "string",
          "options": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
          "default": "gpt-4o-mini",
          "pricing": {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006}
          },
          "context_windows": {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000
          }
        }
      ],
      "capabilities": ["chat", "functions", "streaming"]
    }
  ],
  "total": 5
}
```

**Authentication**: Not required
**Use Case**: Render provider configuration forms in UI

#### Create Provider Configuration

**Endpoint**: `POST /api/v1/model-providers/configs`

**Description**: Create a new model provider configuration with encrypted API key storage.

**Request Body**:
```json
{
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Production OpenAI",
  "api_key": "sk-proj-...",
  "config": {
    "default_model": "gpt-4o-mini",
    "organization": "org-..."
  },
  "project_id": null,
  "is_active": true,
  "is_default": true
}
```

**Response**: `201 Created`
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": null,
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Production OpenAI",
  "api_key_masked": "sk-proj-...XXXX",
  "config": {
    "default_model": "gpt-4o-mini",
    "organization": "org-..."
  },
  "is_active": true,
  "is_default": true,
  "usage_count": 0,
  "last_used_at": null,
  "created_at": "2025-02-01T09:15:00Z",
  "updated_at": "2025-02-01T09:15:00Z"
}
```

**Security Notes**:
- **Requires ADMIN role**
- API key encrypted with AES-128 (Fernet)
- Only masked API key returned in response
- All operations logged for audit trail

**Error Responses**:
- `400 Bad Request`: Provider not found or inactive
- `403 Forbidden`: Insufficient permissions (requires ADMIN)
- `409 Conflict`: Configuration already exists

#### List Provider Configurations

**Endpoint**: `GET /api/v1/model-providers/configs`

**Description**: List all provider configurations for the current organization.

**Query Parameters**:
- `project_id` (UUID, optional): Filter by project (null for org-level configs)
- `provider_type` (string, optional): Filter by provider type
- `is_active` (boolean, optional): Filter by active status

**Response**: `200 OK`
```json
{
  "configs": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "organization_id": "550e8400-e29b-41d4-a716-446655440000",
      "project_id": null,
      "provider_name": "openai",
      "provider_type": "llm",
      "display_name": "Production OpenAI",
      "api_key_masked": "sk-proj-...XXXX",
      "config": {"default_model": "gpt-4o-mini"},
      "is_active": true,
      "is_default": true,
      "usage_count": 1245,
      "last_used_at": "2025-02-10T15:30:00Z",
      "created_at": "2025-02-01T09:15:00Z",
      "updated_at": "2025-02-01T09:15:00Z"
    }
  ],
  "total": 3
}
```

#### Update Provider Configuration

**Endpoint**: `PUT /api/v1/model-providers/configs/{config_id}`

**Description**: Update provider configuration. Supports API key rotation and partial updates.

**Request Body** (all fields optional):
```json
{
  "display_name": "Production OpenAI (Updated)",
  "api_key": "sk-proj-NEW...",
  "config": {"default_model": "gpt-4o"},
  "is_active": true,
  "is_default": true
}
```

**Response**: `200 OK` (same as Get Configuration)

**Security Notes**:
- **Requires ADMIN role**
- API key rotation logged for audit
- Only provided fields are updated

#### Delete Provider Configuration

**Endpoint**: `DELETE /api/v1/model-providers/configs/{config_id}`

**Description**: Permanently delete a provider configuration and encrypted credentials.

**Response**: `204 No Content`

**Security Notes**:
- **Requires ADMIN role**
- Deletion logged for audit trail
- Secure deletion of encrypted credentials

#### Test Provider Configuration

**Endpoint**: `POST /api/v1/model-providers/configs/{config_id}/test`

**Description**: Test provider configuration by attempting connection and validating credentials.

**Request Body**:
```json
{
  "test_model": "gpt-3.5-turbo"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "provider": "openai",
  "test_result": {
    "connection": "successful",
    "models_available": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
    "test_model": "gpt-3.5-turbo"
  },
  "error": null
}
```

**Error Response**: `200 OK` (with error details)
```json
{
  "success": false,
  "provider": "openai",
  "test_result": {
    "error_details": "Invalid API key"
  },
  "error": "Authentication failed"
}
```

---

### Models

Aggregate view of available models across all configured providers.

#### Get Available Models

**Endpoint**: `GET /api/v1/models/available`

**Description**: Get list of models available to the current organization based on configured provider API keys.

**Response**: `200 OK`
```json
[
  {
    "model_id": "gpt-4o-mini",
    "display_name": "GPT-4o Mini",
    "provider": "OpenAI",
    "description": "Affordable and intelligent small model",
    "input_cost": 0.00015,
    "output_cost": 0.0006,
    "context_window": 128000
  },
  {
    "model_id": "claude-sonnet-4-5-20250929",
    "display_name": "Claude 4.5 Sonnet",
    "provider": "Anthropic",
    "description": "Most intelligent Claude model",
    "input_cost": 0.015,
    "output_cost": 0.075,
    "context_window": 200000
  }
]
```

**Use Case**: Populate model dropdowns in Playground, Insights, and Evaluation UIs

**Note**: Only returns models from providers with active API key configurations

---

## Advanced Features

### Playground

Execute prompts with live model integration and evaluation.

#### Execute Prompt

**Endpoint**: `POST /api/v1/playground/execute`

**Description**: Execute a prompt using a live model API with full tracing and optional evaluations.

**Request Body**:
```json
{
  "title": "Product Description Test",
  "prompt": "Write a product description for wireless earbuds",
  "system_prompt": "You are a creative product copywriter",
  "model": "gpt-4o-mini",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9,
    "top_k": 40
  },
  "metadata": {
    "intent": "product_copy",
    "tone": "professional"
  },
  "evaluation_ids": [
    "eval-001",
    "eval-002"
  ]
}
```

**Response**: `200 OK`
```json
{
  "response": "Discover crystal-clear audio with our premium wireless earbuds...",
  "metrics": {
    "latency_ms": 1245.5,
    "tokens_used": 425,
    "cost": 0.00032
  },
  "trace_id": "trace-990e8400-e29b-41d4-a716-446655440005",
  "model": "gpt-4o-mini",
  "timestamp": "2025-02-15T10:45:00Z"
}
```

**Features**:
- Live model execution via organization's API key
- Automatic trace creation for observability
- Optional evaluation execution on response
- Cost tracking with accurate token counts

**Error Responses**:
- `500 Internal Server Error`: Model execution failed
  - Creates error trace with zero cost
  - Returns user-friendly error message
  - Logs full error details for debugging

---

### Call Insights

3-stage Dynamic Temperature Adjustment (DTA) pipeline for call transcript analysis.

#### Analyze Call Transcript

**Endpoint**: `POST /api/v1/call-insights/analyze`

**Description**: Analyze call transcript with multi-stage LLM processing.

**Request Body**:
```json
{
  "transcript": "Customer: I'm having issues with my order...",
  "transcript_title": "Customer Service Call - Order #12345",
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "enable_pii_redaction": false,
  "stage_params": {
    "fact_extraction": {
      "temperature": 0.25,
      "top_p": 0.95,
      "max_tokens": 1000
    },
    "reasoning": {
      "temperature": 0.65,
      "top_p": 0.95,
      "max_tokens": 1500
    },
    "summary": {
      "temperature": 0.45,
      "top_p": 0.95,
      "max_tokens": 800
    }
  },
  "system_prompts": {
    "stage1_fact_extraction": "Extract key facts from the call...",
    "stage2_reasoning": "Analyze the customer sentiment...",
    "stage3_summary": "Provide actionable summary..."
  },
  "models": {
    "stage1_model": "gpt-4o-mini",
    "stage2_model": "gpt-4o",
    "stage3_model": "gpt-4o-mini"
  },
  "evaluations": ["eval-001"]
}
```

**Response**: `200 OK`
```json
{
  "analysis_id": "analysis-123",
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "summary": "Customer expressed frustration about delayed order...",
  "insights": "Key insight: Order tracking needs improvement...",
  "facts": "Order #12345, placed 5 days ago, status: processing...",
  "pii_redacted": false,
  "traces": [
    {
      "trace_id": "trace-stage1",
      "stage": "Stage 1: Fact Extraction",
      "model": "gpt-4o-mini",
      "temperature": 0.25,
      "top_p": 0.95,
      "max_tokens": 1000,
      "input_tokens": 450,
      "output_tokens": 320,
      "total_tokens": 770,
      "duration_ms": 1200,
      "cost": 0.00025,
      "system_prompt": "Extract key facts..."
    }
  ],
  "evaluations": [
    {
      "evaluation_name": "Groundedness Check",
      "evaluation_uuid": "eval-001",
      "score": 0.92,
      "passed": true,
      "reason": "All facts supported by transcript",
      "threshold": 0.8,
      "category": "Honest",
      "input_tokens": 500,
      "output_tokens": 150,
      "total_tokens": 650,
      "evaluation_cost": 0.0001
    }
  ],
  "total_tokens": 3500,
  "total_cost": 0.0125,
  "created_at": "2025-02-20T14:30:00Z"
}
```

**Pipeline Stages**:
1. **Stage 1 (temp=0.25)**: Fact extraction with high precision
2. **Stage 2 (temp=0.65)**: Reasoning and insights with creativity
3. **Stage 3 (temp=0.45)**: Summary synthesis with balance

**Features**:
- Optional PII redaction with Presidio
- Customizable parameters per stage
- Custom system prompts per stage
- Model selection per stage
- Automatic trace hierarchy (parent + 3 child traces)
- Optional evaluation execution

#### Get Analysis History

**Endpoint**: `GET /api/v1/call-insights/history`

**Description**: List previous call insights analyses with filtering and search.

**Query Parameters**:
- `project_id` (UUID, optional): Filter by project
- `search` (string, optional): Search in title or transcript text
- `limit` (integer, default: 10, max: 100): Results per page
- `offset` (integer, default: 0): Pagination offset

**Response**: `200 OK`
```json
[
  {
    "id": "analysis-123",
    "transcript_title": "Customer Service Call - Order #12345",
    "transcript_preview": "Customer: I'm having issues with my order...",
    "project_id": "660e8400-e29b-41d4-a716-446655440001",
    "total_tokens": 3500,
    "total_cost": 0.0125,
    "pii_redacted": false,
    "created_at": "2025-02-20T14:30:00Z"
  }
]
```

#### Get Analysis by ID

**Endpoint**: `GET /api/v1/call-insights/{analysis_id}`

**Description**: Retrieve full analysis details including all stage outputs.

**Response**: `200 OK`
```json
{
  "id": "analysis-123",
  "transcript_title": "Customer Service Call - Order #12345",
  "transcript_input": "Customer: I'm having issues...",
  "summary_output": "Customer expressed frustration...",
  "insights_output": "Key insight: Order tracking...",
  "facts_output": "Order #12345, placed 5 days ago...",
  "pii_redacted": false,
  "total_tokens": 3500,
  "total_cost": 0.0125,
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "system_prompt_stage1": "Extract key facts...",
  "system_prompt_stage2": "Analyze sentiment...",
  "system_prompt_stage3": "Provide summary...",
  "model_stage1": "gpt-4o-mini",
  "model_stage2": "gpt-4o",
  "model_stage3": "gpt-4o-mini",
  "analysis_metadata": {
    "stage_params": {...},
    "evaluations_run": 1
  },
  "created_at": "2025-02-20T14:30:00Z"
}
```

#### Update Analysis Title

**Endpoint**: `PATCH /api/v1/call-insights/{analysis_id}/title`

**Description**: Rename an analysis for better organization and searchability.

**Request Body**:
```json
{
  "transcript_title": "Customer Escalation - Order Issue"
}
```

**Response**: `200 OK` (same as Get Analysis by ID)

---

### Insight Comparison

Blind judge evaluation to compare two Call Insights analyses.

#### Create Comparison

**Endpoint**: `POST /api/v1/insights/comparisons`

**Description**: Create blind comparison between two analyses using a judge model.

**Request Body**:
```json
{
  "analysis_a_id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_b_id": "550e8400-e29b-41d4-a716-446655440001",
  "judge_model": "claude-sonnet-4-5-20250929",
  "judge_temperature": 0.0,
  "evaluation_criteria": [
    "groundedness",
    "faithfulness",
    "completeness",
    "clarity",
    "accuracy"
  ]
}
```

**Validation**:
- Both analyses must exist in same organization
- Both analyses must use same transcript
- Judge model must be available
- Duplicate comparisons (same analyses + same judge) blocked

**Response**: `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "organization_id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": "880e8400-e29b-41d4-a716-446655440000",
  "analysis_a": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "transcript_title": "Customer Call - Q3 2025",
    "model_stage1": "gpt-4o-mini",
    "model_stage2": "gpt-4o-mini",
    "model_stage3": "gpt-4o-mini",
    "total_tokens": 3500,
    "total_cost": 0.0012,
    "created_at": "2025-10-10T14:20:00Z"
  },
  "analysis_b": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "transcript_title": "Customer Call - Q3 2025",
    "model_stage1": "gpt-4o",
    "model_stage2": "gpt-4o",
    "model_stage3": "gpt-4o",
    "total_tokens": 3600,
    "total_cost": 0.0180,
    "created_at": "2025-10-10T14:25:00Z"
  },
  "judge_model": "claude-sonnet-4-5-20250929",
  "evaluation_criteria": [
    "groundedness",
    "faithfulness",
    "completeness",
    "clarity",
    "accuracy"
  ],
  "overall_winner": "B",
  "overall_reasoning": "Model B outperforms by 19.4% overall...",
  "stage_results": [
    {
      "stage": "Stage 1: Fact Extraction",
      "winner": "B",
      "scores": {
        "A": {
          "groundedness": 0.82,
          "faithfulness": 0.85,
          "completeness": 0.78,
          "clarity": 0.88,
          "accuracy": 0.80
        },
        "B": {
          "groundedness": 0.95,
          "faithfulness": 0.93,
          "completeness": 0.90,
          "clarity": 0.89,
          "accuracy": 0.94
        }
      },
      "reasoning": "Model B extracted more comprehensive facts..."
    }
  ],
  "judge_trace": {
    "trace_id": "990e8400-e29b-41d4-a716-446655440000",
    "model": "claude-sonnet-4-5-20250929",
    "total_tokens": 8500,
    "cost": 0.0255,
    "duration_ms": 4200
  },
  "created_at": "2025-10-10T14:30:00Z"
}
```

**Judge Process**:
1. Blind evaluation (judge doesn't know which model is A or B)
2. Per-stage scoring on 5 criteria (0.0-1.0 scale)
3. Overall winner determination with cost-benefit analysis
4. Detailed reasoning for each stage and overall verdict

**Error Responses**:
- `404 Not Found`: Analysis not found
- `403 Forbidden`: Analyses from different organizations
- `422 Unprocessable Entity`: Different transcripts
- `409 Conflict`: Duplicate comparison exists

#### List Comparisons

**Endpoint**: `GET /api/v1/insights/comparisons`

**Description**: List all comparisons for current organization with pagination.

**Query Parameters**:
- `skip` (integer, default: 0): Pagination offset
- `limit` (integer, default: 20, max: 100): Results per page

**Response**: `200 OK`
```json
{
  "comparisons": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "analysis_a_title": "Customer Call - Q3 2025",
      "analysis_b_title": "Customer Call - Q3 2025",
      "model_a_summary": "gpt-4o-mini (all stages)",
      "model_b_summary": "gpt-4o (all stages)",
      "model_a_stage1": "gpt-4o-mini",
      "model_a_stage2": "gpt-4o-mini",
      "model_a_stage3": "gpt-4o-mini",
      "params_a": {"temperature": 0.25},
      "model_b_stage1": "gpt-4o",
      "model_b_stage2": "gpt-4o",
      "model_b_stage3": "gpt-4o",
      "params_b": {"temperature": 0.25},
      "cost_a": 0.0012,
      "cost_b": 0.0180,
      "tokens_a": 3500,
      "tokens_b": 3600,
      "judge_model": "claude-sonnet-4-5-20250929",
      "overall_winner": "B",
      "cost_difference": "+$0.0168",
      "quality_improvement": "+19.4%",
      "created_at": "2025-10-10T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 45,
    "total_pages": 3
  }
}
```

#### Get Comparison by ID

**Endpoint**: `GET /api/v1/insights/comparisons/{comparison_id}`

**Description**: Retrieve detailed comparison results.

**Response**: `200 OK` (same as Create Comparison response)

**Error Responses**:
- `404 Not Found`: Comparison not found
- `403 Forbidden`: Access denied (different organization)

#### Delete Comparison

**Endpoint**: `DELETE /api/v1/insights/comparisons/{comparison_id}`

**Description**: Permanently delete a comparison. Original analyses are not affected.

**Response**: `204 No Content`

**Error Responses**:
- `404 Not Found`: Comparison not found
- `403 Forbidden`: Access denied (different organization)

---

### Evaluations

#### List Evaluation Results

**Endpoint**: `GET /api/v1/evaluations/list`

**Description**: List evaluation results with advanced filtering and sorting.

**Query Parameters**:
- `limit` (integer, default: 20, max: 100): Results per page
- `offset` (integer, default: 0): Pagination offset
- `trace_id` (UUID, optional): Filter by trace
- `name` (string, optional): Filter by evaluation name (fuzzy search)
- `type` (string, optional): Filter by type (vendor | promptforge | custom)
- `model` (string, optional): Filter by model name
- `prompt_title` (string, optional): Filter by prompt title
- `vendor` (string, optional): Filter by vendor name
- `category` (string, optional): Filter by category (Helpful, Honest, Harmless)
- `status_filter` (string, optional): Filter by status (pass, fail)
- `created_after` (datetime, optional): Filter by creation date
- `created_before` (datetime, optional): Filter by creation date
- `sort_by` (string, default: "timestamp"): Sort column
- `sort_direction` (string, default: "desc"): Sort direction (asc, desc)

**Response**: `200 OK`
```json
{
  "evaluations": [
    {
      "id": "eval-result-001",
      "name": "Groundedness Check",
      "description": "Verifies response is grounded in facts",
      "type": "vendor",
      "status": "completed",
      "trace_id": "trace-990e8400-e29b-41d4-a716-446655440005",
      "trace_identifier": "playground-exec-123",
      "project_id": "660e8400-e29b-41d4-a716-446655440001",
      "prompt_title": "Product Description Test",
      "model": "gpt-4o-mini",
      "vendor_name": "OpenAI",
      "category": "Honest",
      "avg_score": 0.92,
      "passed": true,
      "total_tests": 1,
      "passed_tests": 1,
      "total_tokens": 650,
      "total_cost": 0.0001,
      "duration_ms": 850.5,
      "created_at": "2025-02-15T10:46:00Z"
    }
  ],
  "total": 125,
  "limit": 20,
  "offset": 0
}
```

**Sort Options**:
- `timestamp`: Most recent first (default)
- `score`: Highest/lowest scores
- `evaluation_name`: Alphabetical
- `category`: By category
- `prompt_title`: By prompt
- `model`: By model

#### Run Evaluations

**Endpoint**: `POST /api/v1/evaluations/run`

**Description**: Execute one or more evaluations on a trace.

**Request Body**:
```json
{
  "trace_id": "trace-990e8400-e29b-41d4-a716-446655440005",
  "evaluation_ids": [
    "eval-cat-001",
    "eval-cat-002"
  ],
  "model_override": "gpt-4o-mini"
}
```

**Response**: `200 OK`
```json
[
  {
    "evaluation_id": "eval-cat-001",
    "evaluation_name": "Groundedness Check",
    "trace_id": "trace-990e8400-e29b-41d4-a716-446655440005",
    "score": 0.92,
    "passed": true,
    "reason": "All facts supported by context",
    "metadata": {
      "model_used": "gpt-4o-mini",
      "tokens_used": 650
    },
    "status": "completed",
    "error_message": null
  }
]
```

**Features**:
- Executes multiple evaluations in parallel
- Creates child traces for each evaluation
- Stores results in trace_evaluations table
- Optional model override for all evaluations

**Error Responses**:
- `404 Not Found`: Trace or evaluation not found
- `500 Internal Server Error`: Evaluation execution failed

#### Get Evaluation Detail

**Endpoint**: `GET /api/v1/evaluations/{evaluation_id}/detail`

**Description**: Get comprehensive evaluation details with full trace context.

**Response**: `200 OK`
```json
{
  "id": "eval-result-001",
  "trace_id": "trace-990e8400-e29b-41d4-a716-446655440005",
  "trace_identifier": "playground-exec-123",
  "prompt_title": "Product Description Test",
  "model_name": "gpt-4o-mini",
  "project_name": "Customer Support Bot",
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "created_at": "2025-02-15T10:46:00Z",
  "evaluation_name": "Groundedness Check",
  "evaluation_type": "llm_judge",
  "vendor_name": "OpenAI",
  "category": "Honest",
  "source": "vendor",
  "description": "Verifies response is grounded in facts",
  "score": 0.92,
  "threshold": 0.8,
  "passed": true,
  "reason": "All facts supported by context",
  "explanation": "The response accurately reflects...",
  "execution_time_ms": 850.5,
  "input_tokens": 500,
  "output_tokens": 150,
  "total_tokens": 650,
  "evaluation_cost": 0.0001,
  "input_data": {
    "prompt": "Write a product description...",
    "system_prompt": "You are a creative copywriter"
  },
  "output_data": {
    "response": "Discover crystal-clear audio..."
  },
  "llm_metadata": {
    "model": "gpt-4o-mini",
    "temperature": 0.0
  },
  "trace": {
    "id": "trace-990e8400-e29b-41d4-a716-446655440005",
    "trace_id": "playground-exec-123",
    "name": "Product Description Test",
    "status": "success"
  }
}
```

---

## Error Handling

All API endpoints follow consistent error response format.

### Error Response Schema

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

#### 2xx Success
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no response body

#### 4xx Client Errors
- `400 Bad Request`: Invalid request body or parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists (duplicate)
- `422 Unprocessable Entity`: Validation error

#### 5xx Server Errors
- `500 Internal Server Error`: Server-side error

### Example Error Responses

**400 Bad Request**:
```json
{
  "detail": "Provider 'invalid' of type 'llm' not found or inactive"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Cannot create project for different organization"
}
```

**404 Not Found**:
```json
{
  "detail": "Project not found"
}
```

**409 Conflict**:
```json
{
  "detail": "Comparison already exists between these analyses with judge model 'claude-sonnet-4-5-20250929'. Comparison ID: comp-001"
}
```

**422 Unprocessable Entity**:
```json
{
  "detail": "Cannot compare analyses with different transcripts"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to execute prompt: OpenAI API error"
}
```

---

## Rate Limiting

Rate limits apply per organization per endpoint.

### Default Limits

- **Authentication**: 20 requests/minute
- **Read operations**: 100 requests/minute
- **Write operations**: 60 requests/minute
- **Model execution**: 30 requests/minute
- **Evaluation execution**: 20 requests/minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1612137600
```

### Rate Limit Exceeded

**Response**: `429 Too Many Requests`
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

---

## Best Practices

### Authentication
- Store tokens securely (never in localStorage)
- Refresh tokens before expiration
- Use HTTPS in production

### Pagination
- Always use `limit` and `offset` for large datasets
- Default limit is usually 20-100
- Maximum limit varies by endpoint (typically 100)

### Error Handling
- Always check HTTP status codes
- Parse `detail` field for user-friendly messages
- Implement retry logic for 5xx errors with exponential backoff
- Handle rate limiting with backoff strategy

### Performance
- Use filtering parameters to reduce payload size
- Cache frequently accessed data (organizations, projects)
- Batch operations when possible (e.g., run multiple evaluations)

### Security
- Never expose API keys in client-side code
- Use masked API keys for display
- Require ADMIN role for sensitive operations
- Always validate organization context

### Cost Optimization
- Use `gpt-4o-mini` for routine tasks
- Monitor token usage via trace metadata
- Consider cost-benefit when choosing judge models
- Use multi-judge comparison for critical decisions

---

## API Versioning

Current version: **v1**

Base URL: `/api/v1`

Version changes:
- Breaking changes → new major version (`/api/v2`)
- Backward-compatible changes → same version with deprecation notices
- All versions supported for minimum 12 months after deprecation

---

## Support

- **Documentation**: https://docs.promptforge.com
- **API Status**: https://status.promptforge.com
- **Support Email**: support@promptforge.com
- **GitHub Issues**: https://github.com/promptforge/promptforge/issues

---

*Last Updated: 2025-10-12*
*API Version: 1.0*
