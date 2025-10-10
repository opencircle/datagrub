# Phase 3: Privacy-by-Design Framework with Presidio Integration

## Objective
Implement a comprehensive privacy framework using Microsoft Presidio to protect sensitive data throughout the prompt execution pipeline. This framework follows the **privacy-by-design** principle, ensuring PII (Personally Identifiable Information) is automatically detected, anonymized before LLM invocation, and de-anonymized post-execution for safe auditing.

---

## 1. Purpose

To build a **privacy-first prompt execution pipeline** that:
- **Prevents PII leakage** to LLM providers (OpenAI, Anthropic, etc.)
- **Enables compliance** with GDPR, HIPAA, CCPA, and other privacy regulations
- **Maintains traceability** through reversible anonymization
- **Supports multi-person PII** in complex conversations
- **Handles multi-modal data** (text, images, documents)
- **Integrates seamlessly** via decorator pattern without code changes

---

## 2. Core Privacy Principles

### Privacy-by-Design Tenets
1. **Proactive not Reactive** - PII detection happens before LLM invocation
2. **Privacy as Default** - Security enabled by default when `isSecure=true`
3. **Privacy Embedded in Design** - Decorator pattern ensures separation of concerns
4. **Full Functionality** - Privacy doesn't compromise system capabilities
5. **End-to-End Security** - Protection throughout entire data lifecycle
6. **Visibility and Transparency** - All anonymization/de-anonymization logged
7. **Respect for User Privacy** - User data never exposed unnecessarily

### Threat Model
**What We Protect Against:**
- PII leakage to third-party LLM providers
- Data breaches in trace logs
- Compliance violations (GDPR Article 32, HIPAA §164.308)
- Insider threats accessing sensitive traces
- Cross-tenant data exposure

**What We Preserve:**
- Evaluation quality and accuracy
- Trace auditing and debugging
- User experience and functionality
- System performance (< 100ms overhead)

---

## 3. Presidio Integration Architecture

### Microsoft Presidio Overview
**Components:**
- **Presidio Analyzer** - Detects PII entities (names, emails, SSN, etc.)
- **Presidio Anonymizer** - Replaces PII with tokens or fake data
- **Presidio De-Anonymizer** - Reverses anonymization for authorized access
- **Presidio Image Redactor** - Redacts PII from images (OCR-based)

**Supported PII Entities (50+):**
- Personal: NAME, EMAIL, PHONE, SSN, DATE_OF_BIRTH
- Financial: CREDIT_CARD, IBAN, CRYPTO
- Medical: MEDICAL_LICENSE, HEALTH_DATA
- Location: ADDRESS, ZIP_CODE, IP_ADDRESS
- Custom: Configurable regex patterns

### Decorator Pattern Implementation

