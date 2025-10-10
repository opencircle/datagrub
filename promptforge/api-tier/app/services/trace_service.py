"""
Trace Service - Records API executions for observability
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import Trace


class TraceService:
    """Service for creating execution traces"""

    def __init__(self, db: Session):
        self.db = db

    async def create_trace(
        self,
        trace_id: str,
        user_id: str,
        organization_id: str,
        model: str,
        input_prompt: str,
        output_response: str,
        latency_ms: float,
        tokens_used: int,
        cost: float,
        prompt_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        status: Optional[str] = "success",
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Trace:
        """
        Create a trace record for prompt execution

        This stores:
        - Execution details (model, prompts, response)
        - Performance metrics (latency, tokens, cost)
        - Context (user, organization, prompt_id)
        - Metadata for filtering and analysis
        - Error tracking (status, error_message, error_type)
        """
        from sqlalchemy import select
        from app.models.project import Project

        # Get or create playground project for this organization
        if not project_id:
            # Try to find existing playground project
            stmt = select(Project).where(
                Project.organization_id == organization_id,
                Project.name == "Playground"
            )
            result = await self.db.execute(stmt)
            playground_project = result.scalar_one_or_none()

            if not playground_project:
                # Create playground project
                playground_project = Project(
                    id=uuid.uuid4(),
                    organization_id=organization_id,
                    name="Playground",
                    description="Auto-generated project for playground executions",
                    created_by=user_id,
                )
                self.db.add(playground_project)
                await self.db.flush()

            project_id = str(playground_project.id)

        # Prepare input and output data
        input_data = {
            "prompt": input_prompt,
            "system_prompt": system_prompt,
            "parameters": parameters or {},
        }

        output_data = {
            "response": output_response,
        }

        # Determine trace name: title > project name > source
        trace_name = title
        if not trace_name:
            # Get project name for default title
            project_query = select(Project).where(Project.id == project_id)
            project_result = await self.db.execute(project_query)
            project = project_result.scalar_one_or_none()
            trace_name = project.name if project else (metadata.get("source", "playground") if metadata else "playground")

        # Create trace record
        trace = Trace(
            id=uuid.uuid4(),
            trace_id=trace_id,
            name=trace_name,  # Use title if provided, otherwise project name
            status=status,
            project_id=project_id,
            user_id=user_id if user_id else None,
            model_name=model,
            input_data=input_data,
            output_data=output_data,
            trace_metadata=metadata or {},
            total_duration_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=tokens_used,
            total_cost=cost,
            environment=metadata.get("environment", "playground") if metadata else "playground",
            error_message=error_message,
            error_type=error_type,
        )

        self.db.add(trace)
        await self.db.commit()
        await self.db.refresh(trace)

        print(f"[TRACE] {trace_id}: {model} - {latency_ms:.2f}ms, {tokens_used} tokens, ${cost:.4f}")

        return trace
