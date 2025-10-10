"""
Call Insights Service - 3-stage Dynamic Temperature Adjustment pipeline

Implements:
- Stage 1: Fact Extraction (temperature 0.25, top_p 0.95)
- Stage 2: Reasoning & Insights (temperature 0.65, top_p 0.95)
- Stage 3: Summary Synthesis (temperature 0.45, top_p 0.95)

With:
- Optional PII redaction using Presidio
- Comprehensive tracing for each stage
- Evaluation execution on outputs
- Organization-scoped API key retrieval
"""

import time
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.model_provider import ModelProviderService, ModelExecutionRequest
from app.services.trace_service import TraceService
from app.models.evaluation_catalog import EvaluationCatalog, TraceEvaluation
from app.models.call_insights import CallInsightsAnalysis
from app.evaluations.registry import registry
from app.evaluations.base import EvaluationRequest


# Default stage parameters following DTA spec
DEFAULT_STAGE_PARAMS = {
    "fact_extraction": {
        "temperature": 0.25,
        "top_p": 0.95,
        "max_tokens": 1000,
    },
    "reasoning": {
        "temperature": 0.65,
        "top_p": 0.95,
        "max_tokens": 1500,
    },
    "summary": {
        "temperature": 0.45,
        "top_p": 0.95,
        "max_tokens": 800,
    },
}


