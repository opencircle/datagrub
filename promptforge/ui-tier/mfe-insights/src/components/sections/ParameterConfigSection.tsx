import React from 'react';
import { Settings, ChevronDown, ChevronUp, Thermometer, Sliders, Hash } from 'lucide-react';
import type { InsightsFormState, StageParameters } from '../../types/insights';
import { EvaluationSelector } from '../../../../shared/components/forms/EvaluationSelector';

interface Props {
  formState: InsightsFormState;
  setFormState: React.Dispatch<React.SetStateAction<InsightsFormState>>;
}

/**
 * Parameter Configuration Section
 *
 * Features:
 * - Collapsible advanced parameters for each stage
 * - Temperature, Top-P, Max Tokens sliders
 * - Evaluation selection checkboxes
 * - Stage-specific configuration (fact extraction, reasoning, summary)
 */
export const ParameterConfigSection: React.FC<Props> = ({
  formState,
  setFormState,
}) => {
  const toggleAdvancedParams = () => {
    setFormState(prev => ({ ...prev, showAdvancedParams: !prev.showAdvancedParams }));
  };

  const updateStageParam = (
    stage: 'factExtraction' | 'reasoning' | 'summary',
    param: keyof StageParameters,
    value: number
  ) => {
    setFormState(prev => ({
      ...prev,
      stageParams: {
        ...prev.stageParams,
        [stage]: {
          ...prev.stageParams[stage],
          [param]: value,
        },
      },
    }));
  };

  const handleEvaluationChange = (ids: string[]) => {
    setFormState(prev => ({
      ...prev,
      selectedEvaluations: ids,
    }));
  };

  const renderStageConfig = (
    stage: 'factExtraction' | 'reasoning' | 'summary',
    label: string,
    description: string
  ) => {
    const params = formState.stageParams[stage];

    return (
      <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-4">
        <div className="mb-4">
          <div className="font-semibold text-neutral-700 mb-1">{label}</div>
          <div className="text-xs text-neutral-500">{description}</div>
        </div>

        <div className="space-y-4">
          {/* Temperature */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-neutral-700 flex items-center gap-1">
                <Thermometer className="h-3 w-3" />
                Temperature
              </label>
              <span className="text-xs font-mono text-[#FF385C] bg-white px-2 py-0.5 rounded border border-[#FF385C]/20">
                {params.temperature?.toFixed(2) ?? '0.00'}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={params.temperature ?? 0}
              onChange={(e) => updateStageParam(stage, 'temperature', parseFloat(e.target.value))}
              className="w-full accent-[#FF385C]"
            />
          </div>

          {/* Top P */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-neutral-700 flex items-center gap-1">
                <Sliders className="h-3 w-3" />
                Top P
              </label>
              <span className="text-xs font-mono text-[#FF385C] bg-white px-2 py-0.5 rounded border border-[#FF385C]/20">
                {params.top_p?.toFixed(2) ?? '0.00'}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={params.top_p ?? 0}
              onChange={(e) => updateStageParam(stage, 'top_p', parseFloat(e.target.value))}
              className="w-full accent-[#FF385C]"
            />
          </div>

          {/* Max Tokens */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-neutral-700 flex items-center gap-1">
                <Hash className="h-3 w-3" />
                Max Tokens
              </label>
              <span className="text-xs font-mono text-[#FF385C] bg-white px-2 py-0.5 rounded border border-[#FF385C]/20">
                {params.max_tokens ?? 0}
              </span>
            </div>
            <input
              type="range"
              min="100"
              max="4000"
              step="100"
              value={params.max_tokens ?? 100}
              onChange={(e) => updateStageParam(stage, 'max_tokens', parseInt(e.target.value))}
              className="w-full accent-[#FF385C]"
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-5">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="h-5 w-5 text-[#FF385C]" />
          <h3 className="font-semibold text-neutral-700">Configuration</h3>
        </div>

        <button
          onClick={toggleAdvancedParams}
          className="flex items-center gap-2 text-sm text-[#FF385C] hover:text-[#E31C5F] font-semibold transition-colors"
        >
          {formState.showAdvancedParams ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Hide Advanced
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              Show Advanced
            </>
          )}
        </button>
      </div>

      {/* Evaluation Selection */}
      <EvaluationSelector
        selectedEvaluationIds={formState.selectedEvaluations}
        onSelectionChange={handleEvaluationChange}
      />

      {/* Advanced Parameters - Collapsible */}
      {formState.showAdvancedParams && (
        <div className="space-y-4 pt-4 border-t border-neutral-200">
          <div className="text-sm text-neutral-600 mb-4">
            Customize model parameters for each stage of the DTA pipeline. Defaults are optimized
            for typical call analysis use cases.
          </div>

          <div className="space-y-4">
            {renderStageConfig(
              'factExtraction',
              'Stage 1: Fact Extraction',
              'Low temperature for precise fact extraction'
            )}

            {renderStageConfig(
              'reasoning',
              'Stage 2: Reasoning & Insights',
              'Moderate temperature for balanced creativity'
            )}

            {renderStageConfig(
              'summary',
              'Stage 3: Summary Synthesis',
              'Controlled temperature for coherent summaries'
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ParameterConfigSection;
