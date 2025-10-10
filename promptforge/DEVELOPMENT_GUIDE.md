# PromptForge Development Guide

## Overview

This guide provides best practices, patterns, and instructions for developing PromptForge.

## Architecture Patterns

### 3-Tier Separation

PromptForge follows strict 3-tier architecture:

```
┌─────────────────────────────────────────┐
│         UI Tier (React MFEs)            │
│  - User interface components            │
│  - State management (Redux)             │
│  - API integration (TypeScript clients) │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│         API Tier (FastAPI)              │
│  - Business logic                       │
│  - Authentication & authorization       │
│  - Data validation (Pydantic)           │
└─────────────────┬───────────────────────┘
                  │ SQL/Redis
┌─────────────────▼───────────────────────┐
│    Database Tier (PostgreSQL/Redis)     │
│  - Data persistence                     │
│  - Caching layer                        │
│  - Pub/Sub messaging                    │
└─────────────────────────────────────────┘
```

### Key Principles

1. **No Direct Database Access from UI** - All data flows through API
2. **Type Safety Across Tiers** - PostgreSQL → SQLAlchemy → Pydantic → TypeScript
3. **Async All the Way** - FastAPI + asyncpg + Redis async client
4. **Schema-First Development** - Pydantic schemas define contracts
5. **Micro-Frontend Independence** - Each MFE can be deployed separately

## Backend Development

### Project Structure

```
api-tier/
├── app/
│   ├── api/
│   │   ├── v1/                    # API version 1
│   │   │   ├── auth.py            # Authentication routes
│   │   │   ├── users.py           # User management routes
│   │   │   ├── projects.py        # Project routes
│   │   │   └── ...
│   │   └── dependencies.py        # Shared dependencies (auth, db)
│   ├── models/                    # SQLAlchemy models
│   │   ├── base.py                # Base model with common fields
│   │   ├── user.py                # User & Organization models
│   │   ├── project.py             # Project model
│   │   └── ...
│   ├── schemas/                   # Pydantic schemas
│   │   ├── user.py                # User request/response schemas
│   │   ├── project.py             # Project schemas
│   │   └── ...
│   ├── services/                  # Business logic (future)
│   ├── core/
│   │   ├── config.py              # Settings management
│   │   ├── database.py            # Database connection
│   │   ├── security.py            # JWT & password utilities
│   │   └── redis_client.py        # Redis wrapper
│   └── main.py                    # FastAPI application
├── alembic/
│   ├── versions/                  # Migration files
│   └── env.py                     # Alembic configuration
├── tests/                         # Backend tests
└── requirements.txt               # Python dependencies
```

### Adding a New Model

**Step 1: Create SQLAlchemy Model**

`app/models/feature.py`:
```python
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel

class Feature(BaseModel):
    """Feature model - represents a feature"""

    __tablename__ = "features"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    config = Column(JSON)

    # Foreign Keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="features")
```

**Important Notes:**
- Avoid reserved names like `metadata` (use `feature_metadata` instead)
- Always inherit from `BaseModel` for `id`, `created_at`, `updated_at`
- Use `UUID(as_uuid=True)` for UUID columns
- Add proper relationships with `back_populates`

**Step 2: Update Related Models**

`app/models/project.py`:
```python
class Project(BaseModel):
    # ... existing fields

    # Relationships
    features = relationship("Feature", back_populates="project")
```

**Step 3: Create Pydantic Schemas**

`app/schemas/feature.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class FeatureBase(BaseModel):
    """Base schema for Feature"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class FeatureCreate(FeatureBase):
    """Schema for creating a Feature"""
    project_id: UUID

class FeatureUpdate(BaseModel):
    """Schema for updating a Feature"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class FeatureResponse(FeatureBase):
    """Schema for Feature response"""
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 2.0 compatibility
```

**Step 4: Create API Routes**

`app/api/v1/features.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.feature import Feature
from app.models.user import User
from app.schemas.feature import FeatureCreate, FeatureUpdate, FeatureResponse

router = APIRouter()

@router.get("", response_model=List[FeatureResponse])
async def list_features(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all features"""
    query = select(Feature)

    if project_id:
        query = query.where(Feature.project_id == project_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_in: FeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new feature"""
    feature = Feature(**feature_in.dict())
    db.add(feature)
    await db.commit()
    await db.refresh(feature)
    return feature

@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feature by ID"""
    result = await db.execute(select(Feature).where(Feature.id == feature_id))
    feature = result.scalar_one_or_none()

    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    return feature

@router.put("/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: UUID,
    feature_in: FeatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update feature"""
    result = await db.execute(select(Feature).where(Feature.id == feature_id))
    feature = result.scalar_one_or_none()

    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    update_data = feature_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feature, field, value)

    await db.commit()
    await db.refresh(feature)
    return feature

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete feature"""
    result = await db.execute(select(Feature).where(Feature.id == feature_id))
    feature = result.scalar_one_or_none()

    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    await db.delete(feature)
    await db.commit()
```

**Step 5: Register Router**

