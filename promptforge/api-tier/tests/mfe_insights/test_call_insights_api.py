"""
Call Insights API Integration Tests

Tests for:
- POST /api/v1/call-insights/analyze
- GET /api/v1/call-insights/history
- GET /api/v1/call-insights/{analysis_id}
"""

import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.evaluation_catalog import EvaluationCatalog
from app.services.model_provider import ModelExecutionResult


# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
Agent: Thank you for calling TechSupport Inc. My name is Sarah. How can I help you today?

Customer: Hi Sarah, I'm having issues with my laptop. It won't turn on at all.

Agent: I understand that must be frustrating. Let me help you troubleshoot this. First, can you tell me if the power indicator light comes on when you press the power button?

Customer: No, there's no light at all. I've tried plugging it in but nothing happens.

Agent: Okay, let's try a few things. First, can you try a different power outlet to make sure it's not an outlet issue?

Customer: Sure, let me try... okay I moved to a different outlet but still nothing.

Agent: Alright. Now let's try removing the battery if possible, then holding the power button for 30 seconds to discharge any residual power.

Customer: Okay I removed it and held the button... now what?

Agent: Put the battery back in, plug in the charger, and try turning it on again.

Customer: Oh wow, it's turning on now! I see the startup screen.

Agent: Excellent! The issue was likely residual charge preventing it from powering on. This is a common issue. Is there anything else I can help you with today?

Customer: No that's perfect, thank you so much!

