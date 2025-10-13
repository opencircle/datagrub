# PromptForge Build Specifications

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Organization**: Phase-based with domain grouping

---

## Directory Structure

```
specs/
├── 00_meta/                  # Meta specifications and configuration
├── 01_phase1_foundation/     # Core UI foundation
├── 02_phase2_core_features/  # Main feature implementations
│   ├── apis/                 # API architecture and requirements
│   ├── evaluation/           # Evaluation framework and dashboards
│   ├── insights/             # Deep insights and DTA pipeline
│   ├── models/               # Model provider management
│   ├── traces/               # Trace monitoring and visualization
│   └── ui/                   # UI framework standards
├── 03_phase3_advanced/       # Advanced features
└── 04_phase4_enterprise/     # Enterprise capabilities
```

---

## Specification Index

### 00_meta: Meta Specifications

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Competitor_Analysis.md** | Market analysis and competitive positioning | 15 KB | ✅ Complete |
| **MODEL_PROVIDER_CONFIGURATION_SPEC.md** | Model provider configuration standards | 19 KB | ✅ Complete |

**Purpose**: Cross-cutting specifications that inform design decisions across all phases.

---

### 01_phase1_foundation: Foundation

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase1_CoreUI.md** | Core UI component architecture | 607 bytes | ⚠️ Stub |

**Purpose**: Establishes fundamental UI patterns and component structure.

**Key Topics**:
- Micro-frontend architecture
- Component library
- State management foundation
- Design system basics

---

### 02_phase2_core_features: Core Features

#### APIs Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_APIs.md** | General API architecture | 406 bytes | ⚠️ Stub |
| **Phase2_API_SecurityRequirements.md** | SOC 2 compliance and security | 19 KB | ✅ Complete |
| **Phase2_API_PerformanceRequirements.md** | Performance optimization standards | 23 KB | ✅ Complete |

**Key Topics**:
- FastAPI architecture
- RESTful design patterns
- Authentication & authorization
- Rate limiting and caching
- Security best practices (OWASP Top 10)
- Performance budgets and optimization

---

#### Evaluation Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_Evaluation_Framework.md** | Evaluation abstraction layer | 99 KB | ✅ Complete |
| **Phase2_Evaluation_Dashboard.md** | Evaluation results dashboard | 56 KB | ✅ Complete |
| **Phase2_Evaluation_Playground.md** | Interactive evaluation playground | 26 KB | ✅ Complete |

**Key Topics**:
- Adapter pattern for evaluation frameworks (Ragas, DeepEval, MLflow, Deepchecks, Arize Phoenix)
- Metric aggregation and visualization
- Result filtering and comparison
- Interactive testing interface

---

#### Insights Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_Summarization_Insights_API_DTA.md** | Deep Insights DTA API specification | 21 KB | ✅ Complete |
| **Phase2_Insights_History.md** | Deep Insights implementation guide | 12 KB | ✅ Complete |
| **Phase2_Insight_Comparator.md** | Model comparison feature | 48 KB | ✅ Complete |

**Key Topics**:
- DTA (Document-Template-Analysis) pipeline
- Multi-pass reasoning architecture
- Insight storage and retrieval
- History tracking and pagination
- Side-by-side model comparison

---

#### Models Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_Model_Dashboard.md** | Model provider management UI | 20 KB | ✅ Complete |

**Key Topics**:
- Model provider CRUD operations
- Capability filtering
- Parameter compatibility matrix
- Cost-aware model selection

---

#### Traces Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_Trace_Dashboard.md** | Trace monitoring and visualization | 34 KB | ✅ Complete |

**Key Topics**:
- Parent-child trace relationships
- DTA pipeline trace hierarchy
- Real-time trace monitoring
- Trace search and filtering

---

#### UI Domain

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase2_UI_Framework.md** | UI/UX standards and patterns | 38 KB | ✅ Complete |

**Key Topics**:
- Claude.ai-inspired design system
- Routing and navigation patterns
- State management (React Query)
- Module Federation architecture
- Accessibility (WCAG AAA)
- Performance optimization

---

### 03_phase3_advanced: Advanced Features

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase3_Privacy_Framework.md** | GDPR compliance and data privacy | 29 KB | ✅ Complete |
| **Phase3_SaaSRefinement.md** | Multi-tenancy and SaaS features | 379 bytes | ⚠️ Stub |

**Key Topics**:
- Data encryption at rest and in transit
- User consent management
- Data retention policies
- Multi-tenant architecture
- Billing and subscription management

---

### 04_phase4_enterprise: Enterprise Capabilities

| File | Description | Size | Status |
|------|-------------|------|--------|
| **Phase4_EnterpriseEnablement.md** | Enterprise features and SSO | 376 bytes | ⚠️ Stub |

**Key Topics**:
- SSO integration (SAML, OIDC)
- Role-based access control (RBAC)
- Audit logging
- SLA guarantees
- On-premise deployment

---

## Agent Dependency Matrix

### Which agents use which specs?

