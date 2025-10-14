#!/usr/bin/env python3
"""
Prompt Validation Build Script
Runs comprehensive validation pipeline:
1. Schema validation
2. Guardrails safety checks
3. DeepEval test execution
4. Policy compliance verification

Usage:
    python scripts/validate_prompts.py
    python scripts/validate_prompts.py --test-suite golden
    python scripts/validate_prompts.py --policy-check-only
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
import subprocess
from datetime import datetime
from jsonschema import validate, ValidationError

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from guardrails.fact_extraction_guard import FactExtractionGuard


class Color:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class PromptValidator:
    """Orchestrates all validation steps"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "schema_validation": {},
            "guardrails_validation": {},
            "deepeval_tests": {},
            "policy_compliance": {},
            "overall_status": "UNKNOWN"
        }

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Color.BLUE}{Color.BOLD}{'=' * 80}{Color.END}")
        print(f"{Color.BLUE}{Color.BOLD}{text:^80}{Color.END}")
        print(f"{Color.BLUE}{Color.BOLD}{'=' * 80}{Color.END}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Color.GREEN}✓ {text}{Color.END}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Color.RED}✗ {text}{Color.END}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Color.YELLOW}⚠ {text}{Color.END}")

    def validate_schema_files(self) -> bool:
        """Step 1: Validate all JSON schema files"""
        self.print_header("STEP 1: JSON Schema Validation")

        schema_dir = PROJECT_ROOT / "schemas"
        all_valid = True

        for schema_file in schema_dir.glob("*.json"):
            try:
                with open(schema_file) as f:
                    schema = json.load(f)

                # Validate it's a valid JSON Schema
                if "$schema" in schema:
                    self.print_success(f"Schema valid: {schema_file.name}")
                else:
                    self.print_warning(f"Missing $schema field: {schema_file.name}")

                self.results["schema_validation"][schema_file.name] = {
                    "valid": True,
                    "file": str(schema_file)
                }

            except json.JSONDecodeError as e:
                self.print_error(f"Invalid JSON in {schema_file.name}: {e}")
                all_valid = False
                self.results["schema_validation"][schema_file.name] = {
                    "valid": False,
                    "error": str(e)
                }

        return all_valid

    def validate_prompt_specs(self) -> bool:
        """Step 2: Validate prompt specification YAML files"""
        self.print_header("STEP 2: Prompt Specification Validation")

        prompt_dir = PROJECT_ROOT / "prompts"
        all_valid = True

        for prompt_file in prompt_dir.glob("*.yaml"):
            try:
                with open(prompt_file) as f:
                    prompt_spec = yaml.safe_load(f)

                # Check required fields
                required_fields = [
                    "metadata", "model_config", "schemas",
                    "prompt_template", "guardrails", "evaluations"
                ]

                missing = [field for field in required_fields if field not in prompt_spec]

                if missing:
                    self.print_error(f"{prompt_file.name}: Missing fields: {missing}")
                    all_valid = False
                else:
                    self.print_success(f"Prompt spec valid: {prompt_file.name}")

                # Verify schema references exist
                for schema_type, schema_path in prompt_spec.get("schemas", {}).items():
                    schema_file = PROJECT_ROOT / "prompts" / schema_path
                    if not schema_file.exists():
                        self.print_error(f"{prompt_file.name}: Referenced schema not found: {schema_path}")
                        all_valid = False

                self.results["schema_validation"][prompt_file.name] = {
                    "valid": not missing,
                    "missing_fields": missing
                }

            except yaml.YAMLError as e:
                self.print_error(f"Invalid YAML in {prompt_file.name}: {e}")
                all_valid = False
                self.results["schema_validation"][prompt_file.name] = {
                    "valid": False,
                    "error": str(e)
                }

        return all_valid

    def run_guardrails_checks(self) -> bool:
        """Step 3: Run Guardrails AI validation tests"""
        self.print_header("STEP 3: Guardrails AI Safety Checks")

        try:
            guard = FactExtractionGuard()
            self.print_success("Guardrails initialized successfully")

            # Test with sample valid output
            sample_output = json.dumps({
                "conversation_id": "conv_test123",
                "client_demographics": {"client_age": 55, "employment_status": "employed"},
                "financial_goals": {"retirement_age": 65, "financial_goals": []},
                "financial_situation": {},
                "risk_profile": {"risk_tolerance": "moderate"},
                "compliance_markers": {
                    "suitability_factors_discussed": True,
                    "investment_objectives_documented": True,
                    "disclosures_made": []
                }
            })

            result = guard.validate(sample_output)

            if result["valid"]:
                self.print_success("Sample output passed Guardrails validation")
                self.results["guardrails_validation"] = {
                    "status": "PASSED",
                    "pii_detection_enabled": True,
                    "schema_enforcement_enabled": True
                }
                return True
            else:
                self.print_error(f"Sample output failed: {result['errors']}")
                self.results["guardrails_validation"] = {
                    "status": "FAILED",
                    "errors": result["errors"]
                }
                return False

        except Exception as e:
            self.print_error(f"Guardrails check failed: {e}")
            self.results["guardrails_validation"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def run_deepeval_tests(self, test_suite: str = "all") -> bool:
        """Step 4: Run DeepEval test suite"""
        self.print_header(f"STEP 4: DeepEval Test Execution ({test_suite})")

        test_file = PROJECT_ROOT / "tests" / "test_fact_extraction.py"

        if not test_file.exists():
            self.print_error(f"Test file not found: {test_file}")
            return False

        # Build pytest command
        cmd = ["pytest", str(test_file), "-v", "--tb=short"]

        if test_suite != "all":
            cmd.extend(["-k", test_suite])

        try:
            self.print_success(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )

            # Parse pytest output
            output_lines = result.stdout.split("\n")
            test_results = {}

            for line in output_lines:
                if "PASSED" in line:
                    test_name = line.split("::")[1].split()[0] if "::" in line else "unknown"
                    test_results[test_name] = "PASSED"
                    if self.verbose:
                        print(line)
                elif "FAILED" in line:
                    test_name = line.split("::")[1].split()[0] if "::" in line else "unknown"
                    test_results[test_name] = "FAILED"
                    print(line)

            # Check overall result
            if result.returncode == 0:
                self.print_success(f"All DeepEval tests passed ({len(test_results)} tests)")
                self.results["deepeval_tests"] = {
                    "status": "PASSED",
                    "test_count": len(test_results),
                    "results": test_results
                }
                return True
            else:
                failed_count = sum(1 for v in test_results.values() if v == "FAILED")
                self.print_error(f"DeepEval tests failed: {failed_count} failures")
                self.results["deepeval_tests"] = {
                    "status": "FAILED",
                    "test_count": len(test_results),
                    "failed_count": failed_count,
                    "results": test_results
                }
                return False

        except FileNotFoundError:
            self.print_error("pytest not found. Install with: pip install pytest")
            return False
        except Exception as e:
            self.print_error(f"Test execution failed: {e}")
            self.results["deepeval_tests"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def check_policy_compliance(self) -> Dict[str, Any]:
        """Step 5: Check policy compliance"""
        self.print_header("STEP 5: Policy Compliance Check")

        policy_file = PROJECT_ROOT / "policies" / "evaluation_policy.yaml"

        if not policy_file.exists():
            self.print_error("Policy file not found")
            return {"status": "ERROR", "message": "Policy file not found"}

        try:
            with open(policy_file) as f:
                policy = yaml.safe_load(f)

            self.print_success("Policy file loaded successfully")

            # Check blocking gates status
            blocking_gates = policy.get("blocking_gates", {})
            compliance_results = {}

            for gate_name, gate_config in blocking_gates.items():
                required_pass_rate = gate_config.get("min_pass_rate", 1.0)

                # Check if we have test results for this gate
                if gate_name in ["adversarial_security", "pii_detection"]:
                    # These would be in DeepEval results
                    test_results = self.results.get("deepeval_tests", {}).get("results", {})

                    # Count relevant tests
                    relevant_tests = [
                        (name, status) for name, status in test_results.items()
                        if "adversarial" in name.lower() or "pii" in name.lower()
                    ]

                    if relevant_tests:
                        passed = sum(1 for _, status in relevant_tests if status == "PASSED")
                        total = len(relevant_tests)
                        pass_rate = passed / total if total > 0 else 0

                        compliance_results[gate_name] = {
                            "required_pass_rate": required_pass_rate,
                            "actual_pass_rate": pass_rate,
                            "compliant": pass_rate >= required_pass_rate,
                            "tests": relevant_tests
                        }

                        if pass_rate >= required_pass_rate:
                            self.print_success(f"{gate_name}: {pass_rate:.1%} pass rate (required: {required_pass_rate:.1%})")
                        else:
                            self.print_error(f"{gate_name}: {pass_rate:.1%} pass rate (required: {required_pass_rate:.1%})")
                    else:
                        self.print_warning(f"{gate_name}: No test results found")
                        compliance_results[gate_name] = {
                            "required_pass_rate": required_pass_rate,
                            "actual_pass_rate": None,
                            "compliant": False,
                            "message": "No tests executed"
                        }

            # Overall compliance status
            all_compliant = all(
                result.get("compliant", False)
                for result in compliance_results.values()
            )

            self.results["policy_compliance"] = {
                "status": "COMPLIANT" if all_compliant else "NON_COMPLIANT",
                "gates": compliance_results
            }

            return self.results["policy_compliance"]

        except Exception as e:
            self.print_error(f"Policy check failed: {e}")
            return {"status": "ERROR", "error": str(e)}

    def generate_report(self, output_file: str = None):
        """Generate validation report"""
        self.print_header("VALIDATION REPORT")

        # Determine overall status
        all_passed = (
            self.results["schema_validation"] and
            self.results["guardrails_validation"].get("status") == "PASSED" and
            self.results["deepeval_tests"].get("status") == "PASSED" and
            self.results["policy_compliance"].get("status") == "COMPLIANT"
        )

        self.results["overall_status"] = "PASSED" if all_passed else "FAILED"

        # Print summary
        if all_passed:
            self.print_success("✓ ALL VALIDATION CHECKS PASSED")
            print(f"\n{Color.GREEN}{Color.BOLD}{'=' * 80}{Color.END}")
            print(f"{Color.GREEN}{Color.BOLD}{'READY FOR DEPLOYMENT':^80}{Color.END}")
            print(f"{Color.GREEN}{Color.BOLD}{'=' * 80}{Color.END}\n")
        else:
            self.print_error("✗ VALIDATION FAILED")
            print(f"\n{Color.RED}{Color.BOLD}{'=' * 80}{Color.END}")
            print(f"{Color.RED}{Color.BOLD}{'DEPLOYMENT BLOCKED':^80}{Color.END}")
            print(f"{Color.RED}{Color.BOLD}{'=' * 80}{Color.END}\n")

        # Write report to file if requested
        if output_file:
            output_path = PROJECT_ROOT / output_file
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            self.print_success(f"Report written to: {output_path}")

        return all_passed

    def run_full_validation(self, test_suite: str = "all") -> bool:
        """Run complete validation pipeline"""
        print(f"\n{Color.BOLD}Starting Prompt Validation Pipeline{Color.END}")
        print(f"Project: {PROJECT_ROOT}")
        print(f"Timestamp: {self.results['timestamp']}\n")

        # Run all validation steps
        schema_valid = self.validate_schema_files()
        prompt_valid = self.validate_prompt_specs()
        guardrails_valid = self.run_guardrails_checks()
        tests_passed = self.run_deepeval_tests(test_suite)
        policy_result = self.check_policy_compliance()

        # Generate report
        return self.generate_report(output_file="validation_report.json")


def main():
    parser = argparse.ArgumentParser(description="Validate prompts and run evaluation pipeline")
    parser.add_argument(
        "--test-suite",
        choices=["all", "golden", "edge", "adversarial"],
        default="all",
        help="Which test suite to run"
    )
    parser.add_argument(
        "--policy-check-only",
        action="store_true",
        help="Only check policy compliance"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = PromptValidator(verbose=args.verbose)

    if args.policy_check_only:
        validator.print_header("Policy Compliance Check Only")
        result = validator.check_policy_compliance()
        sys.exit(0 if result["status"] == "COMPLIANT" else 1)

    # Run full validation
    success = validator.run_full_validation(test_suite=args.test_suite)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
