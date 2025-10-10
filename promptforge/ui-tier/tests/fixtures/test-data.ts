/**
 * Test data fixtures for PromptForge tests
 */

export const testUser = {
  email: 'test@promptforge.com',
  password: 'test123',
  organizationId: 'test-org-id',
};

export const testProject = {
  name: 'Test Project',
  description: 'A test project for automated testing',
  status: 'active' as const,
};

export const testPrompt = {
  name: 'Test Prompt',
  description: 'A test prompt for automated testing',
  systemPrompt: 'You are a helpful assistant.',
  userPrompt: 'Please help me with {task}',
  intent: 'assistance',
  tone: 'professional' as const,
  variables: [
    {
      name: 'task',
      type: 'string' as const,
      required: true,
      description: 'The task to help with',
    },
  ],
  fewShotExamples: [],
};

export const testEvaluationConfig = {
  evaluationIds: ['test-eval-1', 'test-eval-2'],
  inputData: { query: 'What is AI?' },
  outputData: { response: 'AI stands for Artificial Intelligence.' },
};

export const API_BASE_URL = process.env.API_URL || 'http://localhost:8000/api/v1';
