/**
 * Prompt Hooks - Centralized React Query hooks for prompt management
 *
 * Implements REACT-QUERY-001 pattern:
 * - useMutation for create/update/delete operations
 * - Proper cache invalidation in onSuccess callbacks
 * - Optimistic updates for instant UI feedback
 * - Separation of server state (React Query) from UI state (useState)
 */

import { useQuery, useMutation, useQueryClient, QueryClient } from '@tanstack/react-query';
import {
  promptService,
  Prompt,
  PromptVersion,
  CreatePromptRequest,
  UpdatePromptRequest,
  CreatePromptVersionRequest,
} from '../services/promptService';
import { projectKeys } from './useProjects';

// Query Keys - centralized for consistency
export const promptKeys = {
  all: ['prompts'] as const,
  lists: () => [...promptKeys.all, 'list'] as const,
  list: (filters?: Record<string, any>) => [...promptKeys.lists(), filters] as const,
  details: () => [...promptKeys.all, 'detail'] as const,
  detail: (id: string) => [...promptKeys.details(), id] as const,
  versions: (promptId: string) => [...promptKeys.detail(promptId), 'versions'] as const,
};

/**
 * Fetch all prompts with optional filters
 */
export function usePrompts(params?: {
  project_id?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: promptKeys.list(params),
    queryFn: () => promptService.getPrompts(params),
    staleTime: 30000,
    gcTime: 300000,
  });
}

/**
 * Fetch single prompt by ID
 */
export function usePrompt(promptId: string | undefined) {
  return useQuery({
    queryKey: promptKeys.detail(promptId!),
    queryFn: () => promptService.getPrompt(promptId!),
    enabled: !!promptId,
    staleTime: 30000,
    gcTime: 300000,
  });
}

/**
 * Fetch prompt versions
 */
export function usePromptVersions(promptId: string | undefined) {
  return useQuery({
    queryKey: promptKeys.versions(promptId!),
    queryFn: () => promptService.getPromptVersions(promptId!),
    enabled: !!promptId,
    staleTime: 30000,
    gcTime: 300000,
  });
}

/**
 * Create prompt mutation with optimistic update
 */
export function useCreatePrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreatePromptRequest) => promptService.createPrompt(data),

    // Optimistic update
    onMutate: async (newPrompt) => {
      const queryKey = promptKeys.list({ project_id: newPrompt.project_id });
      await queryClient.cancelQueries({ queryKey });

      const previousPrompts = queryClient.getQueryData(queryKey);

      // Optimistically add new prompt
      queryClient.setQueryData<Prompt[]>(queryKey, (old = []) => [
        {
          id: 'temp-' + Date.now(),
          name: newPrompt.name,
          description: newPrompt.description || null,
          category: newPrompt.category || null,
          status: newPrompt.status || 'draft',
          project_id: newPrompt.project_id,
          created_by: 'current-user',
          current_version_id: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as Prompt,
        ...old,
      ]);

      return { previousPrompts, queryKey };
    },

    onError: (err, newPrompt, context) => {
      if (context?.previousPrompts) {
        queryClient.setQueryData(context.queryKey, context.previousPrompts);
      }
    },

    onSettled: (data, error, variables) => {
      // Invalidate both prompts list and parent project
      queryClient.invalidateQueries({ queryKey: promptKeys.list({ project_id: variables.project_id }) });
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(variables.project_id) });
    },
  });
}

/**
 * Update prompt mutation with optimistic update
 */
export function useUpdatePrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdatePromptRequest }) =>
      promptService.updatePrompt(id, data),

    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: promptKeys.detail(id) });

      const previousPrompt = queryClient.getQueryData(promptKeys.detail(id));

      // Optimistically update prompt
      queryClient.setQueryData<Prompt>(promptKeys.detail(id), (old) =>
        old
          ? {
              ...old,
              ...data,
              updated_at: new Date().toISOString(),
            }
          : old
      );

      // Update in all lists
      const listQueries = queryClient.getQueriesData<Prompt[]>({ queryKey: promptKeys.lists() });
      listQueries.forEach(([queryKey, prompts]) => {
        if (prompts) {
          queryClient.setQueryData<Prompt[]>(
            queryKey,
            prompts.map((prompt) =>
              prompt.id === id
                ? {
                    ...prompt,
                    ...data,
                    updated_at: new Date().toISOString(),
                  }
                : prompt
            )
          );
        }
      });

      return { previousPrompt };
    },

    onError: (err, { id }, context) => {
      if (context?.previousPrompt) {
        queryClient.setQueryData(promptKeys.detail(id), context.previousPrompt);
      }
    },

    onSettled: (data, error, { id }) => {
      queryClient.invalidateQueries({ queryKey: promptKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}

/**
 * Delete prompt mutation with optimistic update
 */
export function useDeletePrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (promptId: string) => promptService.deletePrompt(promptId),

    onMutate: async (promptId) => {
      // Get all list queries and cancel them
      await queryClient.cancelQueries({ queryKey: promptKeys.lists() });

      // Snapshot all lists
      const listQueries = queryClient.getQueriesData<Prompt[]>({ queryKey: promptKeys.lists() });

      // Optimistically remove from all lists
      listQueries.forEach(([queryKey, prompts]) => {
        if (prompts) {
          queryClient.setQueryData<Prompt[]>(
            queryKey,
            prompts.filter((prompt) => prompt.id !== promptId)
          );
        }
      });

      return { listQueries };
    },

    onError: (err, promptId, context) => {
      // Restore all lists
      if (context?.listQueries) {
        context.listQueries.forEach(([queryKey, prompts]) => {
          queryClient.setQueryData(queryKey, prompts);
        });
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}

/**
 * Create prompt version mutation
 */
export function useCreatePromptVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ promptId, data }: { promptId: string; data: CreatePromptVersionRequest }) =>
      promptService.createPromptVersion(promptId, data),

    onSuccess: (newVersion, { promptId }) => {
      // Invalidate prompt detail (to get updated current_version)
      queryClient.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      // Invalidate versions list
      queryClient.invalidateQueries({ queryKey: promptKeys.versions(promptId) });
      // Update prompt in lists (updated_at changed)
      queryClient.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}

/**
 * Prefetch prompt for instant navigation
 */
export function usePrefetchPrompt(queryClient: QueryClient) {
  return (promptId: string) => {
    queryClient.prefetchQuery({
      queryKey: promptKeys.detail(promptId),
      queryFn: () => promptService.getPrompt(promptId),
      staleTime: 30000,
    });
  };
}

/**
 * Prefetch prompt versions for instant tab switch
 */
export function usePrefetchPromptVersions(queryClient: QueryClient) {
  return (promptId: string) => {
    queryClient.prefetchQuery({
      queryKey: promptKeys.versions(promptId),
      queryFn: () => promptService.getPromptVersions(promptId),
      staleTime: 30000,
    });
  };
}
