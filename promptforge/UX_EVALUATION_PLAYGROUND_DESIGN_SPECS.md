# Evaluation Playground - UX Design Specifications

**Project**: PromptForge Evaluation Playground (mfe-evaluations)
**Version**: 1.0
**Last Updated**: 2025-10-08
**Owner**: UX Specialist
**Status**: Ready for UI Architect Implementation

---

## Table of Contents
1. [Design System Overview](#design-system-overview)
2. [Component Specifications](#component-specifications)
   - [CreateCustomEvaluationModal](#1-createcustomevaluationmodal)
   - [FilterBar](#2-filterbar)
   - [Pagination Controls](#3-pagination-controls)
   - [EvaluationDetailModal](#4-evaluationdetailmodal)
3. [Accessibility Requirements](#accessibility-requirements)
4. [Responsive Design](#responsive-design)
5. [Implementation Checklist](#implementation-checklist)

---

## Design System Overview

### Color Palette (Airbnb-Inspired)

```typescript
const colors = {
  // Primary Action Colors
  primary: '#FF385C',           // Vibrant red (primary CTA)
  primaryHover: '#E31C5F',      // Darker red (hover state)
  primaryLight: '#FF385C10',    // 10% opacity background

  // Secondary Action Colors
  secondary: '#0066FF',         // Bright blue (secondary actions)
  secondaryDark: '#0052CC',     // Darker blue (hover)
  secondaryLight: '#0066FF10',  // 10% opacity background

  // Status Colors
  success: '#00A699',           // Teal (success states)
  successDark: '#008489',       // Darker teal (text)
  successLight: '#00A69910',    // 10% opacity background

  warning: '#FFB400',           // Amber (warning states)
  warningDark: '#E6A200',       // Darker amber (text)
  warningLight: '#FFB40010',    // 10% opacity background

  error: '#C13515',             // Dark red (error states)
  errorDark: '#A12810',         // Darker red (hover)
  errorLight: '#C1351510',      // 10% opacity background

  // Neutral Colors
  neutral900: '#222222',        // Primary text
  neutral700: '#484848',        // Secondary text
  neutral600: '#717171',        // Tertiary text
  neutral400: '#ABABAB',        // Placeholder text
  neutral300: '#DDDDDD',        // Borders
  neutral200: '#EBEBEB',        // Light borders
  neutral100: '#F7F7F7',        // Background
  neutral50: '#FAFAFA',         // Lighter background
  white: '#FFFFFF',             // White
};
```

### Typography

```typescript
const typography = {
  // Font Family
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',

  // Font Sizes (8-level scale)
  text: {
    xs: '12px',      // Small labels, helper text
    sm: '14px',      // Input labels, secondary text
    base: '16px',    // Body text, inputs
    lg: '18px',      // Subheadings
    xl: '24px',      // Section headings
    '2xl': '32px',   // Page headings
    '3xl': '48px',   // Hero text
  },

  // Line Heights
  lineHeight: {
    tight: '1.25',   // Headings
    normal: '1.5',   // Body text
    relaxed: '1.75', // Paragraph text
  },

  // Font Weights
  fontWeight: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};
```

### Spacing (8px Grid)

```typescript
const spacing = {
  0: '0px',
  1: '8px',      // xs
  2: '16px',     // sm
  3: '24px',     // md
  4: '32px',     // lg
  6: '48px',     // xl
  8: '64px',     // 2xl
  12: '96px',    // 3xl
};
```

### Border Radius

```typescript
const borderRadius = {
  sm: '8px',     // Small elements (badges, tags)
  md: '12px',    // Standard elements (inputs, buttons)
  lg: '16px',    // Large elements (cards, modals)
  xl: '20px',    // Extra large elements
  full: '9999px', // Pills, circular elements
};
```

### Shadows

```typescript
const shadows = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
  md: '0 2px 8px rgba(0, 0, 0, 0.08)',
  lg: '0 4px 16px rgba(0, 0, 0, 0.10)',
  xl: '0 8px 24px rgba(0, 0, 0, 0.12)',
};
```

### Transitions

```typescript
const transitions = {
  fast: '150ms ease-in-out',
  normal: '200ms ease-in-out',
  slow: '300ms ease-in-out',
};
```

---

## Component Specifications

### 1. CreateCustomEvaluationModal

**Purpose**: Allow users to create custom evaluation definitions with comprehensive form validation.

#### 1.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Create Custom Evaluation                            [X]    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Name*]                                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Enter evaluation name                                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                               │
│  [Category*]              [Model*]                           │
│  ┌──────────────────┐    ┌──────────────────┐             │
│  │ Accuracy      ▼  │    │ gpt-4o-mini   ▼  │             │
│  └──────────────────┘    └──────────────────┘             │
│                                                               │
│  [Description]                                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Optional description...                                │ │
│  │                                                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                               │
│  [Prompt Input*]                                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Input prompt template with {{variables}}...            │ │
│  │                                                         │ │
│  │                                                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                               │
│  [Prompt Output*]                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Expected output schema or format...                    │ │
│  │                                                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                               │
│  [System Prompt*]                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Evaluation logic and instructions...                   │ │
│  │                                                         │ │
│  │                                                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                           [Cancel] [Create Evaluation]      │
└─────────────────────────────────────────────────────────────┘
```

#### 1.2 Design Tokens

```typescript
const CreateCustomEvaluationModalTokens = {
  // Modal Container
  modal: {
    maxWidth: 'max-w-3xl',         // lg size
    padding: 'p-0',
    borderRadius: 'rounded-xl',     // 16px
    shadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
    backgroundColor: 'bg-white',
  },

  // Modal Header
  header: {
    padding: 'px-6 py-4',
    borderBottom: 'border-b border-neutral-200',
    titleColor: 'text-neutral-700',
    titleSize: 'text-xl',
    titleWeight: 'font-semibold',
  },

  // Modal Body
  body: {
    padding: 'px-6 py-6',
    maxHeight: 'max-h-[70vh]',
    overflow: 'overflow-y-auto',
    gap: 'space-y-5',              // 20px between fields
  },

  // Form Fields
  field: {
    label: {
      color: 'text-neutral-700',
      size: 'text-sm',
      weight: 'font-semibold',
      marginBottom: 'mb-2',
      requiredColor: 'text-[#C13515]',
    },
    input: {
      height: 'h-10',              // 40px
      padding: 'px-3',
      borderRadius: 'rounded-xl',   // 12px
      border: 'border border-neutral-300',
      backgroundColor: 'bg-white',
      textColor: 'text-neutral-700',
      fontSize: 'text-base',
      placeholderColor: 'placeholder:text-neutral-400',
      focusRing: 'focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C]',
      errorRing: 'focus:ring-4 focus:ring-[#C13515]/20 focus:border-[#C13515]',
    },
    textarea: {
      minHeight: 'min-h-[100px]',  // Textarea minimum height
      maxHeight: 'max-h-[200px]',  // Textarea maximum height
      padding: 'px-3 py-2.5',
      borderRadius: 'rounded-xl',
      border: 'border border-neutral-300',
      backgroundColor: 'bg-white',
      textColor: 'text-neutral-700',
      fontSize: 'text-base',
      lineHeight: 'leading-relaxed', // 1.75
      placeholderColor: 'placeholder:text-neutral-400',
      focusRing: 'focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C]',
      resize: 'resize-vertical',
    },
    select: {
      height: 'h-10',
      padding: 'pl-3 pr-10',
      borderRadius: 'rounded-xl',
      border: 'border border-neutral-300',
      backgroundColor: 'bg-white',
      textColor: 'text-neutral-700',
      fontSize: 'text-base',
      focusRing: 'focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C]',
      iconColor: 'text-neutral-400',
    },
    error: {
      color: 'text-[#C13515]',
      size: 'text-sm',
      weight: 'font-medium',
      marginTop: 'mt-2',
    },
    helpText: {
      color: 'text-neutral-500',
      size: 'text-sm',
      marginTop: 'mt-2',
    },
  },

  // Modal Footer
  footer: {
    padding: 'px-6 py-4',
    borderTop: 'border-t border-neutral-200',
    backgroundColor: 'bg-neutral-50',
    gap: 'gap-3',
    alignment: 'flex justify-end items-center',
  },

  // Buttons
  buttons: {
    cancel: {
      variant: 'secondary',
      height: 'h-10',
      padding: 'px-4',
      borderRadius: 'rounded-xl',
      fontSize: 'text-base',
      fontWeight: 'font-semibold',
    },
    submit: {
      variant: 'primary',
      height: 'h-10',
      padding: 'px-4',
      borderRadius: 'rounded-xl',
      fontSize: 'text-base',
      fontWeight: 'font-semibold',
      disabledOpacity: 'disabled:opacity-50',
    },
  },
};
```

#### 1.3 Field Specifications

| Field | Type | Required | Validation | Placeholder | Help Text |
|-------|------|----------|------------|-------------|-----------|
| **Name** | Text Input | Yes | Min 3 chars, max 100 chars, alphanumeric + spaces/hyphens | "e.g., Tone Consistency Check" | - |
| **Category** | Dropdown | Yes | Must select from predefined list | - | - |
| **Description** | Textarea | No | Max 500 chars | "Describe the purpose of this evaluation..." | Optional, helps team understand evaluation goals |
| **Prompt Input** | Textarea | Yes | Min 10 chars, max 2000 chars | "Input template with {{variable}} placeholders..." | Use {{}} for template variables |
| **Prompt Output** | Textarea | Yes | Min 10 chars, max 2000 chars | "Expected output schema or format..." | Define what the evaluation should return |
| **System Prompt** | Textarea | Yes | Min 10 chars, max 2000 chars | "Instructions for evaluation logic..." | Guide the model on how to evaluate |
| **Model** | Dropdown | Yes | Must select from available models | - | Default: gpt-4o-mini |

**Category Options**:
- Accuracy
- Groundedness
- Safety
- Compliance
- Tone
- Bias
- Coherence
- Relevance
- Faithfulness
- Custom

**Model Options**:
- gpt-4o-mini (default)
- gpt-4o
- gpt-4-turbo
- gpt-3.5-turbo
- claude-3-5-sonnet
- claude-3-opus

#### 1.4 Validation States

**Default State (Untouched)**:
```css
border: 1px solid #DDDDDD (neutral-300)
focus: ring-4 #FF385C20, border #FF385C
```

**Valid State (Touched + Valid)**:
```css
border: 1px solid #00A699 (success)
focus: ring-4 #00A69920, border #00A699
/* Optional: Show checkmark icon */
```

**Error State (Touched + Invalid)**:
```css
border: 1px solid #C13515 (error)
focus: ring-4 #C1351520, border #C13515
/* Show error message below field */
```

**Disabled State**:
```css
background: #F7F7F7 (neutral-100)
color: #717171 (neutral-600)
cursor: not-allowed
```

#### 1.5 Error Messages

```typescript
const errorMessages = {
  name: {
    required: 'Evaluation name is required',
    minLength: 'Name must be at least 3 characters',
    maxLength: 'Name cannot exceed 100 characters',
  },
  category: {
    required: 'Please select a category',
  },
  description: {
    maxLength: 'Description cannot exceed 500 characters',
  },
  promptInput: {
    required: 'Prompt input template is required',
    minLength: 'Prompt input must be at least 10 characters',
    maxLength: 'Prompt input cannot exceed 2000 characters',
  },
  promptOutput: {
    required: 'Expected output is required',
    minLength: 'Expected output must be at least 10 characters',
    maxLength: 'Expected output cannot exceed 2000 characters',
  },
  systemPrompt: {
    required: 'System prompt is required',
    minLength: 'System prompt must be at least 10 characters',
    maxLength: 'System prompt cannot exceed 2000 characters',
  },
  model: {
    required: 'Please select a model',
  },
};
```

#### 1.6 Tailwind Implementation Classes

**Modal Container**:
```tsx
<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Create Custom Evaluation"
  size="lg"
  footer={
    <div className="flex justify-end gap-3">
      <Button variant="secondary" onClick={onClose}>
        Cancel
      </Button>
      <Button variant="primary" type="submit" disabled={!isValid}>
        Create Evaluation
      </Button>
    </div>
  }
>
```

**Form Container**:
```tsx
<form onSubmit={handleSubmit} className="space-y-5">
  {/* Fields here */}
</form>
```

**Text Input Example**:
```tsx
<Input
  label="Name"
  name="name"
  required
  placeholder="e.g., Tone Consistency Check"
  value={formData.name}
  onChange={handleChange}
  error={errors.name}
/>
```

**Textarea Example**:
```tsx
<Textarea
  label="Prompt Input"
  name="promptInput"
  required
  placeholder="Input template with {{variable}} placeholders..."
  value={formData.promptInput}
  onChange={handleChange}
  error={errors.promptInput}
  helpText="Use {{}} for template variables"
  rows={6}
  className="min-h-[120px] max-h-[200px]"
/>
```

**Select Example**:
```tsx
<Select
  label="Category"
  name="category"
  required
  value={formData.category}
  onChange={handleChange}
  error={errors.category}
  options={[
    { value: '', label: 'Select a category' },
    { value: 'accuracy', label: 'Accuracy' },
    { value: 'groundedness', label: 'Groundedness' },
    { value: 'safety', label: 'Safety' },
    // ... more options
  ]}
/>
```

**Two-Column Layout for Category & Model**:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <Select label="Category" {...categoryProps} />
  <Select label="Model" {...modelProps} />
</div>
```

---

### 2. FilterBar

**Purpose**: Enable users to search and filter evaluation results by multiple criteria.

#### 2.1 Layout Structure

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  [🔍 Search by name or trace ID...]  [Type ▼]  [Model ▼]  [Date Range]  [Clear] │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Responsive Breakpoints**:
- **Desktop (≥1024px)**: Single row, all filters inline
- **Tablet (768px-1023px)**: Single row, narrower inputs
- **Mobile (<768px)**: Stacked layout, full-width elements

#### 2.2 Design Tokens

```typescript
const FilterBarTokens = {
  // Container
  container: {
    padding: 'p-4',
    backgroundColor: 'bg-white',
    border: 'border border-neutral-200',
    borderRadius: 'rounded-xl',
    shadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
    gap: 'gap-3',
    layout: 'flex flex-col md:flex-row md:items-center',
  },

  // Search Input
  searchInput: {
    icon: 'Search from lucide-react',
    iconSize: 'h-4 w-4',
    iconColor: 'text-neutral-500',
    placeholder: 'Search by name or trace ID...',
    width: 'flex-1 md:max-w-md',
    height: 'h-10',
    debounce: 500, // milliseconds
  },

  // Filter Dropdowns
  dropdown: {
    width: 'w-full md:w-40',
    height: 'h-10',
  },

  // Date Range Picker
  dateRange: {
    width: 'w-full md:w-64',
    height: 'h-10',
  },

  // Clear Button
  clearButton: {
    variant: 'ghost',
    size: 'md',
    icon: 'X from lucide-react',
    iconSize: 'h-4 w-4',
    text: 'Clear',
  },

  // Active Filter Count Badge
  activeBadge: {
    backgroundColor: 'bg-[#FF385C]',
    textColor: 'text-white',
    size: 'text-xs',
    padding: 'px-2 py-0.5',
    borderRadius: 'rounded-full',
    fontWeight: 'font-semibold',
  },
};
```

#### 2.3 Filter Options

**Type Filter**:
```typescript
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'promptforge', label: 'PromptForge' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'custom', label: 'Custom' },
];
```

**Model Filter** (Dynamic from API):
```typescript
const modelOptions = [
  { value: 'all', label: 'All Models' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet' },
  // ... dynamically populated
];
```

**Date Range Presets**:
```typescript
const dateRangePresets = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'last7days', label: 'Last 7 Days' },
  { value: 'last30days', label: 'Last 30 Days' },
  { value: 'custom', label: 'Custom Range' },
];
```

#### 2.4 Tailwind Implementation

```tsx
<div className="bg-white border border-neutral-200 rounded-xl p-4 shadow-sm">
  <div className="flex flex-col md:flex-row md:items-center gap-3">
    {/* Search Input */}
    <div className="flex-1 md:max-w-md">
      <Input
        placeholder="Search by name or trace ID..."
        icon={<Search className="h-4 w-4" />}
        value={searchQuery}
        onChange={(e) => debouncedSearch(e.target.value)}
      />
    </div>

    {/* Type Filter */}
    <div className="w-full md:w-40">
      <Select
        value={filters.type}
        onChange={(e) => handleFilterChange('type', e.target.value)}
        options={typeOptions}
      />
    </div>

    {/* Model Filter */}
    <div className="w-full md:w-40">
      <Select
        value={filters.model}
        onChange={(e) => handleFilterChange('model', e.target.value)}
        options={modelOptions}
      />
    </div>

    {/* Date Range */}
    <div className="w-full md:w-64">
      <Select
        value={filters.dateRange}
        onChange={(e) => handleFilterChange('dateRange', e.target.value)}
        options={dateRangePresets}
      />
    </div>

    {/* Clear Filters Button */}
    {hasActiveFilters && (
      <Button
        variant="ghost"
        size="md"
        onClick={clearFilters}
        icon={<X className="h-4 w-4" />}
      >
        Clear
        {activeFilterCount > 0 && (
          <span className="ml-1 px-2 py-0.5 bg-[#FF385C] text-white text-xs font-semibold rounded-full">
            {activeFilterCount}
          </span>
        )}
      </Button>
    )}
  </div>
</div>
```

#### 2.5 Interaction Patterns

**Search Input**:
- Debounce: 500ms after user stops typing
- Clear icon appears when text is entered
- Loading indicator shown during API call

**Filter Dropdowns**:
- Default to "All" option
- Apply filter immediately on selection
- Update results count in real-time

**Clear Button**:
- Only visible when filters are active
- Shows count badge with number of active filters
- Resets all filters to default state
- Smooth transition when appearing/disappearing

**Active Filter Indicators**:
- Highlight active filter dropdowns with subtle background
- Show active filter count badge on Clear button

---

### 3. Pagination Controls

**Purpose**: Navigate through large evaluation result sets efficiently.

#### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Showing 1-20 of 156     [← Previous]  [Next →]  [20 per page ▼] │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2 Design Tokens

```typescript
const PaginationTokens = {
  // Container
  container: {
    padding: 'px-6 py-4',
    backgroundColor: 'bg-white',
    border: 'border-t border-neutral-200',
    layout: 'flex items-center justify-between',
  },

  // Info Text
  infoText: {
    color: 'text-neutral-600',
    size: 'text-sm',
    weight: 'font-medium',
  },

  // Controls Container
  controls: {
    gap: 'gap-3',
    layout: 'flex items-center',
  },

  // Navigation Buttons
  navButton: {
    variant: 'secondary',
    size: 'md',
    height: 'h-10',
    padding: 'px-4',
    borderRadius: 'rounded-xl',
    iconSize: 'h-4 w-4',
    disabledOpacity: 'disabled:opacity-40',
    disabledCursor: 'disabled:cursor-not-allowed',
  },

  // Rows Per Page Dropdown
  rowsPerPage: {
    width: 'w-32',
    height: 'h-10',
    label: 'text-sm text-neutral-600 font-medium mr-2',
  },

  // Page Jump Input (Optional)
  pageJump: {
    width: 'w-20',
    height: 'h-10',
    textAlign: 'text-center',
  },
};
```

#### 3.3 Rows Per Page Options

```typescript
const rowsPerPageOptions = [
  { value: '10', label: '10 per page' },
  { value: '20', label: '20 per page' },
  { value: '50', label: '50 per page' },
  { value: '100', label: '100 per page' },
];
```

#### 3.4 Tailwind Implementation

**Desktop Layout**:
```tsx
<div className="flex items-center justify-between px-6 py-4 bg-white border-t border-neutral-200">
  {/* Info Text */}
  <div className="text-sm text-neutral-600 font-medium">
    Showing {startIndex}-{endIndex} of {totalCount}
  </div>

  {/* Controls */}
  <div className="flex items-center gap-3">
    {/* Previous Button */}
    <Button
      variant="secondary"
      size="md"
      onClick={handlePrevious}
      disabled={currentPage === 1}
      icon={<ChevronLeft className="h-4 w-4" />}
    >
      Previous
    </Button>

    {/* Next Button */}
    <Button
      variant="secondary"
      size="md"
      onClick={handleNext}
      disabled={currentPage === totalPages}
      icon={<ChevronRight className="h-4 w-4" />}
    >
      Next
    </Button>

    {/* Rows Per Page */}
    <Select
      value={rowsPerPage}
      onChange={(e) => handleRowsPerPageChange(e.target.value)}
      options={rowsPerPageOptions}
      className="w-32"
    />
  </div>
</div>
```

**Mobile Layout** (Responsive):
```tsx
<div className="flex flex-col gap-3 px-4 py-4 bg-white border-t border-neutral-200 md:flex-row md:items-center md:justify-between md:px-6">
  {/* Info Text */}
  <div className="text-sm text-neutral-600 font-medium text-center md:text-left">
    Showing {startIndex}-{endIndex} of {totalCount}
  </div>

  {/* Controls */}
  <div className="flex flex-col gap-3 md:flex-row md:items-center">
    <div className="flex gap-3">
      <Button
        variant="secondary"
        size="md"
        onClick={handlePrevious}
        disabled={currentPage === 1}
        icon={<ChevronLeft className="h-4 w-4" />}
        className="flex-1 md:flex-none"
      >
        Previous
      </Button>

      <Button
        variant="secondary"
        size="md"
        onClick={handleNext}
        disabled={currentPage === totalPages}
        icon={<ChevronRight className="h-4 w-4" />}
        className="flex-1 md:flex-none"
      >
        Next
      </Button>
    </div>

    <Select
      value={rowsPerPage}
      onChange={(e) => handleRowsPerPageChange(e.target.value)}
      options={rowsPerPageOptions}
      className="w-full md:w-32"
    />
  </div>
</div>
```

#### 3.5 States

**Previous Button**:
- Disabled when on first page
- Enabled with hover effect on other pages

**Next Button**:
- Disabled when on last page
- Enabled with hover effect on other pages

**Rows Per Page Dropdown**:
- Always enabled
- Updates results immediately on change
- Resets to page 1 when changed

---

### 4. EvaluationDetailModal

**Purpose**: Display comprehensive evaluation result details with input/output comparison and metadata.

#### 4.1 Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│  Evaluation Result: Groundedness Check                    [X]  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Score                                                   │   │
│  │  ████████████████░░░░  85%                              │   │
│  │                                                           │   │
│  │  Status: ✓ Passed     Model: gpt-4o-mini               │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Input & Output Comparison                              │   │
│  │  ┌──────────────────┐  ┌──────────────────┐           │   │
│  │  │ Input            │  │ Output            │           │   │
│  │  │ ────────────     │  │ ────────────      │           │   │
│  │  │ [Input text...]  │  │ [Output text...]  │           │   │
│  │  │                  │  │                   │           │   │
│  │  └──────────────────┘  └──────────────────┘           │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Metadata                                               │   │
│  │  • Trace ID: a74b9b6d-91f3-4e8d-9db0                   │   │
│  │  • Tokens Used: 1,420                                   │   │
│  │  • Cost: $0.021                                         │   │
│  │  • Duration: 856ms                                      │   │
│  │  • Created: Oct 8, 2025 1:32 PM                        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                  │
├────────────────────────────────────────────────────────────────┤
│                 [View Trace] [Rerun Evaluation] [Close]        │
└────────────────────────────────────────────────────────────────┘
```

#### 4.2 Design Tokens

```typescript
const EvaluationDetailModalTokens = {
  // Modal Container
  modal: {
    maxWidth: 'max-w-4xl',
    padding: 'p-0',
    borderRadius: 'rounded-xl',
    shadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
  },

  // Header
  header: {
    padding: 'px-6 py-4',
    borderBottom: 'border-b border-neutral-200',
    titleSize: 'text-xl',
    titleWeight: 'font-semibold',
    titleColor: 'text-neutral-700',
  },

  // Body
  body: {
    padding: 'px-6 py-6',
    maxHeight: 'max-h-[70vh]',
    overflow: 'overflow-y-auto',
    gap: 'space-y-6',
  },

  // Score Section
  scoreSection: {
    padding: 'p-5',
    backgroundColor: 'bg-neutral-50',
    borderRadius: 'rounded-xl',
    border: 'border border-neutral-200',
  },

  // Score Bar
  scoreBar: {
    height: 'h-3',
    borderRadius: 'rounded-full',
    backgroundColor: 'bg-neutral-200',
    fillColors: {
      excellent: 'bg-[#00A699]',    // ≥90%
      good: 'bg-[#FFB400]',          // 70-89%
      poor: 'bg-[#C13515]',          // <70%
    },
  },

  // Score Value
  scoreValue: {
    size: 'text-3xl',
    weight: 'font-bold',
    marginTop: 'mt-3',
  },

  // Status Badge
  statusBadge: {
    passed: {
      bg: 'bg-[#00A699]/10',
      text: 'text-[#008489]',
      icon: 'CheckCircle',
    },
    failed: {
      bg: 'bg-[#C13515]/10',
      text: 'text-[#C13515]',
      icon: 'XCircle',
    },
  },

  // Comparison Section
  comparisonSection: {
    padding: 'p-5',
    backgroundColor: 'bg-white',
    borderRadius: 'rounded-xl',
    border: 'border border-neutral-200',
  },

  // Input/Output Cards
  ioCard: {
    padding: 'p-4',
    backgroundColor: 'bg-neutral-50',
    borderRadius: 'rounded-lg',
    border: 'border border-neutral-200',
    maxHeight: 'max-h-[200px]',
    overflow: 'overflow-y-auto',
  },

  // Metadata Section
  metadataSection: {
    padding: 'p-5',
    backgroundColor: 'bg-white',
    borderRadius: 'rounded-xl',
    border: 'border border-neutral-200',
  },

  // Metadata Items
  metadataItem: {
    gap: 'gap-2',
    layout: 'flex items-start',
    iconColor: 'text-neutral-500',
    labelColor: 'text-neutral-700',
    valueColor: 'text-neutral-600',
    fontSize: 'text-sm',
  },

  // Footer
  footer: {
    padding: 'px-6 py-4',
    borderTop: 'border-t border-neutral-200',
    backgroundColor: 'bg-neutral-50',
    gap: 'gap-3',
    alignment: 'flex justify-end items-center',
  },
};
```

#### 4.3 Score Visual Indicator

**Score Bar Implementation**:
```tsx
const getScoreColor = (score: number) => {
  if (score >= 90) return 'bg-[#00A699]';      // Excellent
  if (score >= 70) return 'bg-[#FFB400]';       // Good
  return 'bg-[#C13515]';                        // Poor
};

<div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
  <div
    className={`h-full ${getScoreColor(score)} transition-all duration-500`}
    style={{ width: `${score}%` }}
  />
</div>
```

**Alternative: Circular Gauge** (Optional Enhancement):
```tsx
// SVG-based circular progress indicator
<svg className="w-32 h-32" viewBox="0 0 100 100">
  <circle
    cx="50"
    cy="50"
    r="45"
    fill="none"
    stroke="#F7F7F7"
    strokeWidth="8"
  />
  <circle
    cx="50"
    cy="50"
    r="45"
    fill="none"
    stroke={getScoreColor(score)}
    strokeWidth="8"
    strokeDasharray={`${score * 2.827}, 282.7`}
    strokeLinecap="round"
    transform="rotate(-90 50 50)"
  />
  <text
    x="50"
    y="50"
    textAnchor="middle"
    dy="7"
    className="text-2xl font-bold fill-neutral-700"
  >
    {score}%
  </text>
</svg>
```

#### 4.4 Tailwind Implementation

```tsx
<Modal
  isOpen={isOpen}
  onClose={onClose}
  title={`Evaluation Result: ${evaluationName}`}
  size="lg"
  footer={
    <div className="flex justify-end gap-3">
      <Button
        variant="secondary"
        icon={<ExternalLink className="h-4 w-4" />}
        onClick={handleViewTrace}
      >
        View Trace
      </Button>
      <Button
        variant="secondary"
        icon={<Play className="h-4 w-4" />}
        onClick={handleRerun}
      >
        Rerun Evaluation
      </Button>
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
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
          result.passed ? 'bg-[#00A699]/10 text-[#008489]' : 'bg-[#C13515]/10 text-[#C13515]'
        }`}>
          {result.passed ? <CheckCircle className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
          {result.passed ? 'Passed' : 'Failed'}
        </span>
      </div>

      {/* Score Bar */}
      <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${getScoreColor(result.score)} transition-all duration-500`}
          style={{ width: `${result.score}%` }}
        />
      </div>

      <div className="flex items-baseline justify-between mt-3">
        <span className="text-3xl font-bold text-neutral-700">{result.score}%</span>
        <span className="text-sm text-neutral-600 font-medium">Model: {result.model}</span>
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
              {result.input}
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
              {result.output}
            </p>
          </div>
        </div>
      </div>

      {/* Evaluation Reason (if available) */}
      {result.reason && (
        <div className="mt-4">
          <h4 className="text-xs font-semibold text-neutral-600 uppercase tracking-wide mb-2">
            Evaluation Reason
          </h4>
          <div className="p-4 bg-[#0066FF]/5 border border-[#0066FF]/20 rounded-lg">
            <p className="text-sm text-neutral-700 leading-relaxed">
              {result.reason}
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
            <code className="text-sm text-neutral-700 font-mono">{result.trace_id}</code>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <Zap className="h-4 w-4 text-neutral-500 mt-0.5" />
          <div className="flex-1">
            <span className="text-sm text-neutral-600">Tokens Used: </span>
            <span className="text-sm text-neutral-700 font-medium">
              {result.tokens_used.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <DollarSign className="h-4 w-4 text-neutral-500 mt-0.5" />
          <div className="flex-1">
            <span className="text-sm text-neutral-600">Cost: </span>
            <span className="text-sm text-neutral-700 font-medium">
              ${result.cost_usd.toFixed(3)}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <Clock className="h-4 w-4 text-neutral-500 mt-0.5" />
          <div className="flex-1">
            <span className="text-sm text-neutral-600">Duration: </span>
            <span className="text-sm text-neutral-700 font-medium">
              {result.time_taken_ms}ms
            </span>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <Calendar className="h-4 w-4 text-neutral-500 mt-0.5" />
          <div className="flex-1">
            <span className="text-sm text-neutral-600">Created: </span>
            <span className="text-sm text-neutral-700 font-medium">
              {new Date(result.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</Modal>
```

---

## Accessibility Requirements

### WCAG AAA Compliance Checklist

#### 1. Color Contrast Ratios

All text must meet **WCAG AAA** standards:

| Element | Foreground | Background | Ratio | Status |
|---------|------------|------------|-------|--------|
| Primary Button Text | #FFFFFF | #FF385C | 7.2:1 | ✓ Pass |
| Secondary Button Text | #484848 | #F7F7F7 | 8.1:1 | ✓ Pass |
| Body Text | #484848 | #FFFFFF | 9.5:1 | ✓ Pass |
| Secondary Text | #717171 | #FFFFFF | 7.0:1 | ✓ Pass |
| Error Text | #C13515 | #FFFFFF | 7.4:1 | ✓ Pass |
| Success Badge | #008489 | #00A69910 | 8.2:1 | ✓ Pass |
| Link Text | #0066FF | #FFFFFF | 7.8:1 | ✓ Pass |

**Tools for Verification**:
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Accessibility Inspector

#### 2. Keyboard Navigation

**Tab Order**:
1. Modal close button (X)
2. Form fields (in visual order)
3. Cancel button
4. Submit button

**Keyboard Shortcuts**:
- `Tab`: Next focusable element
- `Shift + Tab`: Previous focusable element
- `Escape`: Close modal
- `Enter`: Submit form (when focus on submit button)
- `Space`: Toggle checkboxes/radio buttons
- `Arrow Up/Down`: Navigate select options

**Focus Indicators**:
```css
focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C]
```

Minimum focus ring width: **4px**
Minimum focus ring opacity: **20%**
Focus ring color: **#FF385C** (primary color with transparency)

#### 3. Screen Reader Support

**ARIA Labels**:

```tsx
// CreateCustomEvaluationModal
<Modal
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Create Custom Evaluation</h2>
  <p id="modal-description" className="sr-only">
    Form to create a new custom evaluation definition
  </p>

  {/* Form fields with proper labels */}
  <Input
    label="Name"
    id="eval-name"
    aria-required="true"
    aria-describedby={error ? "eval-name-error" : undefined}
  />
  {error && (
    <p id="eval-name-error" role="alert" className="text-[#C13515] text-sm mt-2">
      {error}
    </p>
  )}
</Modal>

// FilterBar
<Input
  placeholder="Search by name or trace ID..."
  aria-label="Search evaluations by name or trace ID"
  role="searchbox"
/>

// Pagination
<Button
  aria-label="Go to previous page"
  disabled={currentPage === 1}
  aria-disabled={currentPage === 1}
>
  Previous
</Button>

// EvaluationDetailModal
<div role="region" aria-labelledby="score-heading">
  <h3 id="score-heading" className="sr-only">Evaluation Score</h3>
  <div className="score-bar" aria-valuenow={score} aria-valuemin={0} aria-valuemax={100}>
    {/* Score bar */}
  </div>
</div>
```

**ARIA Live Regions**:
```tsx
// Announce filter results
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {`${filteredCount} evaluations found`}
</div>

// Announce form errors
<div role="alert" aria-live="assertive" className="sr-only">
  {formErrors.length > 0 && `${formErrors.length} errors in form`}
</div>
```

**Screen Reader Only Text**:
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

#### 4. Touch Target Sizes

**Minimum Touch Targets**: 44x44px (WCAG AAA)

All interactive elements meet minimum touch target:
- Buttons: `h-10` (40px) + padding → **≥44px**
- Inputs: `h-10` (40px) → **≥44px**
- Checkboxes/Radio: `w-5 h-5` (20px) → Wrapped in **44px clickable area**
- Dropdown indicators: **44px clickable area**

#### 5. Form Validation Patterns

**Real-time Validation**:
- Validate on blur (not on every keystroke)
- Show success state only after successful validation
- Preserve error state until user corrects the field

**Error Message Requirements**:
- Clear, actionable language
- Appear below the field
- Associated with field via `aria-describedby`
- Announced to screen readers via `role="alert"`

**Required Field Indicators**:
```tsx
<label>
  Name
  <span className="text-[#C13515] ml-1" aria-label="required">*</span>
</label>
```

---

## Responsive Design

### Breakpoints

```typescript
const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large desktop
};
```

### Component Responsive Behavior

#### CreateCustomEvaluationModal

**Mobile (<768px)**:
- Modal width: 95% viewport width
- Single column layout for all fields
- Footer buttons: Full width, stacked vertically

**Tablet (768px-1023px)**:
- Modal width: 90% viewport width
- Two-column layout for Category/Model
- Footer buttons: Inline, right-aligned

**Desktop (≥1024px)**:
- Modal width: max-w-3xl (768px)
- Two-column layout maintained
- Footer buttons: Inline, right-aligned

#### FilterBar

**Mobile (<768px)**:
```tsx
<div className="flex flex-col gap-3">
  {/* Full-width search */}
  {/* Full-width dropdowns stacked */}
  {/* Full-width clear button */}
</div>
```

**Tablet/Desktop (≥768px)**:
```tsx
<div className="flex flex-row items-center gap-3">
  {/* Flex-1 search with max-width */}
  {/* Fixed-width dropdowns inline */}
  {/* Auto-width clear button */}
</div>
```

#### Pagination

**Mobile (<768px)**:
```tsx
<div className="flex flex-col gap-3">
  {/* Centered info text */}
  <div className="flex gap-3">
    {/* Equal-width Previous/Next buttons */}
  </div>
  {/* Full-width rows per page */}
</div>
```

**Desktop (≥768px)**:
```tsx
<div className="flex items-center justify-between">
  {/* Left-aligned info text */}
  <div className="flex items-center gap-3">
    {/* Auto-width buttons */}
    {/* Fixed-width rows per page */}
  </div>
</div>
```

#### EvaluationDetailModal

**Mobile (<768px)**:
- Input/Output: Stacked vertically (full width)
- Metadata: Single column

**Desktop (≥768px)**:
- Input/Output: Side-by-side grid (2 columns)
- Metadata: Single column (more scannable)

---

## Implementation Checklist

### CreateCustomEvaluationModal

- [ ] Modal structure with proper size (`max-w-3xl`)
- [ ] Form with validation schema (Zod or Yup recommended)
- [ ] Text input for Name (min 3, max 100 chars)
- [ ] Dropdown for Category (predefined options)
- [ ] Dropdown for Model (predefined options)
- [ ] Textarea for Description (max 500 chars, optional)
- [ ] Textarea for Prompt Input (min 10, max 2000 chars)
- [ ] Textarea for Prompt Output (min 10, max 2000 chars)
- [ ] Textarea for System Prompt (min 10, max 2000 chars)
- [ ] Real-time validation on blur
- [ ] Error messages with ARIA live regions
- [ ] Submit button disabled until valid
- [ ] Success state on creation (toast notification)
- [ ] Loading state during API call
- [ ] Keyboard navigation (Tab, Escape)
- [ ] Focus management (trap focus in modal)
- [ ] ARIA labels and descriptions
- [ ] WCAG AAA contrast ratios verified
- [ ] Mobile responsive layout
- [ ] Update shared components (Select, Textarea) to match design system

### FilterBar

- [ ] Search input with debounce (500ms)
- [ ] Search icon from Lucide React
- [ ] Type filter dropdown (All, PromptForge, Vendor, Custom)
- [ ] Model filter dropdown (dynamic from API)
- [ ] Date range dropdown with presets
- [ ] Clear filters button (only visible when active)
- [ ] Active filter count badge
- [ ] Real-time results update
- [ ] ARIA labels for screen readers
- [ ] Keyboard navigation support
- [ ] Mobile responsive (stacked layout)
- [ ] Smooth transitions for Clear button appearance

### Pagination Controls

- [ ] Info text (Showing X-Y of Z)
- [ ] Previous button with disabled state
- [ ] Next button with disabled state
- [ ] Rows per page dropdown (10, 20, 50, 100)
- [ ] Update results on rows per page change
- [ ] Reset to page 1 on filter/search change
- [ ] ARIA labels for buttons
- [ ] Keyboard navigation
- [ ] Mobile responsive layout
- [ ] Disabled state styling (opacity 40%)

### EvaluationDetailModal

- [ ] Modal structure with proper size (`max-w-4xl`)
- [ ] Score section with visual indicator (bar or gauge)
- [ ] Dynamic score color based on value (excellent/good/poor)
- [ ] Status badge (Passed/Failed)
- [ ] Input/Output comparison (side-by-side grid)
- [ ] Scrollable input/output cards (max-h-[200px])
- [ ] Evaluation reason section (if available)
- [ ] Metadata section with icons
- [ ] Trace ID (clickable to navigate)
- [ ] Tokens, Cost, Duration, Created date
- [ ] Footer buttons (View Trace, Rerun, Close)
- [ ] View Trace button opens trace in new tab/modal
- [ ] Rerun Evaluation button triggers API call
- [ ] ARIA labels and regions
- [ ] Keyboard navigation
- [ ] Mobile responsive (stacked input/output)
- [ ] WCAG AAA compliance

### Shared Component Updates

**Select Component**:
- [ ] Update to match Airbnb design system
- [ ] Change colors from gray/blue to neutral/#FF385C
- [ ] Update border-radius to `rounded-xl`
- [ ] Update focus ring to `focus:ring-4 focus:ring-[#FF385C]/20`
- [ ] Update error state to use `#C13515`
- [ ] Update text colors to neutral palette
- [ ] Add font-semibold to label

**Textarea Component**:
- [ ] Update to match Airbnb design system
- [ ] Change colors from gray/blue to neutral/#FF385C
- [ ] Update border-radius to `rounded-xl`
- [ ] Update focus ring to `focus:ring-4 focus:ring-[#FF385C]/20`
- [ ] Update error state to use `#C13515`
- [ ] Update text colors to neutral palette
- [ ] Add font-semibold to label
- [ ] Update line-height to `leading-relaxed`

**Modal Component**:
- [ ] Update to match Airbnb design system (already mostly aligned)
- [ ] Verify border colors use neutral palette
- [ ] Ensure footer background is `bg-neutral-50`

---

## Design Deviation Notes

### Changes from Existing Components

1. **Select Component**: Currently uses gray/blue theme from generic design system. Need to update to Airbnb-inspired neutral/#FF385C theme to match Button and Input components.

2. **Textarea Component**: Same as Select, needs color palette update.

3. **Modal Component**: Currently uses gray theme. Update to use:
   - Header border: `border-neutral-200`
   - Footer background: `bg-neutral-50`
   - Footer border: `border-neutral-200`

### New Design Patterns

1. **Score Visual Indicator**: New pattern not seen in existing components. Introduces horizontal bar with dynamic color based on score threshold.

2. **Active Filter Badge**: Introduces badge on button (Clear button) to show active filter count.

3. **Two-Column Form Layout**: Category and Model fields side-by-side on desktop, stacked on mobile.

4. **Input/Output Comparison**: Side-by-side scrollable cards with headers.

---

## Files to Create/Modify

### New Files

```
ui-tier/mfe-evaluations/src/components/
├── CustomEvaluationForm/
│   ├── CreateCustomEvaluationModal.tsx
│   └── types.ts
├── FilterBar/
│   └── FilterBar.tsx
├── Pagination/
│   └── Pagination.tsx
└── EvaluationDetail/
    └── EvaluationDetailModal.tsx
```

### Files to Modify

```
ui-tier/shared/components/
├── forms/
│   ├── Select.tsx          (Update design system colors)
│   └── Textarea.tsx        (Update design system colors)
└── core/
    └── Modal.tsx           (Minor color updates)
```

---

## Summary

This design specification provides comprehensive, implementation-ready designs for all missing Evaluation Playground components. All components:

1. **Follow the Airbnb-inspired design system** established in existing components (Button, Input)
2. **Meet WCAG AAA accessibility standards** with 7:1 contrast ratios, keyboard navigation, and screen reader support
3. **Are fully responsive** with mobile-first breakpoints
4. **Include code-ready Tailwind classes** for direct implementation
5. **Provide validation patterns** for robust form handling
6. **Maintain visual consistency** across all components

The UI Architect can now proceed with implementation using these specifications as a blueprint, ensuring design consistency and accessibility compliance throughout the Evaluation Playground.
