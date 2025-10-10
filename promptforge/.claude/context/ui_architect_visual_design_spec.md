# Parent-Child Trace View - Visual Design Specification

## Overview
This document provides the detailed visual design and UX specifications for the parent-child trace view enhancement in the PromptForge Trace Dashboard.

---

## 1. Table Structure Enhancement

### Current Table Columns
```
| Request ID | Project | Status | Model | Duration | Timestamp |
```

### Enhanced Table Columns
```
| [±] | Source | Request ID | Project | Status | Model | Tokens | Cost | Duration | Timestamp |
```

**Column Details:**

1. **[±] Expand/Collapse Icon (New)**
   - Width: 40px
   - Only visible for parent traces
   - Icons: `ChevronRight` (collapsed), `ChevronDown` (expanded)
   - Empty space for normal traces (alignment)

2. **Source (New)**
   - Width: 150px
   - Badge format with icon
   - Dropdown filter in FilterBar

3. **Request ID**
   - Unchanged
   - Font: monospace
   - Truncate with ellipsis if too long

4. **Project**
   - Unchanged

5. **Status**
   - Unchanged (uses StatusIndicator component)

6. **Model**
   - Parent trace: Show first child's model OR "Multiple Models"
   - Child trace: Show actual model
   - Tooltip on hover for parent (lists all models)

7. **Tokens (New - replaces/supplements Duration for parents)**
   - Parent trace: `∑ 12,500` (sum of children)
   - Child trace: `1,500` (actual value)
   - Format: Number with commas

8. **Cost**
   - Parent trace: `∑ $0.0141` (sum of children)
   - Child trace: `$0.0045` (actual value)
   - Format: Currency with 4 decimal places

9. **Duration**
   - Parent trace: `Avg 850ms` (average of children)
   - Child trace: `1247ms` (actual value)

10. **Timestamp**
    - Unchanged

---

## 2. Visual Hierarchy & Styling

### Parent Trace Row
```tsx
<tr className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
  {/* Expand Icon Cell */}
  <td className="px-3 py-3">
    <button onClick={(e) => { e.stopPropagation(); toggleExpand(trace.id); }}>
      {expandedParents.has(trace.id) ?
        <ChevronDown className="h-4 w-4 text-gray-600" /> :
        <ChevronRight className="h-4 w-4 text-gray-600" />
      }
    </button>
  </td>

  {/* Source Badge */}
  <td className="px-6 py-3">
    <SourceBadge source={trace.source} />
  </td>

  {/* Request ID - Bold for parent */}
  <td className="px-6 py-3 text-sm font-mono font-semibold text-gray-900">
    {trace.trace_id}
    <span className="ml-2 text-xs text-gray-500">({trace.child_count} stages)</span>
  </td>

  {/* Project */}
  <td className="px-6 py-3 text-sm text-gray-900">
    {trace.project_name}
  </td>

  {/* Status */}
  <td className="px-6 py-3">
    <StatusIndicator status={trace.status} />
  </td>

  {/* Model - with tooltip */}
  <td className="px-6 py-3 text-sm text-gray-700" title={trace.aggregated_data?.model_names.join(', ')}>
    {trace.aggregated_data?.model_names.length === 1 ?
      trace.aggregated_data.model_names[0] :
      'Multiple Models'
    }
  </td>

  {/* Tokens - aggregated */}
  <td className="px-6 py-3 text-sm text-gray-700 text-right tabular-nums">
    <span className="text-blue-600 font-medium">∑ {trace.aggregated_data?.total_tokens.toLocaleString()}</span>
  </td>

  {/* Cost - aggregated */}
  <td className="px-6 py-3 text-sm text-gray-700 text-right tabular-nums">
    <span className="text-blue-600 font-medium">∑ ${trace.aggregated_data?.total_cost.toFixed(4)}</span>
  </td>

  {/* Duration - average */}
  <td className="px-6 py-3 text-sm text-gray-700 text-right tabular-nums">
    Avg {Math.round(trace.aggregated_data?.avg_duration_ms || 0)}ms
  </td>

  {/* Timestamp */}
  <td className="px-6 py-3 text-sm text-gray-700 text-right tabular-nums">
    {new Date(trace.created_at).toLocaleString()}
  </td>
</tr>
```

