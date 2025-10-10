import React from 'react';
import { Modal } from '../../../../shared/components/core/Modal';
import { Button } from '../../../../shared/components/core/Button';
import { CheckCircle, XCircle, ExternalLink, Play, Hash, Zap, DollarSign, Clock, Calendar } from 'lucide-react';
import { EvaluationResult } from '../../types/customEvaluation';

export interface EvaluationDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluation: EvaluationResult | null;
  onViewTrace?: (traceId: string) => void;
  onRerun?: (evaluationId: string, traceId: string) => void;
}

const getScoreColor = (score: number): string => {
  if (score >= 90) return 'bg-[#00A699]';      // Excellent
  if (score >= 70) return 'bg-[#FFB400]';       // Good
  return 'bg-[#C13515]';                        // Poor
};

export const EvaluationDetailModal: React.FC<EvaluationDetailModalProps> = ({
  isOpen,
  onClose,
  evaluation,
  onViewTrace,
  onRerun,
}) => {
  if (!evaluation) return null;

  const handleViewTrace = () => {
    if (onViewTrace) {
      onViewTrace(evaluation.trace_id);
    }
  };

  const handleRerun = () => {
    if (onRerun) {
      onRerun(evaluation.evaluation_id, evaluation.trace_id);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Evaluation Result: ${evaluation.name}`}
      size="lg"
      footer={
        <div className="flex justify-end gap-3">
          {onViewTrace && (
            <Button
              variant="secondary"
              onClick={handleViewTrace}
            >
              <ExternalLink className="h-4 w-4" />
              View Trace
            </Button>
          )}
          {onRerun && (
            <Button
              variant="secondary"
              onClick={handleRerun}
            >
              <Play className="h-4 w-4" />
              Rerun Evaluation
            </Button>
          )}
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Score Section */}
        <div className="p-5 bg-neutral-50 border border-neutral-200 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">
              Score
            </h3>
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                evaluation.passed
                  ? 'bg-[#00A699]/10 text-[#008489]'
                  : 'bg-[#C13515]/10 text-[#C13515]'
              }`}
            >
              {evaluation.passed ? (
                <CheckCircle className="h-3 w-3" />
              ) : (
                <XCircle className="h-3 w-3" />
              )}
              {evaluation.passed ? 'Passed' : 'Failed'}
            </span>
          </div>

          {/* Score Bar */}
          <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getScoreColor(evaluation.score)} transition-all duration-500`}
              style={{ width: `${evaluation.score}%` }}
              role="progressbar"
              aria-valuenow={evaluation.score}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>

          <div className="flex items-baseline justify-between mt-3">
            <span className="text-3xl font-bold text-neutral-700">{evaluation.score}%</span>
            <span className="text-sm text-neutral-600 font-medium">Model: {evaluation.model}</span>
          </div>
        </div>

        {/* Input/Output Comparison */}
        <div className="p-5 bg-white border border-neutral-200 rounded-xl">
          <h3 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide mb-4">
            Input & Output Comparison
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Input */}
            <div>
              <h4 className="text-xs font-semibold text-neutral-600 uppercase tracking-wide mb-2">
                Input
              </h4>
              <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-lg max-h-[200px] overflow-y-auto">
                <p className="text-sm text-neutral-700 leading-relaxed whitespace-pre-wrap">
                  {evaluation.input}
                </p>
              </div>
            </div>

            {/* Output */}
            <div>
              <h4 className="text-xs font-semibold text-neutral-600 uppercase tracking-wide mb-2">
                Output
              </h4>
              <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-lg max-h-[200px] overflow-y-auto">
                <p className="text-sm text-neutral-700 leading-relaxed whitespace-pre-wrap">
                  {evaluation.output}
                </p>
              </div>
            </div>
          </div>

          {/* Evaluation Reason (if available) */}
          {evaluation.reason && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-neutral-600 uppercase tracking-wide mb-2">
                Evaluation Reason
              </h4>
              <div className="p-4 bg-[#0066FF]/5 border border-[#0066FF]/20 rounded-lg">
                <p className="text-sm text-neutral-700 leading-relaxed">
                  {evaluation.reason}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="p-5 bg-white border border-neutral-200 rounded-xl">
          <h3 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide mb-4">
            Metadata
          </h3>

          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <Hash className="h-4 w-4 text-neutral-500 mt-0.5" />
              <div className="flex-1">
                <span className="text-sm text-neutral-600">Trace ID: </span>
                <code className="text-sm text-neutral-700 font-mono">{evaluation.trace_id}</code>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <Zap className="h-4 w-4 text-neutral-500 mt-0.5" />
              <div className="flex-1">
                <span className="text-sm text-neutral-600">Tokens Used: </span>
                <span className="text-sm text-neutral-700 font-medium">
                  {evaluation.tokens_used.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <DollarSign className="h-4 w-4 text-neutral-500 mt-0.5" />
              <div className="flex-1">
                <span className="text-sm text-neutral-600">Cost: </span>
                <span className="text-sm text-neutral-700 font-medium">
                  ${evaluation.cost_usd.toFixed(3)}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <Clock className="h-4 w-4 text-neutral-500 mt-0.5" />
              <div className="flex-1">
                <span className="text-sm text-neutral-600">Duration: </span>
                <span className="text-sm text-neutral-700 font-medium">
                  {evaluation.time_taken_ms}ms
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <Calendar className="h-4 w-4 text-neutral-500 mt-0.5" />
              <div className="flex-1">
                <span className="text-sm text-neutral-600">Created: </span>
                <span className="text-sm text-neutral-700 font-medium">
                  {new Date(evaluation.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};
