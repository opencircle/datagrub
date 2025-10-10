# API Security Requirements - SOC 2 Compliance

**Document Version:** 1.0
**Last Updated:** 2025-10-05
**Compliance Target:** SOC 2 Type II
**Classification:** Internal - Security Architecture

---

## Executive Summary

PromptForge is designed as a multi-tenant SaaS platform capable of supporting enterprise workloads for financial services and other highly regulated industries. This document outlines the security requirements and architecture to achieve SOC 2 Type II compliance.

### Key Security Principles

1. **Zero Trust Architecture** - Never trust, always verify
2. **Defense in Depth** - Multiple layers of security controls
3. **Least Privilege Access** - Minimal permissions by default
4. **Stateless Authentication** - JWT-based claims for scalability
5. **Organization Isolation** - Strict multi-tenant data segregation
6. **Audit Everything** - Comprehensive logging of all sensitive operations

---

## 1. Authentication & Authorization

### 1.1 JWT Token Structure

All API requests MUST include a valid JWT token in the `Authorization: Bearer` header.

**JWT Claims (Required):**
```json
{
  "sub": "user_id (UUID)",
  "exp": "expiration timestamp",
  "type": "access|refresh",
  "organization_id": "org_id (UUID)",
  "role": "ADMIN|DEVELOPER|VIEWER",
  "email": "user@example.com"
}
```

**Security Requirements:**
- ✅ Tokens MUST expire within 30 days (access tokens)
- ✅ Refresh tokens MUST expire within 90 days
- ✅ Tokens MUST be signed with HS256 or RS256
- ✅ Token signing keys MUST be rotated every 90 days
- ✅ Revoked tokens MUST be stored in blacklist/Redis cache
- ✅ All tokens MUST include organization_id for multi-tenant isolation

### 1.2 Stateless Session Management

**Requirements:**
- ✅ NO server-side session storage
- ✅ ALL user context from JWT claims only
- ✅ Organization ID MUST be validated on EVERY API call
- ✅ User permissions MUST be re-validated for sensitive operations
- ✅ Token refresh MUST require valid refresh token

### 1.3 Password Security

**Requirements:**
- ✅ bcrypt with cost factor ≥ 12
- ✅ Minimum password length: 12 characters
- ✅ Password complexity requirements enforced
- ✅ Password history: last 5 passwords cannot be reused
- ✅ Failed login attempts: lock account after 5 failures
- ✅ Account lockout duration: 15 minutes (exponential backoff)
- ✅ MFA required for ADMIN role users

---

## 2. Multi-Tenant Data Isolation

### 2.1 Organization-Scoped Data Access

**CRITICAL: ALL database queries MUST filter by organization_id**

**Requirements:**
- ✅ Organization ID extracted from JWT token claims
- ✅ ALL SELECT queries MUST include `WHERE organization_id = ?`
- ✅ ALL INSERT queries MUST set `organization_id` from JWT claims
- ✅ ALL UPDATE/DELETE queries MUST filter by organization_id
- ✅ Cross-organization data access MUST be logged and audited
- ✅ Database row-level security (RLS) policies enforced

**Example Query Pattern:**
```python
# ❌ INCORRECT - No organization filter
query = select(ModelProviderConfig).where(
    ModelProviderConfig.id == config_id
)

# ✅ CORRECT - Organization filter from JWT claims
query = select(ModelProviderConfig).where(
    ModelProviderConfig.id == config_id,
    ModelProviderConfig.organization_id == current_user.organization_id
)
```

### 2.2 Project-Level Isolation

**Requirements:**
- ✅ Projects MUST belong to an organization
- ✅ Users can only access projects within their organization
- ✅ Project-scoped resources MUST validate both org_id and project_id
- ✅ Cascade delete on organization removal
- ✅ Orphaned resources MUST be prevented via foreign key constraints

### 2.3 Data Encryption

**At Rest:**
- ✅ Database encryption: AES-256 (PostgreSQL transparent data encryption)
- ✅ Sensitive fields encrypted: Fernet (AES-128 CBC + HMAC)
- ✅ Encryption keys stored in: AWS KMS / HashiCorp Vault
- ✅ Key rotation: Every 90 days
- ✅ Encrypted fields: API keys, credentials, secrets, PII

**In Transit:**
- ✅ TLS 1.3 minimum for all API endpoints
- ✅ TLS 1.2 acceptable with strong cipher suites only
- ✅ Certificate pinning for mobile/desktop clients
- ✅ HSTS headers enforced (Strict-Transport-Security)

**Encryption Implementation:**
```python
# Model Provider API Keys
class ModelProviderConfig(Base):
    api_key_encrypted = Column(Text, nullable=False)  # Fernet encrypted
    api_key_hash = Column(String(128), nullable=False)  # SHA-256 hash
    config_encrypted = Column(Text)  # Fernet encrypted JSONB
```

