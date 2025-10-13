import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Brain, Loader2, GitCompare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { InsightsFormState, InsightsResultState } from '../types/insights';
import { DEFAULT_STAGE_PARAMS } from '../types/insights';
import { useAnalyzeTranscript, useEvaluations } from '../hooks/useInsights';
import { fetchAnalysisById } from '../services/insightsService';
import TranscriptInputSection from './sections/TranscriptInputSection';
import ParameterConfigSection from './sections/ParameterConfigSection';
import ExperimentationSection from './sections/ExperimentationSection';
import ResultsSection from './sections/ResultsSection';
import TracesSection from './sections/TracesSection';
import HistorySection from './sections/HistorySection';
import { ComparisonPage } from './pages/ComparisonPage';
import { ComparisonSelector } from './comparison/ComparisonSelector';
import { InsightsProgressModal } from './InsightsProgressModal';

/**
 * Deep Insights Page - Main container for call transcript analysis
 *
 * Features:
 * - Transcript input (text area or file upload)
 * - 3-stage DTA parameter configuration
 * - Summary, insights, and facts display
 * - Trace visualization for each stage
 * - Evaluation metrics display
 * - Deep linking support for analysis/:id, compare/:idA/:idB, comparisons/:id
 */
export const InsightsPage: React.FC = () => {
  // URL params for deep linking
  const { analysisId, analysisIdA, analysisIdB, comparisonId } = useParams<{
    analysisId?: string;
    analysisIdA?: string;
    analysisIdB?: string;
    comparisonId?: string;
  }>();
  const navigate = useNavigate();
  const location = useLocation();

  // View mode: 'analysis' or 'comparison'
  const [viewMode, setViewMode] = useState<'analysis' | 'comparison'>('analysis');
  const [comparisonToView, setComparisonToView] = useState<string | undefined>(undefined);
  const [preselectedAnalysisA, setPreselectedAnalysisA] = useState<string | undefined>(undefined);
  const [preselectedAnalysisB, setPreselectedAnalysisB] = useState<string | undefined>(undefined);

  // Fetch available evaluations from API
  const { data: availableEvaluations, isLoading: isLoadingEvaluations } = useEvaluations({
    is_active: true,
    is_public: true,
  });

  // Form state
  const [formState, setFormState] = useState<InsightsFormState>({
    transcript: '',
    transcriptTitle: '',
    projectId: '',
    enablePiiRedaction: false,
    showAdvancedParams: false,
    stageParams: DEFAULT_STAGE_PARAMS,
    systemPrompts: {
      stage1: '',
      stage2: '',
      stage3: '',
    },
    models: {
      stage1: 'gpt-4o-mini',
      stage2: 'gpt-4o-mini',
      stage3: 'gpt-4o-mini',
    },
    selectedEvaluations: [], // Will be populated when evaluations load
  });

  // Initialize selectedEvaluations when evaluations are loaded
  useEffect(() => {
    if (availableEvaluations && availableEvaluations.length > 0 && formState.selectedEvaluations.length === 0) {
      // Default to first 3 evaluations
      const defaultEvaluations = availableEvaluations.slice(0, 3).map(e => e.id);
      setFormState(prev => ({
        ...prev,
        selectedEvaluations: defaultEvaluations,
      }));
    }
  }, [availableEvaluations, formState.selectedEvaluations.length]);

  // Handler to load analysis by ID (defined before useEffect that calls it)
  const handleLoadAnalysis = async (analysisId: string) => {
    try {
      // Set loading state
      setResultState(prev => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      // Fetch analysis from API
      const analysis = await fetchAnalysisById(analysisId);

      // Populate form with loaded data
      setFormState(prev => ({
        ...prev,
        transcript: analysis.transcript_input,
        transcriptTitle: analysis.transcript_title || '',
        projectId: analysis.project_id || '',
        systemPrompts: {
          stage1: analysis.system_prompt_stage1 || '',
          stage2: analysis.system_prompt_stage2 || '',
          stage3: analysis.system_prompt_stage3 || '',
        },
        models: {
          stage1: analysis.model_stage1 || 'gpt-4o-mini',
          stage2: analysis.model_stage2 || 'gpt-4o-mini',
          stage3: analysis.model_stage3 || 'gpt-4o-mini',
        },
      }));

      // Extract model parameters from analysis_metadata or use defaults
      const modelParams = analysis.analysis_metadata?.model_parameters || {};
      const stage1Params = modelParams.stage1 || DEFAULT_STAGE_PARAMS.factExtraction;
      const stage2Params = modelParams.stage2 || DEFAULT_STAGE_PARAMS.reasoning;
      const stage3Params = modelParams.stage3 || DEFAULT_STAGE_PARAMS.summary;

      // Build traces array from system prompts, models, and actual parameters
      const traces = [
        {
          trace_id: `${analysis.id}-stage1`,
          stage: 'Stage 1: Fact Extraction',
          model: analysis.model_stage1 || 'gpt-4o-mini',
          temperature: stage1Params.temperature ?? 0.25,
          top_p: stage1Params.top_p ?? 0.95,
          max_tokens: stage1Params.max_tokens ?? 1000,
          input_tokens: 0,
          output_tokens: 0,
          total_tokens: 0,
          duration_ms: 0,
          cost: 0,
          system_prompt: analysis.system_prompt_stage1 || null,
        },
        {
          trace_id: `${analysis.id}-stage2`,
          stage: 'Stage 2: Reasoning & Insights',
          model: analysis.model_stage2 || 'gpt-4o-mini',
          temperature: stage2Params.temperature ?? 0.65,
          top_p: stage2Params.top_p ?? 0.95,
          max_tokens: stage2Params.max_tokens ?? 1500,
          input_tokens: 0,
          output_tokens: 0,
          total_tokens: 0,
          duration_ms: 0,
          cost: 0,
          system_prompt: analysis.system_prompt_stage2 || null,
        },
        {
          trace_id: `${analysis.id}-stage3`,
          stage: 'Stage 3: Summary Synthesis',
          model: analysis.model_stage3 || 'gpt-4o-mini',
          temperature: stage3Params.temperature ?? 0.45,
          top_p: stage3Params.top_p ?? 0.95,
          max_tokens: stage3Params.max_tokens ?? 800,
          input_tokens: 0,
          output_tokens: 0,
          total_tokens: 0,
          duration_ms: 0,
          cost: 0,
          system_prompt: analysis.system_prompt_stage3 || null,
        },
      ];

      // Populate results
      setResultState({
        analysisId: analysis.id,
        summary: analysis.summary_output,
        insights: analysis.insights_output,
        facts: analysis.facts_output,
        traces: traces,
        evaluations: [], // Would need to fetch evaluations separately if needed
        totalTokens: analysis.total_tokens,
        totalCost: analysis.total_cost,
        isLoading: false,
        error: null,
      });

      // Scroll to results
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      setResultState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load analysis',
      }));
    }
  };

  // Handle deep linking via URL params and route detection
  useEffect(() => {
    // Auto-load analysis if analysisId is in URL
    if (analysisId) {
      handleLoadAnalysis(analysisId);
      setViewMode('analysis'); // Ensure we're in analysis mode
      return;
    }

    // Switch to comparison view if comparison routes are used
    if (comparisonId) {
      setComparisonToView(comparisonId);
      setViewMode('comparison');
      return;
    }

    // Pre-select analyses for ad-hoc comparison
    if (analysisIdA && analysisIdB) {
      setPreselectedAnalysisA(analysisIdA);
      setPreselectedAnalysisB(analysisIdB);
      setViewMode('comparison');
      return;
    }

    // Check if we're on the /compare route (comparison selector with no params)
    if (location.pathname.includes('/compare')) {
      setComparisonToView(undefined);
      setPreselectedAnalysisA(undefined);
      setPreselectedAnalysisB(undefined);
      setViewMode('comparison');
      return;
    }

    // Default to analysis mode for main page
    if (location.pathname === '/insights' || location.pathname === '/insights/') {
      setViewMode('analysis');
    }
  }, [analysisId, analysisIdA, analysisIdB, comparisonId, location.pathname]);

  // Result state
  const [resultState, setResultState] = useState<InsightsResultState>({
    analysisId: null,
    summary: null,
    insights: null,
    facts: null,
    traces: [],
    evaluations: [],
    totalTokens: 0,
    totalCost: 0,
    isLoading: false,
    error: null,
  });

  // API mutation
  const analyzeTranscriptMutation = useAnalyzeTranscript();

  const handleAnalyze = () => {
    // Validation
    const errors: string[] = [];

    if (!formState.transcriptTitle.trim()) {
      errors.push('Title is required');
    }

    if (formState.transcriptTitle.trim().length > 500) {
      errors.push('Title is too long (max 500 characters)');
    }

    if (!formState.transcript.trim()) {
      errors.push('Transcript is required');
    }

    if (formState.transcript.trim().length < 100) {
      errors.push('Transcript must be at least 100 characters');
    }

    if (formState.transcript.trim().length > 100000) {
      errors.push('Transcript is too long (max 100,000 characters)');
    }

    if (errors.length > 0) {
      setResultState(prev => ({
        ...prev,
        error: errors.join(', '),
      }));
      return;
    }

    // Clear previous results
    setResultState({
      analysisId: null,
      summary: null,
      insights: null,
      facts: null,
      traces: [],
      evaluations: [],
      totalTokens: 0,
      totalCost: 0,
      isLoading: true,
      error: null,
    });

    // Execute analysis
    analyzeTranscriptMutation.mutate(
      {
        transcript: formState.transcript.trim(),
        transcript_title: formState.transcriptTitle.trim(),
        project_id: formState.projectId || undefined,
        enable_pii_redaction: formState.enablePiiRedaction,
        stage_params: formState.showAdvancedParams ? {
          fact_extraction: formState.stageParams.factExtraction,
          reasoning: formState.stageParams.reasoning,
          summary: formState.stageParams.summary,
        } : undefined,
        system_prompts: (formState.systemPrompts.stage1 || formState.systemPrompts.stage2 || formState.systemPrompts.stage3) ? {
          stage1_fact_extraction: formState.systemPrompts.stage1 || undefined,
          stage2_reasoning: formState.systemPrompts.stage2 || undefined,
          stage3_summary: formState.systemPrompts.stage3 || undefined,
        } : undefined,
        models: {
          stage1_model: formState.models.stage1,
          stage2_model: formState.models.stage2,
          stage3_model: formState.models.stage3,
        },
        evaluations: formState.selectedEvaluations.length > 0
          ? formState.selectedEvaluations
          : undefined,
      },
      {
        onSuccess: (data) => {
          setResultState({
            analysisId: data.analysis_id,
            summary: data.summary,
            insights: data.insights,
            facts: data.facts,
            traces: data.traces,
            evaluations: data.evaluations,
            totalTokens: data.total_tokens,
            totalCost: data.total_cost,
            isLoading: false,
            error: null,
          });
        },
        onError: (error) => {
          setResultState(prev => ({
            ...prev,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Analysis failed',
          }));
        },
      }
    );
  };

  const handleClear = () => {
    const defaultEvaluations = availableEvaluations && availableEvaluations.length > 0
      ? availableEvaluations.slice(0, 3).map(e => e.id)
      : [];

    setFormState({
      transcript: '',
      transcriptTitle: '',
      projectId: '',
      enablePiiRedaction: false,
      showAdvancedParams: false,
      stageParams: DEFAULT_STAGE_PARAMS,
      systemPrompts: {
        stage1: '',
        stage2: '',
        stage3: '',
      },
      models: {
        stage1: 'gpt-4o-mini',
        stage2: 'gpt-4o-mini',
        stage3: 'gpt-4o-mini',
      },
      selectedEvaluations: defaultEvaluations,
    });
    setResultState({
      analysisId: null,
      summary: null,
      insights: null,
      facts: null,
      traces: [],
      evaluations: [],
      totalTokens: 0,
      totalCost: 0,
      isLoading: false,
      error: null,
    });
  };

  const handleCompareAnalyses = (analysisAId: string, analysisBId: string) => {
    // Navigate to comparison route (enables deep linking + bookmarking)
    navigate(`/insights/compare/${analysisAId}/${analysisBId}`);
  };

  const handleViewComparison = (comparisonId: string) => {
    // Navigate to saved comparison route
    navigate(`/insights/comparisons/${comparisonId}`);
  };

  // Render comparison view if in comparison mode
  if (viewMode === 'comparison') {
    return (
      <ComparisonPage
        comparisonId={comparisonToView}
        preselectedAnalysisAId={preselectedAnalysisA}
        preselectedAnalysisBId={preselectedAnalysisB}
        onBack={() => navigate('/insights')}
        onViewAnalysis={(id) => navigate(`/insights/analysis/${id}`)}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* ARIA Live Region for Screen Readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {resultState.isLoading && "Analyzing transcript, please wait"}
        {resultState.error && `Error: ${resultState.error}`}
        {resultState.summary && "Analysis complete"}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#FF385C]/10 rounded-xl">
              <Brain className="h-6 w-6 text-[#FF385C]" />
            </div>
            <h1 className="text-3xl font-bold text-neutral-700">Deep Insights</h1>
          </div>
          <p className="text-neutral-600 mt-2 font-medium">
            Analyze call transcripts with 3-stage Dynamic Temperature Adjustment
          </p>
        </div>

        {/* Comparison Button */}
        <button
          onClick={() => navigate('/insights/compare')}
          className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-[#FF385C] text-[#FF385C] rounded-lg hover:bg-pink-50 transition-colors font-semibold"
        >
          <GitCompare className="h-4 w-4" />
          Compare Analyses
        </button>
      </div>

      {/* History Section */}
      <HistorySection
        onSelectAnalysis={handleLoadAnalysis}
        onCompareAnalyses={handleCompareAnalyses}
      />

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Input Form (2/3 width) */}
        <div className="col-span-2 space-y-6">
          <TranscriptInputSection
            formState={formState}
            setFormState={setFormState}
          />

          <ParameterConfigSection
            formState={formState}
            setFormState={setFormState}
          />

          <ExperimentationSection
            formState={formState}
            setFormState={setFormState}
          />

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleAnalyze}
              disabled={resultState.isLoading || !formState.transcriptTitle.trim() || !formState.transcript.trim()}
              className="flex items-center justify-center gap-2 h-12 bg-[#FF385C] text-white px-8 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 disabled:bg-neutral-300 disabled:text-neutral-500 disabled:cursor-not-allowed font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
            >
              {resultState.isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Analyze Transcript
                </>
              )}
            </button>

            <button
              onClick={handleClear}
              disabled={resultState.isLoading}
              className="flex items-center justify-center gap-2 h-12 bg-white border-2 border-neutral-200 text-neutral-700 px-6 rounded-xl hover:border-neutral-300 hover:bg-neutral-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold focus:outline-none focus:ring-4 focus:ring-neutral-200"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Right Column - Info Panel (1/3 width) */}
        <div className="space-y-4">
          <div className="bg-white border border-neutral-200 rounded-xl p-6">
            <h3 className="font-semibold text-neutral-700 mb-4 flex items-center gap-2">
              <Brain className="h-5 w-5 text-[#FF385C]" />
              How it Works
            </h3>
            <div className="space-y-4 text-sm">
              {/* Pipeline Overview */}
              <div className="bg-[#FF385C]/5 rounded-lg p-3 border border-[#FF385C]/10">
                <p className="text-neutral-600 leading-relaxed">
                  Deep Insights uses a <span className="font-semibold text-neutral-700">3-stage Dynamic Temperature Adjustment (DTA)</span> pipeline to analyze call transcripts with precision and creativity.
                </p>
              </div>

              {/* Stage 1 */}
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                  1
                </div>
                <div>
                  <div className="font-semibold text-neutral-700 mb-1">Fact Extraction</div>
                  <div className="text-neutral-600 leading-relaxed mb-2">
                    Low temperature (0.25) ensures deterministic extraction of verified facts, entities, and key details from the transcript.
                  </div>
                  <div className="text-xs text-neutral-500 font-mono bg-neutral-50 rounded px-2 py-1 inline-block">
                    temp: 0.25 • top_p: 0.95 • max: 1000 tokens
                  </div>
                </div>
              </div>

              {/* Stage 2 */}
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xs">
                  2
                </div>
                <div>
                  <div className="font-semibold text-neutral-700 mb-1">Reasoning & Insights</div>
                  <div className="text-neutral-600 leading-relaxed mb-2">
                    Higher temperature (0.65) enables creative analysis to generate actionable insights, patterns, and recommendations from extracted facts.
                  </div>
                  <div className="text-xs text-neutral-500 font-mono bg-neutral-50 rounded px-2 py-1 inline-block">
                    temp: 0.65 • top_p: 0.95 • max: 1500 tokens
                  </div>
                </div>
              </div>

              {/* Stage 3 */}
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-bold text-xs">
                  3
                </div>
                <div>
                  <div className="font-semibold text-neutral-700 mb-1">Summary Synthesis</div>
                  <div className="text-neutral-600 leading-relaxed mb-2">
                    Balanced temperature (0.45) creates a concise, coherent summary that captures key points while maintaining readability.
                  </div>
                  <div className="text-xs text-neutral-500 font-mono bg-neutral-50 rounded px-2 py-1 inline-block">
                    temp: 0.45 • top_p: 0.95 • max: 800 tokens
                  </div>
                </div>
              </div>

              {/* Evaluations Note */}
              <div className="pt-3 border-t border-neutral-200">
                <div className="flex items-start gap-2">
                  <svg className="h-4 w-4 text-[#FF385C] mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-xs text-neutral-600 leading-relaxed">
                    Each stage is traced independently, and optional evaluations validate output quality, factual accuracy, and relevance.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* PII Badge */}
          {formState.enablePiiRedaction && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center gap-2 text-green-700 font-semibold text-sm">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                PII Protection Enabled
              </div>
              <div className="text-xs text-green-600 mt-1">
                Sensitive information will be redacted before LLM processing
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      <AnimatePresence>
        {(resultState.summary || resultState.error || resultState.isLoading) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <ResultsSection resultState={resultState} />

            {resultState.traces.length > 0 && (
              <TracesSection traces={resultState.traces} />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress Modal */}
      <InsightsProgressModal isVisible={resultState.isLoading} />
    </div>
  );
};

export default InsightsPage;