`app/main.py`:
```python
from app.api.v1 import features

# Add to routers
app.include_router(features.router, prefix=f"{settings.API_V1_PREFIX}/features", tags=["features"])
```

**Step 6: Create Migration**

```bash
# Auto-generate migration
docker-compose exec api alembic revision --autogenerate -m "add features table"

# Review the generated migration file in alembic/versions/

# Apply migration
docker-compose exec api alembic upgrade head
```

**Step 7: Update Seed Data** (optional)

`database-tier/seeds/seed_data.py`:
```python
# Add sample features
feature1 = Feature(
    name="Auto-save",
    description="Automatic saving feature",
    config={"interval_seconds": 30},
    project_id=project1.id,
)
session.add(feature1)
```

### Database Migrations Best Practices

#### Creating Migrations

```bash
# Auto-generate migration (recommended)
docker-compose exec api alembic revision --autogenerate -m "descriptive message"

# Manual migration (for complex changes)
docker-compose exec api alembic revision -m "descriptive message"
```

#### Migration File Structure

```python
"""add features table

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-10-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Create table
    op.create_table(
        'features',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_features_id'), 'features', ['id'], unique=False)

def downgrade():
    # Reverse changes
    op.drop_index(op.f('ix_features_id'), table_name='features')
    op.drop_table('features')
```

#### Common Migration Patterns

**Adding a column:**
```python
def upgrade():
    op.add_column('projects', sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('projects', 'archived')
```

**Renaming a column:**
```python
def upgrade():
    op.alter_column('projects', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('projects', 'new_name', new_column_name='old_name')
```

**Adding an index:**
```python
def upgrade():
    op.create_index('ix_projects_status', 'projects', ['status'])

def downgrade():
    op.drop_index('ix_projects_status', table_name='projects')
```

### Common Pitfalls & Solutions

#### 1. SQLAlchemy Reserved Names

**Problem:**
```python
class MyModel(BaseModel):
    metadata = Column(JSON)  # ERROR: 'metadata' is reserved
```

**Solution:**
```python
class MyModel(BaseModel):
    model_metadata = Column(JSON)  # Use domain-specific prefix
```

#### 2. Circular Foreign Keys

**Problem:**
```python
class Prompt(BaseModel):
    current_version_id = Column(UUID, ForeignKey("prompt_versions.id"))

class PromptVersion(BaseModel):
    prompt_id = Column(UUID, ForeignKey("prompts.id"))
```

**Solution:**
```python
class Prompt(BaseModel):
    current_version_id = Column(
        UUID,
        ForeignKey("prompt_versions.id", use_alter=True, name='fk_prompt_current_version')
    )
```

#### 3. Missing Async/Await

**Problem:**
```python
@router.get("/users")
def list_users(db: AsyncSession = Depends(get_db)):  # Missing async
    result = db.execute(select(User))  # Missing await
```

**Solution:**
```python
@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
```

#### 4. Not Using `from_attributes`

**Problem:**
```python
class UserResponse(BaseModel):
    id: UUID
    email: str

    class Config:
        orm_mode = True  # Deprecated in Pydantic 2.0
```

**Solution:**
```python
class UserResponse(BaseModel):
    id: UUID
    email: str

    class Config:
        from_attributes = True  # Pydantic 2.0+
```

## Frontend Development

### TypeScript API Client Pattern

**Step 1: Define TypeScript Types**

`ui-tier/shared/types/feature.ts`:
```typescript
export interface Feature {
  id: string;
  name: string;
  description: string | null;
  config: Record<string, any> | null;
  project_id: string;
  created_at: string;
  updated_at: string;
}

export interface FeatureCreate {
  name: string;
  description?: string;
  config?: Record<string, any>;
  project_id: string;
}

export interface FeatureUpdate {
  name?: string;
  description?: string;
  config?: Record<string, any>;
}
```

**Step 2: Create Service**

`ui-tier/shared/services/featureService.ts`:
```typescript
import { apiClient } from './apiClient';
import type { Feature, FeatureCreate, FeatureUpdate } from '../types/feature';

interface GetFeaturesParams {
  skip?: number;
  limit?: number;
  project_id?: string;
}

class FeatureService {
  private basePath = '/features';

  async getFeatures(params?: GetFeaturesParams): Promise<Feature[]> {
    const response = await apiClient.get<Feature[]>(this.basePath, { params });
    return response.data;
  }

  async getFeature(featureId: string): Promise<Feature> {
    const response = await apiClient.get<Feature>(`${this.basePath}/${featureId}`);
    return response.data;
  }

  async createFeature(data: FeatureCreate): Promise<Feature> {
    const response = await apiClient.post<Feature>(this.basePath, data);
    return response.data;
  }

  async updateFeature(featureId: string, data: FeatureUpdate): Promise<Feature> {
    const response = await apiClient.put<Feature>(`${this.basePath}/${featureId}`, data);
    return response.data;
  }

  async deleteFeature(featureId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/${featureId}`);
  }
}

