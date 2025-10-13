# Modal Design System - PromptForge

## Overview

The PromptForge modal design system is inspired by Airbnb's design philosophy, emphasizing generous whitespace, clear visual hierarchy, and intuitive interactions. All modals use React Portals to escape stacking contexts, ensuring proper z-index handling and accessibility.

**Design Philosophy:**
- Generous whitespace creates breathing room and improves readability
- Soft, layered shadows provide depth without being heavy
- Rounded corners (16px/1rem) create a modern, friendly aesthetic
- Backdrop blur focuses user attention on the modal content
- Inline styles for critical positioning ensure consistency
- Keyboard and screen reader accessible by default

## Core Principles

### 1. Generous Whitespace and Breathing Room
Content should never feel cramped. Use consistent spacing throughout:
- Modal padding: `3rem` (48px)
- Section gaps: `2rem` (32px)
- Element gaps: `1rem` to `1.5rem` (16px-24px)

### 2. Clear Visual Hierarchy
- Headers are prominent with `2rem 3rem` padding
- Sections use borders and backgrounds to create distinct content areas
- Typography scales from `text-2xl` headers to `text-xs` metadata

### 3. Rounded Corners and Soft Shadows
- Primary border radius: `1rem` (16px) for modal container
- Section border radius: `rounded-2xl` (18px)
- Layered shadows create depth: outer shadow + inner shadow

### 4. Accessible and Keyboard-Friendly
- Semantic HTML with proper ARIA attributes
- Keyboard navigation with ESC to close
- Focus management and screen reader support
- Interactive elements have visible hover/focus states

### 5. Portal-Based Rendering
All modals render to `document.body` using React Portals to:
- Escape parent stacking contexts
- Ensure consistent z-index behavior
- Prevent CSS isolation issues
- Enable full-screen overlays

## Layout Specifications

### Modal Container

The outermost container establishes the modal's positioning and scrolling behavior:

```tsx
<div
  style={{
    position: 'fixed',
    inset: 0,
    zIndex: 9999,
    overflowY: 'auto'
  }}
>
```

**Key Properties:**
- `position: fixed` - Locks modal to viewport
- `inset: 0` - Full screen coverage (top/right/bottom/left: 0)
- `zIndex: 9999` - Ensures modal appears above all content
- `overflowY: auto` - Allows scrolling for tall content

### Backdrop

The backdrop dims the background and provides click-to-close functionality:

```tsx
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
```

**Key Properties:**
- `backgroundColor: rgba(0, 0, 0, 0.6)` - 60% black overlay
- `backdropFilter: blur(8px)` - Gaussian blur for focus effect
- `onClick={onClose}` - Click outside to dismiss
- `aria-hidden="true"` - Hide from screen readers

### Modal Centering Wrapper

Centers the modal content vertically and horizontally:

```tsx
<div style={{
  display: 'flex',
  minHeight: '100%',
  alignItems: 'flex-start',
  justifyContent: 'center',
  padding: '3rem 1rem 2rem 1rem'
}}>
```

**Key Properties:**
- `alignItems: flex-start` - Modals appear near top, not vertically centered
- `padding: 3rem 1rem 2rem 1rem` - Generous top padding (48px), minimal side padding for mobile

### Modal Content Box

The main content container with shadows and rounded corners:

```tsx
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
```

**Key Properties:**
- `maxWidth: 56rem` (896px) - Wide enough for content, narrow enough for readability
- `borderRadius: 1rem` (16px) - Soft, rounded corners
- `boxShadow` - Layered shadow for depth:
  - Outer: `0 20px 40px -8px rgba(0, 0, 0, 0.15)`
  - Inner: `0 8px 16px -4px rgba(0, 0, 0, 0.08)`
- `maxHeight: 90vh` - Prevents modal from exceeding viewport
- `overflow: hidden` - Ensures rounded corners clip content

## Spacing Standards

### Header Spacing
```tsx
style={{ padding: '2rem 3rem' }}
```
- **Vertical:** `2rem` (32px) top and bottom
- **Horizontal:** `3rem` (48px) left and right
- **Purpose:** Creates generous space around title and close button

