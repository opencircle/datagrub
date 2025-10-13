import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Loader2, AlertCircle, GitCompare } from 'lucide-react';
import { useComparisonById } from '../../hooks/useComparisons';
import { ComparisonResults } from '../comparison/ComparisonResults';
import { ComparisonSelector } from '../comparison/ComparisonSelector';
import { ComparisonHistory } from '../comparison/ComparisonHistory';

interface Props {
  comparisonId?: string;
  preselectedAnalysisAId?: string;
  preselectedAnalysisBId?: string;
  onBack?: () => void;
  onViewAnalysis?: (analysisId: string) => void;
}

/**
 * Comparison Page
 *
 * Main page for model comparison feature with:
 * - Create new comparisons (ComparisonSelector)
 * - View comparison results (ComparisonResults with radar charts)
 * - Browse comparison history (ComparisonHistory)
 *
 * Supports:
 * - Deep-linking to specific comparisons via comparisonId prop
 * - Pre-selection of analyses for seamless navigation from history
 */
export const ComparisonPage: React.FC<Props> = ({
  comparisonId: initialComparisonId,
  preselectedAnalysisAId,
  preselectedAnalysisBId,
  onBack,
  onViewAnalysis,
}) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState<'create' | 'history' | 'view'>(
    initialComparisonId ? 'view' : 'create'
  );
  const [activeComparisonId, setActiveComparisonId] = useState<string | null>(
    initialComparisonId || null
  );

  // Detect view mode from URL query parameter
  useEffect(() => {
    const viewParam = searchParams.get('view');
    if (viewParam === 'history') {
      setViewMode('history');
      setActiveComparisonId(null);
    } else if (viewParam === 'create' || (!viewParam && !initialComparisonId)) {
      setViewMode('create');
      setActiveComparisonId(null);
    } else if (initialComparisonId && !viewParam) {
      // When navigating directly to a comparison ID without a view param, ensure view mode
      setViewMode('view');
      setActiveComparisonId(initialComparisonId);
    }
  }, [searchParams, initialComparisonId]);

  const {
    data: comparison,
    isLoading,
    isError,
    error,
  } = useComparisonById(activeComparisonId, viewMode === 'view');

  const handleComparisonCreated = (comparisonId: string) => {
    // Navigate to the comparison deep link
    navigate(`/insights/comparisons/${comparisonId}`);
  };

  const handleViewComparison = (comparisonId: string) => {
    // Navigate to the comparison deep link
    navigate(`/insights/comparisons/${comparisonId}`);
  };

  const handleBackToList = () => {
    // Navigate back to comparison history
    navigate('/insights/compare?view=history');
  };

  return (
    <div className="min-h-screen bg-neutral-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {onBack && (
                <button
                  onClick={onBack}
                  className="p-2 hover:bg-white rounded-lg transition-colors border border-neutral-200"
                  title="Back"
                >
                  <ArrowLeft className="h-5 w-5 text-neutral-600" />
                </button>
              )}
              <div>
                <h1 className="text-3xl font-bold text-neutral-800 flex items-center gap-3">
                  <GitCompare className="h-8 w-8 text-[#FF385C]" />
                  Model Comparison
                </h1>
                <p className="text-neutral-600 mt-1">
                  Compare different models or parameters on the same transcript
                </p>
              </div>
            </div>

            {/* View Mode Tabs */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate('/insights/compare?view=create')}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                  viewMode === 'create'
                    ? 'bg-[#FF385C] text-white'
                    : 'bg-white text-neutral-700 border border-neutral-300 hover:border-[#FF385C]'
                }`}
              >
                Create Comparison
              </button>
              <button
                onClick={() => navigate('/insights/compare?view=history')}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                  viewMode === 'history'
                    ? 'bg-[#FF385C] text-white'
                    : 'bg-white text-neutral-700 border border-neutral-300 hover:border-[#FF385C]'
                }`}
              >
                History
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {viewMode === 'create' && (
          <div className="space-y-6">
            <ComparisonSelector
              onComparisonCreated={handleComparisonCreated}
              preselectedAnalysisAId={preselectedAnalysisAId}
              preselectedAnalysisBId={preselectedAnalysisBId}
            />
          </div>
        )}

        {viewMode === 'history' && (
          <div className="space-y-6">
            <ComparisonHistory onViewComparison={handleViewComparison} />
          </div>
        )}

        {viewMode === 'view' && (
          <div className="space-y-6">
            {/* Back to List Button */}
            <div>
              <button
                onClick={handleBackToList}
                className="flex items-center gap-2 text-sm text-neutral-600 hover:text-[#FF385C] transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to History
              </button>
            </div>

            {/* Comparison Results or Loading State */}
            {isLoading ? (
              <div className="bg-white border border-neutral-200 rounded-xl p-12">
                <div className="flex flex-col items-center justify-center">
                  <Loader2 className="h-8 w-8 animate-spin text-[#FF385C] mb-4" />
                  <p className="text-neutral-600">Loading comparison...</p>
                </div>
              </div>
            ) : isError ? (
              <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-900 mb-1">
                      Failed to Load Comparison
                    </h3>
                    <p className="text-sm text-red-800">
                      {error instanceof Error ? error.message : 'An unexpected error occurred'}
                    </p>
                    <button
                      onClick={handleBackToList}
                      className="mt-3 px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Back to History
                    </button>
                  </div>
                </div>
              </div>
            ) : comparison ? (
              <ComparisonResults comparison={comparison} />
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparisonPage;
