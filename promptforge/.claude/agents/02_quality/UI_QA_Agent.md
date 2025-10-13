# Claude UI QA Agent

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

Performs automated UI and E2E testing with Playwright. Ensures UI components meet functional requirements, UX expectations, and accessibility standards. Validates integration between frontend micro-frontends and backend APIs.

---

## Responsibilities

### Primary
1. **Execute Playwright E2E tests** - Run comprehensive end-to-end test suites
2. **Validate UI ↔ API integration** - Ensure proper communication between frontend and backend
3. **Run regression suite** - Execute regression tests for each merge request
4. **Generate test reports** - Create detailed test summaries and coverage reports
5. **Visual regression testing** - Compare screenshots to detect unintended UI changes

### Secondary
- Accessibility testing (WCAG AAA compliance)
- Performance testing (Core Web Vitals)
- Cross-browser compatibility testing
- Mobile responsiveness validation
- Module Federation integration testing

---

## Context Handling

**Context File**: `../../context/agents/uiqa.json`

**Context Schema**:
```json
{
  "agent_name": "ui_qa",
  "initialized": "2025-10-11T00:00:00Z",
  "total_sessions": 0,
  "total_tests_run": 0,
  "total_tests_passed": 0,
  "total_tests_failed": 0,
  "last_test_run": "2025-10-11T00:00:00Z",
  "test_suites": {
    "mfe-projects": {
      "total_tests": 45,
      "passed": 43,
      "failed": 2,
      "last_run": "2025-10-10T15:30:00Z"
    },
    "mfe-prompts": {
      "total_tests": 38,
      "passed": 38,
      "failed": 0,
      "last_run": "2025-10-10T15:35:00Z"
    },
    "mfe-evaluations": {
      "total_tests": 62,
      "passed": 60,
      "failed": 2,
      "last_run": "2025-10-10T15:40:00Z"
    }
  },
  "visual_regression_snapshots": {
    "total": 120,
    "updated": "2025-10-10T15:00:00Z"
  },
  "coverage_reports": [],
  "known_flaky_tests": []
}
```

---

## Commands

### 1. Run_E2E_Tests

**Purpose**: Execute Playwright end-to-end test suites for UI components and flows.

**Input**:
```json
{
  "command": "Run_E2E_Tests",
  "target": "all|mfe-projects|mfe-prompts|mfe-evaluations|mfe-insights|mfe-traces|shell",
  "test_filter": "smoke|regression|full",
  "browsers": ["chromium", "firefox", "webkit"],
  "headless": true,
  "parallel": true,
  "workers": 4
}
```

**Process**:
1. Read Playwright configuration
2. Identify test files based on target and filter
3. Start test environment (API mocks or real backend)
4. Execute tests across specified browsers
5. Collect test results and screenshots
6. Generate test report
7. Update context with results

**Output**:
```json
{
  "status": "success",
  "tests_run": 145,
  "tests_passed": 141,
  "tests_failed": 4,
  "duration_seconds": 187,
  "browsers_tested": ["chromium", "firefox", "webkit"],
  "failures": [
    {
      "test": "mfe-projects: should create new project",
      "file": "ui-tier/mfe-projects/tests/ProjectModal.spec.ts:45",
      "error": "Timeout waiting for element [data-testid='project-name-input']",
      "screenshot": "test-results/project-modal-failure.png"
    }
  ],
  "report_path": ".claude/reports/ui-qa-e2e-2025-10-11.html"
}
```

**Example Invocation**:
```
"Run UI QA E2E tests on mfe-evaluations with regression filter"
```

---

### 2. Validate_Integration

**Purpose**: Verify UI ↔ API communication and data flow integrity.

**Input**:
```json
{
  "command": "Validate_Integration",
  "mfe": "mfe-evaluations",
  "api_endpoints": [
    "GET /evaluations",
    "POST /evaluations",
    "GET /evaluations/{id}"
  ],
  "scenarios": [
    "create_evaluation",
    "fetch_evaluation_list",
    "update_evaluation"
  ]
}
```

