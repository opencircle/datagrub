import React, { useState, useEffect } from 'react';
import {
  Play,
  Zap,
  Clock,
  DollarSign,
  Hash,
  Settings,
  History,
  FileText,
  Sparkles,
  Thermometer,
  Sliders,
  Target,
  AlertCircle,
  Loader2,
  ArrowLeft,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from '@tanstack/react-query';
import { mockSessions } from './mockData';
import { PlaygroundSession, Model } from './types/playground';
import { executePrompt, PlaygroundExecutionRequest, PlaygroundExecutionResponse } from './services/playgroundService';
import { EvaluationSelector } from '../../shared/components/forms/EvaluationSelector';
import { HistoryCard } from './components/HistoryCard';
import { useSessionNavigation } from './hooks/useSessionNavigation';

// Prompt interface (simplified from shared)
interface Prompt {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  current_version?: {
    template: string;
    system_message: string | null;
    model_config?: {
      tone?: string;
    };
  };
}

// API client for fetching data
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

async function fetchPrompts(): Promise<Prompt[]> {
  const token = localStorage.getItem('promptforge_access_token');
  const response = await fetch(`${API_BASE_URL}/api/v1/prompts`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch prompts');
  }
  return response.json();
}

async function fetchAvailableModels(): Promise<Model[]> {
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
  const data = await response.json();

  // Sort models by cost (cheapest to most expensive)
  const sortedData = [...data].sort((a: any, b: any) => {
    const costA = (a.input_cost + a.output_cost) / 2;
    const costB = (b.input_cost + b.output_cost) / 2;
    return costA - costB;
  });

  // Calculate cost multiplier relative to gpt-4o-mini (baseline)
  const baselineModel = sortedData.find((m: any) => m.model_id === 'gpt-4o-mini') || sortedData[0];
  const baselineCost = baselineModel ? (baselineModel.input_cost + baselineModel.output_cost) / 2 : 1;

  // Transform API response to Model interface with cost multiplier
  return sortedData.map((m: any) => {
    const modelCost = (m.input_cost + m.output_cost) / 2;
    const costMultiplier = Math.round(modelCost / baselineCost);
    return {
      id: m.model_id,
      name: m.display_name,
      provider: m.provider,
      input_cost: m.input_cost,
      output_cost: m.output_cost,
      costMultiplier,
    };
  });
}

export const PlaygroundEnhanced: React.FC = () => {
  // Deep linking hook
  const { sessionId, navigateToSession, navigateToHome, isViewingSession } = useSessionNavigation();

  // UI State
  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(500);
  const [topP, setTopP] = useState(0.9);
  const [topK, setTopK] = useState(40);
  const [sessions, setSessions] = useState<PlaygroundSession[]>(mockSessions);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null);
  const [intent, setIntent] = useState('');
  const [tone, setTone] = useState('professional');
  const [selectedEvaluationIds, setSelectedEvaluationIds] = useState<string[]>([]);
  const [executionMetrics, setExecutionMetrics] = useState<{
    latency_ms: number;
    tokens_used: number;
    cost: number;
    trace_id: string;
  } | null>(null);

  // Server State - fetch prompts and models using React Query
  const { data: existingPrompts = [] } = useQuery({
    queryKey: ['prompts'],
    queryFn: fetchPrompts,
    staleTime: 30000,
    retry: 1,
  });

  const { data: availableModels = [], isLoading: isLoadingModels } = useQuery({
    queryKey: ['models', 'available'],
    queryFn: fetchAvailableModels,
    staleTime: 60000, // Cache for 1 minute
    retry: 2,
  });

  // Set initial model when models are loaded (prefer gpt-4o-mini)
  React.useEffect(() => {
    if (availableModels.length > 0 && !selectedModel) {
      const defaultModel = availableModels.find(m => m.id === 'gpt-4o-mini') || availableModels[0];
      setSelectedModel(defaultModel);
    }
  }, [availableModels, selectedModel]);

  // Live API execution mutation
  const executeMutation = useMutation({
    mutationFn: (request: PlaygroundExecutionRequest) => executePrompt(request),
    onSuccess: (data: PlaygroundExecutionResponse) => {
      setResponse(data.response);
      setExecutionMetrics({
        latency_ms: data.metrics.latency_ms,
        tokens_used: data.metrics.tokens_used,
        cost: data.metrics.cost,
        trace_id: data.trace_id,
      });

      // Add to sessions history - capture ALL form fields
      const newSession: PlaygroundSession = {
        id: data.trace_id,
        timestamp: data.timestamp,
        title: title.trim(),
        prompt,
        systemPrompt: systemPrompt.trim() || undefined,  // NEW: Capture system prompt
        response: data.response,
        model: selectedModel,
        parameters: {
          temperature,
          maxTokens,
          topP,
          topK,  // NEW: Capture topK parameter
        },
        metadata: {
          intent: intent.trim() || undefined,  // NEW: Capture intent
          tone: tone,  // NEW: Capture tone
          promptId: selectedPromptId || undefined,  // NEW: Capture loaded prompt ID
        },
        evaluationIds: selectedEvaluationIds.length > 0 ? selectedEvaluationIds : undefined,  // NEW: Capture evaluation IDs
        metrics: {
          latency: data.metrics.latency_ms / 1000,
          tokens: data.metrics.tokens_used,
          cost: data.metrics.cost,
        },
      };
      setSessions([newSession, ...sessions]);
    },
    onError: (error: Error) => {
      setResponse(`Error: ${error.message}`);
      setExecutionMetrics(null);
    },
  });

  const handleLoadPrompt = (promptObj: Prompt) => {
    setSelectedPromptId(promptObj.id);
    if (promptObj.current_version) {
      setPrompt(promptObj.current_version.template || '');
      setSystemPrompt(promptObj.current_version.system_message || '');
      setIntent(promptObj.category || '');
      setTone(promptObj.current_version.model_config?.tone || 'professional');
    }
  };

  const handleNewPrompt = () => {
    setSelectedPromptId(null);
    setTitle('');
    setPrompt('');
    setSystemPrompt('');
    setIntent('');
    setTone('professional');
    setResponse('');
    setExecutionMetrics(null);
  };

  // Handle "Load into Editor" - Restores ALL form fields from a session
  const handleLoadSession = (session: PlaygroundSession) => {
    // Restore all form fields
    setTitle(session.title || '');
    setPrompt(session.prompt);
    setSystemPrompt(session.systemPrompt || '');
    setResponse(session.response);
    setSelectedModel(session.model);
    setTemperature(session.parameters.temperature);
    setMaxTokens(session.parameters.maxTokens);
    setTopP(session.parameters.topP);
    setTopK(session.parameters.topK || 40);
    setIntent(session.metadata?.intent || '');
    setTone(session.metadata?.tone || 'professional');
    setSelectedEvaluationIds(session.evaluationIds || []);

    // Update metrics if available
    if (session.metrics) {
      setExecutionMetrics({
        latency_ms: session.metrics.latency * 1000,
        tokens_used: session.metrics.tokens,
        cost: session.metrics.cost,
        trace_id: session.id,
      });
    }

    // Update URL to reflect loaded session
    navigateToSession(session.id);

    // Scroll to top to show loaded session
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Collapse history section
    setShowHistory(false);
  };

  // Load session from URL parameter on mount/change
  useEffect(() => {
    if (sessionId) {
      const session = sessions.find((s) => s.id === sessionId);
      if (session) {
        // Load session data into form fields
        setTitle(session.title || '');
        setPrompt(session.prompt);
        setSystemPrompt(session.systemPrompt || '');
        setResponse(session.response);
        setSelectedModel(session.model);
        setTemperature(session.parameters.temperature);
        setMaxTokens(session.parameters.maxTokens);
        setTopP(session.parameters.topP);
        setTopK(session.parameters.topK || 40);
        setIntent(session.metadata?.intent || '');
        setTone(session.metadata?.tone || 'professional');
        setSelectedEvaluationIds(session.evaluationIds || []);

        // Update metrics if available
        if (session.metrics) {
          setExecutionMetrics({
            latency_ms: session.metrics.latency * 1000,
            tokens_used: session.metrics.tokens,
            cost: session.metrics.cost,
            trace_id: session.id,
          });
        }

        // Show history view to display the session details
        setShowHistory(true);

        // Scroll to top to show loaded session
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        console.warn(`Session ${sessionId} not found in history`);
        // Optionally navigate home if session not found
        // navigateToHome();
      }
    } else {
      // No sessionId - hide history view
      setShowHistory(false);
    }
  }, [sessionId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSubmit = () => {
    // Input validation
    const errors: string[] = [];

    if (!title.trim()) {
      errors.push('Title is required');
    }

    if (title.trim().length > 200) {
      errors.push('Title is too long (max 200 characters)');
    }

    if (!prompt.trim()) {
      errors.push('User prompt is required');
    }

    if (prompt.trim().length > 10000) {
      errors.push('Prompt is too long (max 10,000 characters)');
    }

    if (systemPrompt.trim().length > 5000) {
      errors.push('System prompt is too long (max 5,000 characters)');
    }

    if (!selectedModel) {
      errors.push('Please select a model');
    }

    if (temperature < 0 || temperature > 2) {
      errors.push('Temperature must be between 0 and 2');
    }

    if (maxTokens < 1 || maxTokens > 4000) {
      errors.push('Max tokens must be between 1 and 4000');
    }

    if (topP < 0 || topP > 1) {
      errors.push('Top P must be between 0 and 1');
    }

    if (topK && (topK < 1 || topK > 100)) {
      errors.push('Top K must be between 1 and 100');
    }

    // Show validation errors
    if (errors.length > 0) {
      setResponse(`Validation Error:\n${errors.join('\n')}`);
      setExecutionMetrics(null);
      return;
    }

    setResponse('');
    setExecutionMetrics(null);

    const request: PlaygroundExecutionRequest = {
      title: title.trim(),
      prompt: prompt.trim(),
      system_prompt: systemPrompt.trim() || undefined,
      model: selectedModel.id,
      parameters: {
        temperature,
        max_tokens: maxTokens,
        top_p: topP,
        top_k: topK,
      },
      metadata: {
        intent: intent || undefined,
        tone: tone,
        prompt_id: selectedPromptId || undefined,
      },
      evaluation_ids: selectedEvaluationIds.length > 0 ? selectedEvaluationIds : undefined,
    };

    executeMutation.mutate(request);
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Header - Design System: Increased spacing, clearer hierarchy */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isViewingSession && (
            <button
              onClick={navigateToHome}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors border border-neutral-200 focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
              title="Back to Playground"
              aria-label="Back to Playground home"
            >
              <ArrowLeft className="h-5 w-5 text-neutral-600" />
            </button>
          )}
          <div>
            <h1 className="text-3xl font-bold text-neutral-800">
              {isViewingSession ? 'Session Details' : 'Playground'}
            </h1>
            <p className="text-neutral-500 mt-2 text-base">
              {isViewingSession
                ? `Viewing session ${sessionId?.slice(0, 8)}...`
                : 'Test prompts and experiment with AI models'}
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center gap-2 bg-neutral-100 text-neutral-700 h-10 px-4 rounded-xl hover:bg-neutral-200 transition-all duration-200 font-semibold focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
        >
          <History className="h-4 w-4" />
          {showHistory ? 'Hide' : 'Show'} History
        </button>
      </div>

      {/* Existing Prompts Selection - Design System */}
      {existingPrompts.length > 0 && (
        <div className="bg-white border border-neutral-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-[#FF385C]" />
              <h3 className="font-semibold text-neutral-700">Load Existing Prompt</h3>
            </div>
            <button
              onClick={handleNewPrompt}
              className="flex items-center gap-2 text-sm text-[#FF385C] hover:text-[#E31C5F] font-semibold transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              New Prompt
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {existingPrompts.slice(0, 6).map((p) => (
              <button
                key={p.id}
                onClick={() => handleLoadPrompt(p)}
                className={`text-left p-3 rounded-lg border-2 transition-all duration-200 ${
                  selectedPromptId === p.id
                    ? 'border-[#FF385C] bg-[#FF385C]/5'
                    : 'border-neutral-200 hover:border-[#FF385C]/50 hover:bg-neutral-50'
                }`}
              >
                <div className="font-semibold text-sm text-neutral-700 mb-1">{p.name}</div>
                <div className="text-xs text-neutral-500 line-clamp-2">
                  {p.description || 'No description'}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {/* Middle Column - Prompt Configuration (2/3 width) */}
        <div className="col-span-2 space-y-4">
          <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-5">
            {/* Title - Required identifier for traces and evaluations */}
            <div>
              <label className="block text-sm font-semibold text-neutral-700 mb-2">
                Title <span className="text-[#FF385C]">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Customer support response test"
                className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
              />
              <p className="mt-1 text-xs text-neutral-500">
                Give this execution a memorable name to identify it in traces, history, and evaluations.
              </p>
            </div>

            {/* Intent & Tone - Design System */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-neutral-700 mb-2">
                  <Target className="h-4 w-4 inline mr-1" />
                  Intent
                </label>
                <input
                  type="text"
                  value={intent}
                  onChange={(e) => setIntent(e.target.value)}
                  placeholder="e.g., Answer questions, Generate code"
                  className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 placeholder:text-neutral-400"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-neutral-700 mb-2">
                  <Sparkles className="h-4 w-4 inline mr-1" />
                  Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="friendly">Friendly</option>
                  <option value="formal">Formal</option>
                  <option value="technical">Technical</option>
                  <option value="empathetic">Empathetic</option>
                </select>
              </div>
            </div>

            {/* System Prompt - Design System */}
            <div>
              <label className="block text-sm font-semibold text-neutral-700 mb-2">
                System Prompt
              </label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Define the model's role, behavior, and constraints..."
                rows={3}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 text-neutral-700 text-base focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 resize-none placeholder:text-neutral-400 font-mono"
              />
            </div>

            {/* User Prompt - Design System */}
            <div>
              <label className="block text-sm font-semibold text-neutral-700 mb-2">
                User Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your prompt here..."
                rows={6}
                className="w-full px-4 py-3 rounded-xl border border-neutral-200 text-neutral-700 text-base focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 resize-none placeholder:text-neutral-400 font-mono"
              />
            </div>

            {/* Evaluation Selector */}
            <EvaluationSelector
              selectedEvaluationIds={selectedEvaluationIds}
              onSelectionChange={setSelectedEvaluationIds}
            />

            {/* Run Button - Design System */}
            <button
              onClick={handleSubmit}
              disabled={executeMutation.isPending || !title.trim() || !prompt.trim()}
              className="flex items-center justify-center gap-2 w-full h-12 bg-[#FF385C] text-white rounded-xl hover:bg-[#E31C5F] transition-all duration-200 disabled:bg-neutral-300 disabled:text-neutral-500 disabled:cursor-not-allowed font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
            >
              {executeMutation.isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  Run Prompt
                </>
              )}
            </button>

            {/* Response Section - Below Prompt */}
            <AnimatePresence>
              {(response || executeMutation.isPending) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-3"
                >
                  <label className="block text-sm font-semibold text-neutral-700">
                    Response
                  </label>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 min-h-[150px]">
                    {executeMutation.isPending ? (
                      <div className="flex items-center gap-2 text-neutral-600">
                        <Zap className="h-4 w-4 animate-pulse text-[#FF385C]" />
                        Generating response...
                      </div>
                    ) : executeMutation.isError ? (
                      <div className="flex items-start gap-2 text-red-600">
                        <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                        <p className="text-sm">{response}</p>
                      </div>
                    ) : (
                      <p className="text-neutral-700 whitespace-pre-wrap font-mono text-sm">
                        {response}
                      </p>
                    )}
                  </div>

                  {/* Execution Metrics */}
                  {executionMetrics && (
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-white border border-neutral-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 text-neutral-600 text-xs mb-1">
                          <Clock className="h-3 w-3" />
                          Latency
                        </div>
                        <div className="text-lg font-bold text-neutral-800">
                          {executionMetrics.latency_ms.toFixed(0)}ms
                        </div>
                      </div>
                      <div className="bg-white border border-neutral-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 text-neutral-600 text-xs mb-1">
                          <Hash className="h-3 w-3" />
                          Tokens
                        </div>
                        <div className="text-lg font-bold text-neutral-800">
                          {executionMetrics.tokens_used}
                        </div>
                      </div>
                      <div className="bg-white border border-neutral-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 text-neutral-600 text-xs mb-1">
                          <DollarSign className="h-3 w-3" />
                          Cost
                        </div>
                        <div className="text-lg font-bold text-neutral-800">
                          ${executionMetrics.cost.toFixed(4)}
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right Column - Model Configuration & Parameters (1/3 width) */}
        <div className="space-y-4">
          <div className="bg-white border border-neutral-200 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-5">
              <Settings className="h-5 w-5 text-[#FF385C]" />
              <h3 className="font-semibold text-neutral-700">Model & Parameters</h3>
            </div>

            <div className="space-y-5">
              {/* Model Selection */}
              <div>
                <label className="block text-sm font-semibold text-neutral-700 mb-2">
                  Model
                </label>
                <select
                  value={selectedModel?.id || ''}
                  onChange={(e) =>
                    setSelectedModel(availableModels.find((m) => m.id === e.target.value) || null)
                  }
                  disabled={isLoadingModels || availableModels.length === 0}
                  className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 transition-all duration-200 disabled:bg-neutral-100 disabled:text-neutral-400"
                >
                  {isLoadingModels ? (
                    <option>Loading models...</option>
                  ) : availableModels.length === 0 ? (
                    <option>No models configured</option>
                  ) : (
                    availableModels.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.costMultiplier}x){model.input_cost && model.output_cost ? ` - $${model.input_cost.toFixed(5)}/$${model.output_cost.toFixed(5)}` : ''}
                      </option>
                    ))
                  )}
                </select>
                <p className="text-xs text-neutral-500 mt-1">
                  {isLoadingModels ? 'Loading...' : selectedModel ? selectedModel.provider : 'No provider configured'}
                </p>
              </div>
              {/* Temperature - Design System */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-neutral-700 flex items-center gap-1">
                    <Thermometer className="h-4 w-4" />
                    Temperature
                  </label>
                  <span className="text-sm font-mono text-[#FF385C] bg-[#FF385C]/10 px-2 py-0.5 rounded">
                    {temperature.toFixed(1)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-[#FF385C]"
                />
                <p className="text-xs text-neutral-500 mt-1">Controls randomness</p>
              </div>

              {/* Max Tokens - Design System */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-neutral-700 flex items-center gap-1">
                    <Hash className="h-4 w-4" />
                    Max Tokens
                  </label>
                  <span className="text-sm font-mono text-[#FF385C] bg-[#FF385C]/10 px-2 py-0.5 rounded">
                    {maxTokens}
                  </span>
                </div>
                <input
                  type="range"
                  min="100"
                  max="2000"
                  step="100"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full accent-[#FF385C]"
                />
                <p className="text-xs text-neutral-500 mt-1">Maximum response length</p>
              </div>

              {/* Top P - Design System */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-neutral-700 flex items-center gap-1">
                    <Sliders className="h-4 w-4" />
                    Top P
                  </label>
                  <span className="text-sm font-mono text-[#FF385C] bg-[#FF385C]/10 px-2 py-0.5 rounded">
                    {topP.toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={topP}
                  onChange={(e) => setTopP(parseFloat(e.target.value))}
                  className="w-full accent-[#FF385C]"
                />
                <p className="text-xs text-neutral-500 mt-1">Nucleus sampling</p>
              </div>

              {/* Top K - Design System */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-neutral-700 flex items-center gap-1">
                    <Sliders className="h-4 w-4" />
                    Top K
                  </label>
                  <span className="text-sm font-mono text-[#FF385C] bg-[#FF385C]/10 px-2 py-0.5 rounded">
                    {topK}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  className="w-full accent-[#FF385C]"
                />
                <p className="text-xs text-neutral-500 mt-1">Top-K sampling</p>
              </div>
            </div>
          </div>

          {/* Metrics - Design System */}
          {sessions.length > 0 && sessions[0].metrics && (
            <div className="bg-white border border-neutral-200 rounded-xl p-6">
              <h3 className="font-semibold text-neutral-700 mb-4">Last Run Metrics</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-neutral-600">
                    <Clock className="h-4 w-4 text-[#FF385C]" />
                    <span className="text-sm font-medium">Latency</span>
                  </div>
                  <span className="font-semibold text-neutral-700">
                    {sessions[0].metrics.latency.toFixed(2)}s
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-neutral-600">
                    <Hash className="h-4 w-4 text-[#FF385C]" />
                    <span className="text-sm font-medium">Tokens</span>
                  </div>
                  <span className="font-semibold text-neutral-700">{sessions[0].metrics.tokens}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-neutral-600">
                    <DollarSign className="h-4 w-4 text-[#FF385C]" />
                    <span className="text-sm font-medium">Cost</span>
                  </div>
                  <span className="font-semibold text-neutral-700">
                    ${sessions[0].metrics.cost.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History - Enhanced with HistoryCard Components */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white border border-neutral-200 rounded-xl overflow-hidden"
          >
            <div className="p-5 border-b border-neutral-200">
              <h3 className="font-semibold text-neutral-700">Session History</h3>
              <p className="text-xs text-neutral-500 mt-1">
                {sessions.length} session{sessions.length !== 1 ? 's' : ''} • Click to expand details
              </p>
            </div>
            <div className="p-4 space-y-4">
              {sessions.length === 0 ? (
                <div className="py-12 text-center text-neutral-500">
                  <History className="h-12 w-12 mx-auto mb-3 text-neutral-300" />
                  <p className="text-sm">No sessions yet</p>
                  <p className="text-xs mt-1">Run a prompt to create your first session</p>
                </div>
              ) : (
                sessions.map((session) => (
                  <HistoryCard
                    key={session.id}
                    session={session}
                    onLoadIntoEditor={handleLoadSession}
                    defaultExpanded={session.id === sessionId}
                  />
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PlaygroundEnhanced;
