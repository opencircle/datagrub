import React, { useState } from 'react';
import FilterBar from './components/FilterBar';
import TracesTable from './components/TracesTable';
import Pagination from './components/Pagination';
import TraceDetailModal from './components/TraceDetailModal';
import { useTraces } from '../../shared/hooks/useTraces';
import { TraceListItem } from '../../shared/services/traceService';

const App: React.FC = () => {
  // UI State - separated from server state
  const [searchQuery, setSearchQuery] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<'requestId' | 'status' | 'duration' | 'timestamp'>('timestamp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

  const pageSize = 20;

  // Map UI sort column to API sort_by parameter
  const sortColumnMap: Record<string, string> = {
    requestId: 'requestId',
    status: 'status',
    duration: 'duration',
    timestamp: 'timestamp',
  };

  // Server State - using centralized hooks with REACT-QUERY-001 pattern
  const { data, isLoading, error } = useTraces({
    search: searchQuery || undefined,
    model: modelFilter || undefined,
    source_filter: sourceFilter || undefined,
    sort_by: sortColumnMap[sortColumn],
    sort_direction: sortDirection,
    page: currentPage,
    page_size: pageSize,
  });

  const traces = data?.traces || [];
  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;
  const totalItems = data?.total || 0;

  const handleSort = (column: 'requestId' | 'status' | 'duration' | 'timestamp') => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const handleRowClick = (traceId: string) => {
    setSelectedTraceId(traceId);
  };

  const handleCloseModal = () => {
    setSelectedTraceId(null);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Page Header - Design System: Increased spacing, clearer hierarchy */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-800">Traces</h1>
        <p className="text-neutral-500 mt-2 text-base">Monitor LLM request traces and performance</p>
      </div>

        {/* Filter Bar */}
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          modelFilter={modelFilter}
          onModelFilterChange={setModelFilter}
          sourceFilter={sourceFilter}
          onSourceFilterChange={setSourceFilter}
        />

      {/* Error State - Design System: Softer colors */}
      {error && (
        <div className="bg-[#C13515]/5 border border-[#C13515]/20 rounded-xl p-4 text-[#C13515]">
          Failed to load traces. Please try again.
        </div>
      )}

      {/* Loading State - Design System: Brand colors */}
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
            sortDirection={sortDirection}
            onSort={handleSort}
            onRowClick={handleRowClick}
          />

          {/* Pagination */}
          {totalItems > pageSize && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalItems={totalItems}
              pageSize={pageSize}
              onPageChange={handlePageChange}
            />
          )}

          {/* Empty State - Design System: More spacious, warmer feel */}
          {traces.length === 0 && !isLoading && (
            <div className="text-center py-20 bg-white rounded-2xl border border-neutral-100">
              <p className="text-neutral-500">
                No traces found. {searchQuery || modelFilter || sourceFilter ? 'Try adjusting your filters.' : ''}
              </p>
            </div>
          )}
        </>
      )}

      {/* Trace Detail Modal */}
      {selectedTraceId && (
        <TraceDetailModal
          isOpen={!!selectedTraceId}
          onClose={handleCloseModal}
          traceId={selectedTraceId}
        />
      )}
    </div>
  );
};

export default App;
