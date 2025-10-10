import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from './store';
import { loginSuccess } from './store/slices/authSlice';
import { authService } from '../../shared/services/authService';
import { useCurrentUser } from './hooks/useAuth';
import { ErrorBoundary } from './components/ErrorBoundary';
import { MainLayout } from './components/Layout/MainLayout';
import { LoginReal } from './pages/LoginReal';
import { Dashboard } from './pages/Dashboard';
import { NotFound } from './pages/NotFound';
import { ProjectsApp } from './components/RemoteComponents/ProjectsApp';
import { EvaluationsApp } from './components/RemoteComponents/EvaluationsApp';
import { PlaygroundApp } from './components/RemoteComponents/PlaygroundApp';
import { TracesApp } from './components/RemoteComponents/TracesApp';
import { PolicyApp } from './components/RemoteComponents/PolicyApp';
import { ModelsApp } from './components/RemoteComponents/ModelsApp';
import { InsightsApp } from './components/RemoteComponents/InsightsApp';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { mode } = useSelector((state: RootState) => state.theme);

  // Fetch current user using React Query (prevents duplicate calls)
  const { data: user, error: userError } = useCurrentUser();

  // Update Redux store when user data is loaded
  useEffect(() => {
    if (user) {
      dispatch(loginSuccess({
        id: user.id,
        email: user.email,
        name: user.full_name || user.email,
        organization: user.organization_id,
        role: user.role,
      }));
    } else if (userError) {
      // Token invalid, clear and redirect to login
      authService.logout();
    }
  }, [user, userError, dispatch]);

  // Apply theme
  useEffect(() => {
    if (mode === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [mode]);

  return (
    <ErrorBoundary>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={<LoginReal />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <MainLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects/*" element={<ProjectsApp />} />
            <Route path="evaluations/*" element={<EvaluationsApp />} />
            <Route path="playground/*" element={<PlaygroundApp />} />
            <Route path="traces/*" element={<TracesApp />} />
            <Route path="policy/*" element={<PolicyApp />} />
            <Route path="models/*" element={<ModelsApp />} />
            <Route path="insights/*" element={<InsightsApp />} />
          </Route>
          {/* 404 - Must be last */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
