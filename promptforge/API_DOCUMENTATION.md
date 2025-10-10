# PromptForge API Documentation

## Overview

PromptForge API is a RESTful backend built with FastAPI, providing comprehensive endpoints for AI prompt management, evaluation, observability, and governance.

**Base URL:** `http://localhost:8000/api/v1`

**Interactive Documentation:** http://localhost:8000/docs

## Authentication

All endpoints (except `/auth/login` and `/auth/refresh`) require JWT Bearer token authentication.

### Login

**POST** `/auth/login`

Request:
```json
{
  "email": "admin@promptforge.com",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Refresh Token

**POST** `/auth/refresh`

Headers:
```
Authorization: Bearer {refresh_token}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Tokens

Include the access token in all subsequent requests:

```
Authorization: Bearer {access_token}
```

## User Management

### Get Current User

**GET** `/users/me`

Response:
```json
{
  "id": "uuid",
  "email": "admin@promptforge.com",
  "full_name": "Admin User",
  "role": "admin",
  "organization_id": "uuid",
  "is_active": true,
  "created_at": "2025-10-05T12:00:00Z",
  "updated_at": "2025-10-05T12:00:00Z"
}
```

### List Users

**GET** `/users?skip=0&limit=100`

Response:
```json
[
  {
    "id": "uuid",
    "email": "admin@promptforge.com",
    "full_name": "Admin User",
    "role": "admin",
    "organization_id": "uuid",
    "is_active": true,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get User by ID

**GET** `/users/{user_id}`

### Create User

**POST** `/users`

Request:
```json
{
  "email": "newuser@promptforge.com",
  "password": "securepassword",
  "full_name": "New User",
  "role": "developer",
  "organization_id": "uuid"
}
```

### Update User

**PUT** `/users/{user_id}`

Request:
```json
{
  "full_name": "Updated Name",
  "is_active": true
}
```

### Delete User

**DELETE** `/users/{user_id}`

## Organizations

### List Organizations

**GET** `/organizations?skip=0&limit=100`

Response:
```json
[
  {
    "id": "uuid",
    "name": "PromptForge Demo",
    "description": "Demo organization",
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Organization by ID

**GET** `/organizations/{org_id}`

### Create Organization

**POST** `/organizations`

Request:
```json
{
  "name": "My Organization",
  "description": "Organization description"
}
```

### Update Organization

**PUT** `/organizations/{org_id}`

### Delete Organization

**DELETE** `/organizations/{org_id}`

## Projects

### List Projects

**GET** `/projects?skip=0&limit=100&status=active`

Query Parameters:
- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum records to return (default: 100)
- `status` - Filter by status: `active`, `draft`, `archived`

Response:
```json
[
  {
    "id": "uuid",
    "name": "Customer Support Assistant",
    "description": "AI-powered customer support chatbot",
    "status": "active",
    "organization_id": "uuid",
    "created_by": "uuid",
    "created_at": "2025-10-05T12:00:00Z",
    "updated_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Project by ID

**GET** `/projects/{project_id}`

### Create Project

**POST** `/projects`

Request:
```json
{
  "name": "New Project",
  "description": "Project description",
  "status": "draft",
  "organization_id": "uuid"
}
```

### Update Project

**PUT** `/projects/{project_id}`

### Delete Project

**DELETE** `/projects/{project_id}`

## Prompts

### List Prompts

**GET** `/prompts?skip=0&limit=100&project_id={uuid}&status=active`

Query Parameters:
- `project_id` - Filter by project
- `status` - Filter by status

Response:
```json
[
  {
    "id": "uuid",
    "name": "Customer Greeting",
    "description": "Friendly greeting for customer support",
    "category": "chatbot",
    "status": "active",
    "project_id": "uuid",
    "current_version_id": "uuid",
    "created_by": "uuid",
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Prompt by ID

**GET** `/prompts/{prompt_id}`

Includes current version details.

### Create Prompt

**POST** `/prompts`

Request:
```json
{
  "name": "New Prompt",
  "description": "Prompt description",
  "category": "completion",
  "status": "draft",
  "project_id": "uuid"
}
```

### Update Prompt

**PUT** `/prompts/{prompt_id}`

### Delete Prompt

**DELETE** `/prompts/{prompt_id}`

### List Prompt Versions

**GET** `/prompts/{prompt_id}/versions`

Response:
```json
[
  {
    "id": "uuid",
    "prompt_id": "uuid",
    "version_number": 1,
    "template": "You are a helpful assistant...",
    "system_message": "System instructions",
    "variables": {
      "customer_message": {
        "type": "string",
        "description": "Customer's message"
      }
    },
    "model_config": {
      "temperature": 0.7,
      "max_tokens": 150
    },
    "tags": ["greeting", "customer-support"],
    "avg_latency_ms": 450.0,
    "avg_cost": 0.0002,
    "usage_count": 1234,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Create Prompt Version

**POST** `/prompts/{prompt_id}/versions`

Request:
```json
{
  "template": "You are a helpful AI assistant. User: {user_input}",
  "system_message": "Be helpful and concise",
  "variables": {
    "user_input": {
      "type": "string",
      "description": "User's input message"
    }
  },
  "model_config": {
    "temperature": 0.8,
    "max_tokens": 200
  },
  "tags": ["v2", "improved"]
}
```

## Evaluations

### List Evaluations

**GET** `/evaluations?skip=0&limit=100&project_id={uuid}&status=completed`

Query Parameters:
- `project_id` - Filter by project
- `status` - Filter by status: `pending`, `running`, `completed`, `failed`

Response:
```json
[
  {
    "id": "uuid",
    "name": "Greeting Accuracy Test",
    "description": "Test greeting prompt accuracy",
    "evaluation_type": "accuracy",
    "status": "completed",
    "project_id": "uuid",
    "prompt_id": "uuid",
    "config": {
      "criteria": ["tone", "accuracy", "helpfulness"]
    },
    "dataset_id": "greeting-test-v1",
    "total_tests": 10,
    "passed_tests": 9,
    "failed_tests": 1,
    "avg_score": 0.92,
    "created_by": "uuid",
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Evaluation by ID

**GET** `/evaluations/{evaluation_id}`

### Create Evaluation

**POST** `/evaluations`

Request:
```json
{
  "name": "Performance Test",
  "description": "Test prompt performance",
  "evaluation_type": "performance",
  "status": "pending",
  "project_id": "uuid",
  "prompt_id": "uuid",
  "config": {
    "metrics": ["latency", "cost", "accuracy"]
  },
  "dataset_id": "test-dataset-v1"
}
```

### Update Evaluation

**PUT** `/evaluations/{evaluation_id}`

### Delete Evaluation

**DELETE** `/evaluations/{evaluation_id}`

### Get Evaluation Results

**GET** `/evaluations/{evaluation_id}/results`

Response:
```json
[
  {
    "id": "uuid",
    "evaluation_id": "uuid",
    "test_name": "Test Case 1",
    "input_data": {
      "customer_message": "Hello, I need help"
    },
    "expected_output": "Friendly greeting",
    "actual_output": "Hello! How can I help you today?",
    "score": 0.95,
    "passed": true,
    "latency_ms": 420.0,
    "token_count": 45,
    "cost": 0.0002,
    "metrics": {
      "tone_score": 0.98,
      "accuracy_score": 0.92
    },
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

## Traces

### List Traces

**GET** `/traces?skip=0&limit=100&project_id={uuid}&status=success`

Query Parameters:
- `project_id` - Filter by project
- `status` - Filter by status: `success`, `error`
- `start_date` - Filter traces after date
- `end_date` - Filter traces before date

Response:
```json
[
  {
    "id": "uuid",
    "trace_id": "trace-abc123",
    "name": "Customer Support Session 1",
    "status": "success",
    "project_id": "uuid",
    "prompt_version_id": "uuid",
    "model_id": "uuid",
    "input_data": {
      "message": "Sample customer query"
    },
    "output_data": {
      "response": "Sample response"
    },
    "trace_metadata": {
      "user_id": "customer-123"
    },
    "total_duration_ms": 850.0,
    "total_tokens": 120,
    "total_cost": 0.0015,
    "error_message": null,
    "error_type": null,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Trace by ID

**GET** `/traces/{trace_id}`

Includes all spans for the trace.

### Create Trace

**POST** `/traces`

Request:
```json
{
  "trace_id": "trace-custom-id",
  "name": "API Request",
  "status": "success",
  "project_id": "uuid",
  "prompt_version_id": "uuid",
  "model_id": "uuid",
  "input_data": {
    "prompt": "User input"
  },
  "output_data": {
    "response": "AI response"
  },
  "trace_metadata": {
    "session_id": "session-123"
  },
  "total_duration_ms": 1200.0,
  "total_tokens": 150,
  "total_cost": 0.002
}
```

### Update Trace

**PUT** `/traces/{trace_id}`

### Delete Trace

**DELETE** `/traces/{trace_id}`

### Get Trace Spans

**GET** `/traces/{trace_id}/spans`

Response:
```json
[
  {
    "id": "uuid",
    "trace_id": "uuid",
    "span_id": "span-abc123",
    "parent_span_id": null,
    "name": "LLM Call",
    "span_type": "llm",
    "start_time": 1728132000.0,
    "end_time": 1728132000.8,
    "duration_ms": 800.0,
    "input_data": {
      "prompt": "Sample prompt"
    },
    "output_data": {
      "response": "Sample response"
    },
    "span_metadata": {
      "model_version": "gpt-4-0125-preview"
    },
    "model_name": "gpt-4-0125-preview",
    "prompt_tokens": 80,
    "completion_tokens": 40,
    "total_tokens": 120,
    "temperature": 0.7,
    "max_tokens": 150,
    "status": "success",
    "error_message": null
  }
]
```

## Policies

### List Policies

**GET** `/policies?skip=0&limit=100&project_id={uuid}&is_active=true`

Query Parameters:
- `project_id` - Filter by project
- `is_active` - Filter by active status

Response:
```json
[
  {
    "id": "uuid",
    "name": "PII Detection",
    "description": "Detect and flag PII",
    "policy_type": "pii",
    "project_id": "uuid",
    "rules": {
      "patterns": ["email", "phone", "ssn"],
      "action": "redact"
    },
    "threshold": {
      "confidence": 0.8
    },
    "severity": "high",
    "action": "block",
    "is_active": true,
    "is_enforced": true,
    "violation_count": 0,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Policy by ID

**GET** `/policies/{policy_id}`

### Create Policy

**POST** `/policies`

Request:
```json
{
  "name": "Cost Limit",
  "description": "Alert on high costs",
  "policy_type": "cost",
  "project_id": "uuid",
  "rules": {
    "max_cost_per_request": 0.10
  },
  "threshold": {
    "cost": 0.10
  },
  "severity": "medium",
  "action": "warn",
  "is_active": true,
  "is_enforced": false
}
```

### Update Policy

**PUT** `/policies/{policy_id}`

### Delete Policy

**DELETE** `/policies/{policy_id}`

### Get Policy Violations

**GET** `/policies/{policy_id}/violations?skip=0&limit=100`

Response:
```json
[
  {
    "id": "uuid",
    "policy_id": "uuid",
    "trace_id": "uuid",
    "severity": "high",
    "message": "PII detected in input",
    "violation_metadata": {
      "detected_patterns": ["email"],
      "confidence": 0.95
    },
    "resolved": false,
    "resolved_at": null,
    "resolved_by": null,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

## Models

### List Model Providers

**GET** `/models/providers?skip=0&limit=100&is_active=true`

Response:
```json
[
  {
    "id": "uuid",
    "name": "OpenAI",
    "provider_type": "openai",
    "description": "OpenAI GPT models",
    "api_base_url": "https://api.openai.com/v1",
    "is_active": true,
    "is_default": true,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Provider by ID

**GET** `/models/providers/{provider_id}`

### Create Provider

**POST** `/models/providers`

Request:
```json
{
  "name": "Custom Provider",
  "provider_type": "other",
  "description": "Custom LLM provider",
  "api_base_url": "https://api.custom.com",
  "is_active": true
}
```

### Update Provider

**PUT** `/models/providers/{provider_id}`

### Delete Provider

**DELETE** `/models/providers/{provider_id}`

### List AI Models

**GET** `/models?skip=0&limit=100&provider_id={uuid}`

Response:
```json
[
  {
    "id": "uuid",
    "name": "GPT-4",
    "model_id": "gpt-4-0125-preview",
    "description": "Most capable GPT-4 model",
    "provider_id": "uuid",
    "supports_streaming": true,
    "supports_function_calling": true,
    "supports_vision": false,
    "max_context_length": 128000,
    "input_cost_per_million": 10.0,
    "output_cost_per_million": 30.0,
    "default_temperature": 0.7,
    "default_max_tokens": 2000,
    "created_at": "2025-10-05T12:00:00Z"
  }
]
```

### Get Model by ID

**GET** `/models/{model_id}`

### Create AI Model

**POST** `/models`

Request:
```json
{
  "name": "Custom Model",
  "model_id": "custom-model-v1",
  "description": "Custom fine-tuned model",
  "provider_id": "uuid",
  "supports_streaming": true,
  "max_context_length": 8000,
  "input_cost_per_million": 5.0,
  "output_cost_per_million": 15.0,
  "default_temperature": 0.8,
  "default_max_tokens": 1000
}
```

### Update AI Model

**PUT** `/models/{model_id}`

### Delete AI Model

**DELETE** `/models/{model_id}`

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently not implemented. To be added in Phase 3.

## Pagination

All list endpoints support pagination via `skip` and `limit` query parameters:

- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum records to return (default: 100, max: 1000)

## Filtering

Many list endpoints support filtering via query parameters. Refer to individual endpoint documentation for available filters.

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:

**JSON:** http://localhost:8000/api/v1/openapi.json

**Interactive UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

## TypeScript API Client

A type-safe TypeScript client is available in `ui-tier/shared/services/`:

```typescript
import { apiClient } from '@/shared/services/apiClient';
import { projectService } from '@/shared/services/projectService';
import { authService } from '@/shared/services/authService';

// Login
const tokens = await authService.login('admin@promptforge.com', 'admin123');

// Get projects
const projects = await projectService.getProjects({ status: 'active' });

// Create project
const newProject = await projectService.createProject({
  name: 'New Project',
  description: 'Project description',
  status: 'draft',
  organization_id: 'uuid'
});
```

## Example: Complete Workflow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@promptforge.com","password":"admin123"}'
# Returns: {"access_token": "...", "refresh_token": "..."}

# 2. Get current user
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer {access_token}"

# 3. List projects
curl http://localhost:8000/api/v1/projects?status=active \
  -H "Authorization: Bearer {access_token}"

# 4. Create a new prompt
curl -X POST http://localhost:8000/api/v1/prompts \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Prompt",
    "description": "Test prompt",
    "category": "completion",
    "status": "draft",
    "project_id": "{project_id}"
  }'

# 5. Create a prompt version
curl -X POST http://localhost:8000/api/v1/prompts/{prompt_id}/versions \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "You are a helpful assistant. User: {input}",
    "system_message": "Be concise",
    "variables": {"input": {"type": "string"}},
    "model_config": {"temperature": 0.7, "max_tokens": 150}
  }'
```

---

**Last Updated:** October 5, 2025

**API Version:** 2.0.0

**Documentation:** See PHASE2_SUCCESS.md for deployment details
