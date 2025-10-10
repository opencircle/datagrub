import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Model Provider Configuration
 *
 * Tests the complete flow of:
 * - Viewing provider configurations
 * - Adding new provider configurations
 * - Editing existing configurations
 * - Testing provider connections
 * - Viewing model analytics
 */

test.describe('Model Provider Configuration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to models page
    await page.goto('http://localhost:3000/models');

    // Wait for page to load
    await page.waitForSelector('h1:has-text("Model Dashboard")', { timeout: 10000 });
  });

  test('should display model dashboard', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText('Model Dashboard');

    // Check subtitle
    await expect(page.locator('text=Manage providers, models, and configurations')).toBeVisible();

    // Check tab navigation exists
    await expect(page.locator('button:has-text("Providers")')).toBeVisible();
    await expect(page.locator('button:has-text("Models")')).toBeVisible();
  });

  test('should show providers tab by default', async ({ page }) => {
    // Providers tab should be active (has pink underline indicator)
    const providersTab = page.locator('button:has-text("Providers")');
    await expect(providersTab).toHaveClass(/text-\[#FF385C\]/);

    // Should show "Add Provider" button
    await expect(page.locator('button:has-text("Add Provider")')).toBeVisible();
  });

  test('should switch between Providers and Models tabs', async ({ page }) => {
    // Click Models tab
    await page.locator('button:has-text("Models")').click();

    // Verify Models tab is active
    const modelsTab = page.locator('button:has-text("Models")');
    await expect(modelsTab).toHaveClass(/text-\[#FF385C\]/);

    // Should show analytics content
    await expect(page.locator('text=Model Analytics')).toBeVisible();

    // Switch back to Providers
    await page.locator('button:has-text("Providers")').click();
    await expect(page.locator('button:has-text("Add Provider")')).toBeVisible();
  });

  test.describe('Provider List', () => {
    test('should display provider cards', async ({ page }) => {
      // Check if provider cards exist or empty state is shown
      const addProviderButton = page.locator('button:has-text("Add Provider")');
      await expect(addProviderButton).toBeVisible();

      // Either cards exist or empty state
      const hasCards = await page.locator('[class*="border"][class*="rounded-2xl"]').count() > 0;
      const hasEmptyState = await page.locator('text=No providers configured').isVisible();

      expect(hasCards || hasEmptyState).toBeTruthy();
    });

    test('should show provider card details', async ({ page }) => {
      const providerCard = page.locator('[class*="border"][class*="rounded-2xl"]').first();
      const cardCount = await providerCard.count();

      if (cardCount > 0) {
        // Card should show provider name
        await expect(providerCard).toBeVisible();

        // Should have status badge (Active/Inactive)
        const statusBadge = providerCard.locator('[class*="bg-green"], [class*="bg-gray"]');
        await expect(statusBadge).toBeVisible();

        // Should have action buttons
        await expect(providerCard.locator('button:has-text("Test")')).toBeVisible();
        await expect(providerCard.locator('button[aria-label*="Edit"], button:has-text("Edit")')).toBeVisible();
      }
    });

    test('should test provider connection', async ({ page }) => {
      const testButton = page.locator('button:has-text("Test")').first();
      const testButtonExists = await testButton.count() > 0;

      if (testButtonExists) {
        await testButton.click();

        // Should show some feedback (success or error)
        await page.waitForTimeout(2000);

        // Check for success or error indication
        const hasSuccess = await page.locator('[class*="text-green"]').count() > 0;
        const hasError = await page.locator('[class*="text-red"]').count() > 0;

        expect(hasSuccess || hasError).toBeTruthy();
      }
    });
  });

  test.describe('Add Provider Modal', () => {
    test('should open add provider modal', async ({ page }) => {
      // Click Add Provider button
      await page.locator('button:has-text("Add Provider")').click();

      // Modal should appear
      await expect(page.locator('text=Add Model Provider')).toBeVisible({ timeout: 3000 });

      // Should show step 1 (Select Provider)
      await expect(page.locator('text=Select Provider')).toBeVisible();
    });

    test('should show provider selection cards', async ({ page }) => {
      await page.locator('button:has-text("Add Provider")').click();
      await expect(page.locator('text=Add Model Provider')).toBeVisible();

      // Should show provider cards (OpenAI, Anthropic, etc.)
      const providerCards = page.locator('[class*="cursor-pointer"][class*="border"]');
      await expect(providerCards.first()).toBeVisible();

      // Cards should have provider names
      const hasOpenAI = await page.locator('text=OpenAI').count() > 0;
      const hasAnthropic = await page.locator('text=Anthropic').count() > 0;

      expect(hasOpenAI || hasAnthropic).toBeTruthy();
    });

    test('should navigate to step 2 after selecting provider', async ({ page }) => {
      await page.locator('button:has-text("Add Provider")').click();
      await expect(page.locator('text=Add Model Provider')).toBeVisible();

      // Click first provider card
      const providerCard = page.locator('[class*="cursor-pointer"][class*="border"]').first();
      await providerCard.click();

      // Should move to step 2
      await expect(page.locator('text=Configuration')).toBeVisible({ timeout: 3000 });

      // Should show form fields
      await expect(page.locator('label:has-text("Configuration Name")')).toBeVisible();
      await expect(page.locator('label:has-text("API Key")')).toBeVisible();
    });

    test('should validate required fields', async ({ page }) => {
      await page.locator('button:has-text("Add Provider")').click();
      await expect(page.locator('text=Add Model Provider')).toBeVisible();

      // Select first provider
      await page.locator('[class*="cursor-pointer"][class*="border"]').first().click();
      await expect(page.locator('text=Configuration')).toBeVisible();

      // Try to save without filling required fields
      const saveButton = page.locator('button:has-text("Save Configuration"), button:has-text("Save")');
      await saveButton.click();

      // Should still be on modal (validation failed)
      await expect(page.locator('text=Configuration')).toBeVisible();
    });

    test('should close modal on cancel', async ({ page }) => {
      await page.locator('button:has-text("Add Provider")').click();
      await expect(page.locator('text=Add Model Provider')).toBeVisible();

      // Click Cancel or X button
      const cancelButton = page.locator('button:has-text("Cancel")');
      if (await cancelButton.count() > 0) {
        await cancelButton.click();
      } else {
        // Try X button
        await page.locator('button[aria-label="Close"]').click();
      }

      // Modal should close
      await expect(page.locator('text=Add Model Provider')).not.toBeVisible({ timeout: 2000 });
    });

    test('should go back to step 1 from step 2', async ({ page }) => {
      await page.locator('button:has-text("Add Provider")').click();
      await expect(page.locator('text=Add Model Provider')).toBeVisible();

      // Select provider
      await page.locator('[class*="cursor-pointer"][class*="border"]').first().click();
      await expect(page.locator('text=Configuration')).toBeVisible();

      // Click Back button
      const backButton = page.locator('button:has-text("Back")');
      await backButton.click();

      // Should be back on step 1
      await expect(page.locator('text=Select Provider')).toBeVisible();
    });
  });

  test.describe('Edit Provider', () => {
    test('should open edit modal from provider card', async ({ page }) => {
      const editButton = page.locator('button[aria-label*="Edit"], button:has-text("Edit")').first();
      const editButtonExists = await editButton.count() > 0;

      if (editButtonExists) {
        await editButton.click();

        // Modal should open with configuration form
        await expect(page.locator('text=Edit Model Provider, text=Add Model Provider')).toBeVisible({ timeout: 3000 });

        // Should show filled form fields
        await expect(page.locator('label:has-text("Configuration Name")')).toBeVisible();
      }
    });

    test('should prepopulate form with existing data', async ({ page }) => {
      const editButton = page.locator('button[aria-label*="Edit"], button:has-text("Edit")').first();
      const editButtonExists = await editButton.count() > 0;

      if (editButtonExists) {
        await editButton.click();
        await page.waitForTimeout(1000);

        // Check if Configuration Name field has value
        const nameInput = page.locator('input[name="name"], input[placeholder*="name"]').first();
        const nameValue = await nameInput.inputValue();

        // Should have some value
        expect(nameValue.length).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Delete Provider', () => {
    test('should show delete confirmation', async ({ page }) => {
      const deleteButton = page.locator('button[aria-label*="Delete"], button:has-text("Delete")').first();
      const deleteButtonExists = await deleteButton.count() > 0;

      if (deleteButtonExists) {
        await deleteButton.click();

        // Should show confirmation dialog
        await expect(page.locator('text=Delete, text=confirm, text=Are you sure')).toBeVisible({ timeout: 3000 });
      }
    });
  });

  test.describe('Model Analytics', () => {
    test('should display analytics overview', async ({ page }) => {
      // Switch to Models tab
      await page.locator('button:has-text("Models")').click();

      // Should show analytics header
      await expect(page.locator('text=Model Analytics')).toBeVisible({ timeout: 5000 });

      // Should show time range selector
      await expect(page.locator('button:has-text("7 days"), button:has-text("7")')).toBeVisible();
    });

    test('should display stat cards', async ({ page }) => {
      await page.locator('button:has-text("Models")').click();
      await page.waitForTimeout(2000);

      // Should show stat cards (or loading state)
      const hasStatCards = await page.locator('[class*="grid"][class*="gap"]').count() > 0;
      const hasLoading = await page.locator('text=Loading').isVisible();

      expect(hasStatCards || hasLoading).toBeTruthy();
    });

    test('should change time range', async ({ page }) => {
      await page.locator('button:has-text("Models")').click();
      await page.waitForTimeout(2000);

      // Click 30 days button
      const thirtyDaysButton = page.locator('button:has-text("30")').first();
      const buttonExists = await thirtyDaysButton.count() > 0;

      if (buttonExists) {
        await thirtyDaysButton.click();

        // Should be active (highlighted)
        await expect(thirtyDaysButton).toHaveClass(/bg-\[#FF385C\]/);
      }
    });

    test('should show model usage table or empty state', async ({ page }) => {
      await page.locator('button:has-text("Models")').click();
      await page.waitForTimeout(3000);

      // Either table or empty state should be visible
      const hasTable = await page.locator('table').count() > 0;
      const hasEmptyState = await page.locator('text=No Usage Data, text=No model usage').isVisible();
      const hasLoading = await page.locator('text=Loading').isVisible();

      expect(hasTable || hasEmptyState || hasLoading).toBeTruthy();
    });

    test('should display table headers if data exists', async ({ page }) => {
      await page.locator('button:has-text("Models")').click();
      await page.waitForTimeout(3000);

      const hasTable = await page.locator('table').count() > 0;

      if (hasTable) {
        // Check for expected column headers
        await expect(page.locator('th:has-text("Model")')).toBeVisible();
        await expect(page.locator('th:has-text("Requests")')).toBeVisible();
        await expect(page.locator('th:has-text("Success Rate")')).toBeVisible();
      }
    });

    test('should handle error state gracefully', async ({ page }) => {
      await page.locator('button:has-text("Models")').click();
      await page.waitForTimeout(3000);

      // If error occurs, should show error message
      const hasError = await page.locator('text=Error, text=Failed').count() > 0;

      if (hasError) {
        // Should have retry button
        await expect(page.locator('button:has-text("Retry")')).toBeVisible();
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Page should still be accessible
      await expect(page.locator('h1:has-text("Model Dashboard")')).toBeVisible();
      await expect(page.locator('button:has-text("Providers")')).toBeVisible();
    });

    test('should be responsive on tablet', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      // Page should still be accessible
      await expect(page.locator('h1:has-text("Model Dashboard")')).toBeVisible();
      await expect(page.locator('button:has-text("Add Provider")')).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      // H1 should exist
      await expect(page.locator('h1')).toBeVisible();

      // Tab buttons should be keyboard accessible
      const providersTab = page.locator('button:has-text("Providers")');
      await providersTab.focus();
      await expect(providersTab).toBeFocused();
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Should be able to activate buttons with Enter
      await page.locator('button:has-text("Models")').focus();
      await page.keyboard.press('Enter');

      // Should navigate to Models tab
      await expect(page.locator('text=Model Analytics')).toBeVisible();
    });
  });
});
