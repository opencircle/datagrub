/**
 * Project Hooks - Centralized React Query hooks for project management
 *
 * Implements REACT-QUERY-001 pattern:
 * - useMutation for create/update/delete operations
 * - Proper cache invalidation in onSuccess callbacks
 * - Optimistic updates for instant UI feedback
 * - Separation of server state (React Query) from UI state (useState)
 */

import { useQuery, useMutation, useQueryClient, QueryClient } from '@tanstack/react-query';
import { projectService, Project, CreateProjectRequest, UpdateProjectRequest } from '../services/projectService';

// Query Keys - centralized for consistency
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters?: Record<string, any>) => [...projectKeys.lists(), filters] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: string) => [...projectKeys.details(), id] as const,
};

/**
 * Fetch all projects
 */
export function useProjects(params?: {
  organization_id?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: projectKeys.list(params),
    queryFn: () => projectService.getProjects(params),
    staleTime: 30000, // 30 seconds - reduce unnecessary refetches
    gcTime: 300000, // 5 minutes - keep in cache
  });
}

/**
 * Fetch single project by ID
 */
export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: projectKeys.detail(projectId!),
    queryFn: () => projectService.getProject(projectId!),
    enabled: !!projectId,
    staleTime: 30000,
    gcTime: 300000,
  });
}

/**
 * Create project mutation with optimistic update
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectRequest) => projectService.createProject(data),

    // Optimistic update - instantly show new project in UI
    onMutate: async (newProject) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      // Snapshot the previous value
      const previousProjects = queryClient.getQueryData(projectKeys.lists());

      // Optimistically update to the new value
      queryClient.setQueryData<Project[]>(projectKeys.lists(), (old = []) => [
        {
          id: 'temp-' + Date.now(), // Temporary ID
          name: newProject.name,
          description: newProject.description || null,
          status: newProject.status || 'draft',
          organization_id: newProject.organization_id,
          created_by: 'current-user', // Will be replaced by server response
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as Project,
        ...old,
      ]);

      // Return context object with the snapshotted value
      return { previousProjects };
    },

    // If mutation fails, use the context returned from onMutate to roll back
    onError: (err, newProject, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },

    // Always refetch after error or success to sync with server
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

/**
 * Update project mutation with optimistic update
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectRequest }) =>
      projectService.updateProject(id, data),

    // Optimistic update
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: projectKeys.detail(id) });
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      const previousProject = queryClient.getQueryData(projectKeys.detail(id));
      const previousProjects = queryClient.getQueryData(projectKeys.lists());

      // Optimistically update project detail
      queryClient.setQueryData<Project>(projectKeys.detail(id), (old) =>
        old
          ? {
              ...old,
              ...data,
              updated_at: new Date().toISOString(),
            }
          : old
      );

      // Optimistically update project in list
      queryClient.setQueryData<Project[]>(projectKeys.lists(), (old = []) =>
        old.map((project) =>
          project.id === id
            ? {
                ...project,
                ...data,
                updated_at: new Date().toISOString(),
              }
            : project
        )
      );

      return { previousProject, previousProjects };
    },

    onError: (err, { id }, context) => {
      if (context?.previousProject) {
        queryClient.setQueryData(projectKeys.detail(id), context.previousProject);
      }
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },

    onSettled: (data, error, { id }) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

/**
 * Delete project mutation with optimistic update
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId: string) => projectService.deleteProject(projectId),

    // Optimistic update - immediately remove from UI
    onMutate: async (projectId) => {
      await queryClient.cancelQueries({ queryKey: projectKeys.lists() });

      const previousProjects = queryClient.getQueryData(projectKeys.lists());

      // Optimistically remove from list
      queryClient.setQueryData<Project[]>(projectKeys.lists(), (old = []) =>
        old.filter((project) => project.id !== projectId)
      );

      return { previousProjects };
    },

    onError: (err, projectId, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.lists(), context.previousProjects);
      }
    },

    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

/**
 * Prefetch project for instant navigation
 */
export function usePrefetchProject(queryClient: QueryClient) {
  return (projectId: string) => {
    queryClient.prefetchQuery({
      queryKey: projectKeys.detail(projectId),
      queryFn: () => projectService.getProject(projectId),
      staleTime: 30000,
    });
  };
}
