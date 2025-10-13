"""
Insight Comparison API Integration Tests

Tests for:
- POST /api/v1/insights/comparisons
- GET /api/v1/insights/comparisons
- GET /api/v1/insights/comparisons/{id}
- DELETE /api/v1/insights/comparisons/{id}
"""

import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.call_insights import CallInsightsAnalysis
from app.services.model_provider import ModelExecutionResult


# Sample judge model response for Stage 1
MOCK_STAGE1_JUDGE_RESPONSE = {
    "scores_a": {
        "groundedness": 0.82,
        "faithfulness": 0.85,
        "completeness": 0.78,
        "clarity": 0.88,
        "accuracy": 0.80
    },
    "scores_b": {
        "groundedness": 0.95,
        "faithfulness": 0.93,
        "completeness": 0.90,
        "clarity": 0.89,
        "accuracy": 0.94
    },
    "winner": "B",
    "reasoning": "Model B extracted more comprehensive facts with higher accuracy. Specifically, Model B captured all key customer pain points mentioned in the conversation, while Model A missed the critical pricing concern."
}

# Sample judge model response for Stage 2
MOCK_STAGE2_JUDGE_RESPONSE = {
    "scores_a": {
        "groundedness": 0.80,
        "faithfulness": 0.85,
        "completeness": 0.78,
        "clarity": 0.90,
        "accuracy": 0.83
    },
    "scores_b": {
        "groundedness": 0.88,
        "faithfulness": 0.92,
        "completeness": 0.85,
        "clarity": 0.87,
        "accuracy": 0.89
    },
    "winner": "B",
    "reasoning": "Model B provided more grounded insights with better completeness. While Model A had slightly better clarity, Model B identified 3 critical insights that Model A missed."
}

# Sample judge model response for Stage 3
MOCK_STAGE3_JUDGE_RESPONSE = {
    "scores_a": {
        "groundedness": 0.87,
        "faithfulness": 0.90,
        "completeness": 0.82,
        "clarity": 0.93,
        "accuracy": 0.88
    },
    "scores_b": {
        "groundedness": 0.91,
        "faithfulness": 0.94,
        "completeness": 0.89,
        "clarity": 0.90,
        "accuracy": 0.92
    },
    "winner": "B",
    "reasoning": "Model B produced a more complete summary with higher groundedness. While Model A had slightly better clarity, Model B captured all 5 critical insights from Stage 2, whereas Model A omitted 2 key points."
}

# Sample overall verdict
MOCK_OVERALL_VERDICT_RESPONSE = {
    "overall_winner": "B",
    "reasoning": "Model B demonstrated superior performance across all three stages, winning Stage 1 (0.876 avg vs 0.840), Stage 2 (0.882 avg vs 0.792), and Stage 3 (0.912 avg vs 0.880). Despite being 14x more expensive ($0.0180 vs $0.0012), Model B's superior insight generation (+11.4% in Stage 2) provides significantly more business value. Recommendation: Use Model B for production.",
    "quality_improvement": "+5.2%",
    "cost_impact": "+$0.0168 per analysis",
    "recommendation": "Use Model B for production - superior insights justify 14x higher cost"
}


