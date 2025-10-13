import React from 'react';
import { AppRouter } from './AppRouter';

/**
 * Bootstrap file for Module Federation
 *
 * IMPORTANT: Shell provides BrowserRouter, so we don't wrap here
 * - Shell already has router with basename routing
 * - MFE uses Routes directly (not Router)
 * - Supports deep linking, bookmarkable URLs, browser back button
 * - All routes defined in AppRouter.tsx with relative paths
 */
const App: React.FC = () => {
  return <AppRouter />;
};

export default App;
