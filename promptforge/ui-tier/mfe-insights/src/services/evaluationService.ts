/**
 * Evaluation Service - API integration for evaluation catalog
 */

export interface EvaluationCatalogItem {
  id: string;
  name: string;
  description: string;
  category: string;
  source: 'VENDOR' | 'PROMPTFORGE' | 'CUSTOM' | 'LLM_JUDGE';
  evaluation_type: 'METRIC' | 'JUDGE' | 'RULE';
  is_public: boolean;
  adapter_class?: string;
  adapter_evaluation_id?: string;
  tags?: string[];
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * Get access token from localStorage
 */
function getAccessToken(): string | null {
  return localStorage.getItem('promptforge_access_token');
}

/**
 * Fetch available evaluations from the catalog
 *
 * @param filters - Optional filters for source, category, type
 * @returns List of available evaluations
 */
export async function fetchEvaluations(filters?: {
  source?: string;
  category?: string;
  evaluation_type?: string;
  is_public?: boolean;
  is_active?: boolean;
  search?: string;
}): Promise<EvaluationCatalogItem[]> {
  const token = getAccessToken();
  const params = new URLSearchParams();

  // Apply filters
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
  }

  const url = `${API_BASE_URL}/api/v1/evaluation-catalog/catalog${params.toString() ? `?${params.toString()}` : ''}`;

  const response = await fetch(url, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to fetch evaluations');
  }

  return response.json();
}

/**
 * Fetch a specific evaluation by ID
 *
 * @param evaluationId - Evaluation UUID
 * @returns Evaluation details
 */
export async function fetchEvaluationById(
  evaluationId: string
): Promise<EvaluationCatalogItem> {
  const token = getAccessToken();

  const response = await fetch(
    `${API_BASE_URL}/api/v1/evaluation-catalog/catalog/${evaluationId}`,
    {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch evaluation: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch evaluation categories
 *
 * @param source - Optional source filter
 * @returns List of unique categories
 */
export async function fetchEvaluationCategories(
  source?: string
): Promise<string[]> {
  const token = getAccessToken();
  const params = new URLSearchParams();

  if (source) {
    params.append('source', source);
  }

  const url = `${API_BASE_URL}/api/v1/evaluation-catalog/categories${params.toString() ? `?${params.toString()}` : ''}`;

  const response = await fetch(url, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch categories: ${response.statusText}`);
  }

  return response.json();
}
