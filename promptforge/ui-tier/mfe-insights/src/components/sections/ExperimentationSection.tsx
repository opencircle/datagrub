import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Sparkles, Info } from 'lucide-react';
import type { InsightsFormState, AvailableModel } from '../../types/insights';

interface ExperimentationSectionProps {
  formState: InsightsFormState;
  setFormState: React.Dispatch<React.SetStateAction<InsightsFormState>>;
}

/**
 * Experimentation Section - System Prompts and Model Selection
 *
 * Allows users to:
 * - Customize system prompts for each DTA stage
 * - Select different models for each stage
 * - Experiment to find optimal cost/quality balance
 */

// API Base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Fetch function for available models
const fetchAvailableModels = async (): Promise<AvailableModel[]> => {
  const token = localStorage.getItem('promptforge_access_token');
  const response = await fetch(`${API_BASE_URL}/api/v1/models/available`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }

  return response.json();
};

// Default fallback models if API fails (2025 - Latest)
const DEFAULT_MODELS: AvailableModel[] = [
  // OpenAI Models (2025)
  {
    model_id: 'gpt-4.1',
    display_name: 'GPT-4.1',
    provider: 'OpenAI',
    description: 'Latest flagship with 1M context',
    input_cost: 0.01,
    output_cost: 0.03,
    context_window: 1000000,
  },
  {
    model_id: 'gpt-4.1-mini',
    display_name: 'GPT-4.1 Mini',
    provider: 'OpenAI',
    description: 'Fast and efficient',
    input_cost: 0.002,
    output_cost: 0.006,
    context_window: 1000000,
  },
  {
    model_id: 'gpt-4o',
    display_name: 'GPT-4o',
    provider: 'OpenAI',
    description: 'Multimodal flagship',
    input_cost: 0.005,
    output_cost: 0.015,
    context_window: 128000,
  },
  {
    model_id: 'gpt-4o-mini',
    display_name: 'GPT-4o Mini',
    provider: 'OpenAI',
    description: 'Cost-effective multimodal',
    input_cost: 0.00015,
    output_cost: 0.0006,
    context_window: 128000,
  },
  {
    model_id: 'gpt-4-turbo',
    display_name: 'GPT-4 Turbo',
    provider: 'OpenAI',
    description: 'Optimized GPT-4',
    input_cost: 0.01,
    output_cost: 0.03,
    context_window: 128000,
  },
  {
    model_id: 'gpt-4',
    display_name: 'GPT-4',
    provider: 'OpenAI',
    description: 'Legacy high-performance',
    input_cost: 0.03,
    output_cost: 0.06,
    context_window: 8192,
  },
  {
    model_id: 'gpt-3.5-turbo',
    display_name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    description: 'Fast and economical',
    input_cost: 0.0015,
    output_cost: 0.002,
    context_window: 16384,
  },

  // Anthropic Claude Models (2025)
  {
    model_id: 'claude-sonnet-4-5-20250929',
    display_name: 'Claude Sonnet 4.5',
    provider: 'Anthropic',
    description: 'Highest intelligence',
    input_cost: 0.003,
    output_cost: 0.015,
    context_window: 200000,
  },
  {
    model_id: 'claude-opus-4-1-20250805',
    display_name: 'Claude Opus 4.1',
    provider: 'Anthropic',
    description: 'Advanced reasoning',
    input_cost: 0.015,
    output_cost: 0.075,
    context_window: 200000,
  },
  {
    model_id: 'claude-3-5-sonnet-20241022',
    display_name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Balanced performance',
    input_cost: 0.003,
    output_cost: 0.015,
    context_window: 200000,
  },
  {
    model_id: 'claude-3-5-haiku-20241022',
    display_name: 'Claude 3.5 Haiku',
    provider: 'Anthropic',
    description: 'Fast and cost-effective',
    input_cost: 0.0008,
    output_cost: 0.004,
    context_window: 200000,
  },
];