```python
from typing import Callable, Optional, Dict, Any
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig
from dataclasses import dataclass
import logging

@dataclass
class PresidioConfig:
    """Configuration for Presidio privacy protection"""
    enabled: bool = False
    entities_to_detect: list[str] = None  # Default: all entities
    anonymization_method: str = "replace"  # replace, mask, hash, encrypt
    language: str = "en"
    score_threshold: float = 0.5
    multi_person_support: bool = True
    store_mapping: bool = True  # For de-anonymization
    custom_recognizers: Optional[list] = None

class PresidioDecorator:
    """
    Decorator for prompt execution with Presidio PII protection.

    Flow:
    1. Pre-LLM: Detect and anonymize PII in prompt
    2. LLM Execution: Send anonymized prompt to LLM
    3. Post-LLM: De-anonymize response for trace storage
    4. Trace Storage: Store both anonymized (for LLM) and de-anonymized (for audit)
    """

    def __init__(self, config: PresidioConfig):
        self.config = config
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.deanonymizer = DeanonymizeEngine()
        self.anonymization_mapping = {}  # trace_id -> {entity -> original_value}

    def __call__(self, func: Callable) -> Callable:
        """Decorate prompt execution function"""
        async def wrapper(
            prompt: str,
            trace_id: str,
            **kwargs
        ) -> Dict[str, Any]:
            if not self.config.enabled:
                # Privacy disabled, pass through
                return await func(prompt=prompt, trace_id=trace_id, **kwargs)

            # Step 1: Analyze prompt for PII
            analyzer_results = self.analyzer.analyze(
                text=prompt,
                entities=self.config.entities_to_detect,
                language=self.config.language,
                score_threshold=self.config.score_threshold,
            )

            logging.info(f"[Presidio] Detected {len(analyzer_results)} PII entities in trace {trace_id}")

            # Step 2: Anonymize prompt
            anonymized_result = self.anonymizer.anonymize(
                text=prompt,
                analyzer_results=analyzer_results,
                operators={
                    "DEFAULT": OperatorConfig(self.config.anonymization_method)
                }
            )

            anonymized_prompt = anonymized_result.text

            # Step 3: Store mapping for de-anonymization
            if self.config.store_mapping:
                self.anonymization_mapping[trace_id] = {
                    item.entity_type: item.text
                    for item in anonymized_result.items
                }

            # Step 4: Execute LLM with anonymized prompt
            llm_response = await func(
                prompt=anonymized_prompt,
                trace_id=trace_id,
                **kwargs
            )

            # Step 5: Analyze response for PII
            response_text = llm_response.get("output", "")
            response_analyzer_results = self.analyzer.analyze(
                text=response_text,
                entities=self.config.entities_to_detect,
                language=self.config.language,
                score_threshold=self.config.score_threshold,
            )

            # Step 6: De-anonymize response if needed
            if self.config.store_mapping and response_analyzer_results:
                # De-anonymize using stored mapping
                deanonymized_response = self.deanonymizer.deanonymize(
                    text=response_text,
                    entities=anonymized_result.items
                )
                llm_response["output_deanonymized"] = deanonymized_response.text

            # Step 7: Attach privacy metadata
            llm_response["privacy_metadata"] = {
                "presidio_enabled": True,
                "pii_detected_in_prompt": len(analyzer_results),
                "pii_detected_in_response": len(response_analyzer_results),
                "entities_anonymized": [item.entity_type for item in anonymized_result.items],
                "anonymization_method": self.config.anonymization_method,
                "anonymized_prompt": anonymized_prompt,  # Store for auditing
            }

            return llm_response

        return wrapper
```

### Integration with Prompt Execution Pipeline

```python
# app/services/prompt_execution.py

from app.services.privacy import PresidioDecorator, PresidioConfig

class PromptExecutionService:
    """Service for executing prompts with optional privacy protection"""

    async def execute_prompt(
        self,
        trace_id: str,
        prompt: str,
        model_config: Dict[str, Any],
        is_secure: bool = False,  # NEW PARAMETER
        privacy_config: Optional[PresidioConfig] = None,
    ) -> Dict[str, Any]:
        """
        Execute prompt with optional Presidio privacy protection.

        Args:
            trace_id: Unique trace identifier
            prompt: User input prompt
            model_config: LLM configuration (model, temperature, etc.)
            is_secure: Enable Presidio privacy protection
            privacy_config: Custom Presidio configuration (optional)

        Returns:
            Execution result with privacy metadata
        """

        # Build Presidio config
        if is_secure:
            if privacy_config is None:
                # Use default secure configuration
                privacy_config = PresidioConfig(
                    enabled=True,
                    entities_to_detect=None,  # All entities
                    anonymization_method="replace",
                    multi_person_support=True,
                    store_mapping=True,
                )
            else:
                privacy_config.enabled = True
        else:
            privacy_config = PresidioConfig(enabled=False)

        # Create decorator
        presidio = PresidioDecorator(config=privacy_config)

        # Decorate execution function
        @presidio
        async def _execute(prompt: str, trace_id: str, **kwargs):
            # Call LLM provider
            return await self._call_llm(
                prompt=prompt,
                model_config=model_config,
                trace_id=trace_id,
            )

        # Execute with privacy protection
        result = await _execute(
            prompt=prompt,
            trace_id=trace_id,
        )

        return result
```

---

## 4. API Integration

### Enhanced Trace Execution API

