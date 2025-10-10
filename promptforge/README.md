# PromptForge - AI Governance & Prompt Management Platform

## Phase 1: Core UI Build - Complete ✅
## Phase 2: Core APIs & Platform - Complete ✅

A modern, scalable SaaS platform for Prompt Management, PromptOps, and AI Risk Governance built with React 18, TypeScript, FastAPI, PostgreSQL, and Redis.

## 🏗️ Architecture

PromptForge uses a **3-tier architecture** with micro-frontend UI, FastAPI backend, and PostgreSQL/Redis data layer.

### 3-Tier Structure

```
promptforge/
├── ui-tier/                  # Frontend Layer
│   ├── shell/                # Host application (Port 3000)
│   │   ├── src/
│   │   │   ├── components/   # Layout components
│   │   │   ├── pages/        # Login, Dashboard pages
│   │   │   ├── store/        # Redux Toolkit state
│   │   │   └── App.tsx       # Main routing
│   │   └── webpack.config.js # Module Federation config
│   │
│   ├── mfe-projects/         # Projects MFE (Port 3001)
│   ├── mfe-evaluations/      # Evaluations MFE (Port 3002)
│   ├── mfe-playground/       # Playground MFE (Port 3003)
│   ├── mfe-traces/           # Traces MFE (Port 3004)
│   ├── mfe-policy/           # Policy MFE (Port 3005)
│   ├── mfe-models/           # Models MFE (Port 3006)
│   ├── mfe-insights/         # Deep Insights MFE (Port 3007)
│   └── shared/               # Shared API services & types
│
├── api-tier/                 # Backend Layer
│   ├── app/
│   │   ├── api/              # API routes & dependencies
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── core/             # Config, security, database
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── tests/                # Backend tests
│   └── requirements.txt      # Python dependencies
│
└── database-tier/            # Data Layer
    ├── seeds/                # Sample data scripts
    └── scripts/              # Database utilities
```

## ✨ Features

### Implemented in Phase 1 (UI Tier)

- ✅ **Micro-Frontend Architecture** - Webpack Module Federation
- ✅ **Projects Management** - Create and manage AI prompt projects
- ✅ **Evaluations** - Run and monitor prompt performance tests
- ✅ **Playground** - Interactive prompt testing environment
- ✅ **Traces** - Request monitoring and debugging
- ✅ **Policy** - AI governance rules and compliance
- ✅ **Models** - Model registry and configuration
- ✅ **Deep Insights** - Call transcript analysis with 3-stage DTA pipeline
- ✅ **Responsive Design** - Mobile-first, accessible UI
- ✅ **Dark Mode** - Theme switching support
- ✅ **Mock APIs** - Fully functional demo data

### Implemented in Phase 2 (API & Database Tier)

- ✅ **FastAPI Backend** - 50+ RESTful endpoints with async support
- ✅ **JWT Authentication** - Access & refresh tokens with automatic renewal
- ✅ **PostgreSQL Database** - 13 normalized tables with relationships
- ✅ **Redis Integration** - Caching and pub/sub support
- ✅ **Database Migrations** - Alembic migration system
- ✅ **OpenAPI Documentation** - Interactive Swagger UI
- ✅ **TypeScript API Client** - Type-safe frontend services
- ✅ **Docker Compose** - Multi-container development environment
- ✅ **Sample Data Seeding** - Realistic test data generation
- ✅ **Role-Based Access** - Admin, Developer, Viewer roles

## 🚀 Quick Start

### Prerequisites

**Frontend:**
- **Node.js** 18.x or later
- **npm** 9.x or later

**Backend:**
- **Docker** 20.10 or later
- **Docker Compose** 2.0 or later