### Content Padding
```tsx
style={{ padding: '3rem' }}
```
- **All sides:** `3rem` (48px)
- **Purpose:** Main scrollable content area padding

### Section Spacing
```tsx
style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}
```
- **Gap between sections:** `2rem` (32px)
- **Purpose:** Clear separation between major content blocks

### Section Header Padding
```tsx
style={{ padding: '1.5rem 2rem' }}
```
- **Vertical:** `1.5rem` (24px)
- **Horizontal:** `2rem` (32px)
- **Purpose:** Clickable header for collapsible sections

### Section Content Padding
```tsx
style={{ padding: '2rem' }}
```
- **All sides:** `2rem` (32px)
- **Purpose:** Content area inside expanded sections

### InfoItem Spacing
```tsx
style={{
  display: 'flex',
  alignItems: 'baseline',
  gap: '2rem',
  padding: '0.75rem 0'
}}
```
- **Gap between label and value:** `2rem` (32px)
- **Vertical padding:** `0.75rem` (12px) top and bottom
- **Purpose:** Comfortable spacing for label-value pairs

### Grid Gaps
```tsx
// Two-column grid
style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '3rem 4rem' }}
```
- **Row gap:** `3rem` (48px) between rows
- **Column gap:** `4rem` (64px) between columns
- **Purpose:** Generous breathing room in overview layouts

## Border and Shadow Standards