#### POST /projects/{project_id}/traces/execute

**Request with Privacy:**
```json
{
  "prompt": "My name is John Smith and my email is john.smith@example.com. Can you help me?",
  "model_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "is_secure": true,
  "privacy_config": {
    "entities_to_detect": ["PERSON", "EMAIL", "PHONE"],
    "anonymization_method": "replace",
    "multi_person_support": true,
    "score_threshold": 0.6
  }
}
```

**Response:**
```json
{
  "trace_id": "uuid",
  "output": "Hello! I'd be happy to help you.",
  "privacy_metadata": {
    "presidio_enabled": true,
    "pii_detected_in_prompt": 2,
    "pii_detected_in_response": 0,
    "entities_anonymized": ["PERSON", "EMAIL"],
    "anonymization_method": "replace",
    "anonymized_prompt": "My name is <PERSON> and my email is <EMAIL>. Can you help me?"
  },
  "execution_time_ms": 1250.5,
  "tokens_used": 45
}
```

### Enhanced Evaluation Execution API

#### POST /evaluation-catalog/execute

**Request with Privacy:**
```json
{
  "trace_id": "uuid",
  "evaluation_ids": ["uuid1", "uuid2"],
  "is_secure": true,
  "privacy_config": {
    "entities_to_detect": ["PERSON", "EMAIL", "PHONE", "SSN"],
    "anonymization_method": "hash",
    "store_mapping": true
  }
}
```

**Behavior:**
1. Retrieve trace with `trace_id`
2. Apply Presidio anonymization to trace input/output
3. Execute evaluations on anonymized data
4. Store evaluation results with privacy metadata
5. De-anonymize for authorized viewing

---

## 5. Presidio Capabilities Configuration

### PII Detection Entities

```python
class PresidioEntities:
    """Supported PII entity types"""

    # Personal Identifiers
    PERSON = "PERSON"
    EMAIL = "EMAIL_ADDRESS"
    PHONE = "PHONE_NUMBER"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"

    # Government IDs
    SSN = "US_SSN"
    PASSPORT = "US_PASSPORT"
    DRIVERS_LICENSE = "US_DRIVER_LICENSE"

    # Financial
    CREDIT_CARD = "CREDIT_CARD"
    IBAN = "IBAN_CODE"
    CRYPTO = "CRYPTO"

    # Medical
    MEDICAL_LICENSE = "MEDICAL_LICENSE"

    # Location
    ADDRESS = "LOCATION"
    ZIP_CODE = "ZIP_CODE"
    IP_ADDRESS = "IP_ADDRESS"

    # Custom (configurable)
    @staticmethod
    def custom(pattern: str, name: str):
        """Register custom PII pattern"""
        pass
```

### Anonymization Methods

```python
class AnonymizationMethods:
    """Available anonymization techniques"""

    REPLACE = "replace"  # <PERSON>, <EMAIL>
    MASK = "mask"        # J*** S*****, j***@example.com
    HASH = "hash"        # SHA256 hash
    ENCRYPT = "encrypt"  # AES-256 encryption (reversible)
    REDACT = "redact"    # [REDACTED]
    FAKE = "fake"        # Realistic fake data (Faker library)
```

### Multi-Person Support

```python
# Example: Multi-person conversation
prompt = """
Alice (alice@company.com) called Bob (bob@company.com) about the Johnson account.
Bob's SSN is 123-45-6789. Alice's phone is 555-1234.
"""

# Presidio with multi-person tracking
config = PresidioConfig(
    enabled=True,
    multi_person_support=True,
    anonymization_method="replace"
)

# Anonymized output:
"""
<PERSON_1> (<EMAIL_1>) called <PERSON_2> (<EMAIL_2>) about the Johnson account.
<PERSON_2>'s SSN is <SSN_1>. <PERSON_1>'s phone is <PHONE_1>.
"""

# Mapping stored:
{
    "PERSON_1": "Alice",
    "EMAIL_1": "alice@company.com",
    "PERSON_2": "Bob",
    "EMAIL_2": "bob@company.com",
    "SSN_1": "123-45-6789",
    "PHONE_1": "555-1234"
}
```

