/**
 * Deep Insights - Call Analysis TypeScript Interfaces
 *
 * Supports 3-stage Dynamic Temperature Adjustment pipeline:
 * - Stage 1: Fact Extraction (temperature 0.25, top_p 0.95)
 * - Stage 2: Reasoning & Insights (temperature 0.65, top_p 0.95)
 * - Stage 3: Summary Synthesis (temperature 0.45, top_p 0.95)
 *
 * Note: top_k is not supported (OpenAI and Claude don't use this parameter)
 */

export interface StageParameters {
  temperature?: number;
  top_p?: number;
  max_tokens?: number;
}

export interface SystemPrompts {
  stage1_fact_extraction?: string;
  stage2_reasoning?: string;
  stage3_summary?: string;
}

export interface Models {
  stage1_model?: string;
  stage2_model?: string;
  stage3_model?: string;
}

export interface AvailableModel {
  model_id: string;
  display_name: string;
  provider: string;
  description?: string;
  input_cost: number;
  output_cost: number;
  context_window?: number;
}

export interface CallInsightsRequest {
  transcript: string;
  transcript_title?: string;
  project_id?: string;
  stage_params?: {
    fact_extraction?: StageParameters;
    reasoning?: StageParameters;
    summary?: StageParameters;
  };
  system_prompts?: SystemPrompts;
  models?: Models;
  enable_pii_redaction?: boolean;
  evaluations?: string[];
}

export interface TraceMetadata {
  trace_id: string;
  stage: string;
  model: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  duration_ms: number;
  cost: number;
  system_prompt?: string | null;  // Custom system prompt used for this stage
}

export interface EvaluationMetric {
  evaluation_name: string;
  evaluation_uuid: string;
  score: number;
  passed: boolean;
  reason: string;
  threshold?: number;
  category?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  evaluation_cost?: number;
}

export interface CallInsightsResponse {
  analysis_id: string;
  project_id: string;
  summary: string;
  insights: string;
  facts: string;
  pii_redacted: boolean;
  traces: TraceMetadata[];
  evaluations: EvaluationMetric[];
  total_tokens: number;
  total_cost: number;
  created_at: string;
}

export interface CallInsightsAnalysis {
  id: string;
  transcript_title?: string;
  project_id?: string;
  transcript_input: string;
  summary_output: string;
  insights_output: string;
  facts_output: string;
  pii_redacted: boolean;
  total_tokens: number;
  total_cost: number;
  system_prompt_stage1?: string;
  system_prompt_stage2?: string;
  system_prompt_stage3?: string;
  model_stage1?: string;
  model_stage2?: string;
  model_stage3?: string;
  created_at: string;
}

export interface CallInsightsHistoryItem {
  id: string;
  transcript_title?: string;
  transcript_preview: string;
  project_id?: string;
  total_tokens: number;
  total_cost: number;
  pii_redacted: boolean;
  created_at: string;
}

// UI State Types
export interface InsightsFormState {
  transcript: string;
  transcriptTitle: string;
  projectId: string;
  enablePiiRedaction: boolean;
  showAdvancedParams: boolean;
  stageParams: {
    factExtraction: StageParameters;
    reasoning: StageParameters;
    summary: StageParameters;
  };
  systemPrompts: {
    stage1: string;
    stage2: string;
    stage3: string;
  };
  models: {
    stage1: string;
    stage2: string;
    stage3: string;
  };
  selectedEvaluations: string[];
}

export interface InsightsResultState {
  analysisId: string | null;
  summary: string | null;
  insights: string | null;
  facts: string | null;
  traces: TraceMetadata[];
  evaluations: EvaluationMetric[];
  totalTokens: number;
  totalCost: number;
  isLoading: boolean;
  error: string | null;
}

// Constants for default values
export const DEFAULT_STAGE_PARAMS = {
  factExtraction: {
    temperature: 0.25,
    top_p: 0.95,
    max_tokens: 1000,
  },
  reasoning: {
    temperature: 0.65,
    top_p: 0.95,
    max_tokens: 1500,
  },
  summary: {
    temperature: 0.45,
    top_p: 0.95,
    max_tokens: 800,
  },
} as const;

export const AVAILABLE_EVALUATIONS = [
  { id: 'faithfulness', name: 'Faithfulness', description: 'Factual accuracy check' },
  { id: 'coherence', name: 'Coherence', description: 'Logical flow and consistency' },
  { id: 'conciseness', name: 'Conciseness', description: 'Brevity without losing meaning' },
  { id: 'factual-accuracy', name: 'Factual Accuracy', description: 'Verification against source' },
  { id: 'readability', name: 'Readability', description: 'Ease of understanding' },
] as const;