### Section Borders
```tsx
className="border-2 border-neutral-300 rounded-2xl overflow-hidden shadow-md bg-white"
```
- **Border width:** `2px` (border-2)
- **Border color:** `neutral-300` (#d4d4d4)
- **Border radius:** `rounded-2xl` (18px)
- **Shadow:** `shadow-md` (medium drop shadow)

### Header Border
```tsx
className="flex items-center justify-between border-b border-neutral-200"
```
- **Border position:** Bottom only
- **Border width:** `1px` (border)
- **Border color:** `neutral-200` (#e5e5e5)

### Code Block Styling
```tsx
className="bg-neutral-50 border border-neutral-200 rounded-xl p-6"
```
- **Background:** `neutral-50` (#fafafa)
- **Border:** `1px solid neutral-200` (#e5e5e5)
- **Border radius:** `rounded-xl` (12px)
- **Padding:** `1.5rem` (24px)

### Error Messages
```tsx
className="bg-red-50 border border-red-200 rounded-xl p-6"
```
- **Background:** `red-50` (#fef2f2)
- **Border:** `1px solid red-200` (#fecaca)
- **Border radius:** `rounded-xl` (12px)
- **Text color:** `red-700` (#b91c1c)

## Component Patterns

### Section Component (Collapsible)

A reusable collapsible section with consistent styling:

```tsx
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
      {isExpanded && (
        <div className="bg-white" style={{ padding: '2rem' }}>
          {children}
        </div>
      )}
    </div>
  );
};
```

**Usage:**
```tsx
<Section
  title="Overview"
  isExpanded={expandedSections.overview}
  onToggle={() => toggleSection('overview')}
>
  {/* Section content here */}
</Section>
```

**Features:**
- Clickable header with chevron indicator
- Smooth hover state transition (200ms)
- ARIA `aria-expanded` for accessibility
- Conditional rendering of content
- Consistent padding and styling

### InfoItem Component (Label-Value Pairs)

Displays label-value pairs with horizontal layout:

```tsx
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
```

**Usage:**
```tsx
<InfoItem label="Project" value={trace.project_name} />
<InfoItem label="Duration" value={`${duration}ms`} />
<InfoItem label="Total Cost" value={`$${cost.toFixed(4)}`} />
```

**Features:**
- Fixed-width label (140px) for alignment
- Flexible value column with word wrapping
- Baseline alignment for text
- Semantic HTML (`<dt>` and `<dd>`)

### Code Block with Copy Button

Displays formatted code/JSON with a copy-to-clipboard button:

```tsx
const [copiedField, setCopiedField] = useState<string | null>(null);

const copyToClipboard = async (text: string, field: string) => {
  try {
    await navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  } catch (err) {
    console.error('Failed to copy:', err);
  }
};

// In render:
<div>
  <div className="flex items-center justify-between mb-4">
    <label className="text-sm font-medium text-neutral-700">Input Data</label>
    <button
      onClick={() => copyToClipboard(JSON.stringify(data, null, 2), 'input')}
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
    {JSON.stringify(data, null, 2)}
  </pre>
</div>
```

**Features:**
- Visual feedback when copied (check icon for 2 seconds)
- Smooth hover state on button
- Scrollable code block with max height
- Monospace font at `text-xs`

### Interactive Close Button

Standard close button for modal headers:

```tsx
<button
  onClick={onClose}
  className="text-neutral-500 hover:text-neutral-700 transition-all duration-200 rounded-xl p-2.5 hover:bg-neutral-100"
  aria-label="Close modal"
>
  <X className="h-5 w-5" />
</button>
```

**Features:**
- Icon-only button with accessible label
- Color and background hover states
- `rounded-xl` for soft corners
- Standard 20px icon size

### Error Display Pattern

Consistent error message styling:

```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
    {error}
  </div>
)}
```

**Inline Error (within sections):**
```tsx
<div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
  <p className="text-sm font-medium text-red-900">Error: {errorType}</p>
  <p className="text-sm text-red-700 mt-2">{errorMessage}</p>
</div>
```

### Loading State Pattern

Centered loading indicator:

```tsx
{loading && (
  <div className="flex items-center justify-center py-12">
    <div className="text-neutral-600">Loading trace details...</div>
  </div>
)}
```

## Typography Standards

### Modal Title
```tsx
<h2 className="text-2xl font-semibold text-neutral-900">Trace Details</h2>
```
- **Size:** `text-2xl` (24px)
- **Weight:** `font-semibold` (600)
- **Color:** `neutral-900` (#171717)

### Section Headers
```tsx
<h3 className="text-base font-semibold text-neutral-900">{title}</h3>
```
- **Size:** `text-base` (16px)
- **Weight:** `font-semibold` (600)
- **Color:** `neutral-900` (#171717)

### Labels
```tsx
<label className="text-sm font-medium text-neutral-700">Input Data</label>
```
- **Size:** `text-sm` (14px)
- **Weight:** `font-medium` (500)
- **Color:** `neutral-700` (#404040)

### Body Text
```tsx
<span className="text-sm text-neutral-900">Content here</span>
```
- **Size:** `text-sm` (14px)
- **Weight:** `font-normal` (400)
- **Color:** `neutral-900` (#171717)

### Secondary Text
```tsx
<span className="text-sm text-neutral-600">Secondary info</span>
```
- **Size:** `text-sm` (14px)
- **Color:** `neutral-600` (#525252)

### Monospace/Code
```tsx
<code className="text-xs font-mono text-neutral-700">trace-id-123</code>
```
- **Size:** `text-xs` (12px)
- **Font:** `font-mono` (monospace)
- **Color:** `neutral-700` (#404040)

## Accessibility Guidelines

### ARIA Attributes Required

**Modal Container:**
```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Modal Title</h2>
</div>
```

**Close Button:**
```tsx
<button
  onClick={onClose}
  aria-label="Close modal"
>
  <X />
</button>
```

**Collapsible Sections:**
```tsx
<button
  onClick={onToggle}
  aria-expanded={isExpanded}
  aria-controls={sectionId}
>
```

**Backdrop:**
```tsx
<div
  onClick={onClose}
  aria-hidden="true"
/>
```

### Keyboard Navigation

**Required Keyboard Interactions:**
- `ESC` - Close modal
- `Tab` / `Shift+Tab` - Navigate interactive elements
- `Enter` / `Space` - Activate buttons
- Focus should trap within modal when open

**Implementation:**
```tsx
useEffect(() => {
  if (!isOpen) return;

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [isOpen, onClose]);
```

### Focus Management

**Focus Modal on Open:**
```tsx
useEffect(() => {
  if (isOpen) {
    const modalElement = document.getElementById('modal-container');
    modalElement?.focus();
  }
}, [isOpen]);
```

**Return Focus on Close:**
```tsx
const previousFocusRef = useRef<HTMLElement | null>(null);

useEffect(() => {
  if (isOpen) {
    previousFocusRef.current = document.activeElement as HTMLElement;
  } else if (previousFocusRef.current) {
    previousFocusRef.current.focus();
  }
}, [isOpen]);
```

### Screen Reader Considerations

- Use semantic HTML (`<header>`, `<section>`, `<dt>`, `<dd>`)
- Provide descriptive button labels
- Mark decorative elements with `aria-hidden="true"`
- Ensure color is not the only means of conveying information
- Test with screen readers (NVDA, JAWS, VoiceOver)

## Color Palette

### Neutrals
- **neutral-50:** `#fafafa` - Light backgrounds
- **neutral-100:** `#f5f5f5` - Hover backgrounds
- **neutral-200:** `#e5e5e5` - Borders
- **neutral-300:** `#d4d4d4` - Strong borders
- **neutral-500:** `#737373` - Icons
- **neutral-600:** `#525252` - Secondary text
- **neutral-700:** `#404040` - Labels
- **neutral-900:** `#171717` - Primary text

### Status Colors
- **red-50:** `#fef2f2` - Error background
- **red-200:** `#fecaca` - Error border
- **red-700:** `#b91c1c` - Error text
- **red-900:** `#7f1d1d` - Error title

- **green-50:** `#f0fdf4` - Success background
- **green-700:** `#15803d` - Success text

- **yellow-50:** `#fefce8` - Warning background
- **yellow-700:** `#a16207` - Warning text

## Implementation Checklist

### Modal Setup
- [ ] Import `createPortal` from 'react-dom'
- [ ] Render modal using `createPortal(modalContent, document.body)`
- [ ] Use fixed positioning with `inset: 0` and `zIndex: 9999`
- [ ] Add backdrop with 60% black overlay and 8px blur
- [ ] Apply exact spacing values from this document

### Modal Structure
- [ ] Fixed header with `padding: 2rem 3rem`
- [ ] Scrollable content area with `padding: 3rem`
- [ ] Content sections with `gap: 2rem`
- [ ] Max width of `56rem` (896px)
- [ ] Max height of `90vh`
- [ ] Border radius of `1rem` (16px)
- [ ] Layered box shadow as specified

### Accessibility
- [ ] Add `role="dialog"` and `aria-modal="true"`
- [ ] Provide `aria-labelledby` referencing title ID
- [ ] Include ESC key handler to close modal
- [ ] Add `aria-label` to close button
- [ ] Mark backdrop as `aria-hidden="true"`
- [ ] Ensure all interactive elements are keyboard accessible
- [ ] Test with screen reader

### Visual Design
- [ ] Use `border-2 border-neutral-300` for sections
- [ ] Apply `rounded-2xl` to section containers
- [ ] Use `shadow-md` for section shadows
- [ ] Follow typography standards (text-2xl for title, etc.)
- [ ] Implement hover states with 200ms transitions
- [ ] Use consistent color palette

### Interactions
- [ ] Click backdrop to close
- [ ] Close button in top-right corner
- [ ] Collapsible sections with chevron indicators
- [ ] Copy-to-clipboard functionality with visual feedback
- [ ] Loading and error states

## Code Examples

### Complete Modal Structure

```tsx
import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  // ESC key handler
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

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
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          style={{
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
          }}
        >
          {/* Fixed Header */}
          <div
            className="flex items-center justify-between border-b border-neutral-200 bg-white rounded-t-2xl sticky top-0 z-10"
            style={{ padding: '2rem 3rem' }}
          >
            <h2 id="modal-title" className="text-2xl font-semibold text-neutral-900">
              {title}
            </h2>
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
            {children}
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
```

### Section Component (Full Implementation)

```tsx
import { ChevronDown, ChevronRight } from 'lucide-react';

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
      {isExpanded && (
        <div className="bg-white" style={{ padding: '2rem' }}>
          {children}
        </div>
      )}
    </div>
  );
};

// Usage with state management
const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
  overview: true,
  details: false,
  metadata: false,
});

const toggleSection = (section: string) => {
  setExpandedSections((prev) => ({
    ...prev,
    [section]: !prev[section],
  }));
};

// In render:
<Section
  title="Overview"
  isExpanded={expandedSections.overview}
  onToggle={() => toggleSection('overview')}
>
  {/* Content here */}
</Section>
```

### InfoItem Component (Full Implementation)

```tsx
interface InfoItemProps {
  label: string;
  value: string;
}

const InfoItem: React.FC<InfoItemProps> = ({ label, value }) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'baseline',
      gap: '2rem',
      padding: '0.75rem 0'
    }}>
      <dt
        className="text-sm font-medium text-neutral-600"
        style={{ minWidth: '140px', flexShrink: 0 }}
      >
        {label}:
      </dt>
      <dd
        className="text-sm text-neutral-900 font-normal break-words"
        style={{ flex: 1 }}
      >
        {value}
      </dd>
    </div>
  );
};

// Usage in two-column grid:
<div style={{
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: '3rem 4rem'
}}>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
    <InfoItem label="Project" value="My Project" />
    <InfoItem label="Environment" value="Production" />
    <InfoItem label="Model" value="GPT-4" />
  </div>
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
    <InfoItem label="Duration" value="1,234ms" />
    <InfoItem label="Tokens" value="5,000" />
    <InfoItem label="Cost" value="$0.0500" />
  </div>
</div>
```

### Code Block with Copy Button (Full Implementation)

```tsx
import { Copy, Check } from 'lucide-react';

const CodeBlockWithCopy: React.FC<{ data: any; label: string; fieldId: string }> = ({
  data,
  label,
  fieldId
}) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const jsonString = JSON.stringify(data, null, 2);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <label className="text-sm font-medium text-neutral-700">{label}</label>
        <button
          onClick={() => copyToClipboard(jsonString, fieldId)}
          className="text-xs text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 flex items-center gap-1.5 px-2 py-1 rounded-lg transition-all duration-200"
        >
          {copiedField === fieldId ? (
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
        {jsonString}
      </pre>
    </div>
  );
};
```

### Error Message Pattern

```tsx
// Full-width error (loading state):
{error && (
  <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
    {error}
  </div>
)}

// Inline error with title and message:
{errorType && errorMessage && (
  <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
    <p className="text-sm font-medium text-red-900">Error: {errorType}</p>
    <p className="text-sm text-red-700 mt-2">{errorMessage}</p>
  </div>
)}
```

### Loading State Pattern

```tsx
{loading && (
  <div className="flex items-center justify-center py-12">
    <div className="text-neutral-600">Loading...</div>
  </div>
)}

// With spinner (optional):
{loading && (
  <div className="flex items-center justify-center py-12">
    <div className="flex items-center gap-3">
      <div className="animate-spin rounded-full h-5 w-5 border-2 border-neutral-300 border-t-neutral-600" />
      <div className="text-neutral-600">Loading details...</div>
    </div>
  </div>
)}
```

### Nested Content Card (Stages/Children Pattern)

```tsx
<div className="space-y-6">
  {items.map((item, index) => (
    <div key={item.id} className="border border-neutral-200 rounded-xl p-8 bg-neutral-50">
      {/* Card Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono bg-neutral-200 text-neutral-700 px-2.5 py-1 rounded-lg">
            #{index + 1}
          </span>
          <span className="text-sm font-medium text-neutral-900">{item.name}</span>
        </div>
        <span className="text-sm text-neutral-600">{item.duration}ms</span>
      </div>

      {/* Card Content */}
      <div className="grid grid-cols-3 gap-8 mb-6 text-xs">
        <div>
          <span className="text-neutral-600">Label:</span>{' '}
          <span className="font-medium text-neutral-900">{item.value1}</span>
        </div>
        <div>
          <span className="text-neutral-600">Label:</span>{' '}
          <span className="font-medium text-neutral-900">{item.value2}</span>
        </div>
        <div>
          <span className="text-neutral-600">Label:</span>{' '}
          <span className="font-medium text-neutral-900">{item.value3}</span>
        </div>
      </div>

      {/* Nested Code Block */}
      <div>
        <label className="text-xs font-medium text-neutral-700 mb-2 block">Data</label>
        <pre className="bg-white border border-neutral-300 rounded-lg p-4 text-xs font-mono overflow-x-auto max-h-32 overflow-y-auto">
          {item.data}
        </pre>
      </div>
    </div>
  ))}
</div>
```

## Responsive Considerations

### Mobile Adjustments

For screens < 768px, consider these adjustments:

```tsx
// Reduced padding on mobile
<div
  className="flex-1 overflow-y-auto"
  style={{
    padding: window.innerWidth < 768 ? '2rem 1.5rem' : '3rem'
  }}
>

// Single column layout
<div style={{
  display: 'grid',
  gridTemplateColumns: window.innerWidth < 768 ? '1fr' : 'repeat(2, 1fr)',
  gap: '2rem'
}}>

// Full-width modal on mobile
style={{
  maxWidth: window.innerWidth < 768 ? '100%' : '56rem',
  margin: window.innerWidth < 768 ? '0' : undefined
}}
```

### Tailwind Responsive Classes

Alternatively, use Tailwind's responsive utilities:

```tsx
<div className="p-6 md:p-12"> {/* 24px mobile, 48px desktop */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-8"> {/* Single col mobile, two col desktop */}
```

## Performance Considerations

### Portal Optimization

Only render modal when open:

```tsx
if (!isOpen) return null;

const modalContent = (/* ... */);
return createPortal(modalContent, document.body);
```

### Lazy Loading Content

For data-heavy modals, fetch data only when modal opens:

```tsx
useEffect(() => {
  if (isOpen && itemId) {
    fetchItemDetail();
  }
}, [isOpen, itemId]);
```

### Memoization

Memoize expensive computations or large child components:

```tsx
const formattedData = useMemo(() => {
  return JSON.stringify(data, null, 2);
}, [data]);

const SectionContent = React.memo(({ data }) => {
  // Expensive rendering
});
```

## Testing Guidelines

### Visual Regression Tests

- Test modal appearance across different viewport sizes
- Verify backdrop blur and opacity
- Check spacing consistency
- Validate hover states

### Accessibility Tests

```tsx
// Example using @testing-library/react
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('modal closes on ESC key', async () => {
  const onClose = jest.fn();
  render(<Modal isOpen={true} onClose={onClose} title="Test" />);

  await userEvent.keyboard('{Escape}');
  expect(onClose).toHaveBeenCalled();
});

test('modal has correct ARIA attributes', () => {
  render(<Modal isOpen={true} onClose={() => {}} title="Test Modal" />);

  const dialog = screen.getByRole('dialog');
  expect(dialog).toHaveAttribute('aria-modal', 'true');
  expect(dialog).toHaveAttribute('aria-labelledby');
});
```

### Keyboard Navigation Tests

- Test TAB navigation through interactive elements
- Verify ESC key closes modal
- Test ENTER/SPACE on collapsible sections
- Verify focus returns to trigger element on close

## Common Pitfalls

### Don't Use These Patterns

**Avoid hardcoded colors:**
```tsx
// Bad
<div style={{ backgroundColor: '#f5f5f5' }}>

// Good
<div className="bg-neutral-100">
```

**Avoid inconsistent spacing:**
```tsx
// Bad
<div style={{ padding: '15px 20px' }}>

// Good
<div style={{ padding: '1.5rem 2rem' }}>
```

**Avoid rendering without Portal:**
```tsx
// Bad - can cause z-index issues
return <div>{modalContent}</div>;

// Good - escapes stacking context
return createPortal(modalContent, document.body);
```

**Avoid missing accessibility attributes:**
```tsx
// Bad
<button onClick={onClose}>
  <X />
</button>

// Good
<button onClick={onClose} aria-label="Close modal">
  <X />
</button>
```

## Version History

- **v1.0** (2025-10-13): Initial design system based on TraceDetailModal
  - Established spacing standards
  - Documented component patterns
  - Created accessibility guidelines
  - Provided complete code examples

---

**Questions or Suggestions?**
This design system is a living document. If you encounter edge cases or have improvements to suggest, please update this document and notify the team.
