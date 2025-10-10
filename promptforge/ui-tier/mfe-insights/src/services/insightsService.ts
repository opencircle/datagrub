/**
 * Insights Service - API integration for call transcript analysis
 * Implements 3-stage Dynamic Temperature Adjustment (DTA) pipeline
 */

import type {
  CallInsightsRequest,
  CallInsightsResponse,
  CallInsightsAnalysis,
  CallInsightsHistoryItem,
} from '../types/insights';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Get access token from localStorage
 */
function getAccessToken(): string | null {
  return localStorage.getItem('promptforge_access_token');
}

/**
 * Analyze call transcript with 3-stage DTA pipeline
 *
 * This will:
 * 1. Optionally redact PII using Presidio
 * 2. Execute Stage 1: Fact Extraction (temperature 0.2)
 * 3. Execute Stage 2: Reasoning & Insights (temperature 0.4)
 * 4. Execute Stage 3: Summary Synthesis (temperature 0.3)
 * 5. Run configured evaluations on outputs
 * 6. Create parent trace + 3 child traces for observability
 *
 * @param request - Call insights analysis request
 * @returns Analysis results with summary, insights, traces, and evaluations
 */
export async function analyzeCallTranscript(
  request: CallInsightsRequest
): Promise<CallInsightsResponse> {
  const token = getAccessToken();

  const response = await fetch(`${API_BASE_URL}/api/v1/call-insights/analyze`, {
    method: 'POST',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to analyze call transcript');
  }

  return response.json();
}

/**
 * Fetch analysis history with search and filters
 *
 * @param filters - Search and filter options
 * @returns List of previous analyses
 */
export async function fetchAnalysisHistory(filters?: {
  project_id?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<CallInsightsHistoryItem[]> {
  const token = getAccessToken();
  const params = new URLSearchParams();

  if (filters) {
    if (filters.project_id) params.append('project_id', filters.project_id);
    if (filters.search) params.append('search', filters.search);
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters.offset !== undefined) params.append('offset', filters.offset.toString());
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/call-insights/history?${params.toString()}`,
    {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch analysis history: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch a specific analysis by ID
 *
 * @param analysisId - Analysis UUID
 * @returns Call insights analysis
 */
export async function fetchAnalysisById(
  analysisId: string
): Promise<CallInsightsAnalysis> {
  const token = getAccessToken();

  const response = await fetch(
    `${API_BASE_URL}/api/v1/call-insights/${analysisId}`,
    {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch analysis: ${response.statusText}`);
  }

  return response.json();
}
