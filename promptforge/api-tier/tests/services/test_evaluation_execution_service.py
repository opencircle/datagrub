"""
Unit tests for EvaluationExecutionService
"""
import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from app.services.evaluation_execution_service import EvaluationExecutionService
from app.models.trace import Trace
from app.models.evaluation_catalog import (
    EvaluationCatalog,
    EvaluationSource,
    EvaluationType,
    EvaluationCategory,
)
from app.evaluations.base import EvaluationResult


@pytest.mark.asyncio
class TestEvaluationExecutionService:
    """Tests for EvaluationExecutionService"""

    @pytest.fixture
    async def service(self, test_db_session, test_user):
        """Create evaluation execution service"""
        return EvaluationExecutionService(
            db=test_db_session,
            organization_id=test_user.organization_id,
        )

    @pytest.fixture
    async def test_trace(self, test_db_session, test_user):
        """Create test trace"""
        trace = Trace(
            id=uuid4(),
            name="Test Trace",
            status="success",
            project_id=uuid4(),
            user_id=test_user.id,
            model_name="gpt-4o",
            input_data={"prompt": "What is AI?"},
            output_data={"response": "AI is artificial intelligence"},
            total_duration_ms=500.0,
            total_tokens=100,
            total_cost=0.001,
        )
        test_db_session.add(trace)
        await test_db_session.commit()
        return trace

    @pytest.fixture
    async def test_evaluation(self, test_db_session, test_user):
        """Create test evaluation"""
        evaluation = EvaluationCatalog(
            name="Accuracy Check",
            description="Checks response accuracy",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
            adapter_class="PromptForgeAdapter",
            adapter_evaluation_id="accuracy-check",
        )
        test_db_session.add(evaluation)
        await test_db_session.commit()
        return evaluation

    async def test_run_evaluations_success(
        self,
        service,
        test_trace,
        test_evaluation,
        test_user,
        test_db_session,
    ):
        """Test successful evaluation execution"""
        # Mock the registry execution
        with patch.object(
            service.evaluation_registry, "execute_evaluation"
        ) as mock_exec:
            mock_exec.return_value = EvaluationResult(
                score=0.92,
                passed=True,
                reason="Response is accurate and well-structured",
                details={"confidence": 0.95, "metrics": {"precision": 0.9}},
                suggestions=["Consider adding more examples"],
                execution_time_ms=250.0,
                model_used="gpt-4o",
                input_tokens=50,
                output_tokens=30,
                total_tokens=80,
                evaluation_cost=0.0008,
                status="completed",
            )

            # Run evaluations
            results = await service.run_evaluations(
                evaluation_ids=[test_evaluation.id],
                trace_id=test_trace.id,
                user_id=test_user.id,
            )

            # Verify results
            assert len(results) == 1
            result = results[0]

            assert result["evaluation_id"] == test_evaluation.id
            assert result["evaluation_name"] == "Accuracy Check"
            assert result["score"] == 0.92
            assert result["passed"] is True
            assert result["reason"] == "Response is accurate and well-structured"
            assert result["status"] == "completed"
            assert result["error_message"] is None

            # Check metadata
            metadata = result["metadata"]
            assert metadata["model"] == "gpt-4o"
            assert metadata["tokens"] == 80
            assert metadata["cost"] == 0.0008
            assert "duration_ms" in metadata

            # Verify trace evaluation was created
            from sqlalchemy import select
            from app.models.evaluation_catalog import TraceEvaluation

            query = select(TraceEvaluation).where(
                TraceEvaluation.trace_id == test_trace.id,
                TraceEvaluation.evaluation_catalog_id == test_evaluation.id,
            )
            db_result = await test_db_session.execute(query)
            trace_eval = db_result.scalar_one_or_none()

            assert trace_eval is not None
            assert trace_eval.score == 0.92
            assert trace_eval.passed is True
            assert trace_eval.status == "completed"

    async def test_run_evaluations_with_model_override(
        self,
        service,
        test_trace,
        test_evaluation,
        test_user,
    ):
        """Test evaluation execution with model override"""
        with patch.object(
            service.evaluation_registry, "execute_evaluation"
        ) as mock_exec:
            mock_exec.return_value = EvaluationResult(
                score=0.88,
                passed=True,
                status="completed",
                execution_time_ms=200.0,
            )

            results = await service.run_evaluations(
                evaluation_ids=[test_evaluation.id],
                trace_id=test_trace.id,
                user_id=test_user.id,
                model_override="gpt-4-turbo",
            )

            assert len(results) == 1
            # Model override should be reflected in metadata
            assert "gpt-4" in results[0]["metadata"]["model"]

    async def test_run_evaluations_trace_not_found(
        self,
        service,
        test_evaluation,
        test_user,
    ):
        """Test evaluation execution with non-existent trace"""
        with pytest.raises(ValueError, match="Trace not found"):
            await service.run_evaluations(
                evaluation_ids=[test_evaluation.id],
                trace_id=uuid4(),  # Non-existent trace
                user_id=test_user.id,
            )

    async def test_run_evaluations_evaluation_not_found(
        self,
        service,
        test_trace,
        test_user,
    ):
        """Test evaluation execution with non-existent evaluation"""
        results = await service.run_evaluations(
            evaluation_ids=[uuid4()],  # Non-existent evaluation
            trace_id=test_trace.id,
            user_id=test_user.id,
        )

        assert len(results) == 1
        result = results[0]
        assert result["status"] == "failed"
        assert "not found" in result["reason"].lower()

    async def test_run_evaluations_access_denied(
        self,
        service,
        test_trace,
        test_db_session,
        test_user,
    ):
        """Test evaluation execution with access denied to private evaluation"""
        # Create private evaluation for different organization
        other_org_id = uuid4()
        private_eval = EvaluationCatalog(
            name="Private Evaluation",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.CUSTOM,
            evaluation_type=EvaluationType.METRIC,
            is_public=False,
            organization_id=other_org_id,  # Different organization
        )
        test_db_session.add(private_eval)
        await test_db_session.commit()

        results = await service.run_evaluations(
            evaluation_ids=[private_eval.id],
            trace_id=test_trace.id,
            user_id=test_user.id,
        )

        assert len(results) == 1
        result = results[0]
        assert result["status"] == "failed"
        assert "access denied" in result["reason"].lower()

    async def test_run_evaluations_execution_error(
        self,
        service,
        test_trace,
        test_evaluation,
        test_user,
    ):
        """Test evaluation execution with adapter error"""
        with patch.object(
            service.evaluation_registry, "execute_evaluation"
        ) as mock_exec:
            mock_exec.return_value = EvaluationResult(
                status="failed",
                error="Adapter execution failed: timeout",
            )

            results = await service.run_evaluations(
                evaluation_ids=[test_evaluation.id],
                trace_id=test_trace.id,
                user_id=test_user.id,
            )

            assert len(results) == 1
            result = results[0]
            assert result["status"] == "failed"
            assert result["error_message"] is not None

    async def test_run_multiple_evaluations(
        self,
        service,
        test_trace,
        test_user,
        test_db_session,
    ):
        """Test running multiple evaluations on same trace"""
        # Create multiple evaluations
        eval1 = EvaluationCatalog(
            name="Accuracy",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
        )
        eval2 = EvaluationCatalog(
            name="Safety",
            category=EvaluationCategory.SAFETY,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.VALIDATOR,
            is_public=True,
            organization_id=test_user.organization_id,
        )
        test_db_session.add_all([eval1, eval2])
        await test_db_session.commit()

        with patch.object(
            service.evaluation_registry, "execute_evaluation"
        ) as mock_exec:
            # Return different results for each evaluation
            mock_exec.side_effect = [
                EvaluationResult(
                    score=0.9, passed=True, status="completed", execution_time_ms=200.0
                ),
                EvaluationResult(
                    passed=True, status="completed", execution_time_ms=150.0
                ),
            ]

            results = await service.run_evaluations(
                evaluation_ids=[eval1.id, eval2.id],
                trace_id=test_trace.id,
                user_id=test_user.id,
            )

            assert len(results) == 2
            assert results[0]["evaluation_name"] == "Accuracy"
            assert results[0]["score"] == 0.9
            assert results[1]["evaluation_name"] == "Safety"
            assert results[1]["passed"] is True

    async def test_create_evaluation_trace(
        self,
        service,
        test_trace,
        test_evaluation,
        test_user,
        test_db_session,
    ):
        """Test child trace creation for evaluation"""
        eval_result = EvaluationResult(
            score=0.85,
            passed=True,
            reason="Good response",
            status="completed",
            execution_time_ms=300.0,
            model_used="gpt-4o",
            input_tokens=40,
            output_tokens=25,
            total_tokens=65,
            evaluation_cost=0.0007,
        )

        child_trace = await service._create_evaluation_trace(
            parent_trace=test_trace,
            evaluation=test_evaluation,
            eval_result=eval_result,
            user_id=test_user.id,
        )

        assert child_trace is not None
        assert child_trace.name == f"Evaluation: {test_evaluation.name}"
        assert child_trace.parent_trace_id == test_trace.id
        assert child_trace.status == "success"
        assert child_trace.total_duration_ms == 300.0
        assert child_trace.total_tokens == 65
        assert child_trace.total_cost == 0.0007

        # Verify input/output data
        assert "evaluation_id" in child_trace.input_data
        assert child_trace.output_data["score"] == 0.85
        assert child_trace.output_data["passed"] is True
