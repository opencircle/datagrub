"""
Create Oiiro User Account

This script creates a user account for Oiiro organization.
Email: rohit.iyer@oiiro.com
Password: Welcome123
"""
import asyncio
import sys
from pathlib import Path
import os

# Add api-tier directory to path
api_tier_path = os.environ.get('API_TIER_PATH', str(Path(__file__).parent.parent.parent / "api-tier"))
sys.path.insert(0, api_tier_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
import uuid

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, Organization, UserRole


async def create_oiiro_user():
    """Create Oiiro organization and user account"""

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n🏢 Setting up Oiiro Organization and User...")
        print("=" * 60)

        # Check if Oiiro organization exists
        result = await session.execute(
            select(Organization).where(Organization.name == "Oiiro")
        )
        oiiro_org = result.scalar_one_or_none()

        if oiiro_org:
            print(f"✅ Oiiro organization already exists (ID: {oiiro_org.id})")
        else:
            print("📝 Creating Oiiro organization...")
            oiiro_org = Organization(
                id=uuid.uuid4(),
                name="Oiiro",
                description="Oiiro - AI-powered customer experience platform"
            )
            session.add(oiiro_org)
            await session.flush()
            print(f"✅ Created Oiiro organization (ID: {oiiro_org.id})")

        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == "rohit.iyer@oiiro.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"⚠️  User rohit.iyer@oiiro.com already exists (ID: {existing_user.id})")
            print("\n🔄 Updating password to 'Welcome123'...")

            # Update password
            existing_user.hashed_password = get_password_hash("Welcome123")
            existing_user.is_active = True
            existing_user.role = UserRole.ADMIN

            await session.commit()
            print("✅ Password updated successfully!")

        else:
            print("👤 Creating user account...")
            oiiro_user = User(
                id=uuid.uuid4(),
                email="rohit.iyer@oiiro.com",
                hashed_password=get_password_hash("Welcome123"),
                full_name="Rohit Iyer",
                role=UserRole.ADMIN,
                organization_id=oiiro_org.id,
                is_active=True,
            )
            session.add(oiiro_user)
            await session.commit()
            print(f"✅ Created user account (ID: {oiiro_user.id})")

        print("\n" + "=" * 60)
        print("✅ Oiiro Account Setup Complete!")
        print("=" * 60)
        print("\nCredentials:")
        print(f"  Email:    rohit.iyer@oiiro.com")
        print(f"  Password: Welcome123")
        print(f"  Role:     ADMIN")
        print(f"  Org:      Oiiro")
        print("\nYou can now login with these credentials!")
        print()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_oiiro_user())
