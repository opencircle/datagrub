/**
 * React Query hooks for Deep Insights API integration
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type {
  CallInsightsRequest,
  CallInsightsResponse,
  CallInsightsAnalysis,
  CallInsightsHistoryItem,
} from '../types/insights';
import {
  analyzeCallTranscript,
  fetchAnalysisHistory,
  fetchAnalysisById,
} from '../services/insightsService';
import {
  fetchEvaluations,
  fetchEvaluationById,
  fetchEvaluationCategories,
  type EvaluationCatalogItem,
} from '../services/evaluationService';

/**
 * Hook for analyzing call transcripts with 3-stage DTA pipeline
 *
 * @returns Mutation object for executing analysis
 */
export function useAnalyzeTranscript() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CallInsightsRequest) => analyzeCallTranscript(request),
    onSuccess: (data: CallInsightsResponse) => {
      // Invalidate analysis history to refetch with new result
      queryClient.invalidateQueries({ queryKey: ['call-insights', 'history'] });

      // Cache individual analysis result
      queryClient.setQueryData(['call-insights', data.analysis_id], data);
    },
  });
}

/**
 * Hook for fetching analysis history
 *
 * @param filters - Search and filter options
 * @returns Query object with analysis history
 */
export function useAnalysisHistory(filters?: {
  project_id?: string;
  search?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<CallInsightsHistoryItem[]>({
    queryKey: ['call-insights', 'history', filters],
    queryFn: () => fetchAnalysisHistory(filters),
    staleTime: 30000, // 30 seconds
    retry: 1,
  });
}

/**
 * Hook for fetching a specific analysis by ID
 *
 * @param analysisId - Analysis UUID
 * @param enabled - Whether to execute query (default true)
 * @returns Query object with analysis details
 */
export function useAnalysisById(analysisId: string | null, enabled: boolean = true) {
  return useQuery({
    queryKey: ['call-insights', analysisId],
    queryFn: () => fetchAnalysisById(analysisId!),
    enabled: enabled && analysisId !== null,
    staleTime: 60000, // 1 minute (analysis results don't change)
    retry: 1,
  });
}

/**
 * Hook for fetching available evaluations from catalog
 *
 * @param filters - Optional filters for source, category, type
 * @returns Query object with list of evaluations
 */
export function useEvaluations(filters?: {
  source?: string;
  category?: string;
  evaluation_type?: string;
  is_public?: boolean;
  is_active?: boolean;
  search?: string;
}) {
  return useQuery<EvaluationCatalogItem[]>({
    queryKey: ['evaluations', 'catalog', filters],
    queryFn: () => fetchEvaluations(filters),
    staleTime: 300000, // 5 minutes (evaluations don't change often)
    retry: 1,
  });
}

/**
 * Hook for fetching a specific evaluation by ID
 *
 * @param evaluationId - Evaluation UUID
 * @param enabled - Whether to execute query (default true)
 * @returns Query object with evaluation details
 */
export function useEvaluationById(evaluationId: string | null, enabled: boolean = true) {
  return useQuery<EvaluationCatalogItem>({
    queryKey: ['evaluations', evaluationId],
    queryFn: () => fetchEvaluationById(evaluationId!),
    enabled: enabled && evaluationId !== null,
    staleTime: 300000, // 5 minutes
    retry: 1,
  });
}

/**
 * Hook for fetching evaluation categories
 *
 * @param source - Optional source filter
 * @returns Query object with list of categories
 */
export function useEvaluationCategories(source?: string) {
  return useQuery<string[]>({
    queryKey: ['evaluations', 'categories', source],
    queryFn: () => fetchEvaluationCategories(source),
    staleTime: 300000, // 5 minutes
    retry: 1,
  });
}
