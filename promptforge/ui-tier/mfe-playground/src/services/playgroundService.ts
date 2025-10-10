/**
 * Playground Service - API integration for live prompt execution
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Interfaces
export interface Prompt {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  current_version?: {
    template: string;
    system_message: string | null;
    model_config?: {
      tone?: string;
    };
  };
}

export interface PlaygroundExecutionRequest {
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
  evaluation_ids?: string[];  // Optional list of evaluation IDs to run after execution
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

/**
 * Get access token from localStorage
 */
function getAccessToken(): string | null {
  return localStorage.getItem('promptforge_access_token');
}

/**
 * Fetch all prompts
 */
export async function fetchPrompts(): Promise<Prompt[]> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/prompts`, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch prompts: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Execute prompt with live API
 * This will:
 * 1. Look up organization's model API key from backend
 * 2. Execute prompt against actual model provider (OpenAI, Anthropic, etc.)
 * 3. Trace the API call for observability
 */
export async function executePrompt(
  request: PlaygroundExecutionRequest
): Promise<PlaygroundExecutionResponse> {
  const token = getAccessToken();

  const response = await fetch(`${API_BASE_URL}/api/v1/playground/execute`, {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to execute prompt');
  }

  return response.json();
}
