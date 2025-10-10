"""
Evaluation Abstraction Layer (EAL) for PromptForge

This module provides a unified interface for running evaluations from multiple sources:
- Vendor evaluations (DeepEval, Ragas, MLflow, etc.)
- Custom client evaluations (business rules, validators)
- PromptForge proprietary evaluations
- LLM-as-Judge evaluations
"""

from app.evaluations.base import (
    EvaluationAdapter,
    EvaluationRequest,
    EvaluationResult,
    EvaluationMetadata,
)
from app.evaluations.registry import EvaluationRegistry

__all__ = [
    "EvaluationAdapter",
    "EvaluationRequest",
    "EvaluationResult",
    "EvaluationMetadata",
    "EvaluationRegistry",
]
