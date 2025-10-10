# API Performance Requirements - Phase 2

**Document Version:** 1.0
**Last Updated:** 2025-10-05
**Target:** SaaS Platform - Financial Services Grade
**Classification:** Internal - Performance Architecture

---

## Executive Summary

PromptForge must deliver enterprise-grade performance suitable for financial services workloads with high throughput, low latency, and horizontal scalability. This document outlines performance requirements, optimization strategies, and best practices.

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time (p95)** | < 200ms | All endpoints |
| **API Response Time (p99)** | < 500ms | All endpoints |
| **Throughput** | 10,000 req/sec | Per instance |
| **Concurrent Users** | 100,000+ | Global platform |
| **Database Query Time (p95)** | < 50ms | All queries |
| **Time to First Byte (TTFB)** | < 100ms | Static assets |
| **Uptime SLA** | 99.9% | Monthly |

---

## 1. Async Programming & Concurrency

### 1.1 Current Implementation ✅

**Already Implemented:**
- ✅ SQLAlchemy 2.0 async engine with asyncpg driver
- ✅ FastAPI async request handlers
- ✅ Async database sessions
- ✅ Connection pooling (pool_size=10, max_overflow=20)

**Database Configuration:**
```python
# app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,              # postgresql+asyncpg://...
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,                 # Health checks
    pool_size=10,                       # Base pool size
    max_overflow=20,                    # Max additional connections
)
```

### 1.2 Async Best Practices

#### A. Always Use Async/Await for I/O Operations

**✅ GOOD - Async I/O:**
```python
@router.get("/configs")
async def list_configs(
    db: AsyncSession = Depends(get_db),  # Async session
):
    # Async database query - non-blocking
    result = await db.execute(select(ModelProviderConfig))
    configs = result.scalars().all()
    return configs
```

**❌ BAD - Blocking I/O:**
```python
@router.get("/configs")
def list_configs_blocking(db: Session = Depends(get_db)):
    # Blocking query - ties up thread!
    configs = db.query(ModelProviderConfig).all()
    return configs
```

#### B. Concurrent Operations with asyncio.gather()

**✅ GOOD - Parallel Execution:**
```python
async def get_dashboard_data(user: User, db: AsyncSession):
    # Execute multiple queries concurrently
    projects_task = db.execute(select(Project).where(...))
    prompts_task = db.execute(select(Prompt).where(...))
    evals_task = db.execute(select(Evaluation).where(...))

    # Wait for all queries to complete in parallel
    projects_result, prompts_result, evals_result = await asyncio.gather(
        projects_task,
        prompts_task,
        evals_task
    )

    return {
        "projects": projects_result.scalars().all(),
        "prompts": prompts_result.scalars().all(),
        "evaluations": evals_result.scalars().all()
    }
```

**❌ BAD - Sequential Execution:**
```python
async def get_dashboard_data_slow(user: User, db: AsyncSession):
    # Queries run one after another - slow!
    projects = (await db.execute(select(Project))).scalars().all()
    prompts = (await db.execute(select(Prompt))).scalars().all()
    evals = (await db.execute(select(Evaluation))).scalars().all()

    return {"projects": projects, "prompts": prompts, "evaluations": evals}
```

#### C. Async HTTP Requests

**✅ GOOD - httpx async client:**
```python
import httpx

async def call_openai_api(api_key: str, prompt: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]}
        )
        return response.json()
```

**❌ BAD - requests (blocking):**
```python
import requests

def call_openai_api_blocking(api_key: str, prompt: str):
    # Blocks entire thread during HTTP call!
    response = requests.post(...)
    return response.json()
```

---

## 2. Database Performance Optimization

### 2.1 Connection Pooling Configuration

**Current Settings:**
```python
pool_size=10           # Baseline connections
max_overflow=20        # Additional connections when needed
pool_pre_ping=True     # Health check before reuse
pool_recycle=3600      # Recycle connections every hour
```

**Recommended Settings by Load:**

| Environment | pool_size | max_overflow | Total Max | Use Case |
|-------------|-----------|--------------|-----------|----------|
| **Development** | 5 | 5 | 10 | Local testing |
| **Staging** | 10 | 20 | 30 | Load testing |
| **Production** | 20 | 30 | 50 | High traffic |
| **Enterprise** | 50 | 50 | 100 | Financial services |

**Implementation:**
```python
# app/core/config.py
class Settings(BaseSettings):
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    DB_ECHO_POOL: bool = False

# app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo_pool=settings.DB_ECHO_POOL,
)
```

### 2.2 Query Optimization

#### A. Use Indexes Strategically

