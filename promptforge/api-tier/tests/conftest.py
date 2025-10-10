"""
Pytest configuration and shared fixtures for API integration tests
"""

import asyncio
import pytest
import uuid
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User, Organization
from app.core.security import get_password_hash

# Test database URL (use PostgreSQL test database for UUID support)
# Default to 'localhost' for running tests from host machine (simulating browser)
# Set TEST_DB_HOST=postgres when running inside docker
import os
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")  # Default: localhost (host machine)
TEST_DATABASE_URL = f"postgresql+asyncpg://promptforge:promptforge@{TEST_DB_HOST}:5432/promptforge_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create fresh database for each test function
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test HTTP client with database dependency override
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def demo_organization(db_session: AsyncSession) -> Organization:
    """
    Create demo organization for testing
    """
    org = Organization(
        id=uuid.uuid4(),
        name="Demo Organization",
        description="Test organization for API testing",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture(scope="function")
async def demo_user(db_session: AsyncSession, demo_organization: Organization) -> User:
    """
    Create demo user for testing
    Email: demo@promptforge.ai
    Password: demo123
    """
    user = User(
        id=uuid.uuid4(),
        email="demo@promptforge.ai",
        hashed_password=get_password_hash("demo123"),
        full_name="Demo User",
        organization_id=demo_organization.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


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
