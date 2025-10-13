/**
 * React Query hooks for Insight Comparison API integration
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type {
  CreateComparisonRequest,
  ComparisonResponse,
  ComparisonListResponse,
} from '../types/insights';
import {
  createComparison,
  fetchComparisonHistory,
  fetchComparisonById,
  deleteComparison,
} from '../services/insightsService';

/**
 * Hook for creating a new comparison between two analyses
 *
 * This will:
 * 1. Validate both analyses exist and have same transcript
 * 2. Execute judge model for blind evaluation across 3 stages
 * 3. Calculate overall winner with cost-benefit analysis
 * 4. Store comparison results with traces
 *
 * @returns Mutation object for creating comparison
 */
export function useCreateComparison() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateComparisonRequest) => createComparison(request),
    onSuccess: (data: ComparisonResponse) => {
      // Invalidate comparison history to refetch with new result
      queryClient.invalidateQueries({ queryKey: ['insights', 'comparisons', 'list'] });

      // Cache individual comparison result
      queryClient.setQueryData(['insights', 'comparisons', data.id], data);
    },
  });
}

/**
 * Hook for fetching comparison history with pagination
 *
 * @param skip - Number of records to skip (default 0)
 * @param limit - Maximum number of records to return (default 20)
 * @returns Query object with paginated comparison list
 */
export function useComparisonHistory(skip: number = 0, limit: number = 20) {
  return useQuery<ComparisonListResponse>({
    queryKey: ['insights', 'comparisons', 'list', skip, limit],
    queryFn: () => fetchComparisonHistory(skip, limit),
    staleTime: 30000, // 30 seconds
    retry: 1,
  });
}

/**
 * Hook for fetching a specific comparison by ID
 *
 * @param comparisonId - Comparison UUID
 * @param enabled - Whether to execute query (default true)
 * @returns Query object with complete comparison details
 */
export function useComparisonById(comparisonId: string | null, enabled: boolean = true) {
  return useQuery<ComparisonResponse>({
    queryKey: ['insights', 'comparisons', comparisonId],
    queryFn: () => fetchComparisonById(comparisonId!),
    enabled: enabled && comparisonId !== null,
    staleTime: 60000, // 1 minute (comparison results don't change)
    retry: 1,
  });
}

/**
 * Hook for deleting a comparison
 *
 * @returns Mutation object for deleting comparison
 */
export function useDeleteComparison() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (comparisonId: string) => deleteComparison(comparisonId),
    onSuccess: (_data, comparisonId) => {
      // Invalidate comparison history to refetch without deleted item
      queryClient.invalidateQueries({ queryKey: ['insights', 'comparisons', 'list'] });

      // Remove deleted comparison from cache
      queryClient.removeQueries({ queryKey: ['insights', 'comparisons', comparisonId] });
    },
  });
}