**Required Indexes:**
```sql
-- Organization-scoped queries (most common)
CREATE INDEX idx_provider_configs_org_active
ON model_provider_configs(organization_id, is_active);

-- Provider lookup
CREATE INDEX idx_provider_configs_org_provider
ON model_provider_configs(organization_id, provider_name);

-- Project-scoped queries
CREATE INDEX idx_provider_configs_project
ON model_provider_configs(project_id, is_active)
WHERE project_id IS NOT NULL;

-- Composite index for common filters
CREATE INDEX idx_provider_configs_org_type_active
ON model_provider_configs(organization_id, provider_type, is_active);
```

#### B. Eager Loading vs N+1 Queries

**✅ GOOD - Eager Loading (1 query):**
```python
from sqlalchemy.orm import selectinload

# Load user with organization in single query
result = await db.execute(
    select(User)
    .options(selectinload(User.organization))
    .where(User.id == user_id)
)
user = result.scalar_one()
# user.organization is already loaded - no extra query!
```

**❌ BAD - N+1 Problem (N queries):**
```python
# Load all users
users = (await db.execute(select(User))).scalars().all()

# Each access to .organization triggers a new query!
for user in users:
    print(user.organization.name)  # N additional queries!
```

#### C. Pagination & Limits

**✅ ALWAYS paginate large result sets:**
```python
@router.get("/configs")
async def list_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(ModelProviderConfig)
        .where(ModelProviderConfig.organization_id == org_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()
```

#### D. Bulk Operations

**✅ GOOD - Bulk Insert:**
```python
configs = [
    ModelProviderConfig(provider_name="openai", ...),
    ModelProviderConfig(provider_name="anthropic", ...),
    # ... many more
]
db.add_all(configs)  # Single round-trip
await db.commit()
```

**❌ BAD - Individual Inserts:**
```python
for config_data in configs:
    config = ModelProviderConfig(**config_data)
    db.add(config)
    await db.commit()  # N round-trips!
```

### 2.3 Database Query Monitoring

**Implement slow query logging:**
```python
# app/core/database.py
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()

    # Log slow queries (> 100ms)
    if total > 0.1:
        logger.warning(
            f"Slow query ({total:.2f}s): {statement[:200]}"
        )
```

---

## 3. Caching Strategy

### 3.1 Redis Caching

**Cache Layers:**

1. **Application Cache** - Frequently accessed data
2. **Session Cache** - User sessions (if needed)
3. **Rate Limit Cache** - Request counting
4. **Token Blacklist** - Revoked JWT tokens

**Implementation:**
```python
# app/core/cache.py
from redis import asyncio as aioredis
import json
from typing import Optional, Any

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Cache value with TTL"""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str):
        """Invalidate cache"""
        await self.redis.delete(key)

cache = CacheService(settings.REDIS_URL)
```

**Usage in Endpoints:**
```python
@router.get("/catalog")
async def list_provider_catalog(cache: CacheService = Depends(get_cache)):
    # Try cache first
    cached = await cache.get("provider:catalog")
    if cached:
        return cached

    # Cache miss - query database
    result = await db.execute(select(ModelProviderMetadata))
    providers = result.scalars().all()

    # Cache for 1 hour (catalog rarely changes)
    await cache.set("provider:catalog", providers, ttl=3600)

    return providers
```

### 3.2 Cache Invalidation Strategies

**1. Time-Based (TTL):**
```python
await cache.set("key", value, ttl=300)  # 5 minutes
```

**2. Event-Based:**
```python
@router.post("/configs")
async def create_config(cache: CacheService = Depends(get_cache)):
    # Create config...
    await db.commit()

    # Invalidate cached list
    await cache.delete(f"configs:org:{org_id}")
```

**3. Cache-Aside Pattern:**
```python
async def get_user_with_cache(user_id: UUID):
    cache_key = f"user:{user_id}"

    # 1. Try cache
    cached_user = await cache.get(cache_key)
    if cached_user:
        return cached_user

    # 2. Cache miss - query DB
    user = await db.get(User, user_id)

    # 3. Update cache
    await cache.set(cache_key, user, ttl=600)

    return user
```

### 3.3 HTTP Response Caching

**Cache-Control Headers:**
```python
from fastapi import Response

@router.get("/catalog")
async def list_catalog(response: Response):
    # Set cache headers for CDN/browser caching
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["ETag"] = generate_etag(data)

    return data
```

---

## 4. API Rate Limiting

### 4.1 Token Bucket Algorithm

**Implementation with Redis:**
```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
import time

class RateLimiter:
    def __init__(self, redis_client, requests_per_minute: int = 60):
        self.redis = redis_client
        self.limit = requests_per_minute

    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit"""
        current = time.time()
        window_key = f"rate_limit:{key}:{int(current // 60)}"

        # Increment counter
        count = await self.redis.incr(window_key)

        # Set expiry on first request in window
        if count == 1:
            await self.redis.expire(window_key, 60)

        return count <= self.limit

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get user/org from JWT
    user_id = get_user_from_token(request)

    # Check rate limit
    limiter = RateLimiter(redis_client)
    if not await limiter.check_rate_limit(f"user:{user_id}"):
        raise HTTPException(429, "Rate limit exceeded")

    return await call_next(request)
```

