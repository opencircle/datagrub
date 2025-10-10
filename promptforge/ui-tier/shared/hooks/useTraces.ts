/**
 * Trace Hooks - Centralized React Query hooks for trace management
 *
 * Implements REACT-QUERY-001 pattern:
 * - useQuery for fetching operations
 * - Proper cache invalidation in onSuccess callbacks
 * - Separation of server state (React Query) from UI state (useState)
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { traceService, TraceListResponse } from '../services/traceService';

// Query Keys - centralized for consistency
export const traceKeys = {
  all: ['traces'] as const,
  lists: () => [...traceKeys.all, 'list'] as const,
  list: (filters?: Record<string, any>) => [...traceKeys.lists(), filters] as const,
  details: () => [...traceKeys.all, 'detail'] as const,
  detail: (id: string) => [...traceKeys.details(), id] as const,
};

/**
 * Fetch paginated traces list with filters and sorting
 */
export function useTraces(params?: {
  search?: string;
  model?: string;
  status_filter?: string;
  source_filter?: string;
  sort_by?: string;
  sort_direction?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: traceKeys.list(params),
    queryFn: () => traceService.getTraces(params),
    staleTime: 10000, // 10 seconds - traces update frequently
    gcTime: 60000, // 1 minute - keep in cache
  });
}

/**
 * Fetch single trace detail by ID
 */
export function useTraceDetail(traceId: string | undefined) {
  return useQuery({
    queryKey: traceKeys.detail(traceId!),
    queryFn: () => traceService.getTraceDetail(traceId!),
    enabled: !!traceId,
    staleTime: 30000, // 30 seconds
    gcTime: 300000, // 5 minutes
  });
}

/**
 * Prefetch trace detail for instant navigation
 */
export function usePrefetchTraceDetail(queryClient: any) {
  return (traceId: string) => {
    queryClient.prefetchQuery({
      queryKey: traceKeys.detail(traceId),
      queryFn: () => traceService.getTraceDetail(traceId),
      staleTime: 30000,
    });
  };
}
