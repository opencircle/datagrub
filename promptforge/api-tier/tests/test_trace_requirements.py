"""
Comprehensive trace validation tests

CRITICAL REQUIREMENTS (for accounting and billing):
1. ALL model invocations MUST be traced (success or failure)
2. ALL traces MUST have duration tracked (ms)
3. ALL traces MUST have token counts (input, output, total)
4. ALL traces MUST have cost calculated
5. ALL trace failures MUST capture error reason and type
6. Traces MUST be model-neutral (work with OpenAI, Claude, etc.)

These tests validate that no model invocation is ever missed.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response

from app.services.trace_service import TraceService
from app.services.model_provider import (
    ModelProviderService,
    ModelExecutionRequest,
    ModelExecutionResult,
)
from app.services.call_insights_service import CallInsightsService
from app.models.trace import Trace
from app.models.user import User, Organization


class TestTraceRequirements:
    """Test suite for critical trace requirements"""

    @pytest.fixture
    async def organization(self, db_session):
        """Create test organization"""
        org = Organization(
            id=uuid.uuid4(),
            name="Test Organization",
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)
        return org

    @pytest.fixture
    async def user(self, db_session, organization):
        """Create test user"""
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            organization_id=organization.id,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    def trace_service(self, db_session):
        """Create trace service instance"""
        return TraceService(db_session)

    # =====================================================
    # REQUIREMENT 1: ALL model invocations MUST be traced
    # =====================================================

    @pytest.mark.asyncio
    async def test_successful_invocation_creates_trace(
        self, db_session, trace_service, user
    ):
        """Test that successful model invocation creates a trace"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test prompt",
            output_response="Test response",
            latency_ms=150.5,
            tokens_used=100,
            cost=0.001,
            input_tokens=50,
            output_tokens=50,
        )

        # Verify trace was created
        assert trace is not None
        assert trace.trace_id == trace_id
        assert trace.status == "success"
        assert trace.total_duration_ms == 150.5

    @pytest.mark.asyncio
    async def test_failed_invocation_creates_trace(
        self, db_session, trace_service, user
    ):
        """Test that FAILED model invocation ALSO creates a trace"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test prompt",
            output_response="",  # No response on error
            latency_ms=50.0,  # Still track duration
            tokens_used=0,  # No tokens on error
            cost=0.0,  # No cost on error
            status="error",
            error_message="API rate limit exceeded",
            error_type="RateLimitError",
        )

        # Verify error trace was created
        assert trace is not None
        assert trace.status == "error"
        assert trace.error_message == "API rate limit exceeded"
        assert trace.error_type == "RateLimitError"
        assert trace.total_duration_ms == 50.0  # Duration tracked even on error

    # =====================================================
    # REQUIREMENT 2: ALL traces MUST have duration
    # =====================================================

    @pytest.mark.asyncio
    async def test_trace_has_nonzero_duration(self, db_session, trace_service, user):
        """Test that trace duration is never zero for actual invocations"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="Response",
            latency_ms=1.0,  # Even 1ms is tracked
            tokens_used=10,
            cost=0.0001,
        )

        assert trace.total_duration_ms > 0
        assert trace.total_duration_ms is not None

    @pytest.mark.asyncio
    async def test_child_trace_has_duration(
        self, db_session, trace_service, user, organization
    ):
        """Test that CHILD traces also have duration (not hardcoded to 0)"""
        # Create parent trace
        parent_trace_id = str(uuid.uuid4())
        await trace_service.create_trace(
            trace_id=parent_trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Parent",
            output_response="Parent response",
            latency_ms=1000.0,
            tokens_used=200,
            cost=0.002,
        )

        # Create child trace with parent reference
        child_trace_id = str(uuid.uuid4())
        child_trace = await trace_service.create_trace(
            trace_id=child_trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Child",
            output_response="Child response",
            latency_ms=250.0,  # MUST NOT be 0
            tokens_used=50,
            cost=0.0005,
            metadata={"parent_trace_id": parent_trace_id, "stage": "Stage 1"},
        )

        # CRITICAL: Child trace MUST have duration tracked
        assert child_trace.total_duration_ms == 250.0
        assert child_trace.total_duration_ms > 0

    # =====================================================
    # REQUIREMENT 3: ALL traces MUST have token counts
    # =====================================================

    @pytest.mark.asyncio
    async def test_trace_has_token_counts(self, db_session, trace_service, user):
        """Test that trace captures input, output, and total tokens"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test prompt",
            output_response="Test response",
            latency_ms=150.0,
            tokens_used=100,
            cost=0.001,
            input_tokens=60,
            output_tokens=40,
        )

        assert trace.input_tokens == 60
        assert trace.output_tokens == 40
        assert trace.total_tokens == 100

    # =====================================================
    # REQUIREMENT 4: ALL traces MUST have cost
    # =====================================================

    @pytest.mark.asyncio
    async def test_trace_has_cost(self, db_session, trace_service, user):
        """Test that trace calculates and stores cost"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="Response",
            latency_ms=100.0,
            tokens_used=100,
            cost=0.00125,  # Must track cost
        )

        assert trace.total_cost == 0.00125
        assert trace.total_cost >= 0

    # =====================================================
    # REQUIREMENT 5: Failures MUST capture error details
    # =====================================================

    @pytest.mark.asyncio
    async def test_error_trace_captures_failure_reason(
        self, db_session, trace_service, user
    ):
        """Test that error traces capture detailed failure information"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="",
            latency_ms=25.0,
            tokens_used=0,
            cost=0.0,
            status="error",
            error_message="Authentication failed: Invalid API key",
            error_type="AuthenticationError",
        )

        assert trace.status == "error"
        assert trace.error_message == "Authentication failed: Invalid API key"
        assert trace.error_type == "AuthenticationError"
        assert "Invalid API key" in trace.error_message

    # =====================================================
    # REQUIREMENT 6: Model-neutral trace system
    # =====================================================

    @pytest.mark.asyncio
    async def test_trace_works_with_openai(self, db_session, trace_service, user):
        """Test that trace works with OpenAI models"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="Response",
            latency_ms=120.0,
            tokens_used=80,
            cost=0.0008,
        )

        assert trace.model_name == "gpt-4o-mini"
        assert trace.total_duration_ms == 120.0

    @pytest.mark.asyncio
    async def test_trace_works_with_claude(self, db_session, trace_service, user):
        """Test that trace works with Claude/Anthropic models"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="claude-3-5-sonnet-20241022",
            input_prompt="Test",
            output_response="Response",
            latency_ms=200.0,
            tokens_used=100,
            cost=0.0015,
        )

        assert trace.model_name == "claude-3-5-sonnet-20241022"
        assert trace.total_duration_ms == 200.0

    # =====================================================
    # INTEGRATION: Call Insights Service
    # =====================================================

    @pytest.mark.asyncio
    async def test_call_insights_creates_traces_with_duration(
        self, db_session, user, organization
    ):
        """Test that Call Insights creates child traces with duration"""
        with patch.object(
            ModelProviderService, "execute"
        ) as mock_execute:
            # Mock model execution result
            mock_execute.return_value = ModelExecutionResult(
                response="Test response",
                input_tokens=100,
                output_tokens=50,
                tokens_used=150,
                cost=0.001,
                provider_duration_ms=125.5,  # Provider reported duration
                total_duration_ms=150.0,  # Total duration including overhead
            )

            # Create service
            insights_service = CallInsightsService(
                db=db_session, organization_id=str(organization.id)
            )

            # Execute analysis (will create child traces)
            result = await insights_service.analyze_transcript(
                transcript="Customer: I need help. Agent: Sure, how can I help?",
                user_id=str(user.id),
                project_id=None,
            )

            # Query all child traces
            from sqlalchemy import select
            from app.models.trace import Trace

            stmt = select(Trace).where(
                Trace.trace_metadata.op("->>")(
                    "parent_trace_id"
                )
                == result["parent_trace_id"]
            )
            db_result = await db_session.execute(stmt)
            child_traces = db_result.scalars().all()

            # CRITICAL VALIDATION: All child traces MUST have duration
            for child_trace in child_traces:
                assert (
                    child_trace.total_duration_ms is not None
                ), f"Child trace {child_trace.trace_id} missing duration"
                assert (
                    child_trace.total_duration_ms > 0
                ), f"Child trace {child_trace.trace_id} has zero duration"
                assert (
                    child_trace.input_tokens is not None
                ), f"Child trace {child_trace.trace_id} missing input_tokens"
                assert (
                    child_trace.output_tokens is not None
                ), f"Child trace {child_trace.trace_id} missing output_tokens"
                assert (
                    child_trace.total_cost >= 0
                ), f"Child trace {child_trace.trace_id} missing cost"

    # =====================================================
    # ACCOUNTING VALIDATION
    # =====================================================

    @pytest.mark.asyncio
    async def test_no_trace_is_missing_critical_fields(
        self, db_session, trace_service, user
    ):
        """Test that ALL traces have required fields for billing"""
        required_fields = [
            "trace_id",
            "model_name",
            "total_duration_ms",
            "total_tokens",
            "total_cost",
            "status",
        ]

        trace_id = str(uuid.uuid4())
        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="Response",
            latency_ms=100.0,
            tokens_used=50,
            cost=0.0005,
        )

        # Validate all required fields are present
        for field in required_fields:
            value = getattr(trace, field)
            assert (
                value is not None
            ), f"CRITICAL: Trace missing required field '{field}'"

    @pytest.mark.asyncio
    async def test_failed_trace_still_has_accounting_fields(
        self, db_session, trace_service, user
    ):
        """Test that even FAILED traces have accounting fields"""
        trace_id = str(uuid.uuid4())

        trace = await trace_service.create_trace(
            trace_id=trace_id,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            model="gpt-4o-mini",
            input_prompt="Test",
            output_response="",
            latency_ms=75.0,  # Duration tracked even on failure
            tokens_used=0,  # No tokens on error
            cost=0.0,  # No cost on error
            status="error",
            error_message="Timeout",
            error_type="TimeoutError",
        )

        # Even failed traces must have these fields
        assert trace.trace_id is not None
        assert trace.model_name is not None
        assert trace.total_duration_ms == 75.0  # Duration MUST be tracked
        assert trace.total_tokens == 0
        assert trace.total_cost == 0.0
        assert trace.status == "error"
        assert trace.error_message is not None
        assert trace.error_type is not None