### 4.2 Rate Limit Tiers

| Tier | Requests/Min | Requests/Hour | Use Case |
|------|--------------|---------------|----------|
| **Free** | 60 | 1,000 | Individual developers |
| **Starter** | 300 | 10,000 | Small teams |
| **Professional** | 1,000 | 50,000 | Medium businesses |
| **Enterprise** | 10,000 | 500,000 | Large organizations |

---

## 5. Response Compression

### 5.1 GZIP Compression

**Enable for all responses > 1KB:**
```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

**Compression Ratios:**
- JSON responses: 70-80% reduction
- Large text: 80-90% reduction
- Already compressed (images): minimal benefit

### 5.2 Brotli Compression (Advanced)

**Better compression than GZIP:**
```python
from fastapi_brotli import BrotliMiddleware

app.add_middleware(BrotliMiddleware, quality=4)
```

---

## 6. Background Tasks & Async Processing

### 6.1 FastAPI Background Tasks

**For quick non-critical operations (<5s):**
```python
from fastapi import BackgroundTasks

@router.post("/configs")
async def create_config(background_tasks: BackgroundTasks):
    # Create config (sync - user waits)
    config = await create_provider_config(...)

    # Send notification (async - user doesn't wait)
    background_tasks.add_task(send_notification, user.email, config.id)

    return config
```

### 6.2 Celery for Heavy Tasks

**For long-running operations (>5s):**
```python
# app/workers/tasks.py
from celery import Celery

celery_app = Celery('promptforge', broker=settings.REDIS_URL)

@celery_app.task
def run_evaluation(evaluation_id: str):
    """Run evaluation in background worker"""
    # Long-running LLM evaluation
    result = execute_evaluation(evaluation_id)
    return result

# API endpoint
@router.post("/evaluations/{id}/run")
async def run_evaluation_endpoint(id: UUID):
    # Queue task
    task = run_evaluation.delay(str(id))

    return {
        "status": "queued",
        "task_id": task.id,
        "check_status": f"/evaluations/{id}/status"
    }
```

---

## 7. Database Optimizations

### 7.1 Read Replicas

**Route read-only queries to replicas:**
```python
# app/core/database.py
read_engine = create_async_engine(
    settings.DATABASE_READ_REPLICA_URL,
    pool_size=30,  # More connections for read-heavy workload
)

write_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
)

async def get_read_db():
    """For SELECT queries"""
    async with AsyncSession(read_engine) as session:
        yield session

async def get_write_db():
    """For INSERT/UPDATE/DELETE"""
    async with AsyncSession(write_engine) as session:
        yield session
```

### 7.2 Materialized Views

**For complex reporting queries:**
```sql
-- Refresh every hour
CREATE MATERIALIZED VIEW provider_usage_stats AS
SELECT
    organization_id,
    provider_name,
    COUNT(*) as config_count,
    SUM(usage_count) as total_usage,
    MAX(last_used_at) as last_activity
FROM model_provider_configs
GROUP BY organization_id, provider_name;

CREATE INDEX idx_usage_stats_org ON provider_usage_stats(organization_id);

