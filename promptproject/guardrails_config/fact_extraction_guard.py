"""
Guardrails AI Configuration for Fact Extraction
Demonstrates: Schema validation, PII detection, custom validators

Requirements:
    pip install guardrails-ai presidio-analyzer presidio-anonymizer pydantic

Usage:
    from guardrails_config.fact_extraction_guard import FactExtractionGuard

    guard = FactExtractionGuard()
    result = guard.validate(llm_output, context)
"""

from typing import Dict, Any, List, Optional
import json
from pydantic import BaseModel, Field, field_validator
from guardrails import Guard, register_validator
from guardrails.validator_base import Validator, ValidationResult, ErrorSpan
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


# Define Pydantic models for output schema
class Dependent(BaseModel):
    """Dependent information"""
    age: int = Field(ge=0, le=100, description="Dependent's age")
    relationship: str = Field(
        description="Relationship to client",
        pattern="^(child|spouse|parent|other)$"
    )


class ClientDemographics(BaseModel):
    """Client demographic information"""
    client_age: Optional[int] = Field(None, ge=18, le=120, description="Client's age")
    employment_status: Optional[str] = Field(
        None,
        description="Employment status",
        pattern="^(employed|retired|unemployed|self_employed)$"
    )
    dependents: List[Dependent] = Field(default_factory=list, description="List of dependents")


class FinancialGoals(BaseModel):
    """Financial goals and retirement planning"""
    retirement_age: Optional[int] = Field(None, ge=40, le=90, description="Target retirement age")
    retirement_timeline_years: Optional[int] = Field(None, ge=0, le=50, description="Years until retirement")
    financial_goals: List[str] = Field(default_factory=list, description="List of financial goals")


class FinancialSituation(BaseModel):
    """Current financial situation"""
    current_portfolio_value: Optional[float] = Field(None, ge=0, description="Current portfolio value")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income")
    emergency_fund_months: Optional[int] = Field(None, ge=0, le=24, description="Months of emergency fund")


class RiskProfile(BaseModel):
    """Risk tolerance profile"""
    risk_tolerance: str = Field(
        description="Risk tolerance level",
        pattern="^(conservative|moderate|aggressive|conflicting)$"
    )
    risk_tolerance_confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Confidence in risk tolerance assessment"
    )


class ComplianceMarkers(BaseModel):
    """Compliance and regulatory markers"""
    suitability_factors_discussed: bool = Field(description="Whether suitability factors were discussed")
    investment_objectives_documented: bool = Field(description="Whether investment objectives were documented")
    disclosures_made: List[str] = Field(default_factory=list, description="List of disclosures made")


class FactExtractionOutput(BaseModel):
    """Complete fact extraction output schema"""
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    extraction_timestamp: Optional[str] = Field(None, description="Timestamp of extraction")
    client_demographics: ClientDemographics = Field(default_factory=ClientDemographics)
    financial_goals: FinancialGoals = Field(default_factory=FinancialGoals)
    financial_situation: FinancialSituation = Field(default_factory=FinancialSituation)
    risk_profile: RiskProfile
    compliance_markers: ComplianceMarkers


# Custom Validator for PII Detection
@register_validator(name="pii_detection", data_type="string")
class PIIDetectionValidator(Validator):
    """Custom Guardrails validator for PII detection using Presidio"""

    def __init__(
        self,
        entities: List[str] = None,
        on_fail: str = "exception",
        **kwargs
    ):
        super().__init__(on_fail=on_fail, **kwargs)
        self.entities = entities or [
            "PHONE_NUMBER", "US_SSN", "CREDIT_CARD",
            "US_BANK_NUMBER", "EMAIL_ADDRESS"
        ]
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """
        Detect PII entities in the output

        Returns:
            ValidationResult with pass/fail status
        """
        if not isinstance(value, str):
            value = json.dumps(value)

        # Analyze for PII
        results = self.analyzer.analyze(
            text=value,
            entities=self.entities,
            language="en"
        )

        if results:
            # PII detected - return failure
            pii_summary = [
                {"type": r.entity_type, "score": r.score, "start": r.start, "end": r.end}
                for r in results
            ]

            # Create error spans for detected PII
            error_spans = [
                ErrorSpan(
                    start=r.start,
                    end=r.end,
                    reason=f"PII detected: {r.entity_type} (confidence: {r.score:.2f})"
                )
                for r in results
            ]

            return ValidationResult(
                outcome="fail",
                error_message=f"PII detected in output: {pii_summary}",
                fix_value=self.anonymizer.anonymize(text=value, analyzer_results=results).text,
                error_spans=error_spans
            )

        return ValidationResult(outcome="pass")


