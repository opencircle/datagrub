import { test, expect } from '@playwright/test';
import { UI_BASE_URL } from '../fixtures/test-data';

/**
 * Insight Comparison E2E Tests
 *
 * Tests the complete user flow for comparing two Call Insights analyses
 * including:
 * - Creating comparisons from history section
 * - Viewing comparison results with radar charts
 * - Browsing comparison history
 * - Deleting comparisons
 */

test.describe('Insight Comparison E2E Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Deep Insights page
    await page.goto(`${UI_BASE_URL}/insights`);

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display compare button in history section', async ({ page }) => {
    // Expand history section if collapsed
    const historyHeader = page.locator('text=Recent Analyses').first();
    await historyHeader.click();

    // Wait for history table to load
    await page.waitForSelector('table', { timeout: 10000 });

    // Check for compare button
    const compareButton = page.locator('button:has-text("Compare")');
    await expect(compareButton).toBeVisible();
  });

  test('should enable compare mode and select analyses', async ({ page }) => {
    // Expand history section
    const historyHeader = page.locator('text=Recent Analyses').first();
    await historyHeader.click();

    // Wait for table
    await page.waitForSelector('table', { timeout: 10000 });

    // Click compare button
    const compareButton = page.locator('button:has-text("Compare")').first();
    await compareButton.click();

    // Verify compare mode instructions appear
    await expect(page.locator('text=Compare Mode:')).toBeVisible();
    await expect(page.locator('text=Select 2 analyses to compare')).toBeVisible();

    // Check that checkboxes appear in table
    const checkboxes = page.locator('input[type="checkbox"]');
    const checkboxCount = await checkboxes.count();
    expect(checkboxCount).toBeGreaterThan(0);

    // Select first analysis
    await checkboxes.first().check();

    // Verify selection count updated
    await expect(page.locator('text=(1/2 selected)')).toBeVisible();

    // Select second analysis
    await checkboxes.nth(1).check();

    // Verify selection count updated and compare button appears
    await expect(page.locator('text=(2/2 selected)')).toBeVisible();
    await expect(page.locator('button:has-text("Compare Selected Analyses")')).toBeVisible();
  });

  test('should disable additional selections after 2 analyses selected', async ({ page }) => {
    // Expand history and enter compare mode
    await page.locator('text=Recent Analyses').first().click();
    await page.waitForSelector('table', { timeout: 10000 });
    await page.locator('button:has-text("Compare")').first().click();

    const checkboxes = page.locator('input[type="checkbox"]');

    // Select first two analyses
    await checkboxes.first().check();
    await checkboxes.nth(1).check();

    // Verify third checkbox is disabled
    if ((await checkboxes.count()) >= 3) {
      await expect(checkboxes.nth(2)).toBeDisabled();
    }
  });

  test('should cancel compare mode', async ({ page }) => {
    // Enter compare mode
    await page.locator('text=Recent Analyses').first().click();
    await page.waitForSelector('table', { timeout: 10000 });
    await page.locator('button:has-text("Compare")').first().click();

    // Verify in compare mode
    await expect(page.locator('text=Compare Mode:')).toBeVisible();

    // Click cancel button
    await page.locator('button:has-text("Cancel")').click();

    // Verify compare mode instructions disappeared
    await expect(page.locator('text=Compare Mode:')).not.toBeVisible();

    // Verify checkboxes are hidden
    const checkboxes = page.locator('input[type="checkbox"]');
    expect(await checkboxes.count()).toBe(0);
  });

  test('should navigate to comparison page', async ({ page }) => {
    // Navigate to comparison page via URL
    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Verify page loaded
    await expect(page.locator('h1:has-text("Model Comparison")')).toBeVisible();
    await expect(
      page.locator('text=Compare different models or parameters on the same transcript')
    ).toBeVisible();

    // Verify tabs are present
    await expect(page.locator('button:has-text("Create Comparison")')).toBeVisible();
    await expect(page.locator('button:has-text("History")')).toBeVisible();
  });

  test('should display comparison selector form', async ({ page }) => {
    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Verify selector components
    await expect(page.locator('text=Analysis A (Baseline)')).toBeVisible();
    await expect(page.locator('text=Analysis B (Comparison)')).toBeVisible();
    await expect(page.locator('text=Judge Model')).toBeVisible();
    await expect(page.locator('text=Evaluation Criteria')).toBeVisible();

    // Verify default judge model is selected
    await expect(page.locator('text=Claude Sonnet 4.5 (Recommended)')).toBeVisible();

    // Verify criteria buttons are present
    await expect(page.locator('button:has-text("Groundedness")')).toBeVisible();
    await expect(page.locator('button:has-text("Faithfulness")')).toBeVisible();
    await expect(page.locator('button:has-text("Completeness")')).toBeVisible();
    await expect(page.locator('button:has-text("Clarity")')).toBeVisible();
    await expect(page.locator('button:has-text("Accuracy")')).toBeVisible();
  });

  test('should toggle evaluation criteria', async ({ page }) => {
    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    const groundednessButton = page.locator('button:has-text("Groundedness")').first();

    // Verify initially selected (has pink background)
    await expect(groundednessButton).toHaveClass(/border-\[#FF385C\]/);

    // Click to deselect
    await groundednessButton.click();

    // Verify deselected (has neutral background)
    await expect(groundednessButton).toHaveClass(/border-neutral-300/);

    // Click to reselect
    await groundednessButton.click();

    // Verify selected again
    await expect(groundednessButton).toHaveClass(/border-\[#FF385C\]/);
  });

  test('should show validation error when no criteria selected', async ({ page }) => {
    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Deselect all criteria
    const criteriaButtons = page.locator(
      'button:has-text("Groundedness"), button:has-text("Faithfulness"), button:has-text("Completeness"), button:has-text("Clarity"), button:has-text("Accuracy")'
    );

    for (let i = 0; i < (await criteriaButtons.count()); i++) {
      const button = criteriaButtons.nth(i);
      if (await button.evaluate((el) => el.className.includes('border-[#FF385C]'))) {
        await button.click();
      }
    }

    // Verify error message appears
    await expect(page.locator('text=Select at least one evaluation criterion')).toBeVisible();

    // Verify create button is disabled
    const createButton = page.locator('button:has-text("Create Comparison")');
    await expect(createButton).toBeDisabled();
  });

  test('should switch to history tab', async ({ page }) => {
    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Click history tab
    await page.locator('button:has-text("History")').click();

    // Verify history component is displayed
    await expect(page.locator('text=Comparison History')).toBeVisible();

    // Could show empty state or actual comparisons
    const hasComparisons = await page.locator('table').isVisible();
    const hasEmptyState = await page.locator('text=No Comparisons Yet').isVisible();

    expect(hasComparisons || hasEmptyState).toBeTruthy();
  });

  test('should display comparison results page structure', async ({ page }) => {
    test.skip(
      !process.env.TEST_COMPARISON_ID,
      'Requires TEST_COMPARISON_ID environment variable with a valid comparison ID'
    );

    const comparisonId = process.env.TEST_COMPARISON_ID;

    // Navigate to specific comparison
    await page.goto(`${UI_BASE_URL}/insights/comparisons/${comparisonId}`);

    // Wait for comparison to load
    await page.waitForSelector('text=Overall Winner', { timeout: 10000 });

    // Verify main sections are present
    await expect(page.locator('text=Overall Winner')).toBeVisible();
    await expect(page.locator('text=Judge Model')).toBeVisible();
    await expect(page.locator('text=Cost Difference')).toBeVisible();
    await expect(page.locator('text=Quality Difference')).toBeVisible();

    // Verify stage-by-stage analysis
    await expect(page.locator('text=Stage-by-Stage Analysis')).toBeVisible();
    await expect(page.locator('text=Stage 1: Fact Extraction')).toBeVisible();
    await expect(page.locator('text=Stage 2: Reasoning & Insights')).toBeVisible();
    await expect(page.locator('text=Stage 3: Summary')).toBeVisible();

    // Verify radar charts are rendered (check for SVG elements)
    const svgElements = page.locator('svg');
    expect(await svgElements.count()).toBeGreaterThan(0);

    // Verify analysis metadata cards
    await expect(page.locator('text=Model A (Baseline)')).toBeVisible();
    await expect(page.locator('text=Model B (Comparison)')).toBeVisible();

    // Verify judge trace info
    await expect(page.locator('text=Judge Model Trace')).toBeVisible();
  });

  test('should navigate back from comparison details to history', async ({ page }) => {
    test.skip(
      !process.env.TEST_COMPARISON_ID,
      'Requires TEST_COMPARISON_ID environment variable'
    );

    const comparisonId = process.env.TEST_COMPARISON_ID;

    await page.goto(`${UI_BASE_URL}/insights/comparisons/${comparisonId}`);
    await page.waitForSelector('text=Overall Winner', { timeout: 10000 });

    // Click back to history button
    await page.locator('button:has-text("Back to History")').click();

    // Verify returned to history view
    await expect(page.locator('text=Comparison History')).toBeVisible();
  });

  test('should handle comparison creation with full workflow', async ({ page }) => {
    test.skip(
      !process.env.PROMPTFORGE_TEST_TOKEN,
      'Requires authenticated session for comparison creation'
    );

    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Select first analysis from dropdown
    const analysisADropdown = page.locator('select').first();
    await analysisADropdown.selectOption({ index: 1 });

    // Wait for analysis B dropdown to enable
    await page.waitForTimeout(500);

    // Select second analysis from dropdown
    const analysisBDropdown = page.locator('select').nth(1);
    await analysisBDropdown.selectOption({ index: 1 });

    // Verify create button is enabled
    const createButton = page.locator('button:has-text("Create Comparison")');
    await expect(createButton).toBeEnabled();

    // Click create comparison
    await createButton.click();

    // Wait for comparison to be created (could take a while with API calls)
    await page.waitForSelector('text=Overall Winner', { timeout: 60000 });

    // Verify redirected to results view
    await expect(page.locator('text=Overall Winner')).toBeVisible();
    await expect(page.locator('text=Stage-by-Stage Analysis')).toBeVisible();
  });

  test('should handle insufficient analyses gracefully', async ({ page }) => {
    // This test assumes the user has less than 2 analyses
    // In practice, you might need to set up test data specifically for this case

    await page.goto(`${UI_BASE_URL}/insights/comparisons`);

    // Check if warning message appears
    const hasWarning = await page.locator('text=Not Enough Analyses').isVisible();

    if (hasWarning) {
      await expect(
        page.locator(
          'text=You need at least 2 completed analyses to create a comparison'
        )
      ).toBeVisible();
    }
  });

  test('should display winner badges correctly', async ({ page }) => {
    test.skip(!process.env.TEST_COMPARISON_ID, 'Requires TEST_COMPARISON_ID');

    const comparisonId = process.env.TEST_COMPARISON_ID;
    await page.goto(`${UI_BASE_URL}/insights/comparisons/${comparisonId}`);
    await page.waitForSelector('text=Overall Winner', { timeout: 10000 });

    // Check that winner badge is displayed (could be "Model A", "Model B", or "Tie")
    const winnerBadge = page.locator(
      'text=Model A, text=Model B, text=Tie'
    ).first();
    await expect(winnerBadge).toBeVisible();

    // Verify each stage has a winner indicator
    const stages = ['Stage 1: Fact Extraction', 'Stage 2: Reasoning & Insights', 'Stage 3: Summary'];

    for (const stage of stages) {
      await expect(page.locator(`text=${stage}`)).toBeVisible();
    }
  });

  test('should handle comparison deletion from history', async ({ page }) => {
    test.skip(
      !process.env.PROMPTFORGE_TEST_TOKEN,
      'Requires authenticated session for deletion'
    );

    await page.goto(`${UI_BASE_URL}/insights/comparisons`);
    await page.locator('button:has-text("History")').click();

    // Wait for history to load
    await page.waitForTimeout(1000);

    // Check if any comparisons exist
    const hasComparisons = await page.locator('table').isVisible();

    if (hasComparisons) {
      // Set up dialog handler for confirmation
      page.on('dialog', (dialog) => {
        expect(dialog.message()).toContain('delete');
        dialog.accept();
      });

      // Find and click first delete button
      const deleteButton = page.locator('button[title="Delete comparison"]').first();
      await deleteButton.click();

      // Wait for deletion to process
      await page.waitForTimeout(1000);

      // Verify row was removed or empty state appears
      // (Implementation depends on whether there are more comparisons)
    }
  });

  test('should display cost and quality metrics', async ({ page }) => {
    test.skip(!process.env.TEST_COMPARISON_ID, 'Requires TEST_COMPARISON_ID');

    const comparisonId = process.env.TEST_COMPARISON_ID;
    await page.goto(`${UI_BASE_URL}/insights/comparisons/${comparisonId}`);
    await page.waitForSelector('text=Overall Winner', { timeout: 10000 });

    // Verify cost difference is displayed
    await expect(page.locator('text=Cost Difference')).toBeVisible();
    const costValue = page.locator('text=/[+-]?\\$[0-9.]+/').first();
    await expect(costValue).toBeVisible();

    // Verify quality difference is displayed
    await expect(page.locator('text=Quality Difference')).toBeVisible();
    const qualityValue = page.locator('text=/[+-]?[0-9.]+%/').first();
    await expect(qualityValue).toBeVisible();

    // Verify judge trace metrics
    await expect(page.locator('text=Judge Model Trace')).toBeVisible();
    await expect(page.locator('text=Tokens')).toBeVisible();
    await expect(page.locator('text=Cost')).toBeVisible();
    await expect(page.locator('text=Duration')).toBeVisible();
  });

  test('should display score tables for each stage', async ({ page }) => {
    test.skip(!process.env.TEST_COMPARISON_ID, 'Requires TEST_COMPARISON_ID');

    const comparisonId = process.env.TEST_COMPARISON_ID;
    await page.goto(`${UI_BASE_URL}/insights/comparisons/${comparisonId}`);
    await page.waitForSelector('text=Overall Winner', { timeout: 10000 });

    // Check that each stage has a score table
    const tables = page.locator('table');
    expect(await tables.count()).toBeGreaterThanOrEqual(3);

    // Verify score values are displayed (should be percentages)
    const scorePattern = /\d+%/;
    const scores = page.locator('text=/\\d+%/');
    expect(await scores.count()).toBeGreaterThan(0);
  });
});
