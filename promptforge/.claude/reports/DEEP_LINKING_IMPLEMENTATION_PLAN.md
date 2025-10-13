# Deep Linking Implementation Plan

**Version**: 1.0.0
**Date**: 2025-10-12
**Priority**: P0 (CRITICAL)
**Estimated Effort**: 80-120 hours (2-3 weeks with 2 developers)

---

## Overview

This document provides a **step-by-step implementation plan** for adding deep linking and proper routing to all PromptForge micro-frontends (MFEs). The plan prioritizes critical features first (insights, traces) and provides code examples for each implementation.

---

## Phase 1: Foundation (P0 - Week 1)

### Goal
Establish routing foundation in critical MFEs (mfe-insights, mfe-traces) and implement URL state management patterns.

**Estimated Effort**: 40 hours

---

### Task 1.1: Install React Router in All MFEs

**Affected MFEs**: All except mfe-projects (6 MFEs)

**Steps**:
```bash
# Navigate to each MFE directory
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights
npm install react-router-dom@^6.20.0

cd ../mfe-playground
npm install react-router-dom@^6.20.0

cd ../mfe-evaluations
npm install react-router-dom@^6.20.0

cd ../mfe-models
npm install react-router-dom@^6.20.0

cd ../mfe-traces
npm install react-router-dom@^6.20.0

cd ../mfe-policy
npm install react-router-dom@^6.20.0
```

**Verification**:
```bash
# Verify all MFEs have react-router-dom@6.20.0
find /Users/rohitiyer/datagrub/promptforge/ui-tier -name "package.json" -type f -path "*/mfe-*/package.json" -exec grep -H "react-router-dom" {} \;
```

---

### Task 1.2: Create AppRouter for mfe-insights

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/AppRouter.tsx`

**Implementation**:
```typescript
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { InsightsPage } from './components/InsightsPage';
import { AnalysisDetailPage } from './components/pages/AnalysisDetailPage';
import { ComparisonPage } from './components/pages/ComparisonPage';
import { ComparisonDetailPage } from './components/pages/ComparisonDetailPage';
import { HistoryPage } from './components/pages/HistoryPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Main analysis page */}
      <Route path="/" element={<InsightsPage />} />

      {/* Analysis detail */}
      <Route path="/analysis/:analysisId" element={<AnalysisDetailPage />} />

      {/* History */}
      <Route path="/history" element={<HistoryPage />} />

      {/* Comparison selector */}
      <Route path="/compare" element={<ComparisonPage />} />

      {/* Ad-hoc comparison */}
      <Route path="/compare/:analysisIdA/:analysisIdB" element={<ComparisonPage />} />

      {/* Saved comparison detail */}
      <Route path="/comparisons/:comparisonId" element={<ComparisonDetailPage />} />

      {/* 404 fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
```

**Update bootstrap.tsx**:
```typescript
import React from 'react';
import { AppRouter } from './AppRouter';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AppRouter />
    </ErrorBoundary>
  );
};

export default App;
```

**Effort**: 4 hours

---

### Task 1.3: Implement Analysis Detail Route

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/pages/AnalysisDetailPage.tsx`

**Implementation**:
```typescript
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, GitCompare, Download, Edit2 } from 'lucide-react';
import { useAnalysis } from '../../hooks/useInsights';
import { ResultsSection } from '../sections/ResultsSection';
import { TracesSection } from '../sections/TracesSection';

export const AnalysisDetailPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();

  // Fetch analysis by ID using React Query
  const { data: analysis, isLoading, error } = useAnalysis(analysisId);

  useEffect(() => {
    // Update page title
    if (analysis) {
      document.title = `${analysis.transcript_title || 'Analysis'} - PromptForge`;
    }
  }, [analysis]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading analysis...</div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-[#C13515] font-semibold mb-2">Analysis not found</div>
        <button
          onClick={() => navigate('/insights')}
          className="text-[#FF385C] hover:underline"
        >
          Return to Insights
        </button>
      </div>
    );
  }

  const handleCompare = () => {
    // Navigate to comparison selector with this analysis pre-selected
    navigate(`/insights/compare?analysisA=${analysisId}`);
  };

  const resultState = {
    analysisId: analysis.id,
    summary: analysis.summary_output,
    insights: analysis.insights_output,
    facts: analysis.facts_output,
    traces: analysis.traces || [],
    evaluations: analysis.evaluations || [],
    totalTokens: analysis.total_tokens,
    totalCost: analysis.total_cost,
    isLoading: false,
    error: null,
  };

  return (
    <div className="space-y-6">
      {/* Header with back button */}
      <div>
        <button
          onClick={() => navigate('/insights')}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Insights
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-700">
              {analysis.transcript_title || 'Untitled Analysis'}
            </h1>
            <p className="text-neutral-500 mt-2">
              Created {new Date(analysis.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleCompare}
              className="flex items-center gap-2 px-4 py-2 border-2 border-[#FF385C] text-[#FF385C] rounded-lg hover:bg-pink-50 transition-colors font-semibold"
            >
              <GitCompare className="h-4 w-4" />
              Compare
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors font-semibold"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <ResultsSection resultState={resultState} />

      {/* Traces */}
      {resultState.traces.length > 0 && (
        <TracesSection traces={resultState.traces} />
      )}
    </div>
  );
};
```

**Add React Query Hook**:

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/hooks/useInsights.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchAnalysisById } from '../services/insightsService';

// Query keys
export const insightsKeys = {
  all: ['insights'] as const,
  analysis: (id: string) => [...insightsKeys.all, 'analysis', id] as const,
  history: (filters: any) => [...insightsKeys.all, 'history', filters] as const,
  comparisons: () => [...insightsKeys.all, 'comparisons'] as const,
};

// Fetch specific analysis
export function useAnalysis(analysisId: string | undefined) {
  return useQuery({
    queryKey: insightsKeys.analysis(analysisId || ''),
    queryFn: () => fetchAnalysisById(analysisId!),
    enabled: !!analysisId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

**Effort**: 6 hours

---

### Task 1.4: Implement Comparison Routes

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/pages/ComparisonDetailPage.tsx`