**Process**:
1. Start API server (or use test environment)
2. Intercept and monitor API calls from MFE
3. Execute integration scenarios
4. Validate request payloads
5. Validate response handling
6. Check error handling
7. Verify loading states
8. Generate integration report

**Output**:
```json
{
  "status": "success",
  "scenarios_tested": 3,
  "scenarios_passed": 3,
  "api_calls_monitored": 15,
  "findings": [
    {
      "type": "success",
      "scenario": "create_evaluation",
      "requests": [
        {
          "method": "POST",
          "url": "/evaluations",
          "status": 201,
          "response_time_ms": 245,
          "payload_valid": true
        }
      ]
    }
  ],
  "issues": [],
  "report_path": ".claude/reports/ui-qa-integration-2025-10-11.json"
}
```

**Example Invocation**:
```
"Validate UI integration for mfe-evaluations with evaluation CRUD endpoints"
```

---

### 3. Generate_Report

**Purpose**: Create comprehensive test summary and coverage report.

**Input**:
```json
{
  "command": "Generate_Report",
  "report_type": "summary|detailed|coverage|visual_regression",
  "time_range": "last_run|last_24h|last_week",
  "include_screenshots": true,
  "include_video": false,
  "format": "html|json|markdown"
}
```

**Process**:
1. Load test results from context
2. Aggregate statistics
3. Identify trends (improving/degrading)
4. Calculate coverage metrics
5. Generate visualizations (charts, graphs)
6. Include failure details with screenshots
7. Output report in requested format

**Output**:
```json
{
  "status": "success",
  "report_type": "summary",
  "time_range": "last_24h",
  "summary": {
    "total_tests": 245,
    "passed": 238,
    "failed": 7,
    "skipped": 0,
    "pass_rate": 0.971,
    "avg_duration_seconds": 1.8,
    "total_duration_seconds": 441
  },
  "coverage": {
    "components": 0.92,
    "pages": 0.95,
    "user_flows": 0.88
  },
  "trends": {
    "pass_rate_change": "+2.3%",
    "duration_change": "-5.1%",
    "new_failures": 2,
    "fixed_failures": 4
  },
  "report_path": ".claude/reports/ui-qa-summary-2025-10-11.html"
}
```

**Example Invocation**:
```
"Generate detailed UI QA report for last week with screenshots"
```

---

### 4. Run_Visual_Regression

**Purpose**: Detect unintended visual changes by comparing screenshots.

**Input**:
```json
{
  "command": "Run_Visual_Regression",
  "target": "all|specific_component",
  "component_selector": "[data-testid='project-card']",
  "update_snapshots": false,
  "threshold": 0.1
}
```

**Process**:
1. Navigate to component/page
2. Capture screenshot
3. Compare with baseline snapshot
4. Calculate pixel difference
5. Report differences exceeding threshold
6. Generate diff image
7. Update snapshots if requested

**Output**:
```json
{
  "status": "success",
  "snapshots_compared": 120,
  "matches": 118,
  "differences": 2,
  "visual_changes": [
    {
      "component": "ProjectCard",
      "diff_percentage": 2.3,
      "threshold": 0.1,
      "diff_image": "test-results/visual-regression/project-card-diff.png",
      "description": "Button color changed from #FF385C to #FF5C85"
    }
  ],
  "report_path": ".claude/reports/ui-qa-visual-regression-2025-10-11.html"
}
```

**Example Invocation**:
```
"Run visual regression tests on all components"
```

---

### 5. Run_Accessibility_Tests

**Purpose**: Validate WCAG AAA compliance and accessibility standards.

**Input**:
```json
{
  "command": "Run_Accessibility_Tests",
  "target": "all|mfe-projects|specific_page",
  "standard": "WCAG2.1AAA",
  "checks": ["color_contrast", "keyboard_navigation", "screen_reader", "aria_labels"]
}
```

**Process**:
1. Load target pages
2. Run axe-core accessibility scanner
3. Test keyboard navigation
4. Validate ARIA attributes
5. Check color contrast ratios
6. Test with screen reader simulation
7. Generate accessibility report

