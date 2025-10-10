/**
 * React Query hooks for Evaluations
 * Prevents duplicate API calls by using shared query keys
 */

import { useQuery } from '@tanstack/react-query';
import evaluationService, { EvaluationListParams, EvaluationListResponse } from '../../../shared/services/evaluationService';

/**
 * Hook to fetch evaluations list with filters
 * Uses React Query for caching and deduplication
 */
export function useEvaluationsList(params: EvaluationListParams = {}) {
  const queryParams = {
    limit: 100,
    offset: 0,
    ...params,
  };

  return useQuery<EvaluationListResponse>({
    queryKey: ['evaluations', 'list', queryParams],
    queryFn: () => evaluationService.getEvaluationsList(queryParams),
    staleTime: 30000, // 30 seconds
    retry: 2,
  });
}
