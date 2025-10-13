import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import InsightsPage from './components/InsightsPage';

/**
 * App Router for mfe-insights
 *
 * IMPORTANT: Routes are relative to Shell's /insights/* mounting point
 * Shell route: <Route path="insights/*" element={<InsightsApp />} />
 * This means our "/" actually maps to "/insights" in the browser
 *
 * Routes (browser URLs):
 * - /insights - Main insights page (analysis form + history)
 * - /insights/analysis/:analysisId - Deep link to specific analysis
 * - /insights/compare - Comparison selector
 * - /insights/compare/:analysisIdA/:analysisIdB - Ad-hoc comparison
 * - /insights/comparisons/:comparisonId - View saved comparison
 *
 * URL State Management:
 * - All URLs are absolute (include /insights prefix)
 * - Browser back button fully functional
 * - Bookmarkable URLs for all views
 */
export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Main insights page - handles all views via internal state */}
      <Route index element={<InsightsPage />} />

      {/* Deep link routes - handled by InsightsPage with URL params */}
      <Route path="analysis/:analysisId" element={<InsightsPage />} />
      <Route path="compare" element={<InsightsPage />} />
      <Route path="compare/:analysisIdA/:analysisIdB" element={<InsightsPage />} />
      <Route path="comparisons/:comparisonId" element={<InsightsPage />} />

      {/* 404 fallback - redirect to insights home */}
      <Route path="*" element={<Navigate to="/insights" replace />} />
    </Routes>
  );
};
