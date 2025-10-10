/**
 * Evaluation Service
 */

import { apiClient } from './apiClient';

export interface EvaluationResult {
  id: string;
  evaluation_id: string;
  test_name: string;
  input_data: Record<string, any>;
  expected_output: string | null;
  actual_output: string | null;
  score: number | null;
  passed: boolean;
  latency_ms: number | null;
  token_count: number | null;
  cost: number | null;
  metrics: Record<string, any> | null;
  error_message: string | null;
  created_at: string;
}

export interface Evaluation {
  id: string;
  name: string;
  description: string | null;
  evaluation_type: 'accuracy' | 'toxicity' | 'bias' | 'custom';
  status: 'pending' | 'running' | 'completed' | 'failed';
  config: Record<string, any> | null;
  dataset_id: string | null;
  project_id: string;
  prompt_id: string | null;
  created_by: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  avg_score: number | null;
  created_at: string;
  updated_at: string;
  results?: EvaluationResult[];
}

// Enhanced Evaluation list parameters (P0 features)
export interface EvaluationListParams {
  limit?: number;
  offset?: number;
  trace_id?: string;
  name?: string;
  type?: string;
  model?: string;
  created_after?: string;
  created_before?: string;
  // NEW P0 filters
  prompt_title?: string;      // Filter by prompt title (fuzzy search)
  vendor?: string;             // Filter by vendor name
  category?: string;           // Filter by category
  status_filter?: 'pass' | 'fail'; // Filter by pass/fail status
  // NEW P0 sorting
  sort_by?: 'timestamp' | 'score' | 'evaluation_name' | 'category' | 'prompt_title' | 'model';
  sort_direction?: 'asc' | 'desc';
}

// Enhanced Evaluation list item (P0 features)
export interface EvaluationListItem {
  id: string;
  name: string;
  description: string | null;
  type: string;
  status: string;
  trace_id: string;
  // NEW P0 fields
  trace_identifier: string;    // tr_abc123
  project_id: string;
  prompt_title: string;        // Trace name/title
  model: string;               // Model used
  vendor_name: string | null;  // Evaluation vendor
  category: string | null;     // Category (quality, security, etc.)
  // Results
  avg_score: number | null;
  passed: boolean | null;      // Explicit pass/fail
  total_tests: number;
  passed_tests: number;
  // Metrics
  total_tokens: number;
  total_cost: number;
  duration_ms: number;
  created_at: string;
}

export interface EvaluationListResponse {
  evaluations: EvaluationListItem[];
  total: number;
  limit: number;
  offset: number;
}

// Enhanced Evaluation Detail (P1 feature)
export interface EvaluationDetailResponse {
  id: string;
  trace_id: string;
  trace_identifier: string;
  // Trace context
  prompt_title: string;
  model_name: string;
  project_name: string;
  project_id: string;
  created_at: string;
  // Evaluation details
  evaluation_name: string;
  evaluation_type: string;
  vendor_name: string | null;
  category: string | null;
  source: string;
  description: string | null;
  // Results
  score: number | null;
  threshold: number | null;
  passed: boolean | null;
  reason: string | null;
  explanation: string | null;
  // Execution metrics
  execution_time_ms: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  evaluation_cost: number | null;
  // Full data for debugging
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  llm_metadata: Record<string, any> | null;
  // Trace link
  trace: {
    id: string;
    trace_id: string;
    name: string;
    status: string;
  };
}

// Legacy interface for backward compatibility
export interface EvaluationResultDetailed {
  id: string;
  trace_id: string;
  evaluation_id: string;
  name: string;
  description?: string;
  type: 'promptforge' | 'vendor' | 'custom';
  score: number;
  passed: boolean;
  reason?: string;
  input: string;
  output: string;
  tokens_used: number;
  cost_usd: number;
  time_taken_ms: number;
  model: string;
  created_at: string;
}

export interface CustomEvaluationCreate {
  name: string;
  category: string;
  description?: string;
  prompt_input: string;
  prompt_output: string;
  system_prompt: string;
  model: string;
}

export interface CustomEvaluation extends CustomEvaluationCreate {
  id: string;
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface EvaluationRunRequest {
  evaluation_ids: string[];
  trace_id: string;
  model_override?: string;
}

export interface EvaluationRunResult {
  evaluation_id: string;
  trace_id: string;
  score: number;
  passed: boolean;
  reason?: string;
  tokens_used: number;
  cost_usd: number;
  time_taken_ms: number;
}

export const evaluationService = {
  /**
   * Get evaluations with enhanced filtering and pagination (P0)
   */
  async getEvaluationsList(params?: EvaluationListParams): Promise<EvaluationListResponse> {
    return apiClient.get<EvaluationListResponse>('/evaluations/list', { params });
  },

  /**
   * Get evaluation detail with full trace context (P1)
   */
  async getEvaluationDetail(evaluationId: string): Promise<EvaluationDetailResponse> {
    return apiClient.get<EvaluationDetailResponse>(`/evaluations/${evaluationId}/detail`);
  },

  /**
   * Create custom evaluation
   */
  async createCustomEvaluation(data: CustomEvaluationCreate): Promise<CustomEvaluation> {
    return apiClient.post<CustomEvaluation>('/evaluation-catalog/custom', data);
  },

  /**
   * Get custom evaluations
   */
  async getCustomEvaluations(params?: {
    limit?: number;
    offset?: number;
    category?: string;
  }): Promise<CustomEvaluation[]> {
    return apiClient.get<CustomEvaluation[]>('/evaluation-catalog/custom', { params });
  },

  /**
   * Run evaluations on a trace
   */
  async runEvaluations(data: EvaluationRunRequest): Promise<EvaluationRunResult[]> {
    return apiClient.post<EvaluationRunResult[]>('/evaluations/run', data);
  },
};

export default evaluationService;
