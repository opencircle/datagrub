import React, { useState, useMemo } from 'react';
import { ChevronDown, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

interface LLMMetadata {
  provider?: string;
  provider_model?: string;
  token_usage?: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
    cache_read_tokens?: number;
    cache_creation_tokens?: number;
  };
  cost_metrics?: {
    input_cost?: number;
    output_cost?: number;
    cache_read_cost?: number;
    cache_write_cost?: number;
    total_cost?: number;
  };
  performance_metrics?: {
    total_duration_ms?: number;
    time_to_first_token_ms?: number;
    tokens_per_second?: number;
  };
  request_parameters?: {
    temperature?: number;
    top_p?: number;
    max_tokens?: number;
  };
  response_metadata?: {
    finish_reason?: string;
    request_id?: string;
  };
  [key: string]: any;
}

interface Evaluation {
  id: string;
  evaluation_name: string;
  evaluation_source: string;
  evaluation_type: string;
  category: string;
  vendor_name?: string | null;
  score?: number;
  passed?: boolean;
  category_result?: string;
  reason?: string;
  execution_time_ms?: number;
  status: string;
  // LLM Cost Tracking
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  evaluation_cost?: number;
  // Comprehensive LLM metadata
  llm_metadata?: LLMMetadata | null;
  // Vendor-specific metrics
  vendor_metrics?: Record<string, any>;
  // Additional details
  details?: Record<string, any>;
  suggestions?: string[];
  model_used?: string;
}

interface EvaluationResultsTableProps {
  evaluations: Evaluation[];
}

type SortColumn = 'name' | 'category' | 'type' | 'score' | 'result' | 'executionTime' | 'cost' | 'tokens';
type SortDirection = 'asc' | 'desc';

