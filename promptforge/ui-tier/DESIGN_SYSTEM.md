# PromptForge Design System v2.0
## Claude.ai-Inspired Modern Dashboard Aesthetic

Last Updated: 2025-10-08
Status: Active

---

## Table of Contents
1. [Design Principles](#design-principles)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Spacing System](#spacing-system)
5. [Border Radius](#border-radius)
6. [Shadows](#shadows)
7. [Interactive States](#interactive-states)
8. [Component Specifications](#component-specifications)
9. [Layout Patterns](#layout-patterns)
10. [Before/After Examples](#beforeafter-examples)

---

## Design Principles

PromptForge follows the Claude.ai modern dashboard aesthetic with these core principles:

### 1. **Clean Minimalism**
- Generous whitespace creates breathing room
- Neutral color palette (grays) for backgrounds
- Strategic use of primary color (#FF385C) for emphasis only
- Soft, subtle borders and shadows instead of heavy visual weight

### 2. **Generous Spacing**
- Follow 8px grid system strictly
- Larger padding in containers (p-6 to p-8 for cards)
- Increased gaps between elements (gap-6 for grids)
- More vertical rhythm (space-y-8 between sections)

### 3. **Soft Visual Style**
- Rounded corners everywhere (rounded-xl, rounded-2xl)
- Soft shadows only (no hard edges)
- Gentle transitions (200ms duration)
- Light borders (border-neutral-100, border-neutral-200)

### 4. **Clear Visual Hierarchy**
- Large, bold headings (text-3xl font-bold)
- Descriptive subtext in neutral-500
- Strategic use of font weights (semibold for labels, bold for headings)
- Clear separation between sections

### 5. **Accessible by Default**
- WCAG 2.1 AAA compliance
- Large touch targets (minimum h-11 for buttons, h-12 for inputs)
- High contrast text (neutral-800 on white, white on primary)
- Focus rings with 4px ring width and 20% opacity

### 6. **Progressive Disclosure**
- Action buttons appear on hover (group-hover pattern)
- Subtle animations reveal details
- Clear empty states with guidance
- Loading states with spinner and descriptive text

---

## Color Palette

### Primary Colors
```css
--primary: #FF385C              /* Primary action color (red-pink) */
--primary-dark: #E31C5F         /* Hover state for primary */
--primary-bg-subtle: #FF385C/5  /* 5% opacity for backgrounds */
--primary-bg: #FF385C/10        /* 10% opacity for backgrounds */
--primary-border: #FF385C/20    /* 20% opacity for borders */
--primary-ring: #FF385C/10      /* 10% opacity for focus rings */
```

**Tailwind Classes:**
```jsx
bg-[#FF385C]           // Primary background
hover:bg-[#E31C5F]     // Primary hover
text-[#FF385C]         // Primary text
hover:text-[#E31C5F]   // Primary text hover
border-[#FF385C]       // Primary border
ring-[#FF385C]/10      // Primary focus ring
bg-[#FF385C]/5         // Subtle primary background
```

### Neutral Colors (Gray Scale)
```css
--neutral-50: #FAFAFA           /* Page background */
--neutral-100: #F5F5F5          /* Card hover background */
--neutral-200: #E5E5E5          /* Borders, subtle separators */
--neutral-300: #D4D4D4          /* Disabled text */
--neutral-400: #A3A3A3          /* Placeholder text, icons */
--neutral-500: #737373          /* Secondary text, descriptions */
--neutral-600: #525252          /* Icons, less important text */
--neutral-700: #404040          /* Body text (lighter) */
--neutral-800: #262626          /* Headings, primary text */
```

**Tailwind Classes:**
```jsx
bg-neutral-50          // Page background
bg-neutral-100         // Hover backgrounds, dividers
border-neutral-100     // Very subtle borders
border-neutral-200     // Standard borders
text-neutral-400       // Placeholder text
text-neutral-500       // Secondary text
text-neutral-600       // Icons
text-neutral-700       // Less important body text
text-neutral-800       // Headings and primary text
```

### Semantic Colors
```css
--success: #00A699             /* Success states */
--success-bg: #00A699/10       /* Success background */
--success-text: #008489        /* Success text (darker) */

--warning: #FFB400             /* Warning states */
--warning-bg: #FFB400/10       /* Warning background */
--warning-text: #E6A200        /* Warning text (darker) */

--error: #C13515               /* Error states */
--error-bg: #C13515/5          /* Error background */
```

**Tailwind Classes:**
```jsx
// Success
bg-[#00A699]/10 text-[#008489]  // Success badge
text-[#00A699]                   // Success text

// Warning
bg-[#FFB400]/10 text-[#E6A200]  // Warning badge
text-[#FFB400]                   // Warning text

// Error
bg-[#C13515]/5                   // Error background
text-[#C13515]                   // Error text
```

### Background Colors
```css
--bg-page: #FAFAFA (neutral-50)        /* Main page background */
--bg-card: #FFFFFF (white)              /* Card background */
--bg-hover: #F5F5F5 (neutral-100)       /* Hover background */
--bg-input: #FFFFFF (white)             /* Input background */
```

---

## Typography

### Font Family
```css
font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Tailwind:** Default setup in `tailwind.config.js` with Inter font

### Font Sizes & Usage

| Size | Class | Rem | Px | Usage |
|------|-------|-----|-----|-------|
| XS | `text-xs` | 0.75rem | 12px | Tags, meta info, fine print |
| SM | `text-sm` | 0.875rem | 14px | Secondary text, captions, badge text |
| Base | `text-base` | 1rem | 16px | Body text, input text, search placeholder |
| LG | `text-lg` | 1.125rem | 18px | Card titles, section subheadings |
| XL | `text-xl` | 1.25rem | 20px | Modal titles |
| 2XL | `text-2xl` | 1.5rem | 24px | Unused currently |
| 3XL | `text-3xl` | 1.875rem | 30px | **Page headings** |

### Font Weights

| Weight | Class | Value | Usage |
|--------|-------|-------|-------|
| Normal | `font-normal` | 400 | Body text (rarely used) |
| Medium | `font-medium` | 500 | Filter labels, less important labels |
| Semibold | `font-semibold` | 600 | **Buttons, badges, cards, labels, navigation** |
| Bold | `font-bold` | 700 | **Page headings, card titles** |

### Line Heights
```jsx
leading-snug      // 1.375 - Headings (h1, h3)
leading-relaxed   // 1.625 - Body text, descriptions
```

### Common Text Patterns

**Page Heading:**
```jsx
<h1 className="text-3xl font-bold text-neutral-800">Projects</h1>
<p className="text-neutral-500 mt-2 text-base">Manage your AI prompt projects</p>
```

**Card Title:**
```jsx
<h3 className="text-lg font-bold text-neutral-800 mb-2 leading-snug">Card Title</h3>
```

**Section Heading:**
```jsx
<h3 className="text-lg font-semibold text-neutral-800 mb-4">Category</h3>
```

**Body Text:**
```jsx
<p className="text-sm text-neutral-500 mb-4 line-clamp-2 leading-relaxed">
  Description text goes here
</p>
```

**Meta/Helper Text:**
```jsx
<span className="text-xs text-neutral-400">View prompts</span>
```

---

## Spacing System

### 8px Grid System
All spacing follows multiples of 8px (0.5rem):

| Class | Rem | Px | Usage |
|-------|-----|-----|-------|
| `0` | 0 | 0 | No spacing |
| `1` | 0.25rem | 4px | Tight spacing (icon gaps) |
| `1.5` | 0.375rem | 6px | Tag gaps |
| `2` | 0.5rem | 8px | Compact spacing |
| `2.5` | 0.625rem | 10px | Badge padding |
| `3` | 0.75rem | 12px | Icon container padding |
| `4` | 1rem | 16px | Standard spacing |
| `5` | 1.25rem | 20px | Filter gaps, form spacing |
| `6` | 1.5rem | 24px | **Card padding, grid gaps** |
| `8` | 2rem | 32px | **Section spacing (vertical)** |
| `12` | 3rem | 48px | (Deprecated - use pl-14 for search inputs) |
| `14` | 3.5rem | 56px | **Input padding-left (with icon)** |
| `20` | 5rem | 80px | Empty state padding |

### Common Spacing Patterns

**Page Container:**
```jsx
<div className="space-y-8 max-w-7xl">  {/* Sections 32px apart */}
```

**Card Grid:**
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Cards 24px apart */}
```

**Card Interior:**
```jsx
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  {/* 24px padding inside cards */}
```

**Search Bar:**
```jsx
<div className="relative">
  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2" />
  <input className="pl-14 pr-4" />  {/* 56px left (20px icon gap), 16px right */}
</div>
```

**Section Spacing:**
```jsx
<div className="space-y-5">         {/* Filter elements 20px apart */}
<div className="space-y-8">         {/* Major sections 32px apart */}
```

---

## Border Radius

### Values
| Class | Rem | Px | Usage |
|-------|-----|-----|-------|
| `rounded-lg` | 0.5rem | 8px | Small buttons, badges |
| `rounded-xl` | 0.75rem | 12px | **Buttons, inputs, navigation items** |
| `rounded-2xl` | 1rem | 16px | **Cards, containers, modals** |
| `rounded-full` | 9999px | Full | Circular elements (avatars, checkboxes) |

### Component Mapping
- **Buttons**: `rounded-xl` (12px)
- **Inputs/Search**: `rounded-xl` (12px)
- **Cards**: `rounded-2xl` (16px)
- **Modals**: `rounded-2xl` (16px)
- **Badges**: `rounded-full` or `rounded-lg`
- **Filter chips**: `rounded-lg` (8px)
- **Icon containers**: `rounded-xl` (12px)
- **Checkboxes**: `rounded` (4px default)

---

## Shadows

### Shadow Values
```css
shadow-sm    // Subtle card elevation, selected states
shadow-md    // Hover state for cards
shadow-lg    // Emphasized cards, modals
```

### Shadow Usage
- **Default card**: No shadow or `shadow-sm` (very subtle)
- **Card hover**: `shadow-md`
- **Selected card**: `shadow-sm`
- **Buttons**: `shadow-sm` (primary buttons only)
- **Modals**: `shadow-lg`

**Pattern:**
```jsx
// Subtle default
<div className="bg-white rounded-2xl p-6 border border-neutral-100">

// With hover
<div className="bg-white rounded-2xl p-6 hover:shadow-lg transition-all border border-neutral-100">

// Selected state
<div className="border-[#FF385C] ring-4 ring-[#FF385C]/10 shadow-sm">
```

---

## Interactive States

### Hover States

**Cards:**
```jsx
hover:shadow-lg transition-all duration-200
hover:border-neutral-200
```

**Buttons (Primary):**
```jsx
hover:bg-[#E31C5F] transition-all duration-200
```

**Buttons (Secondary/Ghost):**
```jsx
hover:bg-neutral-100 transition-all duration-200
```

**Text Links:**
```jsx
text-[#FF385C] hover:text-[#E31C5F] transition-colors
```

**Icon Buttons:**
```jsx
hover:bg-neutral-100 transition-all duration-200
```

### Focus States

**All Interactive Elements:**
```jsx
focus:outline-none focus:ring-4 focus:ring-[#FF385C]/10
```

**Inputs:**
```jsx
focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10
```

**Buttons:**
```jsx
focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20
```

### Selected/Active States

**Navigation:**
```jsx
bg-[#FF385C]/10 text-[#FF385C]
```

**Cards:**
```jsx
border-[#FF385C] ring-4 ring-[#FF385C]/10 shadow-sm
```

**Filter Chips:**
```jsx
bg-[#FF385C] text-white shadow-sm
```

**Checkboxes:**
```jsx
bg-[#FF385C] border-[#FF385C]
```

### Disabled States
```jsx
opacity-50 cursor-not-allowed
bg-neutral-100 text-neutral-400
```

---

## Component Specifications

### 1. **Primary Button**

**Spec:**
- Height: `h-11` (44px) - touch-friendly
- Padding: `px-5` (20px horizontal)
- Border Radius: `rounded-xl`
- Background: `bg-[#FF385C]`
- Text: `text-white font-semibold`
- Shadow: `shadow-sm`
- Hover: `hover:bg-[#E31C5F]`
- Focus: `focus:ring-4 focus:ring-[#FF385C]/20`
- Transition: `transition-all duration-200`

**Code:**
```jsx
<button className="flex items-center gap-2 h-11 bg-[#FF385C] text-white px-5 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20">
  <Plus className="h-5 w-5" />
  New Project
</button>
```

### 2. **Search Bar**

**Spec:**
- Height: `h-12` (48px)
- Padding: `pl-14 pr-4` (icon spacing - increased from pl-12)
- Border: `border border-neutral-200`
- Border Radius: `rounded-xl`
- Background: `bg-white`
- Text: `text-neutral-700 text-base`
- Placeholder: `placeholder:text-neutral-400`
- Focus: `focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10`
- Icon: `absolute left-4 text-neutral-400 h-5 w-5` (minimum 16px from left edge)
- Icon-to-text spacing: **24px minimum** (icon left-4 + icon width 20px + gap = pl-14)

**Code:**
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

### 3. **Card**

**Spec:**
- Background: `bg-white`
- Border: `border border-neutral-100`
- Border Radius: `rounded-2xl`
- Padding: `p-6`
- Hover: `hover:shadow-lg transition-all duration-200`
- Cursor: `cursor-pointer` (if clickable)

**Code:**
```jsx
<div className="bg-white rounded-2xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer border border-neutral-100">
  {/* Card content */}
</div>
```

**Selected Card:**
```jsx
<div className="bg-white border rounded-2xl p-5 border-[#FF385C] ring-4 ring-[#FF385C]/10 shadow-sm">
  {/* Card content */}
</div>
```

### 4. **Status Badge**

**Spec:**
- Padding: `px-2.5 py-1`
- Border Radius: `rounded-full`
- Font: `text-xs font-semibold`
- Background: 10% opacity of semantic color
- Text: Darker variant of semantic color

**Code:**
```jsx
// Active status
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#00A699]/10 text-[#008489]">
  active
</span>

// Draft status
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#FFB400]/10 text-[#E6A200]">
  draft
</span>

// Archived status
<span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-neutral-100 text-neutral-700">
  archived
</span>
```

### 5. **Icon Container**

**Spec:**
- Background: `bg-neutral-50`
- Padding: `p-3`
- Border Radius: `rounded-xl`
- Icon: `h-6 w-6 text-neutral-600`

**Code:**
```jsx
<div className="bg-neutral-50 p-3 rounded-xl">
  <FolderKanban className="h-6 w-6 text-neutral-600" />
</div>
```

### 6. **Filter Chip**

**Spec (Inactive):**
- Background: `bg-white`
- Border: `border border-neutral-200`
- Hover: `hover:border-neutral-300`
- Padding: `px-3 py-1.5`
- Border Radius: `rounded-lg`
- Font: `text-sm font-medium text-neutral-600`

**Spec (Active):**
- Background: `bg-[#FF385C]`
- Text: `text-white`
- Shadow: `shadow-sm`
- No border

**Code:**
```jsx
// Inactive
<button className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300">
  All Sources
</button>

// Active
<button className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all bg-[#FF385C] text-white shadow-sm">
  All Sources
</button>
```

### 7. **Checkbox**

**Spec:**
- Size: `w-5 h-5`
- Border: `border-2`
- Border Radius: `rounded`
- Inactive: `border-neutral-300 hover:border-neutral-400`
- Active: `bg-[#FF385C] border-[#FF385C]`
- Check Icon: `h-3 w-3 text-white`

**Code:**
```jsx
// Inactive
<div className="w-5 h-5 rounded border-2 border-neutral-300 hover:border-neutral-400 flex items-center justify-center transition-all">
</div>

// Active
<div className="w-5 h-5 rounded border-2 bg-[#FF385C] border-[#FF385C] flex items-center justify-center transition-all">
  <Check className="h-3 w-3 text-white" />
</div>
```

### 8. **Empty State**

**Spec:**
- Background: `bg-white`
- Border: `border border-neutral-100`
- Border Radius: `rounded-2xl`
- Padding: `py-20`
- Alignment: `text-center`
- Icon: `h-16 w-16 text-neutral-300 mx-auto mb-5`
- Title: `text-neutral-700 font-semibold mb-2 text-lg`
- Description: `text-sm text-neutral-400`

**Code:**
```jsx
<div className="text-center py-20 bg-white rounded-2xl border border-neutral-100">
  <FolderKanban className="h-16 w-16 text-neutral-300 mx-auto mb-5" />
  <p className="text-neutral-700 font-semibold mb-2 text-lg">No projects found</p>
  <p className="text-sm text-neutral-400">Try adjusting your search or create a new project</p>
</div>
```

### 9. **Loading State**

**Spec:**
- Container: `flex items-center justify-center h-64`
- Spinner: `h-8 w-8 text-[#FF385C] animate-spin`
- Text: `ml-3 text-neutral-600 font-medium`

**Code:**
```jsx
<div className="flex items-center justify-center h-64">
  <Loader className="h-8 w-8 text-[#FF385C] animate-spin" />
  <span className="ml-3 text-neutral-600 font-medium">Loading projects...</span>
</div>
```

### 10. **Icon Button (Hover Action)**

**Spec:**
- Padding: `p-2`
- Border Radius: `rounded-lg`
- Hover: `hover:bg-neutral-100`
- Focus: `focus:ring-2 focus:ring-[#FF385C]/20`
- Icon: `h-4 w-4 text-neutral-600`
- Opacity: `opacity-0 group-hover:opacity-100`
- Transition: `transition-all duration-200`

**Code:**
```jsx
<button
  className="p-2 rounded-lg hover:bg-neutral-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
  aria-label="Edit project"
>
  <Edit2 className="h-4 w-4 text-neutral-600" />
</button>
```

### 11. **Tag**

**Spec:**
- Padding: `px-2 py-1`
- Background: `bg-neutral-50`
- Text: `text-xs text-neutral-600`
- Border Radius: `rounded-md`

**Code:**
```jsx
<span className="text-xs px-2 py-1 bg-neutral-50 text-neutral-600 rounded-md">
  tag-name
</span>
```

### 12. **Metric/Stat Card**

**Spec:**
- Container: `bg-white rounded-2xl p-6 border border-neutral-100`
- Label: `text-sm font-medium text-neutral-500 mb-2`
- Value: `text-3xl font-bold text-neutral-800`
- Label-to-value spacing: `mb-2` (8px gap)
- Use clear visual hierarchy (label smaller/lighter, value larger/bolder)

**Code:**
```jsx
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
  <div className="text-3xl font-bold text-neutral-800">1,247</div>
</div>
```

**Compact Inline Variant (for dashboard rows):**
```jsx
<div className="flex flex-col gap-2">
  <span className="text-sm font-medium text-neutral-500">Avg Score</span>
  <span className="text-2xl font-bold text-neutral-800">0.94</span>
</div>
```

**Three-Column Stats Layout:**
```jsx
<div className="grid grid-cols-3 gap-6">
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Total Runs</div>
    <div className="text-3xl font-bold text-neutral-800">1</div>
  </div>
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Avg Score</div>
    <div className="text-3xl font-bold text-neutral-800">0.9</div>
  </div>
  <div className="bg-white rounded-2xl p-6 border border-neutral-100">
    <div className="text-sm font-medium text-neutral-500 mb-2">Running</div>
    <div className="text-3xl font-bold text-neutral-800">0</div>
  </div>
</div>
```

### 13. **Tab Navigation**

**Design Principle:** Tab navigation should be clean, spacious, and clearly indicate active state. Claude.ai-style tabs use generous spacing between tabs and within tab buttons, with a minimal bottom-border indicator for the active state.

**Container Spec:**
- Layout: `flex items-center justify-between` (tabs on left, action button on right)
- Bottom border: `border-b border-neutral-200` (separator line)
- Bottom margin: `mb-4` or `mb-6` (space before content)

**Tab Button Spec:**
- Height: `h-11` (44px minimum for touch-friendly targets)
- Padding: `px-4 py-2.5` (16px horizontal, 10px vertical)
- Icon-text gap: `gap-2` (8px between icon and text)
- Font: `text-sm font-semibold`
- Icon size: `h-5 w-5` (20px)
- Border: `border-b-2` (2px bottom border for active state)
- Transition: `transition-all duration-200`

**Tab Container (nav) Spec:**
- Layout: `flex gap-3` (12px gap between tabs)
- Alignment: `items-center`

**Active Tab State:**
- Border: `border-[#FF385C]` (2px bottom border in primary color)
- Text: `text-[#FF385C]`
- Font: `font-semibold`

**Inactive Tab State:**
- Border: `border-transparent`
- Text: `text-neutral-600`
- Hover border: `hover:border-neutral-300`
- Hover text: `hover:text-neutral-800`

**Code (Full Pattern with Action Button):**
```jsx
<div className="border-b border-neutral-200">
  <div className="flex items-center justify-between mb-4">
    <nav className="flex gap-3">
      {/* Active Tab */}
      <button
        className="flex items-center gap-2 h-11 px-4 py-2.5 border-b-2 border-[#FF385C] text-[#FF385C] font-semibold text-sm transition-all duration-200"
      >
        <LineChart className="h-5 w-5" />
        Evaluation Results
      </button>

      {/* Inactive Tab */}
      <button
        className="flex items-center gap-2 h-11 px-4 py-2.5 border-b-2 border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300 font-semibold text-sm transition-all duration-200"
      >
        <BookOpen className="h-5 w-5" />
        Browse Catalog
      </button>
    </nav>

    {/* Optional Action Button */}
    <Button variant="primary">
      <Play className="h-4 w-4 mr-2" />
      Run Evaluation
    </Button>
  </div>
</div>
```

**Code (Simple Tabs Only):**
```jsx
<div className="border-b border-neutral-200 mb-6">
  <nav className="flex gap-3">
    <button
      className={`
        flex items-center gap-2 h-11 px-4 py-2.5 border-b-2 font-semibold text-sm transition-all duration-200
        ${isActive
          ? 'border-[#FF385C] text-[#FF385C]'
          : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
        }
      `}
    >
      <Icon className="h-5 w-5" />
      Tab Label
    </button>
  </nav>
</div>
```

**Tab with Badge (showing count):**
```jsx
<button
  className="flex items-center gap-2 h-11 px-4 py-2.5 border-b-2 border-[#FF385C] text-[#FF385C] font-semibold text-sm transition-all duration-200"
>
  <BookOpen className="h-5 w-5" />
  Browse Catalog
  <span className="px-2 py-0.5 bg-[#FF385C] text-white text-xs font-semibold rounded-full">
    3
  </span>
</button>
```

**Accessibility:**
- Use semantic `<nav>` for tab container
- Add `role="tablist"` to nav if implementing full ARIA tabs pattern
- Add `aria-selected="true"` to active tab button
- Ensure keyboard navigation support (Tab, Arrow keys)
- Minimum 44px touch target height (`h-11`)

**Key Spacing Issues Fixed:**
1. **Tab spacing**: Changed from `space-x-6` (24px) to `gap-3` (12px) for cleaner, more compact layout
2. **Icon-text gap**: Explicit `gap-2` (8px) between icon and text
3. **Button padding**: Explicit `px-4 py-2.5` (16px horizontal, 10px vertical) for comfortable touch targets
4. **Button height**: Explicit `h-11` (44px) for consistent sizing and accessibility
5. **Border weight**: `border-b-2` (2px) for clear active state indication

---

## Layout Patterns

### Page Layout

**Full Page Container:**
```jsx
<div className="space-y-8 max-w-7xl">
  {/* All page sections */}
</div>
```

**Page Header:**
```jsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-3xl font-bold text-neutral-800">Page Title</h1>
    <p className="text-neutral-500 mt-2 text-base">Page description</p>
  </div>
  <button className="...">Primary Action</button>
</div>
```

### Grid Layouts

**3-Column Responsive Grid:**
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <Card key={item.id} />
  ))}
</div>
```

### Card Interior Layout

**Standard Card:**
```jsx
<div className="bg-white rounded-2xl p-6 border border-neutral-100">
  {/* Header with icon and badge */}
  <div className="flex items-start justify-between mb-4">
    <div className="bg-neutral-50 p-3 rounded-xl">
      <Icon className="h-6 w-6 text-neutral-600" />
    </div>
    <StatusBadge status={status} />
  </div>

  {/* Title */}
  <h3 className="text-lg font-bold text-neutral-800 mb-2 leading-snug">
    Title
  </h3>

  {/* Description */}
  <p className="text-sm text-neutral-500 mb-4 line-clamp-2 leading-relaxed">
    Description
  </p>

  {/* Metadata */}
  <div className="text-sm text-neutral-400 mb-4">
    Meta info
  </div>

  {/* Footer action */}
  <div className="pt-4 border-t border-neutral-50">
    <button>Action</button>
  </div>
</div>
```

---

## Before/After Examples

### Example 1: Page Header

**Before (Airbnb-style):**
```jsx
<div className="flex items-center justify-between mb-6">
  <h1 className="text-2xl font-bold text-neutral-800">Projects</h1>
  <button className="bg-[#FF385C] text-white px-4 py-2 rounded-lg">
    New Project
  </button>
</div>
```

**After (Claude.ai-style):**
```jsx
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-3xl font-bold text-neutral-800">Projects</h1>
    <p className="text-neutral-500 mt-2 text-base">Manage your AI prompt projects</p>
  </div>
  <button className="flex items-center gap-2 h-11 bg-[#FF385C] text-white px-5 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20">
    <Plus className="h-5 w-5" />
    New Project
  </button>
</div>
```

**Changes:**
- ✅ Larger heading (text-2xl → text-3xl)
- ✅ Added descriptive subtitle in neutral-500
- ✅ Button height increased (py-2 → h-11)
- ✅ More generous horizontal padding (px-4 → px-5)
- ✅ Rounded corners increased (rounded-lg → rounded-xl)
- ✅ Added shadow, focus ring
- ✅ Icon + text pattern for clarity

---

### Example 2: Search Bar

**Before:**
```jsx
<input
  type="text"
  placeholder="Search..."
  className="w-full px-4 py-2 border rounded-lg"
/>
```

**After:**
```jsx
<div className="relative">
  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
  <input
    type="text"
    placeholder="Search projects by name or description..."
    className="w-full h-12 pl-12 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 placeholder:text-neutral-400"
  />
</div>
```

**Changes:**
- ✅ Fixed height (h-12 = 48px) for consistency
- ✅ Added search icon inside input
- ✅ More descriptive placeholder text
- ✅ Softer border (border-neutral-200)
- ✅ Increased border radius (rounded-lg → rounded-xl)
- ✅ Added focus states with primary color
- ✅ Explicit text size and color

---

### Example 3: Card

**Before:**
```jsx
<div className="bg-white rounded-lg p-4 shadow hover:shadow-md">
  <h3 className="font-semibold mb-2">Card Title</h3>
  <p className="text-sm text-gray-600">Description</p>
</div>
```

**After:**
```jsx
<div className="bg-white rounded-2xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer border border-neutral-100">
  <div className="flex items-start justify-between mb-4">
    <div className="bg-neutral-50 p-3 rounded-xl">
      <FolderKanban className="h-6 w-6 text-neutral-600" />
    </div>
    <StatusBadge status="active" />
  </div>

  <h3 className="text-lg font-bold text-neutral-800 mb-2 leading-snug">
    Card Title
  </h3>
  <p className="text-sm text-neutral-500 mb-4 line-clamp-2 min-h-[2.5rem] leading-relaxed">
    Description text goes here
  </p>

  <div className="pt-4 border-t border-neutral-50">
    <button className="w-full h-10 text-sm text-[#FF385C] hover:text-[#E31C5F] hover:bg-[#FF385C]/5 font-semibold rounded-lg transition-all duration-200">
      Action
    </button>
  </div>
</div>
```

**Changes:**
- ✅ Increased border radius (rounded-lg → rounded-2xl)
- ✅ More padding (p-4 → p-6)
- ✅ Added subtle border (border-neutral-100)
- ✅ Stronger hover shadow (shadow-md → shadow-lg)
- ✅ Added icon container with background
- ✅ Added status badge
- ✅ Larger, bolder title (font-semibold → text-lg font-bold)
- ✅ Better text hierarchy with explicit line heights
- ✅ Added footer section with separator
- ✅ Structured action button with hover states

---

### Example 4: Background Color

**Before:**
```jsx
<main className="flex-1 overflow-y-auto bg-white p-6">
  <Outlet />
</main>
```

**After:**
```jsx
<main className="flex-1 overflow-y-auto bg-neutral-50 p-8">
  <Outlet />
</main>
```

**Changes:**
- ✅ Changed from white to neutral-50 (softer, less harsh)
- ✅ Increased padding (p-6 → p-8)
- ✅ Creates better contrast with white cards

---

### Example 5: Filter Chips

**Before:**
```jsx
<button className="px-2 py-1 rounded text-sm border">
  Filter
</button>
```

**After:**
```jsx
{/* Inactive */}
<button className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300">
  All Sources
</button>

{/* Active */}
<button className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all bg-[#FF385C] text-white shadow-sm">
  Vendor
</button>
```

**Changes:**
- ✅ More generous padding (px-2 py-1 → px-3 py-1.5)
- ✅ Increased border radius (rounded → rounded-lg)
- ✅ Added font-medium for clarity
- ✅ Explicit colors (bg-white, text-neutral-600)
- ✅ Softer borders (border-neutral-200)
- ✅ Clear active state with primary color and shadow
- ✅ Smooth transitions

---

## Animation Guidelines

### Transitions
```jsx
transition-all duration-200      // Standard for most interactions
transition-colors                // Text color changes only
transition-opacity duration-200  // Fade in/out
```

### Motion Library (Framer Motion)
```jsx
// Card entrance
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, delay: index * 0.05 }}
>
```

**Stagger Pattern:**
- Duration: 0.3s
- Delay: index * 0.05 (stagger cards)
- Initial state: `opacity: 0, y: 20`
- Final state: `opacity: 1, y: 0`

---

## Accessibility

### Focus Indicators
All interactive elements must have visible focus states:
```jsx
focus:outline-none focus:ring-4 focus:ring-[#FF385C]/10
```

### Touch Targets
Minimum touch target size: **44px × 44px** (WCAG AAA)
- Buttons: `h-11` (44px) minimum
- Inputs: `h-12` (48px)
- Icon buttons: `p-2` with icon `h-4 w-4` (min 32px, acceptable for secondary actions)

### Color Contrast
- **Text on white**: neutral-800 (high contrast)
- **Secondary text**: neutral-500 (7:1 AAA)
- **Primary button**: #FF385C background, white text (AAA compliant)
- **Placeholder text**: neutral-400 (meets AA, aim for AAA in critical contexts)

### ARIA Labels
All icon-only buttons require `aria-label`:
```jsx
<button aria-label="Edit project" title="Edit project">
  <Edit2 className="h-4 w-4" />
</button>
```

---

## Implementation Checklist

When creating a new component or page, verify:

- [ ] Background is `bg-neutral-50` for pages, `bg-white` for cards
- [ ] Borders are `border-neutral-100` or `border-neutral-200`
- [ ] Border radius is `rounded-xl` (12px) for interactive elements, `rounded-2xl` (16px) for cards
- [ ] Text hierarchy uses `text-3xl font-bold` for headings, `text-lg font-bold` for card titles
- [ ] Secondary text is `text-neutral-500`
- [ ] Primary actions use `bg-[#FF385C] hover:bg-[#E31C5F]`
- [ ] Focus states have `focus:ring-4 focus:ring-[#FF385C]/10`
- [ ] Transitions are `transition-all duration-200`
- [ ] Spacing follows 8px grid (gap-6, p-6, space-y-8)
- [ ] Icons are `h-5 w-5` for buttons, `h-6 w-6` for containers
- [ ] Empty states have icon, title, and description
- [ ] Loading states show spinner with descriptive text
- [ ] All touch targets are minimum 44px tall
- [ ] Icon buttons have `aria-label` and `title` attributes

---

## Files Updated (Reference)

The following files demonstrate the Claude.ai design system:

1. **MainLayout.tsx** (`/ui-tier/shell/src/components/Layout/MainLayout.tsx`)
   - Page background: `bg-neutral-50`
   - Generous padding: `p-8`

2. **ProjectList.tsx** (`/ui-tier/mfe-projects/src/views/ProjectList.tsx`)
   - Complete implementation of Claude.ai aesthetic
   - Page headers, search bars, cards, empty states
   - Status badges, icon containers, hover actions

3. **CatalogBrowser.tsx** (`/ui-tier/mfe-evaluations/src/components/EvaluationCatalog/CatalogBrowser.tsx`)
   - Filter chips pattern
   - Section headers with counts
   - Category grouping

4. **EvaluationCard.tsx** (`/ui-tier/mfe-evaluations/src/components/EvaluationCatalog/EvaluationCard.tsx`)
   - Selected/unselected card states
   - Checkbox pattern
   - Tag display

---

## Version History

- **v2.0** (2025-10-08): Claude.ai-inspired update with increased spacing, softer borders, larger typography
- **v1.0** (2025-10-06): Initial Airbnb-style design system

---

## Questions or Contributions

For questions about the design system or to propose changes:
1. Review this document first
2. Check existing components for patterns
3. Ensure WCAG AAA compliance
4. Follow the 8px grid system
5. Test on mobile and desktop viewports

**Principle**: When in doubt, err on the side of more whitespace and softer visual treatment.
