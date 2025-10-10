/**
 * Prompt Service
 */

import { apiClient } from './apiClient';

export interface PromptVersion {
  id: string;
  version_number: number;
  prompt_id: string;
  template: string;
  system_message: string | null;
  variables: Record<string, any> | null;
  model_config: Record<string, any> | null;
  tags: string[] | null;
  avg_latency_ms: number | null;
  avg_cost: number | null;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface Prompt {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  status: 'draft' | 'active' | 'archived';
  project_id: string;
  created_by: string;
  current_version_id: string | null;
  created_at: string;
  updated_at: string;
  current_version?: PromptVersion;
}

export interface CreatePromptRequest {
  name: string;
  description?: string;
  category?: string;
  status?: 'draft' | 'active' | 'archived';
  project_id: string;
  initial_version: {
    template: string;
    system_message?: string;
    variables?: Record<string, any>;
    model_config?: Record<string, any>;
    tags?: string[];
  };
}

export interface UpdatePromptRequest {
  name?: string;
  description?: string;
  category?: string;
  status?: 'draft' | 'active' | 'archived';
}

export interface CreatePromptVersionRequest {
  template: string;
  system_message?: string;
  variables?: Record<string, any>;
  model_config?: Record<string, any>;
  tags?: string[];
}

export const promptService = {
  /**
   * Get all prompts
   */
  async getPrompts(params?: {
    project_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<Prompt[]> {
    return apiClient.get<Prompt[]>('/prompts', { params });
  },

  /**
   * Get prompt by ID
   */
  async getPrompt(id: string): Promise<Prompt> {
    return apiClient.get<Prompt>(`/prompts/${id}`);
  },

  /**
   * Create new prompt
   */
  async createPrompt(data: CreatePromptRequest): Promise<Prompt> {
    return apiClient.post<Prompt>('/prompts', data);
  },

  /**
   * Update prompt
   */
  async updatePrompt(id: string, data: UpdatePromptRequest): Promise<Prompt> {
    return apiClient.patch<Prompt>(`/prompts/${id}`, data);
  },

  /**
   * Delete prompt
   */
  async deletePrompt(id: string): Promise<void> {
    return apiClient.delete<void>(`/prompts/${id}`);
  },

  /**
   * Get prompt versions
   */
  async getPromptVersions(promptId: string): Promise<PromptVersion[]> {
    return apiClient.get<PromptVersion[]>(`/prompts/${promptId}/versions`);
  },

  /**
   * Create new prompt version
   */
  async createPromptVersion(
    promptId: string,
    data: CreatePromptVersionRequest
  ): Promise<PromptVersion> {
    return apiClient.post<PromptVersion>(`/prompts/${promptId}/versions`, data);
  },
};

export default promptService;
