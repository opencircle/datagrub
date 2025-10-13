/**
 * Evaluation Filters Component (P0)
 *
 * Provides filtering UI for:
 * - Prompt title search (fuzzy, debounced)
 * - Vendor dropdown
 * - Category dropdown
 * - Status dropdown (Pass/Fail/All)
 * - Clear all filters button
 */

import React, { useState, useEffect } from 'react';
import { EvaluationListParams } from '../../../../shared/services/evaluationService';
import { Search, Filter, X } from 'lucide-react';

interface EvaluationFiltersProps {
  filters: EvaluationListParams;
  onChange: (filters: EvaluationListParams) => void;
  totalResults: number;
}

export const EvaluationFilters: React.FC<EvaluationFiltersProps> = ({
  filters,
  onChange,
  totalResults,
}) => {
  const [promptTitle, setPromptTitle] = useState(filters.prompt_title || '');
  const [showFilters, setShowFilters] = useState(false);

  // Debounced search for prompt title
  useEffect(() => {
    const timer = setTimeout(() => {
      if (promptTitle !== filters.prompt_title) {
        onChange({
          ...filters,
          prompt_title: promptTitle || undefined,
          offset: 0, // Reset to first page when filtering
        });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [promptTitle]);

  const handleVendorChange = (value: string) => {
    onChange({
      ...filters,
      vendor: value === 'all' ? undefined : value,
      offset: 0,
    });
  };

  const handleCategoryChange = (value: string) => {
    onChange({
      ...filters,
      category: value === 'all' ? undefined : value,
      offset: 0,
    });
  };

  const handleStatusChange = (value: string) => {
    onChange({
      ...filters,
      status_filter: value === 'all' ? undefined : (value as 'pass' | 'fail'),
      offset: 0,
    });
  };

  const handleClearFilters = () => {
    setPromptTitle('');
    onChange({
      sort_by: 'timestamp',
      sort_direction: 'desc',
      limit: filters.limit,
      offset: 0,
    });
  };

  const hasActiveFilters =
    !!filters.prompt_title ||
    !!filters.vendor ||
    !!filters.category ||
    !!filters.status_filter;

  return (
    <div className="bg-white border-b">
      {/* Filter Toggle Bar */}
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          {/* Prompt Title Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Search prompt titles..."
              value={promptTitle}
              onChange={(e) => setPromptTitle(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>

          {/* Filter Toggle Button */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
              showFilters || hasActiveFilters
                ? 'bg-primary text-white border-primary'
                : 'bg-white text-neutral-700 border-neutral-300 hover:bg-neutral-50'
            }`}
          >
            <Filter className="h-4 w-4" />
            Filters
            {hasActiveFilters && (
              <span className="ml-1 px-2 py-0.5 bg-white text-primary text-xs font-semibold rounded-full">
                {[
                  filters.prompt_title,
                  filters.vendor,
                  filters.category,
                  filters.status_filter,
                ].filter(Boolean).length}
              </span>
            )}
          </button>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="flex items-center gap-1 px-3 py-2 text-sm text-neutral-600 hover:text-neutral-900"
            >
              <X className="h-4 w-4" />
              Clear
            </button>
          )}
        </div>

        {/* Results Count */}
        <div className="text-sm text-neutral-600">
          {totalResults} {totalResults === 1 ? 'result' : 'results'}
        </div>
      </div>

      {/* Expanded Filters */}
      {showFilters && (
        <div className="px-6 pb-4 grid grid-cols-3 gap-4 border-t pt-4">
          {/* Vendor Filter */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Vendor
            </label>
            <select
              value={filters.vendor || 'all'}
              onChange={(e) => handleVendorChange(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All Vendors</option>
              <option value="Ragas">Ragas</option>
              <option value="DeepEval">DeepEval</option>
              <option value="MLflow">MLflow</option>
              <option value="Deepchecks">Deepchecks</option>
              <option value="Arize Phoenix">Arize Phoenix</option>
              <option value="PromptForge">PromptForge</option>
              <option value="Custom">Custom</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Category
            </label>
            <select
              value={filters.category || 'all'}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="quality">Quality</option>
              <option value="performance">Performance</option>
              <option value="security">Security</option>
              <option value="safety">Safety</option>
              <option value="bias">Bias</option>
              <option value="business_rules">Business Rules</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Status
            </label>
            <select
              value={filters.status_filter || 'all'}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="all">All</option>
              <option value="pass">✓ Passed</option>
              <option value="fail">✗ Failed</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};
