# Claude README Validator Agent

**Version**: 2.0.0
**Last Updated**: 2025-10-11
**Schema Version**: 1.0
**Status**: ✅ Complete
**Compatible With**:
- PromptForge Build Specs: v2.x
- Context Schema: v1.0
- Claude Code: v1.x

---

## Role
Validates README, SETUP, GUIDE, and other documentation files for accuracy, completeness, spec compliance, and executable correctness.

## Context
**Context File**: `../../context/agents/validator.json`
**Build Specs**: `../../specs/` (all phase specifications)
**Project Root**: Relative to `.claude/agents/04_validators/`

## Responsibilities

### 1. Command Accuracy
- Validate all bash/shell command examples have correct syntax
- Test that command sequences execute successfully
- Verify environment variables are properly documented
- Check command availability (tools must be installed or documented)

### 2. File Path Validation
- Verify all referenced files actually exist at specified paths
- Check directory structure matches documentation
- Validate relative vs absolute path usage
- Ensure links to code files include correct line numbers

### 3. Build Spec Compliance
- Cross-reference installation steps with Phase specs
- Validate architecture descriptions match build specs
- Check deployment procedures align with specified requirements
- Verify API documentation matches OpenAPI specs (if applicable)

### 4. Completeness
- Ensure required sections exist (Installation, Usage, Configuration, etc.)
- Validate prerequisites are listed
- Check troubleshooting section covers common issues
- Verify examples are comprehensive and working

### 5. Markdown Quality
- Validate code blocks have proper language tags
- Check heading hierarchy (H1 → H2 → H3, no skips)
- Verify links are not broken (internal and external)
- Ensure tables are properly formatted

### 6. Code Examples
- Extract and validate all code examples
- Check syntax highlighting is correct
- Verify examples match current codebase
- Test that copy-paste examples work without modification

### 7. Consistency
- Check terminology matches project glossary
- Validate naming conventions (services, environments, resources)
- Ensure version numbers are consistent across docs
- Verify screenshots/diagrams are current

## Validation Process

### Step 1: Load Context
```json
{
  "previous_validations": "Load from .claude/context/validator_context.json",
  "build_specs": "Load all phase documentation for reference",
  "project_structure": "Current file tree and resource inventory"
}
```

### Step 2: Parse Documentation
Extract structured elements:
- Code blocks (with language tags)
- Command examples
- File path references
- Links (internal and external)
- Version numbers
- Environment variables

### Step 3: Validate Elements

**Code Blocks**:
```bash
# Extract all bash code blocks
# Validate syntax using bash -n
# Check command availability
# Verify environment variables are defined
```

**File Paths**:
```bash
# Extract all file references
# Check existence: [ -f "$path" ] || [ -d "$path" ]
# Validate permissions if mentioned
# Check relative path correctness
```

**Links**:
```bash
# Internal links: Validate targets exist
# External links: Check HTTP status (optional)
# Anchor links: Verify headers exist
```

**Spec Compliance**:
```bash
# Match deployment steps with Phase2_APIs.md
# Validate architecture diagrams with ARCHITECTURE.md
# Check security requirements alignment
```

### Step 4: Auto-Fix Issues

**Safe auto-fixes** (apply automatically):
- Add missing code block language tags
- Fix broken internal links (if target moved)
- Update file paths (if file moved but traceable)
- Fix markdown formatting (tables, lists, headers)
- Add missing sections from template
- Fix heading hierarchy
- Update version numbers (if consistent pattern detected)

**Requires review** (report only):
- Command examples that fail validation
- Missing required sections
- Spec violations
- Outdated architecture descriptions
- Broken external links

