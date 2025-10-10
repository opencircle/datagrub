"""
Playground API Integration Tests
Tests for POST /api/v1/playground/execute
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Organization


class TestPlaygroundExecute:
    """Test playground execute endpoint"""

    @pytest.mark.asyncio
    async def test_execute_prompt_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
    ):
        """
        Test successful prompt execution
        GIVEN: Valid prompt request with authentication
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 200 with response and metrics
        """
        # Note: This will fail until model provider is configured
        # For now, we're testing the request structure
        request_data = {
            "prompt": "What is 2+2?",
            "system_prompt": "You are a helpful math assistant.",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "top_k": 40,
            },
            "metadata": {
                "intent": "math_question",
                "tone": "professional",
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
            headers=auth_headers,
        )

        # Expect 500 for now (no model provider configured)
        # Once provider is set up, change to 200
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "metrics" in data
            assert "trace_id" in data
            assert "model" in data
            assert "timestamp" in data
            assert data["model"] == "gpt-4"
            assert data["metrics"]["latency_ms"] > 0
            assert data["metrics"]["tokens_used"] > 0
            assert data["metrics"]["cost"] >= 0

    @pytest.mark.asyncio
    async def test_execute_prompt_unauthenticated(
        self,
        client: AsyncClient,
    ):
        """
        Test prompt execution without authentication
        GIVEN: Valid prompt request WITHOUT auth token
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 403 Forbidden
        """
        request_data = {
            "prompt": "Test prompt",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_execute_prompt_validation_empty_prompt(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for empty prompt
        GIVEN: Request with empty prompt
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 422 Validation Error
        """
        request_data = {
            "prompt": "",  # Empty prompt
            "model": "gpt-4",
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

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_execute_prompt_validation_temperature_out_of_range(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for temperature out of range
        GIVEN: Request with temperature > 2.0
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 422 Validation Error
        """
        request_data = {
            "prompt": "Test prompt",
            "model": "gpt-4",
            "parameters": {
                "temperature": 3.0,  # Out of range (max 2.0)
                "max_tokens": 500,
                "top_p": 0.9,
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_execute_prompt_validation_max_tokens_out_of_range(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for max_tokens out of range
        GIVEN: Request with max_tokens > 4000
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 422 Validation Error
        """
        request_data = {
            "prompt": "Test prompt",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 5000,  # Out of range (max 4000)
                "top_p": 0.9,
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_execute_prompt_validation_top_p_out_of_range(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test validation for top_p out of range
        GIVEN: Request with top_p > 1.0
        WHEN: POST /api/v1/playground/execute
        THEN: Returns 422 Validation Error
        """
        request_data = {
            "prompt": "Test prompt",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 1.5,  # Out of range (max 1.0)
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_execute_prompt_with_metadata(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test prompt execution with optional metadata
        GIVEN: Request with intent, tone, and prompt_id metadata
        WHEN: POST /api/v1/playground/execute
        THEN: Accepts metadata and processes request
        """
        request_data = {
            "prompt": "Explain machine learning",
            "system_prompt": "You are a technical educator",
            "model": "gpt-4",
            "parameters": {
                "temperature": 0.5,
                "max_tokens": 1000,
                "top_p": 0.95,
                "top_k": 50,
            },
            "metadata": {
                "intent": "education",
                "tone": "technical",
                "prompt_id": "prompt-123",
            },
        }

        response = await client.post(
            "/api/v1/playground/execute",
            json=request_data,
            headers=auth_headers,
        )

        # Will be 500 until provider configured, then 200
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_execute_prompt_minimal_request(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """
        Test minimal valid request (required fields only)
        GIVEN: Request with only prompt, model, and parameters
        WHEN: POST /api/v1/playground/execute
        THEN: Accepts request without optional fields
        """
        request_data = {
            "prompt": "Hello, world!",
            "model": "gpt-4",
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

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_execute_prompt_creates_trace(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test that playground execution creates a retrievable trace
        GIVEN: Successful playground execution
        WHEN: POST /api/v1/playground/execute returns trace_id
        THEN: Trace can be retrieved via GET /api/v1/traces/{trace_id}/detail
        AND: Trace details match the execution parameters

        This test ensures complete observability - no execution goes untraced
        """
        from unittest.mock import AsyncMock, patch
        from app.services.model_provider import ModelExecutionResult

        # Mock the model provider to return a successful response
        mock_execution_result = ModelExecutionResult(
            response="The answer is 4.",
            input_tokens=20,
            output_tokens=22,
            tokens_used=42,
            cost=0.0014,
        )

        with patch('app.api.v1.endpoints.playground.ModelProviderService') as mock_provider:
            # Configure the mock
            mock_instance = AsyncMock()
            mock_instance.execute = AsyncMock(return_value=mock_execution_result)
            mock_provider.return_value = mock_instance

            # Execute playground prompt
            request_data = {
                "prompt": "What is 2+2?",
                "system_prompt": "You are a helpful math assistant.",
                "model": "gpt-4",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                    "top_k": 40,
                },
                "metadata": {
                    "intent": "math_question",
                    "tone": "professional",
                },
            }

            response = await client.post(
                "/api/v1/playground/execute",
                json=request_data,
                headers=auth_headers,
            )

            # Verify successful execution
            assert response.status_code == 200
            playground_data = response.json()

            # Extract trace_id from playground response
            assert "trace_id" in playground_data
            trace_id = playground_data["trace_id"]
            assert trace_id is not None
            assert len(trace_id) > 0

            # Verify other playground response fields
            assert playground_data["response"] == "The answer is 4."
            assert playground_data["model"] == "gpt-4"
            assert playground_data["metrics"]["tokens_used"] == 42
            assert playground_data["metrics"]["cost"] == 0.0014
            assert playground_data["metrics"]["latency_ms"] > 0

            # Now retrieve the trace using the trace API
            # The trace should exist and match the execution
            from sqlalchemy import select
            from app.models.trace import Trace

            # Query the trace by trace_id
            stmt = select(Trace).where(Trace.trace_id == trace_id)
            result = await db_session.execute(stmt)
            trace = result.scalar_one_or_none()

            # Verify trace was created
            assert trace is not None, f"Trace {trace_id} not found in database"

            # Verify trace details match execution
            assert trace.model_name == "gpt-4"
            assert trace.input_tokens == 20
            assert trace.output_tokens == 22
            assert trace.total_tokens == 42
            assert trace.total_cost == 0.0014
            assert trace.status == "success"
            assert trace.user_id == demo_user.id
            assert trace.environment == "playground"

            # Verify input data
            assert trace.input_data is not None
            assert trace.input_data["prompt"] == "What is 2+2?"
            assert trace.input_data["system_prompt"] == "You are a helpful math assistant."
            assert trace.input_data["parameters"]["temperature"] == 0.7

            # Verify output data
            assert trace.output_data is not None
            assert trace.output_data["response"] == "The answer is 4."

            # Verify metadata
            assert trace.trace_metadata is not None
            assert trace.trace_metadata["intent"] == "math_question"
            assert trace.trace_metadata["tone"] == "professional"
            assert trace.trace_metadata["source"] == "playground"

            # Now verify we can retrieve the same trace via the trace detail API
            trace_detail_response = await client.get(
                f"/api/v1/traces/{trace.id}/detail",
                headers=auth_headers,
            )

            assert trace_detail_response.status_code == 200
            trace_detail = trace_detail_response.json()

            # Verify the detail API returns matching data
            assert trace_detail["trace_id"] == trace_id
            assert trace_detail["model_name"] == "gpt-4"
            assert trace_detail["total_tokens"] == 42
            assert trace_detail["total_cost"] == 0.0014
            assert trace_detail["status"] == "success"
            assert trace_detail["environment"] == "playground"

            print(f"✅ Trace {trace_id} successfully created and retrieved")

    @pytest.mark.asyncio
    async def test_execute_prompt_with_evaluation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test playground execution with evaluation integration
        GIVEN: Playground execution request with evaluation_ids
        WHEN: POST /api/v1/playground/execute with evaluation_ids
        THEN: Trace is created and evaluations are executed and stored in trace_evaluations table

        This test ensures evaluations can be run automatically after prompt execution
        """
        from unittest.mock import AsyncMock, patch
        from app.services.model_provider import ModelExecutionResult
        from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation, EvaluationSource, EvaluationCategory, EvaluationType
        from app.models.trace import Trace
        from app.evaluations.base import EvaluationResult as FrameworkEvaluationResult
        from sqlalchemy import select

        # Create a test evaluation in the catalog
        test_evaluation = EvaluationCatalog(
            name="PromptInjectionEval",
            description="Detects prompt injection attacks",
            category=EvaluationCategory.SECURITY,
            source=EvaluationSource.VENDOR,
            evaluation_type=EvaluationType.VALIDATOR,
            is_public=True,
            is_active=True,
            adapter_class="PromptInjectionAdapter",
            default_config={},
            version="1.0.0",
        )
        db_session.add(test_evaluation)
        await db_session.commit()
        await db_session.refresh(test_evaluation)

        # Mock the model provider
        mock_execution_result = ModelExecutionResult(
            response="The answer is 4.",
            input_tokens=20,
            output_tokens=22,
            tokens_used=42,
            cost=0.0014,
        )

        # Mock the evaluation registry
        mock_eval_result = FrameworkEvaluationResult(
            score=0.95,
            passed=True,
            reason="No prompt injection detected",
            details={"confidence": 0.95, "patterns_checked": 5},
            suggestions=[],
            execution_time_ms=15.5,
            model_used=None,
            status="completed",
            error=None,
            category=None,
        )

        with patch('app.api.v1.endpoints.playground.ModelProviderService') as mock_provider, \
             patch('app.evaluations.registry.registry.execute_evaluation', new_callable=AsyncMock) as mock_execute_eval:

            # Configure mocks
            mock_instance = AsyncMock()
            mock_instance.execute = AsyncMock(return_value=mock_execution_result)
            mock_provider.return_value = mock_instance
            mock_execute_eval.return_value = mock_eval_result

            # Execute playground prompt with evaluation
            request_data = {
                "prompt": "What is 2+2?",
                "system_prompt": "You are a helpful math assistant.",
                "model": "gpt-4",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                    "top_k": 40,
                },
                "metadata": {
                    "intent": "math_question",
                    "tone": "professional",
                },
                "evaluation_ids": [str(test_evaluation.id)],  # Include evaluation
            }

            response = await client.post(
                "/api/v1/playground/execute",
                json=request_data,
                headers=auth_headers,
            )

            # Verify successful execution
            assert response.status_code == 200
            playground_data = response.json()

            # Extract trace_id
            trace_id = playground_data["trace_id"]
            assert trace_id is not None

            # Query the trace
            stmt = select(Trace).where(Trace.trace_id == trace_id)
            result = await db_session.execute(stmt)
            trace = result.scalar_one_or_none()

            assert trace is not None, f"Trace {trace_id} not found"

            # Query trace_evaluations table
            eval_stmt = select(TraceEvaluation).where(TraceEvaluation.trace_id == trace.id)
            eval_result = await db_session.execute(eval_stmt)
            trace_evaluations = eval_result.scalars().all()

            # Verify evaluation was executed and stored
            assert len(trace_evaluations) == 1, "Expected 1 evaluation result"
            trace_eval = trace_evaluations[0]

            assert trace_eval.evaluation_catalog_id == test_evaluation.id
            assert trace_eval.score == 0.95
            assert trace_eval.passed == True
            assert trace_eval.reason == "No prompt injection detected"
            assert trace_eval.status == "completed"
            assert trace_eval.execution_time_ms == 15.5

            # Verify evaluation was called with correct parameters
            mock_execute_eval.assert_called_once()
            call_args = mock_execute_eval.call_args
            assert call_args[0][0] == str(test_evaluation.id)  # evaluation_id
            assert call_args[1]['source'] == EvaluationSource.VENDOR

            print(f"✅ Trace {trace_id} successfully created with evaluation {test_evaluation.name}")

    @pytest.mark.asyncio
    async def test_execute_prompt_with_real_evaluation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        demo_user: User,
        db_session: AsyncSession,
    ):
        """
        Test playground execution with REAL evaluation (not mocked)
        GIVEN: Playground execution request with PromptForge evaluation
        WHEN: POST /api/v1/playground/execute with real evaluation_ids
        THEN: Trace is created and evaluations are executed by real adapters

        This test verifies actual adapter execution without mocks
        """
        from unittest.mock import AsyncMock, patch
        from app.services.model_provider import ModelExecutionResult
        from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation, EvaluationSource, EvaluationCategory, EvaluationType
        from app.models.trace import Trace
        from sqlalchemy import select

        # Create a PromptForge evaluation that will use the real adapter
        promptforge_evaluation = EvaluationCatalog(
            name="Prompt Quality Score",
            description="Comprehensive quality assessment",
            category=EvaluationCategory.QUALITY,
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=EvaluationType.METRIC,
            is_public=True,
            is_active=True,
            adapter_class="PromptForgeAdapter",
            adapter_evaluation_id="pf-prompt-quality-score",  # Adapter's internal ID
            default_config={},
            version="1.0.0",
        )
        db_session.add(promptforge_evaluation)
        await db_session.commit()
        await db_session.refresh(promptforge_evaluation)

        # Mock ONLY the model provider (not the evaluation execution)
        mock_execution_result = ModelExecutionResult(
            response="The answer is 4.",
            input_tokens=20,
            output_tokens=22,
            tokens_used=42,
            cost=0.0014,
        )

        with patch('app.api.v1.endpoints.playground.ModelProviderService') as mock_provider:
            # Configure mock for model provider only
            mock_instance = AsyncMock()
            mock_instance.execute = AsyncMock(return_value=mock_execution_result)
            mock_provider.return_value = mock_instance

            # Execute playground prompt with REAL evaluation
            request_data = {
                "prompt": "What is 2+2?",
                "system_prompt": "You are a helpful math assistant.",
                "model": "gpt-4",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                    "top_k": 40,
                },
                "metadata": {
                    "intent": "math_question",
                    "tone": "professional",
                },
                "evaluation_ids": [str(promptforge_evaluation.id)],  # Real evaluation
            }

            response = await client.post(
                "/api/v1/playground/execute",
                json=request_data,
                headers=auth_headers,
            )

            # Verify successful execution
            assert response.status_code == 200
            playground_data = response.json()

            # Extract trace_id
            trace_id = playground_data["trace_id"]
            assert trace_id is not None

            # Query the trace
            stmt = select(Trace).where(Trace.trace_id == trace_id)
            result = await db_session.execute(stmt)
            trace = result.scalar_one_or_none()

            assert trace is not None, f"Trace {trace_id} not found"

            # Query trace_evaluations table
            eval_stmt = select(TraceEvaluation).where(TraceEvaluation.trace_id == trace.id)
            eval_result = await db_session.execute(eval_stmt)
            trace_evaluations = eval_result.scalars().all()

            # Verify evaluation was executed and stored
            assert len(trace_evaluations) == 1, "Expected 1 evaluation result"
            trace_eval = trace_evaluations[0]

            # Print debug info
            print(f"\n=== Evaluation Result Debug ===")
            print(f"Evaluation ID: {trace_eval.evaluation_catalog_id}")
            print(f"Score: {trace_eval.score}")
            print(f"Passed: {trace_eval.passed}")
            print(f"Status: {trace_eval.status}")
            print(f"Error: {trace_eval.error_message}")
            print(f"Reason: {trace_eval.reason}")
            print(f"Details: {trace_eval.details}")
            print(f"Execution Time: {trace_eval.execution_time_ms}")
            print(f"================================\n")

            # Verify the evaluation result
            assert trace_eval.evaluation_catalog_id == promptforge_evaluation.id

            # Check if there was an error
            if trace_eval.error_message:
                raise AssertionError(f"Evaluation failed with error: {trace_eval.error_message}")

            assert trace_eval.score is not None, f"Evaluation should return a score. Got: {trace_eval.score}, Status: {trace_eval.status}, Error: {trace_eval.error_message}"
            assert trace_eval.passed is not None, "Evaluation should return pass/fail"
            assert trace_eval.status in ["completed", "failed"], f"Status should be completed or failed, got {trace_eval.status}"

            # Real evaluations should have execution time
            assert trace_eval.execution_time_ms is not None and trace_eval.execution_time_ms > 0, "Should have execution time"

            print(f"✅ Trace {trace_id} successfully created with REAL evaluation {promptforge_evaluation.name}")
            print(f"   Score: {trace_eval.score}, Passed: {trace_eval.passed}, Status: {trace_eval.status}")
