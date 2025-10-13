import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, Search, Calendar, DollarSign, Shield, Eye, ChevronDown, ChevronUp, GitCompare, Pencil, Check, X } from 'lucide-react';
import { useAnalysisHistory } from '../../hooks/useInsights';
import { updateAnalysisTitle } from '../../services/insightsService';
import type { CallInsightsHistoryItem } from '../../types/insights';

interface Props {
  onSelectAnalysis: (analysisId: string) => void;
  onCompareAnalyses?: (analysisAId: string, analysisBId: string) => void;
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
export const HistorySection: React.FC<Props> = ({ onSelectAnalysis, onCompareAnalyses }) => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [projectFilter, setProjectFilter] = useState('');
  const [isExpanded, setIsExpanded] = useState(true);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const { data: history, isLoading, error, refetch } = useAnalysisHistory({
    search: searchText || undefined,
    project_id: projectFilter || undefined,
    limit: 10,
  });

  const handleToggleCompareMode = () => {
    setCompareMode(!compareMode);
    setSelectedForCompare([]);
  };

  const handleCheckboxChange = (analysisId: string) => {
    setSelectedForCompare((prev) => {
      if (prev.includes(analysisId)) {
        return prev.filter((id) => id !== analysisId);
      }
      if (prev.length < 2) {
        return [...prev, analysisId];
      }
      return prev;
    });
  };

  const handleCompare = () => {
    if (selectedForCompare.length === 2 && onCompareAnalyses) {
      onCompareAnalyses(selectedForCompare[0], selectedForCompare[1]);
      setCompareMode(false);
      setSelectedForCompare([]);
    }
  };

  const handleStartEdit = (item: CallInsightsHistoryItem) => {
    setEditingId(item.id);
    setEditingTitle(item.transcript_title || '');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingTitle('');
  };

  const handleSaveEdit = async (analysisId: string) => {
    if (!editingTitle.trim()) {
      alert('Title cannot be empty');
      return;
    }

    setIsUpdating(true);
    try {
      await updateAnalysisTitle(analysisId, editingTitle.trim());
      setEditingId(null);
      setEditingTitle('');
      // Refetch history to show updated title
      await refetch();
    } catch (error) {
      console.error('Failed to update title:', error);
      alert(`Failed to update title: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUpdating(false);
    }
  };

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
          {/* Search and Filters + Compare Button */}
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
            {onCompareAnalyses && (
              <button
                onClick={handleToggleCompareMode}
                className={`px-4 h-10 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center gap-2 ${
                  compareMode
                    ? 'bg-[#FF385C] text-white hover:bg-[#E31C5F]'
                    : 'bg-white text-[#FF385C] border-2 border-[#FF385C] hover:bg-pink-50'
                }`}
              >
                <GitCompare className="h-4 w-4" />
                {compareMode ? 'Cancel' : 'Compare'}
              </button>
            )}
          </div>

          {/* Compare Mode Instructions */}
          {compareMode && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>Compare Mode:</strong> Select 2 analyses to compare ({selectedForCompare.length}/2 selected)
              </p>
              {selectedForCompare.length === 2 && (
                <button
                  onClick={handleCompare}
                  className="mt-3 px-4 py-2 bg-[#FF385C] text-white font-semibold rounded-lg hover:bg-[#E31C5F] transition-colors flex items-center gap-2"
                >
                  <GitCompare className="h-4 w-4" />
                  Compare Selected Analyses
                </button>
              )}
            </div>
          )}

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
                    {compareMode && (
                      <th className="text-center p-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide">
                        Select
                      </th>
                    )}
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
                      {compareMode && (
                        <td className="p-3 text-center">
                          <input
                            type="checkbox"
                            checked={selectedForCompare.includes(item.id)}
                            onChange={() => handleCheckboxChange(item.id)}
                            disabled={
                              selectedForCompare.length >= 2 && !selectedForCompare.includes(item.id)
                            }
                            className="h-4 w-4 text-[#FF385C] focus:ring-[#FF385C] border-neutral-300 rounded cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                          />
                        </td>
                      )}
                      <td className="p-3">
                        <div className="flex flex-col gap-1">
                          {editingId === item.id ? (
                            <div className="flex items-center gap-2">
                              <input
                                type="text"
                                value={editingTitle}
                                onChange={(e) => setEditingTitle(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    handleSaveEdit(item.id);
                                  } else if (e.key === 'Escape') {
                                    handleCancelEdit();
                                  }
                                }}
                                disabled={isUpdating}
                                className="flex-1 px-2 py-1 text-sm border border-[#FF385C] rounded focus:outline-none focus:ring-2 focus:ring-[#FF385C]/30"
                                autoFocus
                              />
                              <button
                                onClick={() => handleSaveEdit(item.id)}
                                disabled={isUpdating}
                                className="p-1 text-green-600 hover:bg-green-50 rounded transition-colors disabled:opacity-50"
                                title="Save"
                              >
                                <Check className="h-4 w-4" />
                              </button>
                              <button
                                onClick={handleCancelEdit}
                                disabled={isUpdating}
                                className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                                title="Cancel"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2 group">
                              <div className="font-medium text-sm text-neutral-700">
                                {item.transcript_title || (
                                  <span className="text-neutral-400 italic">Untitled</span>
                                )}
                              </div>
                              {!compareMode && (
                                <button
                                  onClick={() => handleStartEdit(item)}
                                  className="opacity-0 group-hover:opacity-100 p-1 text-neutral-500 hover:text-[#FF385C] hover:bg-pink-50 rounded transition-all"
                                  title="Rename"
                                >
                                  <Pencil className="h-3 w-3" />
                                </button>
                              )}
                            </div>
                          )}
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
                        {!compareMode && (
                          <button
                            onClick={() => navigate(`/insights/analysis/${item.id}`)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold text-[#FF385C] hover:bg-[#FF385C] hover:text-white transition-all duration-200 border border-[#FF385C]"
                          >
                            <Eye className="h-4 w-4" />
                            View
                          </button>
                        )}
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
