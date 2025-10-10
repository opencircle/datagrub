# Form Field & Metric Card Specifications
## PromptForge UX Specialist - Component Spacing Guide

**Last Updated**: 2025-10-08
**Status**: Active
**Purpose**: Detailed spacing specifications for form inputs, search fields, and metric displays

---

## Overview

This document addresses spacing issues identified in production screenshots and provides comprehensive specifications for form fields and metric cards following Claude.ai design principles.

---

## Issues Identified

### Screenshot 1: Search Field Spacing

**Problems:**
1. Icon too close to placeholder text (only 12px gap)
2. Insufficient breathing room between icon and text
3. Placeholder text feels cramped against icon

**Root Cause:**
- Using `pl-12` (48px) for input with icon at `left-4` (16px)
- Icon width: 20px (h-5 w-5)
- Actual gap: 48px - 16px - 20px = **12px** (too tight)

**Solution:**
- Increase to `pl-14` (56px) for input
- Creates gap: 56px - 16px - 20px = **20px** (comfortable)

### Screenshot 2: Metric Card Spacing

**Problems:**
1. Label and value too close together (insufficient visual separation)
2. Values too small (same size as body text, lacks emphasis)
3. Labels lack clear hierarchy (should be smaller, lighter)
4. Overall lack of visual weight for numbers

**Root Causes:**
- Missing explicit spacing between label and value
- Values not using larger font sizes (text-xl instead of text-3xl)
- Labels not differentiated enough (missing font-medium, neutral-500)

**Solution:**
- Label: `text-sm font-medium text-neutral-500 mb-2`
- Value: `text-3xl font-bold text-neutral-800`
- Clear 8px gap between label and value (mb-2)

---

## Component Specifications

### 1. Search Input with Icon

#### Visual Anatomy
```
┌─────────────────────────────────────────────┐
│  🔍  Search projects by name...             │
│  ←16px→←20px icon→←20px gap→                │
│  ←────────56px (pl-14)────────→             │
└─────────────────────────────────────────────┘
```

#### Spacing Breakdown
- **Container padding**: 0 (relative positioning)
- **Icon position**: `left-4` (16px from left edge)
- **Icon size**: `h-5 w-5` (20px × 20px)
- **Input padding-left**: `pl-14` (56px)
- **Gap between icon and text**: 20px (56 - 16 - 20 = 20px)
- **Input padding-right**: `pr-4` (16px)
- **Input height**: `h-12` (48px)

#### Complete Implementation
```jsx
<div className="relative">
  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
  <input
    type="text"
    placeholder="Search projects by name or description..."
    className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 placeholder:text-neutral-400"
  />
</div>
```

#### Before/After Comparison

**Before (Incorrect - pl-12):**
```jsx
// ❌ Icon and text too close (12px gap)
<input className="w-full h-12 pl-12 pr-4 ..." />
```

**After (Correct - pl-14):**
```jsx
// ✅ Comfortable spacing (20px gap)
<input className="w-full h-12 pl-14 pr-4 ..." />
```

#### Icon Positioning Rules
1. **Icon left position**: Always `left-4` (16px)
2. **Icon size**: `h-5 w-5` (20px) for search/input icons
3. **Minimum gap**: 16-20px between icon and text
4. **Input padding formula**: `left-position + icon-width + desired-gap`
   - Example: 16px + 20px + 20px = 56px = `pl-14`

---

### 2. Metric/Stat Cards

#### Visual Anatomy (Single Card)
```
┌───────────────────────┐
│  Total Runs           │ ← Label (text-sm, neutral-500)
│  ↓ 8px gap (mb-2)     │
│  1,247                │ ← Value (text-3xl, neutral-800, bold)
│                       │
│  ← p-6 (24px) →       │
└───────────────────────┘
```

#### Spacing Breakdown
- **Container padding**: `p-6` (24px all sides)
- **Container border**: `border border-neutral-100`
- **Container radius**: `rounded-2xl` (16px)
- **Label-to-value gap**: `mb-2` (8px)
- **Label size**: `text-sm` (14px)
- **Value size**: `text-3xl` (30px)
- **Size ratio**: Value is **2.14x** larger than label