Agent: You're very welcome! Have a great day.
"""


@pytest.fixture
async def test_project(db_session: AsyncSession, demo_user: User) -> Project:
    """Create a test project"""
    project = Project(
        id=uuid.uuid4(),
        organization_id=demo_user.organization_id,
        name="Test Call Analytics Project",
        description="Project for testing call insights",
        created_by=str(demo_user.id),
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
async def test_evaluation(db_session: AsyncSession, demo_user: User) -> EvaluationCatalog:
    """Create a test evaluation in catalog"""
    evaluation = EvaluationCatalog(
        id=uuid.uuid4(),
        organization_id=demo_user.organization_id,
        name="Answer Relevance",
        description="Measures how relevant the answer is to the question",
        category="Quality",
        source="ragas",
        adapter_class="RagasAdapter",
        adapter_evaluation_id="answer_relevancy",
        is_active=True,
        is_public=True,
        default_config={"threshold": 0.7},
    )
    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)
    return evaluation


class TestCallInsightsAnalyze:
    """Test call insights analysis endpoint"""

    @pytest.mark.asyncio
    async def test_analyze_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        test_project: Project,
    ):
        """
        Test successful call transcript analysis
        GIVEN: Valid transcript with authentication
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns 200 with summary, insights, facts, and traces
        """
        # Mock the model provider execution
        mock_result = ModelExecutionResult(
            response="Mocked LLM response for testing",
            tokens_used=150,
            cost=0.003,
            input_tokens=100,
            output_tokens=50,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "transcript_title": "Laptop Power Issue Resolution",
                "project_id": str(test_project.id),
                "enable_pii_redaction": False,
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            assert "analysis_id" in data
            assert "summary" in data
            assert "insights" in data
            assert "facts" in data
            assert "pii_redacted" in data
            assert "traces" in data
            assert "evaluations" in data
            assert "total_tokens" in data
            assert "total_cost" in data
            assert "created_at" in data

            # Validate data types
            assert isinstance(data["analysis_id"], str)
            assert isinstance(data["summary"], str)
            assert isinstance(data["insights"], str)
            assert isinstance(data["facts"], str)
            assert data["pii_redacted"] is False
            assert isinstance(data["traces"], list)
            assert isinstance(data["evaluations"], list)
            assert isinstance(data["total_tokens"], int)
            assert isinstance(data["total_cost"], float)

            # Should have 3 traces (one for each stage)
            assert len(data["traces"]) == 3

            # Validate trace structure
            for trace in data["traces"]:
                assert "trace_id" in trace
                assert "stage" in trace
                assert "model" in trace
                assert "temperature" in trace
                assert "top_p" in trace
                assert "max_tokens" in trace
                assert "input_tokens" in trace
                assert "output_tokens" in trace
                assert "total_tokens" in trace
                assert "duration_ms" in trace
                assert "cost" in trace

            # Validate stage names
            stage_names = [trace["stage"] for trace in data["traces"]]
            assert "Stage 1: Fact Extraction" in stage_names
            assert "Stage 2: Reasoning & Insights" in stage_names
            assert "Stage 3: Summary Synthesis" in stage_names

            # Validate DTA parameters (new defaults)
            fact_trace = next(t for t in data["traces"] if "Fact Extraction" in t["stage"])
            reasoning_trace = next(t for t in data["traces"] if "Reasoning" in t["stage"])
            summary_trace = next(t for t in data["traces"] if "Summary" in t["stage"])

            assert fact_trace["temperature"] == 0.25
            assert fact_trace["top_p"] == 0.95
            assert reasoning_trace["temperature"] == 0.65
            assert reasoning_trace["top_p"] == 0.95
            assert summary_trace["temperature"] == 0.45
            assert summary_trace["top_p"] == 0.95

    @pytest.mark.asyncio
    async def test_analyze_with_custom_parameters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
    ):
        """
        Test analysis with custom stage parameters
        GIVEN: Valid transcript with custom DTA parameters
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Uses custom parameters for each stage
        """
        mock_result = ModelExecutionResult(
            response="Mocked response",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "transcript_title": "Custom Parameters Test",
                "stage_params": {
                    "fact_extraction": {
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "max_tokens": 500,
                    },
                    "reasoning": {
                        "temperature": 0.5,
                        "top_p": 0.85,
                        "max_tokens": 1000,
                    },
                    "summary": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "max_tokens": 600,
                    },
                },
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Validate custom parameters were used
            fact_trace = next(t for t in data["traces"] if "Fact Extraction" in t["stage"])
            reasoning_trace = next(t for t in data["traces"] if "Reasoning" in t["stage"])
            summary_trace = next(t for t in data["traces"] if "Summary" in t["stage"])

            assert fact_trace["temperature"] == 0.1
            assert fact_trace["top_p"] == 0.8
            assert fact_trace["max_tokens"] == 500

            assert reasoning_trace["temperature"] == 0.5
            assert reasoning_trace["top_p"] == 0.85
            assert reasoning_trace["max_tokens"] == 1000

            assert summary_trace["temperature"] == 0.3
            assert summary_trace["top_p"] == 0.9
            assert summary_trace["max_tokens"] == 600

    @pytest.mark.asyncio
    async def test_analyze_with_pii_redaction(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test analysis with PII redaction enabled
        GIVEN: Transcript with enable_pii_redaction=True
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns pii_redacted=True in response
        """
        mock_result = ModelExecutionResult(
            response="Redacted response",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "enable_pii_redaction": True,
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["pii_redacted"] is True

    @pytest.mark.asyncio
    async def test_analyze_with_custom_system_prompts_and_models(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test analysis with custom system prompts and model selection
        GIVEN: Valid transcript with custom system prompts and models for each stage
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Uses custom prompts/models and stores them in database
        """
        mock_result = ModelExecutionResult(
            response="Mocked response with custom prompt",
            tokens_used=120,
            cost=0.0025,
            input_tokens=80,
            output_tokens=40,
            model="gpt-4o-mini",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            custom_prompt_stage1 = "You are a precise fact extraction specialist."
            custom_prompt_stage2 = "You are a strategic business analyst."
            custom_prompt_stage3 = "You are a concise executive summary writer."

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "transcript_title": "Custom Prompts and Models Test",
                "system_prompts": {
                    "stage1_fact_extraction": custom_prompt_stage1,
                    "stage2_reasoning": custom_prompt_stage2,
                    "stage3_summary": custom_prompt_stage3,
                },
                "models": {
                    "stage1_model": "gpt-4o-mini",
                    "stage2_model": "gpt-4o",
                    "stage3_model": "gpt-4o-mini",
                },
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            assert "analysis_id" in data
            analysis_id = data["analysis_id"]

            # Validate traces use correct models
            assert len(data["traces"]) == 3
            fact_trace = next(t for t in data["traces"] if "Fact Extraction" in t["stage"])
            reasoning_trace = next(t for t in data["traces"] if "Reasoning" in t["stage"])
            summary_trace = next(t for t in data["traces"] if "Summary" in t["stage"])

            # Debug: Print trace keys
            print(f"\n[DEBUG] Fact trace keys: {fact_trace.keys()}")
            print(f"[DEBUG] Fact trace: {fact_trace}")

            assert fact_trace["model"] == "gpt-4o-mini"
            assert reasoning_trace["model"] == "gpt-4o"
            assert summary_trace["model"] == "gpt-4o-mini"

            # Verify system prompts are included in trace response
            assert fact_trace.get("system_prompt") == custom_prompt_stage1
            assert reasoning_trace["system_prompt"] == custom_prompt_stage2
            assert summary_trace["system_prompt"] == custom_prompt_stage3

            # Verify data was stored in database with system prompts and models
            from app.models.call_insights import CallInsightsAnalysis
            from sqlalchemy import select

            query = select(CallInsightsAnalysis).where(CallInsightsAnalysis.id == analysis_id)
            result = await db_session.execute(query)
            analysis = result.scalar_one_or_none()

            assert analysis is not None
            assert analysis.system_prompt_stage1 == custom_prompt_stage1
            assert analysis.system_prompt_stage2 == custom_prompt_stage2
            assert analysis.system_prompt_stage3 == custom_prompt_stage3
            assert analysis.model_stage1 == "gpt-4o-mini"
            assert analysis.model_stage2 == "gpt-4o"
            assert analysis.model_stage3 == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_analyze_validation_transcript_too_short(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for transcript too short
        GIVEN: Transcript with less than 100 characters
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns 422 validation error
        """
        request_data = {
            "transcript": "This is too short",
        }

        response = await client.post(
            "/api/v1/call-insights/analyze",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_analyze_validation_transcript_too_long(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for transcript too long
        GIVEN: Transcript with more than 100,000 characters
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns 422 validation error
        """
        request_data = {
            "transcript": "x" * 100001,
        }

        response = await client.post(
            "/api/v1/call-insights/analyze",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_validation_missing_transcript(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for missing transcript
        GIVEN: Request without transcript field
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns 422 validation error
        """
        request_data = {
            "transcript_title": "No Transcript",
        }

        response = await client.post(
            "/api/v1/call-insights/analyze",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test analysis without authentication
        GIVEN: Valid request WITHOUT auth token
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Returns 403 Forbidden
        """
        request_data = {
            "transcript": SAMPLE_TRANSCRIPT,
        }

        response = await client.post(
            "/api/v1/call-insights/analyze",
            json=request_data,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_analyze_pipeline_data_flow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
    ):
        """
        Test revised pipeline data flow
        GIVEN: Valid transcript
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Stage 2 only receives facts (no transcript), Stage 3 receives facts + reasoning
        """
        # Track what was sent to the model
        calls_made = []

        def mock_execute_side_effect(request):
            # Capture the user prompt to verify data flow
            user_message = next((msg["content"] for msg in request.messages if msg["role"] == "user"), "")
            calls_made.append({
                "model": request.model,
                "user_prompt": user_message,
                "temperature": request.temperature,
            })

            # Return different responses for each stage
            if len(calls_made) == 1:
                # Stage 1: Fact Extraction
                return ModelExecutionResult(
                    response="FACTS: Customer laptop won't turn on. Tried different outlet. Battery removal fixed issue.",
                    tokens_used=50,
                    cost=0.001,
                    input_tokens=30,
                    output_tokens=20,
                    model=request.model,
                )
            elif len(calls_made) == 2:
                # Stage 2: Reasoning
                return ModelExecutionResult(
                    response="REASONING: Common hardware issue. Residual charge problem. Quick resolution indicates good customer service.",
                    tokens_used=60,
                    cost=0.0012,
                    input_tokens=35,
                    output_tokens=25,
                    model=request.model,
                )
            else:
                # Stage 3: Summary
                return ModelExecutionResult(
                    response="SUMMARY: Successfully resolved laptop power issue through battery reset procedure.",
                    tokens_used=40,
                    cost=0.0008,
                    input_tokens=25,
                    output_tokens=15,
                    model=request.model,
                )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = mock_execute_side_effect

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "transcript_title": "Pipeline Data Flow Test",
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Should have called model 3 times (one per stage)
            assert len(calls_made) == 3

            # Stage 1: Should receive transcript
            stage1_prompt = calls_made[0]["user_prompt"]
            assert "TechSupport" in stage1_prompt or "laptop" in stage1_prompt  # Contains transcript content

            # Stage 2: Should ONLY receive facts, NOT transcript
            stage2_prompt = calls_made[1]["user_prompt"]
            assert "FACTS:" in stage2_prompt or "Customer laptop" in stage2_prompt  # Contains facts from Stage 1
            assert "TechSupport Inc" not in stage2_prompt  # Should NOT contain original transcript
            assert "{{facts}}" not in stage2_prompt  # Template variable should be replaced

            # Stage 3: Should receive facts + reasoning, NOT transcript
            stage3_prompt = calls_made[2]["user_prompt"]
            assert "FACTS:" in stage3_prompt or "REASONING:" in stage3_prompt  # Contains facts and reasoning
            assert "TechSupport Inc" not in stage3_prompt  # Should NOT contain original transcript
            assert "{{facts}}" not in stage3_prompt  # Template variables should be replaced
            assert "{{reasoning}}" not in stage3_prompt  # Template variables should be replaced


class TestCallInsightsHistory:
    """Test call insights history endpoints"""

    @pytest.mark.asyncio
    async def test_get_history_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test getting history when no analyses exist
        GIVEN: No previous analyses
        WHEN: GET /api/v1/call-insights/history
        THEN: Returns 200 with empty array
        """
        response = await client.get(
            "/api/v1/call-insights/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_history_with_results(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        test_project: Project,
    ):
        """
        Test getting history with previous analyses
        GIVEN: Multiple previous analyses
        WHEN: GET /api/v1/call-insights/history
        THEN: Returns 200 with list of analyses ordered by date desc
        """
        mock_result = ModelExecutionResult(
            response="Test response",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create 3 analyses
            for i in range(3):
                request_data = {
                    "transcript": SAMPLE_TRANSCRIPT,
                    "transcript_title": f"Test Analysis {i+1}",
                    "project_id": str(test_project.id),
                }

                await client.post(
                    "/api/v1/call-insights/analyze",
                    json=request_data,
                    headers=auth_headers,
                )

        # Get history
        response = await client.get(
            "/api/v1/call-insights/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Validate structure
        for item in data:
            assert "id" in item
            assert "transcript_title" in item
            assert "transcript_preview" in item
            assert "project_id" in item
            assert "total_tokens" in item
            assert "total_cost" in item
            assert "pii_redacted" in item
            assert "created_at" in item

        # Validate preview is truncated
        assert len(data[0]["transcript_preview"]) <= 203  # 200 + "..."

        # Validate order (most recent first)
        assert data[0]["transcript_title"] == "Test Analysis 3"
        assert data[1]["transcript_title"] == "Test Analysis 2"
        assert data[2]["transcript_title"] == "Test Analysis 1"

    @pytest.mark.asyncio
    async def test_get_history_search_by_title(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
    ):
        """
        Test searching history by title
        GIVEN: Multiple analyses with different titles
        WHEN: GET /api/v1/call-insights/history?search=XYZ_UNIQUE_LAPTOP
        THEN: Returns only analyses matching search term
        """
        mock_result = ModelExecutionResult(
            response="Test",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create analyses with different titles (using unique prefix to avoid conflicts with other tests)
            titles = ["XYZ_UNIQUE_LAPTOP Power Issue", "XYZ_PHONE Support Call", "XYZ_UNIQUE_LAPTOP Screen Problem"]
            for title in titles:
                await client.post(
                    "/api/v1/call-insights/analyze",
                    json={
                        "transcript": SAMPLE_TRANSCRIPT,
                        "transcript_title": title,
                        "project_id": str(test_project.id),
                    },
                    headers=auth_headers,
                )

        # Search for "XYZ_UNIQUE_LAPTOP" (unique search term)
        response = await client.get(
            "/api/v1/call-insights/history?search=XYZ_UNIQUE_LAPTOP",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("XYZ_UNIQUE_LAPTOP" in item["transcript_title"] for item in data)

    @pytest.mark.asyncio
    async def test_get_history_search_by_transcript_text(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test searching history by transcript content
        GIVEN: Analyses with different transcript content
        WHEN: GET /api/v1/call-insights/history?search=TechSupport
        THEN: Returns analyses containing search term in transcript
        """
        mock_result = ModelExecutionResult(
            response="Test",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create analysis with SAMPLE_TRANSCRIPT (contains "TechSupport Inc")
            await client.post(
                "/api/v1/call-insights/analyze",
                json={
                    "transcript": SAMPLE_TRANSCRIPT,
                    "transcript_title": "Support Call 1",
                },
                headers=auth_headers,
            )

            # Create analysis with different transcript
            await client.post(
                "/api/v1/call-insights/analyze",
                json={
                    "transcript": "A" * 150,  # Different content
                    "transcript_title": "Support Call 2",
                },
                headers=auth_headers,
            )

        # Search for "TechSupport" (case insensitive)
        response = await client.get(
            "/api/v1/call-insights/history?search=techsupport",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["transcript_title"] == "Support Call 1"

    @pytest.mark.asyncio
    async def test_get_history_filter_by_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test filtering history by project_id
        GIVEN: Analyses in different projects
        WHEN: GET /api/v1/call-insights/history?project_id={uuid}
        THEN: Returns only analyses for that project
        """
        # Create two projects
        project1 = Project(
            id=uuid.uuid4(),
            organization_id=demo_user.organization_id,
            name="Project Filter 1",
            created_by=str(demo_user.id),
        )
        project2 = Project(
            id=uuid.uuid4(),
            organization_id=demo_user.organization_id,
            name="Project Filter 2",
            created_by=str(demo_user.id),
        )

        db_session.add(project1)
        db_session.add(project2)
        await db_session.commit()
        await db_session.refresh(project1)
        await db_session.refresh(project2)

        mock_result = ModelExecutionResult(
            response="Test",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create analyses in different projects
            await client.post(
                "/api/v1/call-insights/analyze",
                json={
                    "transcript": SAMPLE_TRANSCRIPT,
                    "transcript_title": "Project Filter 1 Analysis",
                    "project_id": str(project1.id),
                },
                headers=auth_headers,
            )

            await client.post(
                "/api/v1/call-insights/analyze",
                json={
                    "transcript": SAMPLE_TRANSCRIPT,
                    "transcript_title": "Project Filter 2 Analysis",
                    "project_id": str(project2.id),
                },
                headers=auth_headers,
            )

        # Filter by project1
        response = await client.get(
            f"/api/v1/call-insights/history?project_id={str(project1.id)}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["transcript_title"] == "Project Filter 1 Analysis"
        assert data[0]["project_id"] == str(project1.id)

    @pytest.mark.asyncio
    async def test_get_history_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test history pagination
        GIVEN: 15 analyses
        WHEN: GET /api/v1/call-insights/history?limit=10&offset=10
        THEN: Returns 5 analyses (second page)
        """
        mock_result = ModelExecutionResult(
            response="Test",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create 15 analyses
            for i in range(15):
                await client.post(
                    "/api/v1/call-insights/analyze",
                    json={
                        "transcript": SAMPLE_TRANSCRIPT,
                        "transcript_title": f"Analysis {i+1:02d}",
                    },
                    headers=auth_headers,
                )

        # Get first page
        response = await client.get(
            "/api/v1/call-insights/history?limit=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 10

        # Get second page
        response = await client.get(
            "/api/v1/call-insights/history?limit=10&offset=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 5

    @pytest.mark.asyncio
    async def test_get_history_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test getting history without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/call-insights/history
        THEN: Returns 403 Forbidden
        """
        response = await client.get("/api/v1/call-insights/history")
        assert response.status_code == 403


class TestCallInsightsModels:
    """Test available models endpoint"""

    @pytest.mark.asyncio
    async def test_get_available_models_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test retrieving available models
        GIVEN: Authenticated user
        WHEN: GET /api/v1/call-insights/models/available
        THEN: Returns 200 with list of available models
        """
        response = await client.get(
            "/api/v1/call-insights/models/available",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5  # Should have 5 OpenAI models

        # Validate structure of each model
        for model in data:
            assert "model_id" in model
            assert "display_name" in model
            assert "provider" in model
            assert "description" in model
            assert "input_cost" in model
            assert "output_cost" in model
            assert "context_window" in model

            # Validate data types
            assert isinstance(model["model_id"], str)
            assert isinstance(model["display_name"], str)
            assert isinstance(model["provider"], str)
            assert isinstance(model["input_cost"], float)
            assert isinstance(model["output_cost"], float)
            assert isinstance(model["context_window"], int)

        # Validate specific models are present
        model_ids = [m["model_id"] for m in data]
        assert "gpt-4o-mini" in model_ids
        assert "gpt-4o" in model_ids
        assert "gpt-4-turbo" in model_ids
        assert "gpt-4" in model_ids
        assert "gpt-3.5-turbo" in model_ids

        # Validate gpt-4o-mini details (default model)
        gpt4o_mini = next(m for m in data if m["model_id"] == "gpt-4o-mini")
        assert gpt4o_mini["provider"] == "OpenAI"
        assert gpt4o_mini["input_cost"] == 0.00015
        assert gpt4o_mini["output_cost"] == 0.0006
        assert gpt4o_mini["context_window"] == 128000

    @pytest.mark.asyncio
    async def test_get_available_models_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test retrieving models without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/call-insights/models/available
        THEN: Returns 403 Forbidden
        """
        response = await client.get("/api/v1/call-insights/models/available")
        assert response.status_code == 403


class TestCallInsightsGetById:
    """Test get specific analysis by ID"""

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
    ):
        """
        Test retrieving specific analysis by ID
        GIVEN: Existing analysis
        WHEN: GET /api/v1/call-insights/{analysis_id}
        THEN: Returns 200 with full analysis details
        """
        mock_result = ModelExecutionResult(
            response="Test response",
            tokens_used=100,
            cost=0.002,
            input_tokens=70,
            output_tokens=30,
            model="gpt-4",
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result

            # Create analysis
            create_response = await client.post(
                "/api/v1/call-insights/analyze",
                json={
                    "transcript": SAMPLE_TRANSCRIPT,
                    "transcript_title": "Retrieve Test",
                    "project_id": str(test_project.id),
                },
                headers=auth_headers,
            )
            analysis_id = create_response.json()["analysis_id"]

        # Retrieve by ID
        response = await client.get(
            f"/api/v1/call-insights/{analysis_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Validate complete structure
        assert data["id"] == analysis_id
        assert data["transcript_title"] == "Retrieve Test"
        assert data["transcript_input"] == SAMPLE_TRANSCRIPT
        assert "summary_output" in data
        assert "insights_output" in data
        assert "facts_output" in data
        assert data["pii_redacted"] is False
        assert data["total_tokens"] > 0
        assert data["total_cost"] > 0
        assert data["project_id"] == str(test_project.id)
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test retrieving non-existent analysis
        GIVEN: Random UUID that doesn't exist
        WHEN: GET /api/v1/call-insights/{random_uuid}
        THEN: Returns 404 Not Found
        """
        random_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/v1/call-insights/{random_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Analysis not found"

    @pytest.mark.asyncio
    async def test_get_analysis_by_id_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test retrieving analysis without authentication
        GIVEN: No auth token
        WHEN: GET /api/v1/call-insights/{analysis_id}
        THEN: Returns 403 Forbidden
        """
        random_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/call-insights/{random_id}")
        assert response.status_code == 403
