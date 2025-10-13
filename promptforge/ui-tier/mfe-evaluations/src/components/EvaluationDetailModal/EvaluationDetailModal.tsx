/**
 * Evaluation Detail Modal Component (P1)
 *
 * Displays comprehensive evaluation details including:
 * - Trace context (prompt title, model, project)
 * - Evaluation results (score, pass/fail, reasoning)
 * - Execution metrics (tokens, cost, duration)
 * - Input/output data for debugging
 * - Link to trace for navigation
 */

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { evaluationService, EvaluationDetailResponse } from '../../../../shared/services/evaluationService';
import {
  X,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Zap,
  ExternalLink,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

interface EvaluationDetailModalProps {
  evaluationId: string;
  onClose: () => void;
}

export const EvaluationDetailModal: React.FC<EvaluationDetailModalProps> = ({
  evaluationId,
  onClose,
}) => {
  const [detail, setDetail] = useState<EvaluationDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState({
    input: false,
    output: false,
  });

  useEffect(() => {
    loadDetail();
  }, [evaluationId]);

  const loadDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await evaluationService.getEvaluationDetail(evaluationId);
      setDetail(data);
    } catch (err: any) {
      console.error('Failed to load evaluation detail:', err);
      setError(err.message || 'Failed to load evaluation details');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTrace = () => {
    if (detail?.trace_id) {
      // Navigate using window.location for micro-frontend compatibility
      window.location.href = `/traces/${detail.trace_id}`;
      onClose();
    }
  };

  const toggleSection = (section: 'input' | 'output') => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section],
    });
  };

  const getScoreColor = (score: number | null) => {
    if (score === null) return 'text-neutral-400';
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBarWidth = (score: number | null) => {
    if (score === null) return '0%';
    return `${score * 100}%`;
  };

  const getScoreBarColor = (score: number | null) => {
    if (score === null) return 'bg-neutral-300';
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    const loadingContent = (
      <>
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(8px)',
            zIndex: 9999
          }}
          onClick={onClose}
        />
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '3rem 1rem'
          }}
        >
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '3rem',
            boxShadow: '0 20px 40px -8px rgba(0, 0, 0, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.08)'
          }} onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center gap-3">
              <Clock className="h-6 w-6 animate-spin text-primary" />
              <span className="text-lg">Loading evaluation details...</span>
            </div>
          </div>
        </div>
      </>
    );
    return createPortal(loadingContent, document.body);
  }

  if (error || !detail) {
    const errorContent = (
      <>
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(8px)',
            zIndex: 9999
          }}
          onClick={onClose}
        />
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '3rem 1rem'
          }}
        >
          <div style={{
            backgroundColor: 'white',
            borderRadius: '1rem',
            padding: '3rem',
            maxWidth: '32rem',
            boxShadow: '0 20px 40px -8px rgba(0, 0, 0, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.08)'
          }} onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-red-600 mb-2">Error</h3>
            <p className="text-neutral-600 mb-4">{error || 'Evaluation not found'}</p>
            <button
              onClick={onClose}
              className="w-full px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200"
            >
              Close
            </button>
          </div>
        </div>
      </>
    );
    return createPortal(errorContent, document.body);
  }

  const modalContent = (
    <>
      {/* Backdrop - Design System: 60% opacity, 8px blur */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(8px)',
          zIndex: 9999
        }}
        onClick={onClose}
      />

      {/* Modal Container - Design System */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 9999,
          display: 'flex',
          minHeight: '100%',
          alignItems: 'flex-start',
          justifyContent: 'center',
          padding: '3rem 1rem 2rem 1rem'
        }}
      >
        <div
          style={{
            position: 'relative',
            width: '100%',
            maxWidth: '56rem',
            backgroundColor: 'white',
            borderRadius: '1rem',
            boxShadow: '0 20px 40px -8px rgba(0, 0, 0, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.08)',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header - Design System: 2rem 3rem padding */}
          <div className="sticky top-0 bg-white border-b border-neutral-200 rounded-t-2xl" style={{ padding: '2rem 3rem' }}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Title and Status Badge */}
              <div className="flex items-center gap-3 mb-3">
                <h2 className="text-2xl font-bold text-neutral-800">{detail.evaluation_name}</h2>
                {detail.passed !== null && (
                  <span
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold ${
                      detail.passed
                        ? 'bg-[#00A699]/10 text-[#008489]'
                        : 'bg-[#C13515]/10 text-[#C13515]'
                    }`}
                  >
                    {detail.passed ? (
                      <>
                        <CheckCircle className="h-4 w-4" /> Passed
                      </>
                    ) : (
                      <>
                        <XCircle className="h-4 w-4" /> Failed
                      </>
                    )}
                  </span>
                )}
              </div>

              {/* Vendor and Category */}
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                {detail.vendor_name && (
                  <>
                    <span className="font-semibold">Vendor:</span>
                    <span>{detail.vendor_name}</span>
                  </>
                )}
                {detail.vendor_name && detail.category && <span>|</span>}
                {detail.category && (
                  <>
                    <span className="font-semibold">Category:</span>
                    <span className="capitalize">{detail.category}</span>
                  </>
                )}
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors ml-4"
            >
              <X className="h-5 w-5 text-neutral-500" />
            </button>
          </div>
        </div>

        {/* Content - Design System: 3rem padding */}
        <div className="flex-1 overflow-y-auto" style={{ padding: '3rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* What This Evaluates */}
          {detail.description && (
            <div>
              <h3 className="text-sm font-semibold text-neutral-700 mb-2">What this evaluates:</h3>
              <p className="text-sm text-neutral-600 leading-relaxed">{detail.description}</p>
            </div>
          )}

          {/* Score Section */}
          <div>
            <h3 className="text-sm font-semibold text-neutral-700 mb-2">Score:</h3>
            <div className="flex items-baseline gap-2">
              <span className={`text-3xl font-bold ${getScoreColor(detail.score)}`}>
                {detail.score !== null ? detail.score.toFixed(2) : 'N/A'}
              </span>
              <span className="text-sm text-neutral-500">on a 0–1 scale (higher = better)</span>
            </div>

            {detail.score !== null && (
              <div className="mt-3 w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${getScoreBarColor(detail.score)}`}
                  style={{ width: getScoreBarWidth(detail.score) }}
                />
              </div>
            )}

            {detail.passed !== null && (
              <p className="mt-2 text-sm text-neutral-600">
                {detail.passed ? 'Pass' : 'Fail'} because {detail.score?.toFixed(2) || 'N/A'} {detail.passed ? '≥' : '<'} vendor pass threshold.
              </p>
            )}
          </div>

          {/* Evaluation Results */}
          {(detail.reason || detail.explanation) && (
            <div>
              <h3 className="text-sm font-semibold text-neutral-700 mb-2">Results:</h3>
              <div className="space-y-3">
                {detail.reason && (
                  <div className="bg-neutral-50 p-4 rounded-xl">
                    <div className="text-xs font-semibold text-neutral-500 uppercase mb-1">Reason</div>
                    <p className="text-sm text-neutral-800 leading-relaxed">{detail.reason}</p>
                  </div>
                )}
                {detail.explanation && (
                  <div className="bg-neutral-50 p-4 rounded-xl">
                    <div className="text-xs font-semibold text-neutral-500 uppercase mb-1">Explanation</div>
                    <p className="text-sm text-neutral-700 leading-relaxed">{detail.explanation}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* References */}
          <div>
            <h3 className="text-sm font-semibold text-neutral-700 mb-2">References:</h3>
            <div className="flex flex-wrap gap-3 text-sm">
              {detail.vendor_name && (
                <span className="text-neutral-600">
                  <span className="font-medium">{detail.vendor_name}:</span> {detail.evaluation_name}
                </span>
              )}
              {detail.trace_identifier && (
                <span className="text-neutral-600">
                  <span className="font-medium">Eval ID:</span> {detail.trace_identifier}
                </span>
              )}
            </div>
          </div>

          {/* Details Section (Collapsible) */}
          <details className="group">
            <summary className="cursor-pointer list-none">
              <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-xl hover:bg-neutral-100 transition-colors">
                <h3 className="text-sm font-semibold text-neutral-700">Details (optional)</h3>
                <ChevronRight className="h-4 w-4 text-neutral-500 transition-transform group-open:rotate-90" />
              </div>
            </summary>

            <div className="mt-3 p-4 bg-neutral-50 rounded-xl space-y-4">
              {/* Single Row: Runtime | Tokens | Cost | Prompt | Model | Project | Created */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Runtime</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Tokens</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Cost</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Prompt</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Model</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Project</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-neutral-500 uppercase">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-2 px-3 font-medium text-neutral-900 whitespace-nowrap">
                        {detail.execution_time_ms ? `${(detail.execution_time_ms / 1000).toFixed(2)}s` : 'N/A'}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 whitespace-nowrap">
                        {detail.total_tokens ? detail.total_tokens.toLocaleString() : 'N/A'}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 whitespace-nowrap">
                        {detail.evaluation_cost ? `$${detail.evaluation_cost.toFixed(4)}` : 'N/A'}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 truncate max-w-[150px]" title={detail.prompt_title}>
                        {detail.prompt_title}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 truncate max-w-[120px]" title={detail.model_name}>
                        {detail.model_name}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 truncate max-w-[120px]" title={detail.project_name}>
                        {detail.project_name}
                      </td>
                      <td className="py-2 px-3 font-medium text-neutral-900 whitespace-nowrap">
                        {new Date(detail.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* View Full Trace Link */}
              {detail.trace_id && (
                <button
                  type="button"
                  onClick={handleViewTrace}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#FF385C] hover:text-white bg-white hover:bg-[#FF385C] border border-[#FF385C] rounded-xl transition-all"
                >
                  <ExternalLink className="h-4 w-4" />
                  View full trace
                </button>
              )}

              {/* Input/Output Data */}
              {(detail.input_data || detail.output_data) && (
                <div className="space-y-3 pt-3 border-t border-neutral-200">
                  {detail.input_data && (
                    <details className="group/input">
                      <summary className="cursor-pointer list-none">
                        <div className="flex items-center justify-between p-2 hover:bg-neutral-100 rounded-lg">
                          <span className="text-sm font-medium text-neutral-700">Input Data</span>
                          <ChevronRight className="h-3 w-3 text-neutral-500 transition-transform group-open/input:rotate-90" />
                        </div>
                      </summary>
                      <pre className="mt-2 text-xs bg-white p-3 rounded-lg overflow-x-auto max-h-40 border border-neutral-200">
                        {JSON.stringify(detail.input_data, null, 2)}
                      </pre>
                    </details>
                  )}

                  {detail.output_data && (
                    <details className="group/output">
                      <summary className="cursor-pointer list-none">
                        <div className="flex items-center justify-between p-2 hover:bg-neutral-100 rounded-lg">
                          <span className="text-sm font-medium text-neutral-700">Output Data</span>
                          <ChevronRight className="h-3 w-3 text-neutral-500 transition-transform group-open/output:rotate-90" />
                        </div>
                      </summary>
                      <pre className="mt-2 text-xs bg-white p-3 rounded-lg overflow-x-auto max-h-40 border border-neutral-200">
                        {JSON.stringify(detail.output_data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          </details>
        </div>

        {/* Footer - Design System */}
        <div className="sticky bottom-0 bg-neutral-50 border-t border-neutral-200 rounded-b-2xl flex items-center justify-end" style={{ padding: '1.5rem 3rem' }}>
          <button
            onClick={onClose}
            className="px-6 py-2.5 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-xl hover:bg-neutral-100 transition-colors"
          >
            Close
          </button>
        </div>
        </div>
      </div>
    </>
  );

  // Render in portal to escape stacking contexts
  return createPortal(modalContent, document.body);
};
