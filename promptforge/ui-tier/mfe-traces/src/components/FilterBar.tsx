import React from 'react';
import { Search } from 'lucide-react';

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  modelFilter: string;
  onModelFilterChange: (model: string) => void;
  sourceFilter: string;
  onSourceFilterChange: (source: string) => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  searchQuery,
  onSearchChange,
  modelFilter,
  onModelFilterChange,
  sourceFilter,
  onSourceFilterChange,
}) => {
  return (
    <div className="flex items-center justify-between gap-4">
      {/* Search Input - Design System: Updated styling */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
        <input
          type="text"
          placeholder="Search by trace ID, project, or user..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white
                     focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
                     transition-all duration-200 placeholder:text-neutral-400"
          aria-label="Search traces by ID, project, or user"
        />
      </div>

      {/* Source Filter - Design System: Updated styling */}
      <select
        value={sourceFilter}
        onChange={(e) => onSourceFilterChange(e.target.value)}
        className="h-12 px-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white
                   focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
                   transition-all duration-200"
        aria-label="Filter traces by source"
      >
        <option value="">All Sources</option>
        <option value="Call Insights">Call Insights</option>
        <option value="Playground">Playground</option>
        <option value="Other">Other</option>
      </select>

      {/* Model Filter - Design System: Updated styling */}
      <select
        value={modelFilter}
        onChange={(e) => onModelFilterChange(e.target.value)}
        className="h-12 px-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white
                   focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
                   transition-all duration-200"
        aria-label="Filter traces by model"
      >
        <option value="">All Models</option>
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        <option value="claude-3-opus">Claude 3 Opus</option>
        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
        <option value="gemini-pro">Gemini Pro</option>
      </select>
    </div>
  );
};

export default FilterBar;
