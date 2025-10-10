import { test, expect } from '@playwright/test';

test.describe('Evaluations Module', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/evaluations');
  });

  test('should display evaluation results tab', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Check if the page title is visible
    await expect(page.locator('h1')).toContainText('Evaluations');

    // Check if stats cards are present
    await expect(page.locator('text=Total Runs')).toBeVisible();
    await expect(page.locator('text=Avg Score')).toBeVisible();
    await expect(page.locator('text=Running')).toBeVisible();
    await expect(page.locator('text=Failed')).toBeVisible();
  });

  // ==================== P0 FEATURES: EVALUATION TABLE ====================

  test('should display evaluation table with all columns', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Check if table headers are present
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Prompt Title")')).toBeVisible();
    await expect(page.locator('th:has-text("Evaluation")')).toBeVisible();
    await expect(page.locator('th:has-text("Vendor")')).toBeVisible();
    await expect(page.locator('th:has-text("Category")')).toBeVisible();
    await expect(page.locator('th:has-text("Score")')).toBeVisible();
    await expect(page.locator('th:has-text("Model")')).toBeVisible();
    await expect(page.locator('th:has-text("Time")')).toBeVisible();
  });

  test('should filter evaluations by prompt title', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Find and use the prompt title search box
    const searchBox = page.locator('input[placeholder*="Search prompt titles"]');
    await expect(searchBox).toBeVisible();

    // Type a search query
    await searchBox.fill('Customer');

    // Wait for debounce (300ms) and API call
    await page.waitForTimeout(500);

    // Results should be filtered
    await expect(page.locator('text=/\\d+ results?/')).toBeVisible();
  });

  test('should filter evaluations by vendor', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Click the Filters button to expand
    const filtersButton = page.locator('button:has-text("Filters")');
    await filtersButton.click();

    // Select a vendor from dropdown
    const vendorSelect = page.locator('select', { has: page.locator('option:has-text("DeepEval")') });
    await vendorSelect.selectOption('DeepEval');

    // Wait for API call
    await page.waitForTimeout(500);

    // Active filter count should be visible
    await expect(filtersButton.locator('text=/\\d+/')).toBeVisible();
  });

  test('should filter evaluations by category', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Click the Filters button
    await page.locator('button:has-text("Filters")').click();

    // Select a category
    const categorySelect = page.locator('label:has-text("Category")').locator('..').locator('select');
    await categorySelect.selectOption('quality');

    await page.waitForTimeout(500);
  });

  test('should filter evaluations by status', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Click Filters button
    await page.locator('button:has-text("Filters")').click();

    // Select status
    const statusSelect = page.locator('label:has-text("Status")').locator('..').locator('select');
    await statusSelect.selectOption('pass');

    await page.waitForTimeout(500);
  });

  test('should clear all filters', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Add a filter
    const searchBox = page.locator('input[placeholder*="Search prompt titles"]');
    await searchBox.fill('Test');
    await page.waitForTimeout(500);

    // Clear filters button should appear
    const clearButton = page.locator('button:has-text("Clear")');
    await expect(clearButton).toBeVisible();

    // Click clear
    await clearButton.click();

    // Search box should be empty
    await expect(searchBox).toHaveValue('');
  });

  test('should sort by clicking column headers', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Click on Score header
    const scoreHeader = page.locator('th:has-text("Score")');
    await scoreHeader.click();

    // Wait for sort to apply
    await page.waitForTimeout(500);

    // Should see sort indicator (↑ or ↓)
    await expect(scoreHeader).toContainText(/[↑↓]/);

    // Click again to reverse sort
    await scoreHeader.click();
    await page.waitForTimeout(500);
  });

  test('should paginate through evaluation results', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Wait for table to load
    await page.waitForTimeout(1000);

    // Check if pagination is visible (only if more than one page)
    const nextButton = page.locator('button:has-text("Next")');
    const hasMultiplePages = await nextButton.isVisible();

    if (hasMultiplePages && !(await nextButton.isDisabled())) {
      // Click next page
      await nextButton.click();
      await page.waitForTimeout(500);

      // Should be on page 2
      await expect(page.locator('text=/Page \\d+ of \\d+/')).toBeVisible();

      // Previous button should be enabled
      const prevButton = page.locator('button:has-text("Previous")');
      await expect(prevButton).toBeEnabled();
    }
  });

  // ==================== P1 FEATURES: EVALUATION DETAIL MODAL ====================

  test('should open detail modal when clicking on evaluation row', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Wait for table to load
    await page.waitForTimeout(1000);

    // Get first table row (excluding header)
    const firstRow = page.locator('tbody tr').first();

    // Check if there are any rows
    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      // Click the row
      await firstRow.click();

      // Wait for modal to open
      await page.waitForTimeout(500);

      // Modal should be visible with key sections
      await expect(page.locator('text=SCORE')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('text=TRACE CONTEXT')).toBeVisible();
      await expect(page.locator('text=EVALUATION RESULTS')).toBeVisible();
      await expect(page.locator('text=EXECUTION METRICS')).toBeVisible();
    }
  });

  test('should display score in detail modal', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Score should be visible
      await expect(page.locator('text=SCORE')).toBeVisible();

      // Score should have a value (number or N/A)
      const scoreSection = page.locator('text=SCORE').locator('..');
      await expect(scoreSection).toBeVisible();
    }
  });

  test('should display execution metrics in detail modal', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Metrics section should be visible
      await expect(page.locator('text=EXECUTION METRICS')).toBeVisible();
      await expect(page.locator('text=Duration')).toBeVisible();
      await expect(page.locator('text=Tokens')).toBeVisible();
      await expect(page.locator('text=Cost')).toBeVisible();
    }
  });

  test('should navigate to trace from detail modal', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Click "View Trace" button
      const viewTraceButton = page.locator('button:has-text("View Trace")').first();

      if (await viewTraceButton.isVisible()) {
        await viewTraceButton.click();

        // Should navigate to traces page
        await page.waitForURL(/.*\/traces\/.*/);
      }
    }
  });

  test('should expand input/output sections in detail modal', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Check if Input/Output section exists
      const inputOutputSection = page.locator('text=INPUT / OUTPUT');

      if (await inputOutputSection.isVisible()) {
        // Click "Expand All"
        const expandAllButton = page.locator('button:has-text("Expand All")');
        await expandAllButton.click();
        await page.waitForTimeout(300);

        // Input and Output data should be visible
        const inputSection = page.locator('button:has-text("Input Data")');
        const outputSection = page.locator('button:has-text("Output Data")');

        // At least one should be visible
        const inputVisible = await inputSection.isVisible();
        const outputVisible = await outputSection.isVisible();
        expect(inputVisible || outputVisible).toBeTruthy();
      }
    }
  });

  test('should close detail modal when clicking close button', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Click Close button in footer
      const closeButton = page.locator('button:has-text("Close")').last();
      await closeButton.click();
      await page.waitForTimeout(300);

      // Modal should be closed (score section should not be visible)
      await expect(page.locator('text=SCORE')).not.toBeVisible();
    }
  });

  test('should close detail modal when clicking outside', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });
    await page.waitForTimeout(1000);

    const rowCount = await page.locator('tbody tr').count();

    if (rowCount > 0) {
      await page.locator('tbody tr').first().click();
      await page.waitForTimeout(500);

      // Click on backdrop (outside modal)
      await page.locator('.fixed.inset-0').first().click({ position: { x: 10, y: 10 } });
      await page.waitForTimeout(300);

      // Modal should be closed
      await expect(page.locator('text=SCORE')).not.toBeVisible();
    }
  });

  // ==================== ORIGINAL CATALOG TESTS ====================

  test('should switch to catalog tab', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Click Browse Catalog tab
    await page.locator('button:has-text("Browse Catalog")').click();

    // Verify catalog content is visible
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
  });

  test('should filter evaluations by source', async ({ page }) => {
    await page.goto('http://localhost:3000/evaluations');
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Navigate to catalog
    await page.locator('button:has-text("Browse Catalog")').click();
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });

    // Click on different source filters
    await page.locator('button:has-text("Vendor")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Custom")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("PromptForge")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("LLM Judge")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("All Sources")').click();
    await page.waitForTimeout(500);
  });

  test('should search evaluations', async ({ page }) => {
    await page.goto('http://localhost:3000/evaluations');
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Navigate to catalog
    await page.locator('button:has-text("Browse Catalog")').click();
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });

    // Type in search
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('groundedness');
    await page.waitForTimeout(500);

    // Clear search
    await searchBox.fill('');
    await page.waitForTimeout(500);
  });

  test('should select and deselect evaluations', async ({ page }) => {
    await page.goto('http://localhost:3000/evaluations');
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Navigate to catalog
    await page.locator('button:has-text("Browse Catalog")').click();
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });

    // Wait for evaluations to load
    await page.waitForTimeout(1000);

    // Check if evaluation cards exist
    const evaluationCards = page.locator('[class*="border"][class*="rounded"]').filter({
      has: page.locator('[class*="w-5"][class*="h-5"]') // checkbox
    });

    const cardCount = await evaluationCards.count();

    if (cardCount > 0) {
      // Click first card to select
      await evaluationCards.first().click();
      await page.waitForTimeout(300);

      // Verify selection badge appears
      await expect(page.locator('text=/\\d+ selected/')).toBeVisible({ timeout: 2000 });

      // Click again to deselect
      await evaluationCards.first().click();
      await page.waitForTimeout(300);
    }
  });

  test('should show continue button when evaluations selected', async ({ page }) => {
    await page.goto('http://localhost:3000/evaluations');
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Navigate to catalog
    await page.locator('button:has-text("Browse Catalog")').click();
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });

    await page.waitForTimeout(1000);

    const evaluationCards = page.locator('[class*="border"][class*="rounded"]').filter({
      has: page.locator('[class*="w-5"][class*="h-5"]')
    });

    const cardCount = await evaluationCards.count();

    if (cardCount > 0) {
      // Select an evaluation
      await evaluationCards.first().click();
      await page.waitForTimeout(300);

      // Verify continue button appears
      const continueButton = page.locator('button:has-text("Continue with")');
      await expect(continueButton).toBeVisible({ timeout: 2000 });
    }
  });

  test('should display Run Evaluation button', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Evaluations")', { timeout: 10000 });

    // Check for Run Evaluation button
    const runButton = page.locator('button:has-text("Run Evaluation")');
    await expect(runButton).toBeVisible();

    // Click it to navigate to catalog
    await runButton.click();

    // Should navigate to catalog tab
    await expect(page.locator('h2:has-text("Evaluation Catalog")')).toBeVisible({ timeout: 5000 });
  });
});