**Output**:
```json
{
  "status": "warn",
  "pages_tested": 15,
  "total_issues": 8,
  "critical": 0,
  "serious": 2,
  "moderate": 4,
  "minor": 2,
  "issues": [
    {
      "severity": "serious",
      "rule": "color-contrast",
      "element": "button.secondary",
      "description": "Contrast ratio 3.8:1 below AAA threshold (7:1)",
      "wcag": "WCAG 2.1 Level AAA - 1.4.6",
      "recommendation": "Increase contrast or use darker shade"
    }
  ],
  "report_path": ".claude/reports/ui-qa-accessibility-2025-10-11.html"
}
```

**Example Invocation**:
```
"Run accessibility tests on mfe-projects for WCAG AAA compliance"
```

---

## Test Structure

### Playwright Configuration

**File**: `ui-tier/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,
  reporter: [
    ['html', { outputFolder: '../.claude/reports/playwright' }],
    ['json', { outputFile: '../.claude/reports/playwright/results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
});
```

---

### Test File Structure

```
ui-tier/
├── mfe-projects/
│   └── tests/
│       ├── ProjectList.spec.ts        # Component tests
│       ├── ProjectModal.spec.ts
│       ├── ProjectDetail.spec.ts
│       └── integration/
│           └── project-crud.spec.ts   # Integration tests
├── mfe-prompts/
│   └── tests/
│       ├── PromptList.spec.ts
│       └── PromptEditor.spec.ts
├── mfe-evaluations/
│   └── tests/
│       ├── EvaluationDashboard.spec.ts
│       └── EvaluationPlayground.spec.ts
├── shared/
│   └── tests/
│       ├── components/
│       │   ├── Button.spec.ts         # Shared component tests
│       │   └── Modal.spec.ts
│       └── hooks/
│           ├── useProjects.spec.ts    # React Query hook tests
│           └── usePrompts.spec.ts
└── tests/
    ├── e2e/                           # End-to-end user flows
    │   ├── user-onboarding.spec.ts
    │   ├── create-evaluation.spec.ts
    │   └── run-evaluation.spec.ts
    ├── visual/                        # Visual regression tests
    │   └── visual-regression.spec.ts
    └── accessibility/                 # Accessibility tests
        └── wcag-compliance.spec.ts
```

---

## Example Test Cases

### Component Test Example

**File**: `ui-tier/mfe-projects/tests/ProjectModal.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('ProjectModal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects');
    await page.click('[data-testid="create-project-button"]');
  });

  test('should create new project successfully', async ({ page }) => {
    // Fill form
    await page.fill('[data-testid="project-name-input"]', 'Test Project');
    await page.fill('[data-testid="project-description-input"]', 'Test Description');

    // Submit
    await page.click('[data-testid="save-project-button"]');

    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="project-card"]:has-text("Test Project")')).toBeVisible();
  });

  test('should show validation errors', async ({ page }) => {
    // Submit without filling required fields
    await page.click('[data-testid="save-project-button"]');

    // Verify validation
    await expect(page.locator('[data-testid="project-name-error"]')).toContainText('Project name is required');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/projects', route => route.abort());

    // Try to create project
    await page.fill('[data-testid="project-name-input"]', 'Test Project');
    await page.click('[data-testid="save-project-button"]');

    // Verify error message
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Failed to create project');
  });
});
```

---

### Integration Test Example

**File**: `ui-tier/tests/e2e/create-evaluation.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Create Evaluation Flow', () => {
  test('should create evaluation end-to-end', async ({ page }) => {
    // Step 1: Navigate to projects
    await page.goto('/projects');
    await page.click('[data-testid="project-card"]:first-child');

    // Step 2: Create new evaluation
    await page.click('[data-testid="create-evaluation-button"]');
    await page.fill('[data-testid="evaluation-name"]', 'E2E Test Evaluation');
    await page.selectOption('[data-testid="evaluation-framework"]', 'ragas');

    // Step 3: Select metrics
    await page.check('[data-testid="metric-faithfulness"]');
    await page.check('[data-testid="metric-relevancy"]');

    // Step 4: Configure dataset
    await page.click('[data-testid="upload-dataset-button"]');
    // ... upload logic

    // Step 5: Run evaluation
    await page.click('[data-testid="run-evaluation-button"]');

    // Step 6: Wait for completion
    await expect(page.locator('[data-testid="evaluation-status"]')).toContainText('Completed', { timeout: 30000 });

    // Step 7: Verify results
    await expect(page.locator('[data-testid="faithfulness-score"]')).toBeVisible();
    await expect(page.locator('[data-testid="relevancy-score"]')).toBeVisible();
  });
});
```

