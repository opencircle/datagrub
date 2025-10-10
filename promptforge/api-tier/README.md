# API Tier - PromptForge

## Overview

The API tier is a FastAPI-based backend providing RESTful APIs for the PromptForge platform. It handles authentication, data management, caching, and business logic.

## Tech Stack

- **Framework**: FastAPI 0.109
- **Database**: PostgreSQL 16 with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Cache/Pub-Sub**: Redis 7
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic 2.5

## Project Structure

```
api-tier/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic environment
├── app/
│   ├── api/                    # API routes
│   │   ├── v1/                 # API version 1
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management
│   │   │   ├── organizations.py
│   │   │   ├── projects.py
│   │   │   ├── prompts.py
│   │   │   ├── evaluations.py
│   │   │   ├── traces.py
│   │   │   ├── policies.py
│   │   │   └── models.py       # AI model management
│   │   └── dependencies.py     # Shared dependencies
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database connection
│   │   ├── redis_client.py     # Redis client
│   │   └── security.py         # JWT and hashing
│   ├── models/                 # SQLAlchemy models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── prompt.py
│   │   ├── evaluation.py
│   │   ├── trace.py
│   │   ├── policy.py
│   │   └── model.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── prompt.py
│   │   ├── evaluation.py
│   │   ├── trace.py
│   │   ├── policy.py
│   │   └── model.py
│   └── main.py                 # FastAPI application
├── tests/                      # Test suite
├── .env.example                # Environment template
├── alembic.ini                 # Alembic configuration
├── Dockerfile                  # Docker image
└── requirements.txt            # Python dependencies
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- (Optional) Docker and Docker Compose

### Installation

1. **Create virtual environment**:
```bash
cd api-tier
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start database services** (if using Docker):
```bash
# From project root
docker-compose up -d postgres redis
```

5. **Run migrations**:
```bash
alembic upgrade head
```

6. **Seed database** (optional):
```bash
cd ../database-tier/seeds
python seed_data.py
```

### Running the Server

**Development mode** (with auto-reload):
```bash
uvicorn app.main:app --reload --port 8000
```

**Production mode**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**With Docker Compose**:
```bash
# From project root
docker-compose up api
```

## API Documentation

### Interactive API Docs

Once the server is running:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Authentication

All endpoints except `/auth/login` and `/auth/refresh` require JWT authentication.

**Login to get token**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@promptforge.com","password":"admin123"}'
```

**Use token in requests**:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/refresh` - Refresh access token

#### Users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users` - List users

#### Organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations/me` - Get current organization
- `GET /api/v1/organizations/{org_id}` - Get organization
- `PATCH /api/v1/organizations/{org_id}` - Update organization
- `GET /api/v1/organizations` - List organizations

#### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{project_id}` - Get project
- `PATCH /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `GET /api/v1/projects` - List projects

#### Prompts
- `POST /api/v1/prompts` - Create prompt with initial version
- `GET /api/v1/prompts/{prompt_id}` - Get prompt
- `PATCH /api/v1/prompts/{prompt_id}` - Update prompt metadata
- `DELETE /api/v1/prompts/{prompt_id}` - Delete prompt
- `GET /api/v1/prompts` - List prompts
- `POST /api/v1/prompts/{prompt_id}/versions` - Create new version
- `GET /api/v1/prompts/{prompt_id}/versions` - List versions

#### Evaluations
- `POST /api/v1/evaluations` - Create evaluation
- `GET /api/v1/evaluations/{evaluation_id}` - Get evaluation
- `PATCH /api/v1/evaluations/{evaluation_id}` - Update evaluation
- `DELETE /api/v1/evaluations/{evaluation_id}` - Delete evaluation
- `GET /api/v1/evaluations` - List evaluations

#### Traces
- `POST /api/v1/traces` - Create trace with spans
- `GET /api/v1/traces/{trace_id}` - Get trace
- `DELETE /api/v1/traces/{trace_id}` - Delete trace
- `GET /api/v1/traces` - List traces

#### Policies
- `POST /api/v1/policies` - Create policy
- `GET /api/v1/policies/{policy_id}` - Get policy
- `PATCH /api/v1/policies/{policy_id}` - Update policy
- `DELETE /api/v1/policies/{policy_id}` - Delete policy
- `GET /api/v1/policies` - List policies
- `GET /api/v1/policies/{policy_id}/violations` - List violations

#### AI Models
- `POST /api/v1/models` - Create AI model
- `GET /api/v1/models/{model_id}` - Get model
- `PATCH /api/v1/models/{model_id}` - Update model
- `GET /api/v1/models` - List models
- `POST /api/v1/models/providers` - Create provider
- `GET /api/v1/models/providers/{provider_id}` - Get provider
- `GET /api/v1/models/providers` - List providers

## Configuration

### Environment Variables

Key configuration variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Security Best Practices

1. **Change SECRET_KEY** in production
2. **Use environment-specific .env files**
3. **Enable HTTPS** in production
4. **Restrict CORS origins**
5. **Use strong passwords** for database
6. **Encrypt API keys** before storing

## Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
alembic current
```

## Testing

### Run Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

### Run Specific Test

```bash
pytest tests/test_auth.py::test_login
```

## Development

### Code Formatting

```bash
black app/
ruff app/ --fix
```

### Type Checking

```bash
mypy app/
```

### Database Inspection

```bash
# Connect to database
psql postgresql://promptforge:promptforge@localhost:5432/promptforge

# List tables
\dt

# Describe table
\d users
```

### Redis Inspection

```bash
# Connect to Redis
redis-cli

# List keys
KEYS *

# Get value
GET key_name
```

## Performance

### Caching Strategy

Redis is used for:
- User session caching
- Frequently accessed data (organizations, projects)
- Rate limiting
- Real-time pub/sub for trace streaming

### Database Optimization

- Async SQLAlchemy for non-blocking I/O
- Connection pooling
- Eager loading for relationships
- Indexed foreign keys

## Troubleshooting

### Server Won't Start

```bash
# Check port availability
lsof -i :8000

# Check database connection
psql postgresql://promptforge:promptforge@localhost:5432/promptforge

# Check Redis connection
redis-cli ping
```

### Migration Errors

```bash
# Reset database (WARNING: Deletes all data!)
alembic downgrade base
alembic upgrade head
python ../database-tier/seeds/seed_data.py
```

### CORS Errors

Update `BACKEND_CORS_ORIGINS` in `.env`:
```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t promptforge-api .

# Run container
docker run -p 8000:8000 --env-file .env promptforge-api
```

### Production Checklist

- [ ] Update SECRET_KEY
- [ ] Configure DATABASE_URL with production credentials
- [ ] Set BACKEND_CORS_ORIGINS to production domains
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, DataDog, etc.)
- [ ] Enable rate limiting
- [ ] Review security headers

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Run `black` and `ruff`
5. Submit pull request

## License

Proprietary - PromptForge Platform
