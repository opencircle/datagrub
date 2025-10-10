# PromptForge Backend Setup Guide

## Quick Start

Get the PromptForge backend running in 5 minutes using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- 8GB RAM minimum
- Ports available: 5432 (PostgreSQL), 6379 (Redis), 8000 (API)

### Step 1: Start Services

```bash
cd promptforge

# Start all backend services
docker-compose up -d

# Check status
docker-compose ps
```

This starts:
- PostgreSQL 16 on port 5432
- Redis 7 on port 6379
- FastAPI on port 8000

### Step 2: Run Migrations

```bash
# Access API container
docker-compose exec api bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### Step 3: Seed Database

```bash
# Run seeding script (with correct path inside container)
docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
```

### Step 4: Test API

```bash
# Check API health
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@promptforge.com","password":"admin123"}'
```

### Step 5: Open API Documentation

Visit http://localhost:8000/docs in your browser.

---

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### Installation Steps

#### 1. Install PostgreSQL

**macOS**:
```bash
brew install postgresql@16
brew services start postgresql@16
createdb promptforge
```

**Ubuntu/Debian**:
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb promptforge
```

#### 2. Install Redis

**macOS**:
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt install redis-server
sudo systemctl start redis
```

#### 3. Setup Python Environment

```bash
cd api-tier

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your database credentials
nano .env
```

Update these values in `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<generate-a-secure-32-char-key>
```

#### 5. Run Migrations

```bash
# Apply database migrations
alembic upgrade head
```

#### 6. Seed Database

```bash
# Navigate to seeds directory
cd ../database-tier/seeds

# Run seed script
python seed_data.py

# Return to api-tier
cd ../../api-tier
```

#### 7. Start API Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8000
```

#### 8. Verify Setup

Open http://localhost:8000/docs in your browser.

---

## Test Credentials

After seeding, use these credentials to login:

| Role      | Email                        | Password  |
|-----------|------------------------------|-----------|
| Admin     | admin@promptforge.com        | admin123  |
| Developer | developer@promptforge.com    | dev123    |
| Viewer    | viewer@promptforge.com       | viewer123 |

---

## API Testing

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Login using `/auth/login` endpoint
4. Copy the `access_token` from response
5. Paste token in Authorization dialog
6. Test other endpoints

### Using curl

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@promptforge.com","password":"admin123"}' \
  | jq -r '.access_token')

# Get current user
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# List projects
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"

# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "My test project",
    "status": "active",
    "organization_id": "<org-id-from-users-me>"
  }'
```

### Using Postman

1. Import OpenAPI spec: http://localhost:8000/api/v1/openapi.json
2. Create environment with `baseUrl=http://localhost:8000`
3. Set up Pre-request Script for authentication
4. Test endpoints

---

## Project Structure

```
promptforge/
├── api-tier/               # FastAPI backend
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── core/          # Config, database, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── main.py        # FastAPI app
│   ├── alembic/           # Database migrations
│   ├── tests/             # Unit and integration tests
│   └── requirements.txt   # Python dependencies
├── database-tier/         # Database scripts
│   └── seeds/             # Seeding scripts
├── ui-tier/               # React micro-frontends (Phase 1)
│   ├── shell/             # Main shell app
│   ├── mfe-projects/      # Projects MFE
│   ├── mfe-evaluations/   # Evaluations MFE
│   ├── mfe-playground/    # Playground MFE
│   ├── mfe-traces/        # Traces MFE
│   ├── mfe-policy/        # Policy MFE
│   └── mfe-models/        # Models MFE
└── docker-compose.yml     # Docker services
```

---

## Common Commands

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api

# Restart API
docker-compose restart api

# Access database
docker-compose exec postgres psql -U promptforge

# Access Redis
docker-compose exec redis redis-cli
```

### Database

```bash
# Create migration
cd api-tier
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (WARNING: Deletes all data!)
docker-compose exec api alembic downgrade base
docker-compose exec api alembic upgrade head
docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
```

### API Server

```bash
cd api-tier

# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With specific host/port
uvicorn app.main:app --host 127.0.0.1 --port 8080
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error

```bash
# Test PostgreSQL connection
psql postgresql://promptforge:promptforge@localhost:5432/promptforge

# Check PostgreSQL is running
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux
```

### Redis Connection Error

```bash
# Test Redis connection
redis-cli ping

# Check Redis is running
brew services list | grep redis        # macOS
sudo systemctl status redis            # Linux
```

### Migration Conflicts

```bash
# Reset all migrations (WARNING: Deletes data!)
cd api-tier
alembic downgrade base
alembic upgrade head

# Re-seed database
cd ../database-tier/seeds
python seed_data.py
```

### Import Errors

```bash
# Ensure you're in the virtual environment
which python
# Should show: /path/to/promptforge/api-tier/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Next Steps

1. **Frontend Integration**: Update React MFEs to use real APIs (see `UI_INTEGRATION.md`)
2. **Testing**: Add unit and integration tests
3. **Documentation**: Generate Postman collection
4. **Production**: Configure for production deployment

---

## Support

For issues or questions:
- Check API logs: `docker-compose logs -f api`
- Review database logs: `docker-compose logs -f postgres`
- Consult API documentation: http://localhost:8000/docs
