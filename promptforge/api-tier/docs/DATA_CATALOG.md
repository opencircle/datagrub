# PromptForge Data Catalog

**Version:** 1.0.0
**Last Updated:** 2025-10-12
**Database:** PostgreSQL 14+
**Schema Owner:** DB Architect Agent
**Status:** Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Data Catalog Structure](#data-catalog-structure)
3. [Entity Catalog](#entity-catalog)
   - [Core Domain](#core-domain)
   - [Insights Domain](#insights-domain)
   - [Observability Domain](#observability-domain)
   - [Evaluation Domain](#evaluation-domain)
   - [Model Management Domain](#model-management-domain)
   - [Prompt Management Domain](#prompt-management-domain)
   - [Compliance Domain](#compliance-domain)
4. [Data Relationships](#data-relationships)
5. [Data Quality Rules](#data-quality-rules)
6. [Data Lifecycle](#data-lifecycle)
7. [Index Catalog](#index-catalog)
8. [JSONB Field Catalog](#jsonb-field-catalog)
9. [Data Access Patterns](#data-access-patterns)
10. [Data Governance](#data-governance)

---

## Overview

The PromptForge Data Catalog provides a comprehensive inventory of all data entities, their attributes, relationships, and governance policies. This catalog serves as the authoritative source of truth for understanding the database schema, data flows, and data quality requirements.

### Key Design Principles

1. **Multi-Tenancy**: All data is organization-scoped with strict RBAC
2. **Audit Trail**: Comprehensive timestamps and user tracking
3. **Flexible Metadata**: JSONB fields for extensibility
4. **Referential Integrity**: Foreign keys with appropriate CASCADE/SET NULL policies
5. **Performance**: Strategic indexing for common query patterns
6. **Data Security**: Encryption at rest for sensitive fields

### Domain Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORE DOMAIN (Multi-Tenancy)                  │
│  organizations ──┬── users                                      │
│                  ├── projects ──┬── prompts                     │
│                  │              ├── traces                      │
│                  │              ├── call_insights_analysis      │
│                  │              ├── policies                    │
│                  │              └── evaluation_catalog          │
│                  └── groups                                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
┌───▼──────────────────┐  ┌────────▼────────────┐  ┌──────────────▼──────┐
│  INSIGHTS DOMAIN     │  │ OBSERVABILITY       │  │ EVALUATION DOMAIN   │
│  - Call Insights     │  │ - Traces            │  │ - Evaluation Catalog│
│  - Comparisons       │  │ - Spans             │  │ - Trace Evaluations │
│  - Judge Results     │  │ - Parent/Child      │  │ - Results           │
└──────────────────────┘  └─────────────────────┘  └─────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
┌───▼──────────────────┐  ┌────────▼────────────┐  ┌──────────────▼──────┐
│  MODEL MANAGEMENT    │  │ PROMPT MANAGEMENT   │  │ COMPLIANCE DOMAIN   │
│  - Model Catalog     │  │ - Prompts           │  │ - Policies          │
│  - Provider Metadata │  │ - Versions          │  │ - Violations        │
│  - Provider Configs  │  │ - Variables         │  │ - Audit Trail       │
└──────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

---

## Data Catalog Structure

Each entity in the catalog includes:

- **Entity Name**: Table name
- **Domain**: Business domain classification
- **Description**: Purpose and use cases
- **Cardinality**: Expected row counts
- **Retention**: Data retention policy
- **Attributes**: Column catalog with types, constraints, and business rules
- **Relationships**: Foreign key relationships
- **Indexes**: Performance indexes
- **Access Pattern**: Common query patterns

---

## Entity Catalog

### Core Domain

#### 1. Organizations

**Domain**: Core
**Description**: Multi-tenant organizations that own all data
**Cardinality**: 100-1000 (B2B SaaS)
**Retention**: Permanent (soft delete recommended)
**PII**: Name may contain PII
**RBAC**: Admin-only access

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK, NOT NULL | Immutable unique identifier | `a1b2c3d4-...` |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE | Organization display name | `Acme Corp` |
| `description` | VARCHAR(1000) | NULLABLE | Optional description | `AI consulting firm` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-01 08:00:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:30:00` |

**Relationships**:
- 1:N with `users` (organization can have many users)
- 1:N with `projects` (organization can have many projects)
- 1:N with `groups` (organization can have many groups)
- 1:N with `call_insights_analysis` (organization owns analyses)
- 1:N with `insight_comparisons` (organization owns comparisons)
- 1:N with `model_provider_configs` (organization has provider configs)
- 1:N with `evaluation_catalog` (organization has custom evaluations)
- 1:N with `trace_evaluations` (organization owns evaluation results)

**Indexes**:
- Primary key on `id`
- Unique index on `name`

**Access Patterns**:
- Lookup by ID for RBAC checks (high frequency)
- Lookup by name for login/signup (low frequency)
- List all organizations for admin dashboard (low frequency)

**Data Quality Rules**:
- Name must be unique across all organizations
- Name must not be empty or contain only whitespace
- Created_at must be before updated_at

---

#### 2. Users

**Domain**: Core
**Description**: Application users with role-based access control
**Cardinality**: 1000-10,000 per organization
**Retention**: 7 years after account deletion (GDPR compliance)
**PII**: Email, full_name, hashed_password
**RBAC**: Self-read, admin-full

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK, NOT NULL | Immutable unique identifier | `e5f6g7h8-...` |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Must be valid email format | `john@acme.com` |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hash, never plaintext | `$2b$12$...` |
| `full_name` | VARCHAR(255) | NULLABLE | User display name | `John Doe` |
| `is_active` | BOOLEAN | NOT NULL | Account status | `true` |
| `role` | ENUM(UserRole) | NOT NULL | Access level: admin, developer, viewer | `developer` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `created_at` | TIMESTAMP | NOT NULL | Account creation time | `2025-10-01 08:00:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:30:00` |

**Enums**:
```python
UserRole = Enum('admin', 'developer', 'viewer')
```

**Relationships**:
- N:1 with `organizations` (user belongs to one organization)
- 1:N with `projects` (user creates projects)
- 1:N with `prompts` (user creates prompts)
- 1:N with `call_insights_analysis` (user creates analyses)
- 1:N with `insight_comparisons` (user creates comparisons)
- 1:N with `traces` (user creates traces)
- 1:N with `model_provider_configs` (user configures providers)
- 1:N with `evaluation_catalog` (user creates custom evaluations)
- 1:N with `policy_violations` (user resolves violations)

**Indexes**:
- Primary key on `id`
- Unique index on `email`
- Index on `organization_id`

**Access Patterns**:
- Lookup by email for login (high frequency)
- Lookup by ID for RBAC checks (high frequency)
- List users by organization (medium frequency)
- Filter active users (medium frequency)

**Data Quality Rules**:
- Email must be unique across all users
- Email must be valid format (RFC 5322)
- Password must be bcrypt hashed (strength validation at API layer)
- is_active must be explicitly set (no default)
- role must be one of: admin, developer, viewer

**Security Considerations**:
- PII field: Email, full_name must be encrypted at rest
- Hashed passwords use bcrypt with cost factor 12
- Soft delete recommended (set is_active=false) to preserve audit trail

---

#### 3. Projects

**Domain**: Core
**Description**: Projects organize prompts, traces, and analyses within an organization
**Cardinality**: 10-100 per organization
**Retention**: 5 years after archival
**PII**: None
**RBAC**: Organization-scoped with group-based access

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK, NOT NULL | Immutable unique identifier | `p1r2o3j4-...` |
| `name` | VARCHAR(255) | NOT NULL | Project display name | `Customer Support Bot` |
| `description` | TEXT | NULLABLE | Optional project description | `Analyzes support tickets` |
| `status` | VARCHAR(50) | NOT NULL | active, archived, deleted | `active` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `created_by` | UUID | FK, NOT NULL | User who created the project | `e5f6g7h8-...` |
| `access_level` | VARCHAR(50) | NOT NULL, DEFAULT 'organization' | Access control: organization, group, user | `organization` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-01 08:00:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:30:00` |

**Relationships**:
- N:1 with `organizations` (project belongs to one organization)
- N:1 with `users` (project created by one user)
- 1:N with `prompts` (project has many prompts)
- 1:N with `traces` (project has many traces)
- 1:N with `call_insights_analysis` (project has many analyses)
- 1:N with `model_provider_configs` (project has provider overrides)
- 1:N with `evaluation_catalog` (project has custom evaluations)
- 1:N with `policies` (project has governance policies)
- N:M with `groups` via `project_groups` (project shared with groups)

**Indexes**:
- Primary key on `id`
- Index on `organization_id`
- Index on `created_by`
- Index on `status`

**Access Patterns**:
- List projects by organization (high frequency)
- Lookup project by ID for RBAC (high frequency)
- Filter projects by status (medium frequency)
- Search projects by name (low frequency)

**Data Quality Rules**:
- name must not be empty
- status must be one of: active, archived, deleted
- access_level must be one of: organization, group, user
- organization_id and created_by must reference valid records

---

#### 4. Groups

**Domain**: Core
**Description**: User groups for granular access control
**Cardinality**: 5-50 per organization
**Retention**: Permanent
**PII**: None
**RBAC**: Admin-only

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Immutable unique identifier | `g1r2o3u4-...` |
| `name` | VARCHAR(255) | NOT NULL | Group display name | `Data Science Team` |
| `description` | TEXT | NULLABLE | Optional group description | `ML engineers and researchers` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation time | `2025-10-01 08:00:00+00` |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last modification time | `2025-10-12 14:30:00+00` |

**Relationships**:
- N:1 with `organizations` (group belongs to one organization)
- N:M with `users` via `user_groups` (group has many users)
- N:M with `projects` via `project_groups` (group has access to many projects)

**Indexes**:
- Primary key on `id`
- Index on `organization_id`
- Unique constraint on `(organization_id, name)`

**Access Patterns**:
- List groups by organization (medium frequency)
- Check user group membership (high frequency for RBAC)
- List projects accessible by group (high frequency)

**Data Quality Rules**:
- name must be unique within organization
- organization_id must reference valid organization

---

### Insights Domain

#### 5. Call Insights Analysis

**Domain**: Insights
**Description**: Main insights storage for 3-stage DTA pipeline (Facts → Insights → Summary)
**Cardinality**: 1,000-100,000 per organization
**Retention**: 2 years (archive older data)
**PII**: Transcript may contain PII (configurable redaction)
**RBAC**: Organization-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `c1a2l3l4-...` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `user_id` | UUID | FK, NOT NULL | User who created the analysis | `e5f6g7h8-...` |
| `project_id` | UUID | FK, NULLABLE | Associated project (optional) | `p1r2o3j4-...` |
| `transcript_title` | VARCHAR(500) | NULLABLE | Title or identifier for transcript | `Q3 Sales Call - Acme` |
| `transcript_input` | TEXT | NOT NULL | Original transcript text (may be redacted) | `[REDACTED]...` |
| `facts_output` | TEXT | NOT NULL | Stage 1: Extracted facts | `- Customer needs...` |
| `insights_output` | TEXT | NOT NULL | Stage 2: Reasoned insights | `Customer pain point...` |
| `summary_output` | TEXT | NOT NULL | Stage 3: Final summary | `Key takeaways: ...` |
| `pii_redacted` | BOOLEAN | NOT NULL, DEFAULT false | Whether PII was redacted | `true` |
| `stage_params` | JSONB | NULLABLE | Model parameters per stage | `{"fact_extraction": {...}}` |
| `parent_trace_id` | UUID | FK, NULLABLE | Parent trace for observability | `t1r2a3c4-...` |
| `total_tokens` | INTEGER | NOT NULL, DEFAULT 0 | Total tokens across all stages | `7523` |
| `total_cost` | DOUBLE PRECISION | NOT NULL, DEFAULT 0 | Total cost in USD | `0.00205` |
| `total_duration_ms` | DOUBLE PRECISION | NULLABLE | Total execution time in milliseconds | `12345.67` |
| `analysis_metadata` | JSONB | NULLABLE | Additional metadata | `{"stage_count": 3}` |
| `system_prompt_stage1` | TEXT | NULLABLE | System prompt for Stage 1 (fact extraction) | `Extract key facts...` |
| `system_prompt_stage2` | TEXT | NULLABLE | System prompt for Stage 2 (insights) | `Generate insights...` |
| `system_prompt_stage3` | TEXT | NULLABLE | System prompt for Stage 3 (summary) | `Synthesize summary...` |
| `model_stage1` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 1 | `gpt-4o-mini` |
| `model_stage2` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 2 | `gpt-4o` |
| `model_stage3` | VARCHAR(100) | DEFAULT 'gpt-4o-mini' | Model used for Stage 3 | `gpt-4o-mini` |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation time | `2025-10-12 14:30:00+00` |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Last modification time | `2025-10-12 14:35:00+00` |

**Relationships**:
- N:1 with `organizations` (analysis belongs to one organization)
- N:1 with `users` (analysis created by one user)
- N:1 with `projects` (analysis belongs to one project, optional)
- N:1 with `traces` (analysis has parent trace for observability)
- 1:N with `insight_comparisons` (analysis can be compared with others)

**Indexes**:
- Primary key on `id`
- Index on `organization_id`
- Index on `project_id`
- Index on `created_at`
- Index on `transcript_title`

**Access Patterns**:
- List analyses by organization (high frequency)
- Filter analyses by date range (high frequency)
- Filter analyses by model (medium frequency for comparisons)
- Full-text search on transcript_title (low frequency)

**Data Quality Rules**:
- transcript_input must not be empty
- facts_output, insights_output, summary_output must not be empty
- total_tokens >= 0
- total_cost >= 0
- model_stage1, model_stage2, model_stage3 must be valid model names from model_catalog
- parent_trace_id must reference valid trace if present

**JSONB Fields**: See [JSONB Field Catalog](#jsonb-field-catalog)

**Security Considerations**:
- PII in transcript_input must be redacted if pii_redacted=true
- Consider encryption at rest for transcript_input

---

#### 6. Insight Comparisons

**Domain**: Insights
**Description**: Blind comparison results between two insight analyses using a judge model
**Cardinality**: 100-10,000 per organization
**Retention**: 1 year
**PII**: None
**RBAC**: Organization-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Immutable unique identifier | `i1n2s3i4-...` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `user_id` | UUID | FK, NOT NULL | User who created comparison | `e5f6g7h8-...` |
| `analysis_a_id` | UUID | FK, NOT NULL, CASCADE | First analysis being compared | `c1a2l3l4-...` |
| `analysis_b_id` | UUID | FK, NOT NULL, CASCADE | Second analysis being compared | `c5a6l7l8-...` |
| `judge_model` | VARCHAR(100) | NOT NULL, DEFAULT 'claude-sonnet-4.5' | Judge model identifier | `claude-sonnet-4.5` |
| `judge_model_version` | VARCHAR(200) | NULLABLE | Exact API version | `claude-sonnet-4-5-20250929` |
| `evaluation_criteria` | JSONB | NOT NULL | List of evaluation criteria | `["groundedness", ...]` |
| `overall_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Overall winner | `A` |
| `overall_reasoning` | TEXT | NOT NULL | Overall reasoning for winner | `Analysis A is more...` |
| `stage1_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 1 (facts) winner | `B` |
| `stage1_scores` | JSONB | NULLABLE | Stage 1 scores per criterion | `{"A": {...}, "B": {...}}` |
| `stage1_reasoning` | TEXT | NULLABLE | Stage 1 reasoning | `Facts in B are more...` |
| `stage2_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 2 (insights) winner | `A` |
| `stage2_scores` | JSONB | NULLABLE | Stage 2 scores per criterion | `{"A": {...}, "B": {...}}` |
| `stage2_reasoning` | TEXT | NULLABLE | Stage 2 reasoning | `Insights in A are...` |
| `stage3_winner` | VARCHAR(1) | CHECK: 'A', 'B', 'tie' | Stage 3 (summary) winner | `tie` |
| `stage3_scores` | JSONB | NULLABLE | Stage 3 scores per criterion | `{"A": {...}, "B": {...}}` |
| `stage3_reasoning` | TEXT | NULLABLE | Stage 3 reasoning | `Both summaries are...` |
| `judge_trace_id` | UUID | FK, NULLABLE | Trace of judge model invocation | `t1r2a3c4-...` |
| `comparison_metadata` | JSONB | NULLABLE | Judge metrics (cost, tokens, duration) | `{"total_cost": 0.103}` |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Record creation time | `2025-10-12 14:30:00+00` |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Last modification time | `2025-10-12 14:35:00+00` |

**Relationships**:
- N:1 with `organizations` (comparison belongs to one organization)
- N:1 with `users` (comparison created by one user)
- N:1 with `call_insights_analysis` as analysis_a_id (CASCADE delete)
- N:1 with `call_insights_analysis` as analysis_b_id (CASCADE delete)
- N:1 with `traces` (comparison has judge trace for observability)

**Indexes**:
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

**Access Patterns**:
- List comparisons by organization (high frequency)
- List comparisons by user (medium frequency)
- Lookup comparison by analysis pair (medium frequency)
- Filter comparisons by judge model (low frequency)

**Data Quality Rules**:
- analysis_a_id != analysis_b_id (no self-comparison)
- overall_winner must be 'A', 'B', or 'tie'
- stage1_winner, stage2_winner, stage3_winner must be 'A', 'B', or 'tie' if present
- judge_model must be valid model name from model_catalog
- evaluation_criteria must be non-empty array
- overall_reasoning must not be empty

**JSONB Fields**: See [JSONB Field Catalog](#jsonb-field-catalog)

---

### Observability Domain

#### 7. Traces

**Domain**: Observability
**Description**: OpenTelemetry-compatible traces for LLM calls and workflows
**Cardinality**: 10,000-1,000,000 per organization
**Retention**: 90 days (archive older data)
**PII**: Input/output may contain PII
**RBAC**: Organization-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Internal unique identifier | `t1r2a3c4-...` |
| `trace_id` | VARCHAR(255) | NOT NULL, UNIQUE | OpenTelemetry trace ID | `otel-trace-123` |
| `name` | VARCHAR(255) | NOT NULL | Trace name | `generate-insights` |
| `status` | VARCHAR(50) | NULLABLE | Trace status: ok, error, etc. | `ok` |
| `input_data` | JSON | NULLABLE | Input data (prompt, params) | `{"prompt": "..."}` |
| `output_data` | JSON | NULLABLE | Output data (response) | `{"response": "..."}` |
| `trace_metadata` | JSON | NULLABLE | Additional metadata | `{"intent": "summarization"}` |
| `total_duration_ms` | DOUBLE PRECISION | NULLABLE | Total execution time | `12345.67` |
| `total_tokens` | INTEGER | NULLABLE | Total tokens used | `7523` |
| `input_tokens` | INTEGER | NULLABLE | Input tokens | `5000` |
| `output_tokens` | INTEGER | NULLABLE | Output tokens | `2523` |
| `total_cost` | DOUBLE PRECISION | NULLABLE | Total cost in USD | `0.00205` |
| `error_message` | TEXT | NULLABLE | Error message if failed | `Model timeout` |
| `error_type` | VARCHAR(100) | NULLABLE | Error type | `timeout` |
| `project_id` | UUID | FK, NOT NULL | Associated project | `p1r2o3j4-...` |
| `prompt_version_id` | UUID | FK, NULLABLE | Prompt version used | `pv1234-...` |
| `model_id` | UUID | FK, NULLABLE | Model used (legacy) | `m1o2d3e4-...` |
| `model_name` | VARCHAR(100) | NULLABLE | Model name | `gpt-4o-mini` |
| `provider` | VARCHAR(100) | NULLABLE | Provider name | `openai` |
| `user_id` | UUID | FK, SET NULL | User who created the trace | `e5f6g7h8-...` |
| `environment` | VARCHAR(50) | NULLABLE | Environment: dev, staging, prod | `prod` |
| `retry_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of retries | `0` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `projects` (trace belongs to one project)
- N:1 with `users` (trace created by one user, SET NULL on user delete)
- N:1 with `prompt_versions` (trace uses one prompt version)
- N:1 with `ai_models` (trace uses one model, legacy)
- 1:N with `spans` (trace has many child spans)
- 1:N with `call_insights_analysis` (trace has many analyses)
- 1:N with `insight_comparisons` (trace used for judge invocations)
- 1:N with `policy_violations` (trace may have violations)
- 1:N with `trace_evaluations` (trace has evaluation results)

**Indexes**:
- Primary key on `id`
- Unique index on `trace_id`
- Index on `model_name`
- Index on `provider`
- Index on `environment`
- Index on `user_id`
- GIN index on `(trace_metadata->>'parent_trace_id')` where trace_metadata IS NOT NULL
- GIN index on `(trace_metadata->>'source')` where trace_metadata IS NOT NULL

**Access Patterns**:
- Lookup by trace_id (high frequency for observability)
- List traces by project (high frequency)
- Filter traces by model_name (medium frequency)
- Filter traces by date range (high frequency)
- Search traces by metadata (low frequency)

**Data Quality Rules**:
- trace_id must be unique across all traces
- name must not be empty
- status must be one of: ok, error, timeout, cancelled
- total_tokens = input_tokens + output_tokens (if all present)
- total_cost >= 0
- retry_count >= 0
- model_name should reference model_catalog.model_name

**JSONB Fields**: See [JSONB Field Catalog](#jsonb-field-catalog)

**Security Considerations**:
- PII in input_data and output_data should be redacted or encrypted
- Error messages should not contain sensitive information

---

#### 8. Spans

**Domain**: Observability
**Description**: Child spans of traces representing individual LLM calls or operations
**Cardinality**: 30,000-3,000,000 per organization (3 spans per trace avg)
**Retention**: 90 days (archive older data)
**PII**: Input/output may contain PII
**RBAC**: Organization-scoped via parent trace

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Internal unique identifier | `s1p2a3n4-...` |
| `span_id` | VARCHAR(255) | NOT NULL, UNIQUE | OpenTelemetry span ID | `otel-span-456` |
| `parent_span_id` | VARCHAR(255) | NULLABLE | Parent span ID (for nested spans) | `otel-span-123` |
| `trace_id` | UUID | FK, NOT NULL | Parent trace | `t1r2a3c4-...` |
| `name` | VARCHAR(255) | NOT NULL | Span name | `stage1-fact-extraction` |
| `span_type` | VARCHAR(50) | NULLABLE | Span type: llm, tool, workflow | `llm` |
| `start_time` | DOUBLE PRECISION | NOT NULL | Start time (Unix timestamp) | `1697123456.789` |
| `end_time` | DOUBLE PRECISION | NULLABLE | End time (Unix timestamp) | `1697123466.789` |
| `duration_ms` | DOUBLE PRECISION | NULLABLE | Duration in milliseconds | `10000.0` |
| `input_data` | JSON | NULLABLE | Input data | `{"prompt": "..."}` |
| `output_data` | JSON | NULLABLE | Output data | `{"response": "..."}` |
| `span_metadata` | JSON | NULLABLE | Additional metadata | `{"stage": 1}` |
| `model_name` | VARCHAR(100) | NULLABLE | Model used for this span | `gpt-4o-mini` |
| `prompt_tokens` | INTEGER | NULLABLE | Input tokens | `5000` |
| `completion_tokens` | INTEGER | NULLABLE | Output tokens | `2523` |
| `total_tokens` | INTEGER | NULLABLE | Total tokens | `7523` |
| `temperature` | DOUBLE PRECISION | NULLABLE | Temperature parameter | `0.25` |
| `max_tokens` | INTEGER | NULLABLE | Max tokens parameter | `1000` |
| `status` | VARCHAR(50) | NULLABLE | Span status | `ok` |
| `error_message` | TEXT | NULLABLE | Error message if failed | `Model timeout` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `traces` (span belongs to one trace)
- 1:N with `spans` (span can have child spans via parent_span_id)

**Indexes**:
- Primary key on `id`
- Unique index on `span_id`
- Index on `parent_span_id`
- Index on `trace_id`

**Access Patterns**:
- List spans by trace_id (high frequency)
- Lookup by span_id (medium frequency)
- List child spans by parent_span_id (medium frequency)

**Data Quality Rules**:
- span_id must be unique across all spans
- name must not be empty
- start_time < end_time (if end_time present)
- duration_ms = (end_time - start_time) * 1000 (if both present)
- total_tokens = prompt_tokens + completion_tokens (if all present)
- trace_id must reference valid trace

---

### Evaluation Domain

#### 9. Evaluation Catalog

**Domain**: Evaluation
**Description**: Catalog of available evaluations (LLM-as-Judge, custom, vendor-specific)
**Cardinality**: 100-1000 per organization
**Retention**: Permanent
**PII**: None
**RBAC**: Organization-scoped, public evals visible to all

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `e1v2a3l4-...` |
| `name` | VARCHAR(255) | NOT NULL | Evaluation name | `Faithfulness` |
| `description` | TEXT | NULLABLE | Evaluation description | `Measures factual accuracy` |
| `category` | ENUM(EvaluationCategory) | NOT NULL | Category | `accuracy` |
| `source` | ENUM(EvaluationSource) | NOT NULL | Source: builtin, custom, vendor | `builtin` |
| `evaluation_type` | ENUM(EvaluationType) | NOT NULL | Type | `llm_as_judge` |
| `organization_id` | UUID | FK, NULLABLE | Organization (for custom evals) | `a1b2c3d4-...` |
| `project_id` | UUID | FK, NULLABLE | Project (for custom evals) | `p1r2o3j4-...` |
| `is_public` | BOOLEAN | NOT NULL | Whether evaluation is publicly available | `true` |
| `config_schema` | JSON | NULLABLE | JSON schema for configuration | `{"type": "object", ...}` |
| `default_config` | JSON | NULLABLE | Default configuration values | `{"threshold": 0.5}` |
| `implementation` | TEXT | NULLABLE | Implementation code (for custom evals) | `def evaluate(...):` |
| `adapter_class` | VARCHAR(255) | NULLABLE | Adapter class name (for vendor evals) | `RagasFaithfulnessAdapter` |
| `adapter_evaluation_id` | VARCHAR(255) | NULLABLE | Vendor's evaluation ID | `ragas_faithfulness` |
| `vendor_name` | VARCHAR(100) | NULLABLE | Display name of vendor | `Ragas` |
| `llm_criteria` | TEXT | NULLABLE | Evaluation criteria for LLM-as-Judge | `Is the response...` |
| `llm_model` | VARCHAR(100) | NULLABLE | Model to use for LLM-as-Judge | `claude-sonnet-4.5` |
| `llm_system_prompt` | TEXT | NULLABLE | System prompt for LLM-as-Judge | `You are an evaluator...` |
| `prompt_input` | TEXT | NULLABLE | Input prompt template | `Evaluate the following...` |
| `prompt_output` | TEXT | NULLABLE | Expected output schema | `{"score": 0.0-1.0}` |
| `custom_system_prompt` | TEXT | NULLABLE | System prompt for custom evals | `Evaluate based on...` |
| `version` | VARCHAR(50) | NULLABLE | Evaluation version | `1.0.0` |
| `is_active` | BOOLEAN | NOT NULL | Whether evaluation is active | `true` |
| `tags` | JSON | NULLABLE | Tags for categorization | `["rag", "accuracy"]` |
| `created_by` | UUID | FK, NULLABLE | User who created this evaluation | `e5f6g7h8-...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Enums**:
```python
EvaluationCategory = Enum('accuracy', 'relevance', 'safety', 'quality', 'coherence', 'custom')
EvaluationSource = Enum('builtin', 'custom', 'vendor')
EvaluationType = Enum('llm_as_judge', 'rule_based', 'heuristic', 'model_based')
```

**Relationships**:
- N:1 with `organizations` (custom eval belongs to one organization)
- N:1 with `projects` (custom eval belongs to one project)
- N:1 with `users` (eval created by one user)
- 1:N with `trace_evaluations` (eval used in many evaluation results)

**Indexes**:
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

**Access Patterns**:
- List evaluations by category (high frequency)
- Filter evaluations by source (medium frequency)
- Lookup evaluation by ID (high frequency)
- Search evaluations by name (low frequency)

**Data Quality Rules**:
- name must not be empty
- category must be one of defined enum values
- source must be one of defined enum values
- evaluation_type must be one of defined enum values
- If source = 'custom', organization_id must be set
- If source = 'builtin', is_public must be true
- adapter_class and adapter_evaluation_id must both be set for vendor evals
- llm_model must reference model_catalog.model_name if present

---

#### 10. Trace Evaluations

**Domain**: Evaluation
**Description**: Evaluation results for traces
**Cardinality**: 100,000-10,000,000 per organization
**Retention**: 1 year
**PII**: Reason may contain PII from trace
**RBAC**: Organization-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `te1234-...` |
| `trace_id` | UUID | FK, NOT NULL | Trace being evaluated | `t1r2a3c4-...` |
| `evaluation_catalog_id` | UUID | FK, NOT NULL | Evaluation used | `e1v2a3l4-...` |
| `organization_id` | UUID | FK, NOT NULL | Parent organization | `a1b2c3d4-...` |
| `score` | DOUBLE PRECISION | NULLABLE | Evaluation score (0.0 - 1.0) | `0.88` |
| `passed` | BOOLEAN | NULLABLE | Whether evaluation passed | `true` |
| `category` | VARCHAR(255) | NULLABLE | Evaluation category | `accuracy` |
| `reason` | TEXT | NULLABLE | Evaluation reasoning | `Response is accurate...` |
| `details` | JSON | NULLABLE | Detailed results | `{"metrics": {...}}` |
| `suggestions` | JSON | NULLABLE | Improvement suggestions | `["Consider adding..."]` |
| `execution_time_ms` | DOUBLE PRECISION | NULLABLE | Evaluation execution time | `2345.67` |
| `model_used` | VARCHAR(100) | NULLABLE | Model used (if LLM-as-Judge) | `claude-sonnet-4.5` |
| `input_tokens` | INTEGER | NULLABLE | Input tokens (if LLM-as-Judge) | `1234` |
| `output_tokens` | INTEGER | NULLABLE | Output tokens (if LLM-as-Judge) | `567` |
| `total_tokens` | INTEGER | NULLABLE | Total tokens (if LLM-as-Judge) | `1801` |
| `evaluation_cost` | DOUBLE PRECISION | NULLABLE | Cost of evaluation in USD | `0.0123` |
| `config` | JSON | NULLABLE | Configuration used | `{"threshold": 0.5}` |
| `status` | VARCHAR(50) | NOT NULL | Evaluation status | `completed` |
| `error_message` | TEXT | NULLABLE | Error message if failed | `Evaluation timeout` |
| `vendor_metrics` | JSONB | NULLABLE | Vendor-specific metrics | `{"ragas_score": 0.9}` |
| `llm_metadata` | JSONB | NULLABLE | Comprehensive LLM metrics | `{"model": "...", ...}` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `traces` (evaluation result for one trace)
- N:1 with `evaluation_catalog` (evaluation result uses one evaluation)
- N:1 with `organizations` (evaluation result belongs to one organization)

**Indexes**:
- Primary key on `id`
- Index on `trace_id`
- Index on `evaluation_catalog_id`
- Index on `organization_id`
- Composite index on `(organization_id, created_at DESC)`
- Index on `model_used`
- Index on `created_at DESC`
- GIN index on `vendor_metrics`
- GIN index on `llm_metadata`

**Access Patterns**:
- List evaluations by trace (high frequency)
- Filter evaluations by catalog (medium frequency)
- Aggregate scores by evaluation type (medium frequency)
- Search vendor_metrics (low frequency)

**Data Quality Rules**:
- score must be between 0.0 and 1.0 if present
- status must be one of: completed, failed, running, cancelled
- total_tokens = input_tokens + output_tokens (if all present for LLM-as-Judge)
- evaluation_cost >= 0
- model_used should reference model_catalog.model_name if present

**JSONB Fields**: See [JSONB Field Catalog](#jsonb-field-catalog)

---

### Model Management Domain

#### 11. Model Catalog

**Domain**: Model Management
**Description**: Centralized catalog of AI models with pricing, capabilities, and compatibility
**Cardinality**: 50-200 models
**Retention**: Permanent
**PII**: None
**RBAC**: Public read, admin write

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `mc1234-...` |
| `model_name` | VARCHAR(100) | NOT NULL, UNIQUE | Model name | `gpt-4o-mini` |
| `model_version` | VARCHAR(200) | NOT NULL | Exact API version | `gpt-4o-mini-2024-07-18` |
| `provider_name` | VARCHAR(100) | NOT NULL | Provider | `openai` |
| `model_family` | VARCHAR(100) | NOT NULL | Model family | `gpt-4` |
| `display_name` | VARCHAR(255) | NOT NULL | Human-readable name | `GPT-4o Mini` |
| `description` | TEXT | NULLABLE | Model description | `Cost-effective GPT-4o` |
| `context_window` | JSON | NULLABLE | Context window limits | `{"input": 128000, ...}` |
| `capabilities` | JSON | NULLABLE | Model capabilities | `["text", "vision"]` |
| `pricing` | JSON | NULLABLE | Pricing per million tokens | `{"input": 0.15, ...}` |
| `is_active` | BOOLEAN | NOT NULL | Currently available | `true` |
| `is_deprecated` | BOOLEAN | NOT NULL | Deprecated status | `false` |
| `is_recommended` | BOOLEAN | NOT NULL | Recommended for use | `true` |
| `release_date` | TIMESTAMP | NULLABLE | Model release date | `2024-07-18` |
| `deprecation_date` | TIMESTAMP | NULLABLE | Model deprecation date | `null` |
| `notes` | TEXT | NULLABLE | Additional notes | `Uses legacy max_tokens` |
| `documentation_url` | VARCHAR(500) | NULLABLE | Documentation URL | `https://...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Check Constraints**:
- `model_name != ''`
- `model_version != ''`
- `provider_name IN ('openai', 'anthropic', 'google', 'cohere', 'mistral')`

**Relationships**:
- 1:N with pricing lookups in API layer (model_name referenced by traces, evaluations, etc.)

**Indexes**:
- Primary key on `id`
- Unique index on `model_name`
- Index on `provider_name`
- Index on `is_active`

**Access Patterns**:
- Lookup model by name (high frequency)
- List active models by provider (high frequency)
- Filter recommended models (medium frequency)
- Check if model is deprecated (high frequency)

**Data Quality Rules**:
- model_name must be unique across all models
- provider_name must be one of supported providers
- is_active, is_deprecated, is_recommended must be explicitly set
- release_date should be set for all active models
- deprecation_date must be after release_date if both present

---

#### 12. Model Provider Metadata

**Domain**: Model Management
**Description**: Metadata for model providers (configuration templates, capabilities)
**Cardinality**: 10-50 providers
**Retention**: Permanent
**PII**: None
**RBAC**: Public read, admin write

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `mpm123-...` |
| `provider_name` | VARCHAR(100) | NOT NULL, UNIQUE | Provider name | `openai` |
| `provider_type` | VARCHAR(50) | NOT NULL | Provider type | `llm` |
| `display_name` | VARCHAR(255) | NOT NULL | Human-readable name | `OpenAI` |
| `description` | TEXT | NULLABLE | Provider description | `Leading AI research lab` |
| `icon_url` | VARCHAR(500) | NULLABLE | Provider icon URL | `https://...` |
| `documentation_url` | VARCHAR(500) | NULLABLE | Provider documentation | `https://platform.openai.com/docs` |
| `required_fields` | JSONB | NULLABLE | Required config fields | `{"api_key": "string"}` |
| `optional_fields` | JSONB | NULLABLE | Optional config fields | `{"organization": "string"}` |
| `default_config` | JSONB | NULLABLE | Default configuration | `{"timeout": 30}` |
| `capabilities` | JSONB | NULLABLE | Provider capabilities | `["text", "vision"]` |
| `supported_models` | JSONB | NULLABLE | List of supported models | `["gpt-4o", ...]` |
| `api_key_pattern` | VARCHAR(255) | NULLABLE | Regex for API key validation | `^sk-[A-Za-z0-9]{48}$` |
| `api_key_prefix` | VARCHAR(20) | NULLABLE | API key prefix | `sk-` |
| `is_active` | BOOLEAN | NULLABLE | Provider is active | `true` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- 1:N with `model_provider_configs` (metadata used for validation)

**Indexes**:
- Primary key on `id`
- Unique index on `provider_name`
- Index on `provider_type`
- Index on `is_active`

**Access Patterns**:
- Lookup provider by name (high frequency)
- List active providers by type (medium frequency)
- Validate API key format (high frequency)

**Data Quality Rules**:
- provider_name must be unique and not empty
- provider_type must be one of: llm, embedding, image, audio, multimodal
- api_key_pattern must be valid regex if present

---

#### 13. Model Provider Configs

**Domain**: Model Management
**Description**: User-configured model provider credentials and settings (encrypted)
**Cardinality**: 100-1000 per organization
**Retention**: Until user deletes
**PII**: API keys (encrypted)
**RBAC**: Organization-scoped, user-created

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `mpc123-...` |
| `organization_id` | UUID | FK, NOT NULL, CASCADE | Parent organization | `a1b2c3d4-...` |
| `project_id` | UUID | FK, CASCADE | Associated project (optional) | `p1r2o3j4-...` |
| `provider_name` | VARCHAR(100) | NOT NULL | Provider name | `openai` |
| `provider_type` | VARCHAR(50) | NOT NULL | Provider type | `llm` |
| `display_name` | VARCHAR(255) | NULLABLE | Custom display name | `OpenAI Production` |
| `api_key_encrypted` | TEXT | NOT NULL | Encrypted API key | `encrypted_blob` |
| `api_key_hash` | VARCHAR(128) | NOT NULL | SHA-256 hash for dedup | `sha256_hash` |
| `config_encrypted` | TEXT | NULLABLE | Encrypted additional config | `encrypted_blob` |
| `is_active` | BOOLEAN | NULLABLE | Config is active | `true` |
| `is_default` | BOOLEAN | NULLABLE | Default for org/project | `false` |
| `last_used_at` | TIMESTAMP | NULLABLE | Last time config was used | `2025-10-12 14:30:00` |
| `usage_count` | INTEGER | NULLABLE | Number of times used | `42` |
| `created_by` | UUID | FK | User who created the config | `e5f6g7h8-...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Check Constraints**:
- `provider_name != ''`
- `provider_type IN ('llm', 'embedding', 'image', 'audio', 'multimodal')`

**Relationships**:
- N:1 with `organizations` (config belongs to one organization, CASCADE)
- N:1 with `projects` (config belongs to one project, CASCADE)
- N:1 with `users` (config created by one user)

**Indexes**:
- Primary key on `id`
- Index on `organization_id`
- Index on `project_id`
- Index on `is_active`
- Unique constraint on `(organization_id, project_id, provider_name, provider_type)`

**Access Patterns**:
- Lookup config by organization and provider (high frequency)
- Lookup default config for org/project (high frequency)
- Update last_used_at and usage_count (high frequency)

**Data Quality Rules**:
- provider_name must reference model_provider_metadata.provider_name
- provider_type must be one of allowed types
- api_key_encrypted must not be empty
- api_key_hash must be SHA-256 hash (64 hex chars)
- Only one config can be is_default=true per (organization_id, project_id, provider_name, provider_type)

**Security Considerations**:
- CRITICAL: api_key_encrypted must be AES-256 encrypted with organization-specific key
- api_key_hash used for deduplication, not authentication
- config_encrypted may contain OAuth tokens, endpoints, etc.
- Encryption keys stored in separate encryption_keys table

---

### Prompt Management Domain

#### 14. Prompts

**Domain**: Prompt Management
**Description**: Prompt templates with versioning support
**Cardinality**: 100-10,000 per organization
**Retention**: Permanent
**PII**: None
**RBAC**: Project-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `pr1234-...` |
| `name` | VARCHAR(255) | NOT NULL | Prompt name | `Support Ticket Triage` |
| `description` | TEXT | NULLABLE | Prompt description | `Triages customer tickets` |
| `category` | VARCHAR(100) | NULLABLE | Prompt category | `customer_support` |
| `status` | VARCHAR(50) | NOT NULL | Prompt status | `active` |
| `project_id` | UUID | FK, NOT NULL | Associated project | `p1r2o3j4-...` |
| `created_by` | UUID | FK, NOT NULL | User who created the prompt | `e5f6g7h8-...` |
| `current_version_id` | UUID | FK | Current version | `pv1234-...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `projects` (prompt belongs to one project)
- N:1 with `users` (prompt created by one user)
- 1:1 with `prompt_versions` (prompt has current version)
- 1:N with `prompt_versions` (prompt has many versions)

**Indexes**:
- Primary key on `id`
- Index on `project_id`
- Index on `created_by`
- Index on `status`

**Access Patterns**:
- List prompts by project (high frequency)
- Lookup prompt by ID (high frequency)
- Filter prompts by status (medium frequency)

**Data Quality Rules**:
- name must not be empty
- status must be one of: active, archived, deleted
- current_version_id must reference valid prompt_version if present

---

#### 15. Prompt Versions

**Domain**: Prompt Management
**Description**: Versions of prompt templates
**Cardinality**: 1,000-100,000 per organization (10 versions per prompt avg)
**Retention**: Permanent
**PII**: None
**RBAC**: Project-scoped via parent prompt

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `pv1234-...` |
| `prompt_id` | UUID | FK, NOT NULL | Parent prompt | `pr1234-...` |
| `version_number` | INTEGER | NOT NULL | Version number | `3` |
| `template` | TEXT | NOT NULL | Prompt template | `Triage this ticket: {{text}}` |
| `system_message` | TEXT | NULLABLE | System message | `You are a support agent...` |
| `variables` | JSON | NULLABLE | Template variables | `{"text": "string"}` |
| `model_config` | JSON | NULLABLE | Model configuration | `{"temperature": 0.7}` |
| `tags` | JSON | NULLABLE | Tags for categorization | `["support", "triage"]` |
| `avg_latency_ms` | DOUBLE PRECISION | NULLABLE | Average latency | `1234.56` |
| `avg_cost` | DOUBLE PRECISION | NULLABLE | Average cost | `0.0012` |
| `usage_count` | INTEGER | NULLABLE | Number of times used | `42` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `prompts` (version belongs to one prompt)
- 1:N with `traces` (version used in many traces)

**Indexes**:
- Primary key on `id`
- Index on `prompt_id`
- Unique constraint on `(prompt_id, version_number)`

**Access Patterns**:
- List versions by prompt (medium frequency)
- Lookup version by ID (high frequency for trace creation)
- Get latest version (high frequency)

**Data Quality Rules**:
- template must not be empty
- version_number must be > 0
- version_number must be unique within prompt
- avg_latency_ms >= 0 if present
- avg_cost >= 0 if present
- usage_count >= 0 if present

---

### Compliance Domain

#### 16. Policies

**Domain**: Compliance
**Description**: Governance policies for traces and LLM outputs
**Cardinality**: 10-100 per project
**Retention**: Permanent
**PII**: None
**RBAC**: Project-scoped

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `pol123-...` |
| `name` | VARCHAR(255) | NOT NULL | Policy name | `PII Detection` |
| `description` | TEXT | NULLABLE | Policy description | `Detects PII in outputs` |
| `policy_type` | VARCHAR(100) | NOT NULL | Policy type | `pii` |
| `rules` | JSON | NOT NULL | Policy rules configuration | `{"patterns": [...]}` |
| `threshold` | JSON | NULLABLE | Threshold values | `{"confidence": 0.8}` |
| `severity` | ENUM(PolicySeverity) | NOT NULL | Severity | `high` |
| `action` | ENUM(PolicyAction) | NOT NULL | Action | `redact` |
| `is_active` | BOOLEAN | NOT NULL | Policy is active | `true` |
| `is_enforced` | BOOLEAN | NOT NULL | Policy is enforced | `true` |
| `project_id` | UUID | FK, NOT NULL | Associated project | `p1r2o3j4-...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Enums**:
```python
PolicySeverity = Enum('low', 'medium', 'high', 'critical')
PolicyAction = Enum('warn', 'block', 'redact', 'log')
```

**Relationships**:
- N:1 with `projects` (policy belongs to one project)
- 1:N with `policy_violations` (policy has many violations)

**Indexes**:
- Primary key on `id`
- Index on `project_id`
- Index on `policy_type`
- Index on `is_active`

**Access Patterns**:
- List policies by project (high frequency)
- Filter active policies (high frequency for enforcement)
- Lookup policy by ID (medium frequency)

**Data Quality Rules**:
- name must not be empty
- policy_type must not be empty
- rules must be valid JSON and not empty
- severity must be one of defined enum values
- action must be one of defined enum values
- is_active and is_enforced must be explicitly set

---

#### 17. Policy Violations

**Domain**: Compliance
**Description**: Detected policy violations in traces
**Cardinality**: 1,000-100,000 per organization
**Retention**: 2 years
**PII**: Detected value may contain PII
**RBAC**: Project-scoped via policy

**Attributes**:

| Column | Type | Constraints | Business Rule | Example |
|--------|------|-------------|---------------|---------|
| `id` | UUID | PK | Immutable unique identifier | `pv1234-...` |
| `policy_id` | UUID | FK, NOT NULL | Policy that was violated | `pol123-...` |
| `trace_id` | UUID | FK | Trace where violation occurred | `t1r2a3c4-...` |
| `violation_type` | VARCHAR(100) | NOT NULL | Type of violation | `pii_email` |
| `severity` | ENUM(PolicySeverity) | NOT NULL | Violation severity | `high` |
| `detected_value` | JSON | NULLABLE | Detected violating value (redacted) | `{"email": "[REDACTED]"}` |
| `threshold_value` | JSON | NULLABLE | Threshold that was exceeded | `{"confidence": 0.8}` |
| `confidence_score` | INTEGER | NULLABLE | Confidence score (0-100) | `95` |
| `message` | TEXT | NULLABLE | Violation message | `PII email detected` |
| `violation_metadata` | JSON | NULLABLE | Additional metadata | `{"location": "output"}` |
| `status` | VARCHAR(50) | NULLABLE | Violation status | `open` |
| `resolution_notes` | TEXT | NULLABLE | Resolution notes | `False positive` |
| `resolved_at` | VARCHAR(50) | NULLABLE | Resolution timestamp (FIXME: should be TIMESTAMP) | `2025-10-12 14:30:00` |
| `resolved_by` | UUID | FK | User who resolved the violation | `e5f6g7h8-...` |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | `2025-10-12 14:30:00` |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification time | `2025-10-12 14:35:00` |

**Relationships**:
- N:1 with `policies` (violation belongs to one policy)
- N:1 with `traces` (violation belongs to one trace)
- N:1 with `users` (violation resolved by one user)

**Indexes**:
- Primary key on `id`
- Index on `policy_id`
- Index on `trace_id`
- Index on `severity`
- Index on `status`

**Access Patterns**:
- List violations by policy (medium frequency)
- List violations by trace (medium frequency)
- Filter violations by status (high frequency for dashboard)
- Filter violations by severity (high frequency)

**Data Quality Rules**:
- violation_type must not be empty
- severity must be one of defined enum values
- confidence_score must be between 0 and 100 if present
- status must be one of: open, resolved, false_positive, acknowledged
- resolved_at must be set if status = 'resolved'
- resolved_by must be set if status = 'resolved'

**Schema Issues**:
- FIXME: `resolved_at` should be TIMESTAMP, not VARCHAR(50)

---

## Data Relationships

### Relationship Matrix

```
organizations (1) ──── (N) users
organizations (1) ──── (N) projects
organizations (1) ──── (N) groups
organizations (1) ──── (N) call_insights_analysis
organizations (1) ──── (N) insight_comparisons
organizations (1) ──── (N) model_provider_configs
organizations (1) ──── (N) evaluation_catalog
organizations (1) ──── (N) trace_evaluations

projects (1) ──── (N) prompts
projects (1) ──── (N) traces
projects (1) ──── (N) call_insights_analysis
projects (1) ──── (N) model_provider_configs
projects (1) ──── (N) evaluation_catalog
projects (1) ──── (N) policies
projects (N) ──── (M) groups via project_groups

traces (1) ──── (N) spans
traces (1) ──── (N) call_insights_analysis (as parent_trace_id)
traces (1) ──── (N) insight_comparisons (as judge_trace_id)
traces (1) ──── (N) policy_violations
traces (1) ──── (N) trace_evaluations

call_insights_analysis (1) ──── (N) insight_comparisons (as analysis_a_id)
call_insights_analysis (1) ──── (N) insight_comparisons (as analysis_b_id)

evaluation_catalog (1) ──── (N) trace_evaluations
```

### Cascade Delete Rules

**CASCADE DELETE** (child deleted when parent deleted):
- `organizations` → ALL child tables (users, projects, etc.)
- `call_insights_analysis` → `insight_comparisons`
- `model_provider_configs` → children (if any)

**SET NULL** (child orphaned when parent deleted):
- `users` → `traces` (user_id set to NULL)

**RESTRICT** (parent cannot be deleted if children exist):
- Most foreign keys by default

---

## Data Quality Rules

### Cross-Table Rules

1. **Token Consistency**:
   - `traces.total_tokens = traces.input_tokens + traces.output_tokens` (if all present)
   - `spans.total_tokens = spans.prompt_tokens + spans.completion_tokens` (if all present)
   - `trace_evaluations.total_tokens = trace_evaluations.input_tokens + trace_evaluations.output_tokens` (if all present)

2. **Cost Non-Negative**:
   - `call_insights_analysis.total_cost >= 0`
   - `traces.total_cost >= 0`
   - `trace_evaluations.evaluation_cost >= 0`

3. **Timestamp Ordering**:
   - `created_at <= updated_at` for all tables
   - `spans.start_time < spans.end_time` (if both present)
   - `model_catalog.release_date < model_catalog.deprecation_date` (if both present)

4. **Model Reference Integrity**:
   - `call_insights_analysis.model_stage1, model_stage2, model_stage3` should reference `model_catalog.model_name`
   - `traces.model_name` should reference `model_catalog.model_name`
   - `evaluation_catalog.llm_model` should reference `model_catalog.model_name`
   - `trace_evaluations.model_used` should reference `model_catalog.model_name`

5. **Winner Values**:
   - `insight_comparisons.overall_winner IN ('A', 'B', 'tie')`
   - `insight_comparisons.stage1_winner IN ('A', 'B', 'tie')`
   - `insight_comparisons.stage2_winner IN ('A', 'B', 'tie')`
   - `insight_comparisons.stage3_winner IN ('A', 'B', 'tie')`

6. **Self-Reference Prevention**:
   - `insight_comparisons.analysis_a_id != insight_comparisons.analysis_b_id`

---

## Data Lifecycle

### Retention Policies

| Entity | Retention | Archive Policy | Rationale |
|--------|-----------|----------------|-----------|
| `organizations` | Permanent | Soft delete | Business continuity |
| `users` | 7 years after deletion | Hard delete | GDPR compliance |
| `projects` | 5 years after archival | Cold storage | Business records |
| `prompts` | Permanent | No archive | Version history |
| `traces` | 90 days | S3 cold storage | Cost optimization |
| `spans` | 90 days | S3 cold storage | Cost optimization |
| `call_insights_analysis` | 2 years | S3 cold storage | Analytics history |
| `insight_comparisons` | 1 year | S3 cold storage | Evaluation history |
| `trace_evaluations` | 1 year | S3 cold storage | Evaluation history |
| `policy_violations` | 2 years | S3 cold storage | Compliance audit |
| `model_catalog` | Permanent | No archive | Reference data |
| `model_provider_configs` | Until user deletes | Immediate delete | Security |

### Data Archival Process

**Step 1: Identify Archival Candidates**
```sql
SELECT id FROM traces WHERE created_at < NOW() - INTERVAL '90 days';
```

**Step 2: Export to S3**
```bash
pg_dump --table=traces --where="created_at < NOW() - INTERVAL '90 days'" | \
  gzip | aws s3 cp - s3://promptforge-archives/traces/2025-10-12.sql.gz
```

**Step 3: Verify Export**
```bash
aws s3 ls s3://promptforge-archives/traces/2025-10-12.sql.gz
```

**Step 4: Delete from Primary**
```sql
DELETE FROM traces WHERE created_at < NOW() - INTERVAL '90 days';
```

**Step 5: Vacuum**
```sql
VACUUM ANALYZE traces;
```

---

## Index Catalog

### Primary Indexes

All tables have a primary key index on `id`.

### Unique Indexes

| Table | Columns | Purpose |
|-------|---------|---------|
| `organizations` | `name` | Prevent duplicate org names |
| `users` | `email` | Prevent duplicate user emails |
| `traces` | `trace_id` | OpenTelemetry trace ID uniqueness |
| `spans` | `span_id` | OpenTelemetry span ID uniqueness |
| `model_catalog` | `model_name` | Prevent duplicate model entries |
| `model_provider_metadata` | `provider_name` | Prevent duplicate provider entries |
| `model_provider_configs` | `(organization_id, project_id, provider_name, provider_type)` | One config per provider per project |
| `insight_comparisons` | `(analysis_a_id, analysis_b_id, judge_model)` | Prevent duplicate comparisons |
| `groups` | `(organization_id, name)` | Unique group names within org |

### Foreign Key Indexes

All foreign key columns have indexes for join performance.

### Composite Indexes

| Table | Columns | Purpose |
|-------|---------|---------|
| `insight_comparisons` | `(organization_id, created_at DESC)` | Org-scoped time-series queries |
| `insight_comparisons` | `(user_id, created_at DESC)` | User-scoped time-series queries |
| `trace_evaluations` | `(organization_id, created_at DESC)` | Org-scoped time-series queries |

### JSONB GIN Indexes

| Table | Column | Expression | Purpose |
|-------|--------|------------|---------|
| `traces` | `trace_metadata` | `(trace_metadata->>'parent_trace_id')` | Parent trace lookups |
| `traces` | `trace_metadata` | `(trace_metadata->>'source')` | Source filtering |
| `trace_evaluations` | `vendor_metrics` | Full GIN | Vendor metric queries |
| `trace_evaluations` | `llm_metadata` | Full GIN | LLM metadata queries |

---

## JSONB Field Catalog

### call_insights_analysis.stage_params

**Purpose**: Model parameters for each stage of DTA pipeline

**Schema**:
```json
{
  "fact_extraction": {
    "temperature": 0.0-2.0,
    "top_p": 0.0-1.0,
    "max_tokens": 1-16384
  },
  "reasoning": {
    "temperature": 0.0-2.0,
    "top_p": 0.0-1.0,
    "max_tokens": 1-16384
  },
  "summary": {
    "temperature": 0.0-2.0,
    "top_p": 0.0-1.0,
    "max_tokens": 1-16384
  }
}
```

**Access Pattern**: Read entire object, no filtering

---

### call_insights_analysis.analysis_metadata

**Purpose**: Analysis metadata including stage count and model parameters

**Schema**:
```json
{
  "stage_count": 3,
  "evaluation_count": 3,
  "model_parameters": {
    "stage1": {"temperature": 0.25, "top_p": 0.95, "max_tokens": 1000},
    "stage2": {"temperature": 0.65, "top_p": 0.95, "max_tokens": 1500},
    "stage3": {"temperature": 0.45, "top_p": 0.95, "max_tokens": 800}
  }
}
```

**Access Pattern**: Read entire object, no filtering

---

### insight_comparisons.evaluation_criteria

**Purpose**: List of evaluation criteria used by judge model

**Schema**:
```json
["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]
```

**Access Pattern**: Read entire array, no filtering

---

### insight_comparisons.stage1_scores (stage2_scores, stage3_scores)

**Purpose**: Scores for each analysis per criterion (0.0-1.0 scale)

**Schema**:
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

**Access Pattern**: Read entire object, extract specific scores in API layer

---

### insight_comparisons.comparison_metadata

**Purpose**: Judge model metrics and cost comparison

**Schema**:
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

**Access Pattern**: Read entire object, no filtering

---

### traces.input_data

**Purpose**: Input data including prompt, system prompt, and model parameters

**Schema**:
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

**Access Pattern**: Read entire object, no filtering

---

### traces.trace_metadata

**Purpose**: Additional trace metadata including parent trace ID, source, intent

**Schema**:
```json
{
  "intent": "Content Summarization",
  "tone": "professional",
  "source": "playground",
  "parent_trace_id": "parent-trace-uuid"
}
```

**Access Pattern**:
- GIN index on `parent_trace_id` for parent trace lookups
- GIN index on `source` for source filtering

---

### trace_evaluations.llm_metadata

**Purpose**: Comprehensive LLM metrics for evaluation invocations

**Schema**:
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

**Access Pattern**:
- GIN index for filtering by model
- Aggregate queries for cost analysis

---

### model_catalog.context_window

**Purpose**: Context window limits (input/output tokens)

**Schema**:
```json
{
  "input": 200000,
  "output": 8192
}
```

**Access Pattern**: Read entire object for validation

---

### model_catalog.capabilities

**Purpose**: Model capabilities (text, vision, etc.)

**Schema**:
```json
["text", "vision", "thinking", "computer_use"]
```

**Access Pattern**: Array membership checks

---

### model_catalog.pricing

**Purpose**: Pricing per million tokens in USD

**Schema**:
```json
{
  "input": 3.0,
  "output": 15.0,
  "currency": "USD"
}
```

**Access Pattern**: Read entire object for cost calculations

---

## Data Access Patterns

### High-Frequency Queries

1. **RBAC Lookup**:
```sql
SELECT organization_id FROM users WHERE id = $user_id;
```

2. **List Analyses by Organization**:
```sql
SELECT * FROM call_insights_analysis
WHERE organization_id = $org_id
ORDER BY created_at DESC
LIMIT 50;
```

3. **List Traces by Project**:
```sql
SELECT * FROM traces
WHERE project_id = $project_id
ORDER BY created_at DESC
LIMIT 100;
```

4. **Lookup Model Pricing**:
```sql
SELECT pricing FROM model_catalog WHERE model_name = $model_name;
```

5. **Lookup Provider Config**:
```sql
SELECT api_key_encrypted FROM model_provider_configs
WHERE organization_id = $org_id
  AND provider_name = $provider_name
  AND is_active = true
  AND (project_id = $project_id OR project_id IS NULL)
ORDER BY project_id NULLS LAST
LIMIT 1;
```

### Medium-Frequency Queries

1. **Filter Analyses by Model**:
```sql
SELECT * FROM call_insights_analysis
WHERE organization_id = $org_id
  AND (model_stage1 = $model OR model_stage2 = $model OR model_stage3 = $model)
ORDER BY created_at DESC;
```

2. **Aggregate Costs by Organization**:
```sql
SELECT
  DATE_TRUNC('day', created_at) as date,
  SUM(total_cost) as daily_cost
FROM call_insights_analysis
WHERE organization_id = $org_id
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;
```

3. **List Evaluations by Trace**:
```sql
SELECT * FROM trace_evaluations
WHERE trace_id = $trace_id
ORDER BY created_at DESC;
```

### Low-Frequency Queries

1. **Full-Text Search on Transcripts**:
```sql
SELECT * FROM call_insights_analysis
WHERE organization_id = $org_id
  AND transcript_title ILIKE '%' || $search || '%'
LIMIT 50;
```
*Note: Consider adding tsvector column for better performance*

2. **Search Vendor Metrics**:
```sql
SELECT * FROM trace_evaluations
WHERE organization_id = $org_id
  AND vendor_metrics @> '{"ragas_score": 0.9}'::jsonb;
```

---

## Data Governance

### Data Classification

| Classification | Tables | Access Control | Encryption |
|----------------|--------|----------------|------------|
| **Public** | model_catalog, model_provider_metadata, evaluation_catalog (is_public=true) | Read-only | No |
| **Internal** | organizations, projects, prompts, policies | Organization-scoped RBAC | At rest |
| **Confidential** | users, traces, call_insights_analysis | Organization + user RBAC | At rest + in transit |
| **Restricted** | model_provider_configs | Organization + user RBAC | AES-256 + at rest |

### PII Fields

| Table | Column | PII Type | Protection |
|-------|--------|----------|------------|
| `users` | `email` | Email address | Encryption at rest |
| `users` | `full_name` | Personal name | Encryption at rest |
| `users` | `hashed_password` | Credential | bcrypt hash + encryption |
| `call_insights_analysis` | `transcript_input` | Customer data | Configurable redaction |
| `traces` | `input_data` | Prompt data | Encryption at rest |
| `traces` | `output_data` | Response data | Encryption at rest |
| `trace_evaluations` | `reason` | Trace data | Encryption at rest |
| `policy_violations` | `detected_value` | Sensitive data | Redaction + encryption |
| `model_provider_configs` | `api_key_encrypted` | API credential | AES-256 encryption |

### GDPR Compliance

1. **Right to Access**: Users can export all their data via API
2. **Right to Deletion**: Soft delete users (set is_active=false), hard delete after 7 years
3. **Right to Rectification**: Users can update their email and full_name
4. **Data Portability**: Export API provides JSON export of all user data
5. **Consent**: Users consent to data processing during signup
6. **Data Breach Notification**: Audit logs track all access to PII fields

### Audit Trail

All tables include:
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `created_by`: User who created the record (where applicable)

Additional audit logging recommended for:
- Model provider config access (who decrypted API keys)
- Policy violation resolution (who marked as resolved)
- User account changes (email updates, password resets)

---

## Schema Evolution

### Migration Strategy

1. **Backward Compatibility**: All schema changes must be backward compatible for 2 versions
2. **Column Additions**: New columns must be nullable or have defaults
3. **Column Renames**: Use views for old column names during deprecation period
4. **Foreign Key Changes**: Add new FK, deprecate old, remove after 2 versions
5. **Data Type Changes**: Add new column, backfill, deprecate old, remove after 2 versions

### Known Schema Issues

1. **policy_violations.resolved_at**: Should be TIMESTAMP, currently VARCHAR(50)
   - **Fix**: Create migration to alter column type
   - **Priority**: Low (data type accepts timestamp strings)

2. **Missing Full-Text Search**: No tsvector columns for transcript_title, transcript_input
   - **Fix**: Add tsvector columns with GIN indexes
   - **Priority**: Medium (impacts search performance)

3. **No Soft Delete Support**: Most tables lack is_deleted flag
   - **Fix**: Add is_deleted BOOLEAN DEFAULT false to core tables
   - **Priority**: Medium (impacts audit trail and GDPR compliance)

---

## Contact & Support

**Data Catalog Owner**: DB Architect Agent
**Last Updated**: 2025-10-12
**Next Review**: 2025-11-12
**Feedback**: Submit issues to DB Architect Agent via orchestrator

For schema changes:
1. Consult API Architect for API compatibility
2. Create Alembic migration with up/down scripts
3. Test migration on staging database
4. Update this data catalog
5. Deploy to production

---

**End of Data Catalog**
