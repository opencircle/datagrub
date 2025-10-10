"""
Prompts API Integration Tests
Tests for GET /api/v1/prompts (used by Playground MFE)
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Organization
from app.models.prompt import Prompt, PromptVersion
from app.models.project import Project


class TestPromptsAPI:
    """Test prompts API endpoints"""

    @pytest.mark.asyncio
    async def test_list_prompts_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test listing prompts for authenticated user
        GIVEN: Authenticated user with prompts in their organization
        WHEN: GET /api/v1/prompts
        THEN: Returns 200 with list of prompts including current_version
        """
        # Create a project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create prompt
        prompt = Prompt(
            id=uuid.uuid4(),
            name="Test Prompt",
            description="A test prompt",
            category="general",
            project_id=project.id,
            created_by=demo_user.id,
        )
        db_session.add(prompt)
        await db_session.flush()

        # Create prompt version
        version = PromptVersion(
            id=uuid.uuid4(),
            prompt_id=prompt.id,
            version_number=1,
            template="You are a helpful assistant. {context}",
            system_message="Be concise and accurate.",
            model_config={"temperature": 0.7, "tone": "professional"},
        )
        db_session.add(version)
        await db_session.flush()

        # Link current version
        prompt.current_version_id = version.id
        await db_session.commit()

        # Test API
        response = await client.get(
            "/api/v1/prompts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify prompt structure
        prompt_data = next((p for p in data if p["id"] == str(prompt.id)), None)
        assert prompt_data is not None
        assert prompt_data["name"] == "Test Prompt"
        assert prompt_data["description"] == "A test prompt"
        assert prompt_data["category"] == "general"

        # Verify current_version is loaded (no MissingGreenlet error)
        assert "current_version" in prompt_data
        if prompt_data["current_version"]:
            assert prompt_data["current_version"]["template"] == "You are a helpful assistant. {context}"
            assert prompt_data["current_version"]["system_message"] == "Be concise and accurate."
            assert "model_config" in prompt_data["current_version"]

    @pytest.mark.asyncio
    async def test_list_prompts_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test listing prompts without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/prompts
        THEN: Returns 403 Forbidden
        """
        response = await client.get("/api/v1/prompts")

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_list_prompts_with_project_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering prompts by project_id
        GIVEN: Multiple projects with prompts
        WHEN: GET /api/v1/prompts?project_id={id}
        THEN: Returns only prompts for that project
        """
        # Create two projects
        project1 = Project(
            id=uuid.uuid4(),
            name="Project 1",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        project2 = Project(
            id=uuid.uuid4(),
            name="Project 2",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project1)
        db_session.add(project2)
        await db_session.flush()

        # Create prompts in each project
        prompt1 = Prompt(
            id=uuid.uuid4(),
            name="Prompt in Project 1",
            project_id=project1.id,
            created_by=demo_user.id,
        )
        prompt2 = Prompt(
            id=uuid.uuid4(),
            name="Prompt in Project 2",
            project_id=project2.id,
            created_by=demo_user.id,
        )
        db_session.add(prompt1)
        db_session.add(prompt2)
        await db_session.commit()

        # Test filtering
        response = await client.get(
            f"/api/v1/prompts?project_id={project1.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Verify only project1 prompts returned
        prompt_ids = [p["id"] for p in data]
        assert str(prompt1.id) in prompt_ids
        assert str(prompt2.id) not in prompt_ids

    @pytest.mark.asyncio
    async def test_get_prompt_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting single prompt by ID
        GIVEN: Prompt with version exists
        WHEN: GET /api/v1/prompts/{id}
        THEN: Returns 200 with prompt details including current_version
        """
        # Create prompt with version
        project = Project(
            id=uuid.uuid4(),
            name="Get Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        prompt = Prompt(
            id=uuid.uuid4(),
            name="Get Test Prompt",
            description="Test getting by ID",
            project_id=project.id,
            created_by=demo_user.id,
        )
        db_session.add(prompt)
        await db_session.flush()

        version = PromptVersion(
            id=uuid.uuid4(),
            prompt_id=prompt.id,
            version_number=1,
            template="Test template",
        )
        db_session.add(version)
        await db_session.flush()

        prompt.current_version_id = version.id
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/prompts/{prompt.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(prompt.id)
        assert data["name"] == "Get Test Prompt"
        assert data["description"] == "Test getting by ID"
        assert "current_version" in data
        if data["current_version"]:
            assert data["current_version"]["template"] == "Test template"

    @pytest.mark.asyncio
    async def test_get_prompt_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test getting non-existent prompt
        GIVEN: Invalid prompt ID
        WHEN: GET /api/v1/prompts/{invalid_id}
        THEN: Returns 404 Not Found
        """
        response = await client.get(
            "/api/v1/prompts/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Prompt not found"

    @pytest.mark.asyncio
    async def test_list_prompts_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test pagination with skip and limit
        GIVEN: Multiple prompts exist
        WHEN: GET /api/v1/prompts?skip=0&limit=2
        THEN: Returns limited number of prompts
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Pagination Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create 5 prompts
        for i in range(5):
            prompt = Prompt(
                id=uuid.uuid4(),
                name=f"Prompt {i}",
                project_id=project.id,
                created_by=demo_user.id,
            )
            db_session.add(prompt)

        await db_session.commit()

        # Test pagination
        response = await client.get(
            "/api/v1/prompts?skip=0&limit=2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_jwt_token_extracts_user_and_organization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        demo_organization: Organization,
        db_session: AsyncSession,
    ):
        """
        Test that JWT token correctly identifies user and organization
        GIVEN: Valid JWT token for demo user
        WHEN: GET /api/v1/prompts
        THEN: API uses correct user context from JWT

        This validates:
        1. JWT token is decoded correctly
        2. User is identified from token payload
        3. Organization is looked up from user
        4. Data is scoped to user's organization
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
            description="Another test organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create user in other org
        other_user = User(
            id=uuid.uuid4(),
            email="other@test.com",
            hashed_password="hashed",
            organization_id=other_org.id,
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create project in other org
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=other_user.id,
        )
        db_session.add(other_project)
        await db_session.flush()

        # Create prompt in other org
        other_prompt = Prompt(
            id=uuid.uuid4(),
            name="Other Org Prompt",
            project_id=other_project.id,
            created_by=other_user.id,
        )
        db_session.add(other_prompt)
        await db_session.commit()

        # Call API with demo_user's token
        response = await client.get(
            "/api/v1/prompts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify we DON'T see other organization's prompts
        prompt_ids = [p["id"] for p in data]
        assert str(other_prompt.id) not in prompt_ids

        # This confirms JWT token correctly scoped data to demo_user's organization