**Implementation**:
```typescript
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download } from 'lucide-react';
import { useComparison } from '../../hooks/useComparisons';
import { ComparisonResults } from '../comparison/ComparisonResults';

export const ComparisonDetailPage: React.FC = () => {
  const { comparisonId } = useParams<{ comparisonId: string }>();
  const navigate = useNavigate();

  const { data: comparison, isLoading, error } = useComparison(comparisonId);

  useEffect(() => {
    if (comparison) {
      document.title = `Comparison ${comparison.id.slice(0, 8)} - PromptForge`;
    }
  }, [comparison]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading comparison...</div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-[#C13515] font-semibold mb-2">Comparison not found</div>
        <button
          onClick={() => navigate('/insights')}
          className="text-[#FF385C] hover:underline"
        >
          Return to Insights
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/insights')}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Insights
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-700">
              Comparison Results
            </h1>
            <p className="text-neutral-500 mt-2">
              Created {new Date(comparison.created_at).toLocaleDateString()}
            </p>
          </div>

          <button
            className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors font-semibold"
          >
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      <ComparisonResults comparison={comparison} />
    </div>
  );
};
```

**Update ComparisonPage.tsx to handle URL params**:
```typescript
import React, { useEffect, useState } from 'react';
import { useSearchParams, useParams, useNavigate } from 'react-router-dom';
import { ComparisonSelector } from '../comparison/ComparisonSelector';
import { ComparisonResults } from '../comparison/ComparisonResults';

export const ComparisonPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { analysisIdA, analysisIdB } = useParams<{ analysisIdA?: string; analysisIdB?: string }>();
  const navigate = useNavigate();

  // Pre-selected analyses from URL
  const preselectedA = searchParams.get('analysisA') || analysisIdA;
  const preselectedB = searchParams.get('analysisB') || analysisIdB;

  const [selectedAnalysisA, setSelectedAnalysisA] = useState<string | undefined>(preselectedA || undefined);
  const [selectedAnalysisB, setSelectedAnalysisB] = useState<string | undefined>(preselectedB || undefined);
  const [comparisonId, setComparisonId] = useState<string | undefined>();

  const handleRunComparison = async (idA: string, idB: string) => {
    // Update URL to reflect comparison
    navigate(`/insights/compare/${idA}/${idB}`);

    // Run comparison (handled by ComparisonSelector)
  };

  return (
    <div className="space-y-6">
      <ComparisonSelector
        preselectedAnalysisAId={selectedAnalysisA}
        preselectedAnalysisBId={selectedAnalysisB}
        onRunComparison={handleRunComparison}
        onBack={() => navigate('/insights')}
      />
    </div>
  );
};
```

**Effort**: 8 hours

---

