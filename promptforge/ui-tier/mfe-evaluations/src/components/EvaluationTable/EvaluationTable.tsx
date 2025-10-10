/**
 * Enhanced Evaluation Table Component (P0)
 *
 * Features:
 * - Display prompt title, model, vendor, category
 * - Filter by prompt title, vendor, category, status
 * - Sort by timestamp (default: most recent first), score, etc.
 * - Click row to open detail modal
 */

import React, { useState } from 'react';
import {
  EvaluationListItem,
  EvaluationListParams
} from '../../../../shared/services/evaluationService';
import { CheckCircle, XCircle, Clock } from 'lucide-react';
import { EvaluationFilters } from './EvaluationFilters';
import { EvaluationDetailModal } from '../EvaluationDetailModal/EvaluationDetailModal';
import { useEvaluationsList } from '../../hooks/useEvaluations';

interface EvaluationTableProps {
  refreshTrigger?: number;
}

export const EvaluationTable: React.FC<EvaluationTableProps> = ({ refreshTrigger }) => {
  const [selectedEvalId, setSelectedEvalId] = useState<string | null>(null);

  // Filter and pagination state
  const [filters, setFilters] = useState<EvaluationListParams>({
    sort_by: 'timestamp',
    sort_direction: 'desc',
    limit: 20,
    offset: 0,
  });

  // Fetch evaluations using React Query (prevents duplicate calls)
  const {
    data,
    isLoading: loading,
    error: queryError,
    refetch,
  } = useEvaluationsList(filters);

  const evaluations = data?.evaluations || [];
  const total = data?.total || 0;
  const error = queryError ? (queryError instanceof Error ? queryError.message : 'Failed to load evaluations') : null;

  const handleRowClick = (evalId: string) => {
    setSelectedEvalId(evalId);
  };

  const handleSortChange = (column: string) => {
    const newDirection =
      filters.sort_by === column && filters.sort_direction === 'desc'
        ? 'asc'
        : 'desc';

    setFilters({
      ...filters,
      sort_by: column as any,
      sort_direction: newDirection,
    });
  };

  const getStatusIcon = (passed: boolean | null) => {
    if (passed === null) {
      return <Clock className="h-4 w-4 text-gray-400" />;
    }
    return passed
      ? <CheckCircle className="h-4 w-4 text-green-600" />
      : <XCircle className="h-4 w-4 text-red-600" />;
  };

  const getScoreColor = (score: number | null) => {
    if (score === null) return 'text-gray-400';
    if (score >= 0.8) return 'text-green-600 font-semibold';
    if (score >= 0.5) return 'text-yellow-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  const getSortIcon = (column: string) => {
    if (filters.sort_by !== column) return null;
    return filters.sort_direction === 'asc' ? ' ↑' : ' ↓';
  };

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-2">Error loading evaluations</div>
        <div className="text-sm text-gray-600">{error}</div>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="evaluation-table-container">
      {/* Filters */}
      <EvaluationFilters
        filters={filters}
        onChange={setFilters}
        totalResults={total}
      />

      {/* Results Info */}
      <div className="flex items-center justify-between px-6 py-3 bg-gray-50 border-b">
        <div className="text-sm text-gray-600">
          Showing <span className="font-semibold">{evaluations.length}</span> of{' '}
          <span className="font-semibold">{total}</span> evaluations
        </div>
      </div>

      {/* Table - Matches Traces Table Design */}
      <div className="overflow-x-auto bg-white">
        <table className="min-w-full">
          <thead className="border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('timestamp')}>
                <div className="flex items-center gap-1">
                  Status{getSortIcon('timestamp')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('prompt_title')}>
                <div className="flex items-center gap-1">
                  Prompt{getSortIcon('prompt_title')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('evaluation_name')}>
                <div className="flex items-center gap-1">
                  Evaluation{getSortIcon('evaluation_name')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600">
                Vendor
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('category')}>
                <div className="flex items-center gap-1">
                  Category{getSortIcon('category')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('score')}>
                <div className="flex items-center gap-1">
                  Score{getSortIcon('score')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600 cursor-pointer" onClick={() => handleSortChange('model')}>
                <div className="flex items-center gap-1">
                  Model{getSortIcon('model')}
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-normal text-gray-600">
                Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                  <div className="flex items-center justify-center gap-2">
                    <Clock className="h-5 w-5 animate-spin" />
                    Loading evaluations...
                  </div>
                </td>
              </tr>
            ) : evaluations.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                  No evaluations found. Try adjusting your filters.
                </td>
              </tr>
            ) : (
              evaluations.map((evaluation) => (
                <tr
                  key={evaluation.id}
                  onClick={() => handleRowClick(evaluation.id)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRowClick(evaluation.id)}
                  tabIndex={0}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  aria-label={`View evaluation ${evaluation.name}`}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      {getStatusIcon(evaluation.passed)}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{evaluation.prompt_title}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{evaluation.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {evaluation.vendor_name || <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700 capitalize">
                    {evaluation.category || <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700 tabular-nums">
                    <span className={`font-medium ${getScoreColor(evaluation.avg_score)}`}>
                      {evaluation.avg_score !== null ? evaluation.avg_score.toFixed(2) : '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">{evaluation.model}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {formatRelativeTime(evaluation.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > filters.limit! && (
        <div className="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
          <button
            onClick={() => setFilters({ ...filters, offset: Math.max(0, (filters.offset || 0) - filters.limit!) })}
            disabled={!filters.offset}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <div className="text-sm text-gray-600">
            Page {Math.floor((filters.offset || 0) / filters.limit!) + 1} of {Math.ceil(total / filters.limit!)}
          </div>
          <button
            onClick={() => setFilters({ ...filters, offset: (filters.offset || 0) + filters.limit! })}
            disabled={(filters.offset || 0) + filters.limit! >= total}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}

      {/* Detail Modal */}
      {selectedEvalId && (
        <EvaluationDetailModal
          evaluationId={selectedEvalId}
          onClose={() => setSelectedEvalId(null)}
        />
      )}
    </div>
  );
};
