/**
 * Playground Type Definitions
 *
 * Defines TypeScript interfaces for Playground session data, models, and API requests/responses.
 * All fields align with backend API schemas.
 */

export interface Model {
  id: string;
  name: string;
  provider: string;
  input_cost?: number;
  output_cost?: number;
  costMultiplier?: number;
}

export interface PlaygroundSession {
  // Identifiers
  id: string;                    // trace_id from API
  timestamp: string;             // ISO 8601 datetime
  title?: string;                // Session title for identification

  // Prompts
  prompt: string;                // User prompt (required)
  systemPrompt?: string;         // System prompt (optional, defines model behavior)
  response: string;              // Model response

  // Model Configuration
  model: Model;                  // Selected model

  // Parameters
  parameters: {
    temperature: number;         // 0-2 (controls randomness)
    maxTokens: number;           // Max response length
    topP: number;                // Nucleus sampling 0-1
    topK?: number;               // Top-K sampling 1-100 (optional, some models don't support)
  };

  // Metadata
  metadata?: {
    intent?: string;             // User intent (e.g., "support", "creative writing")
    tone?: string;               // Response tone (e.g., "professional", "casual")
    promptId?: string;           // Loaded prompt template ID (optional)
  };

  // Evaluations
  evaluationIds?: string[];      // Evaluation UUIDs to run on this execution

  // Metrics
  metrics: {
    latency: number;             // Execution time in seconds
    tokens: number;              // Total tokens used
    cost: number;                // USD cost
  };
}

// API Request/Response types (for type safety with backend)

export interface PlaygroundExecutionRequest {
  title: string;
  prompt: string;
  system_prompt?: string;
  model: string;
  parameters: {
    temperature: number;
    max_tokens: number;
    top_p: number;
    top_k?: number;
  };
  metadata?: {
    intent?: string;
    tone?: string;
    prompt_id?: string;
  };
  evaluation_ids?: string[];
}

export interface PlaygroundExecutionResponse {
  response: string;
  metrics: {
    latency_ms: number;
    tokens_used: number;
    cost: number;
  };
  trace_id: string;
  model: string;
  timestamp: string;
}
