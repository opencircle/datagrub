"""
Seed the evaluation catalog with vendor library evaluations

This script populates the evaluation_catalog table with evaluations from:
- DeepEval (17+ metrics)
- Ragas (27+ metrics)
- MLflow (basic metrics)
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


# ==================== DeepEval Evaluations ====================

DEEPEVAL_EVALUATIONS = [
    # RAG Metrics
    {
        "name": "Answer Relevancy",
        "description": "Evaluates if the generated answer is relevant to the user query",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "rag", "relevancy"],
        "version": "1.0.0",
    },
    {
        "name": "Faithfulness",
        "description": "Measures if the generated answer is factually consistent with the provided context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "rag", "faithfulness"],
        "version": "1.0.0",
    },
    {
        "name": "Contextual Relevancy",
        "description": "Assesses if the retrieved context is relevant to the user query",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "rag", "context"],
        "version": "1.0.0",
    },
    {
        "name": "Contextual Recall",
        "description": "Evaluates if the retrieved context contains all relevant information",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "rag", "recall"],
        "version": "1.0.0",
    },
    {
        "name": "Contextual Precision",
        "description": "Measures if the retrieved context is precise and focused",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "rag", "precision"],
        "version": "1.0.0",
    },
    # Agent Metrics
    {
        "name": "Task Completion",
        "description": "Assesses if the agent successfully completed a given task",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "agent", "completion"],
        "version": "1.0.0",
    },
    {
        "name": "Tool Correctness",
        "description": "Evaluates if tools were called and used correctly",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "agent", "tools"],
        "version": "1.0.0",
    },
    # Chatbot Metrics
    {
        "name": "Conversation Completeness",
        "description": "Evaluates if conversation satisfies user needs",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "chatbot", "conversation"],
        "version": "1.0.0",
    },
    {
        "name": "Conversation Relevancy",
        "description": "Measures if generated outputs are relevant to user inputs",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "chatbot", "relevancy"],
        "version": "1.0.0",
    },
    {
        "name": "Role Adherence",
        "description": "Assesses if the chatbot stays in character throughout a conversation",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "chatbot", "role"],
        "version": "1.0.0",
    },
    {
        "name": "Knowledge Retention",
        "description": "Evaluates if the chatbot retains knowledge learned throughout a conversation",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "chatbot", "memory"],
        "version": "1.0.0",
    },
    # Safety Metrics
    {
        "name": "Bias Detection",
        "description": "Identifies potential biases in LLM outputs",
        "category": EvaluationCategory.BIAS,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "safety", "bias"],
        "version": "1.0.0",
    },
    {
        "name": "Toxicity Detection",
        "description": "Uses LLM-as-a-judge to evaluate toxicness in LLM outputs",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "safety", "toxicity"],
        "version": "1.0.0",
    },
    {
        "name": "Hallucination Detection",
        "description": "Detects hallucinations in LLM outputs",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "safety", "hallucination"],
        "version": "1.0.0",
    },
    {
        "name": "PII Leakage Detection",
        "description": "Identifies personally identifiable information leakage in outputs",
        "category": EvaluationCategory.SECURITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepEvalAdapter",
        "is_public": True,
        "tags": ["deepeval", "security", "pii"],
        "version": "1.0.0",
    },
]


# ==================== Ragas Evaluations ====================

RAGAS_EVALUATIONS = [
    # RAG Metrics
    {
        "name": "Context Precision",
        "description": "Measures the precision of retrieved context relevant to the query",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "precision"],
        "version": "1.0.0",
    },
    {
        "name": "Context Recall",
        "description": "Evaluates the recall of retrieved context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "recall"],
        "version": "1.0.0",
    },
    {
        "name": "Context Entities Recall",
        "description": "Measures recall of entities in retrieved context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "entities"],
        "version": "1.0.0",
    },
    {
        "name": "Noise Sensitivity",
        "description": "Evaluates sensitivity to noise in retrieved context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "noise"],
        "version": "1.0.0",
    },
    {
        "name": "Response Relevancy",
        "description": "Measures relevancy of generated response to the query",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "relevancy"],
        "version": "1.0.0",
    },
    {
        "name": "Faithfulness",
        "description": "Evaluates factual consistency between response and context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "rag", "faithfulness"],
        "version": "1.0.0",
    },
    # Nvidia Metrics
    {
        "name": "Answer Accuracy",
        "description": "Nvidia metric for measuring answer accuracy",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nvidia", "accuracy"],
        "version": "1.0.0",
    },
    {
        "name": "Context Relevance",
        "description": "Nvidia metric for context relevance evaluation",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nvidia", "relevance"],
        "version": "1.0.0",
    },
    {
        "name": "Response Groundedness",
        "description": "Nvidia metric for response groundedness in context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nvidia", "grounding"],
        "version": "1.0.0",
    },
    # Agent Metrics
    {
        "name": "Topic Adherence",
        "description": "Evaluates if agent stays on topic",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "agent", "topic"],
        "version": "1.0.0",
    },
    {
        "name": "Tool Call Accuracy",
        "description": "Measures accuracy of tool calls made by agent",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "agent", "tools"],
        "version": "1.0.0",
    },
    {
        "name": "Agent Goal Accuracy",
        "description": "Evaluates if agent achieves its stated goals",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "agent", "goals"],
        "version": "1.0.0",
    },
    # NLP Comparison Metrics
    {
        "name": "Factual Correctness",
        "description": "Evaluates factual correctness of generated text",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "factuality"],
        "version": "1.0.0",
    },
    {
        "name": "Semantic Similarity",
        "description": "Measures semantic similarity between texts",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "similarity"],
        "version": "1.0.0",
    },
    {
        "name": "BLEU Score",
        "description": "Traditional BLEU metric for text comparison",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "bleu"],
        "version": "1.0.0",
    },
    {
        "name": "ROUGE Score",
        "description": "Traditional ROUGE metric for text comparison",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "rouge"],
        "version": "1.0.0",
    },
    {
        "name": "String Presence",
        "description": "Checks for presence of specific strings",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.VALIDATOR,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "string"],
        "version": "1.0.0",
    },
    {
        "name": "Exact Match",
        "description": "Validates exact string matching",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.VALIDATOR,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "nlp", "exact"],
        "version": "1.0.0",
    },
    # SQL Metrics
    {
        "name": "SQL Query Equivalence",
        "description": "Checks if SQL queries are equivalent",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.VALIDATOR,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "sql", "equivalence"],
        "version": "1.0.0",
    },
    # General Purpose
    {
        "name": "Aspect Critic",
        "description": "Evaluates specific aspects based on criteria",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "general", "critic"],
        "version": "1.0.0",
    },
    {
        "name": "Simple Criteria Scoring",
        "description": "Scores based on simple criteria",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "general", "scoring"],
        "version": "1.0.0",
    },
    {
        "name": "Rubrics Based Scoring",
        "description": "Evaluates using predefined rubrics",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "general", "rubrics"],
        "version": "1.0.0",
    },
    # Summarization
    {
        "name": "Summarization Score",
        "description": "Evaluates quality of text summarization",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "RagasAdapter",
        "is_public": True,
        "tags": ["ragas", "summarization"],
        "version": "1.0.0",
    },
]


# Combine all vendor evaluations
ALL_VENDOR_EVALUATIONS = DEEPEVAL_EVALUATIONS + RAGAS_EVALUATIONS


async def seed_vendor_evaluations():
    """Seed the evaluation catalog with vendor evaluations"""

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("=" * 70)
        print("Seeding Vendor Evaluations")
        print("=" * 70)

        # Seed DeepEval
        print(f"\n📦 DeepEval Evaluations ({len(DEEPEVAL_EVALUATIONS)} total)")
        print("-" * 70)
        deepeval_created = 0
        for eval_data in DEEPEVAL_EVALUATIONS:
            # Check if evaluation already exists
            query = select(EvaluationCatalog).where(
                EvaluationCatalog.name == eval_data["name"],
                EvaluationCatalog.source == eval_data["source"],
                EvaluationCatalog.adapter_class == eval_data["adapter_class"]
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  {eval_data['name']} (already exists)")
                continue

            # Create new evaluation
            evaluation = EvaluationCatalog(**eval_data)
            session.add(evaluation)
            deepeval_created += 1
            print(f"  ✅ {eval_data['name']}")

        # Seed Ragas
        print(f"\n📦 Ragas Evaluations ({len(RAGAS_EVALUATIONS)} total)")
        print("-" * 70)
        ragas_created = 0
        for eval_data in RAGAS_EVALUATIONS:
            # Check if evaluation already exists
            query = select(EvaluationCatalog).where(
                EvaluationCatalog.name == eval_data["name"],
                EvaluationCatalog.source == eval_data["source"],
                EvaluationCatalog.adapter_class == eval_data["adapter_class"]
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  {eval_data['name']} (already exists)")
                continue

            # Create new evaluation
            evaluation = EvaluationCatalog(**eval_data)
            session.add(evaluation)
            ragas_created += 1
            print(f"  ✅ {eval_data['name']}")

        await session.commit()

        # Summary
        print("\n" + "=" * 70)
        print("📊 Seeding Summary")
        print("=" * 70)
        print(f"DeepEval:  {deepeval_created} created, {len(DEEPEVAL_EVALUATIONS) - deepeval_created} existing")
        print(f"Ragas:     {ragas_created} created, {len(RAGAS_EVALUATIONS) - ragas_created} existing")
        print(f"Total:     {deepeval_created + ragas_created} created")
        print("=" * 70)


async def main():
    """Main entry point"""
    try:
        await seed_vendor_evaluations()
        print("\n✅ Vendor evaluation seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error seeding vendor evaluations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