### Child Trace Row
```tsx
<tr className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors bg-gray-50/50">
  {/* Empty expand icon cell for alignment */}
  <td className="px-3 py-3"></td>

  {/* Empty source cell (inherited from parent) */}
  <td className="px-6 py-3"></td>

  {/* Request ID - with indentation and stage indicator */}
  <td className="px-6 py-3 pl-12 text-sm font-mono text-gray-600">
    <div className="flex items-center gap-2">
      <div className="w-6 h-px bg-gray-300"></div> {/* Connector line */}
      <span>{trace.trace_id}</span>
    </div>
    <div className="text-xs text-gray-500 mt-1 pl-8">
      {trace.stage} {/* e.g., "Stage 1: Fact Extraction" */}
    </div>
  </td>

  {/* Project - lighter text */}
  <td className="px-6 py-3 text-sm text-gray-500">
    {trace.project_name}
  </td>

  {/* Status */}
  <td className="px-6 py-3">
    <StatusIndicator status={trace.status} size="sm" />
  </td>

  {/* Model - actual value */}
  <td className="px-6 py-3 text-sm text-gray-600">
    {trace.model_name}
  </td>

  {/* Tokens - actual value */}
  <td className="px-6 py-3 text-sm text-gray-600 text-right tabular-nums">
    {trace.total_tokens?.toLocaleString()}
  </td>

  {/* Cost - actual value */}
  <td className="px-6 py-3 text-sm text-gray-600 text-right tabular-nums">
    ${trace.total_cost?.toFixed(4)}
  </td>

  {/* Duration - actual value */}
  <td className="px-6 py-3 text-sm text-gray-600 text-right tabular-nums">
    {Math.round(trace.total_duration_ms || 0)}ms
  </td>

  {/* Timestamp */}
  <td className="px-6 py-3 text-sm text-gray-600 text-right tabular-nums">
    {new Date(trace.created_at).toLocaleString()}
  </td>
</tr>
```

### Normal Trace Row (No Children)
```tsx
{/* Same as current implementation - no changes */}
<tr className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
  {/* Empty expand icon cell */}
  <td className="px-3 py-3"></td>

  {/* Source Badge */}
  <td className="px-6 py-3">
    <SourceBadge source={trace.source} />
  </td>

  {/* Rest of columns same as current */}
  {/* ... */}
</tr>
```

---

## 3. Source Badge Component

### Component Design
```tsx
// File: /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/src/components/SourceBadge.tsx

import React from 'react';
import { Workflow, Sparkles } from 'lucide-react';

export type TraceSource = 'call_insights' | 'playground' | 'other';

interface SourceBadgeProps {
  source?: string;
}

const SourceBadge: React.FC<SourceBadgeProps> = ({ source }) => {
  const getBadgeConfig = (source?: string) => {
    switch (source) {
      case 'call_insights':
        return {
          text: 'Call Insights',
          icon: Workflow,
          className: 'bg-blue-100 text-blue-800 border-blue-200',
        };
      case 'playground':
        return {
          text: 'Prompt Playground',
          icon: Sparkles,
          className: 'bg-purple-100 text-purple-800 border-purple-200',
        };
      default:
        return {
          text: 'Other',
          icon: null,
          className: 'bg-gray-100 text-gray-800 border-gray-200',
        };
    }
  };

  const config = getBadgeConfig(source);
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.className}`}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {config.text}
    </span>
  );
};

export default SourceBadge;
```

### Visual Examples

**Call Insights Badge:**
```
┌─────────────────────────┐
│ [≋] Call Insights       │  (Blue badge with Workflow icon)
└─────────────────────────┘
bg-blue-100 text-blue-800 border-blue-200
```

**Prompt Playground Badge:**
```
┌─────────────────────────┐
│ [✨] Prompt Playground   │  (Purple badge with Sparkles icon)
└─────────────────────────┘
bg-purple-100 text-purple-800 border-purple-200
```

**Other Badge:**
```
┌─────────────────────────┐
│ Other                   │  (Gray badge, no icon)
└─────────────────────────┘
bg-gray-100 text-gray-800 border-gray-200
```

---

## 4. Filter Bar Enhancement

### Current FilterBar
```tsx
<FilterBar
  searchQuery={searchQuery}
  onSearchChange={setSearchQuery}
  modelFilter={modelFilter}
  onModelFilterChange={setModelFilter}