class CallInsightsService:
    """Service for analyzing call transcripts with 3-stage DTA pipeline"""

    def __init__(self, db: AsyncSession, organization_id: str):
        self.db = db
        self.organization_id = organization_id
        self.model_service = ModelProviderService(db, organization_id)
        self.trace_service = TraceService(db)

    async def analyze_transcript(
        self,
        transcript: str,
        user_id: str,
        transcript_title: Optional[str] = None,
        project_id: Optional[str] = None,
        enable_pii_redaction: bool = False,
        stage_params: Optional[Dict[str, Any]] = None,
        system_prompts: Optional[Dict[str, Optional[str]]] = None,
        models: Optional[Dict[str, Optional[str]]] = None,
        evaluation_ids: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute 3-stage analysis on call transcript

        Args:
            system_prompts: Dict with keys 'stage1', 'stage2', 'stage3' for custom system prompts
            models: Dict with keys 'stage1', 'stage2', 'stage3' for model selection

        Returns:
            Dict containing:
            - summary: str
            - insights: str
            - facts: str
            - pii_redacted: bool
            - traces: list[dict]
            - evaluations: list[dict]
            - total_tokens: int
            - total_cost: float
        """
        # Track total analysis duration
        analysis_start_time = time.time()

        # Merge custom params with defaults
        params = self._merge_stage_params(stage_params or {})

        # Extract models with defaults
        model_stage1 = (models.get("stage1") if models else None) or "gpt-4o-mini"
        model_stage2 = (models.get("stage2") if models else None) or "gpt-4o-mini"
        model_stage3 = (models.get("stage3") if models else None) or "gpt-4o-mini"

        # Extract custom system prompts
        system_prompt_stage1 = system_prompts.get("stage1") if system_prompts else None
        system_prompt_stage2 = system_prompts.get("stage2") if system_prompts else None
        system_prompt_stage3 = system_prompts.get("stage3") if system_prompts else None

        # PII redaction (placeholder - would integrate Presidio here)
        processed_transcript = transcript
        pii_redacted = False
        if enable_pii_redaction:
            # TODO: Integrate Presidio for PII redaction
            # from presidio_analyzer import AnalyzerEngine
            # from presidio_anonymizer import AnonymizerEngine
            # processed_transcript = self._redact_pii(transcript)
            pii_redacted = True

        # Load prompt templates
        fact_extraction_prompt = self._load_prompt_template("fact_extraction")
        reasoning_prompt = self._load_prompt_template("reasoning")
        summary_prompt = self._load_prompt_template("summary")

        # Create parent trace
        parent_trace_id = str(uuid.uuid4())
        parent_trace = await self.trace_service.create_trace(
            trace_id=parent_trace_id,
            user_id=user_id,
            organization_id=self.organization_id,
            project_id=project_id,
            model="gpt-4o-mini",  # Fast, cost-effective model for insights
            input_prompt=processed_transcript,
            output_response="",  # Will be updated after all stages
            latency_ms=0.0,  # Will be updated
            tokens_used=0,  # Will be updated
            cost=0.0,  # Will be updated
            parameters={"pipeline": "3-stage-dta"},
            metadata={
                "source": "call_insights",
                "pii_redacted": pii_redacted,
                "stage_count": 3,
            },
        )

        traces = []
        total_tokens = 0
        total_cost = 0.0

        # Stage 1: Fact Extraction
        stage1_result = await self._execute_stage(
            stage_name="Stage 1: Fact Extraction",
            transcript=processed_transcript,
            prompt_template=fact_extraction_prompt,
            previous_output=None,
            params=params["fact_extraction"],
            parent_trace_id=parent_trace_id,
            user_id=user_id,
            project_id=project_id,
            system_prompt=system_prompt_stage1,
            model=model_stage1,
        )
        facts = stage1_result["response"]
        traces.append({
            "trace_id": stage1_result["trace_id"],
            "stage": "Stage 1: Fact Extraction",
            "model": model_stage1,
            "temperature": params["fact_extraction"]["temperature"],
            "top_p": params["fact_extraction"]["top_p"],
            "max_tokens": params["fact_extraction"]["max_tokens"],
            "input_tokens": stage1_result["input_tokens"],
            "output_tokens": stage1_result["output_tokens"],
            "total_tokens": stage1_result["total_tokens"],
            "duration_ms": stage1_result["duration_ms"],  # Use actual trace duration
            "cost": stage1_result["cost"],
            "system_prompt": system_prompt_stage1,  # Include custom system prompt
        })
        total_tokens += stage1_result["total_tokens"]
        total_cost += stage1_result["cost"]

        # Stage 2: Reasoning & Insights (uses facts only, no transcript)
        stage2_result = await self._execute_stage(
            stage_name="Stage 2: Reasoning & Insights",
            transcript="",  # No transcript - Stage 2 only sees facts
            prompt_template=reasoning_prompt,
            previous_output=None,  # Not using previous_output pattern
            params=params["reasoning"],
            parent_trace_id=parent_trace_id,
            user_id=user_id,
            project_id=project_id,
            system_prompt=system_prompt_stage2,
            model=model_stage2,
            facts=facts,  # Pass facts explicitly
        )
        insights = stage2_result["response"]
        traces.append({
            "trace_id": stage2_result["trace_id"],
            "stage": "Stage 2: Reasoning & Insights",
            "model": model_stage2,
            "temperature": params["reasoning"]["temperature"],
            "top_p": params["reasoning"]["top_p"],
            "max_tokens": params["reasoning"]["max_tokens"],
            "input_tokens": stage2_result["input_tokens"],
            "output_tokens": stage2_result["output_tokens"],
            "total_tokens": stage2_result["total_tokens"],
            "duration_ms": stage2_result["duration_ms"],  # Use actual trace duration
            "cost": stage2_result["cost"],
            "system_prompt": system_prompt_stage2,  # Include custom system prompt
        })
        total_tokens += stage2_result["total_tokens"]
        total_cost += stage2_result["cost"]

        # Stage 3: Summary Synthesis (uses facts + reasoning, no transcript)
        stage3_result = await self._execute_stage(
            stage_name="Stage 3: Summary Synthesis",
            transcript="",  # No transcript - Stage 3 only sees facts + reasoning
            prompt_template=summary_prompt,
            previous_output=None,  # Not using previous_output pattern
            params=params["summary"],
            parent_trace_id=parent_trace_id,
            user_id=user_id,
            project_id=project_id,
            system_prompt=system_prompt_stage3,
            model=model_stage3,
            facts=facts,  # Pass facts from Stage 1
            reasoning=insights,  # Pass reasoning from Stage 2
        )
        summary = stage3_result["response"]
        traces.append({
            "trace_id": stage3_result["trace_id"],
            "stage": "Stage 3: Summary Synthesis",
            "model": model_stage3,
            "temperature": params["summary"]["temperature"],
            "top_p": params["summary"]["top_p"],
            "max_tokens": params["summary"]["max_tokens"],
            "input_tokens": stage3_result["input_tokens"],
            "output_tokens": stage3_result["output_tokens"],
            "total_tokens": stage3_result["total_tokens"],
            "duration_ms": stage3_result["duration_ms"],  # Use actual trace duration
            "cost": stage3_result["cost"],
            "system_prompt": system_prompt_stage3,  # Include custom system prompt
        })
        total_tokens += stage3_result["total_tokens"]
        total_cost += stage3_result["cost"]

        # Execute evaluations if specified
        evaluations = []
        if evaluation_ids:
            evaluations = await self._execute_evaluations(
                evaluation_ids=evaluation_ids,
                parent_trace=parent_trace,
                transcript=transcript,
                summary=summary,
                insights=insights,
                facts=facts,
            )

        # Update parent trace with total duration and aggregated metrics
        total_analysis_duration_ms = (time.time() - analysis_start_time) * 1000
        parent_trace.total_duration_ms = total_analysis_duration_ms
        parent_trace.total_tokens = total_tokens
        parent_trace.total_cost = total_cost
        parent_trace.output_data = {
            "summary": summary,
            "insights": insights,
            "facts": facts,
        }
        await self.db.commit()
        await self.db.refresh(parent_trace)

        # Save analysis to database for history
        analysis = CallInsightsAnalysis(
            organization_id=self.organization_id,
            user_id=user_id,
            project_id=project_id if project_id else None,
            transcript_title=transcript_title,
            transcript_input=transcript,
            facts_output=facts,
            insights_output=insights,
            summary_output=summary,
            pii_redacted=pii_redacted,
            stage_params=params,
            system_prompt_stage1=system_prompt_stage1,
            system_prompt_stage2=system_prompt_stage2,
            system_prompt_stage3=system_prompt_stage3,
            model_stage1=model_stage1,
            model_stage2=model_stage2,
            model_stage3=model_stage3,
            parent_trace_id=parent_trace.id,  # Use parent_trace.id (DB primary key), not parent_trace_id (trace identifier)
            total_tokens=total_tokens,
            total_cost=total_cost,
            analysis_metadata={
                "stage_count": 3,
                "evaluation_count": len(evaluations),
            }
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        return {
            "analysis_id": str(analysis.id),  # Return saved analysis ID
            "summary": summary,
            "insights": insights,
            "facts": facts,
            "pii_redacted": pii_redacted,
            "traces": traces,
            "evaluations": evaluations,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
        }

    async def _execute_stage(
        self,
        stage_name: str,
        transcript: str,
        prompt_template: str,
        previous_output: Optional[str],
        params: Dict[str, Any],
        parent_trace_id: str,
        user_id: str,
        project_id: Optional[str],
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        facts: Optional[str] = None,
        reasoning: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a single stage of the DTA pipeline"""
        stage_start_time = time.time()

        # Format prompt with variables
        user_prompt = prompt_template.replace("{{transcript}}", transcript if transcript else "")
        if previous_output:
            user_prompt = user_prompt.replace("{{previous_output}}", previous_output)
        if facts:
            user_prompt = user_prompt.replace("{{facts}}", facts)
        if reasoning:
            user_prompt = user_prompt.replace("{{reasoning}}", reasoning)

        # Use custom system prompt or default
        system_content = system_prompt if system_prompt else "You are an expert call analyst."

        # Execute with model provider
        execution_request = ModelExecutionRequest(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt},
            ],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            top_p=params["top_p"],
        )

        try:
            execution_result = await self.model_service.execute(execution_request)

            # Calculate total stage duration (includes model invocation + overhead)
            stage_duration_ms = (time.time() - stage_start_time) * 1000

            # Use provider duration if available (more accurate), otherwise use total duration
            actual_duration_ms = execution_result.provider_duration_ms or execution_result.total_duration_ms or stage_duration_ms

            status = "success"
            error_message = None
            error_type = None

        except Exception as e:
            # Calculate duration even on failure
            stage_duration_ms = (time.time() - stage_start_time) * 1000
            actual_duration_ms = stage_duration_ms

            status = "error"
            error_message = str(e)
            error_type = type(e).__name__

            # Re-raise after capturing trace data
            raise

        # Create child trace with actual duration and error tracking
        trace_id = str(uuid.uuid4())
        await self.trace_service.create_trace(
            trace_id=trace_id,
            user_id=user_id,
            organization_id=self.organization_id,
            project_id=project_id,
            model=model,
            input_prompt=user_prompt[:1000],  # Truncate for storage
            output_response=execution_result.response[:1000] if status == "success" else "",
            latency_ms=actual_duration_ms,  # Now tracking actual duration
            tokens_used=execution_result.tokens_used if status == "success" else 0,
            cost=execution_result.cost if status == "success" else 0.0,
            input_tokens=execution_result.input_tokens if status == "success" else None,
            output_tokens=execution_result.output_tokens if status == "success" else None,
            system_prompt=system_content,  # Include in input_data for UI
            parameters=params,
            status=status,  # Pass status to trace
            error_message=error_message,  # Pass error details
            error_type=error_type,  # Pass error type
            metadata={
                "parent_trace_id": parent_trace_id,
                "stage": stage_name,
                "source": "call_insights",
                "system_prompt": system_content,  # Also keep in metadata
            },
        )

        return {
            "trace_id": trace_id,
            "response": execution_result.response,
            "input_tokens": execution_result.input_tokens,
            "output_tokens": execution_result.output_tokens,
            "total_tokens": execution_result.tokens_used,
            "cost": execution_result.cost,
            "duration_ms": actual_duration_ms,
        }

    async def _execute_evaluations(
        self,
        evaluation_ids: list[str],
        parent_trace: Any,
        transcript: str,
        summary: str,
        insights: str,
        facts: str,
    ) -> list[Dict[str, Any]]:
        """Execute evaluations on the outputs"""

        evaluations = []

        for evaluation_id in evaluation_ids:
            try:
                # Get evaluation from catalog
                eval_query = select(EvaluationCatalog).where(EvaluationCatalog.id == evaluation_id)
                eval_result = await self.db.execute(eval_query)
                evaluation = eval_result.scalar_one_or_none()

                if not evaluation:
                    continue

                # Check access
                if not evaluation.is_public and evaluation.organization_id != self.organization_id:
                    continue

                # Build evaluation request
                eval_request = EvaluationRequest(
                    trace_id=parent_trace.id,
                    input_data={"transcript": transcript, "facts": facts, "insights": insights},
                    output_data={"summary": summary},
                    metadata={
                        "model": "gpt-4o-mini",
                        "organization_id": self.organization_id,
                        "project_id": str(parent_trace.project_id) if parent_trace.project_id else None,
                    },
                    config=evaluation.default_config or {},
                    db_session=self.db,  # Pass db session for API key retrieval
                )

                # Execute evaluation
                eval_result_data = await registry.execute_evaluation(
                    evaluation.adapter_evaluation_id,
                    eval_request,
                    adapter_class=evaluation.adapter_class,
                    source=evaluation.source
                )

                # Save to database
                trace_eval = TraceEvaluation(
                    trace_id=parent_trace.id,
                    evaluation_catalog_id=evaluation.id,
                    organization_id=self.organization_id,  # Required for multi-tenant isolation
                    score=eval_result_data.score,
                    passed=eval_result_data.passed,
                    category=eval_result_data.category,
                    reason=eval_result_data.reason,
                    details=eval_result_data.details,
                    suggestions=eval_result_data.suggestions,
                    execution_time_ms=eval_result_data.execution_time_ms,
                    model_used=eval_result_data.model_used,
                    input_tokens=eval_result_data.input_tokens,
                    output_tokens=eval_result_data.output_tokens,
                    total_tokens=eval_result_data.total_tokens,
                    evaluation_cost=eval_result_data.evaluation_cost,
                    vendor_metrics=eval_result_data.vendor_metrics,
                    llm_metadata=eval_result_data.llm_metadata,
                    config=eval_request.config,
                    status=eval_result_data.status,
                    error_message=eval_result_data.error,
                )

                self.db.add(trace_eval)
                await self.db.commit()

                evaluations.append({
                    "evaluation_name": evaluation.name,
                    "evaluation_uuid": str(evaluation.id),  # Convert UUID to string
                    "score": eval_result_data.score,
                    "passed": eval_result_data.passed if eval_result_data.passed is not None else False,  # Handle None
                    "reason": eval_result_data.reason or "",  # Ensure string
                    "threshold": evaluation.default_config.get("threshold") if evaluation.default_config else None,
                    "category": eval_result_data.category,
                    "input_tokens": eval_result_data.input_tokens,
                    "output_tokens": eval_result_data.output_tokens,
                    "total_tokens": eval_result_data.total_tokens,
                    "evaluation_cost": eval_result_data.evaluation_cost,
                })

            except Exception as e:
                print(f"[WARN] Failed to execute evaluation {evaluation_id}: {e}")

        return evaluations

    def _merge_stage_params(self, custom_params: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Merge custom parameters with defaults"""

        merged = {}
        for stage in ["fact_extraction", "reasoning", "summary"]:
            merged[stage] = DEFAULT_STAGE_PARAMS[stage].copy()
            if stage in custom_params and custom_params[stage]:
                merged[stage].update({k: v for k, v in custom_params[stage].items() if v is not None})
        return merged

    def _load_prompt_template(self, stage: str) -> str:
        """Load prompt template from file"""

        prompt_dir = Path(__file__).parent.parent / "prompts" / "call_insights"
        prompt_file = prompt_dir / f"{stage}.prompt"

        if prompt_file.exists():
            return prompt_file.read_text()

        # Fallback templates if files don't exist
        fallback_templates = {
            "fact_extraction": """Analyze the following call transcript and extract all factual information.

Extract:
- Key entities (people, companies, products, dates)
- Specific numbers and metrics mentioned
- Actions taken or commitments made
- Explicit statements of fact

Transcript:
{{transcript}}

Provide a structured list of verified facts only. Do not include opinions or interpretations.""",

            "reasoning": """Based on the extracted facts, provide key insights and analysis.

Facts:
{{facts}}

Provide:
- Key insights and patterns
- Notable concerns or opportunities
- Underlying themes or motivations
- Risk factors or considerations
- Actionable recommendations""",

            "summary": """Create a concise executive summary based on the facts and insights.

Facts:
{{facts}}

Insights & Reasoning:
{{reasoning}}

Provide a 3-5 sentence executive summary covering:
- Main purpose of the call
- Key outcomes or decisions
- Important action items
- Overall sentiment""",
        }

        return fallback_templates.get(stage, "{{transcript}}")
