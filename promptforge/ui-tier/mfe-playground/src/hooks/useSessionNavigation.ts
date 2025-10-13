import { useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

interface UseSessionNavigationReturn {
  // Current session ID from URL
  sessionId: string | null;

  // Navigate to a specific session
  navigateToSession: (sessionId: string) => void;

  // Navigate back to playground home
  navigateToHome: () => void;

  // Check if currently viewing a session
  isViewingSession: boolean;
}

/**
 * Custom hook for session deep linking and navigation
 *
 * Handles:
 * - URL parameter parsing (session=<id>)
 * - Programmatic navigation to sessions
 * - Browser back button support
 * - Bookmarkable URLs
 *
 * @example
 * const { sessionId, navigateToSession, navigateToHome, isViewingSession } = useSessionNavigation();
 *
 * // Navigate to session
 * navigateToSession('abc-123-def-456');
 *
 * // Navigate back to home
 * navigateToHome();
 *
 * // Check if viewing a session
 * if (isViewingSession) {
 *   // Show session-specific UI
 * }
 */
export function useSessionNavigation(): UseSessionNavigationReturn {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Extract session ID from URL
  const sessionId = useMemo(() => {
    return searchParams.get('session');
  }, [searchParams]);

  const isViewingSession = sessionId !== null;

  // Navigate to a specific session (updates URL)
  const navigateToSession = (id: string) => {
    setSearchParams({ session: id });
  };

  // Navigate back to playground home (clears URL params)
  const navigateToHome = () => {
    navigate('/playground', { replace: false });
  };

  return {
    sessionId,
    navigateToSession,
    navigateToHome,
    isViewingSession,
  };
}
