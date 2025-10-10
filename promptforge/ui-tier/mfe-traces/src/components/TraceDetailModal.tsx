import React, { useState, useEffect } from 'react';
import { X, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import StatusIndicator from './StatusIndicator';
import EvaluationResultsTable from './EvaluationResultsTable';
import { traceService, TraceDetail } from '../../../shared/services/traceService';

interface TraceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  traceId: string;
}

export const TraceDetailModal: React.FC<TraceDetailModalProps> = ({
  isOpen,
  onClose,
  traceId,
}) => {
  const [trace, setTrace] = useState<TraceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  // Section expansion state
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    prompt: false,
    response: false,
    evaluations: true,
    stages: true,
    spans: false,
    metadata: false,
  });

  useEffect(() => {
    if (isOpen && traceId) {
      fetchTraceDetail();
    }
  }, [isOpen, traceId]);

  const fetchTraceDetail = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await traceService.getTraceDetail(traceId);
      setTrace(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load trace details');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="flex min-h-full items-start justify-center p-4 pt-10">
        <div className="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl max-h-[90vh] flex flex-col">
          {/* Fixed Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-gray-200 bg-white rounded-t-2xl sticky top-0 z-10">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">Trace Details</h2>
              {trace && (
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-sm font-mono text-gray-700">{trace.trace_id}</span>
                  <StatusIndicator status={trace.status as any} />
                  <span className="text-sm text-gray-600">{trace.model_name || 'Unknown Model'}</span>
                </div>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-all duration-200 rounded-xl p-2 hover:bg-gray-100"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-6 py-6">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-gray-600">Loading trace details...</div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
              </div>
            )}

            {trace && (
              <div className="space-y-6">
                {/* Overview Section - Always Expanded */}
                <Section
                  title="Overview"
                  isExpanded={expandedSections.overview}
                  onToggle={() => toggleSection('overview')}
                >
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-8 divide-y lg:divide-y-0 divide-gray-100">
                    <div className="space-y-1">
                      <InfoItem label="Project" value={trace.project_name} />
                      <InfoItem label="Environment" value={trace.environment || 'N/A'} />
                      <InfoItem label="Model" value={trace.model_name || 'N/A'} />
                      <InfoItem label="Provider" value={trace.provider || 'N/A'} />
                      <InfoItem label="User" value={trace.user_email || 'N/A'} />
                    </div>
                    <div className="space-y-1 pt-4 lg:pt-0">
                      <InfoItem label="Duration" value={`${trace.total_duration_ms?.toFixed(0) || 0}ms`} />
                      <InfoItem label="Input Tokens" value={trace.input_tokens?.toLocaleString() || '0'} />
                      <InfoItem label="Output Tokens" value={trace.output_tokens?.toLocaleString() || '0'} />
                      <InfoItem label="Total Cost" value={`$${trace.total_cost?.toFixed(4) || '0.0000'}`} />
                      <InfoItem label="Retries" value={trace.retry_count?.toString() || '0'} />
                      <InfoItem label="Timestamp" value={new Date(trace.created_at).toLocaleString()} />
                    </div>
                  </div>
                  {trace.error_message && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm font-medium text-red-900">Error: {trace.error_type}</p>
                      <p className="text-sm text-red-700 mt-1">{trace.error_message}</p>
                    </div>
                  )}
                </Section>

                {/* Prompt & Context Section */}
                <Section
                  title="Prompt & Context"
                  isExpanded={expandedSections.prompt}
                  onToggle={() => toggleSection('prompt')}
                >
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">Input Data</label>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(trace.input_data, null, 2), 'input')}
                          className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1"
                        >
                          {copiedField === 'input' ? (
                            <>
                              <Check className="h-3 w-3" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3" /> Copy
                            </>
                          )}
                        </button>
                      </div>
                      <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs overflow-x-auto max-h-64 overflow-y-auto">
                        {JSON.stringify(trace.input_data, null, 2)}
                      </pre>
                    </div>
                  </div>
                </Section>

                {/* Response Section */}
                <Section
                  title="Response Data"
                  isExpanded={expandedSections.response}
                  onToggle={() => toggleSection('response')}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">Output Data</label>
                      <button
                        onClick={() => copyToClipboard(JSON.stringify(trace.output_data, null, 2), 'output')}
                        className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1"
                      >
                        {copiedField === 'output' ? (
                          <>
                            <Check className="h-3 w-3" /> Copied
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" /> Copy
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs overflow-x-auto max-h-64 overflow-y-auto">
                      {JSON.stringify(trace.output_data, null, 2)}
                    </pre>
                  </div>
                </Section>

                {/* Evaluations Section - Expanded by Default */}
                <Section
                  title={`Evaluations (${trace.evaluations?.length || 0})`}
                  isExpanded={expandedSections.evaluations}
                  onToggle={() => toggleSection('evaluations')}
                >
                  {trace.evaluations && trace.evaluations.length > 0 ? (
                    <EvaluationResultsTable evaluations={trace.evaluations} />
                  ) : (
                    <p className="text-sm text-gray-600">No evaluations run for this trace.</p>
                  )}
                </Section>

                {/* Stages Section - Show child traces for multi-stage workflows */}
                {trace.children && trace.children.length > 0 && (
                  <Section
                    title={`Stages (${trace.children.length})`}
                    isExpanded={expandedSections.stages}
                    onToggle={() => toggleSection('stages')}
                  >
                    <div className="space-y-4">
                      {trace.children.map((child, index) => (
                        <div key={child.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          {/* Stage Header */}
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono bg-gray-200 text-gray-700 px-2 py-1 rounded">
                                Stage {index + 1}
                              </span>
                              {child.stage && (
                                <span className="text-sm font-medium text-gray-900">{child.stage}</span>
                              )}
                              <StatusIndicator status={child.status as any} />
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              {child.model_name && <span>{child.model_name}</span>}
                              {child.total_duration_ms != null && (
                                <span>{Math.round(child.total_duration_ms)}ms</span>
                              )}
                            </div>
                          </div>

                          {/* Metrics */}
                          <div className="grid grid-cols-3 gap-4 mb-3 text-xs">
                            <div>
                              <span className="text-gray-600">Tokens:</span>{' '}
                              <span className="font-medium text-gray-900">
                                {child.total_tokens?.toLocaleString() || '0'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Cost:</span>{' '}
                              <span className="font-medium text-gray-900">
                                ${child.total_cost?.toFixed(4) || '0.0000'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Time:</span>{' '}
                              <span className="font-medium text-gray-900">
                                {new Date(child.created_at).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>

                          {/* System Prompt */}
                          {child.input_data?.system_prompt && (
                            <div className="mb-3">
                              <div className="flex items-center justify-between mb-1">
                                <label className="text-xs font-medium text-gray-700">System Prompt</label>
                                <button
                                  onClick={() => copyToClipboard(child.input_data.system_prompt, `child-system-${child.id}`)}
                                  className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1"
                                >
                                  {copiedField === `child-system-${child.id}` ? (
                                    <>
                                      <Check className="h-3 w-3" /> Copied
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="h-3 w-3" /> Copy
                                    </>
                                  )}
                                </button>
                              </div>
                              <pre className="bg-white border border-gray-300 rounded p-3 text-xs overflow-x-auto max-h-40 overflow-y-auto">
                                {child.input_data.system_prompt}
                              </pre>
                            </div>
                          )}

                          {/* Input Prompt */}
                          {child.input_data?.prompt && (
                            <div className="mb-3">
                              <label className="text-xs font-medium text-gray-700 mb-1 block">Input</label>
                              <pre className="bg-white border border-gray-300 rounded p-3 text-xs overflow-x-auto max-h-32 overflow-y-auto">
                                {child.input_data.prompt}
                              </pre>
                            </div>
                          )}

                          {/* Output Response */}
                          {child.output_data?.response && (
                            <div>
                              <label className="text-xs font-medium text-gray-700 mb-1 block">Output</label>
                              <pre className="bg-white border border-gray-300 rounded p-3 text-xs overflow-x-auto max-h-32 overflow-y-auto">
                                {child.output_data.response}
                              </pre>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </Section>
                )}

                {/* Spans Section */}
                {trace.spans && trace.spans.length > 0 && (
                  <Section
                    title={`Spans (${trace.spans.length})`}
                    isExpanded={expandedSections.spans}
                    onToggle={() => toggleSection('spans')}
                  >
                    <div className="space-y-3">
                      {trace.spans.map((span, index) => (
                        <div key={span.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono text-gray-500">#{index + 1}</span>
                              <span className="text-sm font-medium text-gray-900">{span.name}</span>
                              <StatusIndicator status={span.status as any} />
                            </div>
                            <span className="text-sm text-gray-600">{span.duration_ms?.toFixed(0) || 0}ms</span>
                          </div>
                          {span.prompt_tokens && (
                            <div className="text-xs text-gray-600 mt-1">
                              Tokens: {span.prompt_tokens} in / {span.completion_tokens} out
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </Section>
                )}

                {/* System Metadata */}
                <Section
                  title="System Metadata"
                  isExpanded={expandedSections.metadata}
                  onToggle={() => toggleSection('metadata')}
                >
                  <div>
                    <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs overflow-x-auto max-h-64 overflow-y-auto">
                      {JSON.stringify(trace.trace_metadata || {}, null, 2)}
                    </pre>
                  </div>
                </Section>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Collapsible Section Component
interface SectionProps {
  title: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, isExpanded, onToggle, children }) => {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
        aria-expanded={isExpanded}
      >
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        {isExpanded ? (
          <ChevronDown className="h-4 w-4 text-gray-600" />
        ) : (
          <ChevronRight className="h-4 w-4 text-gray-600" />
        )}
      </button>
      {isExpanded && <div className="p-4 bg-white">{children}</div>}
    </div>
  );
};

// Info Item Component with horizontal label-value layout
interface InfoItemProps {
  label: string;
  value: string;
}

const InfoItem: React.FC<InfoItemProps> = ({ label, value }) => {
  return (
    <div className="flex items-baseline gap-3 py-2">
      <dt className="text-sm font-medium text-gray-600 min-w-[120px] flex-shrink-0">
        {label}:
      </dt>
      <dd className="text-sm text-gray-900 font-normal break-words flex-1">
        {value}
      </dd>
    </div>
  );
};

export default TraceDetailModal;
