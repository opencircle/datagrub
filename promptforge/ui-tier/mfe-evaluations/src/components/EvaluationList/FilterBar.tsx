import React, { useState, useEffect, useCallback } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '../../../../shared/components/forms/Input';
import { Select } from '../../../../shared/components/forms/Select';
import { Button } from '../../../../shared/components/core/Button';
import {
  EvaluationFilters,
  TYPE_FILTER_OPTIONS,
  MODEL_FILTER_OPTIONS,
  DATE_RANGE_OPTIONS,
} from '../../types/customEvaluation';

export interface FilterBarProps {
  filters: EvaluationFilters;
  onFilterChange: (filters: EvaluationFilters) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onFilterChange }) => {
  const [searchQuery, setSearchQuery] = useState(filters.search || '');
  const [typeFilter, setTypeFilter] = useState(filters.type || 'all');
  const [modelFilter, setModelFilter] = useState(filters.model || 'all');
  const [dateRange, setDateRange] = useState('all');

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onFilterChange({
        ...filters,
        search: searchQuery || undefined,
      });
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as EvaluationFilters['type'];
    setTypeFilter(value);
    onFilterChange({
      ...filters,
      type: value === 'all' ? undefined : value,
    });
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setModelFilter(value);
    onFilterChange({
      ...filters,
      model: value === 'all' ? undefined : value,
    });
  };

  const handleDateRangeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setDateRange(value);

    // Calculate date range based on selection
    let created_after: string | undefined;
    let created_before: string | undefined;

    const now = new Date();
    switch (value) {
      case 'today':
        created_after = new Date(now.setHours(0, 0, 0, 0)).toISOString();
        break;
      case 'last7days':
        created_after = new Date(now.setDate(now.getDate() - 7)).toISOString();
        break;
      case 'last30days':
        created_after = new Date(now.setDate(now.getDate() - 30)).toISOString();
        break;
      case 'all':
      default:
        created_after = undefined;
        created_before = undefined;
        break;
    }

    onFilterChange({
      ...filters,
      created_after,
      created_before,
    });
  };

  const clearFilters = () => {
    setSearchQuery('');
    setTypeFilter('all');
    setModelFilter('all');
    setDateRange('all');
    onFilterChange({});
  };

  const activeFilterCount = [
    searchQuery,
    typeFilter !== 'all' ? typeFilter : null,
    modelFilter !== 'all' ? modelFilter : null,
    dateRange !== 'all' ? dateRange : null,
  ].filter(Boolean).length;

  const hasActiveFilters = activeFilterCount > 0;

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-4 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center gap-3">
        {/* Search Input */}
        <div className="flex-1 md:max-w-md">
          <Input
            placeholder="Search by name or trace ID..."
            icon={<Search className="h-4 w-4" />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search evaluations by name or trace ID"
          />
        </div>

        {/* Type Filter */}
        <div className="w-full md:w-40">
          <Select
            value={typeFilter}
            onChange={handleTypeChange}
            options={TYPE_FILTER_OPTIONS}
            aria-label="Filter by evaluation type"
          />
        </div>

        {/* Model Filter */}
        <div className="w-full md:w-40">
          <Select
            value={modelFilter}
            onChange={handleModelChange}
            options={MODEL_FILTER_OPTIONS}
            aria-label="Filter by model"
          />
        </div>

        {/* Date Range */}
        <div className="w-full md:w-64">
          <Select
            value={dateRange}
            onChange={handleDateRangeChange}
            options={DATE_RANGE_OPTIONS}
            aria-label="Filter by date range"
          />
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="md"
            onClick={clearFilters}
            icon={<X className="h-4 w-4" />}
            className="transition-all duration-200"
          >
            Clear
            {activeFilterCount > 0 && (
              <span className="ml-1 px-2 py-0.5 bg-[#FF385C] text-white text-xs font-semibold rounded-full">
                {activeFilterCount}
              </span>
            )}
          </Button>
        )}
      </div>

      {/* Announce filter results to screen readers */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {hasActiveFilters && `${activeFilterCount} filter${activeFilterCount !== 1 ? 's' : ''} active`}
      </div>
    </div>
  );
};