### Multi-Modal Support

```python
from presidio_image_redactor import ImageRedactorEngine

class MultiModalPresidioDecorator(PresidioDecorator):
    """Extended decorator for multi-modal PII protection"""

    def __init__(self, config: PresidioConfig):
        super().__init__(config)
        self.image_redactor = ImageRedactorEngine()

    async def redact_image(self, image_path: str) -> str:
        """Redact PII from images using OCR"""
        redacted_image = self.image_redactor.redact(
            image_path=image_path,
            fill="blur",  # or "black", "white"
            padding_width=25
        )
        return redacted_image

    async def redact_document(self, document_path: str) -> str:
        """Redact PII from PDFs and documents"""
        # Extract text with OCR
        # Apply text-based anonymization
        # Redact in original document
        pass
```

---

## 6. Database Schema Extensions

### privacy_configs Table

```sql
CREATE TABLE privacy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Configuration
    is_default BOOLEAN DEFAULT false,
    enabled BOOLEAN DEFAULT true,

    -- Presidio Settings
    entities_to_detect TEXT[],  -- Array of entity types
    anonymization_method VARCHAR(50) NOT NULL,  -- replace, mask, hash, encrypt
    score_threshold FLOAT DEFAULT 0.5,
    language VARCHAR(10) DEFAULT 'en',
    multi_person_support BOOLEAN DEFAULT true,
    store_mapping BOOLEAN DEFAULT true,

    -- Custom Recognizers
    custom_recognizers JSONB DEFAULT '[]',

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    -- Indexes
    INDEX idx_privacy_org (organization_id),
    INDEX idx_privacy_project (project_id),
    UNIQUE (organization_id, project_id, is_default)
);
```

### anonymization_mappings Table

```sql
CREATE TABLE anonymization_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,

    -- Mapping Data (encrypted)
    entity_type VARCHAR(100) NOT NULL,
    anonymized_value TEXT NOT NULL,
    original_value_encrypted BYTEA NOT NULL,  -- AES-256 encrypted

    -- Metadata
    person_index INTEGER,  -- For multi-person support
    position_start INTEGER,
    position_end INTEGER,
    confidence_score FLOAT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accessed_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    accessed_by UUID REFERENCES users(id),

    -- Indexes
    INDEX idx_mapping_trace (trace_id),
    INDEX idx_mapping_entity (entity_type)
);
```

### Enhanced traces Table

```sql
ALTER TABLE traces ADD COLUMN privacy_enabled BOOLEAN DEFAULT false;
ALTER TABLE traces ADD COLUMN pii_detected_count INTEGER DEFAULT 0;
ALTER TABLE traces ADD COLUMN entities_anonymized TEXT[];
ALTER TABLE traces ADD COLUMN anonymized_input TEXT;  -- Anonymized version
ALTER TABLE traces ADD COLUMN privacy_config_id UUID REFERENCES privacy_configs(id);
```

---

## 7. Security & Compliance

### Encryption at Rest
```python
from cryptography.fernet import Fernet

class SecureMapping:
    """Encrypted storage for anonymization mappings"""

    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)

    def encrypt(self, original_value: str) -> bytes:
        """Encrypt original PII value"""
        return self.cipher.encrypt(original_value.encode())

    def decrypt(self, encrypted_value: bytes) -> str:
        """Decrypt for authorized de-anonymization"""
        return self.cipher.decrypt(encrypted_value).decode()
```

### Access Control for De-Anonymization

