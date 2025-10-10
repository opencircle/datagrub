/**
 * Model Provider API Service
 *
 * Handles all API calls for model provider configuration management
 */
import {
  ProviderMetadataListResponse,
  ModelProviderConfigListResponse,
  ModelProviderConfig,
  ModelProviderConfigCreate,
  ModelProviderConfigUpdate,
  ProviderTestResponse,
  ProviderFilters,
} from '../types/provider';

// Use process.env which is defined by webpack DefinePlugin
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

/**
 * Get auth token from localStorage
 * The shell uses 'promptforge_access_token' as the key
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('promptforge_access_token');
};

/**
 * Build headers with authentication
 */
const buildHeaders = (): HeadersInit => {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Handle API errors
 */
const handleError = async (response: Response): Promise<never> => {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

  try {
    const errorData = await response.json();
    errorMessage = errorData.detail || errorData.message || errorMessage;
  } catch {
    // Response body not JSON
  }

  throw new Error(errorMessage);
};

/**
 * Get catalog of available providers with metadata
 * Public endpoint, no auth required
 */
export const getProviderCatalog = async (
  providerType?: string,
  isActive: boolean = true
): Promise<ProviderMetadataListResponse> => {
  const params = new URLSearchParams();
  if (providerType) params.append('provider_type', providerType);
  params.append('is_active', String(isActive));
  // Add timestamp to prevent browser caching
  params.append('_t', Date.now().toString());

  const url = `${API_V1}/model-providers/catalog?${params.toString()}`;
  const response = await fetch(url, {
    cache: 'no-store', // Prevent browser from caching the response
  });

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * Create new provider configuration
 * Requires admin role
 */
export const createProviderConfig = async (
  config: ModelProviderConfigCreate
): Promise<ModelProviderConfig> => {
  const response = await fetch(`${API_V1}/model-providers/configs`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(config),
  });

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * List provider configurations for current organization
 */
export const listProviderConfigs = async (
  filters?: ProviderFilters
): Promise<ModelProviderConfigListResponse> => {
  const params = new URLSearchParams();

  if (filters?.provider_type) {
    params.append('provider_type', filters.provider_type);
  }
  if (filters?.is_active !== undefined) {
    params.append('is_active', String(filters.is_active));
  }
  if (filters?.project_id) {
    params.append('project_id', filters.project_id);
  }

  const url = `${API_V1}/model-providers/configs?${params.toString()}`;
  const response = await fetch(url, {
    headers: buildHeaders(),
  });

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * Get single provider configuration by ID
 */
export const getProviderConfig = async (
  configId: string
): Promise<ModelProviderConfig> => {
  const response = await fetch(`${API_V1}/model-providers/configs/${configId}`, {
    headers: buildHeaders(),
  });

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * Update provider configuration
 * Requires admin role
 */
export const updateProviderConfig = async (
  configId: string,
  update: ModelProviderConfigUpdate
): Promise<ModelProviderConfig> => {
  const response = await fetch(`${API_V1}/model-providers/configs/${configId}`, {
    method: 'PUT',
    headers: buildHeaders(),
    body: JSON.stringify(update),
  });

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * Delete provider configuration (soft delete)
 * Requires admin role
 */
export const deleteProviderConfig = async (configId: string): Promise<void> => {
  const response = await fetch(`${API_V1}/model-providers/configs/${configId}`, {
    method: 'DELETE',
    headers: buildHeaders(),
  });

  if (!response.ok) {
    await handleError(response);
  }
};

/**
 * Test provider configuration connection
 */
export const testProviderConfig = async (
  configId: string
): Promise<ProviderTestResponse> => {
  const response = await fetch(
    `${API_V1}/model-providers/configs/${configId}/test`,
    {
      method: 'POST',
      headers: buildHeaders(),
    }
  );

  if (!response.ok) {
    await handleError(response);
  }

  return response.json();
};

/**
 * Get provider metadata by name
 */
export const getProviderMetadata = async (
  providerName: string,
  providerType: string = 'llm'
): Promise<ProviderMetadataListResponse> => {
  const params = new URLSearchParams();
  params.append('provider_type', providerType);
  params.append('is_active', 'true');

  const url = `${API_V1}/model-providers/catalog?${params.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    await handleError(response);
  }

  const data: ProviderMetadataListResponse = await response.json();

  // Filter to specific provider
  const filteredProviders = data.providers.filter(
    (p) => p.provider_name === providerName
  );

  return {
    providers: filteredProviders,
    total: filteredProviders.length,
  };
};
