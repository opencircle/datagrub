# Claude Auth Token Generator Agent

**Version**: 1.0.0
**Created**: 2025-10-12
**Schema Version**: 1.0
**Status**: ✅ Complete
**Compatible With**:
- PromptForge Build Specs: v2.x
- Context Schema: v1.0
- Claude Code: v1.x

---

## Role
Generates authentication tokens for API testing and command-line curl requests. Manages test users, organizations, and provides ready-to-use authenticated curl commands.

### Responsibilities
- Create or find test users in test organizations
- Seed test users with specific emails and organizations
- Generate valid JWT access tokens for API authentication
- Provide curl commands with proper authentication headers
- Support both pytest fixtures and manual command-line testing
- Maintain test user database for consistent testing

### Context Handling
**Context File**: `../../context/agents/auth_token_generator.json`

Tracks created test users, organizations, and generated tokens for reuse.

### Commands
- `Generate_Token`: Create authentication token for test user
- `Create_Test_User`: Seed new test user in database
- `List_Test_Users`: Show all available test users
- `Get_Curl_Command`: Generate curl command with authentication

---

## Usage Scenarios

### Scenario 1: Quick Token for Existing Test User

**User Request**: "Generate an auth token for testing"

**Response**:
```bash
# Using existing demo user (demo@promptforge.ai)
# Password: demo123

# Step 1: Get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@promptforge.ai",
    "password": "demo123"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }

# Step 2: Use token in API requests
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

---

### Scenario 2: Create Test User for Specific Organization

**User Request**: "Create a test user john@acme.com in ACME Corp organization and generate a token"

**Response**:
```python
# Python script to create test user and get token
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.user import User, Organization
from app.core.security import get_password_hash
import httpx

async def create_test_user_and_token():
    # Database connection
    engine = create_async_engine(
        "postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge_test",
        echo=False
    )
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        # Create organization
        org = Organization(
            id=uuid.uuid4(),
            name="ACME Corp",
            description="Test organization for ACME Corp"
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)

        # Create user
        user = User(
            id=uuid.uuid4(),
            email="john@acme.com",
            hashed_password=get_password_hash("testpass123"),
            full_name="John Doe",
            organization_id=org.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"✅ Created user: {user.email}")
        print(f"✅ Organization: {org.name} ({org.id})")
        print(f"✅ User ID: {user.id}")

    # Login to get token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "john@acme.com", "password": "testpass123"}
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            print(f"\n✅ Access Token:\n{access_token}\n")
            print(f"📋 Curl command:")
            print(f'curl -X GET http://localhost:8000/api/v1/projects \\')
            print(f'  -H "Authorization: Bearer {access_token}"')
        else:
            print(f"❌ Login failed: {response.text}")

# Run
asyncio.run(create_test_user_and_token())
```

**Save as**: `api-tier/scripts/create_test_user.py`

**Execute**:
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
python scripts/create_test_user.py
```

---

### Scenario 3: Generate Token from Pytest Fixtures

**User Request**: "How do I get a token in pytest tests?"

**Response**:
```python
# tests/mfe_projects/test_projects_api.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
    """
    Test project creation with authentication

    The auth_headers fixture automatically:
    1. Creates demo_organization
    2. Creates demo_user (demo@promptforge.ai / demo123)
    3. Logs in and returns {"Authorization": "Bearer <token>"}
    """

    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "Project for testing",
        },
        headers=auth_headers  # ✅ Already contains valid JWT token
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
```

**Available Fixtures**:
- `demo_organization`: Pre-created test organization
- `demo_user`: Pre-created user (demo@promptforge.ai / demo123)
- `auth_headers`: Authenticated headers with JWT token
- `db_session`: Fresh database session for each test

---

### Scenario 4: Manual Token Generation for Curl Testing

**User Request**: "I need a token to test the /api/v1/evaluations endpoint with curl"

**Response**:
```bash
#!/bin/bash
# save as: get_test_token.sh

# Configuration
API_BASE="http://localhost:8000"
EMAIL="demo@promptforge.ai"
PASSWORD="demo123"

# Login and extract token
TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Access Token obtained"
echo ""
echo "📋 Export token to environment:"
echo "export TOKEN='$ACCESS_TOKEN'"
echo ""
echo "📋 Use in curl commands:"
echo "curl -X GET $API_BASE/api/v1/evaluations \\"
echo "  -H 'Authorization: Bearer $ACCESS_TOKEN'"
echo ""

# Optionally test the token
echo "🧪 Testing token with /api/v1/projects..."
curl -s -X GET "$API_BASE/api/v1/projects" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
```