```python
from app.auth.permissions import require_permission

@require_permission("pii:read")
async def deanonymize_trace(
    trace_id: str,
    current_user: User,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    De-anonymize trace for authorized users.

    Requires: pii:read permission
    Logs: All de-anonymization access
    """
    # Retrieve trace
    trace = await db.get(Trace, trace_id)

    if not trace.privacy_enabled:
        return trace.to_dict()

    # Retrieve anonymization mappings
    mappings = await db.execute(
        select(AnonymizationMapping)
        .where(AnonymizationMapping.trace_id == trace_id)
    )

    # Decrypt and de-anonymize
    deanonymized_input = trace.anonymized_input
    for mapping in mappings:
        original_value = secure_mapping.decrypt(mapping.original_value_encrypted)
        deanonymized_input = deanonymized_input.replace(
            mapping.anonymized_value,
            original_value
        )

    # Log access
    await audit_log.log(
        event="pii:deanonymize",
        user_id=current_user.id,
        trace_id=trace_id,
        timestamp=datetime.utcnow()
    )

    return {
        "trace_id": trace_id,
        "input": deanonymized_input,
        "output": trace.output,
        "privacy_metadata": trace.privacy_metadata
    }
```

### Compliance Mappings

```python
class ComplianceProfiles:
    """Pre-configured profiles for compliance standards"""

    GDPR = PresidioConfig(
        enabled=True,
        entities_to_detect=["PERSON", "EMAIL", "PHONE", "LOCATION", "IP_ADDRESS"],
        anonymization_method="encrypt",
        store_mapping=True,
        multi_person_support=True
    )

    HIPAA = PresidioConfig(
        enabled=True,
        entities_to_detect=[
            "PERSON", "DATE_OF_BIRTH", "PHONE", "EMAIL",
            "SSN", "MEDICAL_LICENSE", "LOCATION"
        ],
        anonymization_method="hash",
        store_mapping=False,  # HIPAA may prohibit mapping storage
        multi_person_support=True
    )

    CCPA = PresidioConfig(
        enabled=True,
        entities_to_detect=["PERSON", "EMAIL", "PHONE", "IP_ADDRESS", "LOCATION"],
        anonymization_method="replace",
        store_mapping=True,
        multi_person_support=True
    )

    PCI_DSS = PresidioConfig(
        enabled=True,
        entities_to_detect=["CREDIT_CARD", "IBAN", "CRYPTO"],
        anonymization_method="mask",
        store_mapping=False,
        multi_person_support=False
    )
```

---

## 8. API Endpoints

### Privacy Configuration Management

#### POST /privacy/configs
Create privacy configuration for organization/project.

**Request:**
```json
{
  "organization_id": "uuid",
  "project_id": "uuid",  // optional
  "is_default": true,
  "enabled": true,
  "entities_to_detect": ["PERSON", "EMAIL", "PHONE"],
  "anonymization_method": "replace",
  "score_threshold": 0.6,
  "multi_person_support": true,
  "compliance_profile": "GDPR"  // Auto-applies GDPR settings
}
```

#### GET /privacy/configs
List privacy configurations.

**Query Parameters:**
- `organization_id` - Filter by organization
- `project_id` - Filter by project
- `is_default` - Get default config

#### PUT /privacy/configs/{config_id}
Update privacy configuration.

#### DELETE /privacy/configs/{config_id}
Delete privacy configuration.

---

### Privacy Testing

#### POST /privacy/analyze
Test PII detection without anonymization.

**Request:**
```json
{
  "text": "My name is John Smith, email john@example.com, SSN 123-45-6789",
  "entities_to_detect": ["PERSON", "EMAIL", "SSN"],
  "language": "en",
  "score_threshold": 0.5
}
```

**Response:**
```json
{
  "pii_detected": 3,
  "entities": [
    {
      "entity_type": "PERSON",
      "text": "John Smith",
      "start": 11,
      "end": 21,
      "score": 0.95
    },
    {
      "entity_type": "EMAIL",
      "text": "john@example.com",
      "start": 29,
      "end": 45,
      "score": 1.0
    },
    {
      "entity_type": "SSN",
      "text": "123-45-6789",
      "start": 51,
      "end": 62,
      "score": 0.99
    }
  ]
}
```

#### POST /privacy/anonymize
Test anonymization.

**Request:**
```json
{
  "text": "My name is John Smith",
  "anonymization_method": "replace",
  "entities_to_detect": ["PERSON"]
}
```

**Response:**
```json
{
  "anonymized_text": "My name is <PERSON>",
  "entities_anonymized": ["PERSON"],
  "mapping": {
    "PERSON": "John Smith"
  }
}
```