-- Auto-refresh with pg_cron
SELECT cron.schedule('refresh-usage-stats', '0 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY provider_usage_stats');
```

### 7.3 Partitioning (Large Tables)

**For audit logs, traces, etc.:**
```sql
-- Partition by month
CREATE TABLE audit_logs (
    id UUID,
    event_type VARCHAR,
    created_at TIMESTAMP,
    organization_id UUID,
    ...
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE audit_logs_2025_10 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE audit_logs_2025_11 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

---

## 8. API Response Optimization

### 8.1 Field Selection (GraphQL-style)

**Allow clients to request only needed fields:**
```python
@router.get("/configs")
async def list_configs(
    fields: Optional[str] = Query(None, description="Comma-separated fields"),
):
    # Default: return all fields
    if not fields:
        return configs

    # Client requested specific fields: "id,provider_name,is_active"
    field_list = fields.split(',')
    return [
        {k: v for k, v in config.dict().items() if k in field_list}
        for config in configs
    ]
```

### 8.2 Streaming Responses

**For large datasets:**
```python
from fastapi.responses import StreamingResponse
import json

@router.get("/export/configs")
async def export_configs():
    async def generate():
        # Stream configs one at a time
        query = select(ModelProviderConfig).execution_options(stream_results=True)
        result = await db.stream(query)

        yield "["
        first = True
        async for config in result.scalars():
            if not first:
                yield ","
            yield json.dumps(config.dict())
            first = False
        yield "]"

    return StreamingResponse(generate(), media_type="application/json")
```

---

## 9. Monitoring & Observability

### 9.1 Performance Metrics

**Key Metrics to Track:**
```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('api_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Query duration', ['table'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start
    REQUEST_DURATION.labels(request.method, request.url.path).observe(duration)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()

    return response
```

### 9.2 APM Integration

**Datadog, New Relic, or AWS X-Ray:**
```python
from ddtrace import tracer

@router.get("/configs")
async def list_configs():
    with tracer.trace("list_provider_configs", service="api"):
        with tracer.trace("db.query"):
            result = await db.execute(select(...))

        with tracer.trace("encryption.mask"):
            masked_configs = [mask_api_key(c) for c in configs]

        return masked_configs
```

---

## 10. Load Testing & Benchmarking

### 10.1 Load Testing Tools

**Locust (Python-based):**
```python
# locustfile.py
from locust import HttpUser, task, between

class PromptForgeUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def list_configs(self):
        self.client.get(
            "/api/v1/model-providers/configs",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def create_config(self):
        self.client.post(
            "/api/v1/model-providers/configs",
            headers={"Authorization": f"Bearer {self.token}"},
            json={...}
        )
```

**Run Load Test:**
```bash
# 100 users, 10 new users/second
locust -f locustfile.py --users 100 --spawn-rate 10 --host http://localhost:8000
```

### 10.2 Performance Benchmarks

**Target Results:**

| Endpoint | RPS | p50 | p95 | p99 |
|----------|-----|-----|-----|-----|
| GET /catalog | 10,000 | 20ms | 50ms | 100ms |
| GET /configs (cached) | 15,000 | 10ms | 30ms | 50ms |
| GET /configs (db) | 5,000 | 50ms | 150ms | 300ms |
| POST /configs | 1,000 | 100ms | 200ms | 400ms |
| POST /test | 500 | 200ms | 500ms | 1000ms |

---

## 11. Horizontal Scaling

### 11.1 Stateless Application

**Requirements:**
- ✅ No in-memory session storage
- ✅ JWT-based authentication (no server sessions)
- ✅ Shared cache (Redis)
- ✅ Shared database (PostgreSQL)

### 11.2 Load Balancer Configuration

**AWS ALB / NGINX:**
```nginx
upstream promptforge_api {
    least_conn;  # Route to least busy server

    server api-1:8000 max_fails=3 fail_timeout=30s;
    server api-2:8000 max_fails=3 fail_timeout=30s;
    server api-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;

    location /api/ {
        proxy_pass http://promptforge_api;
        proxy_http_version 1.1;

        # Connection pooling
        proxy_set_header Connection "";
        keepalive_timeout 65;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 11.3 Auto-Scaling Rules

**AWS ECS / Kubernetes:**
```yaml
# CPU-based scaling
- type: TargetTrackingScaling
  targetTrackingScaling:
    predefinedMetricType: ECSServiceAverageCPUUtilization
    targetValue: 70.0

# Request count scaling
- type: TargetTrackingScaling
  targetTrackingScaling:
    predefinedMetricType: ALBRequestCountPerTarget
    targetValue: 1000.0
```

---

## 12. Performance Checklist

### Pre-Deployment Checklist

- [ ] All endpoints use async/await
- [ ] Database connection pooling configured
- [ ] Indexes created for common queries
- [ ] Pagination implemented for large datasets
- [ ] Eager loading used to prevent N+1 queries
- [ ] Redis caching for frequently accessed data
- [ ] Response compression enabled (GZIP)
- [ ] Rate limiting implemented
- [ ] Background tasks for long operations
- [ ] Slow query logging enabled
- [ ] APM/monitoring configured
- [ ] Load testing completed
- [ ] Auto-scaling rules defined
- [ ] CDN configured for static assets
- [ ] Database read replicas configured
- [ ] Connection timeouts set appropriately

---

## 13. Performance Optimization Roadmap

### Phase 1: Foundation (Complete) ✅
- ✅ Async/await throughout
- ✅ asyncpg database driver
- ✅ Connection pooling
- ✅ Basic indexes

### Phase 2: Caching & Optimization (Current)
- [ ] Redis caching layer
- [ ] Response compression
- [ ] Query optimization
- [ ] Rate limiting

### Phase 3: Scaling (Next)
- [ ] Read replicas
- [ ] Horizontal scaling
- [ ] Load balancer
- [ ] Auto-scaling

### Phase 4: Advanced (Future)
- [ ] GraphQL for flexible queries
- [ ] Materialized views
- [ ] Table partitioning
- [ ] Multi-region deployment

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-05 | Engineering Team | Initial release |

---

## Approval

**Document Owner:** VP Engineering
**Review Frequency:** Quarterly
**Next Review Date:** 2026-01-05
