import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import StatusIndicator from './StatusIndicator';
import SourceBadge from './SourceBadge';
import { TraceListItem } from '../../../shared/services/traceService';

interface TracesTableProps {
  traces: TraceListItem[];
  sortColumn: 'requestId' | 'status' | 'duration' | 'timestamp';
  sortDirection: 'asc' | 'desc';
  onSort: (column: 'requestId' | 'status' | 'duration' | 'timestamp') => void;
  onRowClick: (traceId: string) => void;
}

const TracesTable: React.FC<TracesTableProps> = ({
  traces,
  sortColumn,
  sortDirection,
  onSort,
  onRowClick,
}) => {
  const [expandedTraceIds, setExpandedTraceIds] = useState<Set<string>>(new Set());

  const toggleExpanded = (traceId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setExpandedTraceIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(traceId)) {
        newSet.delete(traceId);
      } else {
        newSet.add(traceId);
      }
      return newSet;
    });
  };

  const SortButton: React.FC<{
    column: 'requestId' | 'status' | 'duration' | 'timestamp';
    children: React.ReactNode;
    align?: 'left' | 'right';
  }> = ({ column, children, align = 'left' }) => (
    <button
      onClick={() => onSort(column)}
      className={`flex items-center gap-1 hover:text-neutral-900 transition-colors ${
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

  const renderTraceRow = (trace: TraceListItem, isChild = false, depth = 0) => {
    const isExpanded = expandedTraceIds.has(trace.id);
    const hasChildren = trace.has_children && trace.children.length > 0;

    // Determine what data to display
    const displayTokens = trace.aggregated_data?.total_tokens ?? trace.total_tokens;
    const displayCost = trace.aggregated_data?.total_cost ?? trace.total_cost;
    const displayDuration = trace.aggregated_data?.avg_duration_ms ?? trace.total_duration_ms;
    const displayModel = trace.aggregated_data?.model_names?.[0] ?? trace.model_name;

    return (
      <React.Fragment key={trace.id}>
        <tr
          onClick={() => onRowClick(trace.id)}
          onKeyDown={(e) => e.key === 'Enter' && onRowClick(trace.id)}
          tabIndex={0}
          className={`border-b border-neutral-100 hover:bg-neutral-50 cursor-pointer transition-colors last:border-b-0 ${
            isChild ? 'bg-neutral-50/50' : ''
          }`}
          aria-label={`View trace ${trace.trace_id}`}
        >
          <td className="px-6 py-3">
            <div className="flex items-center gap-2" style={{ paddingLeft: `${depth * 24}px` }}>
              {hasChildren ? (
                <button
                  onClick={(e) => toggleExpanded(trace.id, e)}
                  className="p-1 hover:bg-neutral-200 rounded transition-colors flex-shrink-0"
                  aria-label={isExpanded ? 'Collapse children' : 'Expand children'}
                  aria-expanded={isExpanded}
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4 text-neutral-600" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-neutral-600" />
                  )}
                </button>
              ) : (
                <div className="w-6" /> // Spacer for alignment
              )}
              <span className="text-sm font-mono text-neutral-900 truncate">
                {trace.trace_id}
              </span>
              {isChild && trace.stage && (
                <span className="text-xs text-neutral-500 bg-neutral-100 px-2 py-0.5 rounded">
                  {trace.stage}
                </span>
              )}
            </div>
          </td>
          <td className="px-6 py-3 text-sm text-neutral-900">{trace.project_name}</td>
          <td className="px-6 py-3">
            <div className="flex items-center gap-2">
              <StatusIndicator status={trace.status as any} />
              <SourceBadge source={trace.source} />
            </div>
          </td>
          <td className="px-6 py-3 text-sm text-neutral-700">
            {displayModel ? (
              <div className="flex flex-col gap-0.5">
                <span>{displayModel}</span>
                {trace.aggregated_data?.model_names && trace.aggregated_data.model_names.length > 1 && (
                  <span className="text-xs text-neutral-500">
                    +{trace.aggregated_data.model_names.length - 1} more
                  </span>
                )}
              </div>
            ) : (
              '-'
            )}
          </td>
          <td className="px-6 py-3 text-sm text-neutral-700 text-right tabular-nums">
            {displayTokens != null ? (
              <>
                {trace.aggregated_data ? '∑ ' : ''}
                {displayTokens.toLocaleString()}
              </>
            ) : (
              '-'
            )}
          </td>
          <td className="px-6 py-3 text-sm text-neutral-700 text-right tabular-nums">
            {displayCost != null ? (
              <>
                {trace.aggregated_data ? '∑ ' : ''}${displayCost.toFixed(4)}
              </>
            ) : (
              '-'
            )}
          </td>
          <td className="px-6 py-3 text-sm text-neutral-700 text-right tabular-nums">
            {displayDuration != null ? (
              <>
                {trace.aggregated_data ? 'Ø ' : ''}
                {Math.round(displayDuration)}ms
              </>
            ) : (
              '-'
            )}
          </td>
          <td className="px-6 py-3 text-sm text-neutral-700 text-right tabular-nums">
            {new Date(trace.created_at).toLocaleString()}
          </td>
        </tr>

        {/* Render children if expanded */}
        {isExpanded && hasChildren && (
          <>
            {trace.children.map((child) => renderTraceRow(child, true, depth + 1))}
          </>
        )}
      </React.Fragment>
    );
  };

  return (
    <div className="border border-neutral-200 rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-neutral-50 border-b border-neutral-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wide">
              <SortButton column="requestId">Request ID</SortButton>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wide">
              Project
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wide">
              <SortButton column="status">Status / Source</SortButton>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-neutral-700 uppercase tracking-wide">
              Model
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-neutral-700 uppercase tracking-wide">
              Tokens
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-neutral-700 uppercase tracking-wide">
              Cost
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-neutral-700 uppercase tracking-wide">
              <SortButton column="duration" align="right">
                Duration
              </SortButton>
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-neutral-700 uppercase tracking-wide">
              <SortButton column="timestamp" align="right">
                Timestamp
              </SortButton>
            </th>
          </tr>
        </thead>
        <tbody>
          {traces.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-6 py-12 text-center text-sm text-neutral-700">
                No traces found
              </td>
            </tr>
          ) : (
            traces.map((trace) => renderTraceRow(trace))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TracesTable;
