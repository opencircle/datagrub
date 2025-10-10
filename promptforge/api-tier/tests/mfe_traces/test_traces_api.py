"""
Traces API Integration Tests
Tests for /api/v1/traces endpoints (used by Traces MFE)
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.user import User, Organization
from app.models.project import Project
from app.models.trace import Trace, Span
from app.models.model import AIModel, ModelProvider, ModelProviderType


class TestTracesAPI:
    """Test traces API endpoints"""

    @pytest.mark.asyncio
    async def test_list_traces_with_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test listing traces with pagination
        GIVEN: Authenticated user with traces in their organization
        WHEN: GET /api/v1/traces?page=1&page_size=5
        THEN: Returns 200 with paginated trace list
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create model provider and model
        provider = ModelProvider(
            id=uuid.uuid4(),
            name="OpenAI",
            provider_type=ModelProviderType.OPENAI,
        )
        db_session.add(provider)
        await db_session.flush()

        model = AIModel(
            id=uuid.uuid4(),
            name="GPT-4",
            model_id="gpt-4",
            provider_id=provider.id,
        )
        db_session.add(model)
        await db_session.flush()

        # Create 10 traces
        trace_ids = []
        for i in range(10):
            trace = Trace(
                id=uuid.uuid4(),
                trace_id=f"trace-{i:03d}",
                name=f"Test Trace {i}",
                status="success",
                project_id=project.id,
                model_id=model.id,
                total_duration_ms=100.0 + i,
            )
            db_session.add(trace)
            trace_ids.append(trace.id)

        await db_session.commit()

        # Test API with pagination
        response = await client.get(
            "/api/v1/traces?page=1&page_size=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "traces" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total"] == 10
        assert len(data["traces"]) == 5

        # Verify trace structure
        trace_data = data["traces"][0]
        assert "id" in trace_data
        assert "trace_id" in trace_data
        assert "project_name" in trace_data
        assert "status" in trace_data
        assert "model_name" in trace_data
        assert "total_duration_ms" in trace_data
        assert "created_at" in trace_data
        assert "user_email" in trace_data

        assert trace_data["project_name"] == "Test Project"
        assert trace_data["model_name"] == "GPT-4"

    @pytest.mark.asyncio
    async def test_list_traces_with_search(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test searching traces by trace_id, project name, or user email
        GIVEN: Traces with different trace_ids and project names
        WHEN: GET /api/v1/traces?search=special
        THEN: Returns only matching traces
        """
        # Create projects
        project1 = Project(
            id=uuid.uuid4(),
            name="Special Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        project2 = Project(
            id=uuid.uuid4(),
            name="Normal Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add_all([project1, project2])
        await db_session.flush()

        # Create traces
        trace1 = Trace(
            id=uuid.uuid4(),
            trace_id="special-trace-001",
            name="Special Trace",
            status="success",
            project_id=project1.id,
        )
        trace2 = Trace(
            id=uuid.uuid4(),
            trace_id="normal-trace-001",
            name="Normal Trace",
            status="success",
            project_id=project2.id,
        )
        db_session.add_all([trace1, trace2])
        await db_session.commit()

        # Test search by trace_id
        response = await client.get(
            "/api/v1/traces?search=special",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Verify only matching traces returned
        trace_ids = [t["trace_id"] for t in data["traces"]]
        assert "special-trace-001" in trace_ids or any("Special" in t["project_name"] for t in data["traces"])

    @pytest.mark.asyncio
    async def test_list_traces_with_model_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering traces by model name
        GIVEN: Traces using different models
        WHEN: GET /api/v1/traces?model=GPT-4
        THEN: Returns only traces using GPT-4
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create providers and models
        provider = ModelProvider(
            id=uuid.uuid4(),
            name="OpenAI",
            provider_type=ModelProviderType.OPENAI,
        )
        db_session.add(provider)
        await db_session.flush()

        gpt4 = AIModel(
            id=uuid.uuid4(),
            name="GPT-4",
            model_id="gpt-4",
            provider_id=provider.id,
        )
        gpt35 = AIModel(
            id=uuid.uuid4(),
            name="GPT-3.5",
            model_id="gpt-3.5-turbo",
            provider_id=provider.id,
        )
        db_session.add_all([gpt4, gpt35])
        await db_session.flush()

        # Create traces with different models
        trace1 = Trace(
            id=uuid.uuid4(),
            trace_id="gpt4-trace-001",
            name="GPT-4 Trace",
            status="success",
            project_id=project.id,
            model_id=gpt4.id,
        )
        trace2 = Trace(
            id=uuid.uuid4(),
            trace_id="gpt35-trace-001",
            name="GPT-3.5 Trace",
            status="success",
            project_id=project.id,
            model_id=gpt35.id,
        )
        db_session.add_all([trace1, trace2])
        await db_session.commit()

        # Test model filter
        response = await client.get(
            "/api/v1/traces?model=GPT-4",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify only GPT-4 traces returned
        for trace in data["traces"]:
            if trace["model_name"]:
                assert "GPT-4" in trace["model_name"]

    @pytest.mark.asyncio
    async def test_list_traces_with_sorting(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test sorting traces by different columns
        GIVEN: Traces with different durations
        WHEN: GET /api/v1/traces?sort_by=duration&sort_direction=asc
        THEN: Returns traces sorted by duration ascending
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create traces with different durations
        for i in range(5):
            trace = Trace(
                id=uuid.uuid4(),
                trace_id=f"trace-{i:03d}",
                name=f"Test Trace {i}",
                status="success",
                project_id=project.id,
                total_duration_ms=float(500 - i * 100),  # 500, 400, 300, 200, 100
            )
            db_session.add(trace)

        await db_session.commit()

        # Test ascending sort by duration
        response = await client.get(
            "/api/v1/traces?sort_by=duration&sort_direction=asc&page_size=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify ascending order
        durations = [t["total_duration_ms"] for t in data["traces"] if t["total_duration_ms"]]
        assert durations == sorted(durations)

        # Test descending sort by duration
        response = await client.get(
            "/api/v1/traces?sort_by=duration&sort_direction=desc&page_size=5",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify descending order
        durations = [t["total_duration_ms"] for t in data["traces"] if t["total_duration_ms"]]
        assert durations == sorted(durations, reverse=True)

    @pytest.mark.asyncio
    async def test_create_trace_with_organization_scoping(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test creating trace with organization validation
        GIVEN: Authenticated user and valid project
        WHEN: POST /api/v1/traces
        THEN: Creates trace successfully
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.commit()

        # Create trace
        trace_data = {
            "trace_id": "test-trace-001",
            "name": "Test Trace",
            "status": "success",
            "project_id": str(project.id),
            "total_duration_ms": 123.45,
        }

        response = await client.post(
            "/api/v1/traces",
            headers=auth_headers,
            json=trace_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["trace_id"] == "test-trace-001"
        assert data["name"] == "Test Trace"
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_trace_wrong_organization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test creating trace for project in different organization
        GIVEN: Project in different organization
        WHEN: POST /api/v1/traces with that project_id
        THEN: Returns 404 (project not found or access denied)
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create project in other organization
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=demo_user.id,
        )
        db_session.add(other_project)
        await db_session.commit()

        # Try to create trace for other org's project
        trace_data = {
            "trace_id": "test-trace-002",
            "name": "Test Trace",
            "status": "success",
            "project_id": str(other_project.id),
        }

        response = await client.post(
            "/api/v1/traces",
            headers=auth_headers,
            json=trace_data,
        )

        assert response.status_code == 404
        assert "not found or access denied" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_trace_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting trace by ID with organization scoping
        GIVEN: Trace in user's organization
        WHEN: GET /api/v1/traces/{trace_id}
        THEN: Returns trace with details
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace with spans
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="test-trace-003",
            name="Test Trace",
            status="success",
            project_id=project.id,
            total_duration_ms=250.5,
        )
        db_session.add(trace)
        await db_session.flush()

        # Create span
        span = Span(
            id=uuid.uuid4(),
            span_id="span-001",
            name="Test Span",
            start_time=1234567890.0,
            trace_id=trace.id,
        )
        db_session.add(span)
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}?include_spans=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == "test-trace-003"
        assert data["name"] == "Test Trace"
        assert data["status"] == "success"
        assert "spans" in data
        assert len(data["spans"]) == 1
        assert data["spans"][0]["span_id"] == "span-001"

    @pytest.mark.asyncio
    async def test_get_trace_wrong_organization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test accessing trace from different organization
        GIVEN: Trace in different organization
        WHEN: GET /api/v1/traces/{trace_id}
        THEN: Returns 404
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create project in other organization
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=demo_user.id,
        )
        db_session.add(other_project)
        await db_session.flush()

        # Create trace in other organization
        other_trace = Trace(
            id=uuid.uuid4(),
            trace_id="other-trace-001",
            name="Other Trace",
            status="success",
            project_id=other_project.id,
        )
        db_session.add(other_trace)
        await db_session.commit()

        # Try to access other org's trace
        response = await client.get(
            f"/api/v1/traces/{other_trace.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_trace(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test deleting trace with organization scoping
        GIVEN: Trace in user's organization
        WHEN: DELETE /api/v1/traces/{trace_id}
        THEN: Deletes trace successfully
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="test-trace-delete",
            name="Test Trace",
            status="success",
            project_id=project.id,
        )
        db_session.add(trace)
        await db_session.commit()

        # Delete trace
        response = await client.delete(
            f"/api/v1/traces/{trace.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify trace is deleted
        get_response = await client.get(
            f"/api/v1/traces/{trace.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_trace_wrong_organization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test deleting trace from different organization
        GIVEN: Trace in different organization
        WHEN: DELETE /api/v1/traces/{trace_id}
        THEN: Returns 404
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create project in other organization
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=demo_user.id,
        )
        db_session.add(other_project)
        await db_session.flush()

        # Create trace in other organization
        other_trace = Trace(
            id=uuid.uuid4(),
            trace_id="other-trace-delete",
            name="Other Trace",
            status="success",
            project_id=other_project.id,
        )
        db_session.add(other_trace)
        await db_session.commit()

        # Try to delete other org's trace
        response = await client.delete(
            f"/api/v1/traces/{other_trace.id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_list_traces_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test accessing traces without authentication
        GIVEN: No authentication headers
        WHEN: GET /api/v1/traces
        THEN: Returns 403 Forbidden
        """
        response = await client.get("/api/v1/traces")
        assert response.status_code == 403
        assert "not authenticated" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_list_traces_organization_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test that users can only see traces from their organization
        GIVEN: Traces in multiple organizations
        WHEN: GET /api/v1/traces
        THEN: Returns only traces from user's organization
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create project in user's org
        user_project = Project(
            id=uuid.uuid4(),
            name="User Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        # Create project in other org
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=demo_user.id,
        )
        db_session.add_all([user_project, other_project])
        await db_session.flush()

        # Create trace in user's org
        user_trace = Trace(
            id=uuid.uuid4(),
            trace_id="user-trace-001",
            name="User Trace",
            status="success",
            project_id=user_project.id,
        )
        # Create trace in other org
        other_trace = Trace(
            id=uuid.uuid4(),
            trace_id="other-trace-001",
            name="Other Trace",
            status="success",
            project_id=other_project.id,
        )
        db_session.add_all([user_trace, other_trace])
        await db_session.commit()

        # List traces
        response = await client.get(
            "/api/v1/traces",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify only user's org traces returned
        trace_ids = [t["trace_id"] for t in data["traces"]]
        assert "user-trace-001" in trace_ids
        assert "other-trace-001" not in trace_ids

    @pytest.mark.asyncio
    async def test_list_traces_with_status_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering traces by status
        GIVEN: Traces with different statuses
        WHEN: GET /api/v1/traces?status_filter=error
        THEN: Returns only error traces
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create traces with different statuses
        success_trace = Trace(
            id=uuid.uuid4(),
            trace_id="success-trace",
            name="Success Trace",
            status="success",
            project_id=project.id,
        )
        error_trace = Trace(
            id=uuid.uuid4(),
            trace_id="error-trace",
            name="Error Trace",
            status="error",
            project_id=project.id,
            error_message="Test error",
        )
        db_session.add_all([success_trace, error_trace])
        await db_session.commit()

        # Filter by error status
        response = await client.get(
            "/api/v1/traces?status_filter=error",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify only error traces returned
        for trace in data["traces"]:
            assert trace["status"] == "error"

    @pytest.mark.asyncio
    async def test_get_trace_detail_with_evaluations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting comprehensive trace details with evaluations
        GIVEN: Trace with evaluations in user's organization
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns complete trace data with evaluation results
        """
        from app.models.evaluation_catalog import (
            EvaluationCatalog,
            TraceEvaluation,
            EvaluationSource,
            EvaluationType,
            EvaluationCategory,
        )

        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace with full details
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="detail-trace-001",
            name="Detail Test Trace",
            status="success",
            project_id=project.id,
            user_id=demo_user.id,
            model_name="GPT-4",
            provider="OpenAI",
            environment="production",
            input_data={"prompt": "Test prompt", "temperature": 0.7},
            output_data={"response": "Test response"},
            trace_metadata={"request_id": "req-123", "session_id": "sess-456"},
            total_duration_ms=250.5,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            total_cost=0.0025,
            retry_count=0,
        )
        db_session.add(trace)
        await db_session.flush()

        # Create evaluation catalog entry
        eval_catalog = EvaluationCatalog(
            id=uuid.uuid4(),
            name="Response Quality",
            description="Evaluates response quality",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.METRIC,
            organization_id=demo_user.organization_id,
            is_public=False,
        )
        db_session.add(eval_catalog)
        await db_session.flush()

        # Create trace evaluation
        trace_eval = TraceEvaluation(
            id=uuid.uuid4(),
            trace_id=trace.id,
            evaluation_catalog_id=eval_catalog.id,
            score=0.85,
            passed=None,
            category=None,
            reason="High quality response with good coherence",
            execution_time_ms=125.3,
            status="completed",
        )
        db_session.add(trace_eval)
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify trace data
        assert data["trace_id"] == "detail-trace-001"
        assert data["name"] == "Detail Test Trace"
        assert data["status"] == "success"
        assert data["project_name"] == "Test Project"
        assert data["model_name"] == "GPT-4"
        assert data["provider"] == "OpenAI"
        assert data["user_email"] == demo_user.email
        assert data["environment"] == "production"

        # Verify input/output data
        assert data["input_data"]["prompt"] == "Test prompt"
        assert data["output_data"]["response"] == "Test response"

        # Verify metadata
        assert data["trace_metadata"]["request_id"] == "req-123"

        # Verify performance metrics
        assert data["total_duration_ms"] == 250.5
        assert data["input_tokens"] == 100
        assert data["output_tokens"] == 50
        assert data["total_tokens"] == 150
        assert data["total_cost"] == 0.0025
        assert data["retry_count"] == 0

        # Verify evaluations
        assert "evaluations" in data
        assert len(data["evaluations"]) == 1
        eval_data = data["evaluations"][0]
        assert eval_data["evaluation_name"] == "Response Quality"
        assert eval_data["evaluation_source"] == "vendor"
        assert eval_data["evaluation_type"] == "metric"
        assert eval_data["category"] == "quality"
        assert eval_data["score"] == 0.85
        assert eval_data["reason"] == "High quality response with good coherence"
        assert eval_data["execution_time_ms"] == 125.3
        assert eval_data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_trace_detail_with_spans(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting trace details with multiple spans
        GIVEN: Trace with multiple spans
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns trace with ordered spans
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="spans-trace-001",
            name="Spans Test Trace",
            status="success",
            project_id=project.id,
            total_duration_ms=500.0,
        )
        db_session.add(trace)
        await db_session.flush()

        # Create spans with different start times
        span1 = Span(
            id=uuid.uuid4(),
            span_id="span-001",
            name="LLM Call",
            start_time=1000.0,
            end_time=1250.0,
            duration_ms=250.0,
            status="success",
            trace_id=trace.id,
            model_name="GPT-4",
            prompt_tokens=100,
            completion_tokens=50,
        )
        span2 = Span(
            id=uuid.uuid4(),
            span_id="span-002",
            name="Validation",
            start_time=1250.0,
            end_time=1350.0,
            duration_ms=100.0,
            status="success",
            trace_id=trace.id,
        )
        span3 = Span(
            id=uuid.uuid4(),
            span_id="span-003",
            name="Post-processing",
            start_time=1350.0,
            end_time=1500.0,
            duration_ms=150.0,
            status="success",
            trace_id=trace.id,
        )
        db_session.add_all([span1, span2, span3])
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify spans are present and ordered by start_time
        assert "spans" in data
        assert len(data["spans"]) == 3

        spans = data["spans"]
        assert spans[0]["span_id"] == "span-001"
        assert spans[0]["name"] == "LLM Call"
        assert spans[0]["duration_ms"] == 250.0
        assert spans[0]["prompt_tokens"] == 100
        assert spans[0]["completion_tokens"] == 50

        assert spans[1]["span_id"] == "span-002"
        assert spans[1]["name"] == "Validation"

        assert spans[2]["span_id"] == "span-003"
        assert spans[2]["name"] == "Post-processing"

        # Verify spans are ordered by start_time
        assert spans[0]["start_time"] < spans[1]["start_time"]
        assert spans[1]["start_time"] < spans[2]["start_time"]

    @pytest.mark.asyncio
    async def test_get_trace_detail_with_multiple_evaluation_types(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting trace details with different evaluation types
        GIVEN: Trace with metric, validator, and classifier evaluations
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns all evaluation types correctly
        """
        from app.models.evaluation_catalog import (
            EvaluationCatalog,
            TraceEvaluation,
            EvaluationSource,
            EvaluationType,
            EvaluationCategory,
        )

        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="eval-types-trace-001",
            name="Evaluation Types Test",
            status="success",
            project_id=project.id,
        )
        db_session.add(trace)
        await db_session.flush()

        # Create metric evaluation
        metric_catalog = EvaluationCatalog(
            id=uuid.uuid4(),
            name="Relevance Score",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.METRIC,
            organization_id=demo_user.organization_id,
        )
        metric_eval = TraceEvaluation(
            id=uuid.uuid4(),
            trace_id=trace.id,
            evaluation_catalog_id=metric_catalog.id,
            score=0.92,
            execution_time_ms=100.0,
            status="completed",
        )

        # Create validator evaluation
        validator_catalog = EvaluationCatalog(
            id=uuid.uuid4(),
            name="PII Check",
            category=EvaluationCategory.SECURITY,
            source=EvaluationSource.CUSTOM,
            evaluation_type=EvaluationType.VALIDATOR,
            organization_id=demo_user.organization_id,
        )
        validator_eval = TraceEvaluation(
            id=uuid.uuid4(),
            trace_id=trace.id,
            evaluation_catalog_id=validator_catalog.id,
            passed=True,
            reason="No PII detected in output",
            execution_time_ms=50.0,
            status="completed",
        )

        # Create classifier evaluation
        classifier_catalog = EvaluationCatalog(
            id=uuid.uuid4(),
            name="Sentiment Analysis",
            category=EvaluationCategory.CUSTOM,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.CLASSIFIER,
            organization_id=demo_user.organization_id,
        )
        classifier_eval = TraceEvaluation(
            id=uuid.uuid4(),
            trace_id=trace.id,
            evaluation_catalog_id=classifier_catalog.id,
            category="positive",
            reason="Response tone is positive and helpful",
            execution_time_ms=75.0,
            status="completed",
        )

        db_session.add_all([
            metric_catalog, metric_eval,
            validator_catalog, validator_eval,
            classifier_catalog, classifier_eval,
        ])
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify evaluations
        assert len(data["evaluations"]) == 3

        # Find each evaluation type
        metric_result = next(e for e in data["evaluations"] if e["evaluation_type"] == "metric")
        validator_result = next(e for e in data["evaluations"] if e["evaluation_type"] == "validator")
        classifier_result = next(e for e in data["evaluations"] if e["evaluation_type"] == "classifier")

        # Verify metric
        assert metric_result["evaluation_name"] == "Relevance Score"
        assert metric_result["score"] == 0.92
        assert metric_result["passed"] is None
        assert metric_result["category_result"] is None

        # Verify validator
        assert validator_result["evaluation_name"] == "PII Check"
        assert validator_result["passed"] is True
        assert validator_result["score"] is None
        assert validator_result["reason"] == "No PII detected in output"

        # Verify classifier
        assert classifier_result["evaluation_name"] == "Sentiment Analysis"
        assert classifier_result["category_result"] == "positive"
        assert classifier_result["score"] is None
        assert classifier_result["passed"] is None

    @pytest.mark.asyncio
    async def test_get_trace_detail_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test getting trace details for non-existent trace
        GIVEN: Non-existent trace ID
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns 404
        """
        non_existent_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/traces/{non_existent_id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_trace_detail_wrong_organization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test accessing trace details from different organization
        GIVEN: Trace in different organization
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns 404 (organization scoped)
        """
        # Create another organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Create project in other organization
        other_project = Project(
            id=uuid.uuid4(),
            name="Other Project",
            organization_id=other_org.id,
            created_by=demo_user.id,
        )
        db_session.add(other_project)
        await db_session.flush()

        # Create trace in other organization
        other_trace = Trace(
            id=uuid.uuid4(),
            trace_id="other-org-trace",
            name="Other Org Trace",
            status="success",
            project_id=other_project.id,
        )
        db_session.add(other_trace)
        await db_session.commit()

        # Try to access other org's trace detail
        response = await client.get(
            f"/api/v1/traces/{other_trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_trace_detail_with_error_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting trace details for failed trace with error information
        GIVEN: Trace with error status and error details
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns trace with error information
        """
        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace with error
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="error-trace-detail",
            name="Error Test Trace",
            status="error",
            project_id=project.id,
            error_type="RateLimitError",
            error_message="API rate limit exceeded. Please retry after 60 seconds.",
            retry_count=3,
            total_duration_ms=5000.0,
        )
        db_session.add(trace)
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify error information
        assert data["status"] == "error"
        assert data["error_type"] == "RateLimitError"
        assert data["error_message"] == "API rate limit exceeded. Please retry after 60 seconds."
        assert data["retry_count"] == 3
        assert data["total_duration_ms"] == 5000.0

    @pytest.mark.asyncio
    async def test_get_trace_detail_with_failed_evaluation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test getting trace details with failed evaluation
        GIVEN: Trace with evaluation that failed during execution
        WHEN: GET /api/v1/traces/{trace_id}/detail
        THEN: Returns trace with failed evaluation status
        """
        from app.models.evaluation_catalog import (
            EvaluationCatalog,
            TraceEvaluation,
            EvaluationSource,
            EvaluationType,
            EvaluationCategory,
        )

        # Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            organization_id=demo_user.organization_id,
            created_by=demo_user.id,
        )
        db_session.add(project)
        await db_session.flush()

        # Create trace
        trace = Trace(
            id=uuid.uuid4(),
            trace_id="failed-eval-trace",
            name="Failed Eval Test",
            status="success",
            project_id=project.id,
        )
        db_session.add(trace)
        await db_session.flush()

        # Create evaluation catalog
        eval_catalog = EvaluationCatalog(
            id=uuid.uuid4(),
            name="Toxicity Check",
            category=EvaluationCategory.SAFETY,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.VALIDATOR,
            organization_id=demo_user.organization_id,
        )
        db_session.add(eval_catalog)
        await db_session.flush()

        # Create failed evaluation
        failed_eval = TraceEvaluation(
            id=uuid.uuid4(),
            trace_id=trace.id,
            evaluation_catalog_id=eval_catalog.id,
            status="failed",
            error_message="API timeout while checking toxicity",
            execution_time_ms=10000.0,
        )
        db_session.add(failed_eval)
        await db_session.commit()

        # Test API
        response = await client.get(
            f"/api/v1/traces/{trace.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify failed evaluation
        assert len(data["evaluations"]) == 1
        eval_data = data["evaluations"][0]
        assert eval_data["evaluation_name"] == "Toxicity Check"
        assert eval_data["status"] == "failed"
        assert eval_data["score"] is None
        assert eval_data["passed"] is None