#### Typography Hierarchy
| Element | Size | Weight | Color | Purpose |
|---------|------|--------|-------|---------|
| Label | text-sm (14px) | font-medium (500) | neutral-500 | Descriptive, subdued |
| Value | text-3xl (30px) | font-bold (700) | neutral-800 | Emphasis, readability |

#### Complete Implementation (Single Card)
```jsx
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
  <div className="text-3xl font-bold text-neutral-800">1,247</div>
</div>
```

#### Three-Column Grid Layout
```jsx
<div className="grid grid-cols-3 gap-6">
  {/* Card 1 */}
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
    <div className="text-3xl font-bold text-neutral-800">1</div>
  </div>

  {/* Card 2 */}
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Avg Score</div>
    <div className="text-3xl font-bold text-neutral-800">0.9</div>
  </div>

  {/* Card 3 */}
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Running</div>
    <div className="text-3xl font-bold text-neutral-800">0</div>
  </div>
</div>
```

#### Before/After Comparison

**Before (Incorrect):**
```jsx
// ❌ Problems:
// - No explicit spacing between label and value
// - Value too small (text-xl instead of text-3xl)
// - Label not differentiated (missing font-medium, color)
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  <div className="text-neutral-800">Total Runs</div>
  <div className="text-xl font-bold text-neutral-800">1</div>
</div>
```

**After (Correct):**
```jsx
// ✅ Solutions:
// - Clear 8px gap (mb-2)
// - Larger value size (text-3xl)
// - Proper label hierarchy (text-sm, font-medium, neutral-500)
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
  <div className="text-3xl font-bold text-neutral-800">1</div>
</div>
```

---

### 3. Compact Inline Stat Display

For dashboard rows or tighter layouts:

```jsx
<div className="flex flex-col gap-2">
  <span className="text-sm font-medium text-neutral-500">Avg Score</span>
  <span className="text-2xl font-bold text-neutral-800">0.94</span>
</div>
```

**Spacing:**
- Gap: `gap-2` (8px)
- Value size: `text-2xl` (24px) - smaller than card variant
- Use when space is constrained

---

### 4. Metric Card with Icon

For enhanced visual interest:

```jsx
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  <div className="flex items-center justify-between mb-4">
    <div className="bg-neutral-50 p-3 rounded-xl">
      <TrendingUp className="h-6 w-6 text-neutral-600" />
    </div>
    <div className="text-xs px-2.5 py-1 rounded-full bg-[#00A699]/10 text-[#008489] font-semibold">
      +12%
    </div>
  </div>
  <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
  <div className="text-3xl font-bold text-neutral-800">1,247</div>
</div>
```

**Additional Spacing:**
- Icon container: `mb-4` (16px below icon area)
- Icon padding: `p-3` (12px)
- Badge spacing: Uses flex justify-between

---

## Spacing Patterns Reference

### Form Input Icon Spacing Matrix

| Icon Size | Icon Position | Minimum Gap | Input Padding-Left | Tailwind Class |
|-----------|---------------|-------------|-------------------|----------------|
| h-4 w-4 (16px) | left-3 (12px) | 16px | 44px | pl-11 |
| h-5 w-5 (20px) | left-4 (16px) | 20px | 56px | **pl-14** ⭐ |
| h-6 w-6 (24px) | left-4 (16px) | 16px | 56px | pl-14 |
| h-6 w-6 (24px) | left-5 (20px) | 20px | 64px | pl-16 |

**Recommended**: `h-5 w-5` icon with `left-4` and `pl-14` (20px gap)

### Label-Value Spacing Matrix

| Context | Label Size | Value Size | Gap | Label Color | Value Color |
|---------|------------|------------|-----|-------------|-------------|
| Large Card | text-sm | text-3xl | mb-2 (8px) | neutral-500 | neutral-800 |
| Medium Card | text-sm | text-2xl | mb-2 (8px) | neutral-500 | neutral-800 |
| Inline Compact | text-xs | text-xl | gap-1 (4px) | neutral-400 | neutral-800 |
| Dashboard Row | text-sm | text-2xl | gap-2 (8px) | neutral-500 | neutral-800 |

**Recommended**: Large card pattern for primary metrics

---

## Usage Guidelines

