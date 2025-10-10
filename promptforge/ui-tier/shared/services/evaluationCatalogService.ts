/**
 * Evaluation Catalog Service
 *
 * Service for browsing and executing evaluations from the unified catalog
 * Supports vendor, custom, PromptForge, and LLM-as-Judge evaluations
 */

import { apiClient } from './apiClient';

export type EvaluationSource = 'vendor' | 'custom' | 'promptforge' | 'llm_judge';
export type EvaluationType = 'metric' | 'validator' | 'classifier' | 'judge';

export interface EvaluationMetadata {
  id: string;
  name: string;
  description: string | null;
  source: EvaluationSource;
  evaluation_type: EvaluationType;
  category: string;
  is_public: boolean;
  is_active: boolean;
  version: string;
  tags: string[] | null;
}

export interface EvaluationDetailedMetadata extends EvaluationMetadata {
  organization_id: string | null;
  project_id: string | null;
  config_schema: Record<string, any> | null;
  default_config: Record<string, any> | null;
  implementation: string | null;
  adapter_class: string | null;
  llm_criteria: string | null;
  llm_model: string | null;
  llm_system_prompt: string | null;
  created_at: string;
  updated_at: string;
}

export interface EvaluationRequest {
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  context?: string[];
  ground_truth?: string;
  metadata?: Record<string, any>;
  config?: Record<string, any>;
}

export interface EvaluationResult {
  evaluation_id: string;
  evaluation_name: string;
  source: EvaluationSource;
  score: number;
  passed: boolean | null;
  category: string | null;
  reason: string;
  details: Record<string, any> | null;
  suggestions: string[];
  execution_time_ms: number;
  model_used: string | null;
  status: 'completed' | 'failed';
  error: string | null;
}

export interface ExecuteEvaluationsRequest {
  evaluation_ids: string[];
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  context?: string[];
  ground_truth?: string;
  config_overrides?: Record<string, Record<string, any>>;
}

export interface ExecuteEvaluationsResponse {
  trace_id?: string;
  results: EvaluationResult[];
  summary: {
    total_evaluations: number;
    passed: number;
    failed: number;
    avg_score: number;
    total_execution_time_ms: number;
  };
}

export interface CreateLLMJudgeEvaluationRequest {
  name: string;
  description: string;
  category: string;
  criteria: string;
  model: string;
  system_prompt?: string;
  organization_id?: string;
  project_id?: string;
}

export const evaluationCatalogService = {
  /**
   * Get evaluation catalog
   */
  async getCatalog(params?: {
    source?: EvaluationSource;
    category?: string;
    is_public?: boolean;
    organization_id?: string;
    project_id?: string;
    search?: string;
  }): Promise<EvaluationMetadata[]> {
    return apiClient.get<EvaluationMetadata[]>('/evaluation-catalog/catalog', { params });
  },

  /**
   * Get specific evaluation metadata (detailed)
   */
  async getEvaluation(id: string): Promise<EvaluationDetailedMetadata> {
    return apiClient.get<EvaluationDetailedMetadata>(`/evaluation-catalog/catalog/${id}`);
  },

  /**
   * Execute evaluations on a trace
   */
  async executeEvaluations(
    traceId: string,
    data: ExecuteEvaluationsRequest
  ): Promise<ExecuteEvaluationsResponse> {
    return apiClient.post<ExecuteEvaluationsResponse>(
      `/evaluation-catalog/traces/${traceId}/execute`,
      data
    );
  },

  /**
   * Execute single evaluation
   */
  async executeEvaluation(
    evaluationId: string,
    data: EvaluationRequest
  ): Promise<EvaluationResult> {
    return apiClient.post<EvaluationResult>(
      `/evaluation-catalog/catalog/${evaluationId}/execute`,
      data
    );
  },

  /**
   * Create LLM-as-Judge evaluation
   */
  async createLLMJudge(data: CreateLLMJudgeEvaluationRequest): Promise<EvaluationDetailedMetadata> {
    return apiClient.post<EvaluationDetailedMetadata>('/evaluation-catalog/llm-judge', data);
  },

  /**
   * Get evaluation categories
   */
  async getCategories(params?: { source?: EvaluationSource }): Promise<string[]> {
    return apiClient.get<string[]>('/evaluation-catalog/categories', { params });
  },

  /**
   * Get evaluations by category
   */
  async getByCategory(category: string, params?: { source?: EvaluationSource }): Promise<EvaluationMetadata[]> {
    return apiClient.get<EvaluationMetadata[]>('/evaluation-catalog/catalog', {
      params: { category, ...params },
    });
  },

  /**
   * Search evaluations
   */
  async search(query: string, params?: {
    source?: EvaluationSource;
    limit?: number;
  }): Promise<EvaluationMetadata[]> {
    return apiClient.get<EvaluationMetadata[]>('/evaluation-catalog/catalog', {
      params: { search: query, ...params },
    });
  },
};

export default evaluationCatalogService;