const EvaluationResultsTable: React.FC<EvaluationResultsTableProps> = ({ evaluations }) => {
  const [sortColumn, setSortColumn] = useState<SortColumn>('category');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRow = (evaluationId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(evaluationId)) {
      newExpanded.delete(evaluationId);
    } else {
      newExpanded.add(evaluationId);
    }
    setExpandedRows(newExpanded);
  };

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const sortedEvaluations = useMemo(() => {
    const sorted = [...evaluations];

    sorted.sort((a, b) => {
      let comparison = 0;

      switch (sortColumn) {
        case 'name':
          comparison = a.evaluation_name.localeCompare(b.evaluation_name);
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
        case 'type':
          comparison = a.evaluation_type.localeCompare(b.evaluation_type);
          break;
        case 'score':
          comparison = (a.score || 0) - (b.score || 0);
          break;
        case 'result':
          const aResult = a.passed !== undefined ? (a.passed ? 1 : 0) : -1;
          const bResult = b.passed !== undefined ? (b.passed ? 1 : 0) : -1;
          comparison = aResult - bResult;
          break;
        case 'executionTime':
          comparison = (a.execution_time_ms || 0) - (b.execution_time_ms || 0);
          break;
        case 'cost':
          comparison = (a.evaluation_cost || 0) - (b.evaluation_cost || 0);
          break;
        case 'tokens':
          comparison = (a.total_tokens || 0) - (b.total_tokens || 0);
          break;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [evaluations, sortColumn, sortDirection]);

  const SortButton: React.FC<{
    column: SortColumn;
    children: React.ReactNode;
    align?: 'left' | 'right';
  }> = ({ column, children, align = 'left' }) => (
    <button
      onClick={() => handleSort(column)}
      className={`flex items-center gap-1 hover:text-gray-900 transition-colors ${
        align === 'right' ? 'ml-auto' : ''
      }`}
      aria-label={`Sort by ${column}`}
    >
      {children}
      <ChevronDown
        className={`h-3 w-3 transition-transform ${
          sortColumn === column && sortDirection === 'asc' ? 'rotate-180' : ''
        }`}
      />
    </button>
  );

  const getResultBadge = (evaluation: Evaluation) => {
    if (evaluation.status === 'failed') {
      return (
        <span className="inline-flex items-center gap-1 text-sm text-red-700">
          <XCircle className="h-4 w-4" />
          <span>Failed</span>
        </span>
      );
    }

    // For validators
    if (evaluation.evaluation_type === 'validator') {
      if (evaluation.passed === true) {
        return (
          <span className="inline-flex items-center gap-1 text-sm text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            <span>Pass</span>
          </span>
        );
      } else if (evaluation.passed === false) {
        return (
          <span className="inline-flex items-center gap-1 text-sm text-red-700">
            <XCircle className="h-4 w-4" />
            <span>Fail</span>
          </span>
        );
      }
    }

    // For metrics with score
    if (evaluation.evaluation_type === 'metric' && evaluation.score !== undefined) {
      const scorePercent = (evaluation.score * 100).toFixed(0);
      const color = evaluation.score >= 0.8 ? 'text-green-700' : evaluation.score >= 0.6 ? 'text-amber-700' : 'text-red-700';
      return (
        <span className={`text-sm font-medium ${color}`}>
          {scorePercent}%
        </span>
      );
    }

    // For classifiers
    if (evaluation.evaluation_type === 'classifier' && evaluation.category_result) {
      return (
        <span className="text-sm text-gray-700">
          {evaluation.category_result}
        </span>
      );
    }

    return (
      <span className="text-sm text-gray-500">
        N/A
      </span>
    );
  };

  const getSourceBadge = (source: string) => {
    const colors: Record<string, string> = {
      vendor: 'bg-blue-100 text-blue-700',
      custom: 'bg-purple-100 text-purple-700',
      promptforge: 'bg-green-100 text-green-700',
      llm_judge: 'bg-amber-100 text-amber-700',
    };

    return (
      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${colors[source] || 'bg-gray-100 text-gray-700'}`}>
        {source.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  if (evaluations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-600">
        No evaluations available
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="name">Name</SortButton>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="category">Category</SortButton>
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wide">
              Source
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="score" align="right">Score</SortButton>
            </th>
            <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wide">
              Result
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="tokens" align="right">Tokens</SortButton>
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="cost" align="right">Cost</SortButton>
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wide">
              <SortButton column="executionTime" align="right">Time</SortButton>
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedEvaluations.map((evaluation, index) => (
            <React.Fragment key={evaluation.id}>
              <tr
                className={`border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${
                  index === sortedEvaluations.length - 1 ? 'last:border-b-0' : ''
                }`}
                onClick={() => toggleRow(evaluation.id)}
              >
                <td className="px-4 py-3 text-sm text-gray-900">
                  <div className="flex items-center gap-2">
                    <span>{evaluation.evaluation_name}</span>
                    {evaluation.vendor_name && (
                      <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-700">
                        {evaluation.vendor_name}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 capitalize">
                  {evaluation.category}
                </td>
                <td className="px-4 py-3">
                  {getSourceBadge(evaluation.evaluation_source)}
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-700 tabular-nums">
                  {evaluation.score !== undefined && evaluation.score !== null ?
                    (evaluation.score * 100).toFixed(1) + '%' : '-'}
                </td>
                <td className="px-4 py-3 text-center">
                  {evaluation.passed !== undefined && evaluation.passed !== null ? (
                    evaluation.passed ? (
                      <CheckCircle2 className="h-4 w-4 text-green-700 inline" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-700 inline" />
                    )
                  ) : '-'}
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-700 tabular-nums">
                  {evaluation.total_tokens ? evaluation.total_tokens.toLocaleString() : '-'}
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-700 tabular-nums">
                  {evaluation.evaluation_cost ? `$${evaluation.evaluation_cost.toFixed(4)}` : '-'}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 text-right tabular-nums">
                  {evaluation.execution_time_ms ? `${evaluation.execution_time_ms.toFixed(0)}ms` : '-'}
                </td>
              </tr>
              {expandedRows.has(evaluation.id) && (
                <tr className="bg-gray-50">
                  <td colSpan={8} className="px-4 py-4">
                    <div className="space-y-3 text-sm">
                      {/* Reason */}
                      {evaluation.reason && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Reason</div>
                          <div className="text-gray-700">{evaluation.reason}</div>
                        </div>
                      )}

                      {/* Token Breakdown */}
                      {(evaluation.input_tokens || evaluation.output_tokens) && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Token Usage</div>
                          <div className="grid grid-cols-3 gap-2 text-gray-700">
                            <div>Input: {evaluation.input_tokens?.toLocaleString() || 0}</div>
                            <div>Output: {evaluation.output_tokens?.toLocaleString() || 0}</div>
                            <div>Total: {evaluation.total_tokens?.toLocaleString() || 0}</div>
                          </div>
                        </div>
                      )}

                      {/* Model Used */}
                      {evaluation.model_used && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Model</div>
                          <div className="text-gray-700">{evaluation.model_used}</div>
                        </div>
                      )}

                      {/* LLM Metadata - Comprehensive Metrics */}
                      {evaluation.llm_metadata && (
                        <div>
                          <div className="font-medium text-gray-900 mb-2">LLM Performance Metrics</div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Provider & Model */}
                            {evaluation.llm_metadata.provider && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Provider & Model</div>
                                <div className="text-sm text-gray-900">
                                  {evaluation.llm_metadata.provider}
                                  {evaluation.llm_metadata.provider_model && (
                                    <span className="text-gray-600"> / {evaluation.llm_metadata.provider_model}</span>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Token Usage (enhanced with cache metrics) */}
                            {evaluation.llm_metadata.token_usage && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Token Usage</div>
                                <div className="text-sm text-gray-900 space-y-1">
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Input:</span>
                                    <span className="font-mono">{evaluation.llm_metadata.token_usage.input_tokens?.toLocaleString() || 0}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Output:</span>
                                    <span className="font-mono">{evaluation.llm_metadata.token_usage.output_tokens?.toLocaleString() || 0}</span>
                                  </div>
                                  {evaluation.llm_metadata.token_usage.cache_read_tokens !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Cache Read:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.token_usage.cache_read_tokens?.toLocaleString() || 0}</span>
                                    </div>
                                  )}
                                  <div className="flex justify-between font-medium border-t border-gray-200 pt-1 mt-1">
                                    <span className="text-gray-900">Total:</span>
                                    <span className="font-mono">{evaluation.llm_metadata.token_usage.total_tokens?.toLocaleString() || 0}</span>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Cost Metrics */}
                            {evaluation.llm_metadata.cost_metrics && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Cost Breakdown</div>
                                <div className="text-sm text-gray-900 space-y-1">
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Input:</span>
                                    <span className="font-mono">${evaluation.llm_metadata.cost_metrics.input_cost?.toFixed(6) || '0.000000'}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Output:</span>
                                    <span className="font-mono">${evaluation.llm_metadata.cost_metrics.output_cost?.toFixed(6) || '0.000000'}</span>
                                  </div>
                                  {evaluation.llm_metadata.cost_metrics.cache_read_cost !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Cache Read:</span>
                                      <span className="font-mono">${evaluation.llm_metadata.cost_metrics.cache_read_cost?.toFixed(6) || '0.000000'}</span>
                                    </div>
                                  )}
                                  <div className="flex justify-between font-medium border-t border-gray-200 pt-1 mt-1">
                                    <span className="text-gray-900">Total:</span>
                                    <span className="font-mono">${evaluation.llm_metadata.cost_metrics.total_cost?.toFixed(6) || '0.000000'}</span>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Performance Metrics */}
                            {evaluation.llm_metadata.performance_metrics && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Performance</div>
                                <div className="text-sm text-gray-900 space-y-1">
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Duration:</span>
                                    <span className="font-mono">{evaluation.llm_metadata.performance_metrics.total_duration_ms?.toFixed(0) || 0}ms</span>
                                  </div>
                                  {evaluation.llm_metadata.performance_metrics.time_to_first_token_ms !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">TTFT:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.performance_metrics.time_to_first_token_ms?.toFixed(0) || 0}ms</span>
                                    </div>
                                  )}
                                  {evaluation.llm_metadata.performance_metrics.tokens_per_second !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Throughput:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.performance_metrics.tokens_per_second?.toFixed(1) || 0} tok/s</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Request Parameters */}
                            {evaluation.llm_metadata.request_parameters && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Request Parameters</div>
                                <div className="text-sm text-gray-900 space-y-1">
                                  {evaluation.llm_metadata.request_parameters.temperature !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Temperature:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.request_parameters.temperature}</span>
                                    </div>
                                  )}
                                  {evaluation.llm_metadata.request_parameters.top_p !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Top P:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.request_parameters.top_p}</span>
                                    </div>
                                  )}
                                  {evaluation.llm_metadata.request_parameters.max_tokens !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Max Tokens:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.request_parameters.max_tokens}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Response Metadata */}
                            {evaluation.llm_metadata.response_metadata && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="text-xs text-gray-600 mb-1">Response Info</div>
                                <div className="text-sm text-gray-900 space-y-1">
                                  {evaluation.llm_metadata.response_metadata.finish_reason && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Finish:</span>
                                      <span className="font-mono">{evaluation.llm_metadata.response_metadata.finish_reason}</span>
                                    </div>
                                  )}
                                  {evaluation.llm_metadata.response_metadata.request_id && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Request ID:</span>
                                      <span className="font-mono text-xs truncate max-w-[150px]" title={evaluation.llm_metadata.response_metadata.request_id}>
                                        {evaluation.llm_metadata.response_metadata.request_id}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Vendor Metrics */}
                      {evaluation.vendor_metrics && Object.keys(evaluation.vendor_metrics).length > 0 && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Vendor Metrics</div>
                          <pre className="text-xs bg-white border border-gray-200 rounded p-2 overflow-x-auto">
                            {JSON.stringify(evaluation.vendor_metrics, null, 2)}
                          </pre>
                        </div>
                      )}

                      {/* Details */}
                      {evaluation.details && Object.keys(evaluation.details).length > 0 && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Details</div>
                          <pre className="text-xs bg-white border border-gray-200 rounded p-2 overflow-x-auto">
                            {JSON.stringify(evaluation.details, null, 2)}
                          </pre>
                        </div>
                      )}

                      {/* Suggestions */}
                      {evaluation.suggestions && evaluation.suggestions.length > 0 && (
                        <div>
                          <div className="font-medium text-gray-900 mb-1">Suggestions</div>
                          <ul className="list-disc list-inside text-gray-700 space-y-1">
                            {evaluation.suggestions.map((suggestion, idx) => (
                              <li key={idx}>{suggestion}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EvaluationResultsTable;
