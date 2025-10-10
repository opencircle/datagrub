"""
Unit tests for new evaluation endpoints
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.user import User
from app.models.trace import Trace
from app.models.evaluation_catalog import (
    EvaluationCatalog,
    TraceEvaluation,
    EvaluationSource,
    EvaluationType,
    EvaluationCategory,
)
from app.schemas.evaluation_execution import (
    EvaluationRunRequest,
    CustomEvaluationCreate,
)


@pytest.mark.asyncio
class TestEvaluationListEndpoint:
    """Tests for GET /api/v1/evaluations/list endpoint"""

    async def test_list_evaluations_with_filters(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test listing evaluations with various filters"""
        # Create test data
        trace = Trace(
            id=uuid4(),
            name="Test Trace",
            status="success",
            project_id=uuid4(),
            user_id=test_user.id,
            model_name="gpt-4o",
        )
        test_db_session.add(trace)

        evaluation_catalog = EvaluationCatalog(
            name="Test Evaluation",
            description="Test description",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
        )
        test_db_session.add(evaluation_catalog)
        await test_db_session.flush()

        trace_eval = TraceEvaluation(
            trace_id=trace.id,
            evaluation_catalog_id=evaluation_catalog.id,
            score=0.85,
            passed=True,
            total_tokens=150,
            evaluation_cost=0.002,
            execution_time_ms=350.5,
            model_used="gpt-4o",
            status="completed",
        )
        test_db_session.add(trace_eval)
        await test_db_session.commit()

        # Test without filters
        response = await client.get(
            "/api/v1/evaluations/list",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "evaluations" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["evaluations"]) > 0

        # Test with trace_id filter
        response = await client.get(
            f"/api/v1/evaluations/list?trace_id={trace.id}",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["evaluations"]) == 1
        assert data["evaluations"][0]["trace_id"] == str(trace.id)

        # Test with name filter (fuzzy search)
        response = await client.get(
            "/api/v1/evaluations/list?name=Test",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["evaluations"]) > 0

        # Test with type filter
        response = await client.get(
            "/api/v1/evaluations/list?type=promptforge",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Test with model filter
        response = await client.get(
            "/api/v1/evaluations/list?model=gpt-4o",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_list_evaluations_pagination(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test pagination for evaluation list"""
        # Create multiple trace evaluations
        trace = Trace(
            id=uuid4(),
            name="Test Trace",
            status="success",
            project_id=uuid4(),
            user_id=test_user.id,
        )
        test_db_session.add(trace)

        evaluation_catalog = EvaluationCatalog(
            name="Test Evaluation",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
        )
        test_db_session.add(evaluation_catalog)
        await test_db_session.flush()

        # Create 25 trace evaluations
        for i in range(25):
            trace_eval = TraceEvaluation(
                trace_id=trace.id,
                evaluation_catalog_id=evaluation_catalog.id,
                score=0.8 + (i * 0.01),
                passed=True,
                status="completed",
            )
            test_db_session.add(trace_eval)
        await test_db_session.commit()

        # Test first page
        response = await client.get(
            "/api/v1/evaluations/list?limit=10&offset=0",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["evaluations"]) == 10
        assert data["total"] == 25
        assert data["limit"] == 10
        assert data["offset"] == 0

        # Test second page
        response = await client.get(
            "/api/v1/evaluations/list?limit=10&offset=10",
            headers={"Authorization": f"Bearer {test_user.token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["evaluations"]) == 10
        assert data["offset"] == 10


@pytest.mark.asyncio
class TestEvaluationRunEndpoint:
    """Tests for POST /api/v1/evaluations/run endpoint"""

    async def test_run_evaluations_success(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test successful evaluation execution"""
        # Create test trace
        trace = Trace(
            id=uuid4(),
            name="Test Trace",
            status="success",
            project_id=uuid4(),
            user_id=test_user.id,
            model_name="gpt-4o",
            input_data={"prompt": "Test input"},
            output_data={"response": "Test output"},
        )
        test_db_session.add(trace)

        # Create evaluation catalog entry
        evaluation = EvaluationCatalog(
            name="Test Evaluation",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
            adapter_class="PromptForgeAdapter",
            adapter_evaluation_id="test-eval-id",
        )
        test_db_session.add(evaluation)
        await test_db_session.commit()

        # Mock the execution service
        with patch(
            "app.services.evaluation_execution_service.EvaluationExecutionService.run_evaluations"
        ) as mock_run:
            mock_run.return_value = [
                {
                    "evaluation_id": evaluation.id,
                    "evaluation_name": "Test Evaluation",
                    "trace_id": uuid4(),
                    "score": 0.9,
                    "passed": True,
                    "reason": "Evaluation passed",
                    "metadata": {
                        "model": "gpt-4o",
                        "tokens": 100,
                        "cost": 0.001,
                        "duration_ms": 250.0,
                    },
                    "status": "completed",
                    "error_message": None,
                }
            ]

            # Make request
            request_data = {
                "evaluation_ids": [str(evaluation.id)],
                "trace_id": str(trace.id),
                "model_override": None,
            }

            response = await client.post(
                "/api/v1/evaluations/run",
                json=request_data,
                headers={"Authorization": f"Bearer {test_user.token}"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["evaluation_name"] == "Test Evaluation"
            assert data[0]["score"] == 0.9
            assert data[0]["passed"] is True
            assert data[0]["status"] == "completed"

    async def test_run_evaluations_invalid_trace(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test running evaluations on non-existent trace"""
        # Mock the execution service to raise ValueError
        with patch(
            "app.services.evaluation_execution_service.EvaluationExecutionService.run_evaluations"
        ) as mock_run:
            mock_run.side_effect = ValueError("Trace not found")

            request_data = {
                "evaluation_ids": [str(uuid4())],
                "trace_id": str(uuid4()),
            }

            response = await client.post(
                "/api/v1/evaluations/run",
                json=request_data,
                headers={"Authorization": f"Bearer {test_user.token}"},
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestCustomEvaluationEndpoint:
    """Tests for POST /api/v1/evaluation-catalog/custom-simple endpoint"""

    async def test_create_custom_evaluation(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test creating a custom evaluation"""
        request_data = {
            "name": "Custom Accuracy Check",
            "category": "accuracy",
            "description": "Checks response accuracy",
            "prompt_input": "Evaluate the accuracy of the input based on facts",
            "prompt_output": "Evaluate if the output is accurate and factual",
            "system_prompt": "You are an accuracy evaluator. Check if responses are factually correct.",
            "model": "gpt-4o-mini",
        }

        response = await client.post(
            "/api/v1/evaluation-catalog/custom-simple",
            params=request_data,
            headers={"Authorization": f"Bearer {test_user.token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Custom Accuracy Check"
        assert data["source"] == "custom"
        assert "id" in data
        assert "created_at" in data

    async def test_create_custom_evaluation_validation_error(
        self,
        client,
        test_user,
        test_db_session,
    ):
        """Test validation errors for custom evaluation creation"""
        # Test with short name
        request_data = {
            "name": "Ab",  # Too short
            "category": "accuracy",
            "prompt_input": "Test prompt",
            "prompt_output": "Test output",
            "system_prompt": "Test system",
        }

        response = await client.post(
            "/api/v1/evaluation-catalog/custom-simple",
            params=request_data,
            headers={"Authorization": f"Bearer {test_user.token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with short prompt_input
        request_data = {
            "name": "Valid Name",
            "category": "accuracy",
            "prompt_input": "Short",  # Too short
            "prompt_output": "Valid output prompt",
            "system_prompt": "Valid system prompt",
        }

        response = await client.post(
            "/api/v1/evaluation-catalog/custom-simple",
            params=request_data,
            headers={"Authorization": f"Bearer {test_user.token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
class TestEvaluationExecutionService:
    """Tests for EvaluationExecutionService"""

    async def test_run_evaluations(self, test_db_session, test_user):
        """Test the evaluation execution service"""
        from app.services.evaluation_execution_service import (
            EvaluationExecutionService,
        )

        # Create test data
        trace = Trace(
            id=uuid4(),
            name="Test Trace",
            status="success",
            project_id=uuid4(),
            user_id=test_user.id,
            model_name="gpt-4o",
            input_data={"prompt": "Test"},
            output_data={"response": "Test response"},
        )
        test_db_session.add(trace)

        evaluation = EvaluationCatalog(
            name="Test Eval",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            organization_id=test_user.organization_id,
        )
        test_db_session.add(evaluation)
        await test_db_session.commit()

        # Create service
        service = EvaluationExecutionService(
            db=test_db_session,
            organization_id=test_user.organization_id,
        )

        # Mock the registry execution
        with patch.object(
            service.evaluation_registry, "execute_evaluation"
        ) as mock_exec:
            from app.evaluations.base import EvaluationResult

            mock_exec.return_value = EvaluationResult(
                score=0.85,
                passed=True,
                reason="Test passed",
                status="completed",
                execution_time_ms=200.0,
            )

            # Run evaluations
            results = await service.run_evaluations(
                evaluation_ids=[evaluation.id],
                trace_id=trace.id,
                user_id=test_user.id,
            )

            assert len(results) == 1
            assert results[0]["evaluation_id"] == evaluation.id
            assert results[0]["score"] == 0.85
            assert results[0]["passed"] is True
            assert results[0]["status"] == "completed"