---

## 9. Implementation Timeline

### Week 1-2: Presidio Integration (12-15 hours)
- [ ] Install Presidio libraries (analyzer, anonymizer, image-redactor)
- [ ] Create PresidioDecorator class
- [ ] Implement basic PII detection and anonymization
- [ ] Unit tests for decorator pattern

### Week 3-4: API Integration (15-18 hours)
- [ ] Add `is_secure` parameter to trace execution API
- [ ] Add `is_secure` parameter to evaluation execution API
- [ ] Integrate PresidioDecorator into PromptExecutionService
- [ ] Create privacy_configs and anonymization_mappings tables
- [ ] Database migrations

### Week 5-6: Advanced Features (18-22 hours)
- [ ] Multi-person PII support
- [ ] Multi-modal support (images, documents)
- [ ] Custom entity recognizers
- [ ] Encryption at rest for mappings
- [ ] De-anonymization with access control

### Week 7-8: Compliance & Testing (15-18 hours)
- [ ] Compliance profiles (GDPR, HIPAA, CCPA, PCI-DSS)
- [ ] Privacy management APIs
- [ ] Privacy testing endpoints (analyze, anonymize)
- [ ] Comprehensive integration tests
- [ ] Performance optimization (< 100ms overhead)

### Week 9-10: Documentation & Validation (10-12 hours)
- [ ] API documentation
- [ ] Compliance documentation
- [ ] User guides
- [ ] End-to-end validation script
- [ ] Security audit

**Total: 70-85 hours (9-11 weeks part-time)**

---

## 10. Success Criteria

Phase 3 Privacy Framework is complete when:

**Core Functionality:**
- [ ] Presidio decorator working with all LLM providers
- [ ] `is_secure` parameter functional in trace execution API
- [ ] `is_secure` parameter functional in evaluation execution API
- [ ] PII detection accuracy >= 95% for common entities
- [ ] Anonymization/de-anonymization round-trip successful

**Advanced Features:**
- [ ] Multi-person PII tracking functional
- [ ] Multi-modal support (images) working
- [ ] Custom entity recognizers configurable
- [ ] Encryption at rest implemented
- [ ] Access control for de-anonymization enforced

**Performance:**
- [ ] Privacy overhead < 100ms per prompt
- [ ] No degradation in LLM response quality
- [ ] Scalable to 10,000+ traces/day

**Compliance:**
- [ ] GDPR compliance profile validated
- [ ] HIPAA compliance profile validated
- [ ] Audit logging complete
- [ ] Security audit passed

**Documentation:**
- [ ] API documentation complete
- [ ] Compliance mapping documented
- [ ] User guides created
- [ ] Integration examples provided

---

## 11. Example Use Cases

### Healthcare: HIPAA Compliance
```python
# Execute prompt with HIPAA privacy
result = await prompt_service.execute_prompt(
    trace_id=trace_id,
    prompt="Patient John Doe, DOB 01/15/1980, SSN 123-45-6789 has diabetes",
    model_config={"provider": "openai", "model": "gpt-4"},
    is_secure=True,
    privacy_config=ComplianceProfiles.HIPAA
)

# LLM receives:
# "Patient <PERSON>, DOB <DATE_OF_BIRTH>, SSN <SSN> has diabetes"
```

### Finance: PCI-DSS Compliance
```python
result = await prompt_service.execute_prompt(
    trace_id=trace_id,
    prompt="Process payment for card 4532-1234-5678-9010",
    model_config={"provider": "anthropic", "model": "claude-3"},
    is_secure=True,
    privacy_config=ComplianceProfiles.PCI_DSS
)

# LLM receives:
# "Process payment for card ****-****-****-9010"
```

### Customer Service: Multi-Person Tracking
```python
result = await prompt_service.execute_prompt(
    trace_id=trace_id,
    prompt="Alice (alice@co.com) called about Bob's (bob@co.com) order",
    is_secure=True,
    privacy_config=PresidioConfig(
        enabled=True,
        multi_person_support=True,
        entities_to_detect=["PERSON", "EMAIL"]
    )
)

# LLM receives:
# "<PERSON_1> (<EMAIL_1>) called about <PERSON_2>'s (<EMAIL_2>) order"
```

