#!/usr/bin/env python3
"""
Script to update all LLM-based DeepEval metrics with database API key support.

This script adds the _setup_api_key() call to all metrics that use LLMs.
"""

import re

# File to update
FILE_PATH = "/Users/rohitiyer/datagrub/promptforge/api-tier/app/evaluations/adapters/deepeval.py"

# Metrics that need API key setup (use LLMs)
LLM_METRICS = [
    "_evaluate_contextual_relevancy",
    "_evaluate_contextual_recall",
    "_evaluate_contextual_precision",
    "_evaluate_bias",
    "_evaluate_toxicity",
    "_evaluate_hallucination",
]

# Template for API key setup code
API_KEY_SETUP = '''        model = request.config.get("model", "gpt-4")

        # Setup API key from database (with env fallback)
        api_key = await self._setup_api_key(model, request)
        if not api_key:
            return EvaluationResult(
                score=0.0,
                passed=False,
                reason=f"API key not configured for model: {model}",
                details={"error": "Missing API key configuration"}
            )

'''

def update_metric(content, metric_name):
    """Update a single metric method to include API key setup"""

    # Pattern to find the metric method
    # Match from method definition to the metric instantiation line
    pattern = rf'(async def {metric_name}\(self, request: EvaluationRequest\) -> EvaluationResult:.*?""".*?""")\n(\s+)(from .+?\n.+?\n\n\s+)(metric = )'

    def replacer(match):
        method_start = match.group(1)  # Method def and docstring
        indent = match.group(2)  # Indentation
        imports = match.group(3)  # Import statements
        metric_start = match.group(4)  # "metric = "

        # Insert API key setup after imports, before metric instantiation
        return f"{method_start}\n{imports}\n{API_KEY_SETUP}{indent}{metric_start}"

    # Apply replacement
    updated_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

    # Also need to update the metric instantiation to use `model` variable instead of request.config.get
    # Change: model=request.config.get("model", "gpt-4")
    # To: model=model
    metric_instantiation_pattern = rf'({metric_name}.*?metric = \w+Metric\([^)]*?)model=request\.config\.get\("model", "gpt-4"\)'
    updated_content = re.sub(
        metric_instantiation_pattern,
        r'\1model=model',
        updated_content,
        flags=re.DOTALL
    )

    return updated_content

def main():
    print("Reading DeepEval adapter file...")
    with open(FILE_PATH, 'r') as f:
        content = f.read()

    original_content = content

    # Update each LLM-based metric
    for metric_name in LLM_METRICS:
        print(f"Updating {metric_name}...")
        content = update_metric(content, metric_name)

    # Check if any changes were made
    if content == original_content:
        print("No changes needed - metrics already updated or pattern not found")
        return

    # Write updated content
    print(f"Writing updated file to {FILE_PATH}...")
    with open(FILE_PATH, 'w') as f:
        f.write(content)

    print("✅ Successfully updated all LLM-based DeepEval metrics!")
    print(f"Updated {len(LLM_METRICS)} metrics:")
    for metric in LLM_METRICS:
        print(f"  - {metric}")

if __name__ == "__main__":
    main()
