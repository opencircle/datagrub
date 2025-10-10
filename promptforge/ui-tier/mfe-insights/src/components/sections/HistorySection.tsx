import React, { useState } from 'react';
import { History, Search, Calendar, DollarSign, Shield, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { useAnalysisHistory } from '../../hooks/useInsights';
import type { CallInsightsHistoryItem } from '../../types/insights';

interface Props {
  onSelectAnalysis: (analysisId: string) => void;
}

/**
 * History Section - Display and search previous analyses
 *
 * Features:
 * - Tabular view of last 10 analyses
 * - Search by title or transcript text
 * - Filter by project UUID
 * - View previous analysis capability
 * - Collapsible to save space
 */
export const HistorySection: React.FC<Props> = ({ onSelectAnalysis }) => {
  const [searchText, setSearchText] = useState('');
  const [projectFilter, setProjectFilter] = useState('');
  const [isExpanded, setIsExpanded] = useState(true);

  const { data: history, isLoading, error } = useAnalysisHistory({
    search: searchText || undefined,
    project_id: projectFilter || undefined,
    limit: 10,
  });

  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden">
      {/* Header - Collapsible */}
      <div
        className="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-[#FF385C]" />
          <h3 className="font-semibold text-neutral-700">Recent Analyses</h3>
          {history && history.length > 0 && (
            <span className="text-sm text-neutral-500">({history.length})</span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-neutral-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-neutral-400" />
        )}
      </div>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="px-6 pb-6 space-y-4 border-t border-neutral-100">
          {/* Search and Filters */}
          <div className="flex gap-3 pt-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <input
                  type="text"
                  placeholder="Search by title or transcript..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  className="w-full h-10 pl-10 pr-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
                />
              </div>
            </div>
            <div className="w-64">
              <input
                type="text"
                placeholder="Filter by project UUID"
                value={projectFilter}
                onChange={(e) => setProjectFilter(e.target.value)}
                className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
              />
            </div>
          </div>

          {/* History Table */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF385C] mx-auto mb-3"></div>
                <p className="text-neutral-500 text-sm">Loading history...</p>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-8 px-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">Failed to load history</p>
            </div>
          ) : !history || history.length === 0 ? (
            <div className="text-center py-12 px-4">
              <History className="h-12 w-12 text-neutral-300 mx-auto mb-3" />
              <p className="text-neutral-500 text-sm">No analyses found</p>
              {(searchText || projectFilter) && (
                <p className="text-neutral-400 text-xs mt-1">Try adjusting your search filters</p>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-200">
              <table className="w-full">
                <thead className="bg-neutral-50 border-b border-neutral-200">
                  <tr>
                    <th className="text-left p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Title
                    </th>
                    <th className="text-left p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Preview
                    </th>
                    <th className="text-center p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Tokens
                    </th>
                    <th className="text-center p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Cost
                    </th>
                    <th className="text-center p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Date
                    </th>
                    <th className="text-center p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {history.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-neutral-50 transition-colors"
                    >
                      <td className="p-3">
                        <div className="flex flex-col gap-1">
                          <div className="font-medium text-sm text-neutral-700">
                            {item.transcript_title || (
                              <span className="text-neutral-400 italic">Untitled</span>
                            )}
                          </div>
                          {item.pii_redacted && (
                            <div className="flex items-center gap-1 text-xs text-green-600">
                              <Shield className="h-3 w-3" />
                              PII Redacted
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="text-sm text-neutral-600 max-w-md truncate">
                          {item.transcript_preview}
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <div className="text-sm font-mono text-neutral-700">
                          {item.total_tokens.toLocaleString()}
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <div className="text-sm font-mono text-neutral-700">
                          ${item.total_cost.toFixed(4)}
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <div className="flex flex-col items-center gap-0.5">
                          <div className="text-sm text-neutral-700">
                            {new Date(item.created_at).toLocaleDateString()}
                          </div>
                          <div className="text-xs text-neutral-500">
                            {new Date(item.created_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => onSelectAnalysis(item.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold text-[#FF385C] hover:bg-[#FF385C] hover:text-white transition-all duration-200 border border-[#FF385C]"
                        >
                          <Eye className="h-4 w-4" />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HistorySection;