/>
```

### Enhanced FilterBar
```tsx
<FilterBar
  searchQuery={searchQuery}
  onSearchChange={setSearchQuery}
  modelFilter={modelFilter}
  onModelFilterChange={setModelFilter}
  sourceFilter={sourceFilter}           // NEW
  onSourceFilterChange={setSourceFilter} // NEW
/>
```

### Source Filter Dropdown Design
```tsx
{/* Add after Model filter in FilterBar.tsx */}
<div className="relative">
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Source
  </label>
  <select
    value={sourceFilter}
    onChange={(e) => onSourceFilterChange(e.target.value)}
    className="w-48 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  >
    <option value="">All Sources</option>
    <option value="call_insights">Call Insights</option>
    <option value="playground">Prompt Playground</option>
  </select>
</div>
```

**Visual Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Search  [_________________________________]                      │
│  Model   [All Models ▼]    Source  [All Sources ▼]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Trace Detail Modal Enhancement

### Parent Trace Detail View

**Header Addition:**
```tsx
<div className="flex items-center gap-3 mt-2">
  <SourceBadge source={trace.source} />
  <span className="text-sm font-mono text-gray-700">{trace.trace_id}</span>
  <StatusIndicator status={trace.status as any} />
  <span className="text-sm text-gray-600">{trace.model_name || 'Unknown Model'}</span>

  {/* NEW: Child count indicator for parent traces */}
  {trace.has_children && (
    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
      {trace.child_count} child traces
    </span>
  )}
</div>
```

**New Section: Child Traces (for parent traces)**
```tsx
{trace.has_children && trace.children && (
  <Section
    title={`Child Traces (${trace.children.length})`}
    isExpanded={expandedSections.children}
    onToggle={() => toggleSection('children')}
  >
    <div className="space-y-2">
      {trace.children.map((child) => (
        <div
          key={child.id}
          onClick={() => openChildTraceDetail(child.id)}
          className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-900">{child.stage}</span>
              <StatusIndicator status={child.status as any} size="sm" />
            </div>
            <div className="text-sm text-gray-600">
              {child.total_tokens?.toLocaleString()} tokens • ${child.total_cost?.toFixed(4)}
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1 font-mono">
            {child.trace_id}
          </div>
        </div>
      ))}
    </div>

    {/* Aggregation Summary */}
    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="text-sm font-medium text-blue-900 mb-2">Total Aggregated Metrics</div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-blue-700">Tokens:</span>
          <span className="ml-2 font-semibold text-blue-900">
            ∑ {trace.aggregated_data?.total_tokens.toLocaleString()}
          </span>
        </div>
        <div>
          <span className="text-blue-700">Cost:</span>
          <span className="ml-2 font-semibold text-blue-900">
            ∑ ${trace.aggregated_data?.total_cost.toFixed(4)}
          </span>
        </div>
        <div>
          <span className="text-blue-700">Avg Duration:</span>
          <span className="ml-2 font-semibold text-blue-900">
            {Math.round(trace.aggregated_data?.avg_duration_ms || 0)}ms
          </span>
        </div>
      </div>
    </div>
  </Section>
)}
```

### Child Trace Detail View

**Header Addition:**
```tsx
{/* NEW: Parent trace link for child traces */}
{trace.parent_trace_id && (
  <div className="mt-2 text-sm text-gray-600">
    <span>Child of:</span>
    <button
      onClick={() => openParentTraceDetail(trace.parent_trace_id)}
      className="ml-2 text-blue-600 hover:text-blue-800 underline font-mono"
    >
      {trace.parent_trace_id}
    </button>
  </div>
)}

{/* Stage indicator */}
{trace.stage && (
  <div className="mt-1 text-sm text-gray-500">
    {trace.stage}
  </div>
)}
```

---

## 6. Interaction Flows

### Flow 1: Expand Parent Trace
```
User Action: Click expand icon (ChevronRight) on parent row
   ↓
System Response:
   1. Call toggleExpand(parentTraceId)
   2. Update expandedParents state: Set.add(parentTraceId)
   3. Re-render table with children visible
   4. Animate expansion (using CSS transition)
   5. Change icon to ChevronDown
