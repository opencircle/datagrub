#!/usr/bin/env python3
"""
Vendor Library Verification Script

This script verifies that all required vendor evaluation libraries are properly
installed and functional in the Docker environment.

Usage:
    python verify_vendor_libraries.py [--detailed]

Exit codes:
    0 - All required libraries verified
    1 - One or more required libraries missing
    2 - Import errors or compatibility issues
"""

import sys
import importlib
from typing import Dict, List, Tuple, Optional
import json


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {text}")


def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {text}")


def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")


def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {text}")


def verify_library(
    module_name: str,
    display_name: str,
    required: bool = True,
    expected_evaluations: int = 0
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Verify a single library installation

    Args:
        module_name: Python module name to import
        display_name: Human-readable library name
        required: Whether this library is required
        expected_evaluations: Number of evaluations this library provides

    Returns:
        Tuple of (success, version, error_message)
    """
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")

        status = "REQUIRED" if required else "OPTIONAL"
        evals = f" ({expected_evaluations} evaluations)" if expected_evaluations > 0 else ""
        print_success(f"{display_name}: {version} [{status}]{evals}")

        return True, version, None
    except ImportError as e:
        if required:
            print_error(f"{display_name}: Import failed - {e}")
        else:
            print_warning(f"{display_name}: Not available - {e}")
        return False, None, str(e)
    except Exception as e:
        print_error(f"{display_name}: Unexpected error - {e}")
        return False, None, str(e)


def verify_adapter_availability() -> Dict[str, bool]:
    """
    Verify that all adapter classes can be instantiated

    Returns:
        Dictionary of adapter name to availability status
    """
    print_header("Verifying Adapter Availability")

    adapter_results = {}

    # Import base classes
    try:
        from app.evaluations.base import EvaluationAdapter
        print_success("Base EvaluationAdapter imported")
    except ImportError as e:
        print_error(f"Cannot import base adapter: {e}")
        return {}

    # Test each adapter
    adapters_to_test = [
        ("app.evaluations.adapters.promptforge", "PromptForgeAdapter", "PromptForge", 6),
        ("app.evaluations.adapters.deepeval", "DeepEvalAdapter", "DeepEval", 15),
        ("app.evaluations.adapters.ragas", "RagasAdapter", "Ragas", 23),
        ("app.evaluations.adapters.mlflow", "MLflowAdapter", "MLflow", 18),
        ("app.evaluations.adapters.vendor_simplified", "DeepchecksAdapter", "Deepchecks", 15),
        ("app.evaluations.adapters.vendor_simplified", "ArizePhoenixAdapter", "Phoenix", 16),
        ("app.evaluations.adapters.custom", "CustomEvaluatorAdapter", "Custom", 0),
        ("app.evaluations.adapters.llm_judge", "LLMJudgeAdapter", "LLM-Judge", 0),
    ]

    for module_path, class_name, display_name, eval_count in adapters_to_test:
        try:
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            adapter = adapter_class()

            # Check if adapter reports availability
            is_available = adapter.is_available()

            evals = f" ({eval_count} evaluations)" if eval_count > 0 else ""
            if is_available:
                print_success(f"{display_name} adapter: Available{evals}")
                adapter_results[display_name] = True
            else:
                print_warning(f"{display_name} adapter: Created but library not available{evals}")
                adapter_results[display_name] = False

        except Exception as e:
            print_error(f"{display_name} adapter: Failed - {e}")
            adapter_results[display_name] = False

    return adapter_results


def verify_registry() -> bool:
    """
    Verify the evaluation registry is working properly

    Returns:
        True if registry is functional
    """
    print_header("Verifying Evaluation Registry")

    try:
        from app.evaluations.registry import registry
        from app.models.evaluation_catalog import EvaluationSource

        # Check adapter count
        total_adapters = len(registry._adapters)
        print_info(f"Total adapters registered: {total_adapters}")

        if total_adapters == 0:
            print_error("No adapters registered in registry!")
            return False

        # List all adapters
        print_info("Registered adapters:")
        for adapter_name in registry._adapters.keys():
            print(f"  - {adapter_name}")

        # Check adapters by source
        print_info("\nAdapters by source:")
        for source, adapters in registry._adapters_by_source.items():
            print(f"  - {source.value}: {len(adapters)} adapter(s)")
            for adapter in adapters:
                available = adapter.is_available()
                status = "✓" if available else "✗"
                print(f"    {status} {adapter.__class__.__name__}")

        print_success("Registry is functional")
        return True

    except Exception as e:
        print_error(f"Registry verification failed: {e}")
        return False


def main():
    """Main verification workflow"""
    detailed = "--detailed" in sys.argv

    print_header("PromptForge Vendor Library Verification")
    print_info("Verifying all vendor evaluation libraries...")
    print()

    results = {
        "required": {},
        "optional": {},
        "adapters": {},
        "registry": False,
        "summary": {}
    }

    #
    # Phase 1: Verify Core Vendor Libraries
    #
    print_header("Phase 1: Core Vendor Evaluation Libraries")

    core_libraries = [
        ("deepeval", "DeepEval", True, 15),
        ("ragas", "Ragas", True, 23),
        ("mlflow", "MLflow", True, 18),
    ]

    for module_name, display_name, required, evals in core_libraries:
        success, version, error = verify_library(module_name, display_name, required, evals)
        results["required"][display_name] = {
            "status": "OK" if success else "FAILED",
            "version": version,
            "error": error,
            "evaluations": evals
        }

    print()

    #
    # Phase 2: Verify Optional Vendor Libraries
    #
    print_header("Phase 2: Optional Vendor Libraries")

    optional_libraries = [
        ("deepchecks_client", "Deepchecks LLM Client", False, 15),
        ("phoenix", "Arize Phoenix", False, 16),
    ]

    for module_name, display_name, required, evals in optional_libraries:
        success, version, error = verify_library(module_name, display_name, required, evals)
        results["optional"][display_name] = {
            "status": "OK" if success else "MISSING",
            "version": version,
            "error": error,
            "evaluations": evals
        }

    print()

    #
    # Phase 3: Verify Support Libraries
    #
    print_header("Phase 3: Support Libraries")

    support_libraries = [
        ("datasets", "Datasets", True, 0),
        ("nest_asyncio", "nest-asyncio", True, 0),
        ("textstat", "textstat", False, 0),
        ("rouge_score", "rouge-score", False, 0),
        ("tiktoken", "tiktoken", False, 0),
        ("nltk", "NLTK", False, 0),
        ("sqlparse", "sqlparse", False, 0),
    ]

    for module_name, display_name, required, _ in support_libraries:
        success, version, error = verify_library(module_name, display_name, required, 0)
        category = "required" if required else "optional"
        results[category][display_name] = {
            "status": "OK" if success else ("FAILED" if required else "MISSING"),
            "version": version,
            "error": error
        }

    print()

    #
    # Phase 4: Verify Adapters (if detailed mode)
    #
    if detailed:
        adapter_results = verify_adapter_availability()
        results["adapters"] = adapter_results
        print()

        # Phase 5: Verify Registry
        registry_ok = verify_registry()
        results["registry"] = registry_ok
        print()

    #
    # Generate Summary
    #
    print_header("Verification Summary")

    required_ok = sum(1 for r in results["required"].values() if r["status"] == "OK")
    required_total = len(results["required"])

    optional_ok = sum(1 for r in results["optional"].values() if r["status"] == "OK")
    optional_total = len(results["optional"])

    total_evaluations = sum(
        r.get("evaluations", 0)
        for category in ["required", "optional"]
        for r in results[category].values()
        if r["status"] == "OK"
    )

    results["summary"] = {
        "required_libraries": f"{required_ok}/{required_total}",
        "optional_libraries": f"{optional_ok}/{optional_total}",
        "total_evaluations_available": total_evaluations,
        "maximum_evaluations": 87  # 15+23+18+15+16
    }

    print_info(f"Required libraries: {required_ok}/{required_total}")
    print_info(f"Optional libraries: {optional_ok}/{optional_total}")
    print_info(f"Total vendor evaluations available: {total_evaluations}/87")

    if detailed and results["adapters"]:
        adapters_ok = sum(1 for available in results["adapters"].values() if available)
        adapters_total = len(results["adapters"])
        print_info(f"Adapters available: {adapters_ok}/{adapters_total}")

        if results["registry"]:
            print_success("Registry is functional")
        else:
            print_error("Registry is not functional")

    print()

    # Determine exit code
    if required_ok < required_total:
        failed = [name for name, r in results["required"].items() if r["status"] != "OK"]
        print_error(f"Verification FAILED: {len(failed)} required library(ies) missing")
        for lib in failed:
            print(f"  - {lib}")
        exit_code = 1
    else:
        print_success("Verification PASSED: All required libraries installed")

        if optional_ok < optional_total:
            missing = [name for name, r in results["optional"].items() if r["status"] != "OK"]
            print_warning(f"{len(missing)} optional library(ies) not available:")
            for lib in missing:
                print(f"  - {lib}")

        exit_code = 0

    # Write JSON report
    try:
        with open("/tmp/vendor_verification_report.json", "w") as f:
            json.dump(results, f, indent=2)
        print_info("\nDetailed report saved to: /tmp/vendor_verification_report.json")
    except Exception as e:
        print_warning(f"Could not save report: {e}")

    print()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