| Agent | Primary Specs | Secondary Specs |
|-------|---------------|-----------------|
| **UI Architect** | `01_phase1_foundation/Phase1_CoreUI.md`<br>`02_phase2_core_features/ui/Phase2_UI_Framework.md` | `02_phase2_core_features/insights/Phase2_Insights_History.md`<br>`02_phase2_core_features/evaluation/Phase2_Evaluation_Dashboard.md` |
| **API Architect** | `02_phase2_core_features/apis/Phase2_APIs.md`<br>`02_phase2_core_features/apis/Phase2_API_SecurityRequirements.md` | `02_phase2_core_features/apis/Phase2_API_PerformanceRequirements.md`<br>`02_phase2_core_features/insights/Phase2_Summarization_Insights_API_DTA.md`<br>`02_phase2_core_features/evaluation/Phase2_Evaluation_Framework.md` |
| **DB Architect** | `02_phase2_core_features/apis/Phase2_APIs.md` | All domain specs for schema requirements |
| **UX Specialist** | `02_phase2_core_features/ui/Phase2_UI_Framework.md` | All feature specs for UX requirements |
| **Checker Agent** | **ALL SPECS** | - |
| **API QA** | `02_phase2_core_features/apis/Phase2_APIs.md`<br>`02_phase2_core_features/apis/Phase2_API_SecurityRequirements.md` | All API-related specs |
| **UI QA** | `01_phase1_foundation/Phase1_CoreUI.md`<br>`02_phase2_core_features/ui/Phase2_UI_Framework.md` | All UI-related specs |

---

## Phase Progression Guide

### Phase 1: Foundation (Complete)
**Goal**: Establish core UI architecture and component library

**Deliverables**:
- ✅ Micro-frontend shell application
- ✅ Shared component library
- ✅ Basic state management
- ✅ Design system foundation

---

### Phase 2: Core Features (In Progress)
**Goal**: Implement main feature set for LLM application evaluation

**Deliverables**:
- ✅ API architecture with FastAPI
- ✅ Evaluation framework with adapter pattern
- ✅ Deep Insights (DTA pipeline) - **100% Complete**
- ✅ Insight Comparator - **100% Complete**
- ✅ Model Dashboard
- ✅ Trace visualization
- ✅ Comprehensive UI framework
- 🔄 Complete stub specifications (Phase2_APIs.md, Phase1_CoreUI.md)

**Current Focus**: Implementing Insight Comparator feature

---

### Phase 3: Advanced Features (Planned)
**Goal**: Add privacy, compliance, and SaaS capabilities

**Deliverables**:
- ⏳ GDPR compliance framework
- ⏳ Multi-tenancy architecture
- ⏳ Billing and subscription management
- ⏳ Advanced analytics

---

### Phase 4: Enterprise (Planned)
**Goal**: Enable enterprise deployment and management

**Deliverables**:
- ⏳ SSO integration
- ⏳ RBAC and advanced permissions
- ⏳ Audit logging
- ⏳ On-premise deployment support

---

## Domain Grouping Rationale

### APIs Domain
All API-related specifications including architecture, security, and performance requirements.

**Why grouped**: Backend implementation consistency, security policy enforcement.

### Evaluation Domain
Evaluation framework, dashboards, and interactive playground.

**Why grouped**: Core product feature, tightly integrated components.

### Insights Domain
Deep insights DTA pipeline, history tracking, and model comparison.

**Why grouped**: Multi-pass reasoning system with shared data models.

### Models Domain
Model provider management and configuration.

**Why grouped**: Standalone domain with CRUD operations.

### Traces Domain
Trace monitoring, visualization, and hierarchical relationships.

**Why grouped**: Observability feature with unique data structures.

### UI Domain
UI framework standards, design system, and architectural patterns.

**Why grouped**: Cross-cutting UI concerns affecting all features.

---

## Searching for Specifications

### By Feature
- **Evaluation**: `02_phase2_core_features/evaluation/`
- **Deep Insights**: `02_phase2_core_features/insights/`
- **Model Management**: `02_phase2_core_features/models/`
- **Tracing**: `02_phase2_core_features/traces/`

### By Concern
- **Security**: `02_phase2_core_features/apis/Phase2_API_SecurityRequirements.md`
- **Performance**: `02_phase2_core_features/apis/Phase2_API_PerformanceRequirements.md`
- **UI/UX**: `02_phase2_core_features/ui/Phase2_UI_Framework.md`
- **Privacy**: `03_phase3_advanced/Phase3_Privacy_Framework.md`

### By Phase
- **Phase 1**: `01_phase1_foundation/`
- **Phase 2**: `02_phase2_core_features/`
- **Phase 3**: `03_phase3_advanced/`
- **Phase 4**: `04_phase4_enterprise/`

---

## Version History

### 2.0.0 (2025-10-11)
- Reorganized into phase-based structure with domain grouping
- Added comprehensive README with index
- Created agent dependency matrix
- Documented phase progression

### 1.0.0 (2025-10-05)
- Initial flat directory structure
- Core Phase 2 specifications complete

---

## Contributing

When adding new specifications:

1. **Choose appropriate directory** based on phase and domain
2. **Follow naming convention**: `PhaseN_FeatureName.md`
3. **Add entry to this README** under appropriate section
4. **Update agent dependency matrix** if new dependencies created
5. **Include version header** in specification file

---

**Maintained by**: PromptForge Team
**Location**: `/Users/rohitiyer/datagrub/promptforge/.claude/specs/`
