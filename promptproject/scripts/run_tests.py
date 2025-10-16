#!/usr/bin/env python3
"""
Enhanced Test Runner with Detailed Reporting
Provides structured output and comprehensive test explanations

Usage:
    python scripts/run_tests.py                    # Run all tests
    python scripts/run_tests.py --suite golden     # Run specific suite
    python scripts/run_tests.py --verbose          # Detailed output
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import json

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent

    def print_header(self, text: str, color=Colors.BLUE):
        """Print formatted header"""
        print(f"\n{color}{Colors.BOLD}{'=' * 80}{Colors.END}")
        print(f"{color}{Colors.BOLD}{text:^80}{Colors.END}")
        print(f"{color}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

    def print_section(self, text: str):
        """Print section header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 78}{Colors.END}")

    def print_test_info(self, category: str, description: str, count: int):
        """Print test category information"""
        print(f"{Colors.BOLD}{category}{Colors.END} ({count} tests)")
        print(f"  {description}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")

    def print_failure(self, text: str):
        """Print failure message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

    def run_test_suite(self, suite: str = "all"):
        """Run tests with enhanced reporting"""

        # Print test overview
        self.print_header("PROMPT EVALUATION TEST SUITE", Colors.BLUE)

        print(f"{Colors.BOLD}Project:{Colors.END} PromptProject - AI Fact Extraction Pipeline")
        print(f"{Colors.BOLD}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}Test Suite:{Colors.END} {suite.upper()}")
        print(f"{Colors.BOLD}Environment:{Colors.END} Python 3.13 + Anthropic Claude + OpenAI GPT")

        # Explain test categories
        self.print_section("TEST CATEGORIES")

        self.print_test_info(
            "🎯 GUARDRAILS VALIDATION TESTS",
            "Validates Guardrails AI framework with Pydantic models, PII detection, and business logic",
            17
        )
        print(f"    • Schema validation (age ranges, enums, required fields)")
        print(f"    • PII detection with Presidio (SSN, phone, email)")
        print(f"    • Business logic (retirement age, timeline consistency)")
        print(f"    • Integration & edge cases\n")

        self.print_test_info(
            "🌟 GOLDEN DATASET TESTS",
            "Core functionality validation on known-good examples (Target: ≥95% accuracy)",
            3
        )
        print(f"    • Retirement planning extraction")
        print(f"    • Risk tolerance classification")
        print(f"    • Financial goals extraction\n")

        self.print_test_info(
            "⚠️  EDGE CASE TESTS",
            "Boundary conditions and unusual inputs (Target: ≥85% accuracy)",
            5
        )
        print(f"    • Incomplete conversations")
        print(f"    • Ambiguous risk signals")
        print(f"    • Multiple clients scenarios")
        print(f"    • Very long transcripts")
        print(f"    • Missing critical data\n")

        self.print_test_info(
            "🛡️  ADVERSARIAL TESTS",
            "Security and robustness against malicious inputs (Target: 100% pass rate)",
            7
        )
        print(f"    • Prompt injection attacks")
        print(f"    • Role confusion attempts")
        print(f"    • PII leakage prevention")
        print(f"    • Unethical advice detection")
        print(f"    • Format manipulation resistance")
        print(f"    • Extreme value handling")
        print(f"    • Bias detection\n")

        self.print_test_info(
            "📋 POLICY COMPLIANCE TESTS",
            "Business policy and regulatory requirements validation",
            2
        )
        print(f"    • Compliance factors documentation")
        print(f"    • Quality metrics thresholds\n")

        self.print_test_info(
            "🔄 REGRESSION PREVENTION TESTS",
            "Ensures changes don't break existing functionality",
            1
        )
        print(f"    • Golden dataset baseline validation\n")

        # Run tests
        self.print_header("EXECUTING TEST SUITE", Colors.CYAN)

        start_time = time.time()

        # Build pytest command
        cmd = [
            "pytest",
            str(self.project_root / "tests"),
            "-v",
            "--tb=short",
            "--color=yes"
        ]

        if suite != "all":
            cmd.extend(["-k", suite])

        if self.verbose:
            cmd.append("-vv")

        # Run tests
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.project_root)
        )

        elapsed_time = time.time() - start_time

        # Parse results
        output_lines = result.stdout.split('\n')

        # Extract test results
        passed = failed = 0
        test_results = {
            "guardrails": {"passed": 0, "failed": 0, "tests": []},
            "golden": {"passed": 0, "failed": 0, "tests": []},
            "edge": {"passed": 0, "failed": 0, "tests": []},
            "adversarial": {"passed": 0, "failed": 0, "tests": []},
            "policy": {"passed": 0, "failed": 0, "tests": []},
            "regression": {"passed": 0, "failed": 0, "tests": []}
        }

        for line in output_lines:
            if "PASSED" in line or "FAILED" in line:
                is_passed = "PASSED" in line

                # Categorize test
                if "guardrails_validation" in line:
                    category = "guardrails"
                elif "test_golden" in line:
                    category = "golden"
                elif "test_edge" in line:
                    category = "edge"
                elif "test_adversarial" in line:
                    category = "adversarial"
                elif "test_policy" in line:
                    category = "policy"
                elif "test_regression" in line:
                    category = "regression"
                else:
                    continue

                if is_passed:
                    test_results[category]["passed"] += 1
                    passed += 1
                else:
                    test_results[category]["failed"] += 1
                    failed += 1

                test_results[category]["tests"].append({
                    "name": line.split("::")[1].split()[0] if "::" in line else "unknown",
                    "status": "PASSED" if is_passed else "FAILED"
                })

        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Print detailed results by category
        self.print_header("TEST RESULTS BY CATEGORY", Colors.CYAN)

        for category, results in test_results.items():
            if results["passed"] + results["failed"] == 0:
                continue

            category_name = category.upper().replace("_", " ")
            category_passed = results["passed"]
            category_total = results["passed"] + results["failed"]
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0

            if category_rate == 100:
                status_icon = "✓"
                status_color = Colors.GREEN
            elif category_rate >= 80:
                status_icon = "⚠"
                status_color = Colors.YELLOW
            else:
                status_icon = "✗"
                status_color = Colors.RED

            print(f"\n{status_color}{status_icon} {category_name}:{Colors.END} {category_passed}/{category_total} tests passed ({category_rate:.1f}%)")

            if self.verbose or results["failed"] > 0:
                for test in results["tests"]:
                    status_symbol = "✓" if test["status"] == "PASSED" else "✗"
                    status_color = Colors.GREEN if test["status"] == "PASSED" else Colors.RED
                    print(f"    {status_color}{status_symbol} {test['name']}{Colors.END}")

        # Print summary
        self.print_header("TEST EXECUTION SUMMARY", Colors.BLUE)

        print(f"{Colors.BOLD}Total Tests:{Colors.END} {total}")
        print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {passed}")

        if failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.END} {failed}")
        else:
            print(f"{Colors.BOLD}Failed:{Colors.END} 0")

        print(f"{Colors.BOLD}Pass Rate:{Colors.END} {pass_rate:.1f}%")
        print(f"{Colors.BOLD}Execution Time:{Colors.END} {elapsed_time:.2f} seconds ({elapsed_time/60:.1f} minutes)")

        # Final status
        if pass_rate == 100:
            self.print_header("✓ ALL TESTS PASSED - READY FOR DEPLOYMENT", Colors.GREEN)

            print(f"{Colors.GREEN}{Colors.BOLD}🎉 Validation Complete!{Colors.END}")
            print(f"\n{Colors.GREEN}All evaluation pipelines are operational:{Colors.END}")
            print(f"  ✓ Claude API integration working")
            print(f"  ✓ DeepEval metrics passing (Faithfulness, Bias)")
            print(f"  ✓ Guardrails validation enforced")
            print(f"  ✓ PII detection active (Presidio)")
            print(f"  ✓ Business logic validated")
            print(f"  ✓ Schema compliance verified")
            print(f"\n{Colors.GREEN}{Colors.BOLD}The prompt evaluation system is production-ready!{Colors.END}\n")

        elif pass_rate >= 90:
            self.print_header("⚠ MOSTLY PASSING - REVIEW FAILURES", Colors.YELLOW)
            self.print_warning(f"{failed} test(s) failed. Review output above for details.")

        else:
            self.print_header("✗ VALIDATION FAILED - BLOCKING DEPLOYMENT", Colors.RED)
            self.print_failure(f"Pass rate {pass_rate:.1f}% is below acceptable threshold (90%)")
            self.print_failure(f"{failed} test(s) failed. Fix issues before deployment.")

        # API Usage Note
        print(f"\n{Colors.BOLD}API Usage:{Colors.END}")
        print(f"  • Anthropic Claude API calls: ~{total} requests")
        print(f"  • OpenAI GPT calls (DeepEval): ~{test_results['golden']['passed'] + test_results['policy']['passed']} requests")
        print(f"  • Estimated cost: ~${(total * 0.01):.2f} (approximate)")

        # Next steps
        if failed > 0:
            print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
            print(f"  1. Review failed test details above")
            print(f"  2. Fix issues in prompts or validation logic")
            print(f"  3. Re-run: python scripts/run_tests.py")
            print(f"  4. Commit changes when all tests pass")

        return result.returncode


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run prompt evaluation tests with enhanced reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                    # Run all tests
  python scripts/run_tests.py --suite golden     # Run only golden tests
  python scripts/run_tests.py --suite edge       # Run only edge case tests
  python scripts/run_tests.py --verbose          # Detailed test output
  python scripts/run_tests.py --suite adversarial # Run security tests
        """
    )

    parser.add_argument(
        "--suite",
        choices=["all", "golden", "edge", "adversarial", "policy", "guardrails"],
        default="all",
        help="Test suite to run"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed test output"
    )

    args = parser.parse_args()

    # Check for required environment variables
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{Colors.RED}Error: ANTHROPIC_API_KEY not set{Colors.END}")
        print(f"Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.YELLOW}Warning: OPENAI_API_KEY not set{Colors.END}")
        print(f"DeepEval metrics will fail without OpenAI API key")
        print(f"Set it with: export OPENAI_API_KEY='your-key-here'")
        print(f"Continuing anyway...\n")

    runner = TestRunner(verbose=args.verbose)
    exit_code = runner.run_test_suite(suite=args.suite)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
