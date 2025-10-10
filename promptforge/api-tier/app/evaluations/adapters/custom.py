"""
Custom Evaluator Adapter - Client-specific custom evaluations

This adapter allows clients to create custom evaluations using Python code.
Code is executed in a sandboxed environment for security.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import time
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.evaluation_catalog import (
    EvaluationCatalog,
    EvaluationSource,
    EvaluationType,
)
from app.evaluations.base import (
    EvaluationAdapter,
    EvaluationRequest,
    EvaluationResult,
    EvaluationMetadata,
)

logger = logging.getLogger(__name__)


class CustomEvaluatorAdapter(EvaluationAdapter):
    """
    Custom evaluator adapter for client-specific business rules

    Executes custom Python code in a sandboxed environment.
    Custom evaluations are stored in the evaluation_catalog table.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the custom evaluator adapter

        Args:
            db_session: Database session for accessing evaluation catalog
        """
        super().__init__(EvaluationSource.CUSTOM)
        self.db_session = db_session
        logger.info("Initialized CustomEvaluatorAdapter")

    async def list_evaluations(
        self,
        organization_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None
    ) -> List[EvaluationMetadata]:
        """
        List all custom evaluations

        Args:
            organization_id: Filter by organization
            project_id: Filter by project

        Returns:
            List of custom evaluation metadata
        """
        # Build query
        query = select(EvaluationCatalog).where(
            EvaluationCatalog.source == EvaluationSource.CUSTOM,
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
        Get metadata for a specific custom evaluation

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
            EvaluationCatalog.source == EvaluationSource.CUSTOM,
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
        Execute a custom evaluation

        Args:
            evaluation_uuid: Evaluation identifier
            request: Evaluation request

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
            EvaluationCatalog.source == EvaluationSource.CUSTOM
        )

        result = await self.db_session.execute(query)
        eval_catalog = result.scalar_one_or_none()

        if not eval_catalog:
            return EvaluationResult(
                status="failed",
                error=f"Custom evaluation not found: {evaluation_uuid}"
            )

        if not eval_catalog.implementation:
            return EvaluationResult(
                status="failed",
                error="Custom evaluation has no implementation code"
            )

        try:
            # Execute the custom code in sandboxed environment
            result = await self._execute_sandboxed(
                eval_catalog.implementation,
                request,
                eval_catalog.config_schema or {}
            )

            # Add execution time
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time

            return result

        except Exception as e:
            logger.error(f"Error executing custom evaluation {evaluation_uuid}: {e}")
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
        Validate configuration for a custom evaluation

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
            EvaluationCatalog.source == EvaluationSource.CUSTOM
        )

        result = await self.db_session.execute(query)
        eval_catalog = result.scalar_one_or_none()

        if not eval_catalog:
            return False, f"Evaluation not found: {evaluation_uuid}"

        # Validate against schema
        config_schema = eval_catalog.config_schema or {}

        for field, spec in config_schema.items():
            if spec.get("required", False) and field not in config:
                return False, f"Missing required field: {field}"

            if field in config:
                expected_type = spec.get("type")
                if expected_type and not self._check_type(config[field], expected_type):
                    return False, f"Field {field} has incorrect type (expected {expected_type})"

        return True, None

    async def _execute_sandboxed(
        self,
        code: str,
        request: EvaluationRequest,
        config_schema: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Execute custom code in a sandboxed environment

        Uses RestrictedPython for safe execution.

        Args:
            code: Python code to execute
            request: Evaluation request
            config_schema: Configuration schema for validation

        Returns:
            Evaluation result
        """
        try:
            # Import RestrictedPython (will need to be added to requirements)
            from RestrictedPython import compile_restricted, safe_globals
            from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence

            # Compile the restricted code
            byte_code = compile_restricted(
                code,
                filename='<custom_evaluation>',
                mode='exec'
            )

            # Check for compilation errors
            if byte_code.errors:
                error_msg = "; ".join(byte_code.errors)
                return EvaluationResult(
                    status="failed",
                    error=f"Code compilation error: {error_msg}"
                )

            # Create safe execution environment
            safe_locals = {
                '__builtins__': safe_builtins,
                '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            }

            # Add safe globals
            exec_globals = safe_globals.copy()

            # Add request data to context
            exec_globals['request'] = {
                'input': request.input_data,
                'output': request.output_data,
                'metadata': request.metadata or {},
                'config': request.config or {},
                'trace_metadata': request.trace_metadata or {},
            }

            # Execute the code
            exec(byte_code.code, exec_globals, safe_locals)

            # The custom code must define an 'evaluate' function
            if 'evaluate' not in safe_locals:
                return EvaluationResult(
                    status="failed",
                    error="Custom evaluation code must define an 'evaluate' function"
                )

            # Call the evaluate function
            evaluate_func = safe_locals['evaluate']
            result_dict = evaluate_func(exec_globals['request'])

            # Convert result dictionary to EvaluationResult
            return EvaluationResult(
                score=result_dict.get('score'),
                passed=result_dict.get('passed'),
                category=result_dict.get('category'),
                reason=result_dict.get('reason'),
                details=result_dict.get('details'),
                suggestions=result_dict.get('suggestions'),
                status="completed"
            )

        except ImportError:
            logger.warning("RestrictedPython not installed, using basic execution")
            # Fallback to basic execution (less secure, for development only)
            return await self._execute_basic(code, request)

        except Exception as e:
            logger.error(f"Error in sandboxed execution: {e}")
            return EvaluationResult(
                status="failed",
                error=f"Execution error: {str(e)}"
            )

    async def _execute_basic(
        self,
        code: str,
        request: EvaluationRequest
    ) -> EvaluationResult:
        """
        Basic execution without RestrictedPython (for development)

        WARNING: This is not secure and should only be used in development.

        Args:
            code: Python code to execute
            request: Evaluation request

        Returns:
            Evaluation result
        """
        logger.warning("Using basic (unsecured) execution - not for production!")

        try:
            # Create execution context
            exec_globals = {}
            exec_locals = {
                'request': {
                    'input': request.input_data,
                    'output': request.output_data,
                    'metadata': request.metadata or {},
                    'config': request.config or {},
                    'trace_metadata': request.trace_metadata or {},
                }
            }

            # Execute code
            exec(code, exec_globals, exec_locals)

            # Get evaluate function
            if 'evaluate' not in exec_locals:
                return EvaluationResult(
                    status="failed",
                    error="Custom code must define an 'evaluate' function"
                )

            # Call evaluate
            evaluate_func = exec_locals['evaluate']
            result_dict = evaluate_func(exec_locals['request'])

            # Convert to EvaluationResult
            return EvaluationResult(
                score=result_dict.get('score'),
                passed=result_dict.get('passed'),
                category=result_dict.get('category'),
                reason=result_dict.get('reason'),
                details=result_dict.get('details'),
                suggestions=result_dict.get('suggestions'),
                status="completed"
            )

        except Exception as e:
            logger.error(f"Error in basic execution: {e}")
            return EvaluationResult(
                status="failed",
                error=f"Execution error: {str(e)}"
            )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            "string": str,
            "number": (int, float),
            "float": float,
            "int": int,
            "boolean": bool,
            "object": dict,
            "array": list,
        }

        expected = type_map.get(expected_type)
        if not expected:
            return True  # Unknown type, allow it

        return isinstance(value, expected)