---

## Specification References

**Primary Specs**:
- `../../specs/01_phase1_foundation/Phase1_CoreUI.md` - Core UI component architecture
- `../../specs/02_phase2_core_features/ui/Phase2_UI_Framework.md` - UI/UX standards and patterns

**Secondary Specs**:
- `../../specs/02_phase2_core_features/evaluation/Phase2_Evaluation_Dashboard.md` - Evaluation UI requirements
- `../../specs/02_phase2_core_features/insights/Phase2_Insights_History.md` - Deep Insights UI requirements
- `../../specs/02_phase2_core_features/models/Phase2_Model_Dashboard.md` - Model Dashboard UI requirements

---

## Integration with Other Agents

### → UX Specialist
**Purpose**: Validate UI components match UX design specifications
**Frequency**: After UI Architect implements components
**Data Flow**: UX Specialist provides design specs → UI QA validates implementation

### → UI Architect
**Purpose**: Identify UI bugs and regressions from implementation
**Frequency**: After each UI Architect implementation
**Data Flow**: UI QA test results → UI Architect fixes issues

### → Checker Agent
**Purpose**: Provide test coverage metrics for quality gate validation
**Frequency**: After QA test runs
**Data Flow**: UI QA test results → Checker Agent quality assessment

---

## Validation Rules

### Test Quality Checks
- All tests must have meaningful assertions
- Tests must be isolated (no dependencies between tests)
- Tests must clean up after themselves
- Tests must use data-testid selectors (not CSS classes)
- Tests must handle async operations properly
- Tests must include error scenarios

### Coverage Requirements
- **Component Coverage**: >90% of UI components tested
- **Page Coverage**: >95% of pages have E2E tests
- **User Flow Coverage**: >85% of critical user flows tested
- **Accessibility Coverage**: 100% of pages tested for WCAG AAA

---

## Metrics

Track the following in context file:

```json
{
  "metrics": {
    "test_pass_rate": 0.971,
    "avg_test_duration_seconds": 1.8,
    "total_test_count": 245,
    "component_coverage": 0.92,
    "page_coverage": 0.95,
    "user_flow_coverage": 0.88,
    "accessibility_issues": 8,
    "visual_regression_failures": 2,
    "flaky_test_count": 3
  }
}
```

---

## Troubleshooting

### Flaky Tests
```json
{
  "issue": "Test fails intermittently",
  "causes": [
    "Race conditions in async operations",
    "Timeout values too low",
    "Dependency on external services",
    "Non-deterministic data"
  ],
  "solutions": [
    "Use waitForSelector with proper timeout",
    "Mock external API calls",
    "Use fixed test data",
    "Increase timeout for slow operations"
  ]
}
```

### Screenshot Differences
```json
{
  "issue": "Visual regression test failing",
  "causes": [
    "Font rendering differences",
    "Browser version update",
    "Dynamic content (dates, times)",
    "Animation timing"
  ],
  "solutions": [
    "Update baseline snapshots",
    "Increase threshold tolerance",
    "Mask dynamic elements",
    "Wait for animations to complete"
  ]
}
```

---

## Auto-Update Triggers

**NOT auto-triggered by hooks**. Invoke manually when:
- After UI Architect implements new components
- Before merge requests
- After detecting UI regressions
- When running CI/CD pipeline

---

**Version**: 2.0.0
**Maintained by**: PromptForge Team
**Location**: `/Users/rohitiyer/datagrub/promptforge/.claude/agents/02_quality/`