@pytest.fixture
async def test_project(db_session: AsyncSession, demo_user: User) -> Project:
    """Create a test project"""
    project = Project(
        id=uuid.uuid4(),
        organization_id=demo_user.organization_id,
        name="Test Comparison Project",
        description="Project for testing insight comparisons",
        created_by=str(demo_user.id),
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
async def analysis_a(db_session: AsyncSession, demo_user: User, test_project: Project) -> CallInsightsAnalysis:
    """Create first test analysis (gpt-4o-mini)"""
    from app.models.trace import Trace

    # Create parent trace for analysis A
    trace_a = Trace(
        id=uuid.uuid4(),
        trace_id=str(uuid.uuid4()),
        name="Test Analysis A",
        status="success",
        project_id=test_project.id,
        user_id=demo_user.id,
        model_name="gpt-4o-mini",
        input_data={"prompt": "Test transcript A"},
        output_data={"response": "Test response A"},
        trace_metadata={},
        total_duration_ms=1000.0,
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        total_cost=0.0012,
        environment="test",
    )
    db_session.add(trace_a)
    await db_session.flush()

    analysis = CallInsightsAnalysis(
        id=uuid.uuid4(),
        organization_id=demo_user.organization_id,
        user_id=demo_user.id,
        project_id=test_project.id,
        transcript_title="Customer Call - Q3 2025 (Model A)",
        transcript_input="Agent: Hello, how can I help you today? Customer: I need help with my account.",
        facts_output="Facts from Model A: Customer requested account assistance.",
        insights_output="Insights from Model A: Customer needs account support.",
        summary_output="Summary from Model A: Account support requested.",
        pii_redacted=False,
        stage_params={},
        model_stage1="gpt-4o-mini",
        model_stage2="gpt-4o-mini",
        model_stage3="gpt-4o-mini",
        parent_trace_id=trace_a.id,
        total_tokens=150,
        total_cost=0.0012,
        analysis_metadata={},
    )
    db_session.add(analysis)
    await db_session.commit()
    await db_session.refresh(analysis)
    return analysis


@pytest.fixture
async def analysis_b(db_session: AsyncSession, demo_user: User, test_project: Project, analysis_a: CallInsightsAnalysis) -> CallInsightsAnalysis:
    """Create second test analysis (gpt-4o) with SAME transcript as analysis_a"""
    from app.models.trace import Trace

    # Create parent trace for analysis B
    trace_b = Trace(
        id=uuid.uuid4(),
        trace_id=str(uuid.uuid4()),
        name="Test Analysis B",
        status="success",
        project_id=test_project.id,
        user_id=demo_user.id,
        model_name="gpt-4o",
        input_data={"prompt": "Test transcript B"},
        output_data={"response": "Test response B"},
        trace_metadata={},
        total_duration_ms=1200.0,
        input_tokens=110,
        output_tokens=55,
        total_tokens=165,
        total_cost=0.0180,
        environment="test",
    )
    db_session.add(trace_b)
    await db_session.flush()

    analysis = CallInsightsAnalysis(
        id=uuid.uuid4(),
        organization_id=demo_user.organization_id,
        user_id=demo_user.id,
        project_id=test_project.id,
        transcript_title="Customer Call - Q3 2025 (Model B)",
        transcript_input=analysis_a.transcript_input,  # SAME transcript as A
        facts_output="Facts from Model B: Customer requested comprehensive account assistance with detailed requirements.",
        insights_output="Insights from Model B: Customer needs comprehensive account support with multiple touchpoints.",
        summary_output="Summary from Model B: Comprehensive account support requested with detailed follow-up.",
        pii_redacted=False,
        stage_params={},
        model_stage1="gpt-4o",
        model_stage2="gpt-4o",
        model_stage3="gpt-4o",
        parent_trace_id=trace_b.id,
        total_tokens=165,
        total_cost=0.0180,
        analysis_metadata={},
    )
    db_session.add(analysis)
    await db_session.commit()
    await db_session.refresh(analysis)
    return analysis


def mock_judge_execute_side_effect(request):
    """Mock judge model execution with proper JSON responses"""
    prompt = request.messages[0]["content"]

    # Determine which stage based on prompt content
    # Check for overall verdict FIRST (it contains references to all stages)
    if ("FINAL VERDICT" in prompt
        or ("stage1_winner" in prompt.lower() and "stage2_winner" in prompt.lower() and "stage3_winner" in prompt.lower())
        or "cost-benefit analysis" in prompt.lower()):
        response_dict = MOCK_OVERALL_VERDICT_RESPONSE
        tokens = 800
        stage_name = "Overall Verdict"
    elif "Stage 1: Fact Extraction" in prompt or "STAGE 1" in prompt or ("fact extraction" in prompt.lower() and "stage 2" not in prompt.lower()):
        response_dict = MOCK_STAGE1_JUDGE_RESPONSE
        tokens = 500
        stage_name = "Stage 1"
    elif "Stage 2: Reasoning" in prompt or "STAGE 2" in prompt or ("reasoning and insights" in prompt.lower() and "stage 3" not in prompt.lower()):
        response_dict = MOCK_STAGE2_JUDGE_RESPONSE
        tokens = 550
        stage_name = "Stage 2"
    elif "Stage 3: Summary" in prompt or "STAGE 3" in prompt or "summary" in prompt.lower():
        response_dict = MOCK_STAGE3_JUDGE_RESPONSE
        tokens = 500
        stage_name = "Stage 3"
    else:
        # Default response (shouldn't happen) - use Stage 1 but mark it
        response_dict = MOCK_STAGE1_JUDGE_RESPONSE
        tokens = 500
        stage_name = "DEFAULT (unmatched prompt)"
        print(f"\n!!! UNMATCHED PROMPT !!!")
        print(f"Prompt snippet: {prompt[:200]}...")

    print(f"\n=== Mock returning {stage_name} ===")
    response_json = json.dumps(response_dict)

    return ModelExecutionResult(
        response=response_json,
        input_tokens=tokens,
        output_tokens=200,
        tokens_used=tokens + 200,
        cost=0.002,
        provider_duration_ms=1000.0,
        total_duration_ms=1500.0,
    )


class TestInsightComparisonCreate:
    """Test creating insight comparisons"""

    @pytest.mark.asyncio
    async def test_create_comparison_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test successful comparison creation
        GIVEN: Two analyses with same transcript
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns 201 with complete comparison results
        """
        # Create a mock ModelProviderService instance with execute method
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            request_data = {
                "analysis_a_id": str(analysis_a.id),
                "analysis_b_id": str(analysis_b.id),
                "judge_model": "claude-sonnet-4.5",
                "evaluation_criteria": ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"],
            }

            response = await client.post(
                "/api/v1/insights/comparisons",
                json=request_data,
                headers=auth_headers,
            )

            if response.status_code != 201:
                print(f"\n=== ERROR RESPONSE ===")
                print(f"Status: {response.status_code}")
                print(f"Response text: {response.text}")
                print(f"Mock execute called: {mock_model_service.execute.called}")
                print(f"Mock execute call count: {mock_model_service.execute.call_count}")

            assert response.status_code == 201
            data = response.json()

            # Validate response structure
            assert "id" in data
            assert "organization_id" in data
            assert "user_id" in data
            assert "analysis_a" in data
            assert "analysis_b" in data
            assert "judge_model" in data
            assert "evaluation_criteria" in data
            assert "overall_winner" in data
            assert "overall_reasoning" in data
            assert "stage_results" in data
            assert "judge_trace" in data
            assert "created_at" in data

            # Validate overall winner
            assert data["overall_winner"] == "B"
            assert "superior performance" in data["overall_reasoning"].lower()

            # Validate stage results
            assert len(data["stage_results"]) == 3
            stage_names = [stage["stage"] for stage in data["stage_results"]]
            assert "Stage 1: Fact Extraction" in stage_names
            assert "Stage 2: Reasoning & Insights" in stage_names
            assert "Stage 3: Summary" in stage_names

            # Validate each stage has required fields
            for stage in data["stage_results"]:
                assert "stage" in stage
                assert "winner" in stage
                assert "scores" in stage
                assert "reasoning" in stage
                assert "A" in stage["scores"]
                assert "B" in stage["scores"]

                # Validate scores structure
                for model_scores in [stage["scores"]["A"], stage["scores"]["B"]]:
                    assert "groundedness" in model_scores
                    assert "faithfulness" in model_scores
                    assert "completeness" in model_scores
                    assert "clarity" in model_scores
                    assert "accuracy" in model_scores

            # Validate judge trace metadata
            assert "trace_id" in data["judge_trace"]
            assert data["judge_trace"]["model"] == "claude-sonnet-4.5"
            assert data["judge_trace"]["total_tokens"] > 0
            assert data["judge_trace"]["cost"] > 0
            assert data["judge_trace"]["duration_ms"] > 0

            # Validate analysis summaries
            assert data["analysis_a"]["id"] == str(analysis_a.id)
            assert data["analysis_a"]["model_stage1"] == "gpt-4o-mini"
            assert data["analysis_a"]["total_cost"] == 0.0012

            assert data["analysis_b"]["id"] == str(analysis_b.id)
            assert data["analysis_b"]["model_stage1"] == "gpt-4o"
            assert data["analysis_b"]["total_cost"] == 0.0180

            # Validate judge model was called 4 times (3 stages + overall)
            assert mock_model_service.execute.call_count == 4

    @pytest.mark.asyncio
    async def test_create_comparison_duplicate(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test duplicate comparison detection
        GIVEN: Existing comparison for same analyses with same judge
        WHEN: POST /api/v1/insights/comparisons (second time)
        THEN: Returns 409 Conflict
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            request_data = {
                "analysis_a_id": str(analysis_a.id),
                "analysis_b_id": str(analysis_b.id),
                "judge_model": "claude-sonnet-4.5",
            }

            # Create first comparison (should succeed)
            response1 = await client.post(
                "/api/v1/insights/comparisons",
                json=request_data,
                headers=auth_headers,
            )
            assert response1.status_code == 201

            # Try to create duplicate (should fail)
            response2 = await client.post(
                "/api/v1/insights/comparisons",
                json=request_data,
                headers=auth_headers,
            )
            assert response2.status_code == 409
            data = response2.json()
            assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_comparison_analysis_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
    ):
        """
        Test comparison with non-existent analysis
        GIVEN: One valid analysis, one random UUID
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns 404 Not Found
        """
        random_id = str(uuid.uuid4())
        request_data = {
            "analysis_a_id": str(analysis_a.id),
            "analysis_b_id": random_id,
            "judge_model": "claude-sonnet-4.5",
        }

        response = await client.post(
            "/api/v1/insights/comparisons",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires multi-organization test setup - covered by service layer validation")
    async def test_create_comparison_different_organizations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        analysis_a: CallInsightsAnalysis,
        test_project: Project,
        db_session: AsyncSession,
    ):
        """
        Test comparison across different organizations (should fail)
        GIVEN: Two analyses from different organizations
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns 403 Forbidden
        """
        # Create analysis in different organization
        other_org_id = uuid.uuid4()
        from app.models.trace import Trace

        trace_other = Trace(
            id=uuid.uuid4(),
            trace_id=str(uuid.uuid4()),
            name="Other Org Analysis",
            status="success",
            project_id=test_project.id,  # Use test project (traces require project_id)
            user_id=demo_user.id,
            model_name="gpt-4o",
            input_data={"prompt": "Test"},
            output_data={"response": "Test"},
            trace_metadata={},
            total_duration_ms=1000.0,
            total_tokens=100,
            total_cost=0.001,
            environment="test",
        )
        db_session.add(trace_other)
        await db_session.flush()

        analysis_other_org = CallInsightsAnalysis(
            id=uuid.uuid4(),
            organization_id=other_org_id,  # Different organization
            user_id=demo_user.id,
            project_id=test_project.id,  # Analyses also require project_id
            transcript_title="Other Org Analysis",
            transcript_input=analysis_a.transcript_input,
            facts_output="Facts",
            insights_output="Insights",
            summary_output="Summary",
            pii_redacted=False,
            model_stage1="gpt-4o",
            model_stage2="gpt-4o",
            model_stage3="gpt-4o",
            parent_trace_id=trace_other.id,
            total_tokens=100,
            total_cost=0.001,
        )
        db_session.add(analysis_other_org)
        await db_session.commit()
        await db_session.refresh(analysis_other_org)

        request_data = {
            "analysis_a_id": str(analysis_a.id),
            "analysis_b_id": str(analysis_other_org.id),
            "judge_model": "claude-sonnet-4.5",
        }

        response = await client.post(
            "/api/v1/insights/comparisons",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert "different organizations" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_comparison_different_transcripts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        analysis_a: CallInsightsAnalysis,
        test_project: Project,
        db_session: AsyncSession,
    ):
        """
        Test comparison with different transcripts (should fail)
        GIVEN: Two analyses with different transcripts
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns 422 Unprocessable Entity
        """
        # Create analysis with different transcript
        from app.models.trace import Trace

        trace_diff = Trace(
            id=uuid.uuid4(),
            trace_id=str(uuid.uuid4()),
            name="Different Transcript Analysis",
            status="success",
            project_id=test_project.id,
            user_id=demo_user.id,
            model_name="gpt-4o",
            input_data={"prompt": "Different transcript"},
            output_data={"response": "Test"},
            trace_metadata={},
            total_duration_ms=1000.0,
            total_tokens=100,
            total_cost=0.001,
            environment="test",
        )
        db_session.add(trace_diff)
        await db_session.flush()

        analysis_diff_transcript = CallInsightsAnalysis(
            id=uuid.uuid4(),
            organization_id=demo_user.organization_id,
            user_id=demo_user.id,
            project_id=test_project.id,
            transcript_title="Different Transcript",
            transcript_input="Completely different transcript content here.",  # Different
            facts_output="Facts",
            insights_output="Insights",
            summary_output="Summary",
            pii_redacted=False,
            model_stage1="gpt-4o",
            model_stage2="gpt-4o",
            model_stage3="gpt-4o",
            parent_trace_id=trace_diff.id,
            total_tokens=100,
            total_cost=0.001,
        )
        db_session.add(analysis_diff_transcript)
        await db_session.commit()
        await db_session.refresh(analysis_diff_transcript)

        request_data = {
            "analysis_a_id": str(analysis_a.id),
            "analysis_b_id": str(analysis_diff_transcript.id),
            "judge_model": "claude-sonnet-4.5",
        }

        response = await client.post(
            "/api/v1/insights/comparisons",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "different transcripts" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_comparison_unauthenticated(
        self,
        client: AsyncClient,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test comparison without authentication
        GIVEN: No auth token
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns 403 Forbidden
        """
        request_data = {
            "analysis_a_id": str(analysis_a.id),
            "analysis_b_id": str(analysis_b.id),
        }

        response = await client.post(
            "/api/v1/insights/comparisons",
            json=request_data,
        )

        assert response.status_code == 403


class TestInsightComparisonList:
    """Test listing insight comparisons"""

    @pytest.mark.asyncio
    async def test_list_comparisons_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test listing when no comparisons exist
        GIVEN: No existing comparisons
        WHEN: GET /api/v1/insights/comparisons
        THEN: Returns 200 with empty list
        """
        response = await client.get(
            "/api/v1/insights/comparisons",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "comparisons" in data
        assert "pagination" in data
        assert len(data["comparisons"]) == 0

    @pytest.mark.asyncio
    async def test_list_comparisons_with_results(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test listing with existing comparisons
        GIVEN: Multiple comparisons exist
        WHEN: GET /api/v1/insights/comparisons
        THEN: Returns 200 with list of comparisons
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            # Create comparison
            request_data = {
                "analysis_a_id": str(analysis_a.id),
                "analysis_b_id": str(analysis_b.id),
                "judge_model": "claude-sonnet-4.5",
            }

            create_response = await client.post(
                "/api/v1/insights/comparisons",
                json=request_data,
                headers=auth_headers,
            )
            assert create_response.status_code == 201

        # List comparisons
        response = await client.get(
            "/api/v1/insights/comparisons",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["comparisons"]) == 1

        # Validate list item structure
        item = data["comparisons"][0]
        assert "id" in item
        assert "analysis_a_title" in item
        assert "analysis_b_title" in item
        assert "model_a_summary" in item
        assert "model_b_summary" in item
        assert "judge_model" in item
        assert "overall_winner" in item
        assert "cost_difference" in item
        assert "quality_improvement" in item
        assert "created_at" in item

        # Validate pagination
        assert "page" in data["pagination"]
        assert "page_size" in data["pagination"]
        assert "total_count" in data["pagination"]
        assert "total_pages" in data["pagination"]
        assert data["pagination"]["total_count"] == 1

    @pytest.mark.asyncio
    async def test_list_comparisons_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test pagination in comparison list
        GIVEN: Single comparison
        WHEN: GET /api/v1/insights/comparisons?skip=0&limit=10
        THEN: Returns correct pagination metadata
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            # Create comparison
            await client.post(
                "/api/v1/insights/comparisons",
                json={
                    "analysis_a_id": str(analysis_a.id),
                    "analysis_b_id": str(analysis_b.id),
                },
                headers=auth_headers,
            )

        response = await client.get(
            "/api/v1/insights/comparisons?skip=0&limit=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total_count"] == 1
        assert data["pagination"]["total_pages"] == 1

    @pytest.mark.asyncio
    async def test_list_comparisons_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test listing without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/insights/comparisons
        THEN: Returns 403 Forbidden
        """
        response = await client.get("/api/v1/insights/comparisons")
        assert response.status_code == 403


class TestInsightComparisonGet:
    """Test getting specific comparison"""

    @pytest.mark.asyncio
    async def test_get_comparison_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test retrieving specific comparison by ID
        GIVEN: Existing comparison
        WHEN: GET /api/v1/insights/comparisons/{id}
        THEN: Returns 200 with full comparison details
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            # Create comparison
            create_response = await client.post(
                "/api/v1/insights/comparisons",
                json={
                    "analysis_a_id": str(analysis_a.id),
                    "analysis_b_id": str(analysis_b.id),
                },
                headers=auth_headers,
            )
            comparison_id = create_response.json()["id"]

        # Get comparison by ID
        response = await client.get(
            f"/api/v1/insights/comparisons/{comparison_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Validate complete structure
        assert data["id"] == comparison_id
        assert "overall_winner" in data
        assert "overall_reasoning" in data
        assert "stage_results" in data
        assert len(data["stage_results"]) == 3
        assert "judge_trace" in data
        assert "analysis_a" in data
        assert "analysis_b" in data

    @pytest.mark.asyncio
    async def test_get_comparison_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test retrieving non-existent comparison
        GIVEN: Random UUID that doesn't exist
        WHEN: GET /api/v1/insights/comparisons/{random_uuid}
        THEN: Returns 404 Not Found
        """
        random_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/v1/insights/comparisons/{random_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_comparison_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test retrieving comparison without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/insights/comparisons/{id}
        THEN: Returns 403 Forbidden
        """
        random_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/insights/comparisons/{random_id}")
        assert response.status_code == 403


class TestInsightComparisonDelete:
    """Test deleting comparisons"""

    @pytest.mark.asyncio
    async def test_delete_comparison_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test successful comparison deletion
        GIVEN: Existing comparison
        WHEN: DELETE /api/v1/insights/comparisons/{id}
        THEN: Returns 204 No Content
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            # Create comparison
            create_response = await client.post(
                "/api/v1/insights/comparisons",
                json={
                    "analysis_a_id": str(analysis_a.id),
                    "analysis_b_id": str(analysis_b.id),
                },
                headers=auth_headers,
            )
            comparison_id = create_response.json()["id"]

        # Delete comparison
        response = await client.delete(
            f"/api/v1/insights/comparisons/{comparison_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion - get should return 404
        get_response = await client.get(
            f"/api/v1/insights/comparisons/{comparison_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_comparison_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test deleting non-existent comparison
        GIVEN: Random UUID that doesn't exist
        WHEN: DELETE /api/v1/insights/comparisons/{random_uuid}
        THEN: Returns 404 Not Found
        """
        random_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/v1/insights/comparisons/{random_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_comparison_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test deleting comparison without authentication
        GIVEN: No auth token
        WHEN: DELETE /api/v1/insights/comparisons/{id}
        THEN: Returns 403 Forbidden
        """
        random_id = str(uuid.uuid4())
        response = await client.delete(f"/api/v1/insights/comparisons/{random_id}")
        assert response.status_code == 403


class TestInsightComparisonJudgeModel:
    """Test judge model integration"""

    @pytest.mark.asyncio
    async def test_judge_model_invocation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test that judge model is invoked correctly
        GIVEN: Two analyses to compare
        WHEN: POST /api/v1/insights/comparisons
        THEN: Judge model is called 4 times (3 stages + overall)
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            request_data = {
                "analysis_a_id": str(analysis_a.id),
                "analysis_b_id": str(analysis_b.id),
                "judge_model": "claude-sonnet-4.5",
            }

            response = await client.post(
                "/api/v1/insights/comparisons",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 201

            # Verify judge model was called 4 times
            assert mock_model_service.execute.call_count == 4

            # Verify all calls used judge model with temperature=0.0
            for call in mock_model_service.execute.call_args_list:
                request = call[0][0]  # First positional argument
                assert request.model == "claude-sonnet-4.5"
                assert request.temperature == 0.0

    @pytest.mark.asyncio
    async def test_per_stage_evaluation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        analysis_a: CallInsightsAnalysis,
        analysis_b: CallInsightsAnalysis,
    ):
        """
        Test that each stage is evaluated independently
        GIVEN: Two analyses to compare
        WHEN: POST /api/v1/insights/comparisons
        THEN: Returns separate scores and winners for each stage
        """
        mock_model_service = AsyncMock()
        mock_model_service.execute = AsyncMock(side_effect=mock_judge_execute_side_effect)

        with patch('app.services.insight_comparison_service.ModelProviderService', return_value=mock_model_service):
            response = await client.post(
                "/api/v1/insights/comparisons",
                json={
                    "analysis_a_id": str(analysis_a.id),
                    "analysis_b_id": str(analysis_b.id),
                },
                headers=auth_headers,
            )

            assert response.status_code == 201
            data = response.json()

            # Verify each stage has independent evaluation
            stage1 = next(s for s in data["stage_results"] if "Fact Extraction" in s["stage"])
            stage2 = next(s for s in data["stage_results"] if "Reasoning" in s["stage"])
            stage3 = next(s for s in data["stage_results"] if "Summary" in s["stage"])

            # All stages should have winner B (based on mock data)
            assert stage1["winner"] == "B"
            assert stage2["winner"] == "B"
            assert stage3["winner"] == "B"

            # Verify scores are different for each stage
            assert stage1["scores"]["A"]["groundedness"] == 0.82
            assert stage2["scores"]["A"]["groundedness"] == 0.80
            assert stage3["scores"]["A"]["groundedness"] == 0.87
