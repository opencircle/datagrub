"""
Seed the evaluation catalog with PromptForge evaluations

This script populates the evaluation_catalog table with PromptForge's
proprietary evaluation metrics.
"""
import asyncio
import sys
from pathlib import Path
import os

# Add api-tier directory to path
api_tier_path = os.environ.get('API_TIER_PATH', str(Path(__file__).parent.parent.parent / "api-tier"))
if not os.path.exists(os.path.join(api_tier_path, "app")):
    # Try /app if running in Docker
    api_tier_path = "/app"
sys.path.insert(0, api_tier_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.evaluation_catalog import (
    EvaluationCatalog,
    EvaluationSource,
    EvaluationType,
    EvaluationCategory,
)


# PromptForge evaluations to seed
PROMPTFORGE_EVALUATIONS = [
    {
        "name": "Prompt Quality Score",
        "description": "Comprehensive quality assessment of prompt engineering best practices. "
                      "Evaluates clarity, context provision, instruction keywords, and format specification.",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.METRIC,
        "is_public": True,
        "config_schema": {},
        "default_config": {},
        "tags": ["quality", "prompt", "best-practices"],
        "version": "1.0.0",
    },
    {
        "name": "Cost Efficiency Score",
        "description": "Evaluates the cost-effectiveness of the LLM interaction by comparing "
                      "actual cost per token against target benchmarks.",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.METRIC,
        "is_public": True,
        "config_schema": {
            "target_cost_per_token": {
                "type": "float",
                "description": "Target cost per token",
                "default": 0.00001
            }
        },
        "default_config": {"target_cost_per_token": 0.00001},
        "tags": ["cost", "efficiency", "performance"],
        "version": "1.0.0",
    },
    {
        "name": "Response Completeness",
        "description": "Checks if the response fully addresses all aspects of the input. "
                      "Detects truncation and incompleteness indicators.",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.METRIC,
        "is_public": True,
        "config_schema": {},
        "default_config": {},
        "tags": ["quality", "completeness"],
        "version": "1.0.0",
    },
    {
        "name": "Latency Budget Validator",
        "description": "Validates that response latency is within acceptable bounds. "
                      "Helps ensure SLA compliance and user experience standards.",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.VALIDATOR,
        "is_public": True,
        "config_schema": {
            "max_latency_ms": {
                "type": "float",
                "description": "Maximum allowed latency in milliseconds",
                "default": 5000
            }
        },
        "default_config": {"max_latency_ms": 5000},
        "tags": ["performance", "latency", "sla"],
        "version": "1.0.0",
    },
    {
        "name": "Output Consistency Checker",
        "description": "Validates that output format matches expected structure (JSON, text, etc.). "
                      "Ensures consistent formatting for downstream processing.",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.VALIDATOR,
        "is_public": True,
        "config_schema": {
            "expected_format": {
                "type": "string",
                "description": "Expected output format (json, text, etc.)",
                "default": "json"
            }
        },
        "default_config": {"expected_format": "json"},
        "tags": ["quality", "consistency", "format"],
        "version": "1.0.0",
    },
    {
        "name": "Token Efficiency Score",
        "description": "Measures how efficiently tokens are used relative to output value. "
                      "Helps identify verbose or inefficient prompts.",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.PROMPTFORGE,
        "evaluation_type": EvaluationType.METRIC,
        "is_public": True,
        "config_schema": {},
        "default_config": {},
        "tags": ["performance", "tokens", "efficiency"],
        "version": "1.0.0",
    },
]


async def seed_evaluation_catalog():
    """Seed the evaluation catalog with PromptForge evaluations"""

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Seeding evaluation catalog with PromptForge evaluations...")

        for eval_data in PROMPTFORGE_EVALUATIONS:
            # Check if evaluation already exists (by name and source)
            query = select(EvaluationCatalog).where(
                EvaluationCatalog.name == eval_data["name"],
                EvaluationCatalog.source == eval_data["source"]
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  {eval_data['name']} already exists, skipping...")
                continue

            # Create new evaluation
            evaluation = EvaluationCatalog(**eval_data)
            session.add(evaluation)
            print(f"  ✅ Created: {eval_data['name']}")

        await session.commit()
        print(f"\n✅ Successfully seeded {len(PROMPTFORGE_EVALUATIONS)} PromptForge evaluations!")


async def main():
    """Main entry point"""
    try:
        await seed_evaluation_catalog()
        print("\n" + "="*60)
        print("Evaluation catalog seeding completed successfully!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error seeding evaluation catalog: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
