"""
Guardrails AI Configuration for Fact Extraction
Demonstrates: Schema validation, PII detection, custom validators

Requirements:
    pip install guardrails-ai presidio-analyzer presidio-anonymizer

Usage:
    from guardrails.fact_extraction_guard import FactExtractionGuard

    guard = FactExtractionGuard()
    result = guard.validate(llm_output, context)
"""

from typing import Dict, Any, List
import json
from guardrails import Guard, OnFailAction
from guardrails.validators import (
    ValidRange,
    ValidChoices,
    ValidLength,
    RegexMatch
)
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class PIIValidator:
    """Custom Guardrails validator for PII detection using Presidio"""

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def validate(self, value: str, metadata: Dict) -> Dict:
        """
        Detect PII entities in the output

        Returns:
            Dict with validation results
        """
        # Analyze for PII
        results = self.analyzer.analyze(
            text=value,
            entities=["PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "US_BANK_NUMBER", "EMAIL_ADDRESS"],
            language="en"
        )

        if results:
            # PII detected - return failure
            pii_summary = [
                {"type": r.entity_type, "score": r.score, "start": r.start, "end": r.end}
                for r in results
            ]

            return {
                "outcome": "fail",
                "error_message": f"PII detected in output: {pii_summary}",
                "fix_value": self.anonymizer.anonymize(text=value, analyzer_results=results).text
            }

        return {"outcome": "pass"}


class FactExtractionGuard:
    """
    Guardrails AI Guard for Fact Extraction Output
    Enforces: Schema validation, PII safety, value ranges, compliance requirements
    """

    def __init__(self):
        self.pii_validator = PIIValidator()
        self.guard = self._build_guard()

    def _build_guard(self) -> Guard:
        """
        Build Guardrails Guard with all validators
        """

        # Define the Guardrails RAIL spec
        rail_spec = """
<rail version="0.1">

<output>
    <object name="fact_extraction_output">
        <!-- Client Demographics -->
        <object name="client_demographics">
            <integer
                name="client_age"
                validators="valid-range: min=18 max=120"
                on-fail-valid-range="reask"
                required="false"
            />
            <string
                name="employment_status"
                validators="valid-choices: choices=['employed', 'retired', 'unemployed', 'self_employed']"
                on-fail-valid-choices="reask"
                required="false"
            />
            <list name="dependents">
                <object>
                    <integer
                        name="age"
                        validators="valid-range: min=0 max=100"
                        on-fail-valid-range="fix"
                    />
                    <string
                        name="relationship"
                        validators="valid-choices: choices=['child', 'spouse', 'parent', 'other']"
                        on-fail-valid-choices="fix"
                    />
                </object>
            </list>
        </object>

        <!-- Financial Goals -->
        <object name="financial_goals">
            <integer
                name="retirement_age"
                validators="valid-range: min=40 max=90"
                on-fail-valid-range="reask"
                required="false"
            />
            <integer
                name="retirement_timeline_years"
                validators="valid-range: min=0 max=50"
                on-fail-valid-range="fix"
                required="false"
            />
            <list name="financial_goals">
                <string
                    validators="valid-length: min=5 max=500"
                    on-fail-valid-length="reask"
                />
            </list>
        </object>

        <!-- Financial Situation -->
        <object name="financial_situation">
            <float
                name="current_portfolio_value"
                validators="valid-range: min=0"
                on-fail-valid-range="exception"
                required="false"
            />
            <float
                name="annual_income"
                validators="valid-range: min=0"
                on-fail-valid-range="exception"
                required="false"
            />
        </object>

        <!-- Risk Profile -->
        <object name="risk_profile" required="true">
            <string
                name="risk_tolerance"
                validators="valid-choices: choices=['conservative', 'moderate', 'aggressive', 'conflicting']"
                on-fail-valid-choices="reask"
                required="true"
            />
            <float
                name="risk_tolerance_confidence"
                validators="valid-range: min=0 max=1"
                on-fail-valid-range="fix"
                required="false"
            />
        </object>

        <!-- Compliance Markers -->
        <object name="compliance_markers" required="true">
            <bool name="suitability_factors_discussed" required="true" />
            <bool name="investment_objectives_documented" required="true" />
            <list name="disclosures_made">
                <string validators="valid-length: max=200" />
            </list>
        </object>
    </object>
</output>

</rail>
"""

        # Create Guard from RAIL spec
        guard = Guard.from_rail_string(rail_spec)

        return guard

    def validate(self, llm_output: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate LLM output against all guardrails

        Args:
            llm_output: Raw LLM output (JSON string)
            context: Optional context (e.g., original transcript)

        Returns:
            Dict with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated_output": None,
            "pii_detected": False,
            "schema_valid": True
        }

        # Step 1: Parse JSON
        try:
            parsed_output = json.loads(llm_output)
        except json.JSONDecodeError as e:
            results["valid"] = False
            results["schema_valid"] = False
            results["errors"].append({
                "type": "json_parse_error",
                "message": str(e)
            })
            return results

        # Step 2: Check for PII leakage
        pii_check = self.pii_validator.validate(llm_output, {})
        if pii_check["outcome"] == "fail":
            results["valid"] = False
            results["pii_detected"] = True
            results["errors"].append({
                "type": "pii_leakage",
                "message": pii_check["error_message"],
                "fix": pii_check["fix_value"]
            })

        # Step 3: Schema and value validation using Guardrails
        try:
            validated = self.guard.validate(parsed_output)

            if validated.validation_passed:
                results["validated_output"] = validated.validated_output
            else:
                results["valid"] = False
                results["schema_valid"] = False
                results["errors"].append({
                    "type": "schema_validation_error",
                    "message": "Output failed schema validation",
                    "details": validated.error
                })

        except Exception as e:
            results["valid"] = False
            results["schema_valid"] = False
            results["errors"].append({
                "type": "guardrails_exception",
                "message": str(e)
            })

        # Step 4: Business logic validation
        if results["valid"]:
            business_validation = self._validate_business_logic(parsed_output, context)
            if not business_validation["valid"]:
                results["warnings"].extend(business_validation["warnings"])

        return results

    def _validate_business_logic(self, output: Dict, context: Dict = None) -> Dict:
        """
        Apply business logic validation rules

        Args:
            output: Parsed and schema-validated output
            context: Optional context for faithfulness checks

        Returns:
            Dict with business validation results
        """
        warnings = []

        # Rule 1: Retirement age should be > current age
        if output.get("client_demographics", {}).get("client_age") and \
           output.get("financial_goals", {}).get("retirement_age"):

            client_age = output["client_demographics"]["client_age"]
            retirement_age = output["financial_goals"]["retirement_age"]

            if retirement_age <= client_age:
                warnings.append({
                    "type": "business_logic_warning",
                    "message": f"Retirement age ({retirement_age}) should be greater than current age ({client_age})"
                })

        # Rule 2: Retirement timeline should match age difference
        if output.get("client_demographics", {}).get("client_age") and \
           output.get("financial_goals", {}).get("retirement_age") and \
           output.get("financial_goals", {}).get("retirement_timeline_years"):

            expected_timeline = retirement_age - client_age
            stated_timeline = output["financial_goals"]["retirement_timeline_years"]

            if abs(expected_timeline - stated_timeline) > 1:  # Allow 1 year tolerance
                warnings.append({
                    "type": "business_logic_warning",
                    "message": f"Retirement timeline ({stated_timeline} years) doesn't match age difference ({expected_timeline} years)"
                })

        # Rule 3: Conservative risk + aggressive goals = warning
        if output.get("risk_profile", {}).get("risk_tolerance") == "conservative" and \
           output.get("financial_goals", {}).get("retirement_timeline_years", 100) < 10:

            warnings.append({
                "type": "suitability_concern",
                "message": "Client has conservative risk tolerance but short timeline to retirement - may need planning discussion"
            })

        # Rule 4: High portfolio value with no emergency fund = warning
        if output.get("financial_situation", {}).get("current_portfolio_value", 0) > 1000000 and \
           output.get("financial_situation", {}).get("emergency_fund_months") is None:

            warnings.append({
                "type": "financial_planning_concern",
                "message": "High net worth client without documented emergency fund"
            })

        return {
            "valid": True,  # Warnings don't invalidate
            "warnings": warnings
        }

    def anonymize_pii(self, text: str) -> str:
        """
        Anonymize PII in text using Presidio

        Args:
            text: Input text potentially containing PII

        Returns:
            Anonymized text
        """
        results = self.pii_validator.analyzer.analyze(
            text=text,
            entities=["PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "US_BANK_NUMBER", "EMAIL_ADDRESS", "PERSON"],
            language="en"
        )

        if results:
            anonymized = self.pii_validator.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            return anonymized.text

        return text


def example_usage():
    """Example usage of the FactExtractionGuard"""

    # Example LLM output (valid)
    llm_output_valid = json.dumps({
        "conversation_id": "conv_abc123def4567890",
        "extraction_timestamp": "2025-10-14T10:35:22Z",
        "client_demographics": {
            "client_age": 52,
            "employment_status": "employed",
            "dependents": [
                {"age": 18, "relationship": "child"}
            ]
        },
        "financial_goals": {
            "retirement_age": 65,
            "retirement_timeline_years": 13,
            "financial_goals": ["Retire at 65", "Fund college for kids"]
        },
        "financial_situation": {
            "current_portfolio_value": 500000.0,
            "annual_income": 135000.0
        },
        "risk_profile": {
            "risk_tolerance": "conservative",
            "risk_tolerance_confidence": 0.85
        },
        "compliance_markers": {
            "suitability_factors_discussed": True,
            "investment_objectives_documented": True,
            "disclosures_made": ["Investment risks explained"]
        }
    })

    # Example with PII leakage (should fail)
    llm_output_with_pii = json.dumps({
        "conversation_id": "conv_abc123def4567890",
        "client_demographics": {
            "client_age": 52,
            "client_name_anonymized": "SSN: 123-45-6789"  # PII leakage!
        },
        "financial_goals": {},
        "financial_situation": {},
        "risk_profile": {
            "risk_tolerance": "conservative"
        },
        "compliance_markers": {
            "suitability_factors_discussed": True,
            "investment_objectives_documented": True,
            "disclosures_made": []
        }
    })

    # Initialize guard
    guard = FactExtractionGuard()

    # Validate valid output
    print("=== Validating VALID output ===")
    result_valid = guard.validate(llm_output_valid)
    print(f"Valid: {result_valid['valid']}")
    print(f"Errors: {result_valid['errors']}")
    print(f"Warnings: {result_valid['warnings']}")

    # Validate output with PII
    print("\n=== Validating output with PII ===")
    result_pii = guard.validate(llm_output_with_pii)
    print(f"Valid: {result_pii['valid']}")
    print(f"PII Detected: {result_pii['pii_detected']}")
    print(f"Errors: {result_pii['errors']}")

    # Test anonymization
    print("\n=== Testing PII anonymization ===")
    text_with_pii = "Client's SSN is 123-45-6789 and phone is 555-1234"
    anonymized = guard.anonymize_pii(text_with_pii)
    print(f"Original: {text_with_pii}")
    print(f"Anonymized: {anonymized}")


if __name__ == "__main__":
    example_usage()