```

### Flow 2: View Parent Trace Details
```
User Action: Click on parent row (not on expand icon)
   ↓
System Response:
   1. Call onRowClick(parentTraceId)
   2. Open TraceDetailModal with parent trace data
   3. Show aggregated metrics in modal
   4. Display child traces section with individual child summaries
   5. Allow clicking child to view child detail
```

### Flow 3: View Child Trace Details
```
User Action: Click on child row (when parent is expanded)
   ↓
System Response:
   1. Call onRowClick(childTraceId)
   2. Open TraceDetailModal with child trace data
   3. Show link to parent trace in header
   4. Display stage information
   5. Allow clicking parent link to navigate to parent detail
```

### Flow 4: Filter by Source
```
User Action: Select "Call Insights" from Source dropdown
   ↓
System Response:
   1. Update sourceFilter state
   2. useTraces hook detects change
   3. Fetch traces with source_filter='call_insights'
   4. Re-render table with filtered results
   5. Show only traces with source='call_insights'
```

---

## 7. Responsive Behavior

### Desktop (>1024px)
- All columns visible
- Full text for source badges
- Comfortable spacing

### Tablet (768px - 1024px)
- Hide Duration column (keep Tokens and Cost)
- Shorten source badge text: "Call Insights" → "Insights"
- Reduce padding

### Mobile (<768px)
- Stack into card layout (not table)
- Show only: Source, Request ID, Status, Tokens, Cost
- Expandable details for full info
- Swipe gestures for expand/collapse

---

## 8. Accessibility Requirements

### Keyboard Navigation
- Tab key: Navigate through expand icons, then through rows
- Enter/Space on expand icon: Toggle expansion
- Enter on row: Open detail modal
- Arrow keys: Navigate between rows (optional enhancement)

### Screen Reader Support
```tsx
{/* Expand button */}
<button
  onClick={(e) => { e.stopPropagation(); toggleExpand(trace.id); }}
  aria-label={expandedParents.has(trace.id) ?
    'Collapse to hide child traces' :
    'Expand to show child traces'
  }
  aria-expanded={expandedParents.has(trace.id)}
>
  {/* Icon */}
</button>

{/* Parent row */}
<tr
  role="button"
  tabIndex={0}
  aria-label={`Parent trace ${trace.trace_id} with ${trace.child_count} children. Click to view details.`}
  onClick={() => onRowClick(trace.id)}
  onKeyDown={(e) => e.key === 'Enter' && onRowClick(trace.id)}
>
  {/* Cells */}
</tr>

{/* Child row */}
<tr
  role="button"
  tabIndex={0}
  aria-label={`Child trace ${trace.stage} of parent ${trace.parent_trace_id}. Click to view details.`}
  onClick={() => onRowClick(trace.id)}
  onKeyDown={(e) => e.key === 'Enter' && onRowClick(trace.id)}
>
  {/* Cells */}
</tr>
```

### Color Contrast
- All text colors meet WCAG AA standards (4.5:1 ratio)
- Source badges: High contrast borders and backgrounds
- Focus indicators: 2px blue outline on focus

---

## 9. Animation & Transitions

### Expand/Collapse Animation
```css
/* Add to TracesTable.tsx or global CSS */
.child-row-enter {
  opacity: 0;
  transform: translateY(-10px);
}

.child-row-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 200ms ease-in, transform 200ms ease-in;
}

.child-row-exit {
  opacity: 1;
  transform: translateY(0);
}

.child-row-exit-active {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 150ms ease-out, transform 150ms ease-out;
}
```

### Hover States
```tsx
{/* Parent row hover */}
className="... hover:bg-gray-50 transition-colors duration-150"

{/* Child row hover */}
className="... hover:bg-blue-50 transition-colors duration-150"

