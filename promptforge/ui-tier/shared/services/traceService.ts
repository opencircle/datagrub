/**
 * Trace Service
 */

import { apiClient } from './apiClient';

export interface Span {
  id: string;
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  name: string;
  span_type: string | null;
  start_time: number;
  end_time: number | null;
  duration_ms: number | null;
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  span_metadata: Record<string, any> | null;
  model_name: string | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  temperature: number | null;
  max_tokens: number | null;
  status: string;
  error_message: string | null;
  created_at: string;
}

export interface Trace {
  id: string;
  trace_id: string;
  name: string;
  status: string;
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  trace_metadata: Record<string, any> | null;
  total_duration_ms: number | null;
  total_tokens: number | null;
  total_cost: number | null;
  error_message: string | null;
  error_type: string | null;
  project_id: string;
  prompt_version_id: string | null;
  model_id: string | null;
  created_at: string;
  updated_at: string;
  spans?: Span[];
}

export interface AggregatedTraceData {
  total_tokens: number;
  total_cost: number;
  model_names: string[];
  avg_duration_ms?: number;
}

export interface TraceListItem {
  id: string;
  trace_id: string;
  project_name: string;
  status: string;
  model_name?: string;
  provider?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  total_duration_ms?: number;
  total_cost?: number;
  environment?: string;
  retry_count: number;
  created_at: string;
  user_email?: string;

  // Parent-child trace enhancement fields
  source: string;
  has_children: boolean;
  child_count: number;
  children: TraceListItem[];
  parent_trace_id?: string;
  stage?: string;
  aggregated_data?: AggregatedTraceData;
}

export interface TraceListResponse {
  traces: TraceListItem[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Comprehensive LLM metadata for evaluations that invoke LLMs
 * Captures token usage, costs, performance metrics, and provider-specific data
 */
export interface LLMMetadata {
  /** LLM provider (e.g., "openai", "anthropic", "cohere") */
  provider?: string;
  /** Provider-specific model identifier (e.g., "gpt-4-turbo-2024-04-09") */
  provider_model?: string;

  /** Token usage breakdown */
  token_usage?: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
    cache_read_tokens?: number;  // Anthropic-specific
    cache_creation_tokens?: number;  // Anthropic-specific
  };

  /** Cost metrics in USD */
  cost_metrics?: {
    input_cost?: number;
    output_cost?: number;
    cache_read_cost?: number;  // Anthropic-specific
    cache_write_cost?: number;  // Anthropic-specific
    total_cost?: number;
    input_price_per_1k?: number;
    output_price_per_1k?: number;
  };

  /** Performance metrics */
  performance_metrics?: {
    total_duration_ms?: number;
    time_to_first_token_ms?: number;
    tokens_per_second?: number;
    queue_time_ms?: number;
    processing_time_ms?: number;
  };

  /** Request parameters used */
  request_parameters?: {
    model?: string;
    temperature?: number;
    top_p?: number;
    top_k?: number;
    max_tokens?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    stop_sequences?: string[];
    seed?: number;
  };

  /** Response metadata */
  response_metadata?: {
    finish_reason?: string;
    model_version?: string;
    request_id?: string;
    system_fingerprint?: string;
  };

  /** Rate limit information from provider */
  rate_limit_info?: {
    requests_limit?: number;
    requests_remaining?: number;
    requests_reset_at?: string;
    tokens_limit?: number;
    tokens_remaining?: number;
    tokens_reset_at?: string;
  };

  /** Additional vendor-specific fields */
  [key: string]: any;
}

export interface EvaluationResult {
  id: string;
  evaluation_name: string;
  evaluation_source: string;
  evaluation_type: string;
  category: string;

  /** Display name of evaluation vendor (e.g., "DeepEval", "Ragas", "MLflow") */
  vendor_name?: string | null;

  score?: number;
  passed?: boolean;
  category_result?: string;
  reason?: string;
  execution_time_ms?: number;
  status: string;

  // LLM Cost Tracking (top-level for convenience)
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  evaluation_cost?: number;

  /** Comprehensive LLM metadata (for evaluations that invoke LLMs) */
  llm_metadata?: LLMMetadata | null;

  // Vendor-specific metrics (deprecated - use llm_metadata instead)
  vendor_metrics?: Record<string, any>;

  // Additional details
  details?: Record<string, any>;
  suggestions?: string[];
  model_used?: string;
}

export interface ChildTrace {
  id: string;
  trace_id: string;
  stage?: string;
  status: string;
  model_name?: string;
  provider?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  total_duration_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  total_cost?: number;
  created_at: string;
}

export interface TraceDetail {
  id: string;
  trace_id: string;
  name: string;
  status: string;
  project_id: string;
  project_name: string;
  prompt_version_id?: string;
  model_id?: string;
  model_name?: string;
  provider?: string;
  user_id?: string;
  user_email?: string;
  environment?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  trace_metadata?: Record<string, any>;
  total_duration_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  total_cost?: number;
  retry_count?: number;
  error_message?: string;
  error_type?: string;
  created_at: string;
  updated_at: string;
  spans?: Span[];
  evaluations?: EvaluationResult[];
  children?: ChildTrace[];
}

export interface CreateTraceRequest {
  trace_id: string;
  name: string;
  status?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  trace_metadata?: Record<string, any>;
  total_duration_ms?: number;
  total_tokens?: number;
  total_cost?: number;
  error_message?: string;
  error_type?: string;
  project_id: string;
  prompt_version_id?: string;
  model_id?: string;
  spans?: Array<{
    span_id: string;
    parent_span_id?: string;
    name: string;
    span_type?: string;
    start_time: number;
    end_time?: number;
    duration_ms?: number;
    input_data?: Record<string, any>;
    output_data?: Record<string, any>;
    span_metadata?: Record<string, any>;
    model_name?: string;
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
    temperature?: number;
    max_tokens?: number;
    status?: string;
    error_message?: string;
  }>;
}

export const traceService = {
  /**
   * Get paginated traces list with filters and sorting
   */
  async getTraces(params?: {
    search?: string;
    model?: string;
    status_filter?: string;
    source_filter?: string;
    sort_by?: string;
    sort_direction?: 'asc' | 'desc';
    page?: number;
    page_size?: number;
  }): Promise<TraceListResponse> {
    return apiClient.get<TraceListResponse>('/traces', { params });
  },

  /**
   * Get trace by ID
   */
  async getTrace(id: string, includeSpans = true): Promise<Trace> {
    return apiClient.get<Trace>(`/traces/${id}`, {
      params: { include_spans: includeSpans },
    });
  },

  /**
   * Get comprehensive trace details with evaluations
   */
  async getTraceDetail(id: string): Promise<TraceDetail> {
    return apiClient.get<TraceDetail>(`/traces/${id}/detail`);
  },

  /**
   * Create new trace
   */
  async createTrace(data: CreateTraceRequest): Promise<Trace> {
    return apiClient.post<Trace>('/traces', data);
  },

  /**
   * Delete trace
   */
  async deleteTrace(id: string): Promise<void> {
    return apiClient.delete<void>(`/traces/${id}`);
  },
};

export default traceService;
