"""
Seed the evaluation catalog with MLflow, Deepchecks, and Arize Phoenix evaluations

This script adds:
- MLflow (20+ metrics)
- Deepchecks (15+ metrics)
- Arize Phoenix (16+ evals)
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


# ==================== MLflow Evaluations ====================

MLFLOW_EVALUATIONS = [
    # Text Quality Metrics
    {
        "name": "Flesch-Kincaid Grade Level",
        "description": "Measures readability based on sentence length and syllables per word",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "readability", "text-quality"],
        "version": "1.0.0",
    },
    {
        "name": "Automated Readability Index (ARI)",
        "description": "Grade level metric based on character count and word count",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "readability", "text-quality"],
        "version": "1.0.0",
    },
    # Question Answering Metrics
    {
        "name": "Exact Match",
        "description": "Binary metric checking if prediction exactly matches reference",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.VALIDATOR,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "qa", "exact-match"],
        "version": "1.0.0",
    },
    {
        "name": "ROUGE-1",
        "description": "Unigram overlap between generated and reference text",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "rouge", "summarization"],
        "version": "1.0.0",
    },
    {
        "name": "ROUGE-2",
        "description": "Bigram overlap between generated and reference text",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "rouge", "summarization"],
        "version": "1.0.0",
    },
    {
        "name": "ROUGE-L",
        "description": "Longest common subsequence between generated and reference text",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "rouge", "summarization"],
        "version": "1.0.0",
    },
    {
        "name": "BLEU Score",
        "description": "Precision-based metric for machine translation quality",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "bleu", "translation"],
        "version": "1.0.0",
    },
    {
        "name": "Toxicity Score",
        "description": "Measures toxicity level in generated text using Perspective API",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "safety", "toxicity"],
        "version": "1.0.0",
    },
    {
        "name": "Token Count",
        "description": "Counts number of tokens in generated text",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "performance", "tokens"],
        "version": "1.0.0",
    },
    {
        "name": "Latency",
        "description": "Measures response time for generation",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "performance", "latency"],
        "version": "1.0.0",
    },
    # GenAI Metrics
    {
        "name": "Answer Correctness",
        "description": "Evaluates semantic correctness of generated answers",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "genai", "correctness"],
        "version": "1.0.0",
    },
    {
        "name": "Answer Relevance",
        "description": "Measures relevance of answer to the question",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "genai", "relevance"],
        "version": "1.0.0",
    },
    {
        "name": "Answer Similarity",
        "description": "Semantic similarity between generated and reference answers",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "genai", "similarity"],
        "version": "1.0.0",
    },
    {
        "name": "Faithfulness",
        "description": "Checks if answer is faithful to the provided context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "genai", "faithfulness"],
        "version": "1.0.0",
    },
    {
        "name": "Relevance",
        "description": "Overall relevance metric for generated content",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "genai", "relevance"],
        "version": "1.0.0",
    },
    # Retrieval Metrics
    {
        "name": "Precision at K",
        "description": "Precision of top-K retrieved documents",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "retrieval", "precision"],
        "version": "1.0.0",
    },
    {
        "name": "Recall at K",
        "description": "Recall of top-K retrieved documents",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "retrieval", "recall"],
        "version": "1.0.0",
    },
    {
        "name": "NDCG at K",
        "description": "Normalized Discounted Cumulative Gain for ranking quality",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "MLflowAdapter",
        "is_public": True,
        "tags": ["mlflow", "retrieval", "ranking"],
        "version": "1.0.0",
    },
]


# ==================== Deepchecks Evaluations ====================

DEEPCHECKS_EVALUATIONS = [
    # Core Quality Properties
    {
        "name": "Fluency",
        "description": "Evaluates how well-formed and grammatically correct the text is",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "quality", "fluency"],
        "version": "1.0.0",
    },
    {
        "name": "Coherence",
        "description": "Measures logical flow and coherence of generated text",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "quality", "coherence"],
        "version": "1.0.0",
    },
    {
        "name": "Completeness",
        "description": "Evaluates if the response fully addresses the question",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "quality", "completeness"],
        "version": "1.0.0",
    },
    {
        "name": "Grounded in Context",
        "description": "Checks if answer is grounded in the provided context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "quality", "grounding"],
        "version": "1.0.0",
    },
    {
        "name": "Avoided Answer Detection",
        "description": "Detects if model avoided answering the question",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "quality", "avoidance"],
        "version": "1.0.0",
    },
    # Safety Properties
    {
        "name": "Toxicity Detection",
        "description": "Detects toxic, harmful, or offensive content",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "safety", "toxicity"],
        "version": "1.0.0",
    },
    {
        "name": "Bias Detection",
        "description": "Identifies biased content in model outputs",
        "category": EvaluationCategory.BIAS,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "bias", "fairness"],
        "version": "1.0.0",
    },
    {
        "name": "PII Leakage",
        "description": "Detects personally identifiable information in outputs",
        "category": EvaluationCategory.SECURITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "security", "pii"],
        "version": "1.0.0",
    },
    # Statistical Metrics
    {
        "name": "BLEU Score",
        "description": "Statistical word-based comparison metric",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "statistical", "bleu"],
        "version": "1.0.0",
    },
    {
        "name": "ROUGE Score",
        "description": "Statistical overlap-based metric for summarization",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "statistical", "rouge"],
        "version": "1.0.0",
    },
    {
        "name": "METEOR Score",
        "description": "Harmonic mean of precision and recall with synonym matching",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "statistical", "meteor"],
        "version": "1.0.0",
    },
    {
        "name": "Levenshtein Distance",
        "description": "Character-based edit distance metric",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "statistical", "levenshtein"],
        "version": "1.0.0",
    },
    # Model-Based Metrics
    {
        "name": "BERTScore",
        "description": "Embedding-based similarity using BERT",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "embedding", "bert"],
        "version": "1.0.0",
    },
    {
        "name": "Semantic Similarity",
        "description": "Measures semantic similarity using embeddings",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "embedding", "similarity"],
        "version": "1.0.0",
    },
    {
        "name": "Hallucination Detection",
        "description": "Detects hallucinated or fabricated information",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "DeepchecksAdapter",
        "is_public": True,
        "tags": ["deepchecks", "safety", "hallucination"],
        "version": "1.0.0",
    },
]


# ==================== Arize Phoenix Evaluations ====================

ARIZE_PHOENIX_EVALUATIONS = [
    # RAG Evaluations
    {
        "name": "Hallucination Detection",
        "description": "Detects hallucinations in LLM outputs using Phoenix",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "safety", "hallucination"],
        "version": "1.0.0",
    },
    {
        "name": "Q&A on Retrieved Data",
        "description": "Evaluates quality of Q&A based on retrieved context",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "rag", "qa"],
        "version": "1.0.0",
    },
    {
        "name": "Retrieval Relevance",
        "description": "Evaluates relevance of retrieved documents for RAG",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "rag", "retrieval"],
        "version": "1.0.0",
    },
    {
        "name": "Summarization Evaluation",
        "description": "Evaluates quality of text summarization",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "summarization"],
        "version": "1.0.0",
    },
    # Code & SQL
    {
        "name": "Code Generation Evaluation",
        "description": "Evaluates quality and correctness of generated code",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "code", "generation"],
        "version": "1.0.0",
    },
    {
        "name": "SQL Generation Evaluation",
        "description": "Evaluates correctness of generated SQL queries",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "sql", "generation"],
        "version": "1.0.0",
    },
    # Safety
    {
        "name": "Toxicity Assessment",
        "description": "Assesses toxicity levels in generated content",
        "category": EvaluationCategory.SAFETY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "safety", "toxicity"],
        "version": "1.0.0",
    },
    {
        "name": "Reference Link Verification",
        "description": "Verifies accuracy of citation and reference links",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.VALIDATOR,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "citation", "verification"],
        "version": "1.0.0",
    },
    # User Experience
    {
        "name": "User Frustration Detection",
        "description": "Detects signs of user frustration in interactions",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "ux", "frustration"],
        "version": "1.0.0",
    },
    {
        "name": "AI vs Human Comparison",
        "description": "Compares AI outputs against human ground truth",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "comparison", "groundtruth"],
        "version": "1.0.0",
    },
    # Agent Evaluations
    {
        "name": "Agent Function Calling",
        "description": "Evaluates correctness of agent function/tool calling",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "agent", "function-calling"],
        "version": "1.0.0",
    },
    {
        "name": "Agent Path Convergence",
        "description": "Evaluates if agent converges to optimal solution path",
        "category": EvaluationCategory.PERFORMANCE,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "agent", "convergence"],
        "version": "1.0.0",
    },
    {
        "name": "Agent Planning",
        "description": "Evaluates quality of agent planning and reasoning",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "agent", "planning"],
        "version": "1.0.0",
    },
    {
        "name": "Agent Reflection",
        "description": "Evaluates agent's ability to reflect and self-correct",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "agent", "reflection"],
        "version": "1.0.0",
    },
    # Multimodal
    {
        "name": "Audio Emotion Detection",
        "description": "Detects emotions from audio inputs",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.CLASSIFIER,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "audio", "emotion"],
        "version": "1.0.0",
    },
    # Heuristics
    {
        "name": "Heuristic Metrics",
        "description": "Collection of rule-based heuristic evaluation metrics",
        "category": EvaluationCategory.QUALITY,
        "source": EvaluationSource.VENDOR,
        "evaluation_type": EvaluationType.METRIC,
        "adapter_class": "ArizePhoenixAdapter",
        "is_public": True,
        "tags": ["phoenix", "heuristic"],
        "version": "1.0.0",
    },
]


# Combine all additional vendor evaluations
ALL_ADDITIONAL_EVALUATIONS = MLFLOW_EVALUATIONS + DEEPCHECKS_EVALUATIONS + ARIZE_PHOENIX_EVALUATIONS


async def seed_additional_vendors():
    """Seed the evaluation catalog with MLflow, Deepchecks, and Arize Phoenix evaluations"""

    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("=" * 70)
        print("Seeding Additional Vendor Evaluations")
        print("=" * 70)

        # Seed MLflow
        print(f"\n📦 MLflow Evaluations ({len(MLFLOW_EVALUATIONS)} total)")
        print("-" * 70)
        mlflow_created = 0
        for eval_data in MLFLOW_EVALUATIONS:
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
            mlflow_created += 1
            print(f"  ✅ {eval_data['name']}")

        # Seed Deepchecks
        print(f"\n📦 Deepchecks Evaluations ({len(DEEPCHECKS_EVALUATIONS)} total)")
        print("-" * 70)
        deepchecks_created = 0
        for eval_data in DEEPCHECKS_EVALUATIONS:
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
            deepchecks_created += 1
            print(f"  ✅ {eval_data['name']}")

        # Seed Arize Phoenix
        print(f"\n📦 Arize Phoenix Evaluations ({len(ARIZE_PHOENIX_EVALUATIONS)} total)")
        print("-" * 70)
        phoenix_created = 0
        for eval_data in ARIZE_PHOENIX_EVALUATIONS:
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
            phoenix_created += 1
            print(f"  ✅ {eval_data['name']}")

        await session.commit()

        # Summary
        print("\n" + "=" * 70)
        print("📊 Seeding Summary")
        print("=" * 70)
        print(f"MLflow:      {mlflow_created} created, {len(MLFLOW_EVALUATIONS) - mlflow_created} existing")
        print(f"Deepchecks:  {deepchecks_created} created, {len(DEEPCHECKS_EVALUATIONS) - deepchecks_created} existing")
        print(f"Arize Phoenix: {phoenix_created} created, {len(ARIZE_PHOENIX_EVALUATIONS) - phoenix_created} existing")
        print(f"Total:       {mlflow_created + deepchecks_created + phoenix_created} created")
        print("=" * 70)


async def main():
    """Main entry point"""
    try:
        await seed_additional_vendors()
        print("\n✅ Additional vendor evaluation seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error seeding additional vendor evaluations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