# Custom Validator for Business Logic
@register_validator(name="retirement_age_logic", data_type="object")
class RetirementAgeLogicValidator(Validator):
    """Validates retirement age is greater than current age"""

    def validate(self, value: Any, metadata: Dict = None) -> ValidationResult:
        """Validate business logic for retirement planning"""

        if not isinstance(value, dict):
            return ValidationResult(outcome="pass")

        client_age = value.get("client_demographics", {}).get("client_age")
        retirement_age = value.get("financial_goals", {}).get("retirement_age")

        if client_age and retirement_age:
            if retirement_age <= client_age:
                return ValidationResult(
                    outcome="fail",
                    error_message=f"Retirement age ({retirement_age}) must be greater than current age ({client_age})"
                )

        return ValidationResult(outcome="pass")


class FactExtractionGuard:
    """
    Guardrails AI Guard for Fact Extraction Output
    Enforces: Schema validation, PII safety, value ranges, compliance requirements
    """

    def __init__(self):
        self.pii_validator = PIIDetectionValidator()
        self.retirement_validator = RetirementAgeLogicValidator()
        self.guard = self._build_guard()

    def _build_guard(self) -> Guard:
        """
        Build Guardrails Guard with Pydantic model and validators
        """
        # Create Guard with Pydantic model
        guard = Guard.from_pydantic(
            output_class=FactExtractionOutput
        )

        # Add custom validators
        guard.use(self.pii_validator)
        guard.use(self.retirement_validator)

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

        # Step 2: Validate with Guardrails Guard
        try:
            # Guard.parse expects the raw LLM output string
            validated = self.guard.parse(llm_output)

            if validated.validation_passed:
                results["validated_output"] = validated.validated_output
            else:
                results["valid"] = False

                # Check for PII detection failures
                if validated.error and "PII detected" in str(validated.error):
                    results["pii_detected"] = True

                results["schema_valid"] = False
                results["errors"].append({
                    "type": "validation_error",
                    "message": "Output failed validation",
                    "details": str(validated.error) if validated.error else "Unknown error"
                })

        except Exception as e:
            results["valid"] = False
            results["schema_valid"] = False
            results["errors"].append({
                "type": "guardrails_exception",
                "message": str(e)
            })

        # Step 3: Business logic validation
        if results["valid"]:
            business_validation = self._validate_business_logic(parsed_output, context)
            if business_validation["warnings"]:
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

        # Rule 1: Retirement timeline should match age difference
        if output.get("client_demographics", {}).get("client_age") and \
           output.get("financial_goals", {}).get("retirement_age") and \
           output.get("financial_goals", {}).get("retirement_timeline_years"):

            client_age = output["client_demographics"]["client_age"]
            retirement_age = output["financial_goals"]["retirement_age"]
            expected_timeline = retirement_age - client_age
            stated_timeline = output["financial_goals"]["retirement_timeline_years"]

            if abs(expected_timeline - stated_timeline) > 1:  # Allow 1 year tolerance
                warnings.append({
                    "type": "business_logic_warning",
                    "message": f"Retirement timeline ({stated_timeline} years) doesn't match age difference ({expected_timeline} years)"
                })

        # Rule 2: Conservative risk + aggressive goals = warning
        if output.get("risk_profile", {}).get("risk_tolerance") == "conservative" and \
           output.get("financial_goals", {}).get("retirement_timeline_years", 100) < 10:

            warnings.append({
                "type": "suitability_concern",
                "message": "Client has conservative risk tolerance but short timeline to retirement - may need planning discussion"
            })

        # Rule 3: High portfolio value with no emergency fund = warning
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
            "client_name": "SSN: 123-45-6789"  # PII leakage!
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