---

## 12. Value Proposition

### For Clients
- **Compliance-Ready** - GDPR, HIPAA, CCPA out-of-the-box
- **Risk Reduction** - No PII sent to third-party LLMs
- **Audit Trail** - Complete traceability with de-anonymization
- **Flexibility** - Configurable per organization/project
- **Multi-Modal** - Protects text, images, documents

### For PromptForge
- **Differentiation** - Enterprise-grade privacy features
- **Enterprise Sales** - Unlocks regulated industries (healthcare, finance)
- **Compliance** - Meets stringent data protection requirements
- **Trust** - Demonstrates security-first approach
- **Competitive Edge** - Few LLM platforms offer privacy-by-design

---

## 13. Security Considerations

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| PII leakage to LLM | Pre-LLM anonymization |
| Trace log breaches | Encrypted mapping storage |
| Unauthorized de-anonymization | RBAC with pii:read permission |
| Cross-tenant access | Organization scoping enforced |
| Insider threats | Comprehensive audit logging |
| Compliance violations | Pre-configured compliance profiles |

### Security Best Practices
1. **Encryption Keys** - Rotate every 90 days
2. **Access Logs** - Retain for 2 years (compliance)
3. **Mapping TTL** - Auto-delete after configurable period
4. **Least Privilege** - pii:read permission granted sparingly
5. **Regular Audits** - Quarterly security reviews

---

## 14. Dependencies

### Python Libraries
```txt
# requirements.txt additions
presidio-analyzer>=2.2.0
presidio-anonymizer>=2.2.0
presidio-image-redactor>=0.0.13
spacy>=3.5.0
en-core-web-lg>=3.5.0  # Spacy model for NER
cryptography>=41.0.0
Faker>=18.0.0  # For fake data generation
```

### Installation
```bash
# Install Presidio
pip install presidio-analyzer presidio-anonymizer presidio-image-redactor

# Download Spacy model
python -m spacy download en_core_web_lg

# Install Tesseract (for image OCR)
# macOS:
brew install tesseract

# Ubuntu:
apt-get install tesseract-ocr
```

---

## 15. Next Steps

**Immediate (Week 1-2):**
1. Install Presidio and dependencies
2. Create PresidioDecorator prototype
3. Test basic anonymization flow

**Short-term (Week 3-6):**
4. Integrate with trace execution API
5. Add database schema for privacy configs
6. Implement multi-person support

**Medium-term (Week 7-10):**
7. Build compliance profiles
8. Create privacy management APIs
9. Comprehensive testing and validation

**Phase 4 Preparation:**
- Scale privacy to batch processing
- Add privacy analytics dashboard
- Implement privacy policy automation
- Privacy-preserving evaluation techniques

---

## 16. Monitoring & Observability

### Privacy Metrics
```python
class PrivacyMetrics:
    """Track privacy operations"""

    # Counters
    pii_detections_total = Counter("presidio_pii_detections_total", ["entity_type"])
    anonymizations_total = Counter("presidio_anonymizations_total", ["method"])
    deanonymizations_total = Counter("presidio_deanonymizations_total", ["user_role"])

    # Histograms
    anonymization_duration_ms = Histogram("presidio_anonymization_duration_ms")
    pii_entities_per_trace = Histogram("presidio_pii_entities_per_trace")

    # Gauges
    active_privacy_configs = Gauge("presidio_active_privacy_configs")
    traces_with_privacy_enabled = Gauge("presidio_traces_with_privacy_enabled")
```

### Audit Events
```python
# Log all privacy-sensitive operations
audit_events = [
    "privacy:config_created",
    "privacy:config_updated",
    "privacy:pii_detected",
    "privacy:anonymized",
    "privacy:deanonymized",
    "privacy:unauthorized_access_attempt",
]
```

---

**Document Version:** 1.0
**Created:** October 5, 2025
**Status:** Planning & Design
**Implementation Target:** Q1 2026
