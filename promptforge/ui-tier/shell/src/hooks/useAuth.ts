/**
 * Authentication Hooks using React Query
 * Prevents duplicate /api/v1/users/me calls
 */

import { useQuery } from '@tanstack/react-query';
import { authService, User } from '../../../shared/services/authService';

/**
 * Hook to fetch current user data
 * Uses React Query for caching and deduplication
 */
export function useCurrentUser() {
  return useQuery<User>({
    queryKey: ['auth', 'currentUser'],
    queryFn: () => authService.getCurrentUser(),
    enabled: authService.isAuthenticated(),
    staleTime: 300000, // 5 minutes - user data doesn't change frequently
    retry: 1,
    // Don't refetch on window focus for user data
    refetchOnWindowFocus: false,
  });
}
