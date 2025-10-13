import React from 'react';
import {
  Trophy,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Clock,
  Hash,
  AlertCircle,
  Sparkles,
  GitCompare,
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { ComparisonResponse, StageScores } from '../../types/insights';

interface Props {
  comparison: ComparisonResponse;
}

/**
 * Render markdown to HTML safely
 */
const renderMarkdown = (markdown: string): string => {
  const rawHtml = marked(markdown, {
    breaks: true,
    gfm: true,
  }) as string;
  return DOMPurify.sanitize(rawHtml);
};

/**
 * Comparison Results Component
 *
 * Displays blind comparison results with:
 * - Overall winner and reasoning (with tabular markdown)
 * - Per-stage winners with radar charts
 * - Score breakdowns by evaluation criteria
 * - Cost and performance metrics
 * - Judge model trace information
 */
export const ComparisonResults: React.FC<Props> = ({ comparison }) => {
  const getWinnerBadge = (winner: 'A' | 'B' | 'tie') => {
    if (winner === 'tie') {
      return (
        <div className="inline-flex items-center gap-1.5 bg-neutral-100 border-2 border-neutral-300 rounded-lg px-4 py-2">
          <GitCompare className="h-4 w-4 text-neutral-600" />
          <span className="font-bold text-neutral-700">Tie</span>
        </div>
      );
    }

    return (
      <div className="inline-flex items-center gap-1.5 bg-yellow-50 border-2 border-yellow-300 rounded-lg px-4 py-2">
        <Trophy className="h-4 w-4 text-yellow-600" />
        <span className="font-bold text-yellow-700">Model {winner}</span>
      </div>
    );
  };

  const getWinnerColor = (winner: 'A' | 'B' | 'tie') => {
    if (winner === 'A') return 'text-blue-700 bg-blue-50 border-blue-200';
    if (winner === 'B') return 'text-green-700 bg-green-50 border-green-200';
    return 'text-neutral-700 bg-neutral-50 border-neutral-200';
  };

  // Transform scores for radar chart
  const getRadarData = (scores: { A: StageScores; B: StageScores }) => {
    const criteria = comparison.evaluation_criteria;
    return criteria.map((criterion) => ({
      criterion: criterion.charAt(0).toUpperCase() + criterion.slice(1),
      'Model A': ((scores.A[criterion as keyof StageScores] ?? 0) * 100).toFixed(0),
      'Model B': ((scores.B[criterion as keyof StageScores] ?? 0) * 100).toFixed(0),
    }));
  };

  // Calculate cost difference
  const costDiff = comparison.analysis_b.total_cost - comparison.analysis_a.total_cost;
  const costDiffPercent =
    ((costDiff / comparison.analysis_a.total_cost) * 100).toFixed(1);

  // Calculate quality improvement (average score difference)
  const getAverageScore = (scores: StageScores) => {
    const values = Object.values(scores).filter((v) => v !== null && v !== undefined) as number[];
    return values.reduce((sum, v) => sum + v, 0) / values.length;
  };

  const getOverallAverageScore = (modelKey: 'A' | 'B') => {
    const stageScores = comparison.stage_results.map((stage) =>
      getAverageScore(stage.scores[modelKey])
    );
    return stageScores.reduce((sum, v) => sum + v, 0) / stageScores.length;
  };

  const avgScoreA = getOverallAverageScore('A');
  const avgScoreB = getOverallAverageScore('B');
  const qualityDiff = ((avgScoreB - avgScoreA) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Overall Winner Card */}
      <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-white p-3 rounded-xl border-2 border-yellow-300">
              <Trophy className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-neutral-800">Overall Winner</h2>
              <div className="flex items-center gap-2 mt-1">
                {getWinnerBadge(comparison.overall_winner)}
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-sm text-neutral-600 mb-1">Judge Model</div>
            <div className="flex items-center gap-1.5 text-[#FF385C]">
              <Sparkles className="h-4 w-4" />
              <span className="font-semibold">{comparison.judge_model}</span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur rounded-lg p-6 border border-yellow-200">
          <div
            className="prose prose-sm max-w-none text-neutral-700
                       prose-headings:text-neutral-800 prose-headings:font-bold prose-headings:mb-3 prose-headings:mt-4 first:prose-headings:mt-0
                       prose-h3:text-lg prose-h3:border-b-2 prose-h3:border-yellow-200 prose-h3:pb-2
                       prose-h4:text-base prose-h4:text-neutral-700
                       prose-table:border-collapse prose-table:w-full prose-table:my-4
                       prose-th:bg-neutral-100 prose-th:border prose-th:border-neutral-300 prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:font-semibold prose-th:text-neutral-800
                       prose-td:border prose-td:border-neutral-200 prose-td:px-4 prose-td:py-2
                       prose-tr:even:bg-neutral-50
                       prose-strong:text-neutral-900 prose-strong:font-bold
                       prose-ol:list-decimal prose-ol:ml-6 prose-ol:my-3
                       prose-ul:list-disc prose-ul:ml-6 prose-ul:my-2
                       prose-li:my-1.5 prose-li:pl-1
                       prose-code:bg-neutral-100 prose-code:text-[#FF385C] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono
                       prose-hr:border-neutral-300 prose-hr:my-4
                       prose-p:my-2 prose-p:leading-relaxed"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(comparison.overall_reasoning) }}
          />
        </div>

        {/* Cost vs Quality Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-yellow-200">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-neutral-600" />
              <span className="text-sm font-semibold text-neutral-700">Cost Difference</span>
            </div>
            <div className="flex items-baseline gap-2">
              {costDiff > 0 ? (
                <TrendingUp className="h-5 w-5 text-red-600 flex-shrink-0" />
              ) : (
                <TrendingDown className="h-5 w-5 text-green-600 flex-shrink-0" />
              )}
              <span
                className={`text-2xl font-bold ${
                  costDiff > 0 ? 'text-red-600' : 'text-green-600'
                }`}
              >
                {costDiff > 0 ? '+' : ''}${costDiff.toFixed(4)}
              </span>
              <span className={`text-sm ${costDiff > 0 ? 'text-red-600' : 'text-green-600'}`}>
                ({costDiff > 0 ? '+' : ''}{costDiffPercent}%)
              </span>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-yellow-200">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-neutral-600" />
              <span className="text-sm font-semibold text-neutral-700">Quality Difference</span>
            </div>
            <div className="flex items-baseline gap-2">
              {parseFloat(qualityDiff) > 0 ? (
                <TrendingUp className="h-5 w-5 text-green-600 flex-shrink-0" />
              ) : (
                <TrendingDown className="h-5 w-5 text-red-600 flex-shrink-0" />
              )}
              <span
                className={`text-2xl font-bold ${
                  parseFloat(qualityDiff) > 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {parseFloat(qualityDiff) > 0 ? '+' : ''}
                {qualityDiff}%
              </span>
              <span className="text-sm text-neutral-500">avg score</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stage-by-Stage Results */}
      <div className="bg-white border border-neutral-200 rounded-xl p-6">
        <h3 className="text-lg font-bold text-neutral-800 mb-6">Stage-by-Stage Analysis</h3>

        <div className="space-y-8">
          {comparison.stage_results.map((stage, index) => {
            const radarData = getRadarData(stage.scores);

            return (
              <div key={index} className="pb-8 border-b-2 border-neutral-200 last:border-b-0">
                {/* Stage Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-bold text-neutral-800">{stage.stage}</h4>
                  </div>
                  {getWinnerBadge(stage.winner)}
                </div>

                {/* Radar Chart */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#e5e7eb" />
                        <PolarAngleAxis
                          dataKey="criterion"
                          tick={{ fill: '#6b7280', fontSize: 12 }}
                        />
                        <PolarRadiusAxis
                          angle={90}
                          domain={[0, 100]}
                          tick={{ fill: '#6b7280', fontSize: 10 }}
                        />
                        <Radar
                          name="Model A"
                          dataKey="Model A"
                          stroke="#3b82f6"
                          fill="#3b82f6"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                        <Radar
                          name="Model B"
                          dataKey="Model B"
                          stroke="#10b981"
                          fill="#10b981"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                        <Legend
                          wrapperStyle={{ paddingTop: '20px' }}
                          iconType="circle"
                          iconSize={12}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '2px solid #e5e7eb',
                            borderRadius: '8px',
                          }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Score Table */}
                  <div>
                    <table className="w-full">
                      <thead>
                        <tr className="border-b-2 border-neutral-200">
                          <th className="text-left py-2 px-3 text-sm font-semibold text-neutral-700">
                            Criterion
                          </th>
                          <th className="text-center py-2 px-3 text-sm font-semibold text-blue-700">
                            Model A
                          </th>
                          <th className="text-center py-2 px-3 text-sm font-semibold text-green-700">
                            Model B
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-200">
                        {comparison.evaluation_criteria.map((criterion) => {
                          const scoreA = stage.scores.A[criterion as keyof StageScores];
                          const scoreB = stage.scores.B[criterion as keyof StageScores];

                          return (
                            <tr key={criterion}>
                              <td className="py-3 px-3 text-sm text-neutral-700 capitalize">
                                {criterion}
                              </td>
                              <td className="py-3 px-3 text-center">
                                <span className="inline-block bg-blue-50 border border-blue-200 rounded px-2 py-1 text-sm font-semibold text-blue-700">
                                  {scoreA != null ? (scoreA * 100).toFixed(0) : '-'}%
                                </span>
                              </td>
                              <td className="py-3 px-3 text-center">
                                <span className="inline-block bg-green-50 border border-green-200 rounded px-2 py-1 text-sm font-semibold text-green-700">
                                  {scoreB != null ? (scoreB * 100).toFixed(0) : '-'}%
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>

                    {/* Stage Reasoning */}
                    <div className="mt-4 bg-neutral-50 rounded-lg p-4 border border-neutral-200">
                      <div className="text-xs font-semibold text-neutral-600 mb-2">
                        Judge Reasoning
                      </div>
                      <div
                        className="prose prose-sm max-w-none text-neutral-700
                                   prose-headings:text-sm prose-headings:text-neutral-800 prose-headings:font-bold prose-headings:mt-2 prose-headings:mb-1
                                   prose-p:text-sm prose-p:my-1
                                   prose-ul:my-1 prose-ul:text-sm
                                   prose-li:my-0.5
                                   prose-strong:text-neutral-900 prose-strong:font-semibold"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(stage.reasoning) }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analysis Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model A Info */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
          <h4 className="font-bold text-blue-900 mb-4">Model A (Baseline)</h4>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-blue-700 font-semibold">Title</div>
              <div className="text-neutral-800">
                {comparison.analysis_a.transcript_title || 'Untitled'}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-blue-700 font-semibold mb-1">Tokens</div>
                <div className="flex items-center gap-1 text-neutral-800">
                  <Hash className="h-4 w-4" />
                  {comparison.analysis_a.total_tokens.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-blue-700 font-semibold mb-1">Cost</div>
                <div className="flex items-center gap-1 text-neutral-800">
                  <DollarSign className="h-4 w-4" />
                  {comparison.analysis_a.total_cost.toFixed(4)}
                </div>
              </div>
            </div>
            <div>
              <div className="text-sm text-blue-700 font-semibold">Models & Configuration</div>
              <div className="text-xs text-neutral-600 mt-1 space-y-0.5">
                <div>Stage 1: {comparison.analysis_a.model_stage1}</div>
                <div>Stage 2: {comparison.analysis_a.model_stage2}</div>
                <div>Stage 3: {comparison.analysis_a.model_stage3}</div>
                <div className="text-neutral-500 italic mt-1">
                  Temperature settings shown in comparison analysis
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Model B Info */}
        <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6">
          <h4 className="font-bold text-green-900 mb-4">Model B (Comparison)</h4>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-green-700 font-semibold">Title</div>
              <div className="text-neutral-800">
                {comparison.analysis_b.transcript_title || 'Untitled'}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-green-700 font-semibold mb-1">Tokens</div>
                <div className="flex items-center gap-1 text-neutral-800">
                  <Hash className="h-4 w-4" />
                  {comparison.analysis_b.total_tokens.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-sm text-green-700 font-semibold mb-1">Cost</div>
                <div className="flex items-center gap-1 text-neutral-800">
                  <DollarSign className="h-4 w-4" />
                  {comparison.analysis_b.total_cost.toFixed(4)}
                </div>
              </div>
            </div>
            <div>
              <div className="text-sm text-green-700 font-semibold">Models & Configuration</div>
              <div className="text-xs text-neutral-600 mt-1 space-y-0.5">
                <div>Stage 1: {comparison.analysis_b.model_stage1}</div>
                <div>Stage 2: {comparison.analysis_b.model_stage2}</div>
                <div>Stage 3: {comparison.analysis_b.model_stage3}</div>
                <div className="text-neutral-500 italic mt-1">
                  Temperature settings shown in comparison analysis
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Judge Trace Info */}
      <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="h-5 w-5 text-neutral-600" />
          <h4 className="font-bold text-neutral-800">Judge Model Trace</h4>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-neutral-600 font-semibold mb-1">Model</div>
            <div className="text-neutral-800">{comparison.judge_trace.model}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600 font-semibold mb-1">Tokens</div>
            <div className="flex items-center gap-1 text-neutral-800">
              <Hash className="h-4 w-4" />
              {comparison.judge_trace.total_tokens.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-neutral-600 font-semibold mb-1">Cost</div>
            <div className="flex items-center gap-1 text-neutral-800">
              <DollarSign className="h-4 w-4" />
              {comparison.judge_trace.cost.toFixed(4)}
            </div>
          </div>
          <div>
            <div className="text-sm text-neutral-600 font-semibold mb-1">Duration</div>
            <div className="flex items-center gap-1 text-neutral-800">
              <Clock className="h-4 w-4" />
              {(comparison.judge_trace.duration_ms / 1000).toFixed(2)}s
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonResults;
