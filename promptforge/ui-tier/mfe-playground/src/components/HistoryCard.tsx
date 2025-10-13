import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ChevronDown,
  ChevronRight,
  Clock,
  DollarSign,
  Hash,
  Play,
  Thermometer,
  Sliders,
  Target,
  Sparkles,
  Copy,
  ExternalLink,
  Check,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PlaygroundSession } from '../types/playground';

interface HistoryCardProps {
  session: PlaygroundSession;
  onLoadIntoEditor?: (session: PlaygroundSession) => void;
  defaultExpanded?: boolean;
}

export const HistoryCard: React.FC<HistoryCardProps> = ({
  session,
  onLoadIntoEditor,
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [copiedTraceId, setCopiedTraceId] = useState(false);
  const navigate = useNavigate();

  // Format timestamp to relative time
  const getRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Handle "Load into Editor" - restores all form fields
  const handleLoadIntoEditor = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onLoadIntoEditor) {
      onLoadIntoEditor(session);
    }
  };

  // Copy trace ID to clipboard
  const handleCopyTraceId = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(session.id);
    setCopiedTraceId(true);
    setTimeout(() => setCopiedTraceId(false), 2000);
  };

  return (
    <div
      className="bg-white border border-neutral-200 rounded-xl overflow-hidden hover:border-[#FF385C]/30 transition-all duration-200 shadow-sm hover:shadow-md"
      role="article"
      aria-label={`Playground session: ${session.title || 'Untitled'}`}
    >
      {/* Header - Always Visible (Collapsed View) */}
      <div
        className="p-5 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsExpanded(!isExpanded);
          }
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Title & Timestamp Row */}
            <div className="flex items-center gap-2 mb-2">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-neutral-500 flex-shrink-0" aria-hidden="true" />
              ) : (
                <ChevronRight className="h-4 w-4 text-neutral-500 flex-shrink-0" aria-hidden="true" />
              )}
              <h4 className="text-sm font-bold text-neutral-800 truncate" title={session.title}>
                {session.title || <span className="text-neutral-400 italic">Untitled Session</span>}
              </h4>
              <span className="text-xs text-neutral-500 flex-shrink-0">
                {getRelativeTime(session.timestamp)}
              </span>
            </div>

            {/* Model & Quick Metrics (Collapsed View) */}
            <div className="flex items-center gap-4 text-xs text-neutral-500 ml-6">
              <span className="font-medium text-neutral-700">{session.model.name}</span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" aria-hidden="true" />
                {(session.metrics.latency * 1000).toFixed(0)}ms
              </span>
              <span className="flex items-center gap-1">
                <Hash className="h-3 w-3" aria-hidden="true" />
                {session.metrics.tokens}
              </span>
              <span className="flex items-center gap-1">
                <DollarSign className="h-3 w-3" aria-hidden="true" />
                ${session.metrics.cost.toFixed(4)}
              </span>
            </div>

            {/* Prompt Preview (Collapsed View Only) */}
            {!isExpanded && (
              <p className="text-sm text-neutral-600 line-clamp-2 ml-6 mt-2">{session.prompt}</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 ml-4" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={handleLoadIntoEditor}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-[#FF385C] hover:bg-[#FF385C] hover:text-white rounded-lg transition-colors border border-[#FF385C] focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
              title="Load into Editor"
              aria-label="Load this session into the editor"
            >
              <Play className="h-3 w-3" aria-hidden="true" />
              Load
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-neutral-200 overflow-hidden"
          >
            <div className="p-5 space-y-5">
              {/* Trace ID */}
              <div>
                <label className="block text-xs font-semibold text-neutral-600 mb-1">
                  Trace ID
                </label>
                <div className="flex items-center gap-2">
                  <code className="flex-1 text-xs bg-neutral-50 px-2 py-1.5 rounded border border-neutral-200 font-mono text-neutral-700 break-all">
                    {session.id}
                  </code>
                  <button
                    onClick={handleCopyTraceId}
                    className="p-1.5 text-neutral-600 hover:bg-neutral-100 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
                    title="Copy Trace ID"
                    aria-label="Copy trace ID to clipboard"
                  >
                    {copiedTraceId ? (
                      <Check className="h-3.5 w-3.5 text-green-600" aria-hidden="true" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>

              {/* Intent & Tone (if available) */}
              {(session.metadata?.intent || session.metadata?.tone) && (
                <div className="grid grid-cols-2 gap-4">
                  {session.metadata.intent && (
                    <div>
                      <label className="block text-xs font-semibold text-neutral-600 mb-1 flex items-center gap-1">
                        <Target className="h-3 w-3" aria-hidden="true" />
                        Intent
                      </label>
                      <p className="text-sm text-neutral-700">{session.metadata.intent}</p>
                    </div>
                  )}
                  {session.metadata.tone && (
                    <div>
                      <label className="block text-xs font-semibold text-neutral-600 mb-1 flex items-center gap-1">
                        <Sparkles className="h-3 w-3" aria-hidden="true" />
                        Tone
                      </label>
                      <p className="text-sm text-neutral-700 capitalize">{session.metadata.tone}</p>
                    </div>
                  )}
                </div>
              )}

              {/* System Prompt (if available) */}
              {session.systemPrompt && (
                <div>
                  <label className="block text-xs font-semibold text-neutral-600 mb-1">
                    System Prompt
                  </label>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3 max-h-32 overflow-y-auto">
                    <p className="text-sm text-neutral-700 whitespace-pre-wrap font-mono">
                      {session.systemPrompt}
                    </p>
                  </div>
                </div>
              )}

              {/* User Prompt */}
              <div>
                <label className="block text-xs font-semibold text-neutral-600 mb-1">
                  User Prompt
                </label>
                <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3 max-h-32 overflow-y-auto">
                  <p className="text-sm text-neutral-700 whitespace-pre-wrap font-mono">
                    {session.prompt}
                  </p>
                </div>
              </div>

              {/* Model Parameters */}
              <div>
                <label className="block text-xs font-semibold text-neutral-600 mb-2">
                  Model Parameters
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <Thermometer className="h-3 w-3" aria-hidden="true" />
                      Temperature
                    </div>
                    <div className="text-base font-bold text-neutral-800">
                      {session.parameters.temperature.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <Hash className="h-3 w-3" aria-hidden="true" />
                      Max Tokens
                    </div>
                    <div className="text-base font-bold text-neutral-800">
                      {session.parameters.maxTokens}
                    </div>
                  </div>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <Sliders className="h-3 w-3" aria-hidden="true" />
                      Top P
                    </div>
                    <div className="text-base font-bold text-neutral-800">
                      {session.parameters.topP.toFixed(2)}
                    </div>
                  </div>
                  {session.parameters.topK !== undefined && (
                    <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                      <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                        <Sliders className="h-3 w-3" aria-hidden="true" />
                        Top K
                      </div>
                      <div className="text-base font-bold text-neutral-800">
                        {session.parameters.topK}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Evaluation IDs (if available) */}
              {session.evaluationIds && session.evaluationIds.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-neutral-600 mb-1">
                    Evaluations Run ({session.evaluationIds.length})
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {session.evaluationIds.map((evalId) => (
                      <span
                        key={evalId}
                        className="px-2.5 py-1 text-xs bg-[#FF385C]/10 text-[#FF385C] rounded-full font-medium border border-[#FF385C]/20"
                      >
                        {evalId.slice(0, 8)}...
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Response */}
              <div>
                <label className="block text-xs font-semibold text-neutral-600 mb-1">
                  Model Response
                </label>
                <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3 max-h-64 overflow-y-auto">
                  <p className="text-sm text-neutral-700 whitespace-pre-wrap">
                    {session.response}
                  </p>
                </div>
              </div>

              {/* Detailed Metrics */}
              <div>
                <label className="block text-xs font-semibold text-neutral-600 mb-2">
                  Execution Metrics
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <Clock className="h-3 w-3" aria-hidden="true" />
                      Latency
                    </div>
                    <div className="text-lg font-bold text-neutral-800">
                      {(session.metrics.latency * 1000).toFixed(0)}ms
                    </div>
                  </div>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <Hash className="h-3 w-3" aria-hidden="true" />
                      Tokens
                    </div>
                    <div className="text-lg font-bold text-neutral-800">
                      {session.metrics.tokens}
                    </div>
                  </div>
                  <div className="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-neutral-600 text-xs mb-1">
                      <DollarSign className="h-3 w-3" aria-hidden="true" />
                      Cost
                    </div>
                    <div className="text-lg font-bold text-neutral-800">
                      ${session.metrics.cost.toFixed(4)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HistoryCard;
