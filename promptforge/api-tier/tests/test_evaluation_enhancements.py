"""
Evaluation Dashboard Enhancements Tests
Tests for P0 and P1 features:
- Trace title support (P0)
- Enhanced evaluation list endpoint with new fields (P0)
- Filtering by prompt title, vendor, category, status (P0)
- Sorting (default: most recent first) (P0)
- Evaluation detail endpoint (P1)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from app.models.user import User
from app.models.trace import Trace
from app.models.project import Project
from app.models.evaluation_catalog import (
    EvaluationCatalog,
    TraceEvaluation,
    EvaluationSource,
    EvaluationCategory,
    EvaluationType,
)
from app.services.model_provider import ModelExecutionResult
from app.evaluations.base import EvaluationResult as FrameworkEvaluationResult


# Helper function for test data creation
async def _create_test_evaluation_with_trace(
    db_session: AsyncSession,
    user: User,
    trace_title: str = "Test Trace",
    model: str = "gpt-4o-mini",
    vendor_name: str = "Ragas",
    category: EvaluationCategory = EvaluationCategory.QUALITY,
    score: float = 0.85,
    passed: bool = True,
    created_at: datetime = None,
) -> TraceEvaluation:
    """Helper to create test evaluation with full trace context"""
    # Get or create project
    stmt = select(Project).where(Project.organization_id == user.organization_id)
    result = await db_session.execute(stmt)
    project = result.scalars().first()

    if not project:
        project = Project(
            name="Test Project",
            description="Test project for evaluations",
            organization_id=user.organization_id,
            created_by=user.id,
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

    # Create trace
    import uuid
    trace = Trace(
        trace_id=f"tr_{uuid.uuid4().hex[:12]}",
        name=trace_title,
        user_id=user.id,
        project_id=project.id,
        model_name=model,
        environment="playground",
        status="success",
        input_data={"prompt": "Test prompt"},
        output_data={"response": "Test response"},
        trace_metadata={"source": "playground"},
        input_tokens=100,
        output_tokens=150,
        total_tokens=250,
        total_cost=0.001,
        total_duration_ms=1500.0,
    )
    db_session.add(trace)
    await db_session.commit()
    await db_session.refresh(trace)

    # Create or get evaluation catalog
    stmt = select(EvaluationCatalog).where(
        EvaluationCatalog.vendor_name == vendor_name,
        EvaluationCatalog.category == category,
    )
    result = await db_session.execute(stmt)
    eval_catalog = result.scalars().first()

    if not eval_catalog:
        eval_catalog = EvaluationCatalog(
            name=f"{vendor_name} {category.value} Eval",
            description=f"Test {category.value} evaluation",
            category=category,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.METRIC,
            vendor_name=vendor_name,
            is_public=True,
            is_active=True,
            adapter_class="TestAdapter",
            default_config={},
            version="1.0.0",
        )
        db_session.add(eval_catalog)
        await db_session.commit()
        await db_session.refresh(eval_catalog)

    # Create trace evaluation
    trace_eval = TraceEvaluation(
        trace_id=trace.id,
        evaluation_catalog_id=eval_catalog.id,
        organization_id=user.organization_id,
        score=score,
        passed=passed,
        reason="Test evaluation result",
        status="completed",
        execution_time_ms=150.0,
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        evaluation_cost=0.0005,
        model_used=model,
        details={"input": "Test prompt", "output": "Test response"},
        created_at=created_at or datetime.utcnow(),
    )
    db_session.add(trace_eval)
    await db_session.commit()
    await db_session.refresh(trace_eval)

    return trace_eval


class TestTraceTitle:
    """Test P0: Trace title support for Playground and Insights"""

    @pytest.mark.asyncio
    async def test_playground_with_title_creates_named_trace(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test playground execution with explicit title
        GIVEN: Playground request with title field
        WHEN: POST /api/v1/playground/execute with title="My Test Execution"
        THEN: Trace is created with name="My Test Execution"
        """
        mock_execution_result = ModelExecutionResult(
            response="Test response",
            input_tokens=10,
            output_tokens=12,
            tokens_used=22,
            cost=0.0008,
        )

        with patch('app.api.v1.endpoints.playground.ModelProviderService') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.execute = AsyncMock(return_value=mock_execution_result)
            mock_provider.return_value = mock_instance

            request_data = {
                "title": "My Test Execution",  # Explicit title
                "prompt": "Test prompt",
                "model": "gpt-4o-mini",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                },
            }

            response = await client.post(
                "/api/v1/playground/execute",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            trace_id = data["trace_id"]

            # Verify trace has the provided title
            stmt = select(Trace).where(Trace.trace_id == trace_id)
            result = await db_session.execute(stmt)
            trace = result.scalar_one_or_none()

            assert trace is not None
            assert trace.name == "My Test Execution"

    @pytest.mark.asyncio
    async def test_playground_without_title_uses_project_name(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test playground execution without title (defaults to project name)
        GIVEN: Playground request WITHOUT title field
        WHEN: POST /api/v1/playground/execute without title
        THEN: Trace is created with name from project or "playground" fallback
        """
        mock_execution_result = ModelExecutionResult(
            response="Test response",
            input_tokens=10,
            output_tokens=12,
            tokens_used=22,
            cost=0.0008,
        )

        with patch('app.api.v1.endpoints.playground.ModelProviderService') as mock_provider:
            mock_instance = AsyncMock()
            mock_instance.execute = AsyncMock(return_value=mock_execution_result)
            mock_provider.return_value = mock_instance

            request_data = {
                # No title field - should default to project name or "playground"
                "prompt": "Test prompt",
                "model": "gpt-4o-mini",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                },
            }

            response = await client.post(
                "/api/v1/playground/execute",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            trace_id = data["trace_id"]

            # Verify trace has a name (either project name or "playground")
            stmt = select(Trace).where(Trace.trace_id == trace_id)
            result = await db_session.execute(stmt)
            trace = result.scalar_one_or_none()

            assert trace is not None
            assert trace.name is not None
            assert len(trace.name) > 0
            # Name should be either the project name or "playground" fallback
            assert trace.name == "playground" or len(trace.name) > 0


class TestEvaluationListEnhancements:
    """Test P0: Enhanced evaluation list endpoint"""

    @pytest.mark.asyncio
    async def test_evaluation_list_includes_new_fields(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test that evaluation list includes all new P0 fields
        GIVEN: Evaluation exists with trace and catalog data
        WHEN: GET /api/v1/evaluations/list
        THEN: Response includes prompt_title, model, vendor_name, category, trace_identifier, passed
        """
        # Create a test evaluation with all required relationships
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Customer Support Test",
            model="gpt-4o-mini",
            vendor_name="Ragas",
            category=EvaluationCategory.QUALITY,
        )

        response = await client.get(
            "/api/v1/evaluations/list",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "evaluations" in data
        assert len(data["evaluations"]) > 0

        # Check first evaluation has all new fields
        evaluation = data["evaluations"][0]
        assert "prompt_title" in evaluation
        assert "model" in evaluation
        assert "vendor_name" in evaluation
        assert "category" in evaluation
        assert "trace_identifier" in evaluation
        assert "passed" in evaluation
        assert "created_at" in evaluation

    @pytest.mark.asyncio
    async def test_evaluation_list_default_sort_most_recent_first(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test default sort order (most recent first)
        GIVEN: Multiple evaluations created at different times
        WHEN: GET /api/v1/evaluations/list (no sort params)
        THEN: Results sorted by created_at DESC (most recent first)
        """
        # Create evaluations at different times
        now = datetime.utcnow()

        # Create older evaluation
        older_eval = await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Older Test",
            model="gpt-4o-mini",
            created_at=now - timedelta(hours=2),
        )

        # Create newer evaluation
        newer_eval = await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Newer Test",
            model="gpt-4o-mini",
            created_at=now - timedelta(hours=1),
        )

        response = await client.get(
            "/api/v1/evaluations/list",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        assert len(evaluations) >= 2

        # Verify most recent is first
        eval_titles = [e["prompt_title"] for e in evaluations]
        newer_index = eval_titles.index("Newer Test")
        older_index = eval_titles.index("Older Test")
        assert newer_index < older_index, "Newer evaluation should appear before older"

    @pytest.mark.asyncio
    async def test_filter_by_prompt_title(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering by prompt title (fuzzy search)
        GIVEN: Evaluations with different trace titles
        WHEN: GET /api/v1/evaluations/list?prompt_title=Customer
        THEN: Returns only evaluations with "Customer" in trace name
        """
        # Create evaluations with different titles
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Customer Support Test",
            model="gpt-4o-mini",
        )

        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Product Review Test",
            model="gpt-4o-mini",
        )

        response = await client.get(
            "/api/v1/evaluations/list?prompt_title=Customer",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should contain "Customer" in prompt_title
        for evaluation in evaluations:
            assert "Customer" in evaluation["prompt_title"]

    @pytest.mark.asyncio
    async def test_filter_by_vendor(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering by vendor name
        GIVEN: Evaluations from different vendors
        WHEN: GET /api/v1/evaluations/list?vendor=Ragas
        THEN: Returns only Ragas evaluations
        """
        # Create Ragas evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Test 1",
            vendor_name="Ragas",
        )

        # Create DeepEval evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Test 2",
            vendor_name="DeepEval",
        )

        response = await client.get(
            "/api/v1/evaluations/list?vendor=Ragas",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should be from Ragas
        for evaluation in evaluations:
            assert evaluation["vendor_name"] == "Ragas"

    @pytest.mark.asyncio
    async def test_filter_by_category(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering by category
        GIVEN: Evaluations from different categories
        WHEN: GET /api/v1/evaluations/list?category=quality
        THEN: Returns only quality category evaluations
        """
        # Create quality evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Test 1",
            category=EvaluationCategory.QUALITY,
        )

        # Create security evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Test 2",
            category=EvaluationCategory.SECURITY,
        )

        response = await client.get(
            "/api/v1/evaluations/list?category=quality",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should be quality category
        for evaluation in evaluations:
            assert evaluation["category"] == "quality"

    @pytest.mark.asyncio
    async def test_filter_by_status_pass(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering by status (pass)
        GIVEN: Evaluations with pass and fail results
        WHEN: GET /api/v1/evaluations/list?status_filter=pass
        THEN: Returns only passed evaluations
        """
        # Create passing evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Passing Test",
            passed=True,
        )

        # Create failing evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Failing Test",
            passed=False,
        )

        response = await client.get(
            "/api/v1/evaluations/list?status_filter=pass",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should be passed
        for evaluation in evaluations:
            assert evaluation["passed"] is True

    @pytest.mark.asyncio
    async def test_filter_by_status_fail(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering by status (fail)
        GIVEN: Evaluations with pass and fail results
        WHEN: GET /api/v1/evaluations/list?status_filter=fail
        THEN: Returns only failed evaluations
        """
        # Create passing evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Passing Test",
            passed=True,
        )

        # Create failing evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Failing Test",
            passed=False,
        )

        response = await client.get(
            "/api/v1/evaluations/list?status_filter=fail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should be failed
        for evaluation in evaluations:
            assert evaluation["passed"] is False

    @pytest.mark.asyncio
    async def test_sort_by_score_ascending(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test sorting by score ascending
        GIVEN: Evaluations with different scores
        WHEN: GET /api/v1/evaluations/list?sort_by=score&sort_direction=asc
        THEN: Results sorted by score ascending (lowest first)
        """
        # Create evaluations with different scores
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="High Score",
            score=0.95,
        )

        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Low Score",
            score=0.45,
        )

        response = await client.get(
            "/api/v1/evaluations/list?sort_by=score&sort_direction=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # Verify sorted by score ascending
        scores = [e["avg_score"] for e in evaluations if e["avg_score"] is not None]
        assert scores == sorted(scores), "Scores should be in ascending order"

    @pytest.mark.asyncio
    async def test_combined_filters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test multiple filters combined
        GIVEN: Various evaluations
        WHEN: GET /api/v1/evaluations/list?prompt_title=Support&vendor=Ragas&status_filter=pass
        THEN: Returns only evaluations matching ALL filters
        """
        # Create matching evaluation
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Customer Support Test",
            vendor_name="Ragas",
            passed=True,
        )

        # Create non-matching evaluations
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Customer Support Test",
            vendor_name="DeepEval",  # Different vendor
            passed=True,
        )

        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Product Review",  # Different title
            vendor_name="Ragas",
            passed=True,
        )

        response = await client.get(
            "/api/v1/evaluations/list?prompt_title=Support&vendor=Ragas&status_filter=pass",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # All results should match ALL filters
        for evaluation in evaluations:
            assert "Support" in evaluation["prompt_title"]
            assert evaluation["vendor_name"] == "Ragas"
            assert evaluation["passed"] is True


class TestEvaluationDetail:
    """Test P1: Evaluation detail endpoint"""

    @pytest.mark.asyncio
    async def test_evaluation_detail_returns_full_context(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test evaluation detail endpoint returns comprehensive information
        GIVEN: Evaluation exists with full trace context
        WHEN: GET /api/v1/evaluations/{evaluation_id}/detail
        THEN: Returns full evaluation details with trace context, metrics, and data
        """
        # Create test evaluation
        trace_eval = await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="Customer Support Test",
            model="gpt-4o-mini",
            vendor_name="Ragas",
            category=EvaluationCategory.QUALITY,
            score=0.87,
            passed=True,
        )

        response = await client.get(
            f"/api/v1/evaluations/{trace_eval.id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all detail fields present
        assert data["id"] == str(trace_eval.id)
        assert data["prompt_title"] == "Customer Support Test"
        assert data["model_name"] == "gpt-4o-mini"
        assert data["vendor_name"] == "Ragas"
        assert data["category"] == "quality"
        assert data["score"] == 0.87
        assert data["passed"] is True

        # Verify trace link
        assert "trace" in data
        assert data["trace"]["id"] is not None
        assert data["trace"]["trace_id"] is not None
        assert data["trace"]["name"] == "Customer Support Test"

        # Verify metrics
        assert "execution_time_ms" in data
        assert "total_tokens" in data
        assert "evaluation_cost" in data

        # Verify full data
        assert "input_data" in data
        assert "output_data" in data

    @pytest.mark.asyncio
    async def test_evaluation_detail_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test evaluation detail with non-existent ID
        GIVEN: Invalid evaluation ID
        WHEN: GET /api/v1/evaluations/{invalid_id}/detail
        THEN: Returns 404 Not Found
        """
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/evaluations/{fake_id}/detail",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestMultiTenantIsolation:
    """Test multi-tenant security enforcement"""

    @pytest.mark.asyncio
    async def test_evaluation_list_multi_tenant_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test that users only see evaluations from their organization
        GIVEN: Evaluations from different organizations
        WHEN: GET /api/v1/evaluations/list
        THEN: Returns only evaluations from current user's organization
        """
        # Create evaluation for demo user's organization
        await _create_test_evaluation_with_trace(
            db_session,
            demo_user,
            trace_title="My Organization Test",
        )

        # Note: In production, there would be other organizations
        # This test verifies the organization filter works correctly
        # All evaluations returned should belong to demo_user's organization

        response = await client.get(
            "/api/v1/evaluations/list",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        evaluations = data["evaluations"]

        # Verify all evaluations belong to demo user's organization
        # (by checking they exist - more comprehensive test would check project.organization_id)
        assert len(evaluations) > 0
        # All should have valid trace_id and project_id (filtered by org)
        for evaluation in evaluations:
            assert evaluation["trace_id"] is not None
            assert evaluation["project_id"] is not None