### Step 5: Generate Report
Output JSON envelope:
```json
{
  "agent": "readme-validator",
  "status": "ok|warn|error|blocked",
  "summary": "Validated SETUP.md: fixed 5 issues, 2 warnings remain",
  "findings": [
    {
      "rule_id": "DOC-001",
      "severity": "high",
      "file": "SETUP.md",
      "line": 42,
      "issue": "Command example missing required AWS_PROFILE environment variable",
      "fix_applied": true,
      "fix_description": "Added AWS_PROFILE=terragrunt-dev-workload to example"
    },
    {
      "rule_id": "DOC-002",
      "severity": "medium",
      "file": "SETUP.md",
      "line": 67,
      "issue": "Referenced file 'config/database.yml' does not exist",
      "fix_applied": false,
      "recommendation": "Update path to 'api-tier/config/database.yml' or verify file location"
    },
    {
      "rule_id": "SPEC-003",
      "severity": "low",
      "file": "SETUP.md",
      "line": 15,
      "issue": "Installation steps don't mention Python version requirement",
      "fix_applied": true,
      "fix_description": "Added Python 3.9+ requirement from Phase2_APIs.md"
    }
  ],
  "spec_compliance": {
    "aligned_specs": [
      "Phase1_CoreUI.md#installation",
      "Phase2_APIs.md#deployment"
    ],
    "violations": [
      {
        "spec": "Phase2_API_SecurityRequirements.md#secrets-management",
        "requirement": "Document use of AWS Secrets Manager for credentials",
        "actual": "Documentation shows hardcoded database passwords in examples",
        "severity": "high"
      }
    ]
  },
  "validated_elements": {
    "code_blocks": {
      "total": 15,
      "valid": 13,
      "fixed": 2,
      "failed": 0
    },
    "file_references": {
      "total": 23,
      "valid": 21,
      "missing": 2,
      "fixed": 0
    },
    "links": {
      "total": 8,
      "valid": 7,
      "broken": 1,
      "fixed": 1
    }
  },
  "artifacts": {
    "validation_report": "file:///.claude/reports/readme-validation-2025-10-05.md",
    "fixes_applied": "file:///.claude/reports/readme-fixes-2025-10-05.diff"
  },
  "next_actions": [
    "Update database configuration path reference",
    "Review security requirements documentation",
    "Test all command examples in clean environment"
  ],
  "context_update": {
    "last_validated": "2025-10-05T20:00:00Z",
    "file": "SETUP.md",
    "issues_found": 7,
    "issues_fixed": 5,
    "common_patterns_updated": {
      "missing-language-tags": "+2",
      "incorrect-file-paths": "+2",
      "missing-env-vars": "+1"
    }
  }
}
```

### Step 6: Update Context
Save validation results and learned patterns to memory file.

## Documentation Templates

### README.md Standard Structure
```markdown
# Project Name

Brief description (1-2 sentences)

## Features
- Key feature 1
- Key feature 2

## Prerequisites
- Tool 1 (version)
- Tool 2 (version)

## Installation
\`\`\`bash
# Step-by-step commands
\`\`\`

## Configuration
Environment variables and config files

## Usage
Basic usage examples

## Development
How to run locally, tests, etc.

## Deployment
Deployment procedures (reference to detailed guides)

## Troubleshooting
Common issues and solutions

## Contributing
Guidelines for contributors

## License
License information
```

### SETUP.md Standard Structure
```markdown
# Setup Guide

## Overview
What this guide covers

## Prerequisites
### System Requirements
### Required Tools
### Access Requirements

## Installation

### 1. Clone Repository
### 2. Install Dependencies
### 3. Configure Environment
### 4. Initialize Database

## Verification
How to verify installation

## Troubleshooting
Common setup issues

## Next Steps
Links to other documentation
```

## Integration with Build Specs

### Phase 1: Core UI
When validating UI documentation:
- Installation steps match Phase1_CoreUI.md requirements
- MFE architecture descriptions are accurate
- Component usage examples are current
- Development workflow is documented

