/**
 * Model Provider Configuration Service
 *
 * Service for managing organization-scoped API keys and provider configurations
 * Integrates with the new database-stored API key system
 */

import { apiClient } from './apiClient';

export type ProviderName = 'openai' | 'anthropic' | 'cohere' | 'google' | 'huggingface';
export type ProviderType = 'llm' | 'embedding' | 'completion';

export interface ModelProviderConfig {
  id: string;
  organization_id: string;
  project_id: string | null;
  provider_name: ProviderName;
  provider_type: ProviderType;
  display_name: string;
  is_active: boolean;
  is_default: boolean;
  last_used_at: string | null;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface ModelProviderMetadata {
  provider_name: ProviderName;
  display_name: string;
  description: string;
  supported_types: ProviderType[];
  config_schema: Record<string, any>;
  requires_api_key: boolean;
}

export interface CreateProviderConfigRequest {
  provider_name: ProviderName;
  provider_type: ProviderType;
  api_key: string;
  display_name: string;
  project_id?: string;
  config?: Record<string, any>;
  is_default?: boolean;
}

export interface UpdateProviderConfigRequest {
  api_key?: string;
  display_name?: string;
  config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface TestProviderConfigRequest {
  model?: string;
  test_prompt?: string;
}

export interface TestProviderConfigResponse {
  success: boolean;
  message: string;
  details?: Record<string, any>;
}

export const modelProviderConfigService = {
  /**
   * Get provider catalog (available providers)
   */
  async getProviderCatalog(): Promise<ModelProviderMetadata[]> {
    return apiClient.get<ModelProviderMetadata[]>('/model-providers/catalog');
  },

  /**
   * Get organization's provider configurations
   */
  async getConfigs(params?: {
    provider_name?: ProviderName;
    provider_type?: ProviderType;
    is_active?: boolean;
    project_id?: string;
  }): Promise<ModelProviderConfig[]> {
    return apiClient.get<ModelProviderConfig[]>('/model-providers/configs', { params });
  },

  /**
   * Get specific provider configuration
   */
  async getConfig(id: string): Promise<ModelProviderConfig> {
    return apiClient.get<ModelProviderConfig>(`/model-providers/configs/${id}`);
  },

  /**
   * Create new provider configuration
   */
  async createConfig(data: CreateProviderConfigRequest): Promise<ModelProviderConfig> {
    return apiClient.post<ModelProviderConfig>('/model-providers/configs', data);
  },

  /**
   * Update provider configuration
   */
  async updateConfig(id: string, data: UpdateProviderConfigRequest): Promise<ModelProviderConfig> {
    return apiClient.put<ModelProviderConfig>(`/model-providers/configs/${id}`, data);
  },

  /**
   * Delete provider configuration
   */
  async deleteConfig(id: string): Promise<void> {
    return apiClient.delete<void>(`/model-providers/configs/${id}`);
  },

  /**
   * Test provider configuration (validate API key)
   */
  async testConfig(id: string, data?: TestProviderConfigRequest): Promise<TestProviderConfigResponse> {
    return apiClient.post<TestProviderConfigResponse>(`/model-providers/configs/${id}/test`, data);
  },

  /**
   * Set as default provider configuration
   */
  async setAsDefault(id: string): Promise<ModelProviderConfig> {
    return apiClient.post<ModelProviderConfig>(`/model-providers/configs/${id}/set-default`, {});
  },
};

export default modelProviderConfigService;