### When to Use Search Input with Icon
- ✅ Search bars for filtering content
- ✅ Lookup fields (e.g., "Search users...")
- ✅ Any input where visual affordance helps (location, date, etc.)

### When to Use Metric Cards
- ✅ Dashboard summary statistics
- ✅ KPI displays
- ✅ Real-time metrics (counts, averages, percentages)
- ✅ Comparison data (before/after, current vs. target)

### Accessibility Considerations

**Search Inputs:**
- Use `aria-label` if no visible label: `aria-label="Search projects"`
- Include descriptive placeholder text
- Ensure icon color meets AA contrast (neutral-400 on white = 7:1)

**Metric Cards:**
- Use semantic HTML (`<dl>`, `<dt>`, `<dd>`) for screen readers:
  ```jsx
  <dl className="bg-white rounded-2xl p-6 border border-neutral-100">
    <dt className="text-sm font-medium text-neutral-500 mb-2">Total Runs</dt>
    <dd className="text-3xl font-bold text-neutral-800">1,247</dd>
  </dl>
  ```
- Include units in value when relevant: "0.94 average" instead of just "0.94"
- Use `aria-live="polite"` for real-time updating metrics

---

## Tailwind Class Quick Reference

### Search Input Pattern
```jsx
// Container
<div className="relative">

// Icon
<Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />

// Input
<input className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 placeholder:text-neutral-400" />
```

### Metric Card Pattern
```jsx
// Container
<div className="bg-white rounded-2xl p-6 border border-neutral-100">

// Label
<div className="text-sm font-medium text-neutral-500 mb-2">

// Value
<div className="text-3xl font-bold text-neutral-800">
```

---

## Component Testing Checklist

### Search Input
- [ ] Icon positioned 16px from left edge
- [ ] Icon-to-text gap is 16-20px minimum
- [ ] Input height is 48px (h-12)
- [ ] Placeholder text is readable and not cramped
- [ ] Focus state shows primary color ring
- [ ] Icon color is neutral-400 (sufficient contrast)
- [ ] Touch target is minimum 44px tall

### Metric Card
- [ ] Label uses text-sm font-medium neutral-500
- [ ] Value uses text-3xl font-bold neutral-800
- [ ] Gap between label and value is 8px (mb-2)
- [ ] Card padding is 24px (p-6)
- [ ] Border is subtle (border-neutral-100)
- [ ] Card background is white (bg-white)
- [ ] Values are clearly larger than labels (2x+ size difference)

---

## Common Mistakes to Avoid

### ❌ Don't Do This

**Search Input:**
```jsx
// Too tight (pl-12 instead of pl-14)
<input className="w-full h-12 pl-12 pr-4 ..." />

// Icon too large for spacing
<Search className="absolute left-4 ... h-8 w-8" />

// Missing focus states
<input className="w-full h-12 pl-14 pr-4 border rounded-xl" />
```

**Metric Card:**
```jsx
// No spacing between label and value
<div className="text-sm text-neutral-500">Label</div>
<div className="text-xl font-bold">Value</div>

// Value too small
<div className="text-xl font-bold text-neutral-800">1,247</div>

// Label not differentiated
<div className="text-neutral-800">Total Runs</div>
```

### ✅ Do This Instead

**Search Input:**
```jsx
// Proper spacing (pl-14)
<input className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 ..." />

// Correct icon size
<Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
```

**Metric Card:**
```jsx
// Clear hierarchy and spacing
<div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
<div className="text-3xl font-bold text-neutral-800">1,247</div>
```

---

## Related Documentation

- **Main Design System**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/DESIGN_SYSTEM.md`
- **Color Palette**: See Design System Section 2
- **Typography Scale**: See Design System Section 3
- **Spacing System**: See Design System Section 4

---

## Version History

- **v1.0** (2025-10-08): Initial specification addressing search field and metric card spacing issues

---

## Questions or Issues

If you encounter spacing issues not covered here:
1. Check the main Design System document first
2. Verify you're using the correct Tailwind classes
3. Test on multiple screen sizes
4. Ensure accessibility requirements are met (WCAG AAA)

**Remember**: When in doubt, err on the side of **more generous spacing** for better readability and user experience.
