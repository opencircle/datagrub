import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PlaygroundEnhanced from './PlaygroundEnhanced';

/**
 * App Router for mfe-playground
 *
 * IMPORTANT: Routes are relative to Shell's /playground/* mounting point
 * Shell route: <Route path="playground/*" element={<PlaygroundApp />} />
 * This means our "/" actually maps to "/playground" in the browser
 *
 * Routes (browser URLs):
 * - /playground - Main playground page (session list + new session form)
 * - /playground?session={id} - Deep link to specific session (via URL params)
 *
 * URL State Management:
 * - All URLs are absolute (include /playground prefix)
 * - Browser back button fully functional
 * - Bookmarkable URLs for all views
 */
export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Main playground page with all features */}
      <Route index element={<PlaygroundEnhanced />} />

      {/* 404 fallback - redirect to playground home */}
      <Route path="*" element={<Navigate to="/playground" replace />} />
    </Routes>
  );
};
