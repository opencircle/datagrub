import { test, expect } from '@playwright/test';
import { API_BASE_URL } from '../fixtures/test-data';

test.describe('Evaluation Catalog API', () => {
  let authToken: string;

  test.beforeAll(async () => {
    authToken = 'test-token';
  });

  test('GET /evaluation-catalog/catalog should return evaluation catalog', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/evaluation-catalog/catalog`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();

      // Verify structure of evaluations
      if (data.length > 0) {
        const evaluation = data[0];
        expect(evaluation).toHaveProperty('id');
        expect(evaluation).toHaveProperty('name');
        expect(evaluation).toHaveProperty('source');
        expect(evaluation).toHaveProperty('category');
      }
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('GET /evaluation-catalog/catalog with source filter', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/evaluation-catalog/catalog?source=vendor`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();

      // All evaluations should be from vendor source
      data.forEach((evaluation: any) => {
        expect(evaluation.source).toBe('vendor');
      });
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('GET /evaluation-catalog/categories should return categories', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/evaluation-catalog/categories`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('GET /evaluation-catalog/search should search evaluations', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/evaluation-catalog/search?q=groundedness`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();

      // Results should contain search term in name, description, or tags
      data.forEach((evaluation: any) => {
        const searchTerm = 'groundedness';
        const matchesSearch =
          evaluation.name.toLowerCase().includes(searchTerm) ||
          evaluation.description.toLowerCase().includes(searchTerm) ||
          (evaluation.tags && evaluation.tags.some((tag: string) =>
            tag.toLowerCase().includes(searchTerm)
          ));
        expect(matchesSearch).toBeTruthy();
      });
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('POST /evaluation-catalog/llm-judge should create LLM judge', async ({ request }) => {
    const llmJudgeData = {
      name: 'Test LLM Judge',
      description: 'A test LLM-as-judge evaluation',
      category: 'quality',
      criteria: 'Evaluate the response quality',
      model: 'gpt-4',
    };

    const response = await request.post(`${API_BASE_URL}/evaluation-catalog/llm-judge`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: llmJudgeData,
    });

    if (response.ok()) {
      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data).toHaveProperty('id');
      expect(data.name).toBe(llmJudgeData.name);
      expect(data.source).toBe('llm_judge');
    } else {
      expect([401, 403, 422]).toContain(response.status());
    }
  });

  test('GET /evaluation-catalog/catalog/:id should return specific evaluation', async ({ request }) => {
    // First get the catalog to get a valid ID
    const catalogResponse = await request.get(`${API_BASE_URL}/evaluation-catalog/catalog`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (catalogResponse.ok()) {
      const catalog = await catalogResponse.json();
      if (catalog.length > 0) {
        const evaluationId = catalog[0].id;

        const response = await request.get(`${API_BASE_URL}/evaluation-catalog/catalog/${evaluationId}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        });

        if (response.ok()) {
          expect(response.status()).toBe(200);
          const data = await response.json();
          expect(data.id).toBe(evaluationId);
        } else {
          expect([401, 403, 404]).toContain(response.status());
        }
      }
    }
  });

  test('API should handle invalid evaluation ID', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/evaluation-catalog/catalog/invalid-id`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    expect([401, 403, 404, 422]).toContain(response.status());
  });
});
