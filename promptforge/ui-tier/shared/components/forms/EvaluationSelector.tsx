import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Check, ChevronDown, X, Loader, AlertCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { evaluationCatalogService, EvaluationMetadata } from '../../services/evaluationCatalogService';

export interface EvaluationSelectorProps {
  selectedEvaluationIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

export const EvaluationSelector: React.FC<EvaluationSelectorProps> = ({
  selectedEvaluationIds,
  onSelectionChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [tagsFilter, setTagsFilter] = useState<string>('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch available evaluations
  const { data: evaluations = [], isLoading } = useQuery({
    queryKey: ['evaluation-catalog', { is_active: true }],
    queryFn: () => evaluationCatalogService.getCatalog({ is_active: true }),
    staleTime: 60000,
    retry: 1,
  });

  // Extract unique categories and sources for filter dropdowns
  const categories = useMemo(() => {
    const uniqueCategories = [...new Set(evaluations.map(e => e.category))];
    return uniqueCategories.sort();
  }, [evaluations]);

  const sources = useMemo(() => {
    const uniqueSources = [...new Set(evaluations.map(e => e.source))];
    return uniqueSources.sort();
  }, [evaluations]);

  // Filter evaluations based on active filters
  const filteredEvaluations = useMemo(() => {
    return evaluations.filter(evaluation => {
      if (categoryFilter && evaluation.category !== categoryFilter) return false;
      if (sourceFilter && evaluation.source !== sourceFilter) return false;
      if (tagsFilter && evaluation.tags) {
        const hasMatchingTag = evaluation.tags.some(tag =>
          tag.toLowerCase().includes(tagsFilter.toLowerCase())
        );
        if (!hasMatchingTag) return false;
      }
      return true;
    });
  }, [evaluations, categoryFilter, sourceFilter, tagsFilter]);

  const selectedEvaluations = evaluations.filter((e) =>
    selectedEvaluationIds.includes(e.id)
  );

  const activeFilterCount = [categoryFilter, sourceFilter, tagsFilter].filter(Boolean).length;

  const handleToggleEvaluation = (evaluationId: string) => {
    if (selectedEvaluationIds.includes(evaluationId)) {
      onSelectionChange(selectedEvaluationIds.filter((id) => id !== evaluationId));
    } else {
      onSelectionChange([...selectedEvaluationIds, evaluationId]);
    }
  };

  const handleRemove = (evaluationId: string) => {
    onSelectionChange(selectedEvaluationIds.filter((id) => id !== evaluationId));
  };

  const handleClearFilters = () => {
    setCategoryFilter('');
    setSourceFilter('');
    setTagsFilter('');
  };

  const handleCloseDropdown = () => {
    setIsOpen(false);
    // Reset filters to initial view when clicking outside
    handleClearFilters();
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        handleCloseDropdown();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen]);

  const sourceBadgeStyles: Record<string, string> = {
    vendor: 'bg-blue-50 text-blue-700 border border-blue-200',
    custom: 'bg-purple-50 text-purple-700 border border-purple-200',
    promptforge: 'bg-pink-50 text-pink-700 border border-pink-200',
    llm_judge: 'bg-amber-50 text-amber-700 border border-amber-200',
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Label */}
      <label className="block text-sm font-semibold text-neutral-700 mb-2">
        Evaluations (Optional)
      </label>

      {/* Selected Evaluations Display */}
      {selectedEvaluations.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {selectedEvaluations.map((evaluation) => (
            <div
              key={evaluation.id}
              className="flex items-center gap-1 bg-[#FF385C]/10 text-[#FF385C] text-xs px-2 py-1 rounded-lg border border-[#FF385C]/20"
            >
              <span className="font-medium">{evaluation.name}</span>
              <button
                onClick={() => handleRemove(evaluation.id)}
                className="hover:bg-[#FF385C]/20 rounded p-0.5 transition-colors"
                aria-label={`Remove ${evaluation.name}`}
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Filter Controls */}
      <div className="flex flex-wrap gap-3 mb-3">
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="h-10 px-3 rounded-xl border border-neutral-200 text-sm text-neutral-700 bg-white hover:border-[#FF385C] focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200"
          aria-label="Filter by category"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        <select
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          className="h-10 px-3 rounded-xl border border-neutral-200 text-sm text-neutral-700 bg-white hover:border-[#FF385C] focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200"
          aria-label="Filter by source"
        >
          <option value="">All Sources</option>
          {sources.map((src) => (
            <option key={src} value={src}>
              {src}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Filter by tags..."
          value={tagsFilter}
          onChange={(e) => setTagsFilter(e.target.value)}
          className="flex-1 min-w-[200px] h-10 px-3 rounded-xl border border-neutral-200 text-sm text-neutral-700 placeholder:text-neutral-400 hover:border-[#FF385C] focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200"
          aria-label="Filter by tags"
        />

        {activeFilterCount > 0 && (
          <button
            type="button"
            onClick={handleClearFilters}
            className="h-10 px-4 rounded-xl border border-neutral-200 text-sm font-medium text-neutral-700 bg-white hover:bg-neutral-50 hover:border-[#FF385C] focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 flex items-center gap-2"
            aria-label="Clear all filters"
          >
            <X className="h-4 w-4" />
            Clear Filters ({activeFilterCount})
          </button>
        )}
      </div>

      {/* Dropdown Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between h-10 px-3 rounded-xl border border-neutral-200 text-neutral-700 bg-white hover:border-[#FF385C] focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200"
      >
        <span className="text-sm text-neutral-600">
          {selectedEvaluationIds.length > 0
            ? `${selectedEvaluationIds.length} evaluation${selectedEvaluationIds.length !== 1 ? 's' : ''} selected`
            : 'Select evaluations to run'}
        </span>
        <ChevronDown
          className={`h-4 w-4 text-neutral-500 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu - Table View */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-neutral-200 rounded-xl shadow-lg max-h-96 overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <Loader className="h-6 w-6 text-[#FF385C] animate-spin" />
              <span className="ml-3 text-sm text-neutral-600">Loading evaluations...</span>
            </div>
          ) : evaluations.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8">
              <AlertCircle className="h-8 w-8 text-neutral-400 mb-2" />
              <span className="text-sm text-neutral-600 font-medium">No evaluations available</span>
              <span className="text-xs text-neutral-500 mt-1">Check back later or contact support</span>
            </div>
          ) : filteredEvaluations.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8">
              <AlertCircle className="h-8 w-8 text-neutral-400 mb-2" />
              <span className="text-sm text-neutral-600 font-medium">No evaluations match your filters</span>
              <button
                type="button"
                onClick={handleClearFilters}
                className="mt-3 text-xs text-[#FF385C] font-medium hover:underline"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="overflow-y-auto max-h-96">
              <table className="w-full border-collapse">
                <thead className="sticky top-0 bg-neutral-50 border-b-2 border-neutral-200 z-10">
                  <tr>
                    <th className="w-12 px-3 py-3 text-left">
                      <span className="sr-only">Select</span>
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Tags
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                      Type
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-100">
                  {filteredEvaluations.map((evaluation) => {
                    const isSelected = selectedEvaluationIds.includes(evaluation.id);
                    return (
                      <tr
                        key={evaluation.id}
                        onClick={() => handleToggleEvaluation(evaluation.id)}
                        className={`cursor-pointer transition-colors hover:bg-neutral-50 ${
                          isSelected ? 'bg-[#FF385C]/5' : ''
                        }`}
                        role="button"
                        tabIndex={0}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handleToggleEvaluation(evaluation.id);
                          }
                        }}
                        aria-label={`${isSelected ? 'Deselect' : 'Select'} ${evaluation.name}`}
                      >
                        <td className="px-3 py-3">
                          <div
                            className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                              isSelected
                                ? 'bg-[#FF385C] border-[#FF385C]'
                                : 'border-neutral-300'
                            }`}
                          >
                            {isSelected && <Check className="h-3 w-3 text-white" />}
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          <div className="text-sm font-semibold text-neutral-700">
                            {evaluation.name}
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          <div className="text-xs text-neutral-600 line-clamp-2 max-w-xs">
                            {evaluation.description || '—'}
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-neutral-100 text-neutral-700 border border-neutral-200">
                            {evaluation.category}
                          </span>
                        </td>
                        <td className="px-3 py-3">
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
                              sourceBadgeStyles[evaluation.source] || 'bg-neutral-100 text-neutral-700 border border-neutral-200'
                            }`}
                          >
                            {evaluation.source}
                          </span>
                        </td>
                        <td className="px-3 py-3">
                          {evaluation.tags && evaluation.tags.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                              {evaluation.tags.slice(0, 2).map((tag, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-neutral-100 text-neutral-600"
                                >
                                  {tag}
                                </span>
                              ))}
                              {evaluation.tags.length > 2 && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-neutral-100 text-neutral-600">
                                  +{evaluation.tags.length - 2}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-neutral-400">—</span>
                          )}
                        </td>
                        <td className="px-3 py-3">
                          <span className="text-xs text-neutral-600 capitalize">
                            {evaluation.evaluation_type || '—'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EvaluationSelector;
