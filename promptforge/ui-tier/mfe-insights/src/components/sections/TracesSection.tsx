import React from 'react';
import { Activity, Clock, Hash, DollarSign, Thermometer } from 'lucide-react';
import type { TraceMetadata } from '../../types/insights';

interface Props {
  traces: TraceMetadata[];
}

/**
 * Traces Section
 *
 * Displays execution traces for each of the 3 DTA stages:
 * - Stage 1: Fact Extraction
 * - Stage 2: Reasoning & Insights
 * - Stage 3: Summary Synthesis
 *
 * Shows: model, temperature, tokens, duration, cost
 */
export const TracesSection: React.FC<Props> = ({ traces }) => {
  if (traces.length === 0) {
    return null;
  }

  const getStageColor = (stage: string): string => {
    if (stage.includes('fact') || stage.includes('extraction')) return 'bg-blue-50 border-blue-200';
    if (stage.includes('reasoning') || stage.includes('insight')) return 'bg-purple-50 border-purple-200';
    if (stage.includes('summary') || stage.includes('synthesis')) return 'bg-green-50 border-green-200';
    return 'bg-neutral-50 border-neutral-200';
  };

  const getStageTextColor = (stage: string): string => {
    if (stage.includes('fact') || stage.includes('extraction')) return 'text-blue-700';
    if (stage.includes('reasoning') || stage.includes('insight')) return 'text-purple-700';
    if (stage.includes('summary') || stage.includes('synthesis')) return 'text-green-700';
    return 'text-neutral-700';
  };

  const getStageNumber = (stage: string): number => {
    if (stage.includes('fact') || stage.includes('extraction')) return 1;
    if (stage.includes('reasoning') || stage.includes('insight')) return 2;
    if (stage.includes('summary') || stage.includes('synthesis')) return 3;
    return 0;
  };

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-5">
        <Activity className="h-5 w-5 text-[#FF385C]" />
        <h3 className="font-semibold text-neutral-700">Execution Traces</h3>
        <span className="ml-auto text-sm text-neutral-500">
          {traces.length} {traces.length === 1 ? 'stage' : 'stages'}
        </span>
      </div>

      <div className="space-y-4">
        {traces.map((trace, index) => (
          <div
            key={trace.trace_id}
            className={`border-2 rounded-xl p-4 transition-all ${getStageColor(trace.stage)}`}
          >
            {/* Stage Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full bg-white border-2 flex items-center justify-center font-bold ${
                  trace.stage.includes('fact') ? 'border-blue-500 text-blue-700' :
                  trace.stage.includes('reasoning') ? 'border-purple-500 text-purple-700' :
                  'border-green-500 text-green-700'
                }`}>
                  {getStageNumber(trace.stage)}
                </div>
                <div>
                  <div className={`font-semibold ${getStageTextColor(trace.stage)}`}>
                    {trace.stage}
                  </div>
                  <div className="text-xs text-neutral-500 mt-0.5">
                    Model: {trace.model}
                  </div>
                </div>
              </div>

              {/* Temperature Badge */}
              <div className="flex items-center gap-1.5 bg-white border-2 border-neutral-200 rounded-lg px-3 py-1.5">
                <Thermometer className="h-4 w-4 text-[#FF385C]" />
                <span className="text-sm font-mono font-semibold text-neutral-700">
                  {trace.temperature.toFixed(1)}
                </span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-4 gap-3">
              {/* Duration */}
              <div className="bg-white border border-neutral-200 rounded-lg p-3">
                <div className="flex items-center gap-1.5 text-neutral-600 text-xs mb-1">
                  <Clock className="h-3 w-3" />
                  Duration
                </div>
                <div className="text-base font-bold text-neutral-800">
                  {trace.duration_ms.toFixed(0)}ms
                </div>
              </div>

              {/* Tokens */}
              <div className="bg-white border border-neutral-200 rounded-lg p-3">
                <div className="flex items-center gap-1.5 text-neutral-600 text-xs mb-1">
                  <Hash className="h-3 w-3" />
                  Tokens
                </div>
                <div className="text-base font-bold text-neutral-800">
                  {trace.total_tokens.toLocaleString()}
                </div>
                <div className="text-xs text-neutral-500 mt-0.5">
                  {trace.input_tokens} in • {trace.output_tokens} out
                </div>
              </div>

              {/* Cost */}
              <div className="bg-white border border-neutral-200 rounded-lg p-3">
                <div className="flex items-center gap-1.5 text-neutral-600 text-xs mb-1">
                  <DollarSign className="h-3 w-3" />
                  Cost
                </div>
                <div className="text-base font-bold text-neutral-800">
                  ${trace.cost.toFixed(4)}
                </div>
              </div>

              {/* Parameters */}
              <div className="bg-white border border-neutral-200 rounded-lg p-3">
                <div className="text-neutral-600 text-xs mb-1">
                  Parameters
                </div>
                <div className="text-xs font-mono text-neutral-600 space-y-0.5">
                  <div>top_p: {trace.top_p.toFixed(2)}</div>
                  <div>max: {trace.max_tokens}</div>
                </div>
              </div>
            </div>

            {/* Trace ID */}
            <div className="mt-3 pt-3 border-t border-neutral-200">
              <div className="text-xs text-neutral-500">
                Trace ID:{' '}
                <span className="font-mono text-neutral-600">{trace.trace_id}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Total Summary */}
      {traces.length > 1 && (
        <div className="mt-4 pt-4 border-t-2 border-neutral-200">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm text-neutral-600 mb-1">Total Duration</div>
              <div className="text-xl font-bold text-neutral-800">
                {traces.reduce((sum, t) => sum + t.duration_ms, 0).toFixed(0)}ms
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-neutral-600 mb-1">Total Tokens</div>
              <div className="text-xl font-bold text-neutral-800">
                {traces.reduce((sum, t) => sum + t.total_tokens, 0).toLocaleString()}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-neutral-600 mb-1">Total Cost</div>
              <div className="text-xl font-bold text-neutral-800">
                ${traces.reduce((sum, t) => sum + t.cost, 0).toFixed(4)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TracesSection;
