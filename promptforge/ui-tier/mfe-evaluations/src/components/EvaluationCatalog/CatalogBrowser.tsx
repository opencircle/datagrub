import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, X } from 'lucide-react';
import {
  evaluationCatalogService,
  EvaluationMetadata,
  EvaluationSource,
} from '../../../../shared/services/evaluationCatalogService';
import { EvaluationCard } from './EvaluationCard';
import { Button } from '../../../../shared/components/core/Button';
import { Badge } from '../../../../shared/components/core/Badge';

interface CatalogBrowserProps {
  selectedEvaluations: string[];
  onSelectionChange: (ids: string[]) => void;
  onContinue?: () => void;
}

const SOURCE_FILTERS: { value: EvaluationSource | 'all'; label: string }[] = [
  { value: 'all', label: 'All Sources' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'custom', label: 'Custom' },
  { value: 'promptforge', label: 'PromptForge' },
  { value: 'llm_judge', label: 'LLM Judge' },
];

export const CatalogBrowser: React.FC<CatalogBrowserProps> = ({
  selectedEvaluations,
  onSelectionChange,
  onContinue,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState<EvaluationSource | 'all'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string | 'all'>('all');

  // Fetch catalog
  const { data: evaluations = [], isLoading, error } = useQuery({
    queryKey: ['evaluation-catalog', sourceFilter],
    queryFn: () =>
      evaluationCatalogService.getCatalog({
        source: sourceFilter !== 'all' ? sourceFilter : undefined,
      }),
  });

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['evaluation-categories'],
    queryFn: () => evaluationCatalogService.getCategories(),
  });

  const handleToggleEvaluation = (id: string) => {
    if (selectedEvaluations.includes(id)) {
      onSelectionChange(selectedEvaluations.filter((evalId) => evalId !== id));
    } else {
      onSelectionChange([...selectedEvaluations, id]);
    }
  };

  const handleSelectAll = () => {
    const allIds = filteredEvaluations.map((e) => e.id);
    onSelectionChange(allIds);
  };

  const handleDeselectAll = () => {
    onSelectionChange([]);
  };

  // Filter evaluations
  const filteredEvaluations = evaluations.filter((evaluation) => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch =
        evaluation.name.toLowerCase().includes(query) ||
        evaluation.description.toLowerCase().includes(query) ||
        evaluation.category.toLowerCase().includes(query) ||
        evaluation.tags?.some((tag) => tag.toLowerCase().includes(query));

      if (!matchesSearch) return false;
    }

    // Category filter
    if (categoryFilter !== 'all' && evaluation.category !== categoryFilter) {
      return false;
    }

    return true;
  });

  // Group by category
  const evaluationsByCategory = filteredEvaluations.reduce((acc, evaluation) => {
    const category = evaluation.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(evaluation);
    return acc;
  }, {} as Record<string, EvaluationMetadata[]>);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading evaluation catalog...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">Error loading catalog: {(error as Error).message}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Header - Design System: Increased spacing, clearer hierarchy */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold text-neutral-800">Evaluation Catalog</h2>
            <p className="text-neutral-500 mt-2 text-base">
              Browse and select evaluations to run on your prompts
            </p>
          </div>
          {selectedEvaluations.length > 0 && onContinue && (
            <Button variant="primary" onClick={onContinue}>
              Continue with {selectedEvaluations.length} evaluation
              {selectedEvaluations.length !== 1 ? 's' : ''}
            </Button>
          )}
        </div>

        {/* Selection Summary - Design System: Softer colors */}
        {selectedEvaluations.length > 0 && (
          <div className="bg-[#FF385C]/5 border border-[#FF385C]/20 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="blue">
                {selectedEvaluations.length} selected
              </Badge>
              <span className="text-sm text-neutral-600">
                {selectedEvaluations.length === filteredEvaluations.length
                  ? 'All evaluations selected'
                  : `${filteredEvaluations.length - selectedEvaluations.length} remaining`}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleDeselectAll}>
              <X className="h-4 w-4 mr-1" />
              Clear Selection
            </Button>
          </div>
        )}
      </div>

      {/* Filters - Design System: Softer, more spacious */}
      <div className="space-y-5">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search evaluations by name, description, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 placeholder:text-neutral-400"
          />
        </div>

        {/* Filter Chips */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-neutral-500" />
            <span className="text-sm font-medium text-neutral-600">Source:</span>
          </div>
          {SOURCE_FILTERS.map((filter) => (
            <button
              key={filter.value}
              onClick={() => setSourceFilter(filter.value)}
              className={`
                px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${
                  sourceFilter === filter.value
                    ? 'bg-[#FF385C] text-white shadow-sm'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300'
                }
              `}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {categories.length > 0 && (
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm font-medium text-neutral-600">Category:</span>
            <button
              onClick={() => setCategoryFilter('all')}
              className={`
                px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${
                  categoryFilter === 'all'
                    ? 'bg-[#FF385C] text-white shadow-sm'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300'
                }
              `}
            >
              All
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setCategoryFilter(category)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${
                    categoryFilter === category
                      ? 'bg-[#FF385C] text-white shadow-sm'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300'
                  }
                `}
              >
                {category}
              </button>
            ))}
          </div>
        )}

        {/* Bulk Actions */}
        {filteredEvaluations.length > 0 && (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleSelectAll}>
              Select All ({filteredEvaluations.length})
            </Button>
            {selectedEvaluations.length > 0 && (
              <Button variant="ghost" size="sm" onClick={handleDeselectAll}>
                Deselect All
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Results - Design System: Better spacing and hierarchy */}
      <div>
        <div className="mb-4 text-sm text-neutral-500">
          {filteredEvaluations.length} evaluation{filteredEvaluations.length !== 1 ? 's' : ''} found
        </div>

        {filteredEvaluations.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-neutral-100">
            <p className="text-neutral-500">No evaluations found matching your filters</p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(evaluationsByCategory).map(([category, categoryEvaluations]) => (
              <div key={category}>
                <h3 className="text-lg font-semibold text-neutral-800 mb-4 flex items-center gap-2">
                  {category}
                  <Badge variant="gray">{categoryEvaluations.length}</Badge>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {categoryEvaluations.map((evaluation) => (
                    <EvaluationCard
                      key={evaluation.id}
                      evaluation={evaluation}
                      isSelected={selectedEvaluations.includes(evaluation.id)}
                      onToggle={handleToggleEvaluation}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
