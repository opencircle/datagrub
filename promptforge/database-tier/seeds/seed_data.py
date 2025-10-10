"""
Database seeding script with sample data
"""
import asyncio
import sys
from pathlib import Path
import os

# Add api-tier directory to path
api_tier_path = os.environ.get('API_TIER_PATH', str(Path(__file__).parent.parent.parent / "api-tier"))
sys.path.insert(0, api_tier_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime, timedelta
import uuid

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.user import User, Organization, UserRole
from app.models.project import Project
from app.models.prompt import Prompt, PromptVersion
from app.models.evaluation import Evaluation, EvaluationResult
from app.models.model import ModelProvider, AIModel, ModelProviderType
from app.models.policy import Policy, PolicySeverity, PolicyAction
from app.models.trace import Trace, Span


async def seed_database():
    """Seed the database with sample data"""

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Create Organization
        print("Creating organization...")
        org = Organization(
            name="PromptForge Demo",
            description="Demo organization for PromptForge platform"
        )
        session.add(org)
        await session.flush()

        # 2. Create Users
        print("Creating users...")
        admin_user = User(
            email="admin@promptforge.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            organization_id=org.id,
            is_active=True,
        )
        session.add(admin_user)

        dev_user = User(
            email="developer@promptforge.com",
            hashed_password=get_password_hash("dev123"),
            full_name="Developer User",
            role=UserRole.DEVELOPER,
            organization_id=org.id,
            is_active=True,
        )
        session.add(dev_user)

        viewer_user = User(
            email="viewer@promptforge.com",
            hashed_password=get_password_hash("viewer123"),
            full_name="Viewer User",
            role=UserRole.VIEWER,
            organization_id=org.id,
            is_active=True,
        )
        session.add(viewer_user)
        await session.flush()

        # 3. Create Model Providers
        print("Creating model providers...")
        openai_provider = ModelProvider(
            name="OpenAI",
            provider_type=ModelProviderType.OPENAI,
            description="OpenAI GPT models",
            api_base_url="https://api.openai.com/v1",
            is_active=True,
            is_default=True,
        )
        session.add(openai_provider)

        anthropic_provider = ModelProvider(
            name="Anthropic",
            provider_type=ModelProviderType.ANTHROPIC,
            description="Anthropic Claude models",
            api_base_url="https://api.anthropic.com/v1",
            is_active=True,
        )
        session.add(anthropic_provider)
        await session.flush()

        # 4. Create AI Models
        print("Creating AI models...")
        gpt4 = AIModel(
            name="GPT-4",
            model_id="gpt-4-0125-preview",
            description="Most capable GPT-4 model",
            provider_id=openai_provider.id,
            supports_streaming=True,
            supports_function_calling=True,
            max_context_length=128000,
            input_cost_per_million=10.0,
            output_cost_per_million=30.0,
            default_temperature=0.7,
            default_max_tokens=2000,
        )
        session.add(gpt4)

        claude3 = AIModel(
            name="Claude 3 Sonnet",
            model_id="claude-3-sonnet-20240229",
            description="Balanced Claude 3 model",
            provider_id=anthropic_provider.id,
            supports_streaming=True,
            supports_vision=True,
            max_context_length=200000,
            input_cost_per_million=3.0,
            output_cost_per_million=15.0,
            default_temperature=0.7,
            default_max_tokens=2000,
        )
        session.add(claude3)
        await session.flush()

        # 5. Create Projects
        print("Creating projects...")
        project1 = Project(
            name="Customer Support Assistant",
            description="AI-powered customer support chatbot",
            status="active",
            organization_id=org.id,
            created_by=admin_user.id,
        )
        session.add(project1)

        project2 = Project(
            name="Content Generation Platform",
            description="Automated content creation and optimization",
            status="active",
            organization_id=org.id,
            created_by=dev_user.id,
        )
        session.add(project2)

        project3 = Project(
            name="Code Review Assistant",
            description="AI-powered code review and suggestions",
            status="draft",
            organization_id=org.id,
            created_by=dev_user.id,
        )
        session.add(project3)
        await session.flush()

        # 6. Create Prompts with Versions
        print("Creating prompts...")
        prompt1 = Prompt(
            name="Customer Greeting",
            description="Friendly greeting for customer support",
            category="chatbot",
            status="active",
            project_id=project1.id,
            created_by=admin_user.id,
        )
        session.add(prompt1)
        await session.flush()

        version1 = PromptVersion(
            prompt_id=prompt1.id,
            version_number=1,
            template="You are a friendly customer support agent. Greet the customer and ask how you can help them today.\n\nCustomer: {customer_message}",
            system_message="You are a helpful, friendly, and professional customer support agent.",
            variables={"customer_message": {"type": "string", "description": "Customer's message"}},
            model_config={"temperature": 0.7, "max_tokens": 150},
            tags=["greeting", "customer-support"],
            avg_latency_ms=450.0,
            avg_cost=0.0002,
            usage_count=1234,
        )
        session.add(version1)
        await session.flush()

        prompt1.current_version_id = version1.id

        # 7. Create Policies
        print("Creating policies...")
        policy1 = Policy(
            name="PII Detection",
            description="Detect and flag personally identifiable information",
            policy_type="pii",
            project_id=project1.id,
            rules={
                "patterns": ["email", "phone", "ssn", "credit_card"],
                "action": "redact"
            },
            threshold={"confidence": 0.8},
            severity=PolicySeverity.HIGH,
            action=PolicyAction.BLOCK,
            is_active=True,
            is_enforced=True,
        )
        session.add(policy1)

        policy2 = Policy(
            name="Toxicity Filter",
            description="Filter toxic and harmful content",
            policy_type="toxicity",
            project_id=project1.id,
            rules={
                "categories": ["hate", "harassment", "violence"],
                "threshold": 0.7
            },
            threshold={"toxicity_score": 0.7},
            severity=PolicySeverity.CRITICAL,
            action=PolicyAction.BLOCK,
            is_active=True,
            is_enforced=True,
        )
        session.add(policy2)

        policy3 = Policy(
            name="Cost Limit",
            description="Alert when cost exceeds threshold",
            policy_type="cost",
            project_id=project2.id,
            rules={
                "max_cost_per_request": 0.10,
                "daily_budget": 100.0
            },
            threshold={"cost_per_request": 0.10},
            severity=PolicySeverity.MEDIUM,
            action=PolicyAction.WARN,
            is_active=True,
            is_enforced=False,
        )
        session.add(policy3)
        await session.flush()

        # 8. Create Evaluations
        print("Creating evaluations...")
        eval1 = Evaluation(
            name="Greeting Accuracy Test",
            description="Test greeting prompt accuracy and tone",
            evaluation_type="accuracy",
            status="completed",
            project_id=project1.id,
            prompt_id=prompt1.id,
            created_by=admin_user.id,
            config={"criteria": ["tone", "accuracy", "helpfulness"]},
            dataset_id="greeting-test-v1",
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            avg_score=0.92,
        )
        session.add(eval1)
        await session.flush()

        # Add evaluation results
        for i in range(10):
            result = EvaluationResult(
                evaluation_id=eval1.id,
                test_name=f"Test Case {i+1}",
                input_data={"customer_message": f"Sample input {i+1}"},
                expected_output="Friendly greeting",
                actual_output=f"Hello! How can I help you today? (Test {i+1})",
                score=0.95 if i != 7 else 0.65,
                passed=i != 7,
                latency_ms=420.0 + (i * 10),
                token_count=45 + i,
                cost=0.0002,
                metrics={"tone_score": 0.98, "accuracy_score": 0.92},
            )
            session.add(result)

        # 9. Create Traces
        print("Creating traces...")
        for i in range(5):
            trace = Trace(
                trace_id=f"trace-{uuid.uuid4()}",
                name=f"Customer Support Session {i+1}",
                status="success" if i < 4 else "error",
                project_id=project1.id,
                prompt_version_id=version1.id,
                model_id=gpt4.id,
                input_data={"message": f"Sample customer query {i+1}"},
                output_data={"response": f"Sample response {i+1}"} if i < 4 else None,
                total_duration_ms=850.0 + (i * 50),
                total_tokens=120 + (i * 10),
                total_cost=0.0015,
                error_message="Timeout error" if i == 4 else None,
                error_type="timeout" if i == 4 else None,
            )
            session.add(trace)
            await session.flush()

            # Add spans to trace
            span = Span(
                trace_id=trace.id,
                span_id=f"span-{uuid.uuid4()}",
                name="LLM Call",
                span_type="llm",
                start_time=datetime.utcnow().timestamp(),
                end_time=datetime.utcnow().timestamp() + 0.8,
                duration_ms=800.0,
                input_data={"prompt": "Sample prompt"},
                output_data={"response": "Sample response"} if i < 4 else None,
                span_metadata={"model_version": "gpt-4-0125-preview"},
                model_name="gpt-4-0125-preview",
                prompt_tokens=80,
                completion_tokens=40,
                total_tokens=120,
                temperature=0.7,
                max_tokens=150,
                status="success" if i < 4 else "error",
                error_message="Model timeout" if i == 4 else None,
            )
            session.add(span)

        await session.commit()

    print("\n✅ Database seeded successfully!")
    print("\nTest Credentials:")
    print("  Admin: admin@promptforge.com / admin123")
    print("  Developer: developer@promptforge.com / dev123")
    print("  Viewer: viewer@promptforge.com / viewer123")


if __name__ == "__main__":
    asyncio.run(seed_database())
