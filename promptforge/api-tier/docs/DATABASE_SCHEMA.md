# PromptForge Database Schema Documentation

**Version:** 1.0
**Last Updated:** 2025-10-12
**Database:** PostgreSQL 14+
**Migration Tool:** Alembic

---

## Table of Contents

1. [Overview](#overview)
2. [Core Tables](#core-tables)
   - [Organizations & Users](#organizations--users)
   - [Projects & Access Control](#projects--access-control)
3. [Insights & Analysis](#insights--analysis)
   - [Call Insights Analysis](#call-insights-analysis)
   - [Insight Comparisons](#insight-comparisons)
4. [Tracing & Observability](#tracing--observability)
   - [Traces](#traces)
   - [Spans](#spans)
5. [Evaluation Framework](#evaluation-framework)
   - [Evaluation Catalog](#evaluation-catalog)
   - [Trace Evaluations](#trace-evaluations)
6. [Model Configuration](#model-configuration)
   - [Model Catalog](#model-catalog)
   - [Model Provider Metadata](#model-provider-metadata)
   - [Model Provider Configs](#model-provider-configs)
7. [Prompt Management](#prompt-management)
8. [Policy & Compliance](#policy--compliance)
9. [JSONB Structures](#jsonb-structures)
10. [Data Flow Patterns](#data-flow-patterns)
11. [Migration History](#migration-history)

---

## Overview

PromptForge uses a PostgreSQL database with advanced JSONB support for flexible metadata storage. The schema is organized around several key domains:

- **Multi-tenancy:** Organization-scoped data with RBAC
- **Insights Analysis:** 3-stage DTA (Data-to-Analysis) pipeline for call transcripts
- **Model Comparison:** Blind evaluation of model outputs using judge models
- **Tracing:** OpenTelemetry-compatible observability for LLM calls
- **Evaluation:** Extensible evaluation framework with LLM-as-Judge support
- **Model Management:** Centralized catalog of AI models with pricing and capabilities

---

## Core Tables

### Organizations & Users

#### `organizations`

Multi-tenant organizations that own all data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique organization identifier |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE | Organization name |
| `description` | VARCHAR(1000) | | Organization description |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `name`

**Referenced By:**
- `users`, `projects`, `call_insights_analysis`, `insight_comparisons`, `model_provider_configs`, `evaluation_catalog`, `trace_evaluations`, `groups`

---

#### `users`

Application users with role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | Hashed password (bcrypt) |
| `full_name` | VARCHAR(255) | | User's full name |
| `is_active` | BOOLEAN | NOT NULL | Account active status |
| `role` | ENUM(UserRole) | NOT NULL | User role (admin, developer, viewer) |
| `organization_id` | UUID | FK → organizations.id | Parent organization |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `email`

**Enums:**
```python
UserRole = Enum('admin', 'developer', 'viewer')
```

**Referenced By:**
- `projects`, `prompts`, `call_insights_analysis`, `insight_comparisons`, `traces`, `model_provider_configs`, `evaluation_catalog`, `policy_violations`

---

### Projects & Access Control

#### `projects`

Projects organize prompts, traces, and analyses within an organization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique project identifier |
| `name` | VARCHAR(255) | NOT NULL | Project name |
| `description` | TEXT | | Project description |
| `status` | VARCHAR(50) | NOT NULL | Project status (active, archived, etc.) |
| `organization_id` | UUID | NOT NULL, FK → organizations.id | Parent organization |
| `created_by` | UUID | NOT NULL, FK → users.id | User who created the project |
| `access_level` | VARCHAR(50) | NOT NULL, DEFAULT 'organization' | Access control level |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Referenced By:**
- `prompts`, `traces`, `call_insights_analysis`, `model_provider_configs`, `evaluation_catalog`, `policies`

---

#### `groups`

User groups for granular access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique group identifier |
| `name` | VARCHAR(255) | NOT NULL | Group name |
| `description` | TEXT | | Group description |
| `organization_id` | UUID | NOT NULL, FK → organizations.id | Parent organization |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `organization_id`
- Unique constraint on `(organization_id, name)`

**Referenced By:**
- `user_groups`, `project_groups`

---

## Insights & Analysis

### Call Insights Analysis

#### `call_insights_analysis`

Main insights storage for the 3-stage DTA pipeline (Facts → Insights → Summary).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique analysis identifier |
| `organization_id` | UUID | NOT NULL, FK → organizations.id | Parent organization |
| `user_id` | UUID | NOT NULL, FK → users.id | User who created the analysis |
| `project_id` | UUID | FK → projects.id | Associated project (optional) |
| `transcript_title` | VARCHAR(500) | | Title or identifier for the transcript |
| `transcript_input` | TEXT | NOT NULL | Original transcript text |
| `facts_output` | TEXT | NOT NULL | Stage 1: Extracted facts |
| `insights_output` | TEXT | NOT NULL | Stage 2: Reasoned insights |
| `summary_output` | TEXT | NOT NULL | Stage 3: Final summary |
| `pii_redacted` | BOOLEAN | NOT NULL, DEFAULT false | Whether PII was redacted |
| `stage_params` | JSONB | | Model parameters per stage (see JSONB Structures) |
| `parent_trace_id` | UUID | FK → traces.id | Parent trace for observability |
| `total_tokens` | INTEGER | NOT NULL, DEFAULT 0 | Total tokens across all stages |
| `total_cost` | DOUBLE PRECISION | NOT NULL, DEFAULT 0 | Total cost in USD |
| `total_duration_ms` | DOUBLE PRECISION | | Total execution time in milliseconds |
| `analysis_metadata` | JSONB | | Additional metadata (see JSONB Structures) |
| `system_prompt_stage1` | TEXT | | System prompt for Stage 1 (fact extraction) |
| `system_prompt_stage2` | TEXT | | System prompt for Stage 2 (insights) |
| `system_prompt_stage3` | TEXT | | System prompt for Stage 3 (summary) |
| `model_stage1` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 1 |
| `model_stage2` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 2 |
| `model_stage3` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 3 |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `organization_id`
- Index on `project_id`
- Index on `created_at`
- Index on `transcript_title`

**JSONB Field: `stage_params`**

Stores model parameters for each stage:

```json
{
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
}
```

**JSONB Field: `analysis_metadata`**

Stores analysis metadata:

```json
{
  "stage_count": 3,
  "evaluation_count": 3,
  "model_parameters": {
    "stage1": {
      "temperature": 0.25,
      "top_p": 0.95,
      "max_tokens": 1000
    },
    "stage2": {
      "temperature": 0.65,
      "top_p": 0.95,
      "max_tokens": 1500
    },
    "stage3": {
      "temperature": 0.45,
      "top_p": 0.95,
      "max_tokens": 800
    }
  }
}
```

**Referenced By:**
- `insight_comparisons` (as `analysis_a_id`, `analysis_b_id`)

---

### Insight Comparisons

#### `insight_comparisons`

Blind comparison results between two insight analyses using a judge model.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique comparison identifier |
| `organization_id` | UUID | NOT NULL, FK → organizations.id | Parent organization |
| `user_id` | UUID | NOT NULL, FK → users.id | User who created the comparison |
| `analysis_a_id` | UUID | NOT NULL, FK → call_insights_analysis.id (CASCADE) | First analysis being compared |
| `analysis_b_id` | UUID | NOT NULL, FK → call_insights_analysis.id (CASCADE) | Second analysis being compared |
| `judge_model` | VARCHAR(100) | NOT NULL, DEFAULT 'claude-sonnet-4.5' | Judge model identifier |
| `judge_model_version` | VARCHAR(200) | | Exact API version (e.g., 'claude-sonnet-4-5-20250929') |
| `evaluation_criteria` | JSONB | NOT NULL | List of evaluation criteria (see below) |
| `overall_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Overall winner |
| `overall_reasoning` | TEXT | NOT NULL | Overall reasoning for the winner |
| `stage1_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 1 (facts) winner |
| `stage1_scores` | JSONB | | Stage 1 scores per criterion (see below) |
| `stage1_reasoning` | TEXT | | Stage 1 reasoning |
| `stage2_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 2 (insights) winner |
| `stage2_scores` | JSONB | | Stage 2 scores per criterion |
| `stage2_reasoning` | TEXT | | Stage 2 reasoning |
| `stage3_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 3 (summary) winner |
| `stage3_scores` | JSONB | | Stage 3 scores per criterion |
| `stage3_reasoning` | TEXT | | Stage 3 reasoning |
| `judge_trace_id` | UUID | FK → traces.id | Trace of judge model invocation |
| `comparison_metadata` | JSONB | | Judge metrics (cost, tokens, duration) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `organization_id`
- Index on `user_id`
- Index on `analysis_a_id`
- Index on `analysis_b_id`
- Index on `created_at`
- Composite index on `(organization_id, created_at DESC)`
- Composite index on `(user_id, created_at DESC)`
- Index on `judge_model`
- Unique constraint on `(analysis_a_id, analysis_b_id, judge_model)`

**JSONB Field: `evaluation_criteria`**

List of evaluation criteria:

```json
["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
```

**JSONB Field: `stage1_scores`, `stage2_scores`, `stage3_scores`**

Scores for each analysis per criterion (0.0 - 1.0 scale):

```json
{
  "A": {
    "groundedness": 0.88,
    "faithfulness": 0.92,
    "completeness": 0.85,
    "clarity": 0.9,
    "accuracy": 0.9
  },
  "B": {
    "groundedness": 0.82,
    "faithfulness": 0.85,
    "completeness": 0.88,
    "clarity": 0.88,
    "accuracy": 0.8
  }
}
```

**JSONB Field: `comparison_metadata`**

Judge model metrics and cost comparison:

```json
{
  "cost_a": 0.00205,
  "cost_b": 0.00214,
  "tokens_a": 7523,
  "tokens_b": 7867,
  "total_cost": 0.103689,
  "duration_ms": 68695.18,
  "total_tokens": 19695,
  "cost_difference": "+$0.00009 (+4.3%)",
  "quality_improvement": "+21.9%"
}
```

---

## Tracing & Observability

### Traces

#### `traces`

OpenTelemetry-compatible traces for LLM calls and workflows.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique trace identifier (internal) |
| `trace_id` | VARCHAR(255) | NOT NULL, UNIQUE | OpenTelemetry trace ID |
| `name` | VARCHAR(255) | NOT NULL | Trace name |
| `status` | VARCHAR(50) | | Trace status (ok, error, etc.) |
| `input_data` | JSON | | Input data (see JSONB Structures) |
| `output_data` | JSON | | Output data |
| `trace_metadata` | JSON | | Additional metadata (see below) |
| `total_duration_ms` | DOUBLE PRECISION | | Total execution time |
| `total_tokens` | INTEGER | | Total tokens used |
| `input_tokens` | INTEGER | | Input tokens |
| `output_tokens` | INTEGER | | Output tokens |
| `total_cost` | DOUBLE PRECISION | | Total cost in USD |
| `error_message` | TEXT | | Error message if failed |
| `error_type` | VARCHAR(100) | | Error type |
| `project_id` | UUID | NOT NULL, FK → projects.id | Associated project |
| `prompt_version_id` | UUID | FK → prompt_versions.id | Prompt version used |
| `model_id` | UUID | FK → ai_models.id | Model used (legacy) |
| `model_name` | VARCHAR(100) | | Model name (e.g., 'gpt-4o-mini') |
| `provider` | VARCHAR(100) | | Provider name (e.g., 'openai') |
| `user_id` | UUID | FK → users.id (SET NULL) | User who created the trace |
| `environment` | VARCHAR(50) | | Environment (dev, staging, prod) |
| `retry_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of retries |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `trace_id`
- Index on `model_name`
- Index on `provider`
- Index on `environment`
- Index on `user_id`
- GIN index on `(trace_metadata->>'parent_trace_id')` where trace_metadata IS NOT NULL
- GIN index on `(trace_metadata->>'source')` where trace_metadata IS NOT NULL

**JSONB Field: `input_data`**

Input data includes prompt, system prompt, and model parameters:

```json
{
  "prompt": "The transcript text...",
  "system_prompt": "Generate twenty bullet points with insights from the conversation",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9,
    "top_k": 40
  }
}
```

**JSONB Field: `trace_metadata`**

Additional trace metadata:

```json
{
  "intent": "Content Summarization",
  "tone": "professional",
  "source": "playground",
  "parent_trace_id": "parent-trace-uuid"
}
```

**Referenced By:**
- `spans`, `call_insights_analysis`, `insight_comparisons`, `policy_violations`, `trace_evaluations`

---

### Spans

#### `spans`

Child spans of traces representing individual LLM calls or operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique span identifier (internal) |
| `span_id` | VARCHAR(255) | NOT NULL, UNIQUE | OpenTelemetry span ID |
| `parent_span_id` | VARCHAR(255) | | Parent span ID (for nested spans) |
| `trace_id` | UUID | NOT NULL, FK → traces.id | Parent trace |
| `name` | VARCHAR(255) | NOT NULL | Span name |
| `span_type` | VARCHAR(50) | | Span type (llm, tool, workflow, etc.) |
| `start_time` | DOUBLE PRECISION | NOT NULL | Start time (Unix timestamp) |
| `end_time` | DOUBLE PRECISION | | End time (Unix timestamp) |
| `duration_ms` | DOUBLE PRECISION | | Duration in milliseconds |
| `input_data` | JSON | | Input data |
| `output_data` | JSON | | Output data |
| `span_metadata` | JSON | | Additional metadata |
| `model_name` | VARCHAR(100) | | Model used for this span |
| `prompt_tokens` | INTEGER | | Input tokens |
| `completion_tokens` | INTEGER | | Output tokens |
| `total_tokens` | INTEGER | | Total tokens |
| `temperature` | DOUBLE PRECISION | | Temperature parameter |
| `max_tokens` | INTEGER | | Max tokens parameter |
| `status` | VARCHAR(50) | | Span status |
| `error_message` | TEXT | | Error message if failed |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `span_id`
- Index on `parent_span_id`

---

## Evaluation Framework

### Evaluation Catalog

#### `evaluation_catalog`

Catalog of available evaluations (LLM-as-Judge, custom, vendor-specific).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique evaluation identifier |
| `name` | VARCHAR(255) | NOT NULL | Evaluation name |
| `description` | TEXT | | Evaluation description |
| `category` | ENUM(EvaluationCategory) | NOT NULL | Category (accuracy, relevance, safety, etc.) |
| `source` | ENUM(EvaluationSource) | NOT NULL | Source (builtin, custom, vendor) |
| `evaluation_type` | ENUM(EvaluationType) | NOT NULL | Type (llm_as_judge, rule_based, etc.) |
| `organization_id` | UUID | FK → organizations.id | Organization (for custom evals) |
| `project_id` | UUID | FK → projects.id | Project (for custom evals) |
| `is_public` | BOOLEAN | NOT NULL | Whether evaluation is publicly available |
| `config_schema` | JSON | | JSON schema for configuration |
| `default_config` | JSON | | Default configuration values |
| `implementation` | TEXT | | Implementation code (for custom evals) |
| `adapter_class` | VARCHAR(255) | | Adapter class name (for vendor evals) |
| `adapter_evaluation_id` | VARCHAR(255) | | Vendor's evaluation ID |
| `vendor_name` | VARCHAR(100) | | Display name of vendor (DeepEval, Ragas, etc.) |
| `llm_criteria` | TEXT | | Evaluation criteria for LLM-as-Judge |
| `llm_model` | VARCHAR(100) | | Model to use for LLM-as-Judge |
| `llm_system_prompt` | TEXT | | System prompt for LLM-as-Judge |
| `prompt_input` | TEXT | | Input prompt template for custom evaluations |
| `prompt_output` | TEXT | | Expected output schema for custom evaluations |
| `custom_system_prompt` | TEXT | | System prompt for custom evaluations |
| `version` | VARCHAR(50) | | Evaluation version |
| `is_active` | BOOLEAN | NOT NULL | Whether evaluation is active |
| `tags` | JSON | | Tags for categorization |
| `created_by` | UUID | FK → users.id | User who created this evaluation |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `name`
- Index on `category`
- Index on `source`
- Index on `evaluation_type`
- Index on `organization_id`
- Index on `project_id`
- Index on `is_active`
- Index on `is_public`
- Index on `adapter_evaluation_id`
- Index on `vendor_name`
- Index on `created_by`

**Enums:**
```python
EvaluationCategory = Enum('accuracy', 'relevance', 'safety', 'quality', 'coherence', 'custom')
EvaluationSource = Enum('builtin', 'custom', 'vendor')
EvaluationType = Enum('llm_as_judge', 'rule_based', 'heuristic', 'model_based')
```

---

### Trace Evaluations

#### `trace_evaluations`

Evaluation results for traces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique evaluation result identifier |
| `trace_id` | UUID | NOT NULL, FK → traces.id | Trace being evaluated |
| `evaluation_catalog_id` | UUID | NOT NULL, FK → evaluation_catalog.id | Evaluation used |
| `organization_id` | UUID | NOT NULL, FK → organizations.id | Parent organization |
| `score` | DOUBLE PRECISION | | Evaluation score (0.0 - 1.0) |
| `passed` | BOOLEAN | | Whether evaluation passed |
| `category` | VARCHAR(255) | | Evaluation category |
| `reason` | TEXT | | Evaluation reasoning |
| `details` | JSON | | Detailed results |
| `suggestions` | JSON | | Improvement suggestions |
| `execution_time_ms` | DOUBLE PRECISION | | Evaluation execution time |
| `model_used` | VARCHAR(100) | | Model used for evaluation (if LLM-as-Judge) |
| `input_tokens` | INTEGER | | Input tokens (if LLM-as-Judge) |
| `output_tokens` | INTEGER | | Output tokens (if LLM-as-Judge) |
| `total_tokens` | INTEGER | | Total tokens (if LLM-as-Judge) |
| `evaluation_cost` | DOUBLE PRECISION | | Cost of evaluation in USD |
| `config` | JSON | | Configuration used |
| `status` | VARCHAR(50) | NOT NULL | Evaluation status (completed, failed, etc.) |
| `error_message` | TEXT | | Error message if failed |
| `vendor_metrics` | JSONB | | Vendor-specific metrics |
| `llm_metadata` | JSONB | | Comprehensive LLM metrics |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `trace_id`
- Index on `evaluation_catalog_id`
- Index on `organization_id`
- Composite index on `(organization_id, created_at DESC)`
- Index on `model_used`
- Index on `created_at DESC`
- GIN index on `vendor_metrics`
- GIN index on `llm_metadata`

**JSONB Field: `llm_metadata`**

Comprehensive LLM metrics for evaluation invocations:

```json
{
  "model": "claude-sonnet-4.5",
  "provider": "anthropic",
  "temperature": 0.3,
  "max_tokens": 1000,
  "input_tokens": 1234,
  "output_tokens": 567,
  "total_tokens": 1801,
  "cost": 0.0123,
  "duration_ms": 2345.67,
  "thinking_tokens": 100,
  "cache_creation_tokens": 50,
  "cache_read_tokens": 200
}
```

---

## Model Configuration

### Model Catalog

#### `model_catalog`

Centralized catalog of AI models with pricing, capabilities, and compatibility information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique model identifier |
| `model_name` | VARCHAR(100) | NOT NULL, UNIQUE | Model name (e.g., 'gpt-4o-mini') |
| `model_version` | VARCHAR(200) | NOT NULL | Exact API version |
| `provider_name` | VARCHAR(100) | NOT NULL | Provider (openai, anthropic, google, etc.) |
| `model_family` | VARCHAR(100) | NOT NULL | Model family (gpt-4, claude-3, etc.) |
| `display_name` | VARCHAR(255) | NOT NULL | Human-readable display name |
| `description` | TEXT | | Model description |
| `context_window` | JSON | | Context window limits (input/output) |
| `capabilities` | JSON | | Model capabilities (text, vision, etc.) |
| `pricing` | JSON | | Pricing per million tokens |
| `is_active` | BOOLEAN | NOT NULL | Whether model is currently available |
| `is_deprecated` | BOOLEAN | NOT NULL | Whether model is deprecated |
| `is_recommended` | BOOLEAN | NOT NULL | Whether model is recommended |
| `release_date` | TIMESTAMP | | Model release date |
| `deprecation_date` | TIMESTAMP | | Model deprecation date (if applicable) |
| `notes` | TEXT | | Additional notes |
| `documentation_url` | VARCHAR(500) | | Documentation URL |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `model_name`
- Index on `provider_name`
- Index on `is_active`

**Check Constraints:**
- `model_name != ''`
- `model_version != ''`
- `provider_name IN ('openai', 'anthropic', 'google', 'cohere', 'mistral')`

**JSON Field: `context_window`**

```json
{
  "input": 200000,
  "output": 8192
}
```

**JSON Field: `capabilities`**

```json
["text", "vision", "thinking", "computer_use"]
```

**JSON Field: `pricing`**

Pricing per million tokens in USD:

```json
{
  "input": 3.0,
  "output": 15.0,
  "currency": "USD"
}
```

**Example Models:**

| Model Name | Provider | Family | Notes |
|------------|----------|--------|-------|
| `claude-sonnet-4.5` | anthropic | claude-4 | Recommended for judge models |
| `gpt-4o` | openai | gpt-4 | Uses legacy `max_tokens` parameter |
| `gpt-5` | openai | gpt-5 | Uses `max_completion_tokens` parameter |
| `gpt-5-nano` | openai | gpt-5 | Always uses temperature=1 |

---

### Model Provider Metadata

#### `model_provider_metadata`

Metadata for model providers (configuration templates, capabilities, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique provider metadata identifier |
| `provider_name` | VARCHAR(100) | NOT NULL, UNIQUE | Provider name |
| `provider_type` | VARCHAR(50) | NOT NULL | Provider type (llm, embedding, etc.) |
| `display_name` | VARCHAR(255) | NOT NULL | Human-readable display name |
| `description` | TEXT | | Provider description |
| `icon_url` | VARCHAR(500) | | Provider icon URL |
| `documentation_url` | VARCHAR(500) | | Provider documentation URL |
| `required_fields` | JSONB | | Required configuration fields |
| `optional_fields` | JSONB | | Optional configuration fields |
| `default_config` | JSONB | | Default configuration values |
| `capabilities` | JSONB | | Provider capabilities |
| `supported_models` | JSONB | | List of supported models |
| `api_key_pattern` | VARCHAR(255) | | Regex pattern for API key validation |
| `api_key_prefix` | VARCHAR(20) | | API key prefix (e.g., 'sk-') |
| `is_active` | BOOLEAN | | Whether provider is active |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `provider_name`
- Index on `provider_type`
- Index on `is_active`

---

### Model Provider Configs

#### `model_provider_configs`

User-configured model provider credentials and settings (encrypted).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique config identifier |
| `organization_id` | UUID | NOT NULL, FK → organizations.id (CASCADE) | Parent organization |
| `project_id` | UUID | FK → projects.id (CASCADE) | Associated project (optional) |
| `provider_name` | VARCHAR(100) | NOT NULL | Provider name |
| `provider_type` | VARCHAR(50) | NOT NULL | Provider type (llm, embedding, etc.) |
| `display_name` | VARCHAR(255) | | Custom display name |
| `api_key_encrypted` | TEXT | NOT NULL | Encrypted API key |
| `api_key_hash` | VARCHAR(128) | NOT NULL | Hash of API key for deduplication |
| `config_encrypted` | TEXT | | Encrypted additional configuration |
| `is_active` | BOOLEAN | | Whether config is active |
| `is_default` | BOOLEAN | | Whether config is default for org/project |
| `last_used_at` | TIMESTAMP | | Last time config was used |
| `usage_count` | INTEGER | | Number of times config was used |
| `created_by` | UUID | FK → users.id | User who created the config |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `organization_id`
- Index on `project_id`
- Index on `is_active`
- Unique constraint on `(organization_id, project_id, provider_name, provider_type)`

**Check Constraints:**
- `provider_name != ''`
- `provider_type IN ('llm', 'embedding', 'image', 'audio', 'multimodal')`

---

## Prompt Management

### Prompts

#### `prompts`

Prompt templates with versioning support.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique prompt identifier |
| `name` | VARCHAR(255) | NOT NULL | Prompt name |
| `description` | TEXT | | Prompt description |
| `category` | VARCHAR(100) | | Prompt category |
| `status` | VARCHAR(50) | NOT NULL | Prompt status (active, archived, etc.) |
| `project_id` | UUID | NOT NULL, FK → projects.id | Associated project |
| `created_by` | UUID | NOT NULL, FK → users.id | User who created the prompt |
| `current_version_id` | UUID | FK → prompt_versions.id | Current version |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

---

### Prompt Versions

#### `prompt_versions`

Versions of prompt templates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique version identifier |
| `prompt_id` | UUID | NOT NULL, FK → prompts.id | Parent prompt |
| `version_number` | INTEGER | NOT NULL | Version number |
| `template` | TEXT | NOT NULL | Prompt template |
| `system_message` | TEXT | | System message |
| `variables` | JSON | | Template variables |
| `model_config` | JSON | | Model configuration |
| `tags` | JSON | | Tags for categorization |
| `avg_latency_ms` | DOUBLE PRECISION | | Average latency |
| `avg_cost` | DOUBLE PRECISION | | Average cost |
| `usage_count` | INTEGER | | Number of times used |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

---

## Policy & Compliance

### Policies

#### `policies`

Governance policies for traces and LLM outputs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique policy identifier |
| `name` | VARCHAR(255) | NOT NULL | Policy name |
| `description` | TEXT | | Policy description |
| `policy_type` | VARCHAR(100) | NOT NULL | Policy type (pii, toxicity, etc.) |
| `rules` | JSON | NOT NULL | Policy rules configuration |
| `threshold` | JSON | | Threshold values |
| `severity` | ENUM(PolicySeverity) | NOT NULL | Severity (low, medium, high, critical) |
| `action` | ENUM(PolicyAction) | NOT NULL | Action (warn, block, redact, etc.) |
| `is_active` | BOOLEAN | NOT NULL | Whether policy is active |
| `is_enforced` | BOOLEAN | NOT NULL | Whether policy is enforced |
| `project_id` | UUID | NOT NULL, FK → projects.id | Associated project |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Enums:**
```python
PolicySeverity = Enum('low', 'medium', 'high', 'critical')
PolicyAction = Enum('warn', 'block', 'redact', 'log')
```

---

### Policy Violations

#### `policy_violations`

Detected policy violations in traces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique violation identifier |
| `policy_id` | UUID | NOT NULL, FK → policies.id | Policy that was violated |
| `trace_id` | UUID | FK → traces.id | Trace where violation occurred |
| `violation_type` | VARCHAR(100) | NOT NULL | Type of violation |
| `severity` | ENUM(PolicySeverity) | NOT NULL | Violation severity |
| `detected_value` | JSON | | Detected violating value |
| `threshold_value` | JSON | | Threshold that was exceeded |
| `confidence_score` | INTEGER | | Confidence score (0-100) |
| `message` | TEXT | | Violation message |
| `violation_metadata` | JSON | | Additional metadata |
| `status` | VARCHAR(50) | | Violation status (open, resolved, etc.) |
| `resolution_notes` | TEXT | | Resolution notes |
| `resolved_at` | VARCHAR(50) | | Resolution timestamp (should be TIMESTAMP) |
| `resolved_by` | UUID | FK → users.id | User who resolved the violation |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

---

## JSONB Structures

This section documents the structure of JSONB fields used throughout the database.

### `call_insights_analysis.stage_params`

Model parameters for each stage of the DTA pipeline:

```json
{
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
}
```

### `call_insights_analysis.analysis_metadata`

Analysis metadata including stage count and model parameters:

```json
{
  "stage_count": 3,
  "evaluation_count": 3,
  "model_parameters": {
    "stage1": {
      "temperature": 0.25,
      "top_p": 0.95,
      "max_tokens": 1000
    },
    "stage2": {
      "temperature": 0.65,
      "top_p": 0.95,
      "max_tokens": 1500
    },
    "stage3": {
      "temperature": 0.45,
      "top_p": 0.95,
      "max_tokens": 800
    }
  }
}
```

### `insight_comparisons.evaluation_criteria`

List of evaluation criteria used by the judge model:

```json
["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
```

### `insight_comparisons.stage1_scores` (same for stage2, stage3)

Scores for each analysis per criterion (0.0 - 1.0 scale):

```json
{
  "A": {
    "groundedness": 0.88,
    "faithfulness": 0.92,
    "completeness": 0.85,
    "clarity": 0.9,
    "accuracy": 0.9
  },
  "B": {
    "groundedness": 0.82,
    "faithfulness": 0.85,
    "completeness": 0.88,
    "clarity": 0.88,
    "accuracy": 0.8
  }
}
```

### `insight_comparisons.comparison_metadata`

Judge model metrics and cost comparison:

```json
{
  "cost_a": 0.00205,
  "cost_b": 0.00214,
  "tokens_a": 7523,
  "tokens_b": 7867,
  "total_cost": 0.103689,
  "duration_ms": 68695.18,
  "total_tokens": 19695,
  "cost_difference": "+$0.00009 (+4.3%)",
  "quality_improvement": "+21.9%"
}
```

### `traces.input_data`

Input data includes prompt, system prompt, and model parameters:

```json
{
  "prompt": "The transcript text...",
  "system_prompt": "Generate twenty bullet points with insights from the conversation",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.9,
    "top_k": 40
  }
}
```

**Note:** The `parameters` node contains the model parameters (temperature, top_p, max_tokens, etc.) that are used for the LLM call.

### `traces.trace_metadata`

Additional trace metadata:

```json
{
  "intent": "Content Summarization",
  "tone": "professional",
  "source": "playground",
  "parent_trace_id": "parent-trace-uuid"
}
```

### `trace_evaluations.llm_metadata`

Comprehensive LLM metrics for evaluation invocations:

```json
{
  "model": "claude-sonnet-4.5",
  "provider": "anthropic",
  "temperature": 0.3,
  "max_tokens": 1000,
  "input_tokens": 1234,
  "output_tokens": 567,
  "total_tokens": 1801,
  "cost": 0.0123,
  "duration_ms": 2345.67,
  "thinking_tokens": 100,
  "cache_creation_tokens": 50,
  "cache_read_tokens": 200
}
```

---

## Data Flow Patterns

### 1. Insights Analysis Flow

**API Request → Service → Database**

1. User submits transcript via `/api/v1/playground/generate-insights`
2. Service receives request with:
   - `transcript_input`
   - `model_name` (per stage)
   - `stage_params` (temperature, top_p, max_tokens per stage)
3. Service executes 3-stage DTA pipeline:
   - Stage 1: Fact Extraction
   - Stage 2: Reasoning & Insights
   - Stage 3: Summary Synthesis
4. Service creates a parent trace in `traces` table
5. Service creates child spans in `spans` table for each stage
6. Service stores analysis in `call_insights_analysis`:
   - `stage_params` contains model parameters per stage
   - `analysis_metadata` contains stage count and evaluation count
   - `model_stage1`, `model_stage2`, `model_stage3` contain model names
   - `system_prompt_stage1`, etc. contain system prompts
   - `facts_output`, `insights_output`, `summary_output` contain results
   - `total_tokens`, `total_cost`, `total_duration_ms` contain aggregated metrics
7. Parent trace ID is linked via `parent_trace_id`

### 2. Historical Data Retrieval for Comparison

**Frontend → API → Database**

1. Frontend requests historical analyses via `/api/v1/insight-comparison/analyses-for-comparison`
2. API queries `call_insights_analysis` with filters:
   - `organization_id` (RBAC)
   - `created_at` (date range)
   - `model_stage1`, `model_stage2`, `model_stage3` (optional)
3. API returns list of analyses with:
   - `id`, `transcript_title`, `created_at`
   - `model_stage1`, `model_stage2`, `model_stage3`
   - `total_cost`, `total_tokens`
   - Partial outputs (first 200 chars)

### 3. Model Comparison Flow

**Frontend → API → Judge Model → Database**

1. User selects two analyses to compare
2. Frontend calls `/api/v1/insight-comparison/compare`
3. Service retrieves both analyses from `call_insights_analysis`
4. Service blindly labels them as "A" and "B" (randomized)
5. Service calls judge model (e.g., Claude Sonnet 4.5) with:
   - Both analyses (facts, insights, summary)
   - Evaluation criteria (groundedness, faithfulness, etc.)
   - Blind evaluation instructions
6. Judge model returns:
   - Per-stage winners and scores
   - Overall winner and reasoning
   - Cost-benefit analysis
7. Service creates trace for judge invocation in `traces`
8. Service stores comparison result in `insight_comparisons`:
   - `analysis_a_id`, `analysis_b_id`
   - `judge_model`, `evaluation_criteria`
   - `stage1_winner`, `stage1_scores`, `stage1_reasoning`
   - `stage2_winner`, `stage2_scores`, `stage2_reasoning`
   - `stage3_winner`, `stage3_scores`, `stage3_reasoning`
   - `overall_winner`, `overall_reasoning`
   - `judge_trace_id` (links to judge trace)
   - `comparison_metadata` (judge cost, tokens, duration)

### 4. Trace → Analysis Relationship

- `traces` table stores OpenTelemetry-compatible traces for LLM calls
- `call_insights_analysis` table stores the 3-stage DTA pipeline results
- Relationship: `call_insights_analysis.parent_trace_id` → `traces.id`
- Parent trace represents the entire DTA workflow
- Child spans (in `spans` table) represent individual LLM calls per stage

---

## Migration History

### Current Schema Version

**Revision:** `u0v1w2x3y4z5`
**Date:** 2025-10-11

### Recent Migrations

| Revision | Date | Description |
|----------|------|-------------|
| `u0v1w2x3y4z5` | 2025-10-11 | Added `model_catalog` table and `judge_model_version` column |
| `n0p1q2r3s4t5` | 2025-10-11 | Added `insight_comparisons` table for blind model comparison |
| `4461438681f4` | 2025-10-10 | Added `encryption_keys` table for API key encryption |
| `1762fd0c1389` | 2025-10-09 | Added system prompts and models to `call_insights_analysis` |
| `j6h0i1j2k3l4` | 2025-10-08 | Added `call_insights_analysis` table |
| `i5g9h0i1j2k3` | 2025-10-07 | Fixed `llm_metadata` to JSONB in `trace_evaluations` |
| `h4f8g9h0i1j2` | 2025-10-06 | Added `llm_metadata` and `vendor_name` to evaluation tables |
| `g3e7f8g9h0i1` | 2025-10-05 | Added evaluation cost tracking |
| `f2d6e7f8g9h0` | 2025-10-04 | Added `adapter_evaluation_id` for vendor integrations |
| `e1c5d6f7g8h9` | 2025-10-03 | Added trace dashboard fields (model_name, provider, etc.) |
| `d0b4c5f6g7h8` | 2025-10-02 | Added group-based access control for projects |
| `c9a3b4d5e6f7` | 2025-10-01 | Added `model_provider_metadata` and `model_provider_configs` |
| `b8f209885293` | 2025-09-30 | Added evaluation catalog and trace evaluations |
| `b7e2f2a5439a` | 2025-09-29 | Initial schema with all core models |

### Backward Compatibility Notes

1. **Model Catalog (u0v1w2x3y4z5):**
   - Added `judge_model_version` column to `insight_comparisons` (nullable for backward compatibility)
   - Backfilled `judge_model_version` from `model_catalog` for existing comparisons

2. **Insight Comparisons (n0p1q2r3s4t5):**
   - New table, fully backward compatible
   - CASCADE deletes on `call_insights_analysis` prevent orphaned comparisons

3. **System Prompts (1762fd0c1389):**
   - Added `system_prompt_stage1`, `system_prompt_stage2`, `system_prompt_stage3` columns (nullable)
   - Added `model_stage1`, `model_stage2`, `model_stage3` columns with defaults

---

## Database Maintenance

### Regular Maintenance Tasks

1. **Vacuum and Analyze:**
   ```sql
   VACUUM ANALYZE call_insights_analysis;
   VACUUM ANALYZE traces;
   VACUUM ANALYZE insight_comparisons;
   ```

2. **Index Maintenance:**
   ```sql
   REINDEX TABLE call_insights_analysis;
   REINDEX TABLE traces;
   ```

3. **Check Table Sizes:**
   ```sql
   SELECT
     schemaname,
     tablename,
     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

### Performance Optimization

1. **JSONB GIN Indexes:**
   - `traces.trace_metadata` has GIN indexes on `parent_trace_id` and `source`
   - `trace_evaluations.vendor_metrics` and `llm_metadata` have GIN indexes
   - Consider adding GIN indexes for frequently queried JSONB fields

2. **Composite Indexes:**
   - `(organization_id, created_at DESC)` for time-series queries
   - `(user_id, created_at DESC)` for user-specific queries

3. **Partitioning:**
   - Consider partitioning `traces` and `spans` by date for large-scale deployments
   - Consider partitioning `call_insights_analysis` by organization for multi-tenant isolation

---

## Security Considerations

1. **Encrypted Fields:**
   - `model_provider_configs.api_key_encrypted` stores encrypted API keys
   - `model_provider_configs.config_encrypted` stores encrypted configuration
   - Encryption keys stored in `encryption_keys` table

2. **API Key Hashing:**
   - `model_provider_configs.api_key_hash` stores SHA-256 hash for deduplication
   - Never store plaintext API keys

3. **Row-Level Security:**
   - All tables have `organization_id` for multi-tenant isolation
   - Consider PostgreSQL RLS policies for additional security

4. **Audit Logging:**
   - All tables have `created_at` and `updated_at` timestamps
   - `created_by` fields track user actions
   - Consider adding audit log table for sensitive operations

---

## Future Enhancements

1. **Caching Layer:**
   - Add Redis caching for frequently accessed traces and analyses
   - Cache model catalog entries for faster lookups

2. **Archiving:**
   - Implement time-based archiving for old traces and analyses
   - Move archived data to cold storage

3. **Analytics:**
   - Add materialized views for dashboard queries
   - Pre-aggregate cost and token metrics by organization/project

4. **Full-Text Search:**
   - Add `tsvector` columns for transcript and output search
   - Implement PostgreSQL full-text search or Elasticsearch integration

---

## Contact & Support

For schema changes or questions, contact:
- **DB Architect Agent:** Updates this document as schema evolves
- **API Architect Agent:** Defines data models and relationships
- **Migration Tool:** Alembic (see `/alembic/versions/` for migration history)

---

**End of Document**