export const featureService = new FeatureService();
```

**Step 3: Create React Hook**

`ui-tier/shared/hooks/useFeatures.ts`:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { featureService } from '../services/featureService';
import type { FeatureCreate, FeatureUpdate } from '../types/feature';

export const useFeatures = (params?: { project_id?: string }) => {
  return useQuery({
    queryKey: ['features', params],
    queryFn: () => featureService.getFeatures(params),
  });
};

export const useFeature = (featureId: string) => {
  return useQuery({
    queryKey: ['features', featureId],
    queryFn: () => featureService.getFeature(featureId),
    enabled: !!featureId,
  });
};

export const useCreateFeature = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FeatureCreate) => featureService.createFeature(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
    },
  });
};

export const useUpdateFeature = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FeatureUpdate }) =>
      featureService.updateFeature(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
      queryClient.invalidateQueries({ queryKey: ['features', variables.id] });
    },
  });
};

export const useDeleteFeature = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (featureId: string) => featureService.deleteFeature(featureId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
    },
  });
};
```

**Step 4: Use in Component**

```typescript
import React from 'react';
import { useFeatures, useCreateFeature } from '@/shared/hooks/useFeatures';

export const FeatureList: React.FC = () => {
  const { data: features, isLoading, error } = useFeatures();
  const createFeature = useCreateFeature();

  const handleCreate = async () => {
    await createFeature.mutateAsync({
      name: 'New Feature',
      description: 'Feature description',
      project_id: 'uuid',
    });
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <button onClick={handleCreate}>Create Feature</button>
      <ul>
        {features?.map((feature) => (
          <li key={feature.id}>{feature.name}</li>
        ))}
      </ul>
    </div>
  );
};
```

## Testing

### Backend Tests (Planned)

```python
# tests/test_features.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_feature(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/features",
        json={
            "name": "Test Feature",
            "description": "Test description",
            "project_id": "uuid",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Feature"
```

### Frontend Tests (Planned)

```typescript
// tests/FeatureList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FeatureList } from './FeatureList';
import { featureService } from '@/shared/services/featureService';

jest.mock('@/shared/services/featureService');

test('renders features list', async () => {
  (featureService.getFeatures as jest.Mock).mockResolvedValue([
    { id: '1', name: 'Feature 1' },
    { id: '2', name: 'Feature 2' },
  ]);

  const queryClient = new QueryClient();

  render(
    <QueryClientProvider client={queryClient}>
      <FeatureList />
    </QueryClientProvider>
  );

  await waitFor(() => {
    expect(screen.getByText('Feature 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 2')).toBeInTheDocument();
  });
});
```

## Environment Configuration

### Development

`.env` (git-ignored):
```bash
# Database
DATABASE_URL=postgresql+asyncpg://promptforge:promptforge@postgres:5432/promptforge

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# App
PROJECT_NAME=PromptForge API
VERSION=2.0.0
API_V1_PREFIX=/api/v1
```

### Production (Example)

```bash
# Use environment-specific values
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/promptforge
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=long-random-secure-key-min-32-chars
BACKEND_CORS_ORIGINS=["https://app.promptforge.com"]
```

## Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency production fixes

### Commit Messages

Follow conventional commits:

```
feat: add feature endpoints and TypeScript client
fix: resolve circular foreign key dependency
docs: update API documentation with examples
refactor: extract database session management
test: add integration tests for features
chore: update dependencies
```

## Performance Optimization

### Database Query Optimization

**Use selective loading:**
```python
# BAD: Loads all fields
result = await db.execute(select(User))

# GOOD: Select only needed fields
result = await db.execute(
    select(User.id, User.email, User.full_name)
)
```

**Use joins instead of N+1 queries:**
```python
# BAD: N+1 queries
projects = await db.execute(select(Project))
for project in projects.scalars():
    prompts = await db.execute(select(Prompt).where(Prompt.project_id == project.id))

# GOOD: Single query with join
result = await db.execute(
    select(Project).options(selectinload(Project.prompts))
)
```

### Redis Caching

```python
from app.core.redis_client import redis_client

async def get_project(project_id: UUID):
    # Try cache first
    cached = await redis_client.get(f"project:{project_id}")
    if cached:
        return json.loads(cached)

    # Fetch from database
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one()

    # Cache for 5 minutes
    await redis_client.setex(
        f"project:{project_id}",
        300,
        json.dumps(project.dict())
    )

    return project
```

## Security Best Practices

1. **Never log sensitive data** (passwords, tokens, PII)
2. **Use parameterized queries** (SQLAlchemy handles this)
3. **Validate all inputs** (Pydantic schemas)
4. **Use HTTPS in production**
5. **Rotate JWT secrets regularly**
6. **Implement rate limiting** (Phase 3)
7. **Use RBAC for authorization** (implemented)

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL/TLS certificates installed
- [ ] CORS origins restricted to production domains
- [ ] SECRET_KEY changed from default
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured
- [ ] Database backups scheduled
- [ ] Redis persistence enabled
- [ ] Rate limiting enabled
- [ ] Health checks configured
- [ ] Monitoring dashboards set up

---

**Version:** 2.0.0

**Last Updated:** October 5, 2025
