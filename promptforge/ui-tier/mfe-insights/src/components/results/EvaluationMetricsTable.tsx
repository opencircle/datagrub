import React from 'react';
import { Target, CheckCircle, XCircle, Hash, DollarSign } from 'lucide-react';
import type { EvaluationMetric } from '../../types/insights';

interface Props {
  evaluations: EvaluationMetric[];
}

/**
 * Evaluation Metrics Table
 *
 * Displays evaluation results with:
 * - Evaluation name and score
 * - Pass/Fail status with color coding
 * - Token usage and cost per evaluation
 * - Threshold information
 */
export const EvaluationMetricsTable: React.FC<Props> = ({ evaluations }) => {
  if (evaluations.length === 0) {
    return null;
  }

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-700';
    if (score >= 0.6) return 'text-yellow-700';
    return 'text-red-700';
  };

  const getScoreBackgroundColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-50 border-green-200';
    if (score >= 0.6) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const totalEvaluationTokens = evaluations.reduce((sum, e) => sum + (e.total_tokens ?? 0), 0);
  const totalEvaluationCost = evaluations.reduce((sum, e) => sum + (e.evaluation_cost ?? 0), 0);

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-[#FF385C]" />
          <h3 className="font-semibold text-neutral-700">Evaluation Metrics</h3>
        </div>
        <div className="text-sm text-neutral-500">
          {evaluations.length} {evaluations.length === 1 ? 'evaluation' : 'evaluations'}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-neutral-200">
              <th className="text-left py-3 px-3 text-sm font-semibold text-neutral-700">
                Evaluation
              </th>
              <th className="text-center py-3 px-3 text-sm font-semibold text-neutral-700">
                Score
              </th>
              <th className="text-center py-3 px-3 text-sm font-semibold text-neutral-700">
                Status
              </th>
              <th className="text-center py-3 px-3 text-sm font-semibold text-neutral-700">
                Tokens
              </th>
              <th className="text-center py-3 px-3 text-sm font-semibold text-neutral-700">
                Cost
              </th>
              <th className="text-left py-3 px-3 text-sm font-semibold text-neutral-700">
                Reason
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {evaluations.map((evaluation) => (
              <tr key={evaluation.evaluation_uuid} className="hover:bg-neutral-50 transition-colors">
                {/* Evaluation Name */}
                <td className="py-4 px-3">
                  <div className="font-semibold text-sm text-neutral-700">
                    {evaluation.evaluation_name}
                  </div>
                  {evaluation.category && (
                    <div className="text-xs text-neutral-500 mt-0.5">
                      {evaluation.category}
                    </div>
                  )}
                </td>

                {/* Score */}
                <td className="py-4 px-3 text-center">
                  <div className={`inline-flex items-center justify-center border-2 rounded-lg px-3 py-1 ${getScoreBackgroundColor(evaluation.score)}`}>
                    <span className={`text-lg font-bold font-mono ${getScoreColor(evaluation.score)}`}>
                      {(evaluation.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  {evaluation.threshold != null && (
                    <div className="text-xs text-neutral-500 mt-1">
                      Threshold: {(evaluation.threshold * 100).toFixed(0)}%
                    </div>
                  )}
                </td>

                {/* Pass/Fail Status */}
                <td className="py-4 px-3 text-center">
                  {evaluation.passed ? (
                    <div className="inline-flex items-center gap-1.5 bg-green-50 border-2 border-green-200 rounded-lg px-3 py-1">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-semibold text-green-700">Pass</span>
                    </div>
                  ) : (
                    <div className="inline-flex items-center gap-1.5 bg-red-50 border-2 border-red-200 rounded-lg px-3 py-1">
                      <XCircle className="h-4 w-4 text-red-600" />
                      <span className="text-sm font-semibold text-red-700">Fail</span>
                    </div>
                  )}
                </td>

                {/* Tokens */}
                <td className="py-4 px-3 text-center">
                  {evaluation.total_tokens != null ? (
                    <div>
                      <div className="flex items-center justify-center gap-1 text-sm font-semibold text-neutral-700">
                        <Hash className="h-3 w-3" />
                        {evaluation.total_tokens.toLocaleString()}
                      </div>
                      {evaluation.input_tokens != null && evaluation.output_tokens != null && (
                        <div className="text-xs text-neutral-500 mt-0.5">
                          {evaluation.input_tokens} in • {evaluation.output_tokens} out
                        </div>
                      )}
                    </div>
                  ) : (
                    <span className="text-sm text-neutral-400">-</span>
                  )}
                </td>

                {/* Cost */}
                <td className="py-4 px-3 text-center">
                  {evaluation.evaluation_cost != null ? (
                    <div className="flex items-center justify-center gap-1 text-sm font-semibold text-neutral-700">
                      <DollarSign className="h-3 w-3" />
                      {evaluation.evaluation_cost.toFixed(4)}
                    </div>
                  ) : (
                    <span className="text-sm text-neutral-400">-</span>
                  )}
                </td>

                {/* Reason */}
                <td className="py-4 px-3">
                  <div className="text-sm text-neutral-600 max-w-xs line-clamp-2">
                    {evaluation.reason}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Footer */}
      {evaluations.length > 1 && (
        <div className="mt-4 pt-4 border-t-2 border-neutral-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div>
                <div className="text-sm text-neutral-600">Passed</div>
                <div className="text-lg font-bold text-green-700">
                  {evaluations.filter(e => e.passed).length} / {evaluations.length}
                </div>
              </div>
              <div>
                <div className="text-sm text-neutral-600">Avg Score</div>
                <div className="text-lg font-bold text-neutral-800">
                  {((evaluations.reduce((sum, e) => sum + e.score, 0) / evaluations.length) * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {totalEvaluationTokens > 0 && (
              <div className="flex items-center gap-6">
                <div>
                  <div className="text-sm text-neutral-600">Total Tokens</div>
                  <div className="text-lg font-bold text-neutral-800">
                    {totalEvaluationTokens.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-neutral-600">Total Cost</div>
                  <div className="text-lg font-bold text-neutral-800">
                    ${totalEvaluationCost.toFixed(4)}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EvaluationMetricsTable;
