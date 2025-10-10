import { test, expect } from '@playwright/test';

/**
 * API Integration Tests for Model Provider Endpoints
 *
 * Tests all model provider API endpoints:
 * - GET /api/v1/model-providers
 * - POST /api/v1/model-providers
 * - GET /api/v1/model-providers/{id}
 * - PUT /api/v1/model-providers/{id}
 * - DELETE /api/v1/model-providers/{id}
 * - POST /api/v1/model-providers/{id}/test
 * - GET /api/v1/model-providers/metadata
 * - GET /api/v1/models
 * - GET /api/v1/models/analytics
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Test credentials (should match seed data)
const TEST_USER = {
  email: 'admin@promptforge.com',
  password: 'admin123',
};

let authToken: string;
let testProviderId: string;

test.describe('Model Provider API Tests', () => {
  test.beforeAll(async ({ request }) => {
    // Login and get auth token
    const response = await request.post(`${API_BASE_URL}/api/v1/auth/login`, {
      data: TEST_USER,
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    authToken = data.access_token;

    expect(authToken).toBeTruthy();
  });

  test.describe('GET /api/v1/model-providers/metadata', () => {
    test('should return list of available provider metadata', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers/metadata`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // Should have provider metadata array
      expect(Array.isArray(data.metadata)).toBeTruthy();
      expect(data.total).toBeGreaterThanOrEqual(0);

      // If metadata exists, check structure
      if (data.metadata.length > 0) {
        const provider = data.metadata[0];

        expect(provider).toHaveProperty('provider_name');
        expect(provider).toHaveProperty('provider_type');
        expect(provider).toHaveProperty('display_name');
        expect(provider).toHaveProperty('supported_models');
        expect(provider).toHaveProperty('capabilities');
        expect(provider).toHaveProperty('required_config_fields');
      }
    });

    test('should filter metadata by provider name', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers/metadata?provider_name=openai`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // All returned providers should be OpenAI
      if (data.metadata.length > 0) {
        data.metadata.forEach((provider: any) => {
          expect(provider.provider_name.toLowerCase()).toBe('openai');
        });
      }
    });

    test('should require authentication', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers/metadata`);

      expect(response.status()).toBe(401);
    });
  });

  test.describe('GET /api/v1/model-providers', () => {
    test('should return list of configured providers', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      expect(Array.isArray(data.providers)).toBeTruthy();
      expect(typeof data.total).toBe('number');
    });

    test('should filter by provider name', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers?provider_name=openai`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      if (data.providers.length > 0) {
        data.providers.forEach((provider: any) => {
          expect(provider.provider_name.toLowerCase()).toBe('openai');
        });
      }
    });

    test('should filter by active status', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers?is_active=true`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      if (data.providers.length > 0) {
        data.providers.forEach((provider: any) => {
          expect(provider.is_active).toBe(true);
        });
      }
    });
  });

  test.describe('POST /api/v1/model-providers', () => {
    test('should create new provider configuration', async ({ request }) => {
      const newProvider = {
        name: `Test OpenAI Config ${Date.now()}`,
        provider_name: 'openai',
        provider_type: 'llm',
        api_key: 'sk-test-key-123456789',
        config: {
          organization_id: 'org-test',
        },
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: newProvider,
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // Save ID for later tests
      testProviderId = data.id;

      expect(data.name).toBe(newProvider.name);
      expect(data.provider_name).toBe(newProvider.provider_name);
      expect(data.is_active).toBe(true);

      // API key should be masked
      expect(data.api_key_masked).toContain('...');
      expect(data.api_key_masked).not.toBe(newProvider.api_key);
    });

    test('should validate required fields', async ({ request }) => {
      const invalidProvider = {
        name: 'Invalid Config',
        // Missing provider_name, provider_type, api_key
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: invalidProvider,
      });

      expect(response.status()).toBe(422); // Validation error
    });

    test('should prevent duplicate provider names', async ({ request }) => {
      const providerName = `Duplicate Test ${Date.now()}`;

      // Create first provider
      await request.post(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: {
          name: providerName,
          provider_name: 'openai',
          provider_type: 'llm',
          api_key: 'sk-test-key-1',
        },
      });

      // Try to create duplicate
      const response = await request.post(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: {
          name: providerName,
          provider_name: 'openai',
          provider_type: 'llm',
          api_key: 'sk-test-key-2',
        },
      });

      expect(response.status()).toBe(400); // Bad request
    });
  });

  test.describe('GET /api/v1/model-providers/{id}', () => {
    test('should return provider details', async ({ request }) => {
      // Skip if no test provider created
      if (!testProviderId) {
        test.skip();
        return;
      }

      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      expect(data.id).toBe(testProviderId);
      expect(data).toHaveProperty('name');
      expect(data).toHaveProperty('provider_name');
      expect(data).toHaveProperty('api_key_masked');
    });

    test('should return 404 for non-existent provider', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers/00000000-0000-0000-0000-000000000000`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.status()).toBe(404);
    });
  });

  test.describe('PUT /api/v1/model-providers/{id}', () => {
    test('should update provider configuration', async ({ request }) => {
      if (!testProviderId) {
        test.skip();
        return;
      }

      const updates = {
        name: `Updated Test Config ${Date.now()}`,
        config: {
          organization_id: 'org-updated',
        },
      };

      const response = await request.put(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: updates,
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      expect(data.name).toBe(updates.name);
    });

    test('should update API key separately', async ({ request }) => {
      if (!testProviderId) {
        test.skip();
        return;
      }

      const response = await request.put(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: {
          api_key: 'sk-new-test-key-987654321',
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // Should show new masked key
      expect(data.api_key_masked).toBeTruthy();
    });
  });

  test.describe('POST /api/v1/model-providers/{id}/test', () => {
    test('should test provider connection', async ({ request }) => {
      if (!testProviderId) {
        test.skip();
        return;
      }

      const response = await request.post(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}/test`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      // Response should be ok or return specific error
      const data = await response.json();

      expect(data).toHaveProperty('success');
      expect(typeof data.success).toBe('boolean');

      if (!data.success) {
        expect(data).toHaveProperty('error');
      }
    });
  });

  test.describe('GET /api/v1/models', () => {
    test('should return list of available models', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      expect(data).toHaveProperty('models');
      expect(data).toHaveProperty('total');
      expect(Array.isArray(data.models)).toBeTruthy();
    });

    test('should filter by provider name', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/?provider_name=openai`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      if (data.models.length > 0) {
        data.models.forEach((model: any) => {
          expect(model.provider_name.toLowerCase()).toBe('openai');
        });
      }
    });

    test('should show only available models by default', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      if (data.models.length > 0) {
        data.models.forEach((model: any) => {
          expect(model.is_available).toBe(true);
        });
      }
    });
  });

  test.describe('GET /api/v1/models/analytics', () => {
    test('should return analytics data', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/analytics`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // Check structure
      expect(data).toHaveProperty('analytics');
      expect(data).toHaveProperty('by_model');
      expect(data).toHaveProperty('total');

      // Check analytics fields
      expect(data.analytics).toHaveProperty('total_models_available');
      expect(data.analytics).toHaveProperty('total_requests_7d');
      expect(data.analytics).toHaveProperty('total_cost_7d');
      expect(data.analytics).toHaveProperty('avg_success_rate');
    });

    test('should accept days parameter', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/analytics?days=30`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();
      expect(data.analytics).toHaveProperty('total_requests_7d'); // Field name doesn't change
    });

    test('should validate days parameter range', async ({ request }) => {
      // Test lower bound
      const response1 = await request.get(`${API_BASE_URL}/api/v1/models/analytics?days=0`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response1.status()).toBe(422);

      // Test upper bound
      const response2 = await request.get(`${API_BASE_URL}/api/v1/models/analytics?days=100`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response2.status()).toBe(422);
    });

    test('should return empty data if no traces exist', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/models/analytics?days=1`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      // Should still have valid structure
      expect(Array.isArray(data.by_model)).toBeTruthy();
      expect(typeof data.total).toBe('number');
    });
  });

  test.describe('DELETE /api/v1/model-providers/{id}', () => {
    test('should delete provider configuration', async ({ request }) => {
      if (!testProviderId) {
        test.skip();
        return;
      }

      const response = await request.delete(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.status()).toBe(204);

      // Verify deletion
      const getResponse = await request.get(`${API_BASE_URL}/api/v1/model-providers/${testProviderId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(getResponse.status()).toBe(404);
    });
  });

  test.describe('Authorization & Security', () => {
    test('should enforce organization scoping', async ({ request }) => {
      // All endpoints should only return data for current user's organization
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      // All providers should belong to same organization
      const data = await response.json();

      if (data.providers.length > 0) {
        const firstOrgId = data.providers[0].organization_id;

        data.providers.forEach((provider: any) => {
          expect(provider.organization_id).toBe(firstOrgId);
        });
      }
    });

    test('should not expose raw API keys', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/model-providers`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.ok()).toBeTruthy();

      const data = await response.json();

      if (data.providers.length > 0) {
        data.providers.forEach((provider: any) => {
          // Should not have api_key field
          expect(provider).not.toHaveProperty('api_key');

          // Should have masked version
          expect(provider).toHaveProperty('api_key_masked');
        });
      }
    });

    test('should require valid token for all endpoints', async ({ request }) => {
      const endpoints = [
        '/api/v1/model-providers',
        '/api/v1/model-providers/metadata',
        '/api/v1/models/',
        '/api/v1/models/analytics',
      ];

      for (const endpoint of endpoints) {
        const response = await request.get(`${API_BASE_URL}${endpoint}`);
        expect(response.status()).toBe(401);
      }
    });
  });
});
