import { test, expect } from '@playwright/test';
import { testProject, testPrompt } from '../fixtures/test-data';

test.describe('Projects Module', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to projects page
    await page.goto('http://localhost:3000/projects');
  });

  test('should display projects list', async ({ page }) => {
    // Wait for projects to load
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Check if the page title is visible
    await expect(page.locator('h1')).toContainText('Projects');

    // Check if search box is present
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
  });

  test('should search projects', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Type in search box
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('test');

    // Verify search is working (debouncing may apply)
    await page.waitForTimeout(500);
  });

  test('should open prompt builder modal', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Click "New Prompt" button
    const newPromptButton = page.locator('button:has-text("New Prompt")');
    await newPromptButton.click();

    // Verify modal opens
    await expect(page.locator('text=Create New Prompt')).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to project detail', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Click on first project card (if exists)
    const projectCard = page.locator('[class*="border"][class*="rounded"]').first();
    const projectCardExists = await projectCard.count() > 0;

    if (projectCardExists) {
      await projectCard.click();

      // Verify navigation to project detail
      await expect(page).toHaveURL(/\/projects\/.+/, { timeout: 5000 });
      await expect(page.locator('button:has-text("Back to Projects")')).toBeVisible();
    }
  });

  test('should display prompt builder form fields', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Open prompt builder
    await page.locator('button:has-text("New Prompt")').click();
    await expect(page.locator('text=Create New Prompt')).toBeVisible();

    // Check for basic info tab fields
    await expect(page.locator('label:has-text("Prompt Name")')).toBeVisible();
    await expect(page.locator('label:has-text("Description")')).toBeVisible();
    await expect(page.locator('label:has-text("Intent")')).toBeVisible();
    await expect(page.locator('label:has-text("Tone")')).toBeVisible();

    // Navigate through tabs
    await page.locator('button:has-text("System Prompt")').click();
    await expect(page.locator('label:has-text("System Prompt")')).toBeVisible();

    await page.locator('button:has-text("User Prompt")').click();
    await expect(page.locator('label:has-text("User Prompt Template")')).toBeVisible();

    await page.locator('button:has-text("Variables")').click();
    await expect(page.locator('button:has-text("Add Variable")')).toBeVisible();

    await page.locator('button:has-text("Few-Shot Examples")').click();
    await expect(page.locator('button:has-text("Add Example")')).toBeVisible();
  });

  test('should validate required fields in prompt builder', async ({ page }) => {
    await page.waitForSelector('h1:has-text("Projects")', { timeout: 10000 });

    // Open prompt builder
    await page.locator('button:has-text("New Prompt")').click();
    await expect(page.locator('text=Create New Prompt')).toBeVisible();

    // Try to create without filling required fields
    // Navigate to last tab
    await page.locator('button:has-text("Few-Shot Examples")').click();

    // Click create button
    await page.locator('button:has-text("Create Prompt")').click();

    // Verification: Should still be on the modal (validation failed)
    await expect(page.locator('text=Create New Prompt')).toBeVisible();
  });
});
