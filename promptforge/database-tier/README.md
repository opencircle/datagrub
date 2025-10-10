# Database Tier - PromptForge

## Overview

The database tier contains PostgreSQL schemas, Alembic migrations, and seeding scripts for the PromptForge platform.

## Structure

```
database-tier/
├── migrations/         # Alembic migration scripts (managed via api-tier)
├── seeds/             # Database seeding scripts
│   └── seed_data.py   # Sample data seeding
└── scripts/           # Database management scripts
```

## Setup

### Prerequisites

- PostgreSQL 14+ or Docker
- Python 3.11+

### Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d postgres redis
```

### Manual Setup

1. Install PostgreSQL:
```bash
brew install postgresql@16  # macOS
```

2. Create database:
```bash
createdb promptforge
```

3. Set up environment variables:
```bash
export DATABASE_URL="postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge"
```

## Database Migrations

Migrations are managed via Alembic in the api-tier directory.

### Create Initial Migration

```bash
cd api-tier
alembic revision --autogenerate -m "Initial schema"
```

### Run Migrations

```bash
cd api-tier
alembic upgrade head
```

### Rollback Migration

```bash
cd api-tier
alembic downgrade -1
```

## Seeding Data

### Seed Database with Sample Data

```bash
cd database-tier/seeds
python seed_data.py
```

This creates:
- 1 Organization (PromptForge Demo)
- 3 Users (admin, developer, viewer)
- 2 Model Providers (OpenAI, Anthropic)
- 2 AI Models (GPT-4, Claude 3)
- 3 Projects
- 1 Prompt with 1 Version
- 3 Policies
- 1 Evaluation with 10 Results
- 5 Traces with Spans

### Test Credentials

After seeding, you can login with:

- **Admin**: admin@promptforge.com / admin123
- **Developer**: developer@promptforge.com / dev123
- **Viewer**: viewer@promptforge.com / viewer123

## Database Schema

### Core Tables

- `organizations` - Multi-tenant organizations
- `users` - User accounts with roles
- `projects` - AI projects
- `prompts` - Prompt templates
- `prompt_versions` - Versioned prompt content
- `evaluations` - Evaluation runs
- `evaluation_results` - Individual test results
- `traces` - Execution traces
- `spans` - Trace steps
- `policies` - Governance rules
- `policy_violations` - Policy breach records
- `ai_models` - AI model configurations
- `model_providers` - Model provider settings

### Relationships

```
Organization 1:N User
Organization 1:N Project
Project 1:N Prompt
Project 1:N Evaluation
Project 1:N Trace
Project 1:N Policy
Prompt 1:N PromptVersion
Prompt 1:1 PromptVersion (current_version)
Evaluation 1:N EvaluationResult
Trace 1:N Span
Policy 1:N PolicyViolation
ModelProvider 1:N AIModel
```

## Backup and Restore

### Backup Database

```bash
pg_dump promptforge > backup.sql
```

### Restore Database

```bash
psql promptforge < backup.sql
```

## Troubleshooting

### Connection Refused

```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql@16
```

### Permission Denied

```bash
# Grant user permissions
psql postgres -c "ALTER USER promptforge WITH SUPERUSER;"
```

### Migration Conflicts

```bash
# Reset migrations (WARNING: Deletes all data!)
cd api-tier
alembic downgrade base
alembic upgrade head
```
