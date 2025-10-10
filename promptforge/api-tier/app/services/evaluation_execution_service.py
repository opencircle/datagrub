"""
Evaluation Execution Service - Executes evaluations on traces

This service orchestrates the execution of evaluations on traces, managing:
- Fetching trace data
- Running evaluations via adapters
- Creating child traces for evaluation execution
- Storing results in trace_evaluations table
"""
import logging
import time
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.trace import Trace
from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation
from app.evaluations.registry import registry
from app.evaluations.base import EvaluationRequest, EvaluationResult

logger = logging.getLogger(__name__)


class EvaluationExecutionService:
    """Service for executing evaluations on traces"""

    def __init__(self, db: AsyncSession, organization_id: UUID):
        """
        Initialize the evaluation execution service

        Args:
            db: Database session
            organization_id: Organization context for the execution
        """
        self.db = db
        self.organization_id = organization_id
        self.evaluation_registry = registry

    async def run_evaluations(
        self,
        evaluation_ids: List[UUID],
        trace_id: UUID,
        user_id: UUID,
        model_override: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute evaluations on a trace

        Flow:
        1. Fetch trace input/output from database
        2. For each evaluation:
           - Load definition from catalog
           - Execute via appropriate adapter (PromptForge/Vendor/Custom)
           - Create child trace for evaluation execution
           - Store result in trace_evaluations table
        3. Return results

        Args:
            evaluation_ids: List of evaluation catalog IDs to execute
            trace_id: ID of the trace to evaluate
            user_id: ID of the user executing the evaluations
            model_override: Optional model override for execution

        Returns:
            List of evaluation results
        """
        # Fetch original trace
        trace_query = select(Trace).where(Trace.id == trace_id)
        trace_result = await self.db.execute(trace_query)
        trace = trace_result.scalar_one_or_none()

        if not trace:
            raise ValueError(f"Trace not found: {trace_id}")

        # Extract input/output data from trace
        input_data = trace.input_data or {}
        output_data = trace.output_data or {}

        # Results list
        results = []

        for evaluation_id in evaluation_ids:
            start_time = time.time()

            try:
                # Load evaluation definition from catalog
                eval_query = select(EvaluationCatalog).where(
                    EvaluationCatalog.id == evaluation_id
                )
                eval_result = await self.db.execute(eval_query)
                evaluation = eval_result.scalar_one_or_none()

                if not evaluation:
                    logger.error(f"Evaluation not found: {evaluation_id}")
                    results.append({
                        "evaluation_id": evaluation_id,
                        "evaluation_name": "Unknown",
                        "trace_id": trace_id,
                        "score": None,
                        "passed": False,
                        "reason": "Evaluation not found",
                        "metadata": {},
                        "status": "failed",
                        "error_message": f"Evaluation {evaluation_id} not found",
                    })
                    continue

                # Check access (organization-scoped)
                if not evaluation.is_public and evaluation.organization_id != self.organization_id:
                    logger.error(f"Access denied to evaluation: {evaluation_id}")
                    results.append({
                        "evaluation_id": evaluation_id,
                        "evaluation_name": evaluation.name,
                        "trace_id": trace_id,
                        "score": None,
                        "passed": False,
                        "reason": "Access denied",
                        "metadata": {},
                        "status": "failed",
                        "error_message": "Access denied to this evaluation",
                    })
                    continue

                # Build evaluation request
                eval_request = EvaluationRequest(
                    trace_id=trace_id,
                    input_data=input_data,
                    output_data=output_data,
                    metadata={
                        "organization_id": str(self.organization_id),
                        "project_id": str(trace.project_id) if trace.project_id else None,
                        "original_trace_id": str(trace_id),
                    },
                    trace_metadata={
                        "total_duration_ms": trace.total_duration_ms,
                        "total_tokens": trace.total_tokens,
                        "total_cost": trace.total_cost,
                        "model": trace.model_name,
                    },
                    config=evaluation.default_config or {},
                )

                # Execute evaluation via appropriate adapter
                eval_result = await self._execute_evaluation(
                    evaluation=evaluation,
                    request=eval_request,
                    model_override=model_override,
                )

                # Create child trace for evaluation execution
                child_trace = await self._create_evaluation_trace(
                    parent_trace=trace,
                    evaluation=evaluation,
                    eval_result=eval_result,
                    user_id=user_id,
                )

                # Store result in trace_evaluations table
                trace_evaluation = TraceEvaluation(
                    trace_id=trace_id,
                    evaluation_catalog_id=evaluation_id,
                    organization_id=self.organization_id,  # Required for multi-tenant isolation
                    score=eval_result.score,
                    passed=eval_result.passed,
                    category=eval_result.category,
                    reason=eval_result.reason,
                    details=eval_result.details,
                    suggestions=eval_result.suggestions,
                    execution_time_ms=eval_result.execution_time_ms,
                    model_used=eval_result.model_used or model_override,
                    config=eval_request.config,
                    input_tokens=eval_result.input_tokens,
                    output_tokens=eval_result.output_tokens,
                    total_tokens=eval_result.total_tokens,
                    evaluation_cost=eval_result.evaluation_cost,
                    vendor_metrics=eval_result.vendor_metrics,
                    llm_metadata=eval_result.llm_metadata,
                    status=eval_result.status,
                    error_message=eval_result.error,
                )

                self.db.add(trace_evaluation)
                await self.db.flush()

                # Build result
                duration_ms = (time.time() - start_time) * 1000
                results.append({
                    "evaluation_id": evaluation_id,
                    "evaluation_name": evaluation.name,
                    "trace_id": child_trace.id,
                    "score": eval_result.score,
                    "passed": eval_result.passed,
                    "reason": eval_result.reason,
                    "metadata": {
                        "model": eval_result.model_used or model_override or trace.model_name,
                        "tokens": eval_result.total_tokens or 0,
                        "cost": eval_result.evaluation_cost or 0.0,
                        "duration_ms": duration_ms,
                    },
                    "status": eval_result.status,
                    "error_message": eval_result.error,
                })

            except Exception as e:
                logger.error(f"Error executing evaluation {evaluation_id}: {e}")
                duration_ms = (time.time() - start_time) * 1000
                results.append({
                    "evaluation_id": evaluation_id,
                    "evaluation_name": "Unknown",
                    "trace_id": trace_id,
                    "score": None,
                    "passed": False,
                    "reason": str(e),
                    "metadata": {"duration_ms": duration_ms},
                    "status": "failed",
                    "error_message": str(e),
                })

        # Commit all results
        await self.db.commit()

        return results

    async def _execute_evaluation(
        self,
        evaluation: EvaluationCatalog,
        request: EvaluationRequest,
        model_override: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Execute evaluation via appropriate adapter

        Args:
            evaluation: Evaluation catalog entry
            request: Evaluation request
            model_override: Optional model override

        Returns:
            Evaluation result
        """
        # Execute via registry
        try:
            result = await self.evaluation_registry.execute_evaluation(
                evaluation_uuid=str(evaluation.id),
                request=request,
                adapter_class=evaluation.adapter_class,
                source=evaluation.source,
            )
            return result
        except Exception as e:
            logger.error(f"Error executing evaluation {evaluation.id}: {e}")
            return EvaluationResult(
                status="failed",
                error=str(e),
            )

    async def _create_evaluation_trace(
        self,
        parent_trace: Trace,
        evaluation: EvaluationCatalog,
        eval_result: EvaluationResult,
        user_id: UUID,
    ) -> Trace:
        """
        Create child trace for evaluation execution

        Args:
            parent_trace: Parent trace being evaluated
            evaluation: Evaluation catalog entry
            eval_result: Evaluation result
            user_id: User executing the evaluation

        Returns:
            Created trace
        """
        # Create child trace
        child_trace = Trace(
            name=f"Evaluation: {evaluation.name}",
            status="success" if eval_result.status == "completed" else "error",
            project_id=parent_trace.project_id,
            user_id=user_id,
            model_name=eval_result.model_used or parent_trace.model_name,
            input_data={
                "evaluation_id": str(evaluation.id),
                "evaluation_name": evaluation.name,
                "evaluation_type": evaluation.evaluation_type.value if evaluation.evaluation_type else None,
                "trace_input": parent_trace.input_data,
                "trace_output": parent_trace.output_data,
            },
            output_data={
                "score": eval_result.score,
                "passed": eval_result.passed,
                "category": eval_result.category,
                "reason": eval_result.reason,
                "details": eval_result.details,
                "suggestions": eval_result.suggestions,
            },
            trace_metadata={
                "evaluation_id": str(evaluation.id),
                "evaluation_source": evaluation.source.value if evaluation.source else None,
                "parent_trace_id": str(parent_trace.id),
            },
            total_duration_ms=eval_result.execution_time_ms or 0,
            input_tokens=eval_result.input_tokens,
            output_tokens=eval_result.output_tokens,
            total_tokens=eval_result.total_tokens,
            total_cost=eval_result.evaluation_cost or 0.0,
            environment=parent_trace.environment,
        )

        self.db.add(child_trace)
        await self.db.flush()
        await self.db.refresh(child_trace)

        return child_trace
