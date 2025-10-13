import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import App from './App';

/**
 * App Router for mfe-traces
 *
 * IMPORTANT: Routes are relative to Shell's /traces/* mounting point
 * Shell route: <Route path="traces/*" element={<TracesApp />} />
 * This means our "/" actually maps to "/traces" in the browser
 *
 * Routes (browser URLs):
 * - /traces - Main traces list page
 * - /traces/:traceId - Deep link to specific trace detail
 *
 * URL State Management:
 * - All URLs are absolute (include /traces prefix)
 * - Browser back button fully functional
 * - Bookmarkable URLs for all views
 */
export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Main traces list page */}
      <Route index element={<App />} />

      {/* Deep link to specific trace */}
      <Route path=":traceId" element={<App />} />

      {/* 404 fallback - redirect to traces home */}
      <Route path="*" element={<Navigate to="/traces" replace />} />
    </Routes>
  );
};
