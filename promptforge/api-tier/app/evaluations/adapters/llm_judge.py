"""
LLM Judge Adapter - LLM-as-Judge evaluations

This adapter uses LLMs (GPT-4, Claude, etc.) to perform subjective evaluations
based on human-defined criteria.

Performance: Uses database-stored API keys with environment variable fallback
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import time
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.evaluation_catalog import (
    EvaluationCatalog,
    EvaluationSource,
)
from app.evaluations.base import (
    EvaluationAdapter,
    EvaluationRequest,
    EvaluationResult,
    EvaluationMetadata,
)
from app.services.provider_config_service import ProviderConfigService

logger = logging.getLogger(__name__)


class LLMJudgeAdapter(EvaluationAdapter):
    """
    LLM-as-Judge evaluator adapter

    Uses large language models to evaluate outputs based on subjective criteria.
    Supports multiple LLM providers (OpenAI, Anthropic, etc.)
    """

    DEFAULT_SYSTEM_PROMPT = """You are an expert evaluator assessing AI system outputs.
Your task is to evaluate the output based on the provided criteria and return a structured assessment.

You must respond ONLY with valid JSON in the following format:
{
  "score": <float between 0.0 and 1.0>,
  "passed": <boolean>,
  "reason": "<explanation of your assessment>",
  "details": {
    <any additional analysis details>
  },
  "suggestions": [
    "<improvement suggestion 1>",
    "<improvement suggestion 2>"
  ]
}
"""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the LLM judge adapter

        Args:
            db_session: Database session for accessing evaluation catalog
        """
        super().__init__(EvaluationSource.LLM_JUDGE)
        self.db_session = db_session
        self.provider_service = ProviderConfigService(db_session)
        logger.info("Initialized LLMJudgeAdapter with database-backed provider configs")

    async def list_evaluations(
        self,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> List[EvaluationMetadata]:
        """
        List all LLM judge evaluations

        Args:
            organization_id: Filter by organization
            project_id: Filter by project

        Returns:
            List of LLM judge evaluation metadata
        """
        # Build query
        query = select(EvaluationCatalog).where(
            EvaluationCatalog.source == EvaluationSource.LLM_JUDGE,
            EvaluationCatalog.is_active == True
        )

        # Apply filters
        if organization_id:
            query = query.where(EvaluationCatalog.organization_id == organization_id)
        if project_id:
            query = query.where(EvaluationCatalog.project_id == project_id)

        # Execute query
        result = await self.db_session.execute(query)
        evaluations = result.scalars().all()

        # Convert to metadata
        return [
            EvaluationMetadata(
                uuid=str(eval.id),
                name=eval.name,
                description=eval.description or "",
                source=eval.source,
                evaluation_type=eval.evaluation_type,
                category=eval.category,
                config_schema=eval.config_schema,
                default_config=eval.default_config,
                is_public=eval.is_public,
                organization_id=eval.organization_id,
                project_id=eval.project_id,
                version=eval.version or "1.0.0",
                tags=eval.tags,
            )
            for eval in evaluations
        ]

    async def get_evaluation(self, evaluation_uuid: str) -> Optional[EvaluationMetadata]:
        """
        Get metadata for a specific LLM judge evaluation

        Args:
            evaluation_uuid: Unique identifier

        Returns:
            Evaluation metadata or None
        """
        try:
            eval_id = UUID(evaluation_uuid)
        except ValueError:
            return None

        query = select(EvaluationCatalog).where(
            EvaluationCatalog.id == eval_id,
            EvaluationCatalog.source == EvaluationSource.LLM_JUDGE,
            EvaluationCatalog.is_active == True
        )

        result = await self.db_session.execute(query)
        eval = result.scalar_one_or_none()

        if not eval:
            return None

        return EvaluationMetadata(
            uuid=str(eval.id),
            name=eval.name,
            description=eval.description or "",
            source=eval.source,
            evaluation_type=eval.evaluation_type,
            category=eval.category,
            config_schema=eval.config_schema,
            default_config=eval.default_config,
            is_public=eval.is_public,
            organization_id=eval.organization_id,
            project_id=eval.project_id,
            version=eval.version or "1.0.0",
            tags=eval.tags,
        )

    async def execute(
        self,
        evaluation_uuid: str,
        request: EvaluationRequest
    ) -> EvaluationResult:
        """
        Execute an LLM judge evaluation

        Args:
            evaluation_uuid: Evaluation identifier
            request: Evaluation request with organization_id in metadata

        Returns:
            Evaluation result
        """
        start_time = time.time()

        try:
            # Get evaluation from database
            eval_id = UUID(evaluation_uuid)
        except ValueError:
            return EvaluationResult(
                status="failed",
                error=f"Invalid evaluation UUID: {evaluation_uuid}"
            )

        query = select(EvaluationCatalog).where(
            EvaluationCatalog.id == eval_id,
            EvaluationCatalog.source == EvaluationSource.LLM_JUDGE
        )

        result = await self.db_session.execute(query)
        eval_catalog = result.scalar_one_or_none()

        if not eval_catalog:
            return EvaluationResult(
                status="failed",
                error=f"LLM judge evaluation not found: {evaluation_uuid}"
            )

        if not eval_catalog.llm_criteria:
            return EvaluationResult(
                status="failed",
                error="LLM judge evaluation has no criteria defined"
            )

        try:
            # Extract organization context from request metadata (SOC 2 requirement)
            organization_id = request.metadata.get('organization_id') if request.metadata else None
            project_id = request.metadata.get('project_id') if request.metadata else None

            if not organization_id:
                logger.warning("No organization_id in evaluation request metadata")

            # Execute LLM judgment
            model = eval_catalog.llm_model or "gpt-4o-mini"
            system_prompt = eval_catalog.llm_system_prompt or self.DEFAULT_SYSTEM_PROMPT

            result = await self._call_llm_judge(
                model=model,
                system_prompt=system_prompt,
                criteria=eval_catalog.llm_criteria,
                request=request,
                organization_id=organization_id,
                project_id=project_id
            )

            # Add execution metadata
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            result.model_used = model

            return result

        except Exception as e:
            logger.error(f"Error executing LLM judge {evaluation_uuid}: {e}")
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
        Validate configuration for an LLM judge evaluation

        Args:
            evaluation_uuid: Evaluation identifier
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            eval_id = UUID(evaluation_uuid)
        except ValueError:
            return False, f"Invalid UUID: {evaluation_uuid}"

        query = select(EvaluationCatalog).where(
            EvaluationCatalog.id == eval_id,
            EvaluationCatalog.source == EvaluationSource.LLM_JUDGE
        )

        result = await self.db_session.execute(query)
        eval_catalog = result.scalar_one_or_none()

        if not eval_catalog:
            return False, f"Evaluation not found: {evaluation_uuid}"

        # Validate model if specified
        if "model" in config:
            valid_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"]
            if config["model"] not in valid_models:
                return False, f"Invalid model. Must be one of: {', '.join(valid_models)}"

        return True, None

    async def _call_llm_judge(
        self,
        model: str,
        system_prompt: str,
        criteria: str,
        request: EvaluationRequest,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> EvaluationResult:
        """
        Call LLM to perform judgment

        Args:
            model: Model to use (gpt-4, claude-3, etc.)
            system_prompt: System prompt for the LLM
            criteria: Evaluation criteria
            request: Evaluation request
            organization_id: Organization ID for provider config lookup
            project_id: Optional project ID for scoped configs

        Returns:
            Evaluation result
        """
        # Build user prompt
        user_prompt = self._build_user_prompt(criteria, request)

        # Route to appropriate LLM provider
        if model.startswith("gpt-"):
            return await self._call_openai(
                model, system_prompt, user_prompt, organization_id, project_id
            )
        elif model.startswith("claude-"):
            return await self._call_anthropic(
                model, system_prompt, user_prompt, organization_id, project_id
            )
        else:
            return EvaluationResult(
                status="failed",
                error=f"Unsupported model: {model}"
            )

    def _build_user_prompt(self, criteria: str, request: EvaluationRequest) -> str:
        """Build the user prompt for LLM judgment"""
        return f"""# Evaluation Criteria
{criteria}

# Input
{json.dumps(request.input_data, indent=2)}

# Output to Evaluate
{json.dumps(request.output_data, indent=2)}

# Additional Context
{json.dumps(request.metadata or {}, indent=2)}

Please evaluate the output according to the criteria above and provide your assessment in JSON format.
"""

    async def _call_openai(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> EvaluationResult:
        """
        Call OpenAI API for judgment using database-stored API key

        Args:
            model: OpenAI model name
            system_prompt: System prompt
            user_prompt: User prompt
            organization_id: Organization ID for config lookup
            project_id: Optional project ID

        Returns:
            Evaluation result
        """
        try:
            import openai

            # Get API key from database (with env fallback)
            if organization_id:
                config = await self.provider_service.get_openai_config(
                    organization_id=organization_id,
                    project_id=project_id
                )
                if not config:
                    logger.error(
                        f"OpenAI configuration not found: org={organization_id}, "
                        f"project={project_id}"
                    )
                    return EvaluationResult(
                        status="failed",
                        error="OpenAI API key not configured for this organization"
                    )
                api_key = config['api_key']
                logger.info(
                    f"Using OpenAI config: {config['display_name']}, "
                    f"org={organization_id}"
                )
            else:
                # Fallback to environment variable (backward compatibility)
                import os
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    return EvaluationResult(
                        status="failed",
                        error="OPENAI_API_KEY not configured (no organization context)"
                    )
                logger.warning("Using OpenAI API key from environment variable")

            # Make API call
            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,  # Deterministic for evaluation
                response_format={"type": "json_object"}  # Force JSON response
            )

            # Parse response
            content = response.choices[0].message.content
            result_dict = json.loads(content)

            return EvaluationResult(
                score=result_dict.get("score"),
                passed=result_dict.get("passed"),
                category=result_dict.get("category"),
                reason=result_dict.get("reason"),
                details=result_dict.get("details"),
                suggestions=result_dict.get("suggestions"),
                status="completed"
            )

        except ImportError:
            logger.warning("OpenAI library not installed")
            return EvaluationResult(
                status="failed",
                error="OpenAI library not installed. Install with: pip install openai"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return EvaluationResult(
                status="failed",
                error=f"LLM response was not valid JSON: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return EvaluationResult(
                status="failed",
                error=str(e)
            )

    async def _call_anthropic(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> EvaluationResult:
        """
        Call Anthropic API for judgment using database-stored API key

        Args:
            model: Anthropic model name
            system_prompt: System prompt
            user_prompt: User prompt
            organization_id: Organization ID for config lookup
            project_id: Optional project ID

        Returns:
            Evaluation result
        """
        try:
            import anthropic

            # Get API key from database (with env fallback)
            if organization_id:
                config = await self.provider_service.get_anthropic_config(
                    organization_id=organization_id,
                    project_id=project_id
                )
                if not config:
                    logger.error(
                        f"Anthropic configuration not found: org={organization_id}, "
                        f"project={project_id}"
                    )
                    return EvaluationResult(
                        status="failed",
                        error="Anthropic API key not configured for this organization"
                    )
                api_key = config['api_key']
                logger.info(
                    f"Using Anthropic config: {config['display_name']}, "
                    f"org={organization_id}"
                )
            else:
                # Fallback to environment variable (backward compatibility)
                import os
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    return EvaluationResult(
                        status="failed",
                        error="ANTHROPIC_API_KEY not configured (no organization context)"
                    )
                logger.warning("Using Anthropic API key from environment variable")

            # Make API call
            client = anthropic.AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0  # Deterministic for evaluation
            )

            # Parse response
            content = response.content[0].text
            result_dict = json.loads(content)

            return EvaluationResult(
                score=result_dict.get("score"),
                passed=result_dict.get("passed"),
                category=result_dict.get("category"),
                reason=result_dict.get("reason"),
                details=result_dict.get("details"),
                suggestions=result_dict.get("suggestions"),
                status="completed"
            )

        except ImportError:
            logger.warning("Anthropic library not installed")
            return EvaluationResult(
                status="failed",
                error="Anthropic library not installed. Install with: pip install anthropic"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return EvaluationResult(
                status="failed",
                error=f"LLM response was not valid JSON: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error calling Anthropic: {e}")
            return EvaluationResult(
                status="failed",
                error=str(e)
            )
