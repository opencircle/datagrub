/**
 * AI Model Service
 */

import { apiClient } from './apiClient';

export type ModelProviderType = 'openai' | 'anthropic' | 'google' | 'cohere' | 'huggingface' | 'custom';

export interface ModelProvider {
  id: string;
  name: string;
  provider_type: ModelProviderType;
  description: string | null;
  api_base_url: string | null;
  config: Record<string, any> | null;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface AIModel {
  id: string;
  name: string;
  model_id: string;
  description: string | null;
  supports_streaming: boolean;
  supports_function_calling: boolean;
  supports_vision: boolean;
  max_context_length: number | null;
  input_cost_per_million: number | null;
  output_cost_per_million: number | null;
  default_temperature: number;
  default_max_tokens: number;
  default_config: Record<string, any> | null;
  is_active: boolean;
  is_deprecated: boolean;
  provider_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateModelProviderRequest {
  name: string;
  provider_type: ModelProviderType;
  description?: string;
  api_base_url?: string;
  api_key?: string;
  config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface CreateAIModelRequest {
  name: string;
  model_id: string;
  description?: string;
  supports_streaming?: boolean;
  supports_function_calling?: boolean;
  supports_vision?: boolean;
  max_context_length?: number;
  input_cost_per_million?: number;
  output_cost_per_million?: number;
  default_temperature?: number;
  default_max_tokens?: number;
  default_config?: Record<string, any>;
  is_active?: boolean;
  is_deprecated?: boolean;
  provider_id: string;
}

export interface UpdateAIModelRequest {
  name?: string;
  description?: string;
  supports_streaming?: boolean;
  supports_function_calling?: boolean;
  supports_vision?: boolean;
  max_context_length?: number;
  input_cost_per_million?: number;
  output_cost_per_million?: number;
  default_temperature?: number;
  default_max_tokens?: number;
  default_config?: Record<string, any>;
  is_active?: boolean;
  is_deprecated?: boolean;
}

export const modelService = {
  /**
   * Model Provider APIs
   */
  async getProviders(params?: { is_active?: boolean }): Promise<ModelProvider[]> {
    return apiClient.get<ModelProvider[]>('/models/providers', { params });
  },

  async getProvider(id: string): Promise<ModelProvider> {
    return apiClient.get<ModelProvider>(`/models/providers/${id}`);
  },

  async createProvider(data: CreateModelProviderRequest): Promise<ModelProvider> {
    return apiClient.post<ModelProvider>('/models/providers', data);
  },

  /**
   * AI Model APIs
   */
  async getModels(params?: { provider_id?: string; is_active?: boolean }): Promise<AIModel[]> {
    return apiClient.get<AIModel[]>('/models', { params });
  },

  async getModel(id: string): Promise<AIModel> {
    return apiClient.get<AIModel>(`/models/${id}`);
  },

  async createModel(data: CreateAIModelRequest): Promise<AIModel> {
    return apiClient.post<AIModel>('/models', data);
  },

  async updateModel(id: string, data: UpdateAIModelRequest): Promise<AIModel> {
    return apiClient.patch<AIModel>(`/models/${id}`, data);
  },
};

export default modelService;