**Optional:**
- **Python** 3.11+ (for local development without Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd promptforge
   ```

2. **Start the backend services**
   ```bash
   docker-compose up -d
   ```

   This starts PostgreSQL, Redis, and the FastAPI backend.

3. **Run database migrations** (first time only)
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **Seed the database** (optional, for demo data)
   ```bash
   docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
   ```

5. **Install frontend dependencies**
   ```bash
   cd ui-tier
   npm run install:all
   ```

### Running the Application

#### Full Stack (Recommended)

**Terminal 1 - Backend:**
```bash
# Already running from docker-compose up -d
# View logs with:
docker-compose logs -f api
```

**Terminal 2 - Frontend:**
```bash
cd ui-tier
npm run start:all
```

This starts all 8 frontend applications:
- Shell (http://localhost:3000)
- Projects MFE (http://localhost:3001)
- Evaluations MFE (http://localhost:3002)
- Playground MFE (http://localhost:3003)
- Traces MFE (http://localhost:3004)
- Policy MFE (http://localhost:3005)
- Models MFE (http://localhost:3006)
- Deep Insights MFE (http://localhost:3007)

#### Option 2: Start Individually

```bash
# Terminal 1 - Shell
npm run start:shell

# Terminal 2 - Projects
npm run start:projects

# Terminal 3 - Evaluations
npm run start:evaluations

# Terminal 4 - Playground
npm run start:playground

# Terminal 5 - Traces
npm run start:traces

# Terminal 6 - Policy
npm run start:policy

# Terminal 7 - Models
npm run start:models
```

### Accessing the Application

**Frontend (UI Tier):**
1. Open your browser to **http://localhost:3000**
2. You'll see the login page
3. Use the demo credentials:
   - **Email:** admin@promptforge.com
   - **Password:** admin123
4. After login, you'll be redirected to the dashboard

**Backend (API Tier):**
- **API Documentation:** http://localhost:8000/docs
- **OpenAPI Spec:** http://localhost:8000/api/v1/openapi.json
- **Health Check:** http://localhost:8000/health

**Test Credentials:**
| Role      | Email                        | Password  |
|-----------|------------------------------|-----------|
| Admin     | admin@promptforge.com        | admin123  |
| Developer | developer@promptforge.com    | dev123    |
| Viewer    | viewer@promptforge.com       | viewer123 |

## 📱 Application Pages

### Dashboard
- Welcome screen with key metrics
- Quick actions for common tasks
- Real-time statistics overview

### Projects
- View all AI prompt projects
- Search and filter by tags
- Project status tracking (active, draft, archived)
- Prompt count and last update information

### Evaluations
- Monitor prompt performance tests
- View evaluation scores and metrics
- Track accuracy, latency, and cost
- Filter by status (running, completed, failed)

### Playground
- Interactive prompt testing interface
- Multiple AI model support
- Adjustable parameters (temperature, tokens, etc.)
- Session history tracking

### Traces
- Request trace monitoring
- Multi-span trace visualization
- Error tracking and debugging
- Performance metrics

### Policy
- AI governance rule management
- Violation tracking
- Compliance monitoring
- Policy categories (security, compliance, cost, quality)

### Models
- Model registry across providers
- Pricing and performance information
- Provider filtering
- Usage metrics tracking

## 🛠️ Technology Stack

### UI Tier (Frontend)
- **React 18.2** - UI framework
- **TypeScript 5.3** - Type safety
- **TailwindCSS 3.3** - Utility-first CSS
- **Framer Motion 10.16** - Animations
- **Redux Toolkit 2.0** - Global state
- **TanStack Query 5.12** - Server state
- **React Router 6.20** - Navigation
- **Webpack 5.89** - Module bundler
- **Module Federation** - Micro-frontend architecture
- **Axios** - HTTP client with interceptors

### API Tier (Backend)
- **FastAPI 0.109** - Async web framework
- **SQLAlchemy 2.0.25** - Async ORM
- **Alembic 1.13.1** - Database migrations
- **Pydantic 2.5.3** - Data validation
- **python-jose** - JWT token handling
- **passlib + bcrypt** - Password hashing
- **asyncpg** - PostgreSQL async driver
- **redis-py 5.0.1** - Redis client
- **Uvicorn** - ASGI server

### Database Tier
- **PostgreSQL 16** - Primary database
- **Redis 7** - Cache and pub/sub
- **Docker Compose** - Container orchestration

### Testing (Planned)
- **Jest 29.7** - Frontend unit testing
- **React Testing Library 14.1** - Component testing
- **pytest** - Backend unit testing
- **httpx** - Async HTTP testing

## 📦 Build for Production

```bash
# Build all applications
npm run build:all

# Build individual applications
npm run build:shell
npm run build:projects
npm run build:evaluations
npm run build:playground
npm run build:traces
npm run build:policy
npm run build:models
```

Build outputs will be in each application's `dist/` directory.

## 🎨 Design System

PromptForge uses a custom design system built with Tailwind CSS:

- **Colors:** CSS variables for easy theming
- **Typography:** System font stack with custom scale
- **Spacing:** Consistent 4px base unit
- **Shadows:** Subtle elevation system
- **Animations:** Framer Motion for smooth transitions

## 🔐 Authentication

**Phase 2 Implementation:**

- **JWT-Based Auth:** Access tokens (30 min) + Refresh tokens (7 days)
- **Password Hashing:** bcrypt with salt rounds
- **Token Storage:** LocalStorage with automatic refresh
- **Protected Routes:** Automatic redirect to login
- **API Security:** Bearer token authentication on all endpoints
- **Role-Based Access:** Admin, Developer, Viewer permissions
- **Automatic Token Renewal:** Axios interceptors handle token refresh

## 📊 Database Schema

**13 Tables with Full Relationships:**

- **users** - User accounts with role-based access
- **organizations** - Multi-tenant organization structure
- **projects** - AI prompt projects
- **prompts** - Prompt templates with versioning
- **prompt_versions** - Version history for prompts
- **evaluations** - Prompt performance tests
- **evaluation_results** - Individual test results
- **traces** - Request/response traces for observability
- **spans** - Detailed trace spans
- **policies** - Governance rules
- **policy_violations** - Policy violation records
- **model_providers** - AI provider registry (OpenAI, Anthropic, etc.)
- **ai_models** - Model configurations with pricing

**Sample Data Included:**
- 1 Demo organization
- 3 User accounts (admin, developer, viewer)
- 2 Model providers (OpenAI, Anthropic)
- 2 AI models (GPT-4, Claude 3)
- 3 Projects with various statuses
- 1 Prompt with version history
- 3 Policies (PII detection, toxicity filter, cost limit)
- 1 Evaluation with 10 test results
- 5 Traces with spans

## 🗂️ Project Structure Details

### Shell Application

The shell is the host application that:
- Manages routing and navigation
- Provides layout (sidebar, header)
- Handles authentication
- Dynamically loads micro-frontends
- Manages global state

### Micro-Frontends

Each MFE is:
- **Independent:** Runs standalone on its own port
- **Integrated:** Loads into shell via Module Federation
- **Self-contained:** Own dependencies and state
- **Themed:** Inherits shell's theme and styling

## 🧪 Development

### Adding a New MFE

1. Create directory: `mfe-<name>/`
2. Copy structure from existing MFE
3. Update `webpack.config.js` with unique name and port
4. Update `package.json` with correct metadata
5. Add remote to shell's `webpack.config.js`
6. Create loader component in shell
7. Add route to shell's `App.tsx`
8. Update root `package.json` scripts

### Modifying an MFE

1. Navigate to MFE directory
2. Make changes to `src/` files
3. Hot reload will update automatically
4. Test in isolation on MFE's port
5. Test integration in shell on port 3000

## 📝 Next Steps (Phase 3 - Full Stack Integration)

**Frontend Integration:**
- [ ] Replace mock data with real API calls in all MFEs
- [ ] Update authentication to use JWT from backend
- [ ] Add TanStack Query hooks for data fetching
- [ ] Implement proper error handling and loading states
- [ ] Update Redux slices for real token management

**Testing:**
- [ ] Backend unit tests (pytest)
- [ ] Backend integration tests
- [ ] Frontend unit tests (Jest)
- [ ] Frontend component tests (React Testing Library)
- [ ] E2E tests (Playwright/Cypress)

**Production Readiness:**
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] Error tracking (Sentry)
- [ ] Database backups
- [ ] SSL/TLS configuration
- [ ] Performance optimization
- [ ] CI/CD pipeline

**Future Features:**
- [ ] Git integration for prompt versioning
- [ ] Real-time evaluations with AI models
- [ ] Observability with Langfuse
- [ ] Prompt playground with real LLM calls
- [ ] Advanced analytics and reporting

## 🤝 Contributing

This project follows the [PromptForge Build Specification](./PromptForge_Build_Specs/README.md) for structured, phased development.

## 📄 License

MIT

## 🐛 Common Issues & Solutions

### Backend Issues

**Issue: Database connection failed**
```bash
# Check if containers are running
docker-compose ps

# Restart services
docker-compose restart postgres api
```

**Issue: Migration errors**
```bash
# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

**Issue: Import errors in seed script**
```bash
# Ensure API_TIER_PATH is set
docker-compose exec -e API_TIER_PATH=/app api python /database-tier/seeds/seed_data.py
```

### Frontend Issues

**Issue: Module Federation loading errors**
```bash
# Ensure all MFEs are running
cd ui-tier
npm run start:all
```

**Issue: CORS errors**
```bash
# Backend CORS is configured for http://localhost:3000
# Check BACKEND_CORS_ORIGINS in docker-compose.yml
```

## 🔍 Key Learnings from Phase 2

### SQLAlchemy Reserved Names
**Problem:** Column name `metadata` conflicts with SQLAlchemy's reserved attribute.

**Solution:** Renamed to domain-specific names:
- `Trace.metadata` → `trace_metadata`
- `Span.metadata` → `span_metadata`
- `PolicyViolation.metadata` → `violation_metadata`

### Circular Foreign Keys
**Problem:** `prompts.current_version_id` references `prompt_versions.id`, but `prompt_versions.prompt_id` references `prompts.id`.

**Solution:** Added `use_alter=True` to break circular dependency:
```python
current_version_id = Column(
    UUID(as_uuid=True),
    ForeignKey("prompt_versions.id", use_alter=True, name='fk_prompt_current_version')
)
```

### Docker Database Connections
**Problem:** Alembic trying to connect to `localhost` instead of Docker container.

**Solution:** Override database URL from environment:
```python
# alembic/env.py
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
```

### Dependency Compatibility
**Problem:** bcrypt version incompatibility with passlib.

**Solution:** Pin compatible versions:
```txt
bcrypt==4.0.1
email-validator==2.1.0
```

---

**PromptForge** - Built with Claude Code for enterprise AI governance.

*Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 Ready* 🚀
