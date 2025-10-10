"""
PromptForge Adapter - Proprietary platform evaluations

This adapter provides PromptForge's value-added evaluation metrics.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import time
import logging

from app.models.evaluation_catalog import EvaluationSource, EvaluationType, EvaluationCategory
from app.evaluations.base import (
    EvaluationAdapter,
    EvaluationRequest,
    EvaluationResult,
    EvaluationMetadata,
)

logger = logging.getLogger(__name__)


class PromptForgeAdapter(EvaluationAdapter):
    """
    PromptForge proprietary evaluation adapter

    Provides platform-specific evaluations that add value beyond
    standard vendor evaluations.
    """

    # Define PromptForge evaluations
    EVALUATIONS = [
        {
            "uuid": "pf-prompt-quality-score",
            "name": "Prompt Quality Score",
            "description": "Comprehensive quality assessment of prompt engineering best practices",
            "category": EvaluationCategory.QUALITY,
            "evaluation_type": EvaluationType.METRIC,
            "config_schema": {},
            "default_config": {},
            "version": "1.0.0",
            "tags": ["quality", "prompt", "best-practices"],
        },
        {
            "uuid": "pf-cost-efficiency",
            "name": "Cost Efficiency Score",
            "description": "Evaluates the cost-effectiveness of the LLM interaction",
            "category": EvaluationCategory.PERFORMANCE,
            "evaluation_type": EvaluationType.METRIC,
            "config_schema": {
                "target_cost_per_token": {"type": "float", "description": "Target cost per token"}
            },
            "default_config": {"target_cost_per_token": 0.00001},
            "version": "1.0.0",
            "tags": ["cost", "efficiency", "performance"],
        },
        {
            "uuid": "pf-response-completeness",
            "name": "Response Completeness",
            "description": "Checks if the response fully addresses all aspects of the input",
            "category": EvaluationCategory.QUALITY,
            "evaluation_type": EvaluationType.METRIC,
            "config_schema": {},
            "default_config": {},
            "version": "1.0.0",
            "tags": ["quality", "completeness"],
        },
        {
            "uuid": "pf-latency-budget",
            "name": "Latency Budget Validator",
            "description": "Validates that response latency is within acceptable bounds",
            "category": EvaluationCategory.PERFORMANCE,
            "evaluation_type": EvaluationType.VALIDATOR,
            "config_schema": {
                "max_latency_ms": {"type": "float", "description": "Maximum allowed latency in milliseconds"}
            },
            "default_config": {"max_latency_ms": 5000},
            "version": "1.0.0",
            "tags": ["performance", "latency"],
        },
        {
            "uuid": "pf-output-consistency",
            "name": "Output Consistency Checker",
            "description": "Validates that output format matches expected structure",
            "category": EvaluationCategory.QUALITY,
            "evaluation_type": EvaluationType.VALIDATOR,
            "config_schema": {
                "expected_format": {"type": "string", "description": "Expected output format (json, text, etc.)"}
            },
            "default_config": {"expected_format": "json"},
            "version": "1.0.0",
            "tags": ["quality", "consistency", "format"],
        },
        {
            "uuid": "pf-token-efficiency",
            "name": "Token Efficiency Score",
            "description": "Measures how efficiently tokens are used relative to output value",
            "category": EvaluationCategory.PERFORMANCE,
            "evaluation_type": EvaluationType.METRIC,
            "config_schema": {},
            "default_config": {},
            "version": "1.0.0",
            "tags": ["performance", "tokens", "efficiency"],
        },
    ]

    def __init__(self):
        """Initialize the PromptForge adapter"""
        super().__init__(EvaluationSource.PROMPTFORGE)
        self._evaluations = {eval["uuid"]: eval for eval in self.EVALUATIONS}
        logger.info("Initialized PromptForgeAdapter with %d evaluations", len(self._evaluations))

    async def list_evaluations(
        self,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> List[EvaluationMetadata]:
        """
        List all PromptForge evaluations

        All PromptForge evaluations are public and available to all organizations.

        Args:
            organization_id: Ignored (all evaluations are public)
            project_id: Ignored (all evaluations are public)

        Returns:
            List of PromptForge evaluation metadata
        """
        return [
            EvaluationMetadata(
                uuid=eval["uuid"],
                name=eval["name"],
                description=eval["description"],
                source=EvaluationSource.PROMPTFORGE,
                evaluation_type=eval["evaluation_type"],
                category=eval["category"],
                config_schema=eval.get("config_schema"),
                default_config=eval.get("default_config"),
                is_public=True,
                version=eval.get("version", "1.0.0"),
                tags=eval.get("tags"),
            )
            for eval in self.EVALUATIONS
        ]

    async def get_evaluation(self, evaluation_uuid: str) -> Optional[EvaluationMetadata]:
        """
        Get metadata for a specific PromptForge evaluation

        Args:
            evaluation_uuid: Unique identifier

        Returns:
            Evaluation metadata or None
        """
        eval_def = self._evaluations.get(evaluation_uuid)
        if not eval_def:
            return None

        return EvaluationMetadata(
            uuid=eval_def["uuid"],
            name=eval_def["name"],
            description=eval_def["description"],
            source=EvaluationSource.PROMPTFORGE,
            evaluation_type=eval_def["evaluation_type"],
            category=eval_def["category"],
            config_schema=eval_def.get("config_schema"),
            default_config=eval_def.get("default_config"),
            is_public=True,
            version=eval_def.get("version", "1.0.0"),
            tags=eval_def.get("tags"),
        )

    async def execute(
        self,
        evaluation_uuid: str,
        request: EvaluationRequest
    ) -> EvaluationResult:
        """
        Execute a PromptForge evaluation

        Args:
            evaluation_uuid: Evaluation identifier
            request: Evaluation request

        Returns:
            Evaluation result
        """
        start_time = time.time()

        eval_def = self._evaluations.get(evaluation_uuid)
        if not eval_def:
            return EvaluationResult(
                status="failed",
                error=f"Unknown PromptForge evaluation: {evaluation_uuid}"
            )

        try:
            # Route to specific evaluation implementation
            if evaluation_uuid == "pf-prompt-quality-score":
                result = await self._evaluate_prompt_quality(request)
            elif evaluation_uuid == "pf-cost-efficiency":
                result = await self._evaluate_cost_efficiency(request)
            elif evaluation_uuid == "pf-response-completeness":
                result = await self._evaluate_completeness(request)
            elif evaluation_uuid == "pf-latency-budget":
                result = await self._validate_latency(request)
            elif evaluation_uuid == "pf-output-consistency":
                result = await self._validate_output_consistency(request)
            elif evaluation_uuid == "pf-token-efficiency":
                result = await self._evaluate_token_efficiency(request)
            else:
                result = EvaluationResult(
                    status="failed",
                    error=f"Implementation not found for: {evaluation_uuid}"
                )

            # Add execution time
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time

            return result

        except Exception as e:
            logger.error(f"Error executing {evaluation_uuid}: {e}")
            return EvaluationResult(
                status="failed",
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )

    async def validate_config(
        self,
        evaluation_uuid: str,
        config: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate configuration for a PromptForge evaluation

        Args:
            evaluation_uuid: Evaluation identifier
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        eval_def = self._evaluations.get(evaluation_uuid)
        if not eval_def:
            return False, f"Unknown evaluation: {evaluation_uuid}"

        config_schema = eval_def.get("config_schema", {})

        # Simple validation - check required fields
        for field, spec in config_schema.items():
            if field not in config:
                return False, f"Missing required field: {field}"

            # Basic type checking
            expected_type = spec.get("type")
            if expected_type == "float" and not isinstance(config[field], (int, float)):
                return False, f"Field {field} must be a number"
            if expected_type == "string" and not isinstance(config[field], str):
                return False, f"Field {field} must be a string"

        return True, None

    # ==================== Evaluation Implementations ====================

    async def _evaluate_prompt_quality(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Evaluate prompt quality based on best practices

        Checks for:
        - Clear instructions
        - Appropriate context
        - Well-formed structure
        """
        input_str = str(request.input_data.get("prompt", ""))
        score = 0.0
        details = {}
        suggestions = []

        # Check length (not too short, not too long)
        if len(input_str) < 20:
            suggestions.append("Prompt is very short. Consider adding more context or instructions.")
        elif len(input_str) > 2000:
            suggestions.append("Prompt is very long. Consider condensing to key information.")
        else:
            score += 0.25

        # Check for instruction keywords
        instruction_keywords = ["create", "generate", "write", "explain", "summarize", "analyze"]
        if any(keyword in input_str.lower() for keyword in instruction_keywords):
            score += 0.25
        else:
            suggestions.append("Consider adding clear action verbs (create, generate, explain, etc.)")

        # Check for context markers
        if "context:" in input_str.lower() or "background:" in input_str.lower():
            score += 0.25
        else:
            suggestions.append("Consider adding explicit context section")

        # Check for output format specification
        if "format:" in input_str.lower() or "output:" in input_str.lower():
            score += 0.25
        else:
            suggestions.append("Consider specifying desired output format")

        details["prompt_length"] = len(input_str)
        details["has_clear_instructions"] = score >= 0.25
        details["has_context"] = score >= 0.5
        details["has_format_spec"] = score >= 0.75

        # Threshold: pass if score >= 0.5
        passed = score >= 0.5

        return EvaluationResult(
            score=score,
            passed=passed,
            reason=f"Prompt quality score based on best practices analysis",
            details=details,
            suggestions=suggestions if suggestions else None
        )

    async def _evaluate_cost_efficiency(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate cost efficiency of the LLM interaction"""
        metadata = request.trace_metadata or {}
        total_tokens = metadata.get("total_tokens", 0)
        total_cost = metadata.get("total_cost", 0)

        if total_tokens == 0:
            return EvaluationResult(
                score=0.0,
                reason="No token usage data available",
                details={"error": "Missing token count"}
            )

        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0
        target_cost = request.config.get("target_cost_per_token", 0.00001)

        # Score: 1.0 if at or below target, decreases as cost increases
        if cost_per_token <= target_cost:
            score = 1.0
        else:
            score = max(0.0, 1.0 - ((cost_per_token - target_cost) / target_cost))

        return EvaluationResult(
            score=score,
            reason=f"Cost per token: ${cost_per_token:.6f} (target: ${target_cost:.6f})",
            details={
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "cost_per_token": cost_per_token,
                "target_cost_per_token": target_cost
            }
        )

    async def _evaluate_completeness(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate if response fully addresses the input"""
        output_str = str(request.output_data.get("response", ""))

        # Simple heuristics for completeness
        score = 0.0
        suggestions = []

        # Check output length
        if len(output_str) < 50:
            suggestions.append("Response is very short - may not be complete")
        else:
            score += 0.5

        # Check for common incompleteness indicators
        incomplete_markers = ["...", "to be continued", "incomplete", "truncated"]
        if not any(marker in output_str.lower() for marker in incomplete_markers):
            score += 0.5
        else:
            suggestions.append("Response appears to be incomplete or truncated")

        return EvaluationResult(
            score=score,
            reason="Completeness based on output analysis",
            details={"output_length": len(output_str)},
            suggestions=suggestions if suggestions else None
        )

    async def _validate_latency(self, request: EvaluationRequest) -> EvaluationResult:
        """Validate that latency is within budget"""
        metadata = request.trace_metadata or {}
        actual_latency = metadata.get("total_duration_ms", 0)
        max_latency = request.config.get("max_latency_ms", 5000)

        passed = actual_latency <= max_latency

        return EvaluationResult(
            passed=passed,
            reason=f"Latency: {actual_latency}ms (max: {max_latency}ms)",
            details={
                "actual_latency_ms": actual_latency,
                "max_latency_ms": max_latency,
                "within_budget": passed
            },
            suggestions=["Consider optimizing prompt or using faster model"] if not passed else None
        )

    async def _validate_output_consistency(self, request: EvaluationRequest) -> EvaluationResult:
        """Validate output format consistency"""
        output = request.output_data.get("response", "")
        expected_format = request.config.get("expected_format", "json")

        passed = False
        reason = ""

        if expected_format == "json":
            import json
            try:
                json.loads(str(output))
                passed = True
                reason = "Output is valid JSON"
            except json.JSONDecodeError:
                reason = "Output is not valid JSON"
        else:
            # For non-JSON, just check it's a string
            passed = isinstance(output, str) and len(output) > 0
            reason = f"Output format check for {expected_format}"

        return EvaluationResult(
            passed=passed,
            reason=reason,
            details={"expected_format": expected_format, "actual_type": type(output).__name__}
        )

    async def _evaluate_token_efficiency(self, request: EvaluationRequest) -> EvaluationResult:
        """Evaluate token usage efficiency"""
        metadata = request.trace_metadata or {}
        total_tokens = metadata.get("total_tokens", 0)
        output_str = str(request.output_data.get("response", ""))
        output_length = len(output_str)

        if output_length == 0:
            return EvaluationResult(score=0.0, reason="No output generated")

        # Rough heuristic: ~4 chars per token is efficient
        expected_tokens = output_length / 4
        if total_tokens == 0:
            score = 0.0
        else:
            score = min(1.0, expected_tokens / total_tokens)

        return EvaluationResult(
            score=score,
            reason=f"Token efficiency based on output length",
            details={
                "total_tokens": total_tokens,
                "output_length": output_length,
                "chars_per_token": output_length / total_tokens if total_tokens > 0 else 0
            }
        )
