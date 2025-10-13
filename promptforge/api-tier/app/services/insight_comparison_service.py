"""
Insight Comparison Service - Blind comparison of two Call Insights analyses using judge model

Implements:
- Blind evaluation (judge sees "Response A" and "Response B" without model identifiers)
- Per-stage comparison (Stage 1: Facts, Stage 2: Insights, Stage 3: Summary)
- Overall verdict with cost-benefit analysis
- Comprehensive tracing for judge model invocations
- Organization-scoped RBAC
"""

import time
import uuid
import json
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.model_provider import ModelProviderService, ModelExecutionRequest
from app.services.trace_service import TraceService
from app.models.call_insights import CallInsightsAnalysis
from app.models.insight_comparison import InsightComparison
from app.prompts.judge_comparison_prompts import (
    STAGE1_COMPARISON_PROMPT,
    STAGE2_COMPARISON_PROMPT,
    STAGE3_COMPARISON_PROMPT,
    OVERALL_VERDICT_PROMPT,
)


class InsightComparisonService:
    """Service for comparing two Call Insights analyses with a judge model"""

    def __init__(self, db: AsyncSession, organization_id: str):
        self.db = db
        self.organization_id = organization_id
        self.model_service = ModelProviderService(db, organization_id)
        self.trace_service = TraceService(db)

    async def create_comparison(
        self,
        analysis_a_id: str,
        analysis_b_id: str,
        user_id: str,
        judge_model: str = "claude-sonnet-4-5-20250929",
        judge_temperature: float = 0.0,
        judge_reasoning_effort: Optional[str] = "medium",  # GPT-5 only: minimal, low, medium (default), high
        evaluation_criteria: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare two analyses using a judge model

        Args:
            analysis_a_id: UUID of first analysis
            analysis_b_id: UUID of second analysis
            user_id: User requesting comparison
            judge_model: Exact model API version (e.g., "claude-sonnet-4-5-20250929", "gpt-4o", "gpt-5")
            judge_temperature: Temperature for judge model (default: 0.0 for deterministic evaluation)
                              - 0.0 = Fully deterministic, consistent evaluations (recommended for A/B testing)
                              - 0.3-0.5 = Slightly varied responses, more nuanced reasoning
                              - 0.7-1.0 = More creative/varied, less consistent (not recommended)
                              - NOTE: GPT-5 models only support temperature=1.0 (enforced automatically)
            judge_reasoning_effort: GPT-5 only - controls thinking time (default: "medium")
                              - "minimal" = Fast responses, minimal reasoning (extraction, formatting, classification)
                              - "low" = Faster with less thinking
                              - "medium" = Balanced reasoning (RECOMMENDED for comparisons)
                              - "high" = Maximum quality with extended reasoning (complex analysis)
            evaluation_criteria: Criteria to evaluate (default: all 5)

        Returns:
            Dict containing:
            - comparison_id: UUID of saved comparison
            - overall_winner: 'A', 'B', or 'tie'
            - overall_reasoning: Judge's reasoning with cost-benefit analysis
            - stage_results: List of per-stage results
            - judge_trace: Judge model invocation metadata

        Raises:
            ValueError: If analyses don't exist, belong to different orgs, or have different transcripts
        """
        comparison_start_time = time.time()

        # Default evaluation criteria
        if not evaluation_criteria:
            evaluation_criteria = ["groundedness", "faithfulness", "completeness", "clarity", "accuracy"]

        # Use judge_model directly (already exact API version from UI)
        judge_model_version = judge_model

        # Validate and retrieve analyses (includes duplicate comparison check)
        analysis_a, analysis_b = await self._validate_analyses(
            analysis_a_id,
            analysis_b_id,
            judge_model=judge_model_version
        )

        # Create judge trace to track this comparison
        judge_trace_id = str(uuid.uuid4())
        total_tokens = 0
        total_cost = 0.0

        # Stage 1: Compare Fact Extraction
        stage1_result = await self._evaluate_stage(
            stage_name="Stage 1: Fact Extraction",
            prompt_template=STAGE1_COMPARISON_PROMPT,
            transcript=analysis_a.transcript_input,
            response_a=analysis_a.facts_output,
            response_b=analysis_b.facts_output,
            judge_model=judge_model_version,
            judge_trace_id=judge_trace_id,
            user_id=user_id,
            temperature=judge_temperature,
            reasoning_effort=judge_reasoning_effort,
        )
        total_tokens += stage1_result["tokens_used"]
        total_cost += stage1_result["cost"]

        # Stage 2: Compare Reasoning & Insights
        stage2_result = await self._evaluate_stage(
            stage_name="Stage 2: Reasoning & Insights",
            prompt_template=STAGE2_COMPARISON_PROMPT,
            transcript=analysis_a.transcript_input,
            response_a=analysis_a.insights_output,
            response_b=analysis_b.insights_output,
            judge_model=judge_model_version,
            judge_trace_id=judge_trace_id,
            user_id=user_id,
            temperature=judge_temperature,
            reasoning_effort=judge_reasoning_effort,
            stage1_output=analysis_a.facts_output,  # Pass Stage 1 output for context
        )
        total_tokens += stage2_result["tokens_used"]
        total_cost += stage2_result["cost"]

        # Stage 3: Compare Summary
        stage3_result = await self._evaluate_stage(
            stage_name="Stage 3: Summary",
            prompt_template=STAGE3_COMPARISON_PROMPT,
            transcript=analysis_a.transcript_input,
            response_a=analysis_a.summary_output,
            response_b=analysis_b.summary_output,
            judge_model=judge_model_version,
            judge_trace_id=judge_trace_id,
            user_id=user_id,
            temperature=judge_temperature,
            reasoning_effort=judge_reasoning_effort,
            stage1_output=analysis_a.facts_output,
            stage2_output=analysis_a.insights_output,
        )
        total_tokens += stage3_result["tokens_used"]
        total_cost += stage3_result["cost"]

        # Extract model parameters from analyses
        params_a = await self._get_model_parameters(analysis_a)
        params_b = await self._get_model_parameters(analysis_b)

        # Calculate overall winner with cost-benefit analysis
        overall_result = await self._calculate_overall_winner(
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            stage3_result=stage3_result,
            cost_a=analysis_a.total_cost,
            cost_b=analysis_b.total_cost,
            tokens_a=analysis_a.total_tokens,
            tokens_b=analysis_b.total_tokens,
            model_a_name=self._get_model_summary(analysis_a),
            model_b_name=self._get_model_summary(analysis_b),
            params_a=params_a,
            params_b=params_b,
            judge_model=judge_model_version,
            judge_trace_id=judge_trace_id,
            user_id=user_id,
            temperature=judge_temperature,
            reasoning_effort=judge_reasoning_effort,
        )
        total_tokens += overall_result["tokens_used"]
        total_cost += overall_result["cost"]

        # Calculate total comparison duration
        total_duration_ms = (time.time() - comparison_start_time) * 1000

        # Create parent trace for the entire comparison
        parent_trace = await self.trace_service.create_trace(
            trace_id=judge_trace_id,
            user_id=user_id,
            organization_id=self.organization_id,
            model=judge_model_version,  # Use exact version for trace
            input_prompt=f"Comparison: {analysis_a_id} vs {analysis_b_id}",
            output_response=overall_result["reasoning"][:1000],
            latency_ms=total_duration_ms,
            tokens_used=total_tokens,
            cost=total_cost,
            input_tokens=sum([
                stage1_result.get("input_tokens", 0),
                stage2_result.get("input_tokens", 0),
                stage3_result.get("input_tokens", 0),
                overall_result.get("input_tokens", 0),
            ]),
            output_tokens=sum([
                stage1_result.get("output_tokens", 0),
                stage2_result.get("output_tokens", 0),
                stage3_result.get("output_tokens", 0),
                overall_result.get("output_tokens", 0),
            ]),
            parameters={
                "judge_model": judge_model,
                "evaluation_criteria": evaluation_criteria,
            },
            metadata={
                "source": "insight_comparison",
                "analysis_a_id": analysis_a_id,
                "analysis_b_id": analysis_b_id,
                "overall_winner": overall_result["winner"],
            },
            title=f"Insight Comparison: {analysis_a.transcript_title or 'Untitled'}",
        )

        # Save comparison to database
        comparison = InsightComparison(
            organization_id=self.organization_id,
            user_id=user_id,
            analysis_a_id=analysis_a.id,
            analysis_b_id=analysis_b.id,
            judge_model=judge_model,  # Exact API version (same as judge_model_version)
            judge_model_version=judge_model_version,  # Exact API version
            evaluation_criteria=evaluation_criteria,
            overall_winner=overall_result["winner"],
            overall_reasoning=overall_result["reasoning"],
            stage1_winner=stage1_result["winner"],
            stage1_scores={"A": stage1_result["scores_a"], "B": stage1_result["scores_b"]},
            stage1_reasoning=stage1_result["reasoning"],
            stage2_winner=stage2_result["winner"],
            stage2_scores={"A": stage2_result["scores_a"], "B": stage2_result["scores_b"]},
            stage2_reasoning=stage2_result["reasoning"],
            stage3_winner=stage3_result["winner"],
            stage3_scores={"A": stage3_result["scores_a"], "B": stage3_result["scores_b"]},
            stage3_reasoning=stage3_result["reasoning"],
            judge_trace_id=parent_trace.id,
            comparison_metadata={
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "duration_ms": total_duration_ms,
                "cost_a": float(analysis_a.total_cost),
                "cost_b": float(analysis_b.total_cost),
                "tokens_a": analysis_a.total_tokens,
                "tokens_b": analysis_b.total_tokens,
                "cost_difference": overall_result.get("cost_impact", ""),
                "quality_improvement": overall_result.get("quality_improvement", ""),
            },
        )

        self.db.add(comparison)
        await self.db.commit()
        await self.db.refresh(comparison)

        # Build response
        return {
            "comparison_id": str(comparison.id),
            "overall_winner": overall_result["winner"],
            "overall_reasoning": overall_result["reasoning"],
            "stage_results": [
                {
                    "stage": "Stage 1: Fact Extraction",
                    "winner": stage1_result["winner"],
                    "scores": {"A": stage1_result["scores_a"], "B": stage1_result["scores_b"]},
                    "reasoning": stage1_result["reasoning"],
                },
                {
                    "stage": "Stage 2: Reasoning & Insights",
                    "winner": stage2_result["winner"],
                    "scores": {"A": stage2_result["scores_a"], "B": stage2_result["scores_b"]},
                    "reasoning": stage2_result["reasoning"],
                },
                {
                    "stage": "Stage 3: Summary",
                    "winner": stage3_result["winner"],
                    "scores": {"A": stage3_result["scores_a"], "B": stage3_result["scores_b"]},
                    "reasoning": stage3_result["reasoning"],
                },
            ],
            "judge_trace": {
                "trace_id": str(parent_trace.id),
                "model": judge_model,
                "total_tokens": total_tokens,
                "cost": total_cost,
                "duration_ms": total_duration_ms,
            },
            "analysis_a": self._build_analysis_summary(analysis_a),
            "analysis_b": self._build_analysis_summary(analysis_b),
        }

    async def _validate_analyses(
        self,
        analysis_a_id: str,
        analysis_b_id: str,
        judge_model: Optional[str] = None,
    ) -> tuple[CallInsightsAnalysis, CallInsightsAnalysis]:
        """
        Validate that both analyses exist, belong to same org, have same transcript,
        and no duplicate comparison exists

        Args:
            judge_model: Optional judge model to check for duplicate comparison

        Raises:
            ValueError: If validation fails or comparison already exists
        """
        # Retrieve analysis A
        stmt_a = select(CallInsightsAnalysis).where(CallInsightsAnalysis.id == analysis_a_id)
        result_a = await self.db.execute(stmt_a)
        analysis_a = result_a.scalar_one_or_none()

        if not analysis_a:
            raise ValueError(f"Analysis A not found: {analysis_a_id}")

        # Retrieve analysis B
        stmt_b = select(CallInsightsAnalysis).where(CallInsightsAnalysis.id == analysis_b_id)
        result_b = await self.db.execute(stmt_b)
        analysis_b = result_b.scalar_one_or_none()

        if not analysis_b:
            raise ValueError(f"Analysis B not found: {analysis_b_id}")

        # Verify same organization
        if analysis_a.organization_id != self.organization_id or analysis_b.organization_id != self.organization_id:
            raise ValueError("Cannot compare analyses from different organizations")

        # Verify same transcript (required for fair comparison)
        if analysis_a.transcript_input != analysis_b.transcript_input:
            raise ValueError("Cannot compare analyses with different transcripts")

        # Check if comparison already exists (business rule validation)
        # Look for existing comparison with same analyses (in either order) and same judge model
        from sqlalchemy import or_, and_
        existing_comparison_stmt = select(InsightComparison).where(
            and_(
                InsightComparison.organization_id == self.organization_id,
                or_(
                    # Check both orderings: A vs B and B vs A
                    and_(
                        InsightComparison.analysis_a_id == analysis_a_id,
                        InsightComparison.analysis_b_id == analysis_b_id,
                    ),
                    and_(
                        InsightComparison.analysis_a_id == analysis_b_id,
                        InsightComparison.analysis_b_id == analysis_a_id,
                    ),
                ),
            )
        )

        # If judge model specified, also filter by judge model
        if judge_model:
            existing_comparison_stmt = existing_comparison_stmt.where(
                InsightComparison.judge_model == judge_model
            )

        existing_result = await self.db.execute(existing_comparison_stmt)
        existing_comparison = existing_result.scalar_one_or_none()

        if existing_comparison:
            if judge_model:
                raise ValueError(
                    f"Comparison already exists between these analyses with judge model '{judge_model}'. "
                    f"Comparison ID: {existing_comparison.id}"
                )
            else:
                raise ValueError(
                    f"Comparison already exists between these analyses. "
                    f"Comparison ID: {existing_comparison.id}"
                )

        return analysis_a, analysis_b

    async def _evaluate_stage(
        self,
        stage_name: str,
        prompt_template: str,
        transcript: str,
        response_a: str,
        response_b: str,
        judge_model: str,
        judge_trace_id: str,
        user_id: str,
        temperature: float = 0.0,
        reasoning_effort: Optional[str] = None,
        stage1_output: Optional[str] = None,
        stage2_output: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute judge model evaluation for a single stage

        Args:
            temperature: Temperature for judge model (0.0 = deterministic, 1.0 = creative)
            reasoning_effort: GPT-5 only - thinking time (minimal, low, medium, high)

        Returns:
            Dict with: winner, scores_a, scores_b, reasoning, tokens_used, cost
        """
        stage_start_time = time.time()

        # Format prompt with inputs
        prompt = prompt_template.format(
            transcript=transcript,
            response_a=response_a,
            response_b=response_b,
            stage1_output=stage1_output or "",
            stage2_output=stage2_output or "",
        )

        # Execute judge model
        execution_request = ModelExecutionRequest(
            model=judge_model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,  # Use provided temperature
            max_tokens=6000,  # Doubled for GPT-5 models with extended reasoning
            top_p=1.0,
            reasoning_effort=reasoning_effort,  # GPT-5 only
        )

        execution_result = await self.model_service.execute(execution_request)

        # Parse JSON response from judge
        try:
            judge_output = self._parse_judge_response(execution_result.response)
        except Exception as e:
            # If JSON parsing fails, retry once with explicit JSON instruction
            print(f"[WARN] Judge model JSON parsing failed for {stage_name}: {e}")
            retry_prompt = f"{prompt}\n\nIMPORTANT: You MUST respond with valid JSON only. No markdown, no explanation, just the JSON object."
            retry_request = ModelExecutionRequest(
                model=judge_model,
                messages=[{"role": "user", "content": retry_prompt}],
                temperature=temperature,  # Use same temperature for retry
                max_tokens=6000,  # Doubled for GPT-5 models with extended reasoning
                top_p=1.0,
                reasoning_effort=reasoning_effort,  # GPT-5 only
            )
            retry_result = await self.model_service.execute(retry_request)
            judge_output = self._parse_judge_response(retry_result.response)

            # Update execution result with retry data
            execution_result = retry_result

        stage_duration_ms = (time.time() - stage_start_time) * 1000

        return {
            "winner": judge_output["winner"],
            "scores_a": judge_output["scores_a"],
            "scores_b": judge_output["scores_b"],
            "reasoning": judge_output["reasoning"],
            "tokens_used": execution_result.tokens_used,
            "cost": execution_result.cost,
            "input_tokens": execution_result.input_tokens,
            "output_tokens": execution_result.output_tokens,
            "duration_ms": stage_duration_ms,
        }

    async def _get_model_parameters(self, analysis: CallInsightsAnalysis) -> Dict[str, Dict[str, str]]:
        """Extract model parameters (temperature, top_p, max_tokens) from analysis metadata"""
        # Check for new format: model_parameters (includes all params)
        if analysis.analysis_metadata and "model_parameters" in analysis.analysis_metadata:
            params = analysis.analysis_metadata["model_parameters"]
            return {
                "stage1": {
                    "temperature": str(params.get("stage1", {}).get("temperature", "N/A")),
                    "top_p": str(params.get("stage1", {}).get("top_p", "N/A")),
                    "max_tokens": str(params.get("stage1", {}).get("max_tokens", "N/A")),
                },
                "stage2": {
                    "temperature": str(params.get("stage2", {}).get("temperature", "N/A")),
                    "top_p": str(params.get("stage2", {}).get("top_p", "N/A")),
                    "max_tokens": str(params.get("stage2", {}).get("max_tokens", "N/A")),
                },
                "stage3": {
                    "temperature": str(params.get("stage3", {}).get("temperature", "N/A")),
                    "top_p": str(params.get("stage3", {}).get("top_p", "N/A")),
                    "max_tokens": str(params.get("stage3", {}).get("max_tokens", "N/A")),
                },
            }

        # Backward compatibility: Check for old format (temperature_settings only)
        if analysis.analysis_metadata and "temperature_settings" in analysis.analysis_metadata:
            temps = analysis.analysis_metadata["temperature_settings"]
            return {
                "stage1": {
                    "temperature": str(temps.get("stage1", "N/A")),
                    "top_p": "N/A",
                    "max_tokens": "N/A",
                },
                "stage2": {
                    "temperature": str(temps.get("stage2", "N/A")),
                    "top_p": "N/A",
                    "max_tokens": "N/A",
                },
                "stage3": {
                    "temperature": str(temps.get("stage3", "N/A")),
                    "top_p": "N/A",
                    "max_tokens": "N/A",
                },
            }

        # Default if not found
        return {
            "stage1": {"temperature": "N/A", "top_p": "N/A", "max_tokens": "N/A"},
            "stage2": {"temperature": "N/A", "top_p": "N/A", "max_tokens": "N/A"},
            "stage3": {"temperature": "N/A", "top_p": "N/A", "max_tokens": "N/A"},
        }

    async def _calculate_overall_winner(
        self,
        stage1_result: Dict[str, Any],
        stage2_result: Dict[str, Any],
        stage3_result: Dict[str, Any],
        cost_a: float,
        cost_b: float,
        tokens_a: int,
        tokens_b: int,
        model_a_name: str,
        model_b_name: str,
        params_a: Dict[str, Dict[str, str]],
        params_b: Dict[str, Dict[str, str]],
        judge_model: str,
        judge_trace_id: str,
        user_id: str,
        temperature: float = 0.0,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate overall winner with cost-benefit analysis

        Args:
            temperature: Temperature for judge model evaluation
            reasoning_effort: GPT-5 only - thinking time (minimal, low, medium, high)

        Uses weighted average across stages: Stage 1 (30%), Stage 2 (35%), Stage 3 (35%)
        """
        # Calculate average scores
        def avg_score(scores: Dict[str, float]) -> float:
            """Calculate average of all scores in dict"""
            values = [v for v in scores.values() if v is not None]
            return sum(values) / len(values) if values else 0.0

        stage1_avg_a = avg_score(stage1_result["scores_a"])
        stage1_avg_b = avg_score(stage1_result["scores_b"])
        stage2_avg_a = avg_score(stage2_result["scores_a"])
        stage2_avg_b = avg_score(stage2_result["scores_b"])
        stage3_avg_a = avg_score(stage3_result["scores_a"])
        stage3_avg_b = avg_score(stage3_result["scores_b"])

        # Calculate cost difference with proper formatting
        cost_diff = cost_b - cost_a
        cost_diff_percent = ((cost_diff / cost_a) * 100) if cost_a > 0 else 0
        cost_diff_str = f"+${cost_diff:.5f} (+{cost_diff_percent:.1f}%)" if cost_diff > 0 else f"-${abs(cost_diff):.5f} ({cost_diff_percent:.1f}%)"

        # Format prompt for overall verdict with tabular data and model parameters
        prompt = OVERALL_VERDICT_PROMPT.format(
            stage1_winner=stage1_result["winner"],
            stage1_scores_a=stage1_result["scores_a"],
            stage1_scores_b=stage1_result["scores_b"],
            stage2_winner=stage2_result["winner"],
            stage2_scores_a=stage2_result["scores_a"],
            stage2_scores_b=stage2_result["scores_b"],
            stage3_winner=stage3_result["winner"],
            stage3_scores_a=stage3_result["scores_a"],
            stage3_scores_b=stage3_result["scores_b"],
            cost_a=f"{cost_a:.5f}",
            cost_b=f"{cost_b:.5f}",
            tokens_a=f"{tokens_a:,}",
            tokens_b=f"{tokens_b:,}",
            cost_difference=cost_diff_str,
            model_a_name=model_a_name,
            model_b_name=model_b_name,
            temp_a_stage1=params_a["stage1"]["temperature"],
            temp_a_stage2=params_a["stage2"]["temperature"],
            temp_a_stage3=params_a["stage3"]["temperature"],
            temp_b_stage1=params_b["stage1"]["temperature"],
            temp_b_stage2=params_b["stage2"]["temperature"],
            temp_b_stage3=params_b["stage3"]["temperature"],
            top_p_a_stage1=params_a["stage1"]["top_p"],
            top_p_a_stage2=params_a["stage2"]["top_p"],
            top_p_a_stage3=params_a["stage3"]["top_p"],
            top_p_b_stage1=params_b["stage1"]["top_p"],
            top_p_b_stage2=params_b["stage2"]["top_p"],
            top_p_b_stage3=params_b["stage3"]["top_p"],
            max_tokens_a_stage1=params_a["stage1"]["max_tokens"],
            max_tokens_a_stage2=params_a["stage2"]["max_tokens"],
            max_tokens_a_stage3=params_a["stage3"]["max_tokens"],
            max_tokens_b_stage1=params_b["stage1"]["max_tokens"],
            max_tokens_b_stage2=params_b["stage2"]["max_tokens"],
            max_tokens_b_stage3=params_b["stage3"]["max_tokens"],
        )

        # Execute judge model for overall verdict
        execution_request = ModelExecutionRequest(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,  # Use provided temperature
            max_tokens=8000,  # Doubled for GPT-5 models with extended reasoning and comprehensive analysis
            top_p=1.0,
            reasoning_effort=reasoning_effort,  # GPT-5 only
        )

        execution_result = await self.model_service.execute(execution_request)

        # Parse JSON response
        try:
            judge_output = self._parse_judge_response(execution_result.response)
        except Exception as e:
            print(f"[WARN] Judge model JSON parsing failed for overall verdict: {e}")
            # Retry with explicit instruction
            retry_prompt = f"{prompt}\n\nIMPORTANT: You MUST respond with valid JSON only."
            retry_request = ModelExecutionRequest(
                model=judge_model,
                messages=[{"role": "user", "content": retry_prompt}],
                temperature=temperature,  # Use same temperature for retry
                max_tokens=8000,  # Doubled for GPT-5 models with extended reasoning and comprehensive analysis
                top_p=1.0,
                reasoning_effort=reasoning_effort,  # GPT-5 only
            )
            retry_result = await self.model_service.execute(retry_request)
            judge_output = self._parse_judge_response(retry_result.response)
            execution_result = retry_result

        return {
            "winner": judge_output["overall_winner"],
            "reasoning": judge_output["reasoning"],
            "quality_improvement": judge_output.get("quality_improvement", ""),
            "cost_impact": judge_output.get("cost_impact", ""),
            "recommendation": judge_output.get("recommendation", ""),
            "tokens_used": execution_result.tokens_used,
            "cost": execution_result.cost,
            "input_tokens": execution_result.input_tokens,
            "output_tokens": execution_result.output_tokens,
        }

    def _parse_judge_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from judge model

        Handles:
        - Markdown code blocks (```json ... ```)
        - Plain JSON
        - Whitespace variations
        - Truncated JSON (attempts to fix common issues)

        Raises:
            ValueError: If JSON is invalid and cannot be fixed
        """
        # Strip markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]  # Remove ```json
        elif response.startswith("```"):
            response = response[3:]  # Remove ```
        if response.endswith("```"):
            response = response[:-3]  # Remove trailing ```

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Log the full error with more context
            print(f"[ERROR] JSON parsing failed: {e}")
            print(f"[ERROR] Response preview (first 1000 chars):\n{response[:1000]}")
            print(f"[ERROR] Response preview (last 500 chars):\n{response[-500:]}")

            # Attempt to fix common truncation issues
            # Check if JSON is incomplete (missing closing braces)
            open_braces = response.count('{')
            close_braces = response.count('}')
            if open_braces > close_braces:
                print(f"[WARN] Detected {open_braces - close_braces} unclosed braces, attempting to fix...")
                # Try adding missing closing braces
                fixed_response = response + ('}' * (open_braces - close_braces))
                try:
                    result = json.loads(fixed_response)
                    print(f"[SUCCESS] Fixed truncated JSON by adding {open_braces - close_braces} closing braces")
                    return result
                except json.JSONDecodeError:
                    print(f"[WARN] Failed to fix JSON by adding braces")

            # Check for unterminated strings
            if 'Unterminated string' in str(e):
                print(f"[WARN] Detected unterminated string, attempting to fix...")
                # Try to find the last complete field before the truncation
                last_complete_field = response.rfind('",')
                if last_complete_field > 0:
                    truncated_response = response[:last_complete_field + 1]
                    # Close any open objects
                    open_braces = truncated_response.count('{')
                    close_braces = truncated_response.count('}')
                    truncated_response += '}' * (open_braces - close_braces)
                    try:
                        result = json.loads(truncated_response)
                        print(f"[SUCCESS] Fixed unterminated string by truncating to last complete field")
                        # Add warning to reasoning field if present
                        if 'reasoning' in result and isinstance(result['reasoning'], str):
                            result['reasoning'] += "\n\n⚠️ **Note**: Response was truncated due to length. Summary may be incomplete."
                        return result
                    except json.JSONDecodeError:
                        print(f"[WARN] Failed to fix JSON by truncating")

            raise ValueError(f"Invalid JSON from judge model: {e}\n\nResponse: {response[:500]}")

    def _get_model_summary(self, analysis: CallInsightsAnalysis) -> str:
        """Get human-readable model summary for an analysis"""
        models = [analysis.model_stage1, analysis.model_stage2, analysis.model_stage3]
        unique_models = list(set(models))

        if len(unique_models) == 1:
            return f"{unique_models[0]} (all stages)"
        else:
            return f"Stage 1: {analysis.model_stage1}, Stage 2: {analysis.model_stage2}, Stage 3: {analysis.model_stage3}"

    def _build_analysis_summary(self, analysis: CallInsightsAnalysis) -> Dict[str, Any]:
        """Build analysis summary for response"""
        return {
            "id": str(analysis.id),
            "transcript_title": analysis.transcript_title,
            "model_stage1": analysis.model_stage1,
            "model_stage2": analysis.model_stage2,
            "model_stage3": analysis.model_stage3,
            "total_tokens": analysis.total_tokens,
            "total_cost": float(analysis.total_cost),
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        }

    async def list_comparisons(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List all comparisons for organization with pagination

        Returns:
            Dict with: comparisons (list), pagination (dict)
        """
        # Query comparisons for this organization
        stmt = (
            select(InsightComparison)
            .where(InsightComparison.organization_id == self.organization_id)
            .order_by(InsightComparison.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        comparisons = result.scalars().all()

        # Count total comparisons
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(InsightComparison).where(
            InsightComparison.organization_id == self.organization_id
        )
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()

        # Build list items with enhanced details
        items = []
        for comp in comparisons:
            # Fetch analyses for full details
            analysis_a = await self.db.get(CallInsightsAnalysis, comp.analysis_a_id)
            analysis_b = await self.db.get(CallInsightsAnalysis, comp.analysis_b_id)

            # Extract model parameters for both analyses
            params_a = await self._get_model_parameters(analysis_a) if analysis_a else {}
            params_b = await self._get_model_parameters(analysis_b) if analysis_b else {}

            items.append({
                "id": str(comp.id),
                "analysis_a_title": analysis_a.transcript_title if analysis_a else None,
                "analysis_b_title": analysis_b.transcript_title if analysis_b else None,
                "model_a_summary": self._get_model_summary(analysis_a) if analysis_a else "Unknown",
                "model_b_summary": self._get_model_summary(analysis_b) if analysis_b else "Unknown",
                # Model details for A
                "model_a_stage1": analysis_a.model_stage1 if analysis_a else None,
                "model_a_stage2": analysis_a.model_stage2 if analysis_a else None,
                "model_a_stage3": analysis_a.model_stage3 if analysis_a else None,
                "params_a": params_a,
                # Model details for B
                "model_b_stage1": analysis_b.model_stage1 if analysis_b else None,
                "model_b_stage2": analysis_b.model_stage2 if analysis_b else None,
                "model_b_stage3": analysis_b.model_stage3 if analysis_b else None,
                "params_b": params_b,
                # Cost and tokens
                "cost_a": float(analysis_a.total_cost) if analysis_a else 0.0,
                "cost_b": float(analysis_b.total_cost) if analysis_b else 0.0,
                "tokens_a": analysis_a.total_tokens if analysis_a else 0,
                "tokens_b": analysis_b.total_tokens if analysis_b else 0,
                # Comparison results
                "judge_model": comp.judge_model,
                "overall_winner": comp.overall_winner,
                "cost_difference": comp.comparison_metadata.get("cost_difference", ""),
                "quality_improvement": comp.comparison_metadata.get("quality_improvement", ""),
                "created_at": comp.created_at.isoformat() if comp.created_at else None,
            })

        return {
            "comparisons": items,
            "pagination": {
                "page": (skip // limit) + 1,
                "page_size": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit,
            },
        }

    async def get_comparison(self, comparison_id: str) -> Dict[str, Any]:
        """
        Get detailed comparison by ID

        Raises:
            ValueError: If comparison not found or access denied
        """
        stmt = select(InsightComparison).where(InsightComparison.id == comparison_id)
        result = await self.db.execute(stmt)
        comparison = result.scalar_one_or_none()

        if not comparison:
            raise ValueError(f"Comparison not found: {comparison_id}")

        if comparison.organization_id != self.organization_id:
            raise ValueError("Access denied: comparison belongs to different organization")

        # Fetch analyses
        analysis_a = await self.db.get(CallInsightsAnalysis, comparison.analysis_a_id)
        analysis_b = await self.db.get(CallInsightsAnalysis, comparison.analysis_b_id)

        if not analysis_a or not analysis_b:
            raise ValueError("Associated analyses not found")

        return {
            "id": str(comparison.id),
            "organization_id": str(comparison.organization_id),
            "user_id": str(comparison.user_id),
            "analysis_a": self._build_analysis_summary(analysis_a),
            "analysis_b": self._build_analysis_summary(analysis_b),
            "judge_model": comparison.judge_model,
            "evaluation_criteria": comparison.evaluation_criteria,
            "overall_winner": comparison.overall_winner,
            "overall_reasoning": comparison.overall_reasoning,
            "stage_results": [
                {
                    "stage": "Stage 1: Fact Extraction",
                    "winner": comparison.stage1_winner,
                    "scores": comparison.stage1_scores,
                    "reasoning": comparison.stage1_reasoning,
                },
                {
                    "stage": "Stage 2: Reasoning & Insights",
                    "winner": comparison.stage2_winner,
                    "scores": comparison.stage2_scores,
                    "reasoning": comparison.stage2_reasoning,
                },
                {
                    "stage": "Stage 3: Summary",
                    "winner": comparison.stage3_winner,
                    "scores": comparison.stage3_scores,
                    "reasoning": comparison.stage3_reasoning,
                },
            ],
            "judge_trace": {
                "trace_id": str(comparison.judge_trace_id) if comparison.judge_trace_id else None,
                "model": comparison.judge_model,
                "total_tokens": comparison.comparison_metadata.get("total_tokens", 0),
                "cost": comparison.comparison_metadata.get("total_cost", 0.0),
                "duration_ms": comparison.comparison_metadata.get("duration_ms", 0.0),
            },
            "created_at": comparison.created_at.isoformat() if comparison.created_at else None,
        }

    async def delete_comparison(self, comparison_id: str) -> None:
        """
        Delete comparison by ID

        Raises:
            ValueError: If comparison not found or access denied
        """
        stmt = select(InsightComparison).where(InsightComparison.id == comparison_id)
        result = await self.db.execute(stmt)
        comparison = result.scalar_one_or_none()

        if not comparison:
            raise ValueError(f"Comparison not found: {comparison_id}")

        if comparison.organization_id != self.organization_id:
            raise ValueError("Access denied: comparison belongs to different organization")

        await self.db.delete(comparison)
        await self.db.commit()