### Task 1.5: Implement History Page with URL Filters

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-insights/src/components/pages/HistoryPage.tsx`

**Implementation**:
```typescript
import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Search, SlidersHorizontal } from 'lucide-react';
import { useAnalysisHistory } from '../../hooks/useInsights';
import { HistoryTable } from '../history/HistoryTable';

export const HistoryPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Extract filter state from URL
  const search = searchParams.get('search') || '';
  const filter = searchParams.get('filter') || '';
  const sort = searchParams.get('sort') || 'date';
  const order = searchParams.get('order') || 'desc';
  const page = parseInt(searchParams.get('page') || '1');

  // Fetch history with URL-based filters (React Query caches by params)
  const { data, isLoading } = useAnalysisHistory({
    search: search || undefined,
    filter: filter || undefined,
    sort_by: sort,
    sort_direction: order as 'asc' | 'desc',
    page,
    page_size: 20,
  });

  const handleSearchChange = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set('search', value);
    } else {
      newParams.delete('search');
    }
    newParams.set('page', '1'); // Reset to page 1 on search
    setSearchParams(newParams);
  };

  const handleFilterChange = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set('filter', value);
    } else {
      newParams.delete('filter');
    }
    newParams.set('page', '1'); // Reset to page 1 on filter
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/insights')}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Insights
        </button>

        <h1 className="text-3xl font-bold text-neutral-700">Analysis History</h1>
        <p className="text-neutral-500 mt-2">View and manage past analyses</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search by title or transcript..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full h-12 pl-12 pr-4 border border-neutral-200 rounded-xl text-neutral-700 bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10"
          />
        </div>

        <select
          value={filter}
          onChange={(e) => handleFilterChange(e.target.value)}
          className="h-12 px-4 border border-neutral-200 rounded-xl text-neutral-700 bg-white focus:outline-none focus:border-[#FF385C]"
        >
          <option value="">All Time</option>
          <option value="today">Today</option>
          <option value="last7days">Last 7 Days</option>
          <option value="last30days">Last 30 Days</option>
        </select>
      </div>

      {/* History Table */}
      <HistoryTable
        analyses={data?.analyses || []}
        isLoading={isLoading}
        currentPage={page}
        totalPages={data ? Math.ceil(data.total / 20) : 0}
        onPageChange={handlePageChange}
        onSelectAnalysis={(id) => navigate(`/insights/analysis/${id}`)}
        onCompareAnalyses={(idA, idB) => navigate(`/insights/compare/${idA}/${idB}`)}
      />
    </div>
  );
};
```

**Effort**: 6 hours

---

### Task 1.6: Implement Traces Detail Route

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/AppRouter.tsx`

**Implementation**:
```typescript
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { TracesListPage } from './pages/TracesListPage';
import { TraceDetailPage } from './pages/TraceDetailPage';
import { TraceSpansPage } from './pages/TraceSpansPage';
import { TraceEvaluationsPage } from './pages/TraceEvaluationsPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* Traces list */}
      <Route path="/" element={<TracesListPage />} />

      {/* Trace detail */}
      <Route path="/:traceId" element={<TraceDetailPage />} />

      {/* Trace spans */}
      <Route path="/:traceId/spans" element={<TraceSpansPage />} />

      {/* Trace evaluations */}
      <Route path="/:traceId/evaluations" element={<TraceEvaluationsPage />} />

      {/* 404 fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
```

**Update App.tsx**:
```typescript
import React from 'react';
import { AppRouter } from './AppRouter';

const App: React.FC = () => {
  return <AppRouter />;
};

export default App;
```

**Rename current App.tsx to TracesListPage.tsx** and update to use URL state:

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/pages/TracesListPage.tsx`

```typescript
import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import FilterBar from '../components/FilterBar';
import TracesTable from '../components/TracesTable';
import Pagination from '../components/Pagination';
import { useTraces } from '../../../shared/hooks/useTraces';

