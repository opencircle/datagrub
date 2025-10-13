import React from 'react';
import { AppRouter } from './AppRouter';

/**
 * Error Boundary for capturing and logging MFE errors
 */
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[Insights MFE Error]:', error, errorInfo);
    console.error('[Error Stack]:', error.stack);
    console.error('[Component Stack]:', errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-96 p-8">
          <div className="max-w-2xl">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-red-700 mb-4">
                Insights Module Error
              </h2>
              <p className="text-red-600 mb-4">
                An error occurred while loading the Insights module. Please check the console for details.
              </p>
              {this.state.error && (
                <div className="bg-red-100 rounded p-4 font-mono text-sm text-red-800 overflow-auto">
                  <div className="font-bold mb-2">Error Message:</div>
                  <div className="mb-4">{this.state.error.message}</div>
                  {this.state.error.stack && (
                    <>
                      <div className="font-bold mb-2">Stack Trace:</div>
                      <pre className="whitespace-pre-wrap text-xs">
                        {this.state.error.stack}
                      </pre>
                    </>
                  )}
                </div>
              )}
              <button
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

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
  return (
    <ErrorBoundary>
      <AppRouter />
    </ErrorBoundary>
  );
};

export default App;