---

## 3. API Security Controls

### 3.1 Input Validation

**Requirements:**
- ✅ Pydantic schemas for ALL request/response validation
- ✅ SQL injection prevention via parameterized queries (SQLAlchemy ORM)
- ✅ XSS prevention via output encoding
- ✅ CSRF protection for state-changing operations
- ✅ File upload validation: type, size, content scanning
- ✅ Rate limiting per user/organization/IP

### 3.2 Rate Limiting

**Requirements:**
- ✅ Per User: 1000 requests/hour
- ✅ Per Organization: 10,000 requests/hour
- ✅ Per IP: 100 requests/minute
- ✅ Auth endpoints: 10 login attempts/15 minutes
- ✅ Sensitive operations: 10 requests/minute
- ✅ Rate limit headers in responses (X-RateLimit-*)

**Implementation:**
```python
from fastapi import Request
from slowapi import Limiter

limiter = Limiter(key_func=get_organization_id)

@router.post("/model-providers/configs")
@limiter.limit("10/minute")  # Sensitive operation
async def create_provider_config(request: Request, ...):
    pass
```

### 3.3 API Key Management

**Requirements:**
- ✅ API keys NEVER stored in plaintext
- ✅ API keys NEVER returned in API responses (always masked)
- ✅ API key rotation capability
- ✅ API key usage tracking (last_used_at, usage_count)
- ✅ Automatic alerts on unusual API key usage patterns
- ✅ API key expiration enforcement

**Masking Pattern:**
```json
{
  "api_key_masked": "sk-proj-...xyz",  // First 8 + last 3 chars
  "api_key_hash": "sha256_hash",       // For validation
  "last_rotated_at": "2025-10-05"
}
```

---

## 4. Audit Logging & Monitoring

### 4.1 Audit Log Requirements

**ALL sensitive operations MUST be logged:**

**Categories:**
1. **Authentication Events**
   - Login attempts (success/failure)
   - Logout events
   - Token refresh
   - Password changes
   - MFA enrollment/verification

2. **Authorization Events**
   - Role changes
   - Permission modifications
   - Organization changes
   - Access denials

3. **Data Access Events**
   - Sensitive data reads (API keys, credentials)
   - Data exports
   - Bulk data operations
   - Cross-organization access attempts

4. **Configuration Changes**
   - API key creation/rotation/deletion
   - Provider configuration changes
   - Policy modifications
   - User/organization management

5. **Security Events**
   - Failed authorization attempts
   - Rate limit violations
   - Suspicious activity patterns
   - Encryption key rotations

**Audit Log Schema:**
```json
{
  "timestamp": "2025-10-05T18:30:00Z",
  "event_id": "uuid",
  "event_type": "API_KEY_CREATED",
  "severity": "INFO|WARN|ERROR|CRITICAL",
  "actor": {
    "user_id": "uuid",
    "organization_id": "uuid",
    "email": "user@example.com",
    "role": "ADMIN",
    "ip_address": "1.2.3.4",
    "user_agent": "Mozilla/5.0..."
  },
  "resource": {
    "type": "model_provider_config",
    "id": "uuid",
    "organization_id": "uuid"
  },
  "action": "CREATE|READ|UPDATE|DELETE",
  "result": "SUCCESS|FAILURE",
  "metadata": {
    "provider_name": "openai",
    "changes": {...}
  },
  "request_id": "uuid"
}
```

### 4.2 Log Retention

**Requirements:**
- ✅ Audit logs: 7 years retention
- ✅ Application logs: 90 days retention
- ✅ Security logs: 1 year retention
- ✅ Access logs: 90 days retention
- ✅ Logs MUST be immutable (append-only)
- ✅ Logs MUST be encrypted at rest
- ✅ Log aggregation: CloudWatch / Datadog / Splunk

### 4.3 Monitoring & Alerting

**Requirements:**
- ✅ Real-time alerts for security events
- ✅ Anomaly detection for unusual patterns
- ✅ Performance monitoring (latency, errors)
- ✅ Uptime monitoring (99.9% SLA target)
- ✅ Security dashboard for SOC team
- ✅ Automated incident response workflows

**Alert Triggers:**
- Multiple failed login attempts (>5 in 15 min)
- API key rotation >10 times/day
- Cross-organization access attempts
- Unusual data export volumes
- Rate limit violations
- Encryption failures
- Database query anomalies

---

## 5. Role-Based Access Control (RBAC)

### 5.1 User Roles

**Standard Roles:**

| Role | Permissions |
|------|-------------|
| **VIEWER** | Read-only access to projects, prompts, evaluations |
| **DEVELOPER** | VIEWER + Create/update prompts, run evaluations, view traces |
| **ADMIN** | DEVELOPER + Manage users, API keys, billing, organization settings |
| **SUPER_ADMIN** | System-wide access (PromptForge operators only) |

