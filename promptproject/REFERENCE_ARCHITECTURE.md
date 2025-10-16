# Reference Architecture: OPA-Validated LLM Pipeline with Enterprise Evaluation

**Version:** 2.0
**Date:** 2025-10-16
**Purpose:** Architecture design for production-grade LLM pipeline with Open Policy Agent validation and multi-framework evaluation
**Status:** Design Specification (No Code)

---

## Executive Summary

This document defines the reference architecture for refining the **promptproject** from a test-driven prompt validation system into a production-ready LLM pipeline that prevents "confidently wrong" responses through policy-based validation.

**Key Enhancements:**
1. **OPA Integration:** Open Policy Agent validates LLM responses against business policies before returning results
2. **Multi-Framework Evaluation:** Phoenix, Ragas, and MLflow evaluations (learning from promptforge)
3. **Structured Pipeline:** 7-stage request-response flow with PII handling, schema validation, evaluation, and policy gates
4. **Fallback Mechanisms:** Graceful degradation when OPA policies fail
5. **Observable Architecture:** Comprehensive logging, metrics, and tracing

---

## Table of Contents

1. [Current Architecture Assessment](#1-current-architecture-assessment)
2. [Proposed Architecture Overview](#2-proposed-architecture-overview)
3. [Component Specifications](#3-component-specifications)
4. [Pipeline Flow Design](#4-pipeline-flow-design)
5. [OPA Policy Framework](#5-opa-policy-framework)
6. [Evaluation Integration Strategy](#6-evaluation-integration-strategy)
7. [Error Handling & Fallback Design](#7-error-handling--fallback-design)
8. [Observability & Monitoring](#8-observability--monitoring)
9. [Security & Compliance](#9-security--compliance)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Appendix: Decision Matrix](#11-appendix-decision-matrix)

---

## 1. Current Architecture Assessment

### 1.1 Existing promptproject Components

**Current Tech Stack:**
- **DeepEval:** LLM evaluation framework with pytest integration
- **Guardrails AI:** Pydantic-based runtime validation and schema enforcement
- **Presidio:** Microsoft PII detection and anonymization
- **JSON Schema:** Input/output structure validation
- **YAML:** Prompt specifications and policy definitions

**Current Flow:**
```
User Request (manual test)
  ↓
Fact Extraction Prompt (T=0.25)
  ↓
Claude API Call
  ↓
JSON Response
  ↓
Guardrails Validation (Pydantic models)
  ↓
Presidio PII Detection
  ↓
DeepEval Metrics (Faithfulness, Bias)
  ↓
Policy Compliance Check (YAML-based)
  ↓
Test Pass/Fail (pytest)
```

### 1.2 Current Strengths

1. **Comprehensive Test Coverage:**
   - Golden tests (95% accuracy target)
   - Edge case tests (85% accuracy target)
   - Adversarial tests (100% pass rate)
   - Policy compliance tests

2. **Validation Pipeline:**
   - 5-step validation orchestration (`scripts/validate_prompts.py`)
   - Schema validation for inputs and outputs
   - Guardrails integration with custom validators
   - Presidio PII detection

3. **Policy Framework:**
   - 4-tier quality gates (blocking, high-priority, standard, monitoring)
   - YAML-based policy configuration (`policies/evaluation_policy.yaml`)
   - Configurable thresholds per test category

### 1.3 Current Limitations

1. **No Runtime Request-Response Pipeline:**
   - Current system is testing-focused, not designed for production API requests
   - No user-facing API endpoint or request handler
   - No conversion from user prompt to structured input schema

2. **Limited Evaluation Frameworks:**
   - Only DeepEval is integrated
   - Missing Phoenix, Ragas, and MLflow (available in promptforge)
   - No multi-framework evaluation strategy

3. **No OPA Integration:**
   - Policy checks are Python-based, not declarative
   - No Rego policy language for business rules
   - Cannot enforce complex business logic on LLM responses

4. **Missing Confidence Scoring:**
   - No mechanism to detect "confidently wrong" responses
   - No multi-metric aggregation for confidence thresholds
   - No fallback for low-confidence responses

5. **No Observability:**
   - No distributed tracing
   - No metrics collection for production monitoring
   - No structured logging pipeline

---

## 2. Proposed Architecture Overview

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway / Load Balancer                  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      LLM Pipeline Orchestrator                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 1: PII Detection & Anonymization (Presidio)            │  │
│  │           - Detect SSN, account numbers, credit cards          │  │
│  │           - Anonymize with placeholders                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 2: Input Schema Conversion                             │  │
│  │           - Convert user prompt to JSON schema format          │  │
│  │           - Validate against conversation_input.json schema    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 3: LLM Invocation (Claude API)                         │  │
│  │           - System prompt + input schema JSON                  │  │
│  │           - Temperature: 0.25 (fact extraction)                │  │
│  │           - Output: Structured JSON response                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 4: Guardrails Validation                               │  │
│  │           - Pydantic model validation                          │  │
│  │           - Business logic checks (retirement age, etc.)       │  │
│  │           - Output PII detection                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 5: Multi-Framework Evaluation                          │  │
│  │           ┌─────────────────────────────────────────────┐    │  │
│  │           │  Phoenix:                                    │    │  │
│  │           │  - Q&A on Retrieved Data                     │    │  │
│  │           │  - Hallucination Detection                   │    │  │
│  │           │  - Code/SQL Generation Quality              │    │  │
│  │           └─────────────────────────────────────────────┘    │  │
│  │           ┌─────────────────────────────────────────────┐    │  │
│  │           │  Ragas:                                      │    │  │
│  │           │  - Faithfulness (context grounding)          │    │  │
│  │           │  - Context Precision/Recall                  │    │  │
│  │           │  - Response Relevancy                        │    │  │
│  │           └─────────────────────────────────────────────┘    │  │
│  │           ┌─────────────────────────────────────────────┐    │  │
│  │           │  MLflow:                                     │    │  │
│  │           │  - Answer Correctness                        │    │  │
│  │           │  - Token Count & Latency                     │    │  │
│  │           │  - Toxicity Score                            │    │  │
│  │           └─────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 6: OPA Policy Validation (NEW!)                       │  │
│  │           - Evaluate metrics against Rego policies            │  │
│  │           - Aggregate confidence score                        │  │
│  │           - Decision: PASS / FAIL / WARN                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Stage 7: Response Handler                                    │  │
│  │           - SUCCESS: Return validated response                │  │
│  │           - FAILURE: Return fallback message                  │  │
│  │           - WARN: Return response + warning metadata          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   Observability & Monitoring Layer                   │
│  - Distributed Tracing (OpenTelemetry)                              │
│  - Metrics Collection (Prometheus)                                  │
│  - Structured Logging (ELK/Grafana Loki)                            │
│  - Alerting (PagerDuty/Slack)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Principles

1. **Defense in Depth:** Multiple validation layers (Guardrails → Evaluation → OPA)
2. **Fail-Safe Design:** Fallback responses when policies fail
3. **Observable by Default:** Tracing, logging, and metrics at every stage
4. **Policy-Driven:** Business rules centralized in OPA Rego policies
5. **Framework Agnostic:** Pluggable evaluation adapters (Phoenix, Ragas, MLflow)
6. **Schema-First:** JSON Schema drives input/output contracts

---

## 3. Component Specifications

### 3.1 PII Detection & Anonymization Layer

**Purpose:** Prevent sensitive data from reaching LLM and leaking in responses

**Technology:** Presidio (existing) + Custom Entity Recognition

**Capabilities:**
- **Input Sanitization:**
  - Detect: SSN, credit card numbers, bank account numbers, phone numbers, email addresses
  - Anonymize: Replace with placeholders (`<SSN>`, `<ACCOUNT>`, `<PHONE>`)
  - Preserve context: Maintain semantic meaning without exposing PII

- **Output Validation:**
  - Scan LLM response for PII leakage
  - Block response if PII detected
  - Log incidents for compliance audit

**Configuration:**
```yaml
# presidio_config.yaml
entities:
  - name: US_SSN
    pattern: '\b\d{3}-\d{2}-\d{4}\b'
    confidence: 0.9
    action: ANONYMIZE

  - name: CREDIT_CARD
    pattern: '\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
    confidence: 0.85
    action: ANONYMIZE

  - name: ACCOUNT_NUMBER
    pattern: '\b\d{8,17}\b'
    confidence: 0.7
    action: ANONYMIZE

anonymization_strategy:
  type: PLACEHOLDER
  preserve_length: false
  custom_replacements:
    US_SSN: "<SSN_REDACTED>"
    CREDIT_CARD: "<CARD_REDACTED>"
    ACCOUNT_NUMBER: "<ACCOUNT_REDACTED>"
```

**Design Notes:**
- Presidio runs **before** LLM invocation (input sanitization)
- Presidio runs **after** LLM invocation (output validation)
- PII detection failures are **blocking** (100% compliance requirement)
- Anonymization is reversible via mapping table (for authorized views)

---

### 3.2 Input Schema Converter

**Purpose:** Transform unstructured user prompts into structured JSON matching conversation_input.json schema

**Approach:** LLM-based conversion with validation

**Flow:**
```
User Prompt (natural language)
  ↓
Conversion Prompt (T=0.3, strict formatting)
  ↓
LLM generates JSON matching schema
  ↓
JSON Schema validation
  ↓
Retry on validation failure (max 3 attempts)
  ↓
Validated input JSON OR fallback error
```

**Conversion Prompt Template:**
```
You are a data converter. Convert the following user prompt into a structured JSON format matching this schema:

{conversation_input_schema}

User Prompt:
{user_prompt}

Instructions:
1. Extract all relevant fields from the user prompt
2. Map to schema fields exactly
3. Use null for missing information
4. Do NOT hallucinate missing data
5. Output ONLY valid JSON, no markdown or explanations

Output JSON:
```

**Validation Logic:**
- **Schema Compliance:** Validate against `schemas/conversation_input.json`
- **Required Fields:** Ensure mandatory fields are present
- **Type Checking:** Verify data types (int, string, array, etc.)
- **Range Validation:** Check min/max constraints (e.g., age 18-120)
- **Retry Strategy:** Up to 3 attempts with error feedback to LLM

**Design Notes:**
- Conversion uses **lower temperature (0.3)** for deterministic output
- Failed conversions trigger immediate fallback response (no LLM invocation)
- Conversion step is **logged and traced** for debugging
- Input schema versioning supports backward compatibility

---

### 3.3 LLM Invocation Layer

**Purpose:** Execute fact extraction with structured input/output

**Current Implementation:** Claude Sonnet 4.5 with T=0.25

**System Prompt Structure:**
```yaml
# prompts/fact_extraction.yaml (existing)
model_config:
  provider: "anthropic"
  model: "claude-sonnet-4-5-20250929"
  temperature: 0.25  # Low for precision
  top_p: 0.95
  max_tokens: 1000

prompt_template: |
  You are a financial conversation analyst extracting factual information from advisor-client conversations.

  **CRITICAL INSTRUCTIONS:**
  1. Extract ONLY facts explicitly stated in the conversation
  2. Do NOT infer, assume, or hallucinate missing information
  3. Mark fields as null if information is not provided
  4. Flag any PII (SSN, account numbers, addresses) as <REDACTED>
  5. Ensure all numerical values (ages, amounts) are extracted accurately

  **INPUT JSON:**
  {{ input_json }}

  **OUTPUT FORMAT:**
  Respond with valid JSON matching fact_extraction_output.json schema.
```

**Request Context Injection:**
```json
{
  "request_id": "req_abc123",
  "timestamp": "2025-10-16T16:30:00Z",
  "user_id": "user_xyz789",
  "conversation": {
    "transcript": "<anonymized transcript>",
    "metadata": {
      "channel": "phone",
      "duration_seconds": 1847,
      "participants": ["advisor_id_456", "client_id_789"]
    }
  }
}
```

**Response Processing:**
- **Markdown Stripping:** Remove ```json code blocks from Claude responses
- **JSON Parsing:** Validate JSON structure
- **Schema Validation:** Check against `fact_extraction_output.json`
- **Error Handling:** Retry on malformed JSON (max 2 retries)

**Design Notes:**
- LLM layer is **stateless** - no conversation history maintained
- Each request is **independent** (no multi-turn dialogs)
- Response latency target: **P95 < 3000ms**
- Token usage logged for cost tracking

---

### 3.4 Guardrails Validation Layer

**Purpose:** Runtime validation using Pydantic models and custom business logic validators

**Existing Implementation:** `guardrails_config/fact_extraction_guard.py`

**Validation Stages:**

**Stage 1: Pydantic Model Validation**
```
FactExtractionOutput (Pydantic BaseModel)
  ├─ client_demographics: ClientDemographics
  │   ├─ client_age: int (18-120) OR null
  │   ├─ employment_status: Enum["employed", "retired", "unemployed"] OR null
  │   └─ dependents: List[Dependent]
  ├─ financial_goals: FinancialGoals
  │   ├─ retirement_age: int (40-90) OR null
  │   └─ financial_goals: List[str]
  ├─ financial_situation: FinancialSituation
  ├─ risk_profile: RiskProfile
  │   └─ risk_tolerance: Enum["conservative", "moderate", "aggressive", "conflicting"]
  └─ compliance_markers: ComplianceMarkers
      ├─ suitability_factors_discussed: bool
      └─ investment_objectives_documented: bool
```

**Stage 2: Business Logic Validators**

*Retirement Age Validator:*
```yaml
rule: retirement_age_consistency
description: "Retirement age must be greater than current age"
logic: |
  if client_age is not null AND retirement_age is not null:
    assert retirement_age > client_age
    assert (retirement_age - client_age) >= 5  # Minimum 5 years
    assert (retirement_age - client_age) <= 50  # Maximum 50 years
```

*Timeline Consistency Validator:*
```yaml
rule: timeline_consistency
description: "Retirement timeline should match age calculation"
logic: |
  if client_age AND retirement_age AND retirement_timeline_years:
    calculated_timeline = retirement_age - client_age
    tolerance = 2  # Allow ±2 years discrepancy
    assert abs(calculated_timeline - retirement_timeline_years) <= tolerance
```

*Risk Capacity Validator:*
```yaml
rule: risk_capacity_alignment
description: "Risk tolerance should align with risk capacity"
logic: |
  if risk_tolerance == "aggressive" AND risk_capacity == "low":
    warning: "Aggressive risk tolerance with low risk capacity - flag for review"
  if retirement_timeline_years < 10 AND risk_tolerance == "aggressive":
    warning: "Aggressive risk with short timeline - potential suitability issue"
```

**Stage 3: PII Output Detection**
- Scan final JSON for PII patterns (Presidio)
- Block response if PII detected (even after anonymization)
- Log PII detection events for security audit

**Design Notes:**
- Guardrails validation is **synchronous** (blocks response)
- Business logic validators are **configurable** via YAML
- Validation failures trigger **detailed error messages** for debugging
- All validations are **logged** with pass/fail status

---

### 3.5 Multi-Framework Evaluation Layer

**Purpose:** Execute evaluations from Phoenix, Ragas, and MLflow to assess response quality

**Evaluation Strategy:** Parallel execution with aggregated scoring

#### 3.5.1 Phoenix Evaluations

**Framework:** Arize Phoenix (16 evaluations available)

**Selected Evaluations for Wealth Management:**

1. **Q&A on Retrieved Data (Metric):**
   - Evaluates quality of answers based on retrieved conversation context
   - Measures: relevance, completeness, accuracy
   - Threshold: ≥ 0.85

2. **Hallucination Detection (Classifier):**
   - Detects fabricated information not grounded in transcript
   - Binary: PASS/FAIL
   - Threshold: 100% (blocking)

3. **Summarization Evaluation (Metric):**
   - Evaluates quality of compliance summaries
   - Measures: conciseness, coherence, coverage
   - Threshold: ≥ 0.80

**Execution:**
```
Phoenix Adapter
  ├─ Input: LLM response JSON + original transcript
  ├─ Execution: Parallel async calls to Phoenix API
  └─ Output:
      {
        "qa_quality": 0.89,
        "hallucination_detected": false,
        "summarization_score": 0.83
      }
```

#### 3.5.2 Ragas Evaluations

**Framework:** Ragas (23 evaluations available - most comprehensive)

**Selected Evaluations for Wealth Management:**

1. **Faithfulness (Metric):**
   - Measures factual consistency between response and source transcript
   - Critical for compliance: ensures no fabricated facts
   - Threshold: ≥ 0.95

2. **Context Precision (Metric):**
   - Measures precision of extracted facts relative to full context
   - Prevents over-extraction or hallucination
   - Threshold: ≥ 0.90

3. **Context Recall (Metric):**
   - Measures recall of important facts from transcript
   - Ensures completeness of extraction
   - Threshold: ≥ 0.85

4. **Response Relevancy (Metric):**
   - Measures relevancy of extracted facts to original request
   - Prevents tangential or off-topic extraction
   - Threshold: ≥ 0.90

**Execution:**
```
Ragas Adapter
  ├─ Input:
  │   {
  │     "question": "Extract financial facts from this conversation",
  │     "answer": "<LLM response JSON>",
  │     "contexts": ["<original transcript>"],
  │     "ground_truth": "<optional golden dataset reference>"
  │   }
  ├─ Execution: Ragas.evaluate() with selected metrics
  └─ Output:
      {
        "faithfulness": 0.96,
        "context_precision": 0.91,
        "context_recall": 0.87,
        "response_relevancy": 0.93
      }
```

#### 3.5.3 MLflow Evaluations

**Framework:** MLflow (18 evaluations available)

**Selected Evaluations for Wealth Management:**

1. **Answer Correctness (Metric):**
   - Evaluates semantic correctness against ground truth
   - Uses for regression testing with golden dataset
   - Threshold: ≥ 0.95

2. **Token Count (Performance):**
   - Counts tokens in generated response
   - Tracks cost efficiency
   - Alert threshold: > 1500 tokens

3. **Latency (Performance):**
   - Measures end-to-end response time
   - SLA monitoring
   - Alert threshold: > 5000ms

4. **Toxicity Score (Safety):**
   - Measures toxicity using Perspective API
   - Brand protection for client-facing outputs
   - Threshold: < 0.1 (low toxicity)

**Execution:**
```
MLflow Adapter
  ├─ Input: LLM response + ground truth (optional)
  ├─ Execution: mlflow.evaluate() with custom metrics
  └─ Output:
      {
        "answer_correctness": 0.94,
        "token_count": 847,
        "latency_ms": 2341,
        "toxicity_score": 0.02
      }
```

#### 3.5.4 Evaluation Orchestration

**Parallel Execution Pattern:**
```
Multi-Framework Evaluator
  ├─ Phoenix Adapter  ──┐
  ├─ Ragas Adapter    ──┼──> Async execution (parallel)
  └─ MLflow Adapter   ──┘
         ↓
    Results Aggregator
         ↓
    {
      "phoenix": {...},
      "ragas": {...},
      "mlflow": {...},
      "aggregate_confidence": 0.91,
      "execution_time_ms": 1847
    }
```

**Timeout Strategy:**
- Individual evaluation timeout: 5 seconds
- Total evaluation timeout: 15 seconds
- On timeout: Use partial results OR fallback confidence score

**Design Notes:**
- Evaluations run **asynchronously** in parallel for performance
- Missing evaluations (due to timeout/error) are **flagged** but don't block response
- Evaluation results are **cached** for identical inputs (60-second TTL)
- All metrics feed into **OPA policy validation**

---

### 3.6 OPA Policy Validation Layer (NEW!)

**Purpose:** Declarative policy engine to prevent "confidently wrong" LLM responses

**Technology:** Open Policy Agent (OPA) with Rego policy language

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│            OPA Policy Engine (Sidecar)               │
│  ┌──────────────────────────────────────────────┐  │
│  │  Policy Bundle (.rego files)                  │  │
│  │  ├─ confidence_threshold.rego                 │  │
│  │  ├─ compliance_validation.rego                │  │
│  │  ├─ business_rules.rego                       │  │
│  │  └─ hallucination_detection.rego              │  │
│  └──────────────────────────────────────────────┘  │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐  │
│  │  Policy Evaluation Engine                     │  │
│  │  - Input: Evaluation metrics JSON             │  │
│  │  - Process: Execute Rego policies             │  │
│  │  - Output: Decision (PASS/FAIL/WARN)          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 3.6.1 OPA Policy Structure

**Policy Bundle Organization:**

```
policies/opa/
├── confidence_threshold.rego      # Aggregate confidence scoring
├── compliance_validation.rego     # Regulatory compliance checks
├── business_rules.rego            # Domain-specific logic
├── hallucination_detection.rego   # Fabrication prevention
├── pii_leakage.rego              # PII exposure prevention
└── response_quality.rego         # Quality gate thresholds
```

**Example Rego Policy:** `confidence_threshold.rego`

```rego
package confidence_validation

import future.keywords.if

# Define minimum confidence threshold
min_confidence_score := 0.85

# Aggregate confidence from multiple evaluation frameworks
aggregate_confidence := score if {
    phoenix_score := input.evaluations.phoenix.qa_quality
    ragas_faithfulness := input.evaluations.ragas.faithfulness
    ragas_precision := input.evaluations.ragas.context_precision

    # Weighted average
    weights := {"phoenix": 0.3, "ragas_faithfulness": 0.4, "ragas_precision": 0.3}
    score := (phoenix_score * weights.phoenix) +
             (ragas_faithfulness * weights.ragas_faithfulness) +
             (ragas_precision * weights.ragas_precision)
}

# Decision rule: PASS if confidence >= threshold
default allow := false

allow if {
    aggregate_confidence >= min_confidence_score
    not hallucination_detected
}

# Hallucination detection from Phoenix
hallucination_detected if {
    input.evaluations.phoenix.hallucination_detected == true
}

# Provide failure reason
deny[msg] if {
    aggregate_confidence < min_confidence_score
    msg := sprintf("Confidence score %.2f below threshold %.2f",
                   [aggregate_confidence, min_confidence_score])
}

deny[msg] if {
    hallucination_detected
    msg := "Hallucination detected in response"
}
```

**Example Rego Policy:** `compliance_validation.rego`

```rego
package compliance_validation

import future.keywords.if

# Compliance markers must be present and valid
default allow := false

allow if {
    input.response.compliance_markers.suitability_factors_discussed == true
    input.response.compliance_markers.investment_objectives_documented == true
    no_pii_leakage
}

# PII leakage check
no_pii_leakage if {
    count(input.evaluations.presidio.detected_entities) == 0
}

# Risk tolerance consistency
risk_tolerance_valid if {
    risk := input.response.risk_profile.risk_tolerance
    risk in ["conservative", "moderate", "aggressive", "conflicting"]
}

# Flag warnings for review
warn[msg] if {
    input.response.risk_profile.risk_tolerance == "conflicting"
    msg := "Conflicting risk tolerance signals - requires human review"
}

# Retirement age business rule
retirement_age_valid if {
    client_age := input.response.client_demographics.client_age
    retirement_age := input.response.financial_goals.retirement_age

    retirement_age > client_age
    (retirement_age - client_age) >= 5
    (retirement_age - client_age) <= 50
}

deny[msg] if {
    not retirement_age_valid
    msg := "Retirement age inconsistent with client age"
}
```

**Example Rego Policy:** `response_quality.rego`

```rego
package response_quality

import future.keywords.if

# Quality gate thresholds (from promptforge learnings)
thresholds := {
    "ragas_faithfulness": 0.95,
    "ragas_context_precision": 0.90,
    "ragas_context_recall": 0.85,
    "mlflow_answer_correctness": 0.90,
    "mlflow_toxicity_max": 0.10
}

# Evaluate quality metrics
default quality_pass := false

quality_pass if {
    input.evaluations.ragas.faithfulness >= thresholds.ragas_faithfulness
    input.evaluations.ragas.context_precision >= thresholds.ragas_context_precision
    input.evaluations.ragas.context_recall >= thresholds.ragas_context_recall
    input.evaluations.mlflow.toxicity_score <= thresholds.mlflow_toxicity_max
}

# Token efficiency check
token_efficient if {
    input.evaluations.mlflow.token_count <= 1500
}

# Latency SLA
latency_within_sla if {
    input.evaluations.mlflow.latency_ms <= 5000
}

# Warn on performance issues
warn[msg] if {
    not token_efficient
    msg := sprintf("Token count %d exceeds efficiency target 1500",
                   [input.evaluations.mlflow.token_count])
}

warn[msg] if {
    not latency_within_sla
    msg := sprintf("Latency %dms exceeds SLA 5000ms",
                   [input.evaluations.mlflow.latency_ms])
}
```

#### 3.6.2 OPA Integration Pattern

**Request-Response Flow:**

```
Evaluation Results (JSON)
  ↓
┌──────────────────────────────────┐
│  OPA HTTP API                     │
│  POST /v1/data/policy/allow       │
│  Body: {                          │
│    "input": {                     │
│      "response": {...},           │
│      "evaluations": {...}         │
│    }                              │
│  }                                │
└──────────────────────────────────┘
  ↓
┌──────────────────────────────────┐
│  OPA Policy Engine                │
│  - Load all .rego policies        │
│  - Execute in sequence            │
│  - Aggregate decisions            │
└──────────────────────────────────┘
  ↓
┌──────────────────────────────────┐
│  OPA Response                     │
│  {                                │
│    "result": {                    │
│      "allow": true/false,         │
│      "warnings": [],              │
│      "deny_reasons": []           │
│    }                              │
│  }                                │
└──────────────────────────────────┘
```

**Deployment Model:**

**Option 1: Sidecar Container (Recommended for Kubernetes)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-pipeline
spec:
  template:
    spec:
      containers:
        - name: llm-pipeline-app
          image: llm-pipeline:latest
          ports:
            - containerPort: 8080

        - name: opa-sidecar
          image: openpolicyagent/opa:latest
          args:
            - "run"
            - "--server"
            - "--addr=localhost:8181"
            - "/policies"
          volumeMounts:
            - name: opa-policies
              mountPath: /policies

      volumes:
        - name: opa-policies
          configMap:
            name: opa-policy-bundle
```

**Option 2: Standalone Service (for non-Kubernetes)**
```
┌─────────────────┐         ┌─────────────────┐
│  LLM Pipeline   │ ──HTTP──>│  OPA Service    │
│  (Port 8080)    │<─JSON───│  (Port 8181)    │
└─────────────────┘         └─────────────────┘
        │                           │
        └───────────────────────────┘
              Shared network
```

**Policy Bundle Update Strategy:**

**GitOps Approach:**
```
GitHub Repository: policies/opa/*.rego
         ↓ (on commit)
    CI/CD Pipeline
         ↓
   Build OPA Bundle
         ↓
   ConfigMap Update (Kubernetes)
         ↓
   Rolling Restart of OPA sidecars
         ↓
   New policies active
```

#### 3.6.3 OPA Decision Handling

**Decision Types:**

1. **ALLOW (PASS):**
   - All policies passed
   - Aggregate confidence >= threshold
   - No blocking violations detected
   - **Action:** Return LLM response to user

2. **DENY (FAIL):**
   - One or more blocking policies failed
   - Confidence below threshold OR hallucination detected
   - Compliance violation OR PII leakage
   - **Action:** Return fallback response

3. **WARN (CONDITIONAL PASS):**
   - All blocking policies passed
   - Non-blocking warnings present (e.g., performance issues)
   - **Action:** Return LLM response + warning metadata

**Confidence Score Calculation:**

```rego
# Weighted multi-framework confidence
aggregate_confidence := score if {
    # Phoenix weights
    phoenix_qa := input.evaluations.phoenix.qa_quality * 0.25
    phoenix_hallucination := (1 - input.evaluations.phoenix.hallucination_detected) * 0.15

    # Ragas weights
    ragas_faithfulness := input.evaluations.ragas.faithfulness * 0.30
    ragas_precision := input.evaluations.ragas.context_precision * 0.15
    ragas_recall := input.evaluations.ragas.context_recall * 0.10

    # MLflow weights
    mlflow_correctness := input.evaluations.mlflow.answer_correctness * 0.05

    # Aggregate
    score := phoenix_qa + phoenix_hallucination + ragas_faithfulness +
             ragas_precision + ragas_recall + mlflow_correctness
}
```

**Threshold Configuration:**

```yaml
# opa_config.yaml
confidence_thresholds:
  production:
    blocking: 0.85      # Must exceed to pass
    warning: 0.75       # Warn if between 0.75-0.85

  staging:
    blocking: 0.80
    warning: 0.70

  development:
    blocking: 0.70
    warning: 0.60

policy_enforcement:
  mode: "strict"  # strict | permissive | audit_only
  allow_overrides: false
  audit_log_enabled: true
```

#### 3.6.4 Policy Testing & Validation

**OPA Policy Testing:**

```
policies/opa/tests/
├── confidence_threshold_test.rego
├── compliance_validation_test.rego
└── response_quality_test.rego
```

**Example Test:**

```rego
# confidence_threshold_test.rego
package confidence_validation

test_high_confidence_passes if {
    result := allow with input as {
        "evaluations": {
            "phoenix": {"qa_quality": 0.90},
            "ragas": {
                "faithfulness": 0.95,
                "context_precision": 0.92
            }
        }
    }

    result == true
}

test_low_confidence_fails if {
    result := allow with input as {
        "evaluations": {
            "phoenix": {"qa_quality": 0.70},
            "ragas": {
                "faithfulness": 0.75,
                "context_precision": 0.80
            }
        }
    }

    result == false
}

test_hallucination_detected_fails if {
    result := allow with input as {
        "evaluations": {
            "phoenix": {
                "qa_quality": 0.95,
                "hallucination_detected": true
            },
            "ragas": {
                "faithfulness": 0.95,
                "context_precision": 0.92
            }
        }
    }

    result == false
}
```

**Testing Commands:**

```bash
# Run all OPA policy tests
opa test policies/opa/*.rego policies/opa/tests/*.rego

# Evaluate policy with sample input
opa eval -d policies/opa/ -i sample_input.json data.confidence_validation.allow

# Validate policy bundle
opa check policies/opa/*.rego
```

---

### 3.7 Response Handler

**Purpose:** Return appropriate response based on OPA decision

**Response Types:**

#### 3.7.1 SUCCESS Response (OPA ALLOW)

```json
{
  "status": "success",
  "request_id": "req_abc123",
  "timestamp": "2025-10-16T16:30:05Z",
  "data": {
    "client_demographics": {
      "client_age": 52,
      "employment_status": "employed",
      "dependents": [...]
    },
    "financial_goals": {
      "retirement_age": 65,
      "financial_goals": [...]
    },
    "risk_profile": {
      "risk_tolerance": "conservative",
      "risk_tolerance_confidence": 0.89
    },
    "compliance_markers": {
      "suitability_factors_discussed": true,
      "investment_objectives_documented": true
    }
  },
  "metadata": {
    "model_used": "claude-sonnet-4-5-20250929",
    "temperature": 0.25,
    "tokens_used": 847,
    "latency_ms": 2341,
    "confidence_score": 0.91,
    "evaluation_results": {
      "phoenix": {"qa_quality": 0.89, "hallucination_detected": false},
      "ragas": {"faithfulness": 0.96, "context_precision": 0.91},
      "mlflow": {"answer_correctness": 0.94, "latency_ms": 2341}
    },
    "opa_decision": {
      "allowed": true,
      "warnings": []
    }
  }
}
```

#### 3.7.2 FAILURE Response (OPA DENY)

```json
{
  "status": "error",
  "request_id": "req_abc123",
  "timestamp": "2025-10-16T16:30:05Z",
  "error": {
    "code": "OPA_POLICY_VIOLATION",
    "message": "Unable to process request due to policy validation failure",
    "details": "The response did not meet quality and compliance standards"
  },
  "metadata": {
    "opa_decision": {
      "allowed": false,
      "deny_reasons": [
        "Confidence score 0.73 below threshold 0.85",
        "Hallucination detected in response"
      ]
    },
    "evaluation_results": {
      "phoenix": {"qa_quality": 0.72, "hallucination_detected": true},
      "ragas": {"faithfulness": 0.68, "context_precision": 0.81},
      "mlflow": {"answer_correctness": 0.74, "latency_ms": 2341}
    },
    "fallback_triggered": true
  },
  "suggested_actions": [
    "Please rephrase your request with more specific details",
    "Contact support if you believe this is an error (ref: req_abc123)"
  ]
}
```

#### 3.7.3 WARNING Response (OPA WARN)

```json
{
  "status": "success",
  "request_id": "req_abc123",
  "timestamp": "2025-10-16T16:30:05Z",
  "data": {
    "client_demographics": {...},
    "financial_goals": {...},
    "risk_profile": {
      "risk_tolerance": "conflicting",
      "risk_tolerance_confidence": 0.62
    },
    "compliance_markers": {...}
  },
  "warnings": [
    {
      "code": "LOW_CONFIDENCE",
      "message": "Risk tolerance classification has conflicting signals",
      "severity": "medium",
      "recommendation": "Human review recommended for risk assessment"
    },
    {
      "code": "PERFORMANCE_DEGRADATION",
      "message": "Response latency 4850ms approaching SLA limit 5000ms",
      "severity": "low"
    }
  ],
  "metadata": {
    "confidence_score": 0.82,
    "opa_decision": {
      "allowed": true,
      "warnings": [
        "Conflicting risk tolerance signals - requires human review",
        "Latency 4850ms approaching SLA threshold"
      ]
    }
  }
}
```

#### 3.7.4 Fallback Messages

**Fallback Message Templates:**

```yaml
# fallback_messages.yaml
fallback_templates:
  opa_policy_failure:
    user_message: "We're unable to process your request at this time due to quality validation. Please try again with more specific information."
    internal_reason: "OPA policy validation failed"

  low_confidence:
    user_message: "We don't have enough information to provide a confident response. Please provide additional context about the conversation."
    internal_reason: "Aggregate confidence below threshold"

  hallucination_detected:
    user_message: "We detected inconsistencies in the analysis. Please review the original conversation and try again."
    internal_reason: "Phoenix hallucination detector flagged response"

  pii_leakage:
    user_message: "For your security, we cannot process this request as it may expose sensitive information."
    internal_reason: "PII detected in output"

  timeout:
    user_message: "Request timed out. Please try again in a moment."
    internal_reason: "Evaluation timeout exceeded"

  compliance_violation:
    user_message: "This analysis does not meet regulatory compliance standards. Please contact support for assistance."
    internal_reason: "Compliance markers failed validation"
```

---

## 4. Pipeline Flow Design

### 4.1 End-to-End Request-Response Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  INCOMING REQUEST                                                    │
│  POST /api/v1/analyze-conversation                                   │
│  {                                                                    │
│    "user_prompt": "Extract facts from this advisor call...",        │
│    "transcript": "Advisor: Hi Sarah... Client: Thanks...",          │
│    "metadata": {...}                                                 │
│  }                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: PII DETECTION & ANONYMIZATION                             │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Presidio Analyzer                                             │ │
│  │  - Scan transcript for PII (SSN, account numbers, etc.)        │ │
│  │  - Replace with placeholders: <SSN_REDACTED>, <ACCOUNT>       │ │
│  │  - Preserve mapping for de-anonymization (if authorized)      │ │
│  │  - Log PII detection events for audit                          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: Anonymized transcript                                       │
│  Time: ~200ms                                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: INPUT SCHEMA CONVERSION                                   │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  LLM-Based Converter (Claude, T=0.3)                           │ │
│  │  - Convert user prompt to conversation_input.json format       │ │
│  │  - Validate against JSON Schema                                │ │
│  │  - Retry on validation failure (max 3 attempts)                │ │
│  │  - Fallback on conversion failure                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: Validated input JSON                                        │
│  Time: ~1000ms                                                       │
│  Fallback on failure: Return user-friendly error                     │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: LLM INVOCATION                                             │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Claude Sonnet 4.5 (T=0.25)                                    │ │
│  │  - System prompt + input schema JSON                           │ │
│  │  - Extract structured facts                                    │ │
│  │  - Output: fact_extraction_output.json                         │ │
│  │  - Strip markdown code blocks                                  │ │
│  │  - Parse and validate JSON structure                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: LLM response JSON                                           │
│  Time: ~2000ms (P95 < 3000ms)                                        │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: GUARDRAILS VALIDATION                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Pydantic Model Validation                                     │ │
│  │  - Type checking, range validation, enum constraints           │ │
│  │  - Business logic: retirement age consistency                  │ │
│  │  - Business logic: risk tolerance alignment                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Output PII Detection (Presidio)                               │ │
│  │  - Scan LLM response for PII leakage                           │ │
│  │  - Block response if PII detected                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: Validated response OR validation errors                     │
│  Time: ~150ms                                                        │
│  Blocking: YES (validation failure triggers fallback)                │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5: MULTI-FRAMEWORK EVALUATION (PARALLEL)                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  Phoenix Adapter (Async)                                 │ │ │
│  │  │  - Q&A Quality: 0.89                                     │ │ │
│  │  │  - Hallucination Detection: PASS                         │ │ │
│  │  │  - Summarization Score: 0.83                             │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  Ragas Adapter (Async)                                   │ │ │
│  │  │  - Faithfulness: 0.96                                    │ │ │
│  │  │  - Context Precision: 0.91                               │ │ │
│  │  │  - Context Recall: 0.87                                  │ │ │
│  │  │  - Response Relevancy: 0.93                              │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  MLflow Adapter (Async)                                  │ │ │
│  │  │  - Answer Correctness: 0.94                              │ │ │
│  │  │  - Token Count: 847                                      │ │ │
│  │  │  - Latency: 2341ms                                       │ │ │
│  │  │  - Toxicity Score: 0.02                                  │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: Aggregated evaluation metrics                               │
│  Time: ~1500ms (parallel execution with 5s timeout per adapter)      │
│  Fallback: Partial results if adapter times out                      │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 6: OPA POLICY VALIDATION                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  OPA Policy Engine                                             │ │
│  │  - Load Rego policies (.rego files)                           │ │
│  │  - Execute policies in sequence:                              │ │
│  │    1. Confidence threshold (aggregate: 0.91 >= 0.85 ✓)       │ │
│  │    2. Hallucination detection (PASS ✓)                        │ │
│  │    3. Compliance validation (markers valid ✓)                 │ │
│  │    4. Response quality (metrics >= thresholds ✓)             │ │
│  │    5. Business rules (retirement age valid ✓)                │ │
│  │  - Aggregate decision: ALLOW / DENY / WARN                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: OPA decision + reasons + warnings                           │
│  Time: ~50ms                                                         │
│  Blocking: YES (DENY triggers fallback response)                     │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 7: RESPONSE HANDLER                                           │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Decision Router                                               │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │  IF OPA ALLOW:                                         │   │ │
│  │  │    - Return validated LLM response                     │   │ │
│  │  │    - Include metadata (confidence, metrics, warnings)  │   │ │
│  │  │    - Log success event                                 │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │  IF OPA DENY:                                          │   │ │
│  │  │    - Return fallback error message                     │   │ │
│  │  │    - Include OPA deny reasons (for debugging)          │   │ │
│  │  │    - Log policy violation event                        │   │ │
│  │  │    - Alert monitoring system                           │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  │  ┌───────────────────────────────────────────────────────┐   │ │
│  │  │  IF OPA WARN:                                          │   │ │
│  │  │    - Return LLM response + warning metadata            │   │ │
│  │  │    - Include suggested actions                         │   │ │
│  │  │    - Log warning event                                 │   │ │
│  │  └───────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  Output: HTTP response to client                                     │
│  Time: ~50ms                                                         │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│  RESPONSE                                                            │
│  HTTP 200 OK (SUCCESS) or HTTP 400 (FAILURE)                        │
│  Total Time: ~5000ms (P95 target)                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  ERROR TYPES & HANDLERS                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PII Detection Failure (Stage 1)                             │   │
│  │  - Cannot anonymize PII                                      │   │
│  │  - Action: BLOCK request immediately                         │   │
│  │  - Response: "Unable to process due to sensitive data"       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Schema Conversion Failure (Stage 2)                         │   │
│  │  - Cannot convert user prompt to valid JSON                  │   │
│  │  - Action: Retry up to 3 times, then FALLBACK                │   │
│  │  - Response: "Unable to parse request. Please rephrase."     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  LLM Invocation Failure (Stage 3)                            │   │
│  │  - API error, timeout, or malformed response                 │   │
│  │  - Action: Retry once with exponential backoff, then FAIL    │   │
│  │  - Response: "Service temporarily unavailable. Try again."   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Guardrails Validation Failure (Stage 4)                     │   │
│  │  - Pydantic validation error or business logic violation     │   │
│  │  - Action: BLOCK response, log validation errors             │   │
│  │  - Response: "Analysis failed quality checks."               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Evaluation Timeout (Stage 5)                                │   │
│  │  - Adapter exceeds 5s timeout                                │   │
│  │  - Action: Use partial results, log timeout warning          │   │
│  │  - Continue to OPA with available metrics                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  OPA Policy Failure (Stage 6)                                │   │
│  │  - Confidence below threshold OR compliance violation        │   │
│  │  - Action: DENY, return fallback message                     │   │
│  │  - Response: "Unable to process - policy validation failed"  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. OPA Policy Framework

### 5.1 Policy Organization

**Policy Hierarchy:**

```
policies/opa/
├── _base/
│   ├── helpers.rego              # Utility functions
│   └── constants.rego            # Global constants
│
├── blocking/                     # Tier 1: Must pass (100%)
│   ├── confidence_threshold.rego
│   ├── hallucination_detection.rego
│   ├── pii_leakage.rego
│   └── compliance_markers.rego
│
├── high_priority/                # Tier 2: Should pass (≥95%)
│   ├── response_quality.rego
│   ├── business_rules.rego
│   └── schema_validation.rego
│
├── standard/                     # Tier 3: Expected to pass (≥85%)
│   ├── edge_case_handling.rego
│   └── ambiguity_resolution.rego
│
├── monitoring/                   # Tier 4: Track only (≥80%)
│   ├── performance_metrics.rego
│   └── cost_efficiency.rego
│
└── tests/                        # Policy unit tests
    ├── blocking_tests.rego
    ├── high_priority_tests.rego
    └── integration_tests.rego
```

### 5.2 Policy Tiers

**Tier 1: Blocking Policies (100% Pass Rate)**

These policies MUST pass. Failure blocks response immediately.

```rego
# policies/opa/blocking/confidence_threshold.rego
package blocking.confidence

import future.keywords.if

# Minimum aggregate confidence
min_confidence := 0.85

# Weighted confidence calculation
aggregate_confidence := score if {
    phoenix := input.evaluations.phoenix.qa_quality * 0.25
    ragas_faith := input.evaluations.ragas.faithfulness * 0.30
    ragas_prec := input.evaluations.ragas.context_precision * 0.15
    ragas_recall := input.evaluations.ragas.context_recall * 0.10
    phoenix_hall := (1 - input.evaluations.phoenix.hallucination_detected) * 0.15
    mlflow_correct := input.evaluations.mlflow.answer_correctness * 0.05

    score := phoenix + ragas_faith + ragas_prec + ragas_recall + phoenix_hall + mlflow_correct
}

# Decision
default allow := false

allow if {
    aggregate_confidence >= min_confidence
}

deny[msg] if {
    aggregate_confidence < min_confidence
    msg := sprintf("Aggregate confidence %.2f below threshold %.2f",
                   [aggregate_confidence, min_confidence])
}
```

```rego
# policies/opa/blocking/hallucination_detection.rego
package blocking.hallucination

import future.keywords.if

# Hallucination detected by Phoenix
hallucination_detected if {
    input.evaluations.phoenix.hallucination_detected == true
}

# Decision
default allow := true

allow if {
    not hallucination_detected
}

deny[msg] if {
    hallucination_detected
    msg := "Hallucination detected in LLM response - Phoenix flagged fabricated content"
}
```

```rego
# policies/opa/blocking/pii_leakage.rego
package blocking.pii

import future.keywords.if

# PII entities detected in output
pii_detected if {
    count(input.evaluations.presidio.output_entities) > 0
}

# Decision
default allow := true

allow if {
    not pii_detected
}

deny[msg] if {
    pii_detected
    entities := input.evaluations.presidio.output_entities
    msg := sprintf("PII leakage detected in output: %v", [entities])
}
```

```rego
# policies/opa/blocking/compliance_markers.rego
package blocking.compliance

import future.keywords.if

# Required compliance markers
required_markers_present if {
    input.response.compliance_markers.suitability_factors_discussed == true
    input.response.compliance_markers.investment_objectives_documented == true
}

# Decision
default allow := false

allow if {
    required_markers_present
}

deny[msg] if {
    not input.response.compliance_markers.suitability_factors_discussed
    msg := "Compliance violation: Suitability factors not documented"
}

deny[msg] if {
    not input.response.compliance_markers.investment_objectives_documented
    msg := "Compliance violation: Investment objectives not documented"
}
```

**Tier 2: High Priority Policies (≥95% Pass Rate)**

These policies should pass. Failure triggers warning + human review.

```rego
# policies/opa/high_priority/response_quality.rego
package high_priority.quality

import future.keywords.if

# Quality thresholds from promptforge learnings
thresholds := {
    "ragas_faithfulness": 0.95,
    "ragas_context_precision": 0.90,
    "ragas_context_recall": 0.85,
    "mlflow_toxicity_max": 0.10
}

# Quality checks
quality_pass if {
    input.evaluations.ragas.faithfulness >= thresholds.ragas_faithfulness
    input.evaluations.ragas.context_precision >= thresholds.ragas_context_precision
    input.evaluations.ragas.context_recall >= thresholds.ragas_context_recall
    input.evaluations.mlflow.toxicity_score <= thresholds.mlflow_toxicity_max
}

# Warning for quality issues
warn[msg] if {
    input.evaluations.ragas.faithfulness < thresholds.ragas_faithfulness
    msg := sprintf("Low faithfulness score: %.2f (threshold: %.2f)",
                   [input.evaluations.ragas.faithfulness, thresholds.ragas_faithfulness])
}

warn[msg] if {
    input.evaluations.mlflow.toxicity_score > thresholds.mlflow_toxicity_max
    msg := sprintf("Elevated toxicity score: %.2f (threshold: %.2f)",
                   [input.evaluations.mlflow.toxicity_score, thresholds.mlflow_toxicity_max])
}
```

```rego
# policies/opa/high_priority/business_rules.rego
package high_priority.business_rules

import future.keywords.if

# Retirement age business rule
retirement_age_valid if {
    client_age := input.response.client_demographics.client_age
    retirement_age := input.response.financial_goals.retirement_age

    # Both must be present
    client_age != null
    retirement_age != null

    # Retirement age must be > client age
    retirement_age > client_age

    # Minimum 5 years until retirement
    (retirement_age - client_age) >= 5

    # Maximum 50 years until retirement
    (retirement_age - client_age) <= 50
}

# Risk tolerance consistency
risk_tolerance_consistent if {
    risk_tolerance := input.response.risk_profile.risk_tolerance
    risk_capacity := input.response.risk_profile.risk_capacity
    timeline := input.response.financial_goals.retirement_timeline_years

    # Aggressive risk with low capacity is inconsistent
    not (risk_tolerance == "aggressive" and risk_capacity == "low")

    # Aggressive risk with short timeline is risky
    not (risk_tolerance == "aggressive" and timeline < 10)
}

# Warnings
warn[msg] if {
    not retirement_age_valid
    msg := "Retirement age inconsistent with client age"
}

warn[msg] if {
    not risk_tolerance_consistent
    msg := "Risk tolerance inconsistent with risk capacity or timeline"
}
```

**Tier 3: Standard Policies (≥85% Pass Rate)**

These policies track expected behavior. Failure is logged but doesn't block.

```rego
# policies/opa/standard/edge_case_handling.rego
package standard.edge_cases

import future.keywords.if

# Check for incomplete data handling
incomplete_data_handled if {
    # If transcript is very short (< 100 chars), expect limited extraction
    count(input.request.transcript) < 100

    # Most demographic fields should be null
    input.response.client_demographics.client_age == null
    input.response.financial_goals.retirement_age == null
}

# Check for ambiguity flagging
ambiguity_flagged if {
    # If risk tolerance is conflicting
    input.response.risk_profile.risk_tolerance == "conflicting"

    # Confidence should be low
    input.response.risk_profile.risk_tolerance_confidence < 0.75
}

# Log observations
info[msg] if {
    incomplete_data_handled
    msg := "Edge case: Incomplete conversation detected and handled appropriately"
}

info[msg] if {
    ambiguity_flagged
    msg := "Edge case: Ambiguous risk tolerance flagged with low confidence"
}
```

**Tier 4: Monitoring Policies (≥80% Pass Rate)**

These policies track performance and cost. Used for alerting and optimization.

```rego
# policies/opa/monitoring/performance_metrics.rego
package monitoring.performance

import future.keywords.if

# Performance SLAs
sla := {
    "latency_p95_ms": 5000,
    "token_count_max": 1500,
    "cost_per_request_max": 0.10
}

# Check latency
latency_within_sla if {
    input.evaluations.mlflow.latency_ms <= sla.latency_p95_ms
}

# Check token efficiency
token_efficient if {
    input.evaluations.mlflow.token_count <= sla.token_count_max
}

# Warnings for performance issues
warn[msg] if {
    not latency_within_sla
    msg := sprintf("Latency %dms exceeds SLA %dms",
                   [input.evaluations.mlflow.latency_ms, sla.latency_p95_ms])
}

warn[msg] if {
    not token_efficient
    msg := sprintf("Token count %d exceeds efficiency target %d",
                   [input.evaluations.mlflow.token_count, sla.token_count_max])
}

# Metrics for dashboards
metrics := {
    "latency_ms": input.evaluations.mlflow.latency_ms,
    "token_count": input.evaluations.mlflow.token_count,
    "latency_within_sla": latency_within_sla,
    "token_efficient": token_efficient
}
```

### 5.3 Policy Aggregation

**Master Policy:**

```rego
# policies/opa/master.rego
package master

import data.blocking.confidence
import data.blocking.hallucination
import data.blocking.pii
import data.blocking.compliance
import data.high_priority.quality
import data.high_priority.business_rules
import data.standard.edge_cases
import data.monitoring.performance

# Aggregate all blocking policies
default allow := false

allow if {
    confidence.allow
    hallucination.allow
    pii.allow
    compliance.allow
}

# Collect all deny reasons
deny_reasons := reasons if {
    reasons := array.concat(
        confidence.deny,
        array.concat(
            hallucination.deny,
            array.concat(
                pii.deny,
                compliance.deny
            )
        )
    )
}

# Collect all warnings
warnings := warns if {
    warns := array.concat(
        quality.warn,
        array.concat(
            business_rules.warn,
            array.concat(
                edge_cases.info,
                performance.warn
            )
        )
    )
}

# Final decision
decision := {
    "allow": allow,
    "deny_reasons": deny_reasons,
    "warnings": warnings,
    "confidence_score": confidence.aggregate_confidence,
    "metrics": performance.metrics
}
```

**OPA Query Endpoint:**

```bash
# Query master policy
curl -X POST http://localhost:8181/v1/data/master/decision \
  -H 'Content-Type: application/json' \
  -d @- <<EOF
{
  "input": {
    "request": {...},
    "response": {...},
    "evaluations": {...}
  }
}
EOF

# Response
{
  "result": {
    "allow": true,
    "deny_reasons": [],
    "warnings": [
      "Latency 4850ms approaching SLA threshold"
    ],
    "confidence_score": 0.91,
    "metrics": {
      "latency_ms": 4850,
      "token_count": 847,
      "latency_within_sla": true,
      "token_efficient": true
    }
  }
}
```

---

## 6. Evaluation Integration Strategy

### 6.1 Adapter Pattern

**Evaluation Adapter Interface:**

```
EvaluationAdapter (Abstract Base Class)
├── evaluate(response, context) -> EvaluationResult
├── get_metrics() -> List[MetricDefinition]
├── configure(config) -> None
└── health_check() -> bool
```

**Concrete Adapters:**

```
adapters/
├── phoenix_adapter.py
├── ragas_adapter.py
├── mlflow_adapter.py
└── deepeval_adapter.py (existing)
```

**Adapter Responsibilities:**

1. **Input Transformation:**
   - Convert LLM response to adapter-specific format
   - Prepare context (transcript, ground truth, etc.)
   - Handle adapter-specific configuration

2. **Metric Execution:**
   - Call adapter's evaluation API
   - Handle timeouts and retries
   - Parse results into standard format

3. **Result Normalization:**
   - Convert scores to 0-1 range
   - Map binary classifiers to pass/fail
   - Extract metadata (latency, errors, etc.)

4. **Error Handling:**
   - Timeout gracefully after 5 seconds
   - Return partial results on failure
   - Log errors for debugging

### 6.2 Phoenix Adapter Design

**Evaluation Selection:**
- Q&A on Retrieved Data (Metric)
- Hallucination Detection (Classifier)
- Summarization Evaluation (Metric)

**Configuration:**

```yaml
# config/phoenix_adapter.yaml
phoenix:
  api_endpoint: "https://phoenix.arize.com/api/v1"
  api_key: "${PHOENIX_API_KEY}"
  timeout_seconds: 5
  retry_attempts: 1

  evaluations:
    qa_quality:
      enabled: true
      model: "gpt-4"
      temperature: 0.3

    hallucination_detection:
      enabled: true
      model: "gpt-4"
      threshold: 0.5  # Confidence threshold

    summarization:
      enabled: true
      model: "gpt-4"
```

**Input Format:**

```json
{
  "task_type": "qa",
  "context": "<original transcript>",
  "question": "Extract financial facts from this advisor-client conversation",
  "answer": "<LLM response JSON as string>",
  "reference": "<ground truth JSON (optional for golden tests)>"
}
```

**Output Format:**

```json
{
  "adapter": "phoenix",
  "execution_time_ms": 1234,
  "status": "success",
  "metrics": {
    "qa_quality": 0.89,
    "hallucination_detected": false,
    "summarization_score": 0.83
  },
  "metadata": {
    "model_used": "gpt-4",
    "tokens_used": 450,
    "confidence": 0.92
  }
}
```

### 6.3 Ragas Adapter Design

**Evaluation Selection:**
- Faithfulness (Metric)
- Context Precision (Metric)
- Context Recall (Metric)
- Response Relevancy (Metric)

**Configuration:**

```yaml
# config/ragas_adapter.yaml
ragas:
  model: "gpt-4"
  embeddings: "text-embedding-ada-002"
  timeout_seconds: 5
  retry_attempts: 1

  evaluations:
    faithfulness:
      enabled: true
      threshold: 0.95

    context_precision:
      enabled: true
      threshold: 0.90

    context_recall:
      enabled: true
      threshold: 0.85

    response_relevancy:
      enabled: true
      threshold: 0.90
```

**Input Format:**

```json
{
  "question": "Extract structured facts from this financial planning conversation",
  "answer": "<LLM response JSON as string>",
  "contexts": ["<original transcript>"],
  "ground_truth": "<expected output JSON (optional)>"
}
```

**Output Format:**

```json
{
  "adapter": "ragas",
  "execution_time_ms": 1567,
  "status": "success",
  "metrics": {
    "faithfulness": 0.96,
    "context_precision": 0.91,
    "context_recall": 0.87,
    "response_relevancy": 0.93
  },
  "metadata": {
    "model_used": "gpt-4",
    "embeddings_used": "text-embedding-ada-002"
  }
}
```

### 6.4 MLflow Adapter Design

**Evaluation Selection:**
- Answer Correctness (Metric)
- Token Count (Performance)
- Latency (Performance)
- Toxicity Score (Safety)

**Configuration:**

```yaml
# config/mlflow_adapter.yaml
mlflow:
  tracking_uri: "http://mlflow-server:5000"
  experiment_name: "llm-pipeline-evaluations"
  timeout_seconds: 5

  evaluations:
    answer_correctness:
      enabled: true
      model: "gpt-4"
      threshold: 0.90

    token_count:
      enabled: true
      alert_threshold: 1500

    latency:
      enabled: true
      alert_threshold_ms: 5000

    toxicity:
      enabled: true
      api_key: "${PERSPECTIVE_API_KEY}"
      threshold: 0.10
```

**Input Format:**

```json
{
  "predictions": ["<LLM response JSON as string>"],
  "targets": ["<ground truth JSON (optional)>"],
  "metadata": {
    "model": "claude-sonnet-4-5-20250929",
    "temperature": 0.25,
    "tokens_used": 847,
    "latency_ms": 2341
  }
}
```

**Output Format:**

```json
{
  "adapter": "mlflow",
  "execution_time_ms": 892,
  "status": "success",
  "metrics": {
    "answer_correctness": 0.94,
    "token_count": 847,
    "latency_ms": 2341,
    "toxicity_score": 0.02
  },
  "metadata": {
    "experiment_id": "123",
    "run_id": "abc456"
  }
}
```

### 6.5 Evaluation Orchestrator

**Orchestration Strategy:**

```
Evaluation Orchestrator
  ├─ Initialize adapters (Phoenix, Ragas, MLflow)
  ├─ Prepare common context (transcript, response)
  ├─ Execute adapters in parallel (asyncio)
  ├─ Collect results with timeout handling
  ├─ Aggregate metrics
  └─ Return normalized results
```

**Timeout & Retry Logic:**

```yaml
# config/evaluation_orchestrator.yaml
orchestrator:
  execution_mode: "parallel"  # parallel | sequential
  timeout_per_adapter_seconds: 5
  total_timeout_seconds: 15
  retry_on_failure: true
  retry_attempts: 1
  retry_backoff_seconds: 2

  failure_strategy: "partial_results"  # partial_results | fail_fast | use_fallback

  fallback_confidence_score: 0.70  # If all adapters fail
  min_adapters_required: 2         # At least 2 must succeed
```

**Result Aggregation:**

```json
{
  "orchestrator_status": "success",
  "adapters_executed": ["phoenix", "ragas", "mlflow"],
  "adapters_succeeded": ["phoenix", "ragas", "mlflow"],
  "adapters_failed": [],
  "execution_time_ms": 1847,

  "evaluations": {
    "phoenix": {
      "qa_quality": 0.89,
      "hallucination_detected": false,
      "summarization_score": 0.83
    },
    "ragas": {
      "faithfulness": 0.96,
      "context_precision": 0.91,
      "context_recall": 0.87,
      "response_relevancy": 0.93
    },
    "mlflow": {
      "answer_correctness": 0.94,
      "token_count": 847,
      "latency_ms": 2341,
      "toxicity_score": 0.02
    }
  },

  "aggregate_confidence": 0.91,
  "aggregate_method": "weighted_average"
}
```

---

## 7. Error Handling & Fallback Design

### 7.1 Fallback Strategy Hierarchy

```
Error Detection
       ↓
┌──────────────────────────────────────────────┐
│  Tier 1: Immediate Fallback (Blocking)       │
│  - PII detection failure (input)             │
│  - Schema conversion failure (3 retries)     │
│  - PII leakage detected (output)             │
│  Action: Return generic error, log incident  │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  Tier 2: Retry + Fallback                   │
│  - LLM API error (timeout, 500 error)        │
│  - Guardrails validation failure             │
│  Action: Retry once, then fallback           │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  Tier 3: Partial Results + Fallback         │
│  - Evaluation adapter timeout                │
│  - OPA policy evaluation error               │
│  Action: Use partial data, adjust confidence │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  Tier 4: Warning + Proceed                  │
│  - Non-blocking policy warnings              │
│  - Performance degradation                   │
│  Action: Return response + metadata warnings │
└──────────────────────────────────────────────┘
```

### 7.2 Fallback Response Templates

**PII Detection Failure:**

```json
{
  "status": "error",
  "error": {
    "code": "PII_DETECTION_FAILURE",
    "message": "For your security, we cannot process this request as it contains sensitive information that we cannot safely handle.",
    "user_message": "Please remove any Social Security numbers, account numbers, or credit card information from your request and try again."
  },
  "request_id": "req_abc123",
  "support_contact": "support@example.com"
}
```

**Schema Conversion Failure:**

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST_FORMAT",
    "message": "We were unable to understand your request format.",
    "user_message": "Please rephrase your request with clear details about the conversation you want analyzed.",
    "suggestions": [
      "Ensure the transcript is properly formatted",
      "Include speaker labels (Advisor: / Client:)",
      "Provide sufficient conversation context"
    ]
  },
  "request_id": "req_abc123"
}
```

**OPA Policy Failure (Low Confidence):**

```json
{
  "status": "error",
  "error": {
    "code": "POLICY_VALIDATION_FAILED",
    "message": "Unable to process request due to quality validation failure",
    "user_message": "We don't have enough confidence in the analysis results. Please provide a longer or more detailed conversation transcript.",
    "details": {
      "confidence_score": 0.73,
      "required_confidence": 0.85,
      "issues": [
        "Low faithfulness score indicates potential hallucination",
        "Incomplete conversation data"
      ]
    }
  },
  "request_id": "req_abc123"
}
```

**OPA Policy Failure (Hallucination Detected):**

```json
{
  "status": "error",
  "error": {
    "code": "HALLUCINATION_DETECTED",
    "message": "Unable to process request due to detected inconsistencies",
    "user_message": "We detected that the analysis may contain fabricated information. Please review the original conversation and try again.",
    "details": {
      "detection_source": "Phoenix hallucination detector",
      "confidence_threshold_violated": true
    }
  },
  "request_id": "req_abc123"
}
```

**OPA Policy Failure (Compliance Violation):**

```json
{
  "status": "error",
  "error": {
    "code": "COMPLIANCE_VALIDATION_FAILED",
    "message": "The analysis does not meet regulatory compliance standards",
    "user_message": "This conversation analysis cannot be completed as it does not meet compliance requirements. Please contact support for assistance.",
    "details": {
      "compliance_issues": [
        "Suitability factors not documented",
        "Investment objectives missing"
      ]
    }
  },
  "request_id": "req_abc123",
  "support_escalation": true
}
```

### 7.3 Graceful Degradation

**Partial Evaluation Results:**

```yaml
# Scenario: Ragas adapter times out
evaluation_results:
  phoenix:
    status: "success"
    qa_quality: 0.89
    hallucination_detected: false

  ragas:
    status: "timeout"
    error: "Evaluation exceeded 5s timeout"
    metrics_available: {}

  mlflow:
    status: "success"
    answer_correctness: 0.94
    latency_ms: 2341

# OPA Policy Adjustment:
# - Use Phoenix + MLflow metrics only
# - Reduce confidence threshold to account for missing Ragas metrics
# - Add warning: "Partial evaluation results - Ragas metrics unavailable"
# - Decision: WARN (proceed with lower confidence)
```

**Confidence Adjustment Formula:**

```
Standard Confidence (all adapters):
  = (Phoenix * 0.40) + (Ragas * 0.40) + (MLflow * 0.20)

Adjusted Confidence (Ragas timeout):
  = (Phoenix * 0.60) + (MLflow * 0.30) + (fallback_adjustment: -0.10)

Threshold Adjustment:
  Standard threshold: 0.85
  Adjusted threshold: 0.75 (with warning to user)
```

### 7.4 Circuit Breaker Pattern

**Purpose:** Prevent cascading failures when evaluation services are down

**Configuration:**

```yaml
# config/circuit_breaker.yaml
circuit_breaker:
  enabled: true

  # Per-adapter circuit breaker
  per_adapter:
    failure_threshold: 5          # Open circuit after 5 consecutive failures
    success_threshold: 2          # Close circuit after 2 consecutive successes
    timeout_seconds: 60           # Try again after 60 seconds in open state
    half_open_timeout_seconds: 10 # Test with 1 request in half-open state

  # Global circuit breaker
  global:
    failure_rate_threshold: 0.50  # Open if 50% of requests fail
    window_seconds: 300           # Evaluate over 5-minute window
    min_requests_threshold: 20    # Need at least 20 requests to evaluate
```

**States:**

1. **CLOSED (Normal Operation):**
   - All adapters functioning normally
   - Requests pass through to adapters
   - Track failure rate

2. **OPEN (Failure Detected):**
   - Adapter or global circuit breaker trips
   - Requests immediately return fallback (skip adapter)
   - Wait for timeout period

3. **HALF-OPEN (Testing Recovery):**
   - After timeout, allow limited requests through
   - If successful: transition to CLOSED
   - If failure: transition back to OPEN

**Fallback Behavior:**

```
If Circuit OPEN for adapter:
  ├─ Skip adapter execution
  ├─ Use partial results from other adapters
  ├─ Reduce confidence threshold
  ├─ Add warning: "Service temporarily degraded"
  └─ Continue processing with degraded confidence
```

---

## 8. Observability & Monitoring

### 8.1 Distributed Tracing

**Technology:** OpenTelemetry

**Span Hierarchy:**

```
request.llm_pipeline (Parent Span)
├── presidio.input_pii_detection
├── schema.convert_user_prompt
│   ├── llm.convert_to_schema (3 retries)
│   └── schema.validate_input
├── llm.invoke_claude
│   └── anthropic.api_call
├── guardrails.validate
│   ├── pydantic.model_validation
│   ├── business_logic.retirement_age
│   ├── business_logic.risk_tolerance
│   └── presidio.output_pii_detection
├── evaluation.orchestrate (Parent of evaluations)
│   ├── evaluation.phoenix
│   ├── evaluation.ragas
│   └── evaluation.mlflow
├── opa.policy_validation
│   ├── opa.load_policies
│   ├── opa.execute_confidence_threshold
│   ├── opa.execute_hallucination_detection
│   ├── opa.execute_compliance
│   └── opa.aggregate_decision
└── response.handler
```

**Trace Attributes:**

```yaml
# Span attributes for request.llm_pipeline
attributes:
  request.id: "req_abc123"
  request.user_id: "user_xyz789"
  request.timestamp: "2025-10-16T16:30:00Z"
  request.transcript_length: 2847

  llm.model: "claude-sonnet-4-5-20250929"
  llm.temperature: 0.25
  llm.tokens_input: 1234
  llm.tokens_output: 847
  llm.latency_ms: 2341

  evaluation.phoenix.status: "success"
  evaluation.phoenix.latency_ms: 1234
  evaluation.ragas.status: "success"
  evaluation.ragas.latency_ms: 1567
  evaluation.mlflow.status: "success"
  evaluation.mlflow.latency_ms: 892

  opa.decision: "allow"
  opa.confidence_score: 0.91
  opa.warnings_count: 1

  response.status: "success"
  response.total_latency_ms: 4985
```

**Trace Propagation:**

```
HTTP Headers:
  traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
  tracestate: vendor=otel

OpenTelemetry Context:
  trace_id: 4bf92f3577b34da6a3ce929d0e0e4736
  span_id: 00f067aa0ba902b7
  trace_flags: 01 (sampled)
```

### 8.2 Metrics Collection

**Technology:** Prometheus

**Metric Categories:**

**Request Metrics:**
```
# Counter: Total requests
llm_pipeline_requests_total{status="success|failure"}

# Histogram: Request duration
llm_pipeline_request_duration_seconds{stage="<stage_name>"}

# Gauge: In-flight requests
llm_pipeline_requests_in_flight
```

**LLM Metrics:**
```
# Counter: LLM API calls
llm_api_calls_total{provider="anthropic", model="claude-sonnet-4-5"}

# Counter: Tokens used
llm_tokens_used_total{type="input|output"}

# Histogram: LLM latency
llm_latency_seconds{model="claude-sonnet-4-5"}
```

**Evaluation Metrics:**
```
# Histogram: Evaluation scores
evaluation_score{framework="phoenix|ragas|mlflow", metric="<metric_name>"}

# Counter: Evaluation failures
evaluation_failures_total{framework="<framework>", reason="timeout|error"}

# Histogram: Evaluation duration
evaluation_duration_seconds{framework="<framework>"}
```

**OPA Metrics:**
```
# Counter: OPA decisions
opa_decisions_total{decision="allow|deny|warn"}

# Histogram: Confidence scores
opa_confidence_score{decision="allow|deny"}

# Counter: Policy violations
opa_policy_violations_total{policy="<policy_name>"}

# Histogram: OPA evaluation duration
opa_evaluation_duration_seconds
```

**Error Metrics:**
```
# Counter: Errors by stage
llm_pipeline_errors_total{stage="<stage>", error_type="<type>"}

# Counter: Fallback responses
llm_pipeline_fallbacks_total{reason="<reason>"}

# Counter: Circuit breaker trips
circuit_breaker_trips_total{adapter="<adapter>"}
```

**Cost Metrics:**
```
# Counter: API costs
llm_api_cost_usd_total{provider="anthropic|openai"}

# Gauge: Cost per request
llm_cost_per_request_usd{model="<model>"}
```

### 8.3 Structured Logging

**Log Format:** JSON (ELK Stack / Grafana Loki)

**Log Levels:**
- **DEBUG:** Detailed tracing for development
- **INFO:** Request start/end, stage transitions
- **WARN:** Non-blocking issues, degraded performance
- **ERROR:** Failures, exceptions, policy violations
- **FATAL:** Critical system failures

**Log Schema:**

```json
{
  "timestamp": "2025-10-16T16:30:00.123Z",
  "level": "INFO",
  "logger": "llm_pipeline.orchestrator",
  "message": "Request processed successfully",

  "request_id": "req_abc123",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",

  "context": {
    "user_id": "user_xyz789",
    "stage": "response_handler",
    "decision": "allow"
  },

  "metrics": {
    "total_latency_ms": 4985,
    "llm_latency_ms": 2341,
    "evaluation_latency_ms": 1847,
    "opa_latency_ms": 47,
    "tokens_used": 2081,
    "confidence_score": 0.91
  },

  "metadata": {
    "environment": "production",
    "version": "2.0.0",
    "host": "llm-pipeline-pod-123"
  }
}
```

**Key Log Events:**

```
REQUEST_RECEIVED
  ↓
PII_DETECTION_STARTED → PII_DETECTED / PII_CLEAN
  ↓
SCHEMA_CONVERSION_STARTED → CONVERSION_SUCCESS / CONVERSION_FAILED
  ↓
LLM_INVOCATION_STARTED → LLM_RESPONSE_RECEIVED / LLM_ERROR
  ↓
GUARDRAILS_VALIDATION_STARTED → VALIDATION_PASSED / VALIDATION_FAILED
  ↓
EVALUATION_STARTED → EVALUATION_COMPLETED / EVALUATION_TIMEOUT
  ↓
OPA_POLICY_STARTED → OPA_ALLOW / OPA_DENY / OPA_WARN
  ↓
RESPONSE_RETURNED
```

### 8.4 Alerting Rules

**Critical Alerts (PagerDuty):**

```yaml
alerts:
  - name: HighErrorRate
    condition: sum(rate(llm_pipeline_errors_total[5m])) > 0.10
    severity: critical
    message: "Error rate > 10% in last 5 minutes"

  - name: OPAPolicyViolationSpike
    condition: sum(rate(opa_policy_violations_total[5m])) > 5
    severity: critical
    message: "OPA policy violations spiking"

  - name: PIILeakageDetected
    condition: sum(increase(opa_policy_violations_total{policy="pii_leakage"}[5m])) > 0
    severity: critical
    message: "PII leakage detected in responses"

  - name: ServiceDown
    condition: up{job="llm-pipeline"} == 0
    severity: critical
    message: "LLM pipeline service is down"
```

**Warning Alerts (Slack):**

```yaml
alerts:
  - name: HighLatency
    condition: histogram_quantile(0.95, llm_pipeline_request_duration_seconds) > 7.0
    severity: warning
    message: "P95 latency > 7s (SLA: 5s)"

  - name: LowConfidenceRate
    condition: sum(rate(opa_decisions_total{decision="deny"}[10m])) / sum(rate(opa_decisions_total[10m])) > 0.20
    severity: warning
    message: "20% of requests failing OPA validation"

  - name: EvaluationTimeouts
    condition: sum(rate(evaluation_failures_total{reason="timeout"}[5m])) > 0.10
    severity: warning
    message: "Evaluation timeouts > 10%"

  - name: CircuitBreakerOpen
    condition: circuit_breaker_state{state="open"} == 1
    severity: warning
    message: "Circuit breaker open for adapter"
```

### 8.5 Dashboards

**Executive Dashboard (Grafana):**

```
┌─────────────────────────────────────────────────────────────┐
│  LLM Pipeline - Production Overview                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request Volume (5m rate)                                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │  150 req/min    ▲ 5% from last hour                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Success Rate                     P95 Latency               │
│  ┌────────────────────┐          ┌────────────────────┐   │
│  │  98.5%     ✓       │          │  4.2s      ✓       │   │
│  │  (target: ≥95%)    │          │  (target: <5s)     │   │
│  └────────────────────┘          └────────────────────┘   │
│                                                              │
│  OPA Decision Distribution (Last Hour)                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │  ████████████ ALLOW (92%)                          │   │
│  │  ██ DENY (5%)                                      │   │
│  │  █ WARN (3%)                                       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Aggregate Confidence Score (Avg)                          │
│  ┌────────────────────────────────────────────────────┐   │
│  │  0.89       ✓                                      │   │
│  │  (target: ≥0.85)                                   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Top Policy Violations (Last 24h)                          │
│  1. Low confidence threshold (73 violations)                │
│  2. Hallucination detected (12 violations)                  │
│  3. Compliance markers missing (5 violations)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Technical Dashboard (Grafana):**

```
┌─────────────────────────────────────────────────────────────┐
│  LLM Pipeline - Technical Metrics                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stage Latencies (P50/P95/P99)                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  PII Detection:      0.15s / 0.22s / 0.35s         │   │
│  │  Schema Conversion:  0.85s / 1.20s / 1.85s         │   │
│  │  LLM Invocation:     1.80s / 2.50s / 3.80s         │   │
│  │  Guardrails:         0.12s / 0.18s / 0.28s         │   │
│  │  Evaluation:         1.20s / 1.85s / 2.50s         │   │
│  │  OPA Validation:     0.03s / 0.05s / 0.08s         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Evaluation Adapter Health                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Phoenix:  ✓ 99.2% success   Avg: 1.2s             │   │
│  │  Ragas:    ✓ 98.5% success   Avg: 1.6s             │   │
│  │  MLflow:   ✓ 99.8% success   Avg: 0.9s             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Token Usage & Cost                                         │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Avg tokens/request:  2081 (input: 1234, output: 847)  │   │
│  │  Cost/request:        $0.08                         │   │
│  │  Daily cost:          $1,152 (14,400 requests)     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
│  Error Breakdown (Last Hour)                                │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Schema conversion failure:  8 (0.5%)               │   │
│  │  LLM timeout:                3 (0.2%)               │   │
│  │  Guardrails validation:      5 (0.3%)               │   │
│  │  Evaluation timeout:         12 (0.8%)              │   │
│  │  OPA policy violation:       72 (4.8%)              │   │
│  └────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Security & Compliance

### 9.1 PII Protection Strategy

**Multi-Layer PII Defense:**

```
Layer 1: Input Sanitization (Presidio)
  ├─ Detect PII in user prompt
  ├─ Detect PII in conversation transcript
  ├─ Anonymize with reversible placeholders
  └─ Store anonymization mapping (encrypted)

Layer 2: LLM Prompt Engineering
  ├─ System prompt: "Do NOT echo PII"
  ├─ System prompt: "Use <REDACTED> for sensitive data"
  └─ Temperature: 0.25 (reduces hallucination of fake PII)

Layer 3: Output Validation (Presidio)
  ├─ Scan LLM response for PII patterns
  ├─ Block response if PII detected
  └─ Log PII leakage incident (security audit)

Layer 4: OPA Policy (Final Gate)
  ├─ Policy: pii_leakage.rego
  ├─ Check: count(presidio.output_entities) == 0
  └─ Action: DENY if PII detected
```

**PII Entity Types:**

```yaml
# config/presidio_entities.yaml
entities:
  high_priority:  # Block immediately
    - US_SSN
    - CREDIT_CARD
    - US_BANK_NUMBER
    - CRYPTO_ADDRESS

  medium_priority:  # Anonymize
    - PHONE_NUMBER
    - EMAIL_ADDRESS
    - US_DRIVER_LICENSE
    - US_PASSPORT

  low_priority:  # Log only
    - PERSON
    - LOCATION
    - ORGANIZATION
```

**Anonymization Mapping:**

```json
{
  "request_id": "req_abc123",
  "anonymization_map": {
    "<SSN_1>": "123-45-6789",
    "<ACCOUNT_1>": "9876543210",
    "<PHONE_1>": "+1-555-123-4567"
  },
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_id": "kms://key-12345"
  },
  "access_policy": {
    "authorized_roles": ["compliance_officer", "security_admin"],
    "audit_required": true
  }
}
```

### 9.2 Data Retention & Privacy

**Data Retention Policy:**

```yaml
# config/data_retention.yaml
data_retention:
  conversation_transcripts:
    retention_days: 90
    encryption: "AES-256"
    pii_anonymized: true

  llm_responses:
    retention_days: 180
    encryption: "AES-256"
    pii_anonymized: true

  evaluation_metrics:
    retention_days: 365
    encryption: "none"  # Aggregated metrics, no PII

  opa_policy_logs:
    retention_days: 730  # 2 years for compliance audit
    encryption: "AES-256"

  anonymization_maps:
    retention_days: 90
    encryption: "AES-256-GCM"
    key_rotation: true
    access_logging: true
```

**GDPR Compliance:**

```yaml
# config/gdpr_compliance.yaml
gdpr:
  enabled: true

  data_subject_rights:
    right_to_access:
      enabled: true
      response_time_days: 30

    right_to_erasure:
      enabled: true
      response_time_days: 30
      cascade_delete: true  # Delete all related data

    right_to_rectification:
      enabled: true
      response_time_days: 30

    right_to_portability:
      enabled: true
      export_format: "JSON"

  lawful_basis:
    processing: "legitimate_interest"
    storage: "legal_obligation"

  privacy_by_design:
    data_minimization: true
    pseudonymization: true
    encryption_at_rest: true
    encryption_in_transit: true
```

### 9.3 Access Control

**Role-Based Access Control (RBAC):**

```yaml
# config/rbac.yaml
roles:
  api_consumer:
    permissions:
      - "request:submit"
      - "response:read"
    resource_scope: "own_requests"

  compliance_officer:
    permissions:
      - "request:read"
      - "response:read"
      - "anonymization_map:read"
      - "opa_logs:read"
    resource_scope: "all"
    audit_required: true

  security_admin:
    permissions:
      - "pii_detection:configure"
      - "opa_policy:read"
      - "audit_logs:read"
    resource_scope: "all"
    mfa_required: true

  ml_engineer:
    permissions:
      - "evaluation:read"
      - "metrics:read"
      - "model:read"
    resource_scope: "production"

  system_admin:
    permissions:
      - "*"
    resource_scope: "all"
    mfa_required: true
    audit_required: true
```

### 9.4 Audit Logging

**Audit Events:**

```yaml
# Audit log events
audit_events:
  - event: "pii_detected"
    fields: [request_id, user_id, entity_types, timestamp]
    retention_days: 730

  - event: "opa_policy_violation"
    fields: [request_id, policy_name, deny_reasons, confidence_score]
    retention_days: 730

  - event: "anonymization_map_accessed"
    fields: [request_id, accessor_id, accessor_role, timestamp]
    retention_days: 730

  - event: "fallback_triggered"
    fields: [request_id, reason, stage, error_details]
    retention_days: 365

  - event: "data_subject_request"
    fields: [request_type, user_id, requester_id, timestamp, status]
    retention_days: 2555  # 7 years for legal compliance
```

**Audit Log Format:**

```json
{
  "event_id": "audit_789xyz",
  "event_type": "opa_policy_violation",
  "timestamp": "2025-10-16T16:30:05.123Z",

  "actor": {
    "user_id": "user_xyz789",
    "ip_address": "203.0.113.42",
    "user_agent": "Mozilla/5.0..."
  },

  "resource": {
    "request_id": "req_abc123",
    "resource_type": "llm_response",
    "policy_name": "confidence_threshold"
  },

  "action": {
    "action_type": "policy_evaluation",
    "result": "DENY",
    "deny_reasons": [
      "Confidence score 0.73 below threshold 0.85"
    ]
  },

  "metadata": {
    "environment": "production",
    "version": "2.0.0"
  }
}
```

---

## 10. Implementation Roadmap

### 10.1 Phase 1: Foundation (Weeks 1-3)

**Objective:** Build request-response pipeline without OPA

**Deliverables:**

**Week 1: Core Pipeline**
- [ ] API Gateway setup (FastAPI/Flask)
- [ ] Stage 1: PII Detection layer (Presidio integration)
- [ ] Stage 2: Input Schema Converter (LLM-based)
- [ ] Stage 3: LLM Invocation (existing promptproject integration)
- [ ] Stage 4: Guardrails Validation (existing)
- [ ] End-to-end request-response flow (no evaluation yet)

**Week 2: Evaluation Integration**
- [ ] Evaluation Orchestrator framework
- [ ] Phoenix Adapter implementation
- [ ] Ragas Adapter implementation
- [ ] MLflow Adapter implementation
- [ ] Parallel execution with timeout handling
- [ ] Result aggregation logic

**Week 3: Testing & Validation**
- [ ] Unit tests for each pipeline stage
- [ ] Integration tests for end-to-end flow
- [ ] Load testing (100 req/min target)
- [ ] Golden dataset validation (≥95% accuracy)
- [ ] Error handling and retry logic
- [ ] Fallback response templates

**Success Criteria:**
- End-to-end pipeline functional
- All evaluation adapters working
- P95 latency < 7s (pre-optimization)
- 95% success rate on golden dataset

---

### 10.2 Phase 2: OPA Integration (Weeks 4-6)

**Objective:** Add OPA policy validation layer

**Deliverables:**

**Week 4: OPA Infrastructure**
- [ ] OPA sidecar deployment (Docker Compose for local, K8s for prod)
- [ ] Policy bundle structure (`policies/opa/`)
- [ ] Master policy aggregation (`master.rego`)
- [ ] HTTP API integration (pipeline → OPA)
- [ ] Policy unit tests

**Week 5: Policy Development**
- [ ] Tier 1: Blocking policies (confidence, hallucination, PII, compliance)
- [ ] Tier 2: High-priority policies (quality, business rules)
- [ ] Tier 3: Standard policies (edge cases)
- [ ] Tier 4: Monitoring policies (performance)
- [ ] Policy testing suite (100% coverage)

**Week 6: Integration & Tuning**
- [ ] Stage 6: OPA Policy Validation integration
- [ ] Stage 7: Response Handler with decision routing
- [ ] Confidence score threshold tuning (baseline: 0.85)
- [ ] Fallback response testing
- [ ] Policy GitOps workflow (CI/CD for .rego files)

**Success Criteria:**
- OPA policies blocking "confidently wrong" responses
- 100% pass rate on adversarial tests
- Fallback responses functioning correctly
- Policy updates deployable via GitOps

---

### 10.3 Phase 3: Observability (Weeks 7-8)

**Objective:** Add monitoring, tracing, and alerting

**Deliverables:**

**Week 7: Tracing & Metrics**
- [ ] OpenTelemetry instrumentation
- [ ] Distributed tracing (Jaeger/Tempo)
- [ ] Prometheus metrics export
- [ ] Grafana dashboards (executive + technical)
- [ ] Log aggregation (ELK/Loki)

**Week 8: Alerting & Audit**
- [ ] Critical alerts (PagerDuty)
- [ ] Warning alerts (Slack)
- [ ] Audit log pipeline
- [ ] Security event monitoring
- [ ] Cost tracking dashboard

**Success Criteria:**
- End-to-end tracing functional
- All key metrics collected
- Alert rules tested and validated
- Audit logs compliant with GDPR

---

### 10.4 Phase 4: Production Hardening (Weeks 9-10)

**Objective:** Security, performance, and reliability improvements

**Deliverables:**

**Week 9: Security Hardening**
- [ ] PII anonymization mapping with encryption
- [ ] RBAC implementation
- [ ] Data retention automation
- [ ] GDPR compliance validation
- [ ] Security audit

**Week 10: Performance Optimization**
- [ ] Evaluation result caching (60s TTL)
- [ ] Async execution optimization
- [ ] Circuit breaker implementation
- [ ] Load testing (500 req/min)
- [ ] P95 latency optimization (target: <5s)

**Success Criteria:**
- Security audit passed
- P95 latency < 5s
- 99% uptime target
- Cost per request < $0.10

---

### 10.5 Phase 5: Production Deployment (Weeks 11-12)

**Objective:** Staged rollout to production

**Deliverables:**

**Week 11: Staging Deployment**
- [ ] Deploy to staging environment
- [ ] Smoke tests (10 requests)
- [ ] Synthetic traffic testing (100 req/min for 24 hours)
- [ ] Policy validation on production-like data
- [ ] Runbook documentation

**Week 12: Production Rollout**
- [ ] Canary deployment (1% traffic)
- [ ] Monitor for 24 hours
- [ ] Gradual rollout (1% → 10% → 50% → 100%)
- [ ] Post-deployment validation
- [ ] Incident response training

**Success Criteria:**
- Zero critical incidents during rollout
- 99% success rate on production traffic
- P95 latency < 5s
- Cost per request < $0.10

---

## 11. Appendix: Decision Matrix

### 11.1 Technology Selection Rationale

| Decision | Options Considered | Selected | Rationale |
|----------|-------------------|----------|-----------|
| **LLM Provider** | OpenAI GPT-4, Anthropic Claude, Google Gemini | Anthropic Claude Sonnet 4.5 | Balance of quality, cost, and speed. Temperature=0.25 for precision. Existing promptproject uses Claude. |
| **Policy Engine** | Custom Python, Casbin, OPA | Open Policy Agent (OPA) | Industry standard, declarative Rego language, testable, GitOps-friendly, widely adopted. |
| **Evaluation Frameworks** | DeepEval only, Ragas only, MLflow only | Phoenix + Ragas + MLflow | Multi-framework validation reduces single-point-of-failure. Learnings from promptforge show 93 evaluations across 6 adapters. |
| **PII Detection** | spaCy NER, AWS Comprehend, Presidio | Presidio (Microsoft) | Open-source, customizable, comprehensive entity recognition, already in promptproject. |
| **Tracing** | Jaeger native, OpenTelemetry, Zipkin | OpenTelemetry | Vendor-neutral, widely adopted, supports multiple backends (Jaeger, Tempo, etc.). |
| **Metrics** | StatsD, Prometheus, DataDog | Prometheus | Open-source, pull-based model, integrates with Grafana, K8s-native. |
| **API Framework** | Flask, FastAPI, Django REST | FastAPI | Async support (for parallel evaluations), automatic OpenAPI docs, type hints, fast. |
| **Deployment** | VMs, Docker Compose, Kubernetes | Kubernetes | Scalable, OPA sidecar pattern, health checks, rolling updates, production-grade. |

### 11.2 Confidence Threshold Tuning

**Baseline Configuration:**

| Metric | Weight | Threshold | Justification |
|--------|--------|-----------|---------------|
| **Phoenix: Q&A Quality** | 25% | ≥ 0.85 | Core quality indicator |
| **Phoenix: Hallucination** | 15% | PASS (binary) | Critical for "confidently wrong" prevention |
| **Ragas: Faithfulness** | 30% | ≥ 0.95 | Most important - facts must be grounded |
| **Ragas: Context Precision** | 15% | ≥ 0.90 | Prevents over-extraction |
| **Ragas: Context Recall** | 10% | ≥ 0.85 | Ensures completeness |
| **MLflow: Answer Correctness** | 5% | ≥ 0.90 | Regression validation |
| **Aggregate Confidence** | 100% | ≥ 0.85 | **Final threshold for OPA ALLOW** |

**Tuning Strategy:**

```
Step 1: Establish Baseline (Golden Dataset)
  ├─ Run 100 golden dataset examples
  ├─ Measure aggregate confidence distribution
  ├─ Identify P50, P95, P99 confidence scores
  └─ Set threshold at P10 (conservative)

Step 2: Validate with Edge Cases
  ├─ Run 50 edge case examples
  ├─ Expect lower confidence scores
  ├─ Ensure true failures are blocked
  └─ Adjust threshold if too many false positives

Step 3: Adversarial Testing
  ├─ Run 50 adversarial examples
  ├─ Expect DENY decisions (hallucination, low confidence)
  ├─ Validate fallback messages are appropriate
  └─ Confirm 100% blocking of malicious inputs

Step 4: Production A/B Testing
  ├─ Deploy with threshold = 0.80 (more permissive)
  ├─ Monitor false positive rate (should PASS but DENY)
  ├─ Monitor false negative rate (should DENY but PASS)
  └─ Adjust threshold to minimize false negatives (priority)
```

### 11.3 Cost Analysis

**Per-Request Cost Breakdown:**

| Component | Provider | Cost Estimate | Notes |
|-----------|----------|---------------|-------|
| **Input Schema Conversion** | Claude Sonnet 4.5 | $0.005 | ~500 tokens input, 200 tokens output |
| **Fact Extraction** | Claude Sonnet 4.5 | $0.025 | ~1200 tokens input, 800 tokens output |
| **Phoenix Evaluation** | GPT-4 (via Phoenix API) | $0.015 | ~400 tokens per metric |
| **Ragas Evaluation** | GPT-4 + Embeddings | $0.020 | Multiple metrics, embeddings |
| **MLflow Evaluation** | GPT-4 + Perspective API | $0.012 | Answer correctness + toxicity check |
| **OPA Policy Validation** | Self-hosted | $0.001 | Negligible compute cost |
| **Total per Request** | - | **$0.078** | **~8 cents per request** |

**Monthly Cost Projection:**

```
Assumptions:
- 10,000 requests/day
- 300,000 requests/month
- 20% fallback rate (no evaluation cost for schema conversion failures)

Breakdown:
- LLM Invocations: $9,000 (300k * $0.030)
- Evaluations: $14,100 (240k successful * $0.047)
- Infrastructure: $500 (K8s, OPA, monitoring)

Total Monthly Cost: $23,600
Cost per Request: $0.078
```

**Cost Optimization Strategies:**

1. **Evaluation Caching (60s TTL):**
   - Cache evaluation results for identical inputs
   - Expected savings: 20% reduction in evaluation costs
   - New cost: $0.068/request

2. **Selective Evaluation:**
   - Run Phoenix + Ragas always (critical)
   - Run MLflow only on golden dataset validation (periodic)
   - Expected savings: 15% reduction
   - New cost: $0.066/request

3. **Model Optimization:**
   - Use GPT-4o-mini for non-critical evaluations
   - Expected savings: 30% reduction in evaluation costs
   - New cost: $0.064/request

**Target Cost:** < $0.10 per request

---

## Conclusion

This reference architecture provides a comprehensive blueprint for transforming the existing promptproject into a production-grade LLM pipeline with OPA-based policy validation. The key innovations are:

1. **OPA Integration:** Declarative policies prevent "confidently wrong" responses through multi-metric confidence scoring and business rule validation.

2. **Multi-Framework Evaluation:** Phoenix, Ragas, and MLflow provide comprehensive quality assessment, reducing single-framework bias.

3. **Structured Pipeline:** 7-stage flow with clear responsibilities, error handling, and fallback mechanisms.

4. **Observability:** OpenTelemetry tracing, Prometheus metrics, and structured logging enable production monitoring and debugging.

5. **Security & Compliance:** Multi-layer PII protection, audit logging, and GDPR compliance.

The phased implementation roadmap (12 weeks) provides a clear path from the current test-focused system to a production-ready API service.

**Next Steps:**
1. Review this architecture with stakeholders
2. Prioritize phases based on business needs
3. Begin Phase 1 implementation (Foundation)
4. Iteratively refine policies and thresholds based on production data

---

**Document Version:** 2.0
**Last Updated:** 2025-10-16
**Status:** Design Specification - Ready for Implementation Review
