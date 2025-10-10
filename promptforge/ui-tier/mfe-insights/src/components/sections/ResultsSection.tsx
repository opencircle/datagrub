import React, { useState } from 'react';
import { FileText, Lightbulb, CheckCircle, AlertCircle, Loader, Code } from 'lucide-react';
import type { InsightsResultState } from '../../types/insights';
import EvaluationMetricsTable from '../results/EvaluationMetricsTable';

interface Props {
  resultState: InsightsResultState;
}

/**
 * Results Section
 *
 * Features:
 * - Tabbed view: Summary | Insights | Facts | System Prompts
 * - Evaluation metrics table
 * - Token usage and cost display
 * - Loading and error states
 */
export const ResultsSection: React.FC<Props> = ({ resultState }) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'insights' | 'facts' | 'prompts'>('summary');

  if (resultState.isLoading) {
    return (
      <div className="bg-white border border-neutral-200 rounded-xl p-8">
        <div className="flex flex-col items-center justify-center gap-4 text-neutral-600">
          <Loader className="h-8 w-8 animate-spin text-[#FF385C]" />
          <div>
            <div className="font-semibold text-neutral-700 text-center">Analyzing transcript...</div>
            <div className="text-sm text-neutral-500 text-center mt-1">
              Running 3-stage DTA pipeline
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (resultState.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-red-700 mb-1">Analysis Failed</div>
            <div className="text-sm text-red-600">{resultState.error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!resultState.summary && !resultState.insights && !resultState.facts) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="bg-green-50 border border-green-200 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <CheckCircle className="h-6 w-6 text-green-600" />
          <div>
            <div className="font-semibold text-green-700">Analysis Complete</div>
            <div className="text-sm text-green-600 mt-0.5">
              {resultState.totalTokens.toLocaleString()} tokens used •
              ${resultState.totalCost.toFixed(4)} total cost
            </div>
          </div>
        </div>
      </div>

      {/* Results Card */}
      <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden">
        {/* Tab Navigation */}
        <div className="flex border-b border-neutral-200 bg-neutral-50">
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-semibold transition-all ${
              activeTab === 'summary'
                ? 'bg-white text-[#FF385C] border-b-2 border-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800 hover:bg-neutral-100'
            }`}
          >
            <FileText className="h-5 w-5" />
            Summary
          </button>

          <button
            onClick={() => setActiveTab('insights')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-semibold transition-all ${
              activeTab === 'insights'
                ? 'bg-white text-[#FF385C] border-b-2 border-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800 hover:bg-neutral-100'
            }`}
          >
            <Lightbulb className="h-5 w-5" />
            Insights
          </button>

          <button
            onClick={() => setActiveTab('facts')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-semibold transition-all ${
              activeTab === 'facts'
                ? 'bg-white text-[#FF385C] border-b-2 border-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800 hover:bg-neutral-100'
            }`}
          >
            <CheckCircle className="h-5 w-5" />
            Facts
          </button>

          <button
            onClick={() => setActiveTab('prompts')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-semibold transition-all ${
              activeTab === 'prompts'
                ? 'bg-white text-[#FF385C] border-b-2 border-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800 hover:bg-neutral-100'
            }`}
          >
            <Code className="h-5 w-5" />
            System Prompts
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'summary' && resultState.summary && (
            <div>
              <h3 className="font-semibold text-neutral-700 mb-3">Call Summary</h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-neutral-600 whitespace-pre-wrap leading-relaxed">
                  {resultState.summary}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'insights' && resultState.insights && (
            <div>
              <h3 className="font-semibold text-neutral-700 mb-3">Key Insights</h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-neutral-600 whitespace-pre-wrap leading-relaxed">
                  {resultState.insights}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'facts' && resultState.facts && (
            <div>
              <h3 className="font-semibold text-neutral-700 mb-3">Extracted Facts</h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-neutral-600 whitespace-pre-wrap leading-relaxed">
                  {resultState.facts}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'prompts' && resultState.traces && resultState.traces.length > 0 && (
            <div className="space-y-6">
              <h3 className="font-semibold text-neutral-700 mb-4">System Prompts Used</h3>
              {resultState.traces.map((trace, index) => (
                <div key={trace.trace_id} className="border border-neutral-200 rounded-lg overflow-hidden">
                  {/* Stage Header */}
                  <div className="bg-neutral-50 px-4 py-3 border-b border-neutral-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono bg-neutral-200 text-neutral-700 px-2 py-1 rounded">
                          Stage {index + 1}
                        </span>
                        <span className="text-sm font-semibold text-neutral-700">{trace.stage}</span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-neutral-600">
                        <span>{trace.model}</span>
                        <span>temp: {trace.temperature}</span>
                        <span>{trace.total_tokens.toLocaleString()} tokens</span>
                      </div>
                    </div>
                  </div>

                  {/* System Prompt Content */}
                  <div className="p-4 bg-white">
                    {trace.system_prompt ? (
                      <pre className="bg-neutral-50 border border-neutral-200 rounded-lg p-4 text-xs overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap font-mono text-neutral-700">
                        {trace.system_prompt}
                      </pre>
                    ) : (
                      <p className="text-sm text-neutral-500 italic">No custom system prompt (using default)</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Evaluation Metrics */}
      {resultState.evaluations.length > 0 && (
        <EvaluationMetricsTable evaluations={resultState.evaluations} />
      )}
    </div>
  );
};

export default ResultsSection;
