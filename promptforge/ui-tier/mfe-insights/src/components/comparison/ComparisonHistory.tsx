import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  Trophy,
  TrendingUp,
  DollarSign,
  Calendar,
  Eye,
  Trash2,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Thermometer,
} from 'lucide-react';
import { useComparisonHistory, useDeleteComparison } from '../../hooks/useComparisons';
import type { ComparisonListItem } from '../../types/insights';

interface Props {
  onViewComparison?: (comparisonId: string) => void;
  limit?: number;
}

/**
 * Comparison History Component - Enhanced Tabular View
 *
 * Displays comprehensive comparison details including:
 * - Model titles and configurations
 * - Stage-wise model and parameter breakdown
 * - Winner, cost, and quality metrics
 * - Judge model information
 * - Expandable rows for detailed parameters
 */
export const ComparisonHistory: React.FC<Props> = ({
  onViewComparison,
  limit: defaultLimit = 20,
}) => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultLimit);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const skip = (currentPage - 1) * pageSize;

  const {
    data: comparisonData,
    isLoading,
    isError,
    error,
  } = useComparisonHistory(skip, pageSize);

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setCurrentPage(1);
  };

  const toggleRowExpansion = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const deleteComparison = useDeleteComparison();

  const handleDelete = async (comparisonId: string, event: React.MouseEvent) => {
    event.stopPropagation();

    if (!confirm('Are you sure you want to delete this comparison?')) {
      return;
    }

    try {
      await deleteComparison.mutateAsync(comparisonId);
    } catch (error) {
      console.error('Failed to delete comparison:', error);
    }
  };

  const getWinnerBadge = (winner: 'A' | 'B' | 'tie') => {
    if (winner === 'tie') {
      return (
        <div className="inline-flex items-center gap-1 bg-neutral-100 border border-neutral-300 rounded px-2 py-1">
          <GitCompare className="h-3 w-3 text-neutral-600" />
          <span className="text-xs font-semibold text-neutral-700">Tie</span>
        </div>
      );
    }

    const isA = winner === 'A';
    return (
      <div className={`inline-flex items-center gap-1 ${isA ? 'bg-blue-50 border-blue-300' : 'bg-green-50 border-green-300'} border rounded px-2 py-1`}>
        <Trophy className={`h-3 w-3 ${isA ? 'text-blue-600' : 'text-green-600'}`} />
        <span className={`text-xs font-semibold ${isA ? 'text-blue-700' : 'text-green-700'}`}>
          Model {winner}
        </span>
      </div>
    );
  };

  const getMetricColor = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-neutral-600';
  };

  const renderParameterBadge = (label: string, value: string | undefined) => {
    if (!value || value === 'N/A') return null;
    return (
      <div className="inline-flex items-center gap-1 bg-neutral-100 border border-neutral-200 rounded px-1.5 py-0.5">
        <span className="text-[10px] text-neutral-500 font-medium">{label}:</span>
        <span className="text-[10px] text-neutral-700 font-semibold">{value}</span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-[#FF385C]" />
        <span className="ml-2 text-neutral-600">Loading comparison history...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900 mb-1">Failed to Load Comparisons</h3>
            <p className="text-sm text-red-800">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!comparisonData || comparisonData.comparisons.length === 0) {
    return (
      <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <GitCompare className="h-5 w-5 text-neutral-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-neutral-800 mb-1">No Comparisons Yet</h3>
            <p className="text-sm text-neutral-600">
              Create your first comparison to see how different models or parameters perform on the
              same transcript.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { comparisons, pagination } = comparisonData;

  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b-2 border-neutral-200 bg-neutral-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitCompare className="h-5 w-5 text-[#FF385C]" />
            <h3 className="font-semibold text-neutral-700">Comparison History</h3>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-neutral-500">
              {pagination.total_count} {pagination.total_count === 1 ? 'comparison' : 'comparisons'}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-neutral-600">Show:</span>
              <select
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="px-3 py-1.5 bg-white border-2 border-neutral-300 rounded-lg text-sm font-semibold text-neutral-700 focus:outline-none focus:border-[#FF385C] transition-colors cursor-pointer hover:border-neutral-400"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-neutral-100 border-b-2 border-neutral-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-bold text-neutral-700 uppercase tracking-wider w-8"></th>
              <th className="px-4 py-3 text-left text-xs font-bold text-neutral-700 uppercase tracking-wider">
                Models & Configuration
              </th>
              <th className="px-4 py-3 text-center text-xs font-bold text-neutral-700 uppercase tracking-wider w-24">
                Winner
              </th>
              <th className="px-4 py-3 text-right text-xs font-bold text-neutral-700 uppercase tracking-wider w-32">
                Cost
              </th>
              <th className="px-4 py-3 text-right text-xs font-bold text-neutral-700 uppercase tracking-wider w-28">
                Quality
              </th>
              <th className="px-4 py-3 text-left text-xs font-bold text-neutral-700 uppercase tracking-wider w-40">
                Judge & Date
              </th>
              <th className="px-4 py-3 text-center text-xs font-bold text-neutral-700 uppercase tracking-wider w-24">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {comparisons.map((comparison) => {
              const isExpanded = expandedRows.has(comparison.id);
              return (
                <React.Fragment key={comparison.id}>
                  {/* Main Row */}
                  <tr className="hover:bg-neutral-50 transition-colors">
                    {/* Expand Toggle */}
                    <td className="px-4 py-4">
                      <button
                        onClick={() => toggleRowExpansion(comparison.id)}
                        className="p-1 hover:bg-neutral-200 rounded transition-colors"
                        title={isExpanded ? 'Collapse details' : 'Expand details'}
                      >
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4 text-neutral-600" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-neutral-600" />
                        )}
                      </button>
                    </td>

                    {/* Models & Configuration */}
                    <td className="px-4 py-4">
                      <div className="space-y-2">
                        {/* Model A */}
                        <div className="flex items-start gap-2">
                          <div className="px-2 py-0.5 bg-blue-50 border border-blue-200 rounded text-[10px] font-bold text-blue-700 flex-shrink-0 mt-0.5">
                            A
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-neutral-800 truncate">
                              {comparison.analysis_a_title || 'Untitled Analysis'}
                            </div>
                            <div className="text-xs text-neutral-600 truncate">
                              {comparison.model_a_summary}
                            </div>
                            {comparison.params_a && (
                              <div className="flex gap-1 mt-1 flex-wrap">
                                {renderParameterBadge('T', comparison.params_a.stage1?.temperature)}
                                {renderParameterBadge('p', comparison.params_a.stage1?.top_p)}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Model B */}
                        <div className="flex items-start gap-2">
                          <div className="px-2 py-0.5 bg-green-50 border border-green-200 rounded text-[10px] font-bold text-green-700 flex-shrink-0 mt-0.5">
                            B
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-neutral-800 truncate">
                              {comparison.analysis_b_title || 'Untitled Analysis'}
                            </div>
                            <div className="text-xs text-neutral-600 truncate">
                              {comparison.model_b_summary}
                            </div>
                            {comparison.params_b && (
                              <div className="flex gap-1 mt-1 flex-wrap">
                                {renderParameterBadge('T', comparison.params_b.stage1?.temperature)}
                                {renderParameterBadge('p', comparison.params_b.stage1?.top_p)}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Winner */}
                    <td className="px-4 py-4 text-center">
                      {getWinnerBadge(comparison.overall_winner)}
                    </td>

                    {/* Cost */}
                    <td className="px-4 py-4 text-right">
                      <div className="text-xs text-neutral-600 mb-1">
                        A: ${comparison.cost_a.toFixed(5)}
                      </div>
                      <div className="text-xs text-neutral-600 mb-1">
                        B: ${comparison.cost_b.toFixed(5)}
                      </div>
                      <div className="flex items-center justify-end gap-1">
                        <DollarSign className="h-3 w-3 text-neutral-500" />
                        <span
                          className={`text-sm font-semibold ${getMetricColor(
                            parseFloat(comparison.cost_difference)
                          )}`}
                        >
                          {comparison.cost_difference}
                        </span>
                      </div>
                    </td>

                    {/* Quality */}
                    <td className="px-4 py-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <TrendingUp className="h-3 w-3 text-neutral-500" />
                        <span
                          className={`text-sm font-semibold ${getMetricColor(
                            parseFloat(comparison.quality_improvement.replace('%', ''))
                          )}`}
                        >
                          {comparison.quality_improvement}
                        </span>
                      </div>
                    </td>

                    {/* Judge & Date */}
                    <td className="px-4 py-4">
                      <div className="text-xs text-neutral-700 font-medium mb-1 truncate" title={comparison.judge_model}>
                        Judge: {comparison.judge_model}
                      </div>
                      <div className="flex items-center gap-1 text-[10px] text-neutral-500">
                        <Calendar className="h-3 w-3" />
                        {new Date(comparison.created_at).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => navigate(`/insights/comparisons/${comparison.id}`)}
                          className="p-2 hover:bg-blue-50 rounded-lg transition-colors"
                          title="View comparison"
                        >
                          <Eye className="h-4 w-4 text-blue-600" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(comparison.id, e)}
                          disabled={deleteComparison.isPending}
                          className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                          title="Delete comparison"
                        >
                          {deleteComparison.isPending ? (
                            <Loader2 className="h-4 w-4 text-red-600 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4 text-red-600" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>

                  {/* Expanded Details Row */}
                  {isExpanded && (
                    <tr className="bg-neutral-50">
                      <td colSpan={7} className="px-4 py-4">
                        <div className="grid grid-cols-2 gap-6">
                          {/* Model A Details */}
                          <div className="bg-white border border-blue-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <div className="px-2 py-1 bg-blue-50 border border-blue-200 rounded text-xs font-bold text-blue-700">
                                Model A
                              </div>
                              <span className="text-sm font-semibold text-neutral-800">
                                {comparison.analysis_a_title || 'Untitled'}
                              </span>
                            </div>

                            <div className="space-y-2">
                              {/* Stage 1 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 1:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_a_stage1}
                                  </div>
                                  {comparison.params_a?.stage1 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_a.stage1.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_a.stage1.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_a.stage1.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Stage 2 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 2:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_a_stage2}
                                  </div>
                                  {comparison.params_a?.stage2 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_a.stage2.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_a.stage2.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_a.stage2.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Stage 3 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 3:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_a_stage3}
                                  </div>
                                  {comparison.params_a?.stage3 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_a.stage3.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_a.stage3.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_a.stage3.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Cost/Tokens Summary */}
                              <div className="pt-2 mt-2 border-t border-neutral-200 flex justify-between text-xs">
                                <span className="text-neutral-600">Total:</span>
                                <div className="flex gap-3">
                                  <span className="text-neutral-700 font-semibold">
                                    {comparison.tokens_a.toLocaleString()} tokens
                                  </span>
                                  <span className="text-neutral-700 font-semibold">
                                    ${comparison.cost_a.toFixed(5)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Model B Details */}
                          <div className="bg-white border border-green-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <div className="px-2 py-1 bg-green-50 border border-green-200 rounded text-xs font-bold text-green-700">
                                Model B
                              </div>
                              <span className="text-sm font-semibold text-neutral-800">
                                {comparison.analysis_b_title || 'Untitled'}
                              </span>
                            </div>

                            <div className="space-y-2">
                              {/* Stage 1 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 1:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_b_stage1}
                                  </div>
                                  {comparison.params_b?.stage1 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_b.stage1.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_b.stage1.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_b.stage1.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Stage 2 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 2:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_b_stage2}
                                  </div>
                                  {comparison.params_b?.stage2 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_b.stage2.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_b.stage2.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_b.stage2.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Stage 3 */}
                              <div className="flex items-start gap-2">
                                <div className="text-[10px] font-bold text-neutral-600 w-16">Stage 3:</div>
                                <div className="flex-1">
                                  <div className="text-xs text-neutral-700 font-medium mb-1">
                                    {comparison.model_b_stage3}
                                  </div>
                                  {comparison.params_b?.stage3 && (
                                    <div className="flex gap-1.5 flex-wrap">
                                      {renderParameterBadge('temp', comparison.params_b.stage3.temperature)}
                                      {renderParameterBadge('top_p', comparison.params_b.stage3.top_p)}
                                      {renderParameterBadge('max_tokens', comparison.params_b.stage3.max_tokens)}
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Cost/Tokens Summary */}
                              <div className="pt-2 mt-2 border-t border-neutral-200 flex justify-between text-xs">
                                <span className="text-neutral-600">Total:</span>
                                <div className="flex gap-3">
                                  <span className="text-neutral-700 font-semibold">
                                    {comparison.tokens_b.toLocaleString()} tokens
                                  </span>
                                  <span className="text-neutral-700 font-semibold">
                                    ${comparison.cost_b.toFixed(5)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="p-6 border-t-2 border-neutral-200 bg-neutral-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-neutral-600">
              Showing {skip + 1}-{Math.min(skip + pageSize, pagination.total_count)} of{' '}
              {pagination.total_count} comparisons
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-white border-2 border-neutral-300 rounded-lg font-semibold text-sm text-neutral-700 hover:border-[#FF385C] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <div className="px-3 py-2 bg-white border border-neutral-200 rounded-lg text-sm font-semibold text-neutral-700">
                Page {pagination.page} of {pagination.total_pages}
              </div>
              <button
                onClick={() => setCurrentPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={currentPage === pagination.total_pages}
                className="px-4 py-2 bg-white border-2 border-neutral-300 rounded-lg font-semibold text-sm text-neutral-700 hover:border-[#FF385C] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonHistory;