### 5.2 Permission Matrix

| Resource | VIEWER | DEVELOPER | ADMIN |
|----------|--------|-----------|-------|
| View Projects | ✅ | ✅ | ✅ |
| Create/Edit Projects | ❌ | ✅ | ✅ |
| Delete Projects | ❌ | ❌ | ✅ |
| View API Keys | ❌ | ❌ | ✅ |
| Create/Rotate API Keys | ❌ | ❌ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| View Audit Logs | ❌ | ❌ | ✅ |
| Billing & Subscriptions | ❌ | ❌ | ✅ |

### 5.3 Enforcement

**Requirements:**
- ✅ Role checked on EVERY API endpoint
- ✅ Permission decorators/dependencies
- ✅ Database-level constraints where possible
- ✅ Fail-safe defaults (deny by default)
- ✅ Role changes logged and audited

**Implementation:**
```python
from app.api.dependencies import require_role, get_current_user

@router.post("/model-providers/configs")
async def create_provider_config(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    ...
):
    # Only ADMIN users can create provider configs
    pass
```

---

## 6. Sensitive Data Handling

### 6.1 Data Classification

| Level | Examples | Encryption | Access Control |
|-------|----------|------------|----------------|
| **Public** | Product docs, marketing | None | Public |
| **Internal** | App configs, schemas | TLS | Authenticated users |
| **Confidential** | User data, prompts, traces | At rest + transit | Org members |
| **Restricted** | API keys, passwords, PII | Fernet + TLS | ADMIN only |

### 6.2 PII Handling

