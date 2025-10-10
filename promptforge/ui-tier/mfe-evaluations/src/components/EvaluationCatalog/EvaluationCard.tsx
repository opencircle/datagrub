import React from 'react';
import { Check, Info, Sparkles, Code, Shield, BarChart } from 'lucide-react';
import { EvaluationMetadata } from '../../../../shared/services/evaluationCatalogService';
import { Badge } from '../../../../shared/components/core/Badge';

interface EvaluationCardProps {
  evaluation: EvaluationMetadata;
  isSelected: boolean;
  onToggle: (id: string) => void;
  onViewDetails?: (evaluation: EvaluationMetadata) => void;
}

const sourceIcons = {
  vendor: <Sparkles className="h-4 w-4" />,
  custom: <Code className="h-4 w-4" />,
  promptforge: <Shield className="h-4 w-4" />,
  llm_judge: <BarChart className="h-4 w-4" />,
};

const sourceColors = {
  vendor: 'blue',
  custom: 'purple',
  promptforge: 'green',
  llm_judge: 'orange',
} as const;

const sourceLabels = {
  vendor: 'Vendor',
  custom: 'Custom',
  promptforge: 'PromptForge',
  llm_judge: 'LLM Judge',
};

export const EvaluationCard: React.FC<EvaluationCardProps> = ({
  evaluation,
  isSelected,
  onToggle,
  onViewDetails,
}) => {
  return (
    <div
      className={`
        bg-white border rounded-2xl p-6 transition-all cursor-pointer
        ${isSelected ? 'border-[#FF385C] ring-4 ring-[#FF385C]/10 shadow-sm' : 'border-neutral-100 hover:border-neutral-200 hover:shadow-md'}
      `}
      onClick={() => onToggle(evaluation.id)}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox - Design System: Updated colors */}
        <div className="flex-shrink-0 mt-1">
          <div
            className={`
              w-5 h-5 rounded border-2 flex items-center justify-center transition-all
              ${isSelected ? 'bg-[#FF385C] border-[#FF385C]' : 'border-neutral-300 hover:border-neutral-400'}
            `}
          >
            {isSelected && <Check className="h-3 w-3 text-white" />}
          </div>
        </div>

        {/* Content - Design System: Better spacing */}
        <div className="flex-1 min-w-0 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-lg text-neutral-800 leading-snug mb-2">{evaluation.name}</h3>
              {evaluation.library && (
                <p className="text-xs text-neutral-400">{evaluation.library}</p>
              )}
            </div>
            <Badge variant={sourceColors[evaluation.source]}>
              <span className="inline-flex items-center gap-1.5">
                {sourceIcons[evaluation.source]}
                {sourceLabels[evaluation.source]}
              </span>
            </Badge>
          </div>

          <p className="text-sm text-neutral-500 line-clamp-2 leading-relaxed">
            {evaluation.description}
          </p>

          {/* Requirements - Design System: Better spacing */}
          <div className="flex flex-wrap gap-2">
            <Badge variant="gray" size="sm">{evaluation.category}</Badge>
            {evaluation.requires_context && (
              <Badge variant="gray" size="sm">Needs Context</Badge>
            )}
            {evaluation.requires_ground_truth && (
              <Badge variant="gray" size="sm">Needs Ground Truth</Badge>
            )}
            {evaluation.requires_llm && (
              <Badge variant="orange" size="sm">Uses LLM</Badge>
            )}
          </div>

          {/* Tags - Design System: Softer colors */}
          {evaluation.tags && evaluation.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {evaluation.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-1 bg-neutral-50 text-neutral-600 rounded-md"
                >
                  {tag}
                </span>
              ))}
              {evaluation.tags.length > 3 && (
                <span className="text-xs text-neutral-400">
                  +{evaluation.tags.length - 3} more
                </span>
              )}
            </div>
          )}

          {/* View Details - Design System: Updated color */}
          {onViewDetails && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onViewDetails(evaluation);
              }}
              className="text-sm text-[#FF385C] hover:text-[#E31C5F] flex items-center gap-1.5 font-medium transition-colors"
            >
              <Info className="h-4 w-4" />
              View Details
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
