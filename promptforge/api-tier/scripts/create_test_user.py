#!/usr/bin/env python3
"""
Create Test User - Seed test user for API authentication
Usage: python create_test_user.py --email user@example.com --org "Org Name" [--password pass123]
"""

import asyncio
import argparse
import uuid
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
import httpx

from app.models.user import User, Organization
from app.core.security import get_password_hash


async def find_or_create_organization(db: AsyncSession, name: str, description: str = None) -> Organization:
    """Find existing organization or create new one"""
    result = await db.execute(select(Organization).where(Organization.name == name))
    org = result.scalar_one_or_none()

    if org:
        print(f"✅ Found existing organization: {org.name} ({org.id})")
        return org

    org = Organization(
        id=uuid.uuid4(),
        name=name,
        description=description or f"Test organization for {name}",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    print(f"✅ Created organization: {org.name} ({org.id})")
    return org


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    organization: Organization,
    role: str = "admin"
) -> User:
    """Create test user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"⚠️  User already exists: {existing_user.email} ({existing_user.id})")
        return existing_user

    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        organization_id=organization.id,
        is_active=True,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    print(f"✅ Created user: {user.email} ({user.id})")
    return user


async def get_auth_token(email: str, password: str, api_base: str) -> dict:
    """Login and get authentication tokens"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{api_base}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "access_token": data["access_token"],
                    "refresh_token": data["refresh_token"],
                }
            else:
                return {
                    "success": False,
                    "error": f"Login failed: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }


async def main():
    parser = argparse.ArgumentParser(description="Create test user for API authentication")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--password", default="testpass123", help="User password (default: testpass123)")
    parser.add_argument("--org", "--organization", dest="org_name", required=True, help="Organization name")
    parser.add_argument("--org-desc", dest="org_description", help="Organization description")
    parser.add_argument("--name", "--full-name", dest="full_name", help="User full name (default: from email)")
    parser.add_argument("--role", default="admin", choices=["admin", "member"], help="User role (default: admin)")
    parser.add_argument("--db", default="promptforge_test", help="Database name (default: promptforge_test)")
    parser.add_argument("--api-base", default="http://localhost:8000", help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--skip-token", action="store_true", help="Skip token generation")

    args = parser.parse_args()

    # Default full name from email
    if not args.full_name:
        args.full_name = args.email.split("@")[0].replace(".", " ").title()

    print("🔐 PromptForge Test User Creator")
    print("=" * 80)
    print(f"Email: {args.email}")
    print(f"Full Name: {args.full_name}")
    print(f"Organization: {args.org_name}")
    print(f"Role: {args.role}")
    print(f"Database: {args.db}")
    print("=" * 80)
    print()

    # Database connection
    db_url = f"postgresql+asyncpg://promptforge:promptforge@localhost:5432/{args.db}"
    engine = create_async_engine(db_url, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with SessionLocal() as db:
            # Create organization
            org = await find_or_create_organization(
                db,
                args.org_name,
                args.org_description
            )

            # Create user
            user = await create_user(
                db,
                args.email,
                args.password,
                args.full_name,
                org,
                args.role
            )

            print()
            print("=" * 80)
            print("✅ USER CREATED SUCCESSFULLY")
            print("=" * 80)
            print(f"User ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Password: {args.password}")
            print(f"Organization: {org.name} ({org.id})")
            print(f"Role: {user.role}")
            print()

            if not args.skip_token:
                print("🔑 Generating authentication token...")
                print()
                token_result = await get_auth_token(args.email, args.password, args.api_base)

                if token_result["success"]:
                    access_token = token_result["access_token"]
                    print("=" * 80)
                    print("✅ ACCESS TOKEN")
                    print("=" * 80)
                    print(access_token)
                    print()
                    print("=" * 80)
                    print("📋 EXPORT TO ENVIRONMENT")
                    print("=" * 80)
                    print(f"export TOKEN='{access_token}'")
                    print()
                    print("=" * 80)
                    print("📋 CURL EXAMPLE")
                    print("=" * 80)
                    print(f"curl -X GET {args.api_base}/api/v1/projects \\")
                    print(f"  -H 'Authorization: Bearer {access_token}'")
                    print()
                else:
                    print(f"⚠️  Failed to generate token: {token_result['error']}")
                    print()
                    print("💡 You can get a token later using:")
                    print(f"./scripts/get_test_token.sh {args.email} {args.password}")
                    print()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("=" * 80)
    print("✅ DONE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