**Requirements:**
- ✅ PII fields identified and documented
- ✅ PII encrypted at rest (Fernet)
- ✅ PII access logged in audit trail
- ✅ PII export requires explicit consent
- ✅ Right to deletion (GDPR compliance)
- ✅ Data minimization (collect only what's needed)

**PII Fields:**
- Email addresses
- Full names
- IP addresses (in audit logs)
- Phone numbers (if collected)
- Payment information

### 6.3 Secure Deletion

**Requirements:**
- ✅ Soft delete with retention period (30 days)
- ✅ Hard delete after retention period
- ✅ Cascade delete of dependent resources
- ✅ Deletion audited and logged
- ✅ Encryption keys destroyed on hard delete
- ✅ Backup purging process

---

## 7. Infrastructure Security

### 7.1 Network Security

**Requirements:**
- ✅ VPC isolation for database tier
- ✅ Private subnets for sensitive services
- ✅ Security groups: least privilege rules
- ✅ WAF (Web Application Firewall) for API endpoints
- ✅ DDoS protection (AWS Shield / CloudFlare)
- ✅ No public database access (use bastion/VPN)

### 7.2 Container Security

**Requirements:**
- ✅ Base images: official, minimal (Alpine/Distroless)
- ✅ Image scanning: Trivy/Snyk/Aqua
- ✅ No secrets in images (use env vars/secrets manager)
- ✅ Non-root user in containers
- ✅ Read-only root filesystem where possible
- ✅ Resource limits enforced (CPU, memory)

### 7.3 Secrets Management

**Requirements:**
- ✅ AWS Secrets Manager / HashiCorp Vault
- ✅ Secrets NEVER in code/config files
- ✅ Secrets NEVER in environment variables (use secrets manager)
- ✅ Automatic rotation every 90 days
- ✅ Least privilege access to secrets
- ✅ Audit logging for secret access

---

## 8. Compliance & Certifications

### 8.1 SOC 2 Type II Requirements

**Trust Service Criteria:**

1. **Security (CC)**
   - ✅ Access controls implemented
   - ✅ Encryption at rest and in transit
   - ✅ Network security controls
   - ✅ Vulnerability management

2. **Availability (A)**
   - ✅ 99.9% uptime SLA
   - ✅ Disaster recovery plan
   - ✅ Backup and restore procedures
   - ✅ Incident response plan

3. **Processing Integrity (PI)**
   - ✅ Data validation controls
   - ✅ Error handling and logging
   - ✅ Transaction integrity
   - ✅ Audit trails

4. **Confidentiality (C)**
   - ✅ Encryption controls
   - ✅ Access restrictions
   - ✅ Data classification
   - ✅ Secure disposal

5. **Privacy (P)**
   - ✅ GDPR compliance
   - ✅ CCPA compliance
   - ✅ Data subject rights
   - ✅ Privacy notices

### 8.2 Additional Compliance

**Financial Services:**
- ✅ PCI-DSS (if handling payment data)
- ✅ GLBA (Gramm-Leach-Bliley Act)
- ✅ FINRA recordkeeping requirements
- ✅ SOX compliance for public companies

**Healthcare:**
- ✅ HIPAA compliance (if handling PHI)
- ✅ HITECH Act requirements

---

## 9. Incident Response

### 9.1 Security Incident Categories

**Severity Levels:**
- **P1 (Critical)**: Data breach, encryption failure, complete service outage
- **P2 (High)**: Unauthorized access, API key compromise, partial outage
- **P3 (Medium)**: Failed login attacks, rate limit violations
- **P4 (Low)**: Policy violations, configuration issues

### 9.2 Response Procedures

**P1 Incidents:**
1. Immediate notification to security team (< 15 min)
2. Isolate affected systems
3. Assess scope and impact
4. Contain and remediate
5. Customer notification (< 24 hours)
6. Regulatory notification (if required)
7. Post-mortem and prevention

**Requirements:**
- ✅ 24/7 on-call security team
- ✅ Incident response playbooks
- ✅ Regular incident drills (quarterly)
- ✅ Incident communication templates
- ✅ Post-incident reviews (blameless)

---

## 10. Development Security

### 10.1 Secure SDLC

**Requirements:**
- ✅ Security requirements in all stories
- ✅ Threat modeling for new features
- ✅ Code review mandatory (2 reviewers)
- ✅ Static analysis (SAST): SonarQube/Snyk
- ✅ Dynamic analysis (DAST): OWASP ZAP
- ✅ Dependency scanning: Dependabot/Snyk
- ✅ Pre-commit hooks for secrets scanning

### 10.2 Third-Party Dependencies

**Requirements:**
- ✅ Dependency approval process
- ✅ License compliance checking
- ✅ Vulnerability scanning
- ✅ Regular updates (monthly)
- ✅ Security advisories monitoring
- ✅ Bill of materials (SBOM) generated

---

## 11. API Security Checklist

### Pre-Deployment Checklist

- [ ] All endpoints require JWT authentication
- [ ] Organization ID validated on ALL data access
- [ ] Input validation with Pydantic schemas
- [ ] SQL injection prevention (ORM only)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection enabled
- [ ] Rate limiting implemented
- [ ] Audit logging for sensitive operations
- [ ] Error messages don't leak sensitive info
- [ ] TLS 1.3 enforced
- [ ] CORS configured properly
- [ ] Security headers set (CSP, X-Frame-Options, etc.)
- [ ] Secrets in Secrets Manager (not env vars)
- [ ] Encryption keys rotated
- [ ] Database RLS policies enabled
- [ ] API documentation reviewed
- [ ] Penetration testing completed
- [ ] SOC 2 controls validated

---

## 12. Implementation Guidelines

### 12.1 JWT Token Enhancement

**Current Implementation:**
```python
# app/core/security.py
def create_access_token(subject: str) -> str:
    payload = {
        "exp": datetime.utcnow() + timedelta(days=30),
        "sub": subject,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

**Required Enhancement:**
```python
# app/core/security.py
def create_access_token(user: User) -> str:
    payload = {
        "exp": datetime.utcnow() + timedelta(days=30),
        "sub": str(user.id),
        "type": "access",
        "organization_id": str(user.organization_id),  # REQUIRED
        "role": user.role.value,  # REQUIRED
        "email": user.email  # For audit logging
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

### 12.2 Organization-Scoped Dependencies

```python
# app/api/dependencies.py
async def get_current_user_with_org(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user and validate organization from JWT claims
    """
    token = credentials.credentials
    payload = decode_token(token)

    # Validate required claims
    user_id = payload.get("sub")
    org_id = payload.get("organization_id")  # MUST be present

    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing organization_id"
        )

    # Fetch user and validate organization match
    user = await db.get(User, UUID(user_id))
    if str(user.organization_id) != org_id:
        # Security violation: token org doesn't match user org
        await audit_log(
            event_type="ORGANIZATION_MISMATCH",
            user_id=user_id,
            severity="CRITICAL"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization mismatch detected"
        )

    return user
```

### 12.3 Audit Logging Implementation

```python
# app/services/audit.py
async def audit_log(
    event_type: str,
    user: User,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    action: Optional[str] = None,
    result: str = "SUCCESS",
    metadata: Optional[Dict] = None,
    request: Optional[Request] = None
):
    """Log security audit event"""
    log_entry = AuditLog(
        event_type=event_type,
        user_id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        role=user.role,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        result=result,
        metadata=metadata,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    # Store in database + send to logging service
    await db.add(log_entry)
    logger.info(f"AUDIT: {event_type}", extra=log_entry.dict())
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-05 | Security Team | Initial release |

---

## Approval

**Document Owner:** Chief Information Security Officer (CISO)
**Review Frequency:** Quarterly
**Next Review Date:** 2026-01-05

**Approvals Required:**
- [ ] CISO
- [ ] CTO
- [ ] VP Engineering
- [ ] Compliance Officer
- [ ] Legal Counsel
