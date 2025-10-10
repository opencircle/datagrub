"""
Call Insights Evaluation Integration Tests

Tests to verify evaluations are executed and tracked properly
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation
from app.models.trace import Trace
from app.services.model_provider import ModelExecutionResult
from app.evaluations.base import EvaluationResult


# Sample transcript
SAMPLE_TRANSCRIPT = """
Agent: Thank you for calling. How can I help you?
Customer: My laptop won't turn on.
Agent: Let's try removing the battery and holding the power button for 30 seconds.
Customer: Okay... it's working now!
Agent: Great! Have a nice day.
"""


@pytest.fixture
async def test_evaluation(db_session: AsyncSession, demo_user: User) -> EvaluationCatalog:
    """Create a test evaluation in catalog"""
    evaluation = EvaluationCatalog(
        organization_id=demo_user.organization_id,
        name="Answer Relevance Test",
        description="Test evaluation for answer relevance",
        category="quality",  # lowercase enum value
        source="vendor",  # lowercase enum value
        evaluation_type="metric",  # required field
        adapter_class="RagasAdapter",
        adapter_evaluation_id="answer_relevancy",
        vendor_name="ragas",
        is_active=True,
        is_public=True,
        default_config={"threshold": 0.7},
    )
    db_session.add(evaluation)
    await db_session.commit()
    await db_session.refresh(evaluation)
    return evaluation


class TestCallInsightsEvaluationExecution:
    """Test that evaluations are executed and tracked"""

    @pytest.mark.asyncio
    async def test_evaluations_executed_and_saved(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
        test_evaluation: EvaluationCatalog,
    ):
        """
        Test that evaluations are executed and saved to trace_evaluation table
        GIVEN: Analysis request with evaluation IDs
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Evaluations are executed and saved to trace_evaluation table
        """
        # Mock model provider
        mock_llm_result = ModelExecutionResult(
            response="Mocked LLM response",
            tokens_used=150,
            cost=0.003,
            input_tokens=100,
            output_tokens=50,
            model="gpt-4",
        )

        # Mock evaluation result
        mock_eval_result = EvaluationResult(
            score=0.85,
            passed=True,
            category="quality",
            reason="Answer is highly relevant to the question",
            details={"relevance_score": 0.85, "confidence": 0.9},
            suggestions=["Consider adding more context"],
            execution_time_ms=250.5,
            model_used="gpt-4",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            evaluation_cost=0.003,
            vendor_metrics={"ragas_version": "0.1.0"},
            llm_metadata={"temperature": 0.7},
            status="success",
            error=None,
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute, \
             patch('app.evaluations.registry.registry.execute_evaluation', new_callable=AsyncMock) as mock_eval:

            mock_execute.return_value = mock_llm_result
            mock_eval.return_value = mock_eval_result

            # Request analysis with evaluation
            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "transcript_title": "Evaluation Test",
                "evaluations": [str(test_evaluation.id)],
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify evaluation was executed
            assert mock_eval.called
            assert mock_eval.call_count == 1

            # Verify evaluation result in response
            assert len(data["evaluations"]) == 1
            eval_data = data["evaluations"][0]
            assert eval_data["evaluation_name"] == "Answer Relevance Test"
            assert eval_data["evaluation_uuid"] == str(test_evaluation.id)
            assert eval_data["score"] == 0.85
            assert eval_data["passed"] is True
            assert eval_data["reason"] == "Answer is highly relevant to the question"
            assert eval_data["category"] == "quality"
            assert eval_data["input_tokens"] == 100
            assert eval_data["output_tokens"] == 50
            assert eval_data["total_tokens"] == 150
            assert eval_data["evaluation_cost"] == 0.003

            # Verify trace was created
            analysis_id = data["analysis_id"]
            trace_query = select(Trace).where(
                Trace.name == "call_insights"
            )
            trace_result = await db_session.execute(trace_query)
            traces = trace_result.scalars().all()
            assert len(traces) > 0

            # Find parent trace (should have metadata.source == "call_insights")
            parent_trace = None
            for trace in traces:
                if trace.trace_metadata and trace.trace_metadata.get("source") == "call_insights":
                    parent_trace = trace
                    break

            assert parent_trace is not None, "Parent trace not found"

            # Verify evaluation was saved to trace_evaluation table
            eval_query = select(TraceEvaluation).where(
                TraceEvaluation.trace_id == parent_trace.id
            )
            eval_result = await db_session.execute(eval_query)
            saved_evaluations = eval_result.scalars().all()

            assert len(saved_evaluations) == 1
            saved_eval = saved_evaluations[0]

            # Verify all fields are saved correctly
            assert saved_eval.trace_id == parent_trace.id
            assert saved_eval.evaluation_catalog_id == test_evaluation.id
            assert saved_eval.score == 0.85
            assert saved_eval.passed is True
            assert saved_eval.category == "quality"
            assert saved_eval.reason == "Answer is highly relevant to the question"
            assert saved_eval.details == {"relevance_score": 0.85, "confidence": 0.9}
            assert saved_eval.suggestions == ["Consider adding more context"]
            assert saved_eval.execution_time_ms == 250.5
            assert saved_eval.model_used == "gpt-4"
            assert saved_eval.input_tokens == 100
            assert saved_eval.output_tokens == 50
            assert saved_eval.total_tokens == 150
            assert saved_eval.evaluation_cost == 0.003
            assert saved_eval.vendor_metrics == {"ragas_version": "0.1.0"}
            assert saved_eval.llm_metadata == {"temperature": 0.7}
            assert saved_eval.status == "success"
            assert saved_eval.error_message is None

    @pytest.mark.asyncio
    async def test_multiple_evaluations_executed(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test multiple evaluations are executed and tracked
        GIVEN: Analysis request with multiple evaluation IDs
        WHEN: POST /api/v1/call-insights/analyze
        THEN: All evaluations are executed and saved
        """
        # Create two evaluations
        eval1 = EvaluationCatalog(
            organization_id=demo_user.organization_id,
            name="Faithfulness",
            description="Test faithfulness",
            category="quality",
            source="vendor",
            evaluation_type="metric",
            adapter_class="RagasAdapter",
            adapter_evaluation_id="faithfulness",
            vendor_name="ragas",
            is_active=True,
            is_public=True,
            default_config={"threshold": 0.8},
        )
        eval2 = EvaluationCatalog(
            organization_id=demo_user.organization_id,
            name="Context Precision",
            description="Test context precision",
            category="quality",
            source="vendor",
            evaluation_type="metric",
            adapter_class="RagasAdapter",
            adapter_evaluation_id="context_precision",
            vendor_name="ragas",
            is_active=True,
            is_public=True,
            default_config={"threshold": 0.75},
        )
        db_session.add(eval1)
        db_session.add(eval2)
        await db_session.commit()
        await db_session.refresh(eval1)
        await db_session.refresh(eval2)

        # Mock responses
        mock_llm_result = ModelExecutionResult(
            response="Test", tokens_used=100, cost=0.002, input_tokens=70, output_tokens=30, model="gpt-4"
        )
        mock_eval_result = EvaluationResult(
            score=0.9, passed=True, category="quality", reason="Good",
            details={}, suggestions=[], execution_time_ms=200,
            model_used="gpt-4", input_tokens=50, output_tokens=30, total_tokens=80,
            evaluation_cost=0.002, vendor_metrics={}, llm_metadata={},
            status="success", error=None
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute, \
             patch('app.evaluations.registry.registry.execute_evaluation', new_callable=AsyncMock) as mock_eval:

            mock_execute.return_value = mock_llm_result
            mock_eval.return_value = mock_eval_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "evaluations": [str(eval1.id), str(eval2.id)],
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify both evaluations were executed
            assert mock_eval.call_count == 2
            assert len(data["evaluations"]) == 2

            # Verify both saved to database
            trace_query = select(Trace).where(Trace.name == "call_insights")
            trace_result = await db_session.execute(trace_query)
            traces = trace_result.scalars().all()

            parent_trace = None
            for trace in traces:
                if trace.trace_metadata and trace.trace_metadata.get("source") == "call_insights":
                    parent_trace = trace
                    break

            eval_query = select(TraceEvaluation).where(
                TraceEvaluation.trace_id == parent_trace.id
            )
            eval_result = await db_session.execute(eval_query)
            saved_evaluations = eval_result.scalars().all()

            assert len(saved_evaluations) == 2

    @pytest.mark.asyncio
    async def test_evaluation_failure_handled(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        test_evaluation: EvaluationCatalog,
    ):
        """
        Test that evaluation failures are handled gracefully
        GIVEN: Evaluation that throws an error
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Analysis succeeds but evaluation is not returned
        """
        mock_llm_result = ModelExecutionResult(
            response="Test", tokens_used=100, cost=0.002, input_tokens=70, output_tokens=30, model="gpt-4"
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute, \
             patch('app.evaluations.registry.registry.execute_evaluation', new_callable=AsyncMock) as mock_eval:

            mock_execute.return_value = mock_llm_result
            mock_eval.side_effect = Exception("Evaluation failed")

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "evaluations": [str(test_evaluation.id)],
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            # Analysis should still succeed
            assert response.status_code == 200
            data = response.json()

            # But no evaluations returned
            assert len(data["evaluations"]) == 0

    @pytest.mark.asyncio
    async def test_invalid_evaluation_id_ignored(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test that invalid evaluation IDs are ignored
        GIVEN: Analysis with non-existent evaluation ID
        WHEN: POST /api/v1/call-insights/analyze
        THEN: Analysis succeeds, invalid evaluation is skipped
        """
        import uuid

        mock_llm_result = ModelExecutionResult(
            response="Test", tokens_used=100, cost=0.002, input_tokens=70, output_tokens=30, model="gpt-4"
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_llm_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "evaluations": [str(uuid.uuid4())],  # Random UUID that doesn't exist
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["evaluations"]) == 0  # Invalid evaluation skipped

    @pytest.mark.asyncio
    async def test_organization_scoped_evaluations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test that private evaluations from other orgs are not accessible
        GIVEN: Private evaluation from different organization
        WHEN: POST /api/v1/call-insights/analyze with that evaluation ID
        THEN: Evaluation is skipped (access denied)
        """
        import uuid
        from app.models.user import Organization

        # Create a different organization
        other_org = Organization(
            id=uuid.uuid4(),
            name="Other Organization",
            description="Different org for testing",
        )
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)

        # Create evaluation for the different org
        other_org_eval = EvaluationCatalog(
            organization_id=other_org.id,  # Different org
            name="Private Evaluation",
            description="Private to another org",
            category="quality",
            source="vendor",
            evaluation_type="metric",
            adapter_class="RagasAdapter",
            adapter_evaluation_id="private_eval",
            vendor_name="ragas",
            is_active=True,
            is_public=False,  # Private
            default_config={},
        )
        db_session.add(other_org_eval)
        await db_session.commit()
        await db_session.refresh(other_org_eval)

        mock_llm_result = ModelExecutionResult(
            response="Test", tokens_used=100, cost=0.002, input_tokens=70, output_tokens=30, model="gpt-4"
        )

        with patch('app.services.model_provider.ModelProviderService.execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_llm_result

            request_data = {
                "transcript": SAMPLE_TRANSCRIPT,
                "evaluations": [str(other_org_eval.id)],
            }

            response = await client.post(
                "/api/v1/call-insights/analyze",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            # Private evaluation from other org should be skipped
            assert len(data["evaluations"]) == 0