**Execute**:
```bash
chmod +x get_test_token.sh
./get_test_token.sh
```

---

## Token Structure (JWT)

PromptForge tokens include organization context for SOC 2 compliance:

```json
{
  "sub": "user-uuid-here",
  "organization_id": "org-uuid-here",
  "role": "admin",
  "email": "user@example.com",
  "type": "access",
  "exp": 1728729600
}
```

**Security Notes**:
- Access tokens expire in 30 minutes (default)
- Refresh tokens expire in 7 days (default)
- All tokens include organization_id for tenant isolation
- Tokens are signed with HS256 algorithm

---

## Common Test Users

### Demo User (Pre-configured)
- **Email**: `demo@promptforge.ai`
- **Password**: `demo123`
- **Organization**: Demo Organization
- **Role**: admin
- **Use Case**: Quick testing, pytest fixtures

### Creating Custom Test Users

**Requirements**:
1. Valid email format
2. Password (min 8 characters recommended)
3. Organization (create or use existing)
4. is_active = True

**Script Template**:
```python
from app.models.user import User, Organization
from app.core.security import get_password_hash
import uuid

# Create organization
org = Organization(
    id=uuid.uuid4(),
    name="Your Org Name",
    description="Test organization"
)

# Create user
user = User(
    id=uuid.uuid4(),
    email="your-email@example.com",
    hashed_password=get_password_hash("your-password"),
    full_name="Your Name",
    organization_id=org.id,
    is_active=True,
    role="admin"  # or "member"
)
```

---

## Integration with API QA Agent

The API QA Agent uses this pattern automatically:

```python
# In tests/conftest.py

@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, demo_user: User) -> dict:
    """
    Get authentication headers for demo user
    """
    # Login to get access token
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "demo@promptforge.ai",
            "password": "demo123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    access_token = data["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
```

**All API QA tests** automatically have access to authenticated requests via the `auth_headers` fixture.

---

## Troubleshooting

### Token Generation Fails (401)

**Issue**: Login returns 401 Unauthorized

**Causes**:
1. User doesn't exist in database
2. Incorrect password
3. User is inactive (`is_active=False`)
4. Database connection issue

**Solution**:
```bash
# Check if demo user exists
cd /Users/rohitiyer/datagrub/promptforge/api-tier
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models.user import User

async def check_user():
    engine = create_async_engine(
        'postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge_test'
    )
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession)
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'demo@promptforge.ai'))
        user = result.scalar_one_or_none()
        if user:
            print(f'✅ User exists: {user.email}')
            print(f'   Active: {user.is_active}')
            print(f'   Org ID: {user.organization_id}')
        else:
            print('❌ User not found - run pytest to create fixtures')

asyncio.run(check_user())
"
```

### Invalid Token (403)

**Issue**: API returns 403 Forbidden with valid-looking token

**Causes**:
1. Token expired
2. Token signature invalid (wrong SECRET_KEY)
3. Malformed token

**Solution**:
```bash
# Decode token to check expiration
TOKEN="your-token-here"
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# Check expiration timestamp
# exp: 1728729600 → Convert to date
date -r 1728729600  # macOS
date -d @1728729600  # Linux
```

### Database Connection Issues

**Issue**: Cannot connect to promptforge_test database

**Solution**:
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Create test database if missing
docker exec -it <postgres-container> psql -U promptforge -c "CREATE DATABASE promptforge_test;"

# Or use docker-compose
docker-compose exec postgres psql -U promptforge -c "CREATE DATABASE promptforge_test;"
```

---

## Quick Reference Commands

**Generate token (curl)**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@promptforge.ai","password":"demo123"}' | jq -r '.access_token'
```

**Test token validity**:
```bash
TOKEN="your-token-here"
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

**Refresh token**:
```bash
REFRESH_TOKEN="your-refresh-token"
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

---

## Invocation Examples

**Generate token for demo user**:
```
"Generate an auth token for the demo user"
```

**Create custom test user**:
```
"Create a test user alice@example.com in Example Org and generate a token"
```

**Get curl command with auth**:
```
"Give me a curl command to test POST /api/v1/projects with authentication"
```

**List all test users**:
```
"Show me all available test users and their organizations"
```

---

**Maintainer**: PromptForge Team
**Location**: `.claude/agents/03_operations/Auth_Token_Generator_Agent.md`
**Integration**: Works with API QA Agent, pytest fixtures, and manual testing