export const ExperimentationSection: React.FC<ExperimentationSectionProps> = ({
  formState,
  setFormState,
}) => {
  // Fetch available models using React Query (prevents duplicate calls, provides caching)
  const {
    data: fetchedModels,
    isLoading: isLoadingModels,
  } = useQuery({
    queryKey: ['models', 'available'],
    queryFn: fetchAvailableModels,
    staleTime: 60000, // Cache for 1 minute
    retry: 2,
    // Use default models as fallback on error
    placeholderData: DEFAULT_MODELS,
  });

  // If API returns empty array (no providers configured), use DEFAULT_MODELS
  const fetchedOrDefaultModels = (fetchedModels && fetchedModels.length > 0) ? fetchedModels : DEFAULT_MODELS;

  // Sort models by cost (cheapest to most expensive)
  // Cost calculation: average of input and output cost per token
  const sortedModels = [...fetchedOrDefaultModels].sort((a, b) => {
    const costA = (a.input_cost + a.output_cost) / 2;
    const costB = (b.input_cost + b.output_cost) / 2;
    return costA - costB;
  });

  // Calculate cost multiplier relative to gpt-4o-mini (baseline)
  const baselineModel = sortedModels.find(m => m.model_id === 'gpt-4o-mini') || sortedModels[0];
  const baselineCost = (baselineModel.input_cost + baselineModel.output_cost) / 2;

  const availableModels = sortedModels.map(model => {
    const modelCost = (model.input_cost + model.output_cost) / 2;
    const costMultiplier = Math.round(modelCost / baselineCost);
    return {
      ...model,
      costMultiplier,
    };
  });

  const handleSystemPromptChange = (stage: 'stage1' | 'stage2' | 'stage3', value: string) => {
    setFormState(prev => ({
      ...prev,
      systemPrompts: {
        ...prev.systemPrompts,
        [stage]: value,
      },
    }));
  };

  const handleModelChange = (stage: 'stage1' | 'stage2' | 'stage3', value: string) => {
    setFormState(prev => ({
      ...prev,
      models: {
        ...prev.models,
        [stage]: value,
      },
    }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white rounded-2xl border border-neutral-200 p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-purple-100 rounded-xl">
            <Sparkles className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-neutral-700">Experimentation</h3>
            <p className="text-sm text-neutral-500 mt-0.5">
              Customize prompts and models to optimize cost and quality
            </p>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-purple-50 rounded-lg p-3 flex items-start gap-2">
        <Info className="h-4 w-4 text-purple-600 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-purple-700 leading-relaxed">
          Experiment with different models and system prompts for each stage. All experiments are saved in history for comparison.
        </p>
      </div>

      {/* Model Selection */}
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Model Selection</h4>
          <div className="grid grid-cols-3 gap-3">
            {/* Stage 1 Model */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 1: Fact Extraction
              </label>
              <select
                value={formState.models.stage1}
                onChange={(e) => handleModelChange('stage1', e.target.value)}
                disabled={isLoadingModels}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white disabled:bg-neutral-50 disabled:text-neutral-400"
              >
                {isLoadingModels ? (
                  <option>Loading...</option>
                ) : availableModels.length === 0 ? (
                  <option>No models available</option>
                ) : (
                  availableModels.map(model => (
                    <option key={model.model_id} value={model.model_id}>
                      {model.display_name} ({model.costMultiplier}x) - ${model.input_cost.toFixed(5)}/${model.output_cost.toFixed(5)}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Stage 2 Model */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 2: Reasoning
              </label>
              <select
                value={formState.models.stage2}
                onChange={(e) => handleModelChange('stage2', e.target.value)}
                disabled={isLoadingModels}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white disabled:bg-neutral-50 disabled:text-neutral-400"
              >
                {isLoadingModels ? (
                  <option>Loading...</option>
                ) : availableModels.length === 0 ? (
                  <option>No models available</option>
                ) : (
                  availableModels.map(model => (
                    <option key={model.model_id} value={model.model_id}>
                      {model.display_name} ({model.costMultiplier}x) - ${model.input_cost.toFixed(5)}/${model.output_cost.toFixed(5)}
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* Stage 3 Model */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 3: Summary
              </label>
              <select
                value={formState.models.stage3}
                onChange={(e) => handleModelChange('stage3', e.target.value)}
                disabled={isLoadingModels}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white disabled:bg-neutral-50 disabled:text-neutral-400"
              >
                {isLoadingModels ? (
                  <option>Loading...</option>
                ) : availableModels.length === 0 ? (
                  <option>No models available</option>
                ) : (
                  availableModels.map(model => (
                    <option key={model.model_id} value={model.model_id}>
                      {model.display_name} ({model.costMultiplier}x) - ${model.input_cost.toFixed(5)}/${model.output_cost.toFixed(5)}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* System Prompts */}
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-neutral-700 mb-3">Custom System Prompts</h4>
          <p className="text-xs text-neutral-500 mb-3">
            Leave empty to use default prompts. Custom prompts allow you to guide the model's behavior for each stage.
          </p>

          <div className="space-y-3">
            {/* Stage 1 Prompt */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 1: Fact Extraction System Prompt
              </label>
              <textarea
                value={formState.systemPrompts.stage1}
                onChange={(e) => handleSystemPromptChange('stage1', e.target.value)}
                placeholder="Default: You are an expert call analyst."
                rows={2}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>

            {/* Stage 2 Prompt */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 2: Reasoning & Insights System Prompt
              </label>
              <textarea
                value={formState.systemPrompts.stage2}
                onChange={(e) => handleSystemPromptChange('stage2', e.target.value)}
                placeholder="Default: You are an expert call analyst."
                rows={2}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>

            {/* Stage 3 Prompt */}
            <div>
              <label className="block text-xs font-medium text-neutral-600 mb-1.5">
                Stage 3: Summary Synthesis System Prompt
              </label>
              <textarea
                value={formState.systemPrompts.stage3}
                onChange={(e) => handleSystemPromptChange('stage3', e.target.value)}
                placeholder="Default: You are an expert call analyst."
                rows={2}
                className="w-full px-3 py-2 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ExperimentationSection;
