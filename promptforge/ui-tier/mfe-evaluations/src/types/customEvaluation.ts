/**
 * Custom Evaluation Types
 * Types for custom evaluation creation and management
 *
 * Custom evaluations run after a model invocation to assess the model's input/output.
 * The evaluation system prompt receives the model's input and output and returns a score.
 */

export interface CustomEvaluationCreate {
  /** Display name for the evaluation */
  name: string;

  /** Evaluation category (accuracy, safety, bias, etc.) */
  category: string;

  /** Optional description of evaluation purpose */
  description?: string;

  /**
   * Model Input Definition
   * Defines how to access the model's input for evaluation.
   * Use {{model_input}} to reference the actual input sent to the model.
   */
  prompt_input: string;

  /**
   * Model Output Definition
   * Defines how to access the model's output for evaluation.
   * Use {{model_output}} to reference the actual output from the model.
   */
  prompt_output: string;

  /**
   * Evaluation System Prompt
   * System prompt that evaluates the model's input/output after invocation.
   * Should return a score (0-1) and pass/fail decision.
   * Has access to {{model_input}} and {{model_output}} variables.
   */
  system_prompt: string;

  /** LLM model to use for running the evaluation (e.g., gpt-4o-mini) */
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

export interface EvaluationFilters {
  search?: string;
  type?: 'all' | 'promptforge' | 'vendor' | 'custom';
  model?: string;
  created_after?: string;
  created_before?: string;
}

export interface EvaluationListParams {
  limit?: number;
  offset?: number;
  trace_id?: string;
  name?: string;
  type?: string;
  model?: string;
  created_after?: string;
  created_before?: string;
}

export interface EvaluationListResponse {
  evaluations: EvaluationResult[];
  total: number;
  limit: number;
  offset: number;
}

export interface EvaluationResult {
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

// Category options for custom evaluations
export const EVALUATION_CATEGORIES = [
  { value: 'accuracy', label: 'Accuracy' },
  { value: 'groundedness', label: 'Groundedness' },
  { value: 'safety', label: 'Safety' },
  { value: 'compliance', label: 'Compliance' },
  { value: 'tone', label: 'Tone' },
  { value: 'bias', label: 'Bias' },
  { value: 'coherence', label: 'Coherence' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'faithfulness', label: 'Faithfulness' },
  { value: 'custom', label: 'Custom' },
] as const;

// Model options for evaluations
export const EVALUATION_MODELS = [
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet' },
  { value: 'claude-3-opus', label: 'Claude 3 Opus' },
] as const;

// Type filter options
export const TYPE_FILTER_OPTIONS = [
  { value: 'all', label: 'All Types' },
  { value: 'promptforge', label: 'PromptForge' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'custom', label: 'Custom' },
] as const;

// Model filter options (same as evaluation models but with "All" option)
export const MODEL_FILTER_OPTIONS = [
  { value: 'all', label: 'All Models' },
  ...EVALUATION_MODELS,
] as const;

// Date range preset options
export const DATE_RANGE_OPTIONS = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'last7days', label: 'Last 7 Days' },
  { value: 'last30days', label: 'Last 30 Days' },
  { value: 'custom', label: 'Custom Range' },
] as const;
