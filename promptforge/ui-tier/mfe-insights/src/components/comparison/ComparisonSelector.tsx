import React, { useState, useEffect } from 'react';
import { GitCompare, AlertCircle, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useAnalysisHistory } from '../../hooks/useInsights';
import { useCreateComparison } from '../../hooks/useComparisons';
import type { CallInsightsHistoryItem } from '../../types/insights';

// Model interface matching Playground format
interface AvailableModel {
  model_id: string;
  display_name: string;
  provider: string;
  description?: string;
  input_cost: number;
  output_cost: number;
  context_window?: number;
}

interface Props {
  onComparisonCreated?: (comparisonId: string) => void;
  preselectedAnalysisAId?: string;
  preselectedAnalysisBId?: string;
}

/**
 * Comparison Selector Component
 *
 * Allows users to:
 * 1. Select two Call Insights analyses to compare
 * 2. Choose a judge model (default: claude-sonnet-4.5)
 * 3. Select evaluation criteria
 * 4. Trigger blind comparison
 *
 * Validates that both analyses use the same transcript before comparison
 *
 * Enhanced with pre-selection support for seamless navigation from history
 */
export const ComparisonSelector: React.FC<Props> = ({
  onComparisonCreated,
  preselectedAnalysisAId,
  preselectedAnalysisBId,
}) => {
  const [selectedAnalysisA, setSelectedAnalysisA] = useState<string | null>(
    preselectedAnalysisAId || null
  );
  const [selectedAnalysisB, setSelectedAnalysisB] = useState<string | null>(
    preselectedAnalysisBId || null
  );
  const [judgeModel, setJudgeModel] = useState<string>(''); // Will be set from available models
  const [criteria, setCriteria] = useState<string[]>([
    'groundedness',
    'faithfulness',
    'completeness',
    'clarity',
    'accuracy',
  ]);
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [showProgressModal, setShowProgressModal] = useState(false);

  const { data: analysisHistory, isLoading: isLoadingHistory } = useAnalysisHistory({
    limit: 50,
  });

  const createComparison = useCreateComparison();

  // Fetch available models from same endpoint as Playground
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const { data: availableModels = [], isLoading: isLoadingModels } = useQuery<AvailableModel[]>({
    queryKey: ['models', 'available'],
    queryFn: async () => {
      const token = localStorage.getItem('promptforge_access_token');
      const response = await fetch(`${API_BASE_URL}/api/v1/models/available`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }
      return response.json();
    },
    staleTime: 60000, // Cache for 1 minute
    retry: 2,
  });

  // Set default judge model when models are loaded (prefer Claude Sonnet 4.5)
  useEffect(() => {
    if (availableModels.length > 0 && !judgeModel) {
      const defaultModel =
        availableModels.find((m) => m.model_id.includes('claude-sonnet-4')) ||
        availableModels.find((m) => m.model_id.includes('gpt-4o')) ||
        availableModels[0];
      if (defaultModel) {
        setJudgeModel(defaultModel.model_id);
      }
    }
  }, [availableModels, judgeModel]);

  // Progress simulation effect
  useEffect(() => {
    if (!createComparison.isPending) {
      setCurrentStage(0);
      setShowProgressModal(false);
      return;
    }

    setShowProgressModal(true);

    // Simulate progress through 4 stages over ~45 seconds
    const stageTimings = [0, 10000, 23000, 36000, 45000]; // Stage start times in ms
    const timers: NodeJS.Timeout[] = [];

    stageTimings.forEach((delay, index) => {
      const timer = setTimeout(() => {
        setCurrentStage(index);
      }, delay);
      timers.push(timer);
    });

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [createComparison.isPending]);

  const handleCriteriaToggle = (criterion: string) => {
    setCriteria((prev) =>
      prev.includes(criterion)
        ? prev.filter((c) => c !== criterion)
        : [...prev, criterion]
    );
  };

  const handleCreateComparison = async () => {
    if (!selectedAnalysisA || !selectedAnalysisB) {
      return;
    }

    try {
      const result = await createComparison.mutateAsync({
        analysis_a_id: selectedAnalysisA,
        analysis_b_id: selectedAnalysisB,
        judge_model: judgeModel,
        evaluation_criteria: criteria,
      });

      if (onComparisonCreated) {
        onComparisonCreated(result.id);
      }
    } catch (error) {
      console.error('Failed to create comparison:', error);
    }
  };

  const canCompare = selectedAnalysisA && selectedAnalysisB && criteria.length > 0;

  const availableCriteria = [
    { id: 'groundedness', label: 'Groundedness', description: 'Factual grounding in transcript' },
    { id: 'faithfulness', label: 'Faithfulness', description: 'Accurate representation of facts' },
    { id: 'completeness', label: 'Completeness', description: 'Coverage of key information' },
    { id: 'clarity', label: 'Clarity', description: 'Clarity and readability' },
    { id: 'accuracy', label: 'Accuracy', description: 'Correctness of insights' },
  ];

  // Sort models by cost (cheapest first) and mark recommended models
  const sortedJudgeModels = availableModels
    .map((model) => ({
      ...model,
      avg_cost: (model.input_cost + model.output_cost) / 2,
      is_recommended:
        model.model_id.includes('claude-sonnet-4') ||
        model.model_id.includes('gpt-4o-mini'),
    }))
    .sort((a, b) => a.avg_cost - b.avg_cost);

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-[#FF385C]" />
        <span className="ml-2 text-neutral-600">Loading analyses...</span>
      </div>
    );
  }

  if (!analysisHistory || analysisHistory.length < 2) {
    return (
      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900 mb-1">
              Not Enough Analyses
            </h3>
            <p className="text-sm text-yellow-800">
              You need at least 2 completed analyses to create a comparison. Run more analyses with
              different models or parameters to compare their outputs.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <GitCompare className="h-5 w-5 text-[#FF385C]" />
        <h2 className="text-xl font-semibold text-neutral-800">Compare Analyses</h2>
      </div>

      {/* Analysis Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Analysis A */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            Analysis A (Baseline)
          </label>
          <select
            value={selectedAnalysisA || ''}
            onChange={(e) => setSelectedAnalysisA(e.target.value || null)}
            className="w-full px-4 py-2.5 bg-white border-2 border-neutral-300 rounded-lg focus:outline-none focus:border-[#FF385C] transition-colors text-neutral-800"
          >
            <option value="">Select an analysis...</option>
            {analysisHistory.map((analysis) => (
              <option key={analysis.id} value={analysis.id}>
                {analysis.transcript_title || `Analysis ${analysis.id.slice(0, 8)}`} (
                {new Date(analysis.created_at).toLocaleDateString()})
              </option>
            ))}
          </select>
          {selectedAnalysisA && (
            <div className="mt-2 text-xs text-neutral-500">
              {analysisHistory.find((a) => a.id === selectedAnalysisA)?.transcript_preview.slice(0, 100)}...
            </div>
          )}
        </div>

        {/* Analysis B */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            Analysis B (Comparison)
          </label>
          <select
            value={selectedAnalysisB || ''}
            onChange={(e) => setSelectedAnalysisB(e.target.value || null)}
            className="w-full px-4 py-2.5 bg-white border-2 border-neutral-300 rounded-lg focus:outline-none focus:border-[#FF385C] transition-colors text-neutral-800"
            disabled={!selectedAnalysisA}
          >
            <option value="">Select an analysis...</option>
            {analysisHistory
              .filter((a) => a.id !== selectedAnalysisA)
              .map((analysis) => (
                <option key={analysis.id} value={analysis.id}>
                  {analysis.transcript_title || `Analysis ${analysis.id.slice(0, 8)}`} (
                  {new Date(analysis.created_at).toLocaleDateString()})
                </option>
              ))}
          </select>
          {selectedAnalysisB && (
            <div className="mt-2 text-xs text-neutral-500">
              {analysisHistory.find((a) => a.id === selectedAnalysisB)?.transcript_preview.slice(0, 100)}...
            </div>
          )}
        </div>
      </div>

      {/* Judge Model Selection */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-neutral-700 mb-2">
          Judge Model
        </label>
        {isLoadingModels ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-[#FF385C] mr-2" />
            <span className="text-sm text-neutral-600">Loading models...</span>
          </div>
        ) : sortedJudgeModels.length === 0 ? (
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="text-sm text-yellow-800">
                  No models configured. Please configure at least one AI provider in Settings.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {sortedJudgeModels.map((model) => (
              <button
                key={model.model_id}
                onClick={() => setJudgeModel(model.model_id)}
                className={`px-4 py-3 rounded-lg border-2 transition-all text-left ${
                  judgeModel === model.model_id
                    ? 'border-[#FF385C] bg-pink-50'
                    : 'border-neutral-300 bg-white hover:border-neutral-400'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {judgeModel === model.model_id && (
                    <Sparkles className="h-4 w-4 text-[#FF385C]" />
                  )}
                  <span className="font-semibold text-sm text-neutral-800">
                    {model.display_name}
                    {model.is_recommended && (
                      <span className="ml-1 text-xs text-[#FF385C]">(Recommended)</span>
                    )}
                  </span>
                </div>
                <div className="text-xs text-neutral-500">
                  ${model.input_cost.toFixed(5)} / ${model.output_cost.toFixed(5)} per 1K
                </div>
                <div className="text-xs text-neutral-400 mt-0.5">{model.provider}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Evaluation Criteria */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-neutral-700 mb-2">
          Evaluation Criteria
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {availableCriteria.map((criterion) => (
            <button
              key={criterion.id}
              onClick={() => handleCriteriaToggle(criterion.id)}
              className={`px-4 py-3 rounded-lg border-2 transition-all text-left ${
                criteria.includes(criterion.id)
                  ? 'border-[#FF385C] bg-pink-50'
                  : 'border-neutral-300 bg-white hover:border-neutral-400'
              }`}
            >
              <div className="font-semibold text-sm text-neutral-800 mb-0.5">
                {criterion.label}
              </div>
              <div className="text-xs text-neutral-500">{criterion.description}</div>
            </button>
          ))}
        </div>
        {criteria.length === 0 && (
          <div className="mt-2 text-sm text-red-600">
            Select at least one evaluation criterion
          </div>
        )}
      </div>

      {/* Create Comparison Button */}
      <div className="flex items-center justify-between pt-4 border-t-2 border-neutral-200">
        <div className="text-sm text-neutral-600">
          {canCompare
            ? 'Ready to compare analyses'
            : 'Select two analyses and at least one criterion'}
        </div>
        <button
          onClick={handleCreateComparison}
          disabled={!canCompare || createComparison.isPending}
          className="px-6 py-3 bg-[#FF385C] text-white font-semibold rounded-lg hover:bg-[#E31C5F] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {createComparison.isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Creating Comparison...
            </>
          ) : (
            <>
              <GitCompare className="h-4 w-4" />
              Create Comparison
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {createComparison.isError && (
        <div className="mt-4 bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-red-900 mb-1">Comparison Failed</h4>
              <p className="text-sm text-red-800">
                {createComparison.error instanceof Error
                  ? createComparison.error.message
                  : 'An unexpected error occurred. Please try again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Progress Modal */}
      {showProgressModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-[#FF385C]/10 rounded-full mb-4">
                <GitCompare className="h-8 w-8 text-[#FF385C] animate-pulse" />
              </div>
              <h3 className="text-2xl font-bold text-neutral-800 mb-2">
                Creating Comparison
              </h3>
              <p className="text-sm text-neutral-600">
                Judge model is evaluating both analyses...
              </p>
            </div>

            {/* Stage Progress */}
            <div className="space-y-3 mb-6">
              {[
                { id: 0, label: 'Stage 1: Fact Extraction', emoji: '📋' },
                { id: 1, label: 'Stage 2: Reasoning & Insights', emoji: '🧠' },
                { id: 2, label: 'Stage 3: Summary Synthesis', emoji: '📝' },
                { id: 3, label: 'Final Verdict & Analysis', emoji: '⚖️' },
              ].map((stage) => (
                <div
                  key={stage.id}
                  className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                    currentStage === stage.id
                      ? 'bg-[#FF385C]/10 border-2 border-[#FF385C]'
                      : currentStage > stage.id
                      ? 'bg-green-50 border-2 border-green-300'
                      : 'bg-neutral-50 border-2 border-neutral-200'
                  }`}
                >
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-white">
                    {currentStage > stage.id ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : currentStage === stage.id ? (
                      <Loader2 className="h-5 w-5 text-[#FF385C] animate-spin" />
                    ) : (
                      <span className="text-lg">{stage.emoji}</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <div
                      className={`text-sm font-semibold ${
                        currentStage === stage.id
                          ? 'text-[#FF385C]'
                          : currentStage > stage.id
                          ? 'text-green-700'
                          : 'text-neutral-600'
                      }`}
                    >
                      {stage.label}
                    </div>
                  </div>
                  {currentStage === stage.id && (
                    <div className="text-xs text-[#FF385C] font-semibold">
                      In Progress...
                    </div>
                  )}
                  {currentStage > stage.id && (
                    <div className="text-xs text-green-600 font-semibold">Complete</div>
                  )}
                </div>
              ))}
            </div>

            {/* Progress Bar */}
            <div className="relative h-2 bg-neutral-200 rounded-full overflow-hidden">
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-[#FF385C] to-pink-500 transition-all duration-1000 ease-linear"
                style={{ width: `${(currentStage / 3) * 100}%` }}
              />
            </div>

            <div className="mt-4 text-center text-xs text-neutral-500">
              This typically takes 30-60 seconds. Please wait...
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonSelector;
