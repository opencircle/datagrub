"""
Test suite for Model Provider Configuration API

Tests all CRUD endpoints, RBAC permissions, encryption, and backward compatibility.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Organization, User, UserRole
from app.models.model_provider import ModelProviderConfig, ModelProviderMetadata
from app.services.encryption import EncryptionService
from uuid import uuid4


class TestModelProviderCatalog:
    """Test catalog endpoint (public, no auth required)"""

    async def test_get_catalog(self, client: AsyncClient):
        """Test GET /api/v1/model-providers/catalog"""
        response = await client.get("/api/v1/model-providers/catalog")
        assert response.status_code == 200

        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) > 0

        # Verify structure
        provider = data["providers"][0]
        assert "provider_name" in provider
        assert "provider_type" in provider
        assert "display_name" in provider
        assert "required_fields" in provider

    async def test_get_catalog_filtered_by_type(self, client: AsyncClient):
        """Test catalog filtering by provider type"""
        response = await client.get(
            "/api/v1/model-providers/catalog?provider_type=llm"
        )
        assert response.status_code == 200

        data = response.json()
        for provider in data["providers"]:
            assert provider["provider_type"] == "llm"


class TestModelProviderConfigCRUD:
    """Test CRUD operations for provider configurations"""

    async def test_create_config_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_token: str,
        admin_user: User
    ):
        """Test creating provider config as admin"""
        config_data = {
            "provider_name": "openai",
            "provider_type": "llm",
            "display_name": "Test OpenAI Config",
            "api_key": "sk-proj-test123456789012345678901234567890",
            "config": {
                "default_model": "gpt-4",
                "temperature": 0.7
            }
        }

        response = await client.post(
            "/api/v1/model-providers/configs",
            json=config_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()

        assert data["provider_name"] == "openai"
        assert data["display_name"] == "Test OpenAI Config"
        assert "api_key_masked" in data
        assert data["api_key_masked"].startswith("sk-")
        assert "***" in data["api_key_masked"]
        assert data["organization_id"] == str(admin_user.organization_id)

        # Verify encryption in database
        config_id = data["id"]
        result = await db_session.execute(
            select(ModelProviderConfig).where(
                ModelProviderConfig.id == config_id
            )
        )
        db_config = result.scalar_one()

        # API key should be encrypted
        assert db_config.api_key_encrypted != config_data["api_key"]
        assert len(db_config.api_key_hash) == 64  # SHA-256 hex

        # Config should be encrypted
        assert db_config.config_encrypted is not None

        # Verify decryption works
        encryption_service = EncryptionService()
        decrypted_key = encryption_service.decrypt_api_key(
            db_config.api_key_encrypted
        )
        assert decrypted_key == config_data["api_key"]

    async def test_create_config_non_admin_fails(
        self,
        client: AsyncClient,
        developer_token: str
    ):
        """Test that non-admin users cannot create configs"""
        config_data = {
            "provider_name": "openai",
            "provider_type": "llm",
            "display_name": "Test Config",
            "api_key": "sk-test123"
        }

        response = await client.post(
            "/api/v1/model-providers/configs",
            json=config_data,
            headers={"Authorization": f"Bearer {developer_token}"}
        )

        assert response.status_code == 403

    async def test_list_configs(
        self,
        client: AsyncClient,
        admin_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test listing provider configs"""
        response = await client.get(
            "/api/v1/model-providers/configs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "configs" in data
        assert "total" in data
        assert data["total"] >= 1

        # Find our test config
        config = next(
            (c for c in data["configs"] if c["id"] == str(test_provider_config.id)),
            None
        )
        assert config is not None
        assert "api_key_masked" in config

    async def test_list_configs_filtered(
        self,
        client: AsyncClient,
        admin_token: str
    ):
        """Test listing with filters"""
        response = await client.get(
            "/api/v1/model-providers/configs?provider_type=llm&is_active=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        for config in data["configs"]:
            assert config["provider_type"] == "llm"
            assert config["is_active"] is True

    async def test_get_config_by_id(
        self,
        client: AsyncClient,
        admin_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test getting single config by ID"""
        response = await client.get(
            f"/api/v1/model-providers/configs/{test_provider_config.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_provider_config.id)
        assert "api_key_masked" in data

    async def test_get_config_cross_org_fails(
        self,
        client: AsyncClient,
        admin_token: str,
        other_org_config: ModelProviderConfig
    ):
        """Test that users cannot access configs from other orgs"""
        response = await client.get(
            f"/api/v1/model-providers/configs/{other_org_config.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404

    async def test_update_config_admin(
        self,
        client: AsyncClient,
        admin_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test updating config as admin"""
        update_data = {
            "display_name": "Updated Config Name",
            "config": {
                "default_model": "gpt-4-turbo"
            }
        }

        response = await client.put(
            f"/api/v1/model-providers/configs/{test_provider_config.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["display_name"] == "Updated Config Name"

    async def test_update_config_non_admin_fails(
        self,
        client: AsyncClient,
        developer_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test that non-admin cannot update configs"""
        update_data = {"display_name": "Hacked"}

        response = await client.put(
            f"/api/v1/model-providers/configs/{test_provider_config.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {developer_token}"}
        )

        assert response.status_code == 403

    async def test_delete_config_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test soft-deleting config as admin"""
        response = await client.delete(
            f"/api/v1/model-providers/configs/{test_provider_config.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

        # Verify soft delete
        await db_session.refresh(test_provider_config)
        assert test_provider_config.is_active is False

    async def test_delete_config_non_admin_fails(
        self,
        client: AsyncClient,
        developer_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test that non-admin cannot delete configs"""
        response = await client.delete(
            f"/api/v1/model-providers/configs/{test_provider_config.id}",
            headers={"Authorization": f"Bearer {developer_token}"}
        )

        assert response.status_code == 403


class TestProviderConnectionTest:
    """Test provider connection testing endpoint"""

    async def test_connection_test_openai(
        self,
        client: AsyncClient,
        admin_token: str,
        test_provider_config: ModelProviderConfig
    ):
        """Test OpenAI connection test"""
        response = await client.post(
            f"/api/v1/model-providers/configs/{test_provider_config.id}/test",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # May succeed or fail depending on API key validity
        assert response.status_code in [200, 400, 500]
        data = response.json()

        assert "success" in data
        assert "message" in data

        if data["success"]:
            assert "latency_ms" in data
            assert "models_available" in data


class TestBackwardCompatibility:
    """Test backward compatibility with environment variables"""

    async def test_provider_service_fallback_to_env(
        self,
        db_session: AsyncSession,
        monkeypatch
    ):
        """Test that provider service falls back to env vars"""
        from app.services.provider_config_service import ProviderConfigService

        # Set environment variable
        test_api_key = "sk-test-from-env-123456789012345678901234567890"
        monkeypatch.setenv("OPENAI_API_KEY", test_api_key)

        service = ProviderConfigService(db_session)

        # Create org without any configs
        new_org_id = uuid4()

        config = await service.get_openai_config(
            organization_id=new_org_id
        )

        # Should fall back to env var
        assert config is not None
        assert config["api_key"] == test_api_key
        assert config["display_name"] == "OpenAI (Environment Variable)"

    async def test_provider_service_db_takes_precedence(
        self,
        db_session: AsyncSession,
        monkeypatch,
        test_provider_config: ModelProviderConfig
    ):
        """Test that database config takes precedence over env var"""
        from app.services.provider_config_service import ProviderConfigService

        # Set environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key-123")

        service = ProviderConfigService(db_session)

        config = await service.get_openai_config(
            organization_id=test_provider_config.organization_id
        )

        # Should use database config, not env var
        assert config is not None
        assert config["display_name"] == test_provider_config.display_name
        # API key should be decrypted from database
        assert config["api_key"] != "sk-env-key-123"


class TestEncryption:
    """Test encryption functionality"""

    def test_encrypt_decrypt_api_key(self):
        """Test API key encryption/decryption"""
        service = EncryptionService()

        original_key = "sk-proj-test123456789012345678901234567890"
        encrypted, key_hash = service.encrypt_api_key(original_key)

        assert encrypted != original_key
        assert len(key_hash) == 64  # SHA-256 hex

        decrypted = service.decrypt_api_key(encrypted)
        assert decrypted == original_key

    def test_api_key_masking(self):
        """Test API key masking for display"""
        service = EncryptionService()

        api_key = "sk-proj-abc123def456ghi789"
        masked = service.mask_api_key(api_key, show_chars=3)

        assert masked.startswith("sk-")
        assert "***" in masked
        assert masked.endswith("789")
        assert "abc123def456ghi" not in masked

    def test_validate_api_key_hash(self):
        """Test API key hash validation"""
        service = EncryptionService()

        original_key = "sk-test-key-123"
        _, key_hash = service.encrypt_api_key(original_key)

        # Valid key should match
        assert service.validate_api_key_hash(original_key, key_hash) is True

        # Different key should not match
        assert service.validate_api_key_hash("sk-different-key", key_hash) is False


# Pytest fixtures
@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user for testing"""
    org = Organization(
        id=uuid4(),
        name="Test Organization",
        description="Test org for model providers"
    )
    db_session.add(org)

    user = User(
        id=uuid4(),
        email="admin@test.com",
        hashed_password="hashed",
        full_name="Admin User",
        role=UserRole.ADMIN,
        organization_id=org.id
    )
    db_session.add(user)
    await db_session.commit()

    return user


@pytest.fixture
async def developer_user(db_session: AsyncSession, admin_user: User) -> User:
    """Create developer user for testing"""
    user = User(
        id=uuid4(),
        email="dev@test.com",
        hashed_password="hashed",
        full_name="Developer User",
        role=UserRole.DEVELOPER,
        organization_id=admin_user.organization_id
    )
    db_session.add(user)
    await db_session.commit()

    return user


@pytest.fixture
async def test_provider_config(
    db_session: AsyncSession,
    admin_user: User
) -> ModelProviderConfig:
    """Create test provider config"""
    encryption_service = EncryptionService()
    api_key = "sk-test-key-123456789012345678901234567890"
    encrypted_key, key_hash = encryption_service.encrypt_api_key(api_key)

    config = ModelProviderConfig(
        id=uuid4(),
        organization_id=admin_user.organization_id,
        provider_name="openai",
        provider_type="llm",
        display_name="Test OpenAI Config",
        api_key_encrypted=encrypted_key,
        api_key_hash=key_hash,
        created_by=admin_user.id
    )
    db_session.add(config)
    await db_session.commit()

    return config


@pytest.fixture
async def other_org_config(db_session: AsyncSession) -> ModelProviderConfig:
    """Create config for different org (for cross-org access tests)"""
    other_org = Organization(
        id=uuid4(),
        name="Other Organization"
    )
    db_session.add(other_org)

    encryption_service = EncryptionService()
    api_key = "sk-other-org-key-123"
    encrypted_key, key_hash = encryption_service.encrypt_api_key(api_key)

    config = ModelProviderConfig(
        id=uuid4(),
        organization_id=other_org.id,
        provider_name="openai",
        provider_type="llm",
        display_name="Other Org Config",
        api_key_encrypted=encrypted_key,
        api_key_hash=key_hash
    )
    db_session.add(config)
    await db_session.commit()

    return config