{/* Expand icon hover */}
className="... hover:text-gray-900 transition-colors duration-100"
```

---

## 10. Empty States

### No Parent Traces with Children
```tsx
{traces.length > 0 && !traces.some(t => t.has_children) && (
  <div className="text-center py-8 text-gray-500 text-sm">
    No multi-stage traces found. All traces are standalone executions.
  </div>
)}
```

### No Traces for Selected Source Filter
```tsx
{traces.length === 0 && sourceFilter && (
  <div className="text-center py-8">
    <p className="text-gray-700 text-sm">
      No traces found for source: <strong>{sourceFilter}</strong>
    </p>
    <button
      onClick={() => setSourceFilter('')}
      className="mt-2 text-blue-600 hover:text-blue-800 text-sm underline"
    >
      Clear source filter
    </button>
  </div>
)}
```

---

## 11. Performance Optimizations

### Memoization
```tsx
// Memoize row rendering
const TraceRow = React.memo<TraceRowProps>(({ trace, isChild, onExpand, onRowClick }) => {
  // ... row implementation
});

// Memoize source badge
const SourceBadge = React.memo<SourceBadgeProps>(({ source }) => {
  // ... badge implementation
});
```

### Virtualization (Future Enhancement)
If dataset grows beyond 100+ parent traces:
- Implement react-window or react-virtual
- Render only visible rows + buffer
- Maintain expansion state separately

---

## 12. Testing Scenarios

### Visual Regression Tests
1. Parent trace collapsed state
2. Parent trace expanded state
3. Child traces with indentation
4. Source badges for each type
5. Aggregated values display
6. Hover states
7. Focus states (keyboard navigation)
8. Empty states

### Interaction Tests
1. Click expand icon → children appear
2. Click parent row → modal opens with parent data
3. Click child row → modal opens with child data
4. Filter by source → correct traces shown
5. Navigate with keyboard → focus moves correctly
6. Screen reader → announces correctly

---

## 13. Design Assets Reference

### Color Palette
```
Primary Blue (Aggregations): #2563EB (blue-600)
Secondary Purple (Playground): #9333EA (purple-600)
Gray Scale:
  - Gray 50: #F9FAFB (backgrounds)
  - Gray 100: #F3F4F6 (borders, badges)
  - Gray 500: #6B7280 (secondary text)
  - Gray 700: #374151 (primary text)
  - Gray 900: #111827 (headings)
```

### Typography
```
Font Family: System font stack (default Tailwind)
Font Sizes:
  - xs: 0.75rem (12px) - badges, helper text
  - sm: 0.875rem (14px) - table text
  - base: 1rem (16px) - headings
  - 2xl: 1.5rem (24px) - modal titles
Font Weights:
  - normal: 400
  - medium: 500
  - semibold: 600
  - bold: 700
```

### Spacing
```
Table Cell Padding:
  - px-6 py-3 (1.5rem horizontal, 0.75rem vertical)

Child Row Indentation:
  - pl-12 (3rem left padding)

Badge Padding:
  - px-2.5 py-1 (0.625rem horizontal, 0.25rem vertical)
```

---

## 14. Implementation Checklist

### Phase 1: Backend
- [ ] Create AggregatedTraceData schema
- [ ] Enhance TraceListItem schema
- [ ] Update list_traces query logic
- [ ] Add source_filter parameter
- [ ] Create database indexes
- [ ] Test API with parent-child data

### Phase 2: Frontend
- [ ] Create SourceBadge component
- [ ] Update TypeScript interfaces
- [ ] Add source filter to FilterBar
- [ ] Implement expandable rows in TracesTable
- [ ] Update TraceDetailModal for parent/child
- [ ] Add aggregation display logic
- [ ] Test all interactions

### Phase 3: Polish
- [ ] Add animations
- [ ] Implement accessibility features
- [ ] Add responsive behavior
- [ ] Optimize performance
- [ ] Write component tests
- [ ] Update documentation

---

## Conclusion

This visual design specification provides a complete blueprint for implementing the parent-child trace view enhancement. The design maintains consistency with the existing PromptForge UI while adding powerful hierarchical visualization capabilities.

**Key Design Principles:**
1. **Visual Hierarchy:** Clear distinction between parent and child traces
2. **Information Density:** Show aggregated metrics without cluttering the UI
3. **Interaction Clarity:** Intuitive expand/collapse and navigation behavior
4. **Accessibility First:** Full keyboard and screen reader support
5. **Performance:** Optimized rendering and state management

**Next Steps:**
1. Review design with stakeholders
2. Create mockups/prototypes if needed
3. Begin implementation following the plan
4. Iterate based on user feedback