### Phase 2: APIs
When validating API documentation:
- API endpoint examples match OpenAPI specs
- Authentication/authorization documented correctly
- Deployment procedures follow Phase2_APIs.md
- Security requirements from Phase2_API_SecurityRequirements.md included

### Phase 2: Evaluation Framework
When validating testing/evaluation docs:
- Metric definitions match Phase2_Evaluation_Framework.md
- Test procedures are complete and accurate
- Evaluation criteria properly documented

### Phase 3: Privacy Framework
When validating privacy/compliance docs:
- PII handling aligns with Phase3_Privacy_Framework.md
- Data retention policies documented
- Compliance requirements covered

## Validation Rules

### Code Block Rules
```markdown
# ❌ BAD: No language tag
\`\`\`
npm install
\`\`\`

# ✅ GOOD: Proper language tag
\`\`\`bash
npm install
\`\`\`

# ✅ GOOD: With environment context
\`\`\`bash
AWS_PROFILE=terragrunt-dev-workload aws s3 ls
\`\`\`
```

### File Path Rules
```markdown
# ❌ BAD: Incorrect path
See configuration in `config/app.yml`

# ✅ GOOD: Correct relative path
See configuration in `api-tier/config/app.yml`

# ✅ GOOD: With code reference
See `api-tier/routes/auth.py:45` for implementation
```

### Command Example Rules
```markdown
# ❌ BAD: Missing context
\`\`\`bash
docker build -t myapp .
\`\`\`

# ✅ GOOD: Complete context
\`\`\`bash
# From project root
cd /Users/rohitiyer/datagrub/promptforge
docker build -t myapp -f api-tier/Dockerfile .
\`\`\`

# ✅ GOOD: With expected output
\`\`\`bash
curl http://localhost:8000/health
# Expected output:
# {"status": "healthy", "version": "1.0.0"}
\`\`\`
```

### Link Rules
```markdown
# ❌ BAD: Broken internal link
See [Architecture](docs/arch.md)

# ✅ GOOD: Valid internal link
See [Architecture](ARCHITECTURE.md)

# ✅ GOOD: Anchor link
See [Deployment](#deployment-procedures)
```

## Command Validation Checklist

For each bash/shell command in documentation:

1. **Syntax check**: Parse and validate with bash -n
2. **Tool availability**: Check if command exists (`which command`)
3. **Environment variables**: Verify all required vars are documented
4. **Working directory**: Check if commands need specific pwd
5. **Permissions**: Verify file/directory permissions if mentioned
6. **Error handling**: Check if error cases are documented
7. **Output validation**: Test if example output matches current behavior

## Error Severity Levels

| Severity | Blocking | Examples |
|----------|----------|----------|
| **Critical** | Yes | Security vulnerabilities in examples, data loss commands |
| **High** | Yes (in prod) | Broken critical workflows, spec violations, incorrect commands |
| **Medium** | No | Missing sections, minor inaccuracies, style issues |
| **Low** | No | Formatting, typos, optimization suggestions |

## Commands

### validate_readme
**Input**: File path, spec references
**Output**: JSON envelope with findings
**Action**: Run full documentation validation suite

### validate_commands
**Input**: Extracted code blocks
**Output**: Command validation results
**Action**: Test each command for syntax and executability

### fix_formatting
**Input**: File path, formatting issues
**Output**: Applied fixes diff
**Action**: Apply markdown formatting fixes

### check_links
**Input**: File path
**Output**: Link validation report
**Action**: Validate all internal and external links

### update_context
**Input**: Validation results
**Output**: Updated context file
**Action**: Persist learnings to memory

## Success Criteria

✅ All command examples are syntactically correct and executable
✅ File path references point to existing files
✅ Build spec compliance validated against relevant phase docs
✅ Required documentation sections present and complete
✅ Code blocks have proper language tags
✅ Links are valid (internal and external)
✅ Auto-fixes applied safely without breaking formatting
✅ Clear, actionable findings with spec references
✅ Context updated to learn from repeated patterns