export const TracesListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Extract state from URL (UX-ROUTER-001 pattern)
  const searchQuery = searchParams.get('search') || '';
  const modelFilter = searchParams.get('model') || '';
  const sourceFilter = searchParams.get('source') || '';
  const sortColumn = searchParams.get('sort') || 'timestamp';
  const sortDirection = searchParams.get('order') || 'desc';
  const currentPage = parseInt(searchParams.get('page') || '1');

  const pageSize = 20;

  // Fetch traces with URL-based filters (React Query caches by params)
  const { data, isLoading, error } = useTraces({
    search: searchQuery || undefined,
    model: modelFilter || undefined,
    source_filter: sourceFilter || undefined,
    sort_by: sortColumn,
    sort_direction: sortDirection as 'asc' | 'desc',
    page: currentPage,
    page_size: pageSize,
  });

  const traces = data?.traces || [];
  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  const handleSearchChange = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set('search', value);
    } else {
      newParams.delete('search');
    }
    newParams.set('page', '1'); // Reset to page 1
    setSearchParams(newParams);
  };

  const handleModelFilterChange = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set('model', value);
    } else {
      newParams.delete('model');
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const handleSort = (column: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (sortColumn === column) {
      // Toggle direction
      newParams.set('order', sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      newParams.set('sort', column);
      newParams.set('order', 'desc');
    }
    setSearchParams(newParams);
  };

  const handleRowClick = (traceId: string) => {
    // Navigate to trace detail route (not modal!)
    navigate(`/traces/${traceId}`);
  };

  const handlePageChange = (page: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-800">Traces</h1>
        <p className="text-neutral-500 mt-2 text-base">Monitor LLM request traces and performance</p>
      </div>

      {/* Filter Bar */}
      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        modelFilter={modelFilter}
        onModelFilterChange={handleModelFilterChange}
        sourceFilter={sourceFilter}
        onSourceFilterChange={(value) => {
          const newParams = new URLSearchParams(searchParams);
          if (value) {
            newParams.set('source', value);
          } else {
            newParams.delete('source');
          }
          newParams.set('page', '1');
          setSearchParams(newParams);
        }}
      />

      {/* Error State */}
      {error && (
        <div className="bg-[#C13515]/5 border border-[#C13515]/20 rounded-xl p-4 text-[#C13515]">
          Failed to load traces. Please try again.
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-neutral-600 font-medium">Loading traces...</div>
        </div>
      )}

      {/* Table */}
      {!isLoading && !error && (
        <>
          <TracesTable
            traces={traces}
            sortColumn={sortColumn}
            sortDirection={sortDirection as 'asc' | 'desc'}
            onSort={handleSort}
            onRowClick={handleRowClick}
          />

          {/* Pagination */}
          {data && data.total > pageSize && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalItems={data.total}
              pageSize={pageSize}
              onPageChange={handlePageChange}
            />
          )}

          {/* Empty State */}
          {traces.length === 0 && (
            <div className="text-center py-20 bg-white rounded-2xl border border-neutral-100">
              <p className="text-neutral-500">
                No traces found. {searchQuery || modelFilter || sourceFilter ? 'Try adjusting your filters.' : ''}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};
```

**Effort**: 10 hours

---

### Task 1.7: Implement Trace Detail Page

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/pages/TraceDetailPage.tsx`

**Implementation**:
```typescript
import React, { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Clock, DollarSign, Zap, Activity } from 'lucide-react';
import { useTraceDetail } from '../../../shared/hooks/useTraces';
import { TraceMetadata } from '../components/TraceMetadata';
import { TraceRequestResponse } from '../components/TraceRequestResponse';

export const TraceDetailPage: React.FC = () => {
  const { traceId } = useParams<{ traceId: string }>();
  const navigate = useNavigate();

  const { data: trace, isLoading, error } = useTraceDetail(traceId);

  useEffect(() => {
    if (trace) {
      document.title = `Trace ${trace.request_id || traceId} - PromptForge`;
    }
  }, [trace, traceId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading trace...</div>
      </div>
    );
  }

  if (error || !trace) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-[#C13515] font-semibold mb-2">Trace not found</div>
        <button
          onClick={() => navigate('/traces')}
          className="text-[#FF385C] hover:underline"
        >
          Return to Traces
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/traces')}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Traces
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-700">
              Trace: {trace.request_id || trace.trace_id}
            </h1>
            <p className="text-neutral-500 mt-2">
              {new Date(trace.timestamp).toLocaleString()}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to={`/traces/${traceId}/spans`}
              className="flex items-center gap-2 px-4 py-2 border-2 border-[#FF385C] text-[#FF385C] rounded-lg hover:bg-pink-50 transition-colors font-semibold"
            >
              <Activity className="h-4 w-4" />
              View Spans
            </Link>
            <Link
              to={`/traces/${traceId}/evaluations`}
              className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors font-semibold"
            >
              <Zap className="h-4 w-4" />
              Evaluations
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-neutral-200 rounded-xl p-4">
          <div className="flex items-center gap-2 text-neutral-600 mb-2">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-medium">Duration</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">
            {trace.duration_ms}ms
          </div>
        </div>

        <div className="bg-white border border-neutral-200 rounded-xl p-4">
          <div className="flex items-center gap-2 text-neutral-600 mb-2">
            <DollarSign className="h-4 w-4" />
            <span className="text-sm font-medium">Cost</span>
          </div>
          <div className="text-2xl font-bold text-neutral-800">
            ${trace.cost?.toFixed(4) || '0.0000'}
          </div>
        </div>

        {/* Add more metric cards */}
      </div>

      {/* Trace Metadata */}
      <TraceMetadata trace={trace} />

      {/* Request/Response */}
      <TraceRequestResponse trace={trace} />
    </div>
  );
};
```

**Effort**: 8 hours

---

## Phase 1 Summary

**Total Effort**: 40 hours (1 week with 1 developer)

**Deliverables**:
- ✅ React Router installed in all MFEs
- ✅ mfe-insights routing implemented (6 routes)
- ✅ mfe-traces routing implemented (4 routes)
- ✅ URL state management patterns established
- ✅ React Query integration with URL params
- ✅ Breadcrumb navigation in place

**Key Improvements**:
- Bookmarkable URLs for critical features
- No more duplicate API calls (React Query caching by URL params)
- Browser back button works correctly
- State preserved on refresh

---

## Phase 2: Remaining MFEs (P1 - Week 2)

### Goal
Implement routing in remaining MFEs (playground, evaluations, models, policy).

**Estimated Effort**: 40 hours

---

### Task 2.1: Implement Playground Routing

**Routes**:
- `/playground` - Main playground
- `/playground/session/:sessionId` - Session detail
- `/playground/history` - Session history

**Effort**: 10 hours

---

### Task 2.2: Implement Evaluations Routing

**Routes**:
- `/evaluations/results` - Results list
- `/evaluations/results/:evaluationId` - Result detail
- `/evaluations/catalog` - Catalog
- `/evaluations/catalog/:evaluationId` - Evaluation detail
- `/evaluations/create` - Create custom evaluation

**Effort**: 12 hours

---

### Task 2.3: Implement Models Routing

**Routes**:
- `/models/providers` - Providers list
- `/models/providers/new` - Add provider
- `/models/providers/:providerId` - Provider detail
- `/models/providers/:providerId/edit` - Edit provider
- `/models/analytics` - Analytics

**Effort**: 10 hours

---

### Task 2.4: Implement Policy Routing

**Routes**:
- `/policy/policies` - Policies list
- `/policy/policies/new` - Create policy
- `/policy/policies/:policyId` - Policy detail
- `/policy/violations` - Violations list
- `/policy/violations/:violationId` - Violation detail

**Effort**: 8 hours

---

## Phase 3: Enhancements (P2 - Week 3)

### Goal
Add breadcrumbs, keyboard shortcuts, and URL presets.

**Estimated Effort**: 30 hours

---

### Task 3.1: Implement Breadcrumb Navigation

**Create shared Breadcrumb component**:

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/shared/components/navigation/Breadcrumb.tsx`

```typescript
import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav className="flex items-center gap-2 text-sm text-neutral-600 mb-6" aria-label="Breadcrumb">
      <Link
        to="/dashboard"
        className="flex items-center gap-1 hover:text-neutral-900 transition-colors"
      >
        <Home className="h-4 w-4" />
        <span>Home</span>
      </Link>

      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <React.Fragment key={index}>
            <ChevronRight className="h-4 w-4 text-neutral-400" />
            {isLast || !item.href ? (
              <span className="text-neutral-900 font-medium">{item.label}</span>
            ) : (
              <Link
                to={item.href}
                className="hover:text-neutral-900 transition-colors"
              >
                {item.label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
```

**Usage Example**:
```typescript
import { Breadcrumb } from '../../../shared/components/navigation/Breadcrumb';

// In AnalysisDetailPage
<Breadcrumb
  items={[
    { label: 'Insights', href: '/insights' },
    { label: 'Analysis', href: '/insights/history' },
    { label: analysis.transcript_title || 'Untitled' },
  ]}
/>
```

**Effort**: 8 hours (implement + add to all pages)

---

### Task 3.2: Implement URL Presets

**Examples**:
- `/playground?model=gpt-4&temp=0.7&max=1000`
- `/traces?model=gpt-4&status=error`
- `/evaluations/catalog?category=factual`

**Implementation**: Already handled by URL state management pattern.

**Effort**: 2 hours (documentation only)

---

### Task 3.3: Keyboard Shortcuts for Navigation

**File**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/shared/hooks/useKeyboardShortcuts.ts`

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function useKeyboardShortcuts() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only trigger if no input/textarea is focused
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Cmd/Ctrl + K: Focus search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input (implement in each page)
      }

      // g + i: Go to Insights
      if (e.key === 'g' && !e.metaKey && !e.ctrlKey) {
        const nextKey = new Promise<string>((resolve) => {
          const handler = (e: KeyboardEvent) => {
            resolve(e.key);
            document.removeEventListener('keydown', handler);
          };
          document.addEventListener('keydown', handler);
          setTimeout(() => resolve(''), 1000); // Timeout after 1s
        });

        nextKey.then((key) => {
          if (key === 'i') navigate('/insights');
          if (key === 't') navigate('/traces');
          if (key === 'p') navigate('/projects');
          if (key === 'e') navigate('/evaluations');
        });
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);
}
```

**Effort**: 6 hours

---

### Task 3.4: Add Deep Link Share Buttons

**Component**: Add "Copy Link" button to all detail pages.

```typescript
const handleCopyLink = () => {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  // Show toast notification
};

<button
  onClick={handleCopyLink}
  className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors font-semibold"
>
  <Link2 className="h-4 w-4" />
  Copy Link
</button>
```

**Effort**: 4 hours

---

### Task 3.5: Implement "Open in New Tab" Support

**Requirement**: All detail links should support right-click "Open in new tab".

**Implementation**: Ensure all navigation uses `<Link>` component (not `onClick` handlers).

**Bad**:
```typescript
<div onClick={() => navigate(`/traces/${trace.id}`)}>
```

**Good**:
```typescript
<Link to={`/traces/${trace.id}`}>
```

**Effort**: 6 hours (audit + fix)

---

## Phase 3 Summary

**Total Effort**: 30 hours (1 week with 1 developer)

**Deliverables**:
- ✅ Breadcrumb navigation across all pages
- ✅ Keyboard shortcuts for quick navigation
- ✅ Deep link share buttons
- ✅ "Open in new tab" support

---

## Total Implementation Effort

| Phase | Duration | Effort | Priority |
|-------|----------|--------|----------|
| Phase 1: Foundation | 1 week | 40 hours | P0 (CRITICAL) |
| Phase 2: Remaining MFEs | 1 week | 40 hours | P1 (HIGH) |
| Phase 3: Enhancements | 1 week | 30 hours | P2 (MEDIUM) |
| **TOTAL** | **3 weeks** | **110 hours** | - |

**With 2 developers**: 1.5-2 weeks

---

## Testing Strategy

### Unit Tests

**Example**:
```typescript
describe('AnalysisDetailPage', () => {
  it('should load analysis by ID from URL', () => {
    const { getByText } = render(
      <MemoryRouter initialEntries={['/insights/analysis/123']}>
        <Route path="/insights/analysis/:analysisId" element={<AnalysisDetailPage />} />
      </MemoryRouter>
    );

    expect(getByText('Loading analysis...')).toBeInTheDocument();
  });

  it('should navigate back to insights', () => {
    const { getByText } = render(...);
    fireEvent.click(getByText('Back to Insights'));
    expect(mockNavigate).toHaveBeenCalledWith('/insights');
  });
});
```

### E2E Tests

**Example**:
```typescript
describe('Deep Linking', () => {
  it('should directly navigate to analysis detail', () => {
    cy.visit('/insights/analysis/550e8400-e29b-41d4-a716-446655440000');
    cy.contains('Analysis Detail').should('be.visible');
  });

  it('should preserve filters in URL on refresh', () => {
    cy.visit('/traces?model=gpt-4&status=error&page=2');
    cy.reload();
    cy.url().should('include', 'model=gpt-4');
    cy.url().should('include', 'status=error');
    cy.url().should('include', 'page=2');
  });
});
```

---

## Success Criteria

| Metric | Current | Target | Success |
|--------|---------|--------|---------|
| MFEs with Routing | 1 / 7 | 7 / 7 | ✅ |
| Bookmarkable URLs | 3 | 60+ | ✅ |
| Duplicate API Calls | 50-100/session | <10/session | ✅ |
| Browser Back Button | Broken | Working | ✅ |
| State Preserved on Refresh | 5% | 100% | ✅ |

---

**End of Deep Linking Implementation Plan**
