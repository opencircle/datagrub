# PromptForge Quick Reference

Essential commands and URLs for daily development.

## Starting Services

### Full Stack

```bash
# Start backend (PostgreSQL, Redis, FastAPI)
docker-compose up -d

# Start frontend (all MFEs)
cd ui-tier
npm run start:all
```

### Backend Only

```bash
# Start all backend services
docker-compose up -d

# Start only database
docker-compose up -d postgres redis

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Frontend Only

```bash
cd ui-tier

# All MFEs
npm run start:all

# Individual MFEs
npm run start:shell
npm run start:projects
npm run start:evaluations
npm run start:playground
npm run start:traces
npm run start:policy
npm run start:models
```

## URLs

**Frontend:**
- Shell: http://localhost:3000
- Projects: http://localhost:3001
- Evaluations: http://localhost:3002
- Playground: http://localhost:3003
- Traces: http://localhost:3004
- Policy: http://localhost:3005
- Models: http://localhost:3006

**Backend:**
- API Base: http://localhost:8000/api/v1
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json
- Health Check: http://localhost:8000/health

**Database:**
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Test Credentials

| Role      | Email                        | Password  |
|-----------|------------------------------|-----------|
| Admin     | admin@promptforge.com        | admin123  |
| Developer | developer@promptforge.com    | dev123    |
| Viewer    | viewer@promptforge.com       | viewer123 |

## Database Commands

### Migrations

```bash
# Create new migration (auto-generate from models)
docker-compose exec api alembic revision --autogenerate -m "description"

# Create empty migration (for manual changes)
docker-compose exec api alembic revision -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback one migration
docker-compose exec api alembic downgrade -1

# Show current version
docker-compose exec api alembic current

# Show migration history
docker-compose exec api alembic history
```

### Seeding

```bash
# Seed database with sample data
docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
```

### PostgreSQL Access

```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U promptforge -d promptforge

# Common queries
\dt              # List tables
\d table_name    # Describe table
SELECT * FROM users;
\q               # Quit
```

### Redis Access

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Common commands
KEYS *           # List all keys
GET key_name     # Get value
DEL key_name     # Delete key
FLUSHDB          # Clear database (WARNING)
exit             # Quit
```

## Docker Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f              # All services
docker-compose logs -f api          # API only
docker-compose logs -f postgres     # PostgreSQL only

# Restart services
docker-compose restart              # All services
docker-compose restart api          # API only

# Rebuild and restart
docker-compose up -d --build

# Execute command in container
docker-compose exec api bash        # Shell access
docker-compose exec api python      # Python REPL

# View resource usage
docker stats
```

## API Testing

### cURL Examples

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@promptforge.com","password":"admin123"}'
```

**Get Projects (with auth):**
```bash
TOKEN="your_access_token"
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

**Create Project:**
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Project",
    "description": "Project description",
    "status": "draft",
    "organization_id": "uuid"
  }'
```

### HTTPie Examples (if installed)

```bash
# Login
http POST localhost:8000/api/v1/auth/login \
  email=admin@promptforge.com password=admin123

# Get projects
http localhost:8000/api/v1/projects \
  Authorization:"Bearer $TOKEN"

# Create project
http POST localhost:8000/api/v1/projects \
  Authorization:"Bearer $TOKEN" \
  name="New Project" \
  description="Description" \
  status="draft"
```

## Development Workflow

### Adding a New Feature

1. **Create model** in `api-tier/app/models/`
2. **Create schemas** in `api-tier/app/schemas/`
3. **Create routes** in `api-tier/app/api/v1/`
4. **Register router** in `api-tier/app/main.py`
5. **Create migration**: `alembic revision --autogenerate -m "add feature"`
6. **Apply migration**: `alembic upgrade head`
7. **Create TypeScript types** in `ui-tier/shared/types/`
8. **Create service** in `ui-tier/shared/services/`
9. **Create hooks** in `ui-tier/shared/hooks/`
10. **Use in components**

### Common Development Tasks

**Hot reload API changes:**
```bash
# API auto-reloads on file changes (--reload flag in docker-compose.yml)
# Just save the file and FastAPI will restart
```

**Hot reload frontend changes:**
```bash
# Webpack dev server auto-reloads
# Just save the file and browser will refresh
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
```

**View API errors:**
```bash
docker-compose logs -f api | grep ERROR
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs api

# Common fixes:
docker-compose down
docker-compose up -d --build
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check if database exists
docker-compose exec postgres psql -U promptforge -l
```

### Migration errors

```bash
# Check current version
docker-compose exec api alembic current

# Show pending migrations
docker-compose exec api alembic heads

# If stuck, downgrade and re-upgrade
docker-compose exec api alembic downgrade -1
docker-compose exec api alembic upgrade head

# Nuclear option: reset database
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

### Frontend Module Federation errors

```bash
# Ensure all MFEs are running
cd ui-tier
npm run start:all

# If port is busy, kill process
lsof -ti:3001 | xargs kill -9  # Replace 3001 with your port
```

### CORS errors

```bash
# Check CORS configuration in docker-compose.yml
# Ensure frontend URL is in BACKEND_CORS_ORIGINS

# Restart API after changing CORS config
docker-compose restart api
```

## Environment Variables

### Backend (.env or docker-compose.yml)

```bash
DATABASE_URL=postgresql+asyncpg://promptforge:promptforge@postgres:5432/promptforge
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
PROJECT_NAME=PromptForge API
VERSION=2.0.0
API_V1_PREFIX=/api/v1
```

### Frontend

```bash
# Usually configured in webpack.config.js
API_BASE_URL=http://localhost:8000/api/v1
```

## Build for Production

```bash
# Backend
docker-compose -f docker-compose.prod.yml up -d

# Frontend
cd ui-tier
npm run build:all

# Outputs will be in ui-tier/*/dist/
```

## Useful Git Commands

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/my-feature

# Stage and commit
git add .
git commit -m "feat: add my feature"

# Push to remote
git push origin feature/my-feature

# Merge develop into feature
git checkout feature/my-feature
git merge develop

# Reset local changes
git reset --hard HEAD
git clean -fd
```

## Performance Monitoring

```bash
# Check API response times
docker-compose logs api | grep "GET\|POST\|PUT\|DELETE"

# Monitor database connections
docker-compose exec postgres psql -U promptforge -d promptforge \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor Redis memory
docker-compose exec redis redis-cli INFO memory

# Monitor container resources
docker stats
```

## Keyboard Shortcuts (VS Code)

- `Cmd+P` - Quick file open
- `Cmd+Shift+F` - Search in files
- `Cmd+Shift+P` - Command palette
- `Cmd+B` - Toggle sidebar
- `Cmd+\`` - Toggle terminal
- `Cmd+/` - Toggle comment
- `F12` - Go to definition
- `Shift+F12` - Find references

## Documentation Links

- **Main README**: [README.md](./README.md)
- **API Docs**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Dev Guide**: [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)
- **Phase 2 Success**: [PHASE2_SUCCESS.md](./PHASE2_SUCCESS.md)
- **Interactive API Docs**: http://localhost:8000/docs

---

**Version:** 2.0.0

**Last Updated:** October 5, 2025

*Keep this file open in a split pane for quick reference during development*
