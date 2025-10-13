import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
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

  const modalContent = (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        overflowY: 'auto'
      }}
    >
        {/* Backdrop */}
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(8px)'
          }}
          onClick={onClose}
          aria-hidden="true"
        />

      {/* Modal */}
      <div style={{
        display: 'flex',
        minHeight: '100%',
        alignItems: 'flex-start',
        justifyContent: 'center',
        padding: '3rem 1rem 2rem 1rem'
      }}>
        <div style={{
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
        }}>
          {/* Fixed Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 bg-white rounded-t-2xl sticky top-0 z-10" style={{ padding: '2rem 3rem' }}>
            <div>
              <h2 className="text-2xl font-semibold text-neutral-900">Trace Details</h2>
              {trace && (
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-sm font-mono text-neutral-700">{trace.trace_id}</span>
                  <StatusIndicator status={trace.status as any} />
                  <span className="text-sm text-neutral-600">{trace.model_name || 'Unknown Model'}</span>
                </div>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-neutral-500 hover:text-neutral-700 transition-all duration-200 rounded-xl p-2.5 hover:bg-neutral-100"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto" style={{ padding: '3rem' }}>
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-neutral-600">Loading trace details...</div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
                {error}
              </div>
            )}

            {trace && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {/* Overview Section - Always Expanded */}
                <Section
                  title="Overview"
                  isExpanded={expandedSections.overview}
                  onToggle={() => toggleSection('overview')}
                >
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '3rem 4rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <InfoItem label="Project" value={trace.project_name} />
                      <InfoItem label="Environment" value={trace.environment || 'N/A'} />
                      <InfoItem label="Model" value={trace.model_name || 'N/A'} />
                      <InfoItem label="Provider" value={trace.provider || 'N/A'} />
                      <InfoItem label="User" value={trace.user_email || 'N/A'} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <InfoItem label="Duration" value={`${trace.total_duration_ms?.toFixed(0) || 0}ms`} />
                      <InfoItem label="Input Tokens" value={trace.input_tokens?.toLocaleString() || '0'} />
                      <InfoItem label="Output Tokens" value={trace.output_tokens?.toLocaleString() || '0'} />
                      <InfoItem label="Total Cost" value={`$${trace.total_cost?.toFixed(4) || '0.0000'}`} />
                      <InfoItem label="Retries" value={trace.retry_count?.toString() || '0'} />
                      <InfoItem label="Timestamp" value={new Date(trace.created_at).toLocaleString()} />
                    </div>
                  </div>
                  {trace.error_message && (
                    <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
                      <p className="text-sm font-medium text-red-900">Error: {trace.error_type}</p>
                      <p className="text-sm text-red-700 mt-2">{trace.error_message}</p>
                    </div>
                  )}
                </Section>

                {/* Prompt & Context Section */}
                <Section
                  title="Prompt & Context"
                  isExpanded={expandedSections.prompt}
                  onToggle={() => toggleSection('prompt')}
                >
                  <div className="space-y-6">
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <label className="text-sm font-medium text-neutral-700">Input Data</label>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(trace.input_data, null, 2), 'input')}
                          className="text-xs text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all duration-200"
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
                      <pre className="bg-neutral-50 border border-neutral-200 rounded-xl p-6 text-xs font-mono overflow-x-auto max-h-64 overflow-y-auto">
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
                    <div className="flex items-center justify-between mb-4">
                      <label className="text-sm font-medium text-neutral-700">Output Data</label>
                      <button
                        onClick={() => copyToClipboard(JSON.stringify(trace.output_data, null, 2), 'output')}
                        className="text-xs text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all duration-200"
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
                    <pre className="bg-neutral-50 border border-neutral-200 rounded-xl p-6 text-xs font-mono overflow-x-auto max-h-64 overflow-y-auto">
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
                    <p className="text-sm text-neutral-600">No evaluations run for this trace.</p>
                  )}
                </Section>

                {/* Stages Section - Show child traces for multi-stage workflows */}
                {trace.children && trace.children.length > 0 && (
                  <Section
                    title={`Stages (${trace.children.length})`}
                    isExpanded={expandedSections.stages}
                    onToggle={() => toggleSection('stages')}
                  >
                    <div className="space-y-6">
                      {trace.children.map((child, index) => (
                        <div key={child.id} className="border border-neutral-200 rounded-xl p-8 bg-neutral-50">
                          {/* Stage Header */}
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono bg-neutral-200 text-neutral-700 px-2.5 py-1 rounded-lg">
                                Stage {index + 1}
                              </span>
                              {child.stage && (
                                <span className="text-sm font-medium text-neutral-900">{child.stage}</span>
                              )}
                              <StatusIndicator status={child.status as any} />
                            </div>
                            <div className="flex items-center gap-4 text-sm text-neutral-600">
                              {child.model_name && <span>{child.model_name}</span>}
                              {child.total_duration_ms != null && (
                                <span>{Math.round(child.total_duration_ms)}ms</span>
                              )}
                            </div>
                          </div>

                          {/* Metrics */}
                          <div className="grid grid-cols-3 gap-8 mb-6 text-xs">
                            <div>
                              <span className="text-neutral-600">Tokens:</span>{' '}
                              <span className="font-medium text-neutral-900">
                                {child.total_tokens?.toLocaleString() || '0'}
                              </span>
                            </div>
                            <div>
                              <span className="text-neutral-600">Cost:</span>{' '}
                              <span className="font-medium text-neutral-900">
                                ${child.total_cost?.toFixed(4) || '0.0000'}
                              </span>
                            </div>
                            <div>
                              <span className="text-neutral-600">Time:</span>{' '}
                              <span className="font-medium text-neutral-900">
                                {new Date(child.created_at).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>

                          {/* System Prompt */}
                          {child.input_data?.system_prompt && (
                            <div className="mb-4">
                              <div className="flex items-center justify-between mb-2">
                                <label className="text-xs font-medium text-neutral-700">System Prompt</label>
                                <button
                                  onClick={() => copyToClipboard(child.input_data.system_prompt, `child-system-${child.id}`)}
                                  className="text-xs text-neutral-600 hover:text-neutral-900 hover:bg-white/50 flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all duration-200"
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
                              <pre className="bg-white border border-neutral-300 rounded-lg p-4 text-xs font-mono overflow-x-auto max-h-40 overflow-y-auto">
                                {child.input_data.system_prompt}
                              </pre>
                            </div>
                          )}

                          {/* Input Prompt */}
                          {child.input_data?.prompt && (
                            <div className="mb-4">
                              <label className="text-xs font-medium text-neutral-700 mb-2 block">Input</label>
                              <pre className="bg-white border border-neutral-300 rounded-lg p-4 text-xs font-mono overflow-x-auto max-h-32 overflow-y-auto">
                                {child.input_data.prompt}
                              </pre>
                            </div>
                          )}

                          {/* Output Response */}
                          {child.output_data?.response && (
                            <div>
                              <label className="text-xs font-medium text-neutral-700 mb-2 block">Output</label>
                              <pre className="bg-white border border-neutral-300 rounded-lg p-4 text-xs font-mono overflow-x-auto max-h-32 overflow-y-auto">
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
                    <div className="space-y-5">
                      {trace.spans.map((span, index) => (
                        <div key={span.id} className="border border-neutral-200 rounded-xl p-6">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono text-neutral-500">#{index + 1}</span>
                              <span className="text-sm font-medium text-neutral-900">{span.name}</span>
                              <StatusIndicator status={span.status as any} />
                            </div>
                            <span className="text-sm text-neutral-600">{span.duration_ms?.toFixed(0) || 0}ms</span>
                          </div>
                          {span.prompt_tokens && (
                            <div className="text-xs text-neutral-600 mt-1">
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
                    <pre className="bg-neutral-50 border border-neutral-200 rounded-xl p-6 text-xs font-mono overflow-x-auto max-h-64 overflow-y-auto">
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

  // Render modal in a portal to escape parent stacking contexts
  return createPortal(modalContent, document.body);
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
    <div className="border-2 border-neutral-300 rounded-2xl overflow-hidden shadow-md bg-white">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between bg-neutral-50 hover:bg-neutral-100 transition-colors duration-200"
        style={{ padding: '1.5rem 2rem' }}
        aria-expanded={isExpanded}
      >
        <h3 className="text-base font-semibold text-neutral-900">{title}</h3>
        {isExpanded ? (
          <ChevronDown className="h-4 w-4 text-neutral-600" />
        ) : (
          <ChevronRight className="h-4 w-4 text-neutral-600" />
        )}
      </button>
      {isExpanded && <div className="bg-white" style={{ padding: '2rem' }}>{children}</div>}
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
    <div style={{ display: 'flex', alignItems: 'baseline', gap: '2rem', padding: '0.75rem 0' }}>
      <dt className="text-sm font-medium text-neutral-600" style={{ minWidth: '140px', flexShrink: 0 }}>
        {label}:
      </dt>
      <dd className="text-sm text-neutral-900 font-normal break-words" style={{ flex: 1 }}>
        {value}
      </dd>
    </div>
  );
};

export default TraceDetailModal;
