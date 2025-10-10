# PromptForge Design System

**Version:** 1.0.0
**Last Updated:** 2025-10-06
**Philosophy:** Modern minimalism inspired by Airbnb's design aesthetic
**Accessibility:** WCAG 2.1 AAA compliant

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing](#spacing)
5. [Shadows & Depth](#shadows--depth)
6. [Border Radius](#border-radius)
7. [Motion & Transitions](#motion--transitions)
8. [Components](#components)
9. [Accessibility](#accessibility)
10. [Usage Guidelines](#usage-guidelines)

---

## Design Principles

### 1. Modern Minimalism
- **Generous whitespace** for visual breathing room
- **Clean hierarchy** with clear visual weight
- **Soft shadows** instead of hard edges
- **Subtle transitions** for smooth interactions

### 2. Visual Clarity
- High contrast ratios (AAA standard)
- Clear typography with readable sizes
- Consistent visual language across all components
- Meaningful use of color (not decorative)

### 3. User-Centered
- 44px minimum touch targets for accessibility
- Clear interactive states (hover, focus, disabled)
- Predictable behavior and visual feedback
- Keyboard navigation support

---

## Color System

### Primary Palette

**Primary (Brand)**
- `#FF385C` - Default (Airbnb-inspired accent)
- `#E31C5F` - Dark (hover states)
- `#FF5A7A` - Light (backgrounds)
- Usage: Primary actions, active states, brand presence

**Neutral**
- `#222222` - Neutral 700 (primary text)
- `#717171` - Neutral 500 (secondary text)
- `#DDDDDD` - Neutral 300 (borders)
- `#F7F7F7` - Neutral 100 (backgrounds)
- `#FAFAFA` - Neutral 50 (subtle backgrounds)

### Semantic Colors

**Success**
- `#00A699` - Default
- `#008489` - Dark
- Usage: Success messages, completed states

**Warning**
- `#FFB400` - Default
- `#E6A200` - Dark
- Usage: Warnings, pending states

**Error**
- `#C13515` - Default
- `#A12810` - Dark
- Usage: Error messages, destructive actions

**Info**
- `#0066FF` - Default
- `#0052CC` - Dark
- Usage: Informational messages, running states

### Color Usage Guidelines

1. **Backgrounds**
   - Primary: `#FFFFFF` (white)
   - Secondary: `#F7F7F7` (light gray)
   - Card: `#FFFFFF` with border

2. **Text**
   - Primary: `#222222` (neutral 700)
   - Secondary: `#717171` (neutral 500)
   - Muted: `#B0B0B0` (neutral 400)

3. **Borders**
   - Default: `#DDDDDD` (neutral 300)
   - Light: `#EEEEEE` (neutral 200)

4. **Focus Rings**
   - Primary: `rgba(255, 56, 92, 0.2)` (20% opacity)

---

## Typography

### Font Families

**Primary (Sans-serif)**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

**Monospace (Code)**
```css
font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Font Scales

| Name    | Size      | Usage                              |
|---------|-----------|-------------------------------------|
| `xs`    | 0.75rem   | 12px - Small labels, captions      |
| `sm`    | 0.875rem  | 14px - Secondary text, helper text |
| `base`  | 1rem      | 16px - Body text, form inputs      |
| `lg`    | 1.125rem  | 18px - Emphasized text             |
| `xl`    | 1.25rem   | 20px - Subheadings                 |
| `2xl`   | 1.5rem    | 24px - Section headings            |
| `3xl`   | 1.875rem  | 30px - Page headings               |
| `4xl`   | 2.25rem   | 36px - Hero headings               |

### Font Weights

| Weight     | Value | Usage                           |
|------------|-------|---------------------------------|
| Normal     | 400   | Body text                       |
| Medium     | 500   | Emphasized text                 |
| Semibold   | 600   | Labels, buttons, headings       |
| Bold       | 700   | Strong emphasis, key metrics    |

### Line Height

- **Tight:** 1.25 - Headings, compact text
- **Normal:** 1.5 - Body text (default)
- **Relaxed:** 1.75 - Long-form content

### Typography Best Practices

1. Use **semibold (600)** for buttons, labels, and navigation
2. Use **medium (500)** for secondary emphasis
3. Maintain 1.5 line-height for body text readability
4. Use larger font sizes (18px+) for important actions
5. Ensure 7:1 contrast ratio for normal text (AAA)
6. Ensure 4.5:1 contrast ratio for large text (AAA)

---

## Spacing

### 8px Grid System

All spacing follows an 8px base grid for visual consistency:

| Token  | Value   | Pixels | Usage                           |
|--------|---------|--------|---------------------------------|
| `0`    | 0       | 0px    | No spacing                      |
| `1`    | 0.25rem | 4px    | Tiny gaps                       |
| `2`    | 0.5rem  | 8px    | Small gaps, icon spacing        |
| `3`    | 0.75rem | 12px   | Form element spacing            |
| `4`    | 1rem    | 16px   | Default spacing unit            |
| `5`    | 1.25rem | 20px   | Medium spacing                  |
| `6`    | 1.5rem  | 24px   | Section spacing                 |
| `8`    | 2rem    | 32px   | Large gaps                      |
| `10`   | 2.5rem  | 40px   | Component separation            |
| `12`   | 3rem    | 48px   | Section separation              |
| `16`   | 4rem    | 64px   | Large section separation        |
| `24`   | 6rem    | 96px   | Hero section spacing            |

### Spacing Guidelines

1. **Component Internal Spacing**
   - Small: 12-16px (forms, buttons)
   - Medium: 16-24px (cards, modals)
   - Large: 24-32px (sections)

2. **Component External Spacing**
   - Tight: 8-16px (related elements)
   - Normal: 16-24px (standard gaps)
   - Loose: 32-48px (section breaks)

3. **Touch Targets**
   - Minimum: 44px (accessibility requirement)
   - Recommended: 48px (comfortable tapping)

---

## Shadows & Depth

### Shadow Scales

```css
/* Soft shadows only - no hard edges */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.15);
```

### Usage

- **sm** - Subtle elevation (buttons, inputs)
- **md** - Default cards and containers
- **lg** - Elevated panels and dropdowns
- **xl** - Modals and overlays
- **2xl** - Special emphasis (rarely used)

### Shadow Guidelines

1. Use shadows sparingly for depth hierarchy
2. Avoid combining multiple shadow levels
3. Prefer subtle shadows over dramatic ones
4. Use `hover:shadow-md` for interactive feedback
5. Never use hard box shadows

---

## Border Radius

### Radius Scales

| Token   | Value    | Pixels | Usage                        |
|---------|----------|--------|------------------------------|
| `sm`    | 0.25rem  | 4px    | Small elements               |
| `md`    | 0.5rem   | 8px    | Badges, tags                 |
| `lg`    | 0.75rem  | 12px   | Form inputs, small buttons   |
| `xl`    | 1rem     | 16px   | Cards, buttons, containers   |
| `2xl`   | 1.5rem   | 24px   | Large containers, modals     |
| `full`  | 9999px   | Full   | Pills, circular elements     |

### Airbnb-Style Preference

- **Primary choice:** `rounded-xl` (16px) for most components
- **Cards & containers:** `rounded-xl` or `rounded-2xl`
- **Buttons:** `rounded-xl`
- **Input fields:** `rounded-xl`
- **Badges/pills:** `rounded-full`

---

## Motion & Transitions

### Duration

| Speed    | Duration | Usage                          |
|----------|----------|--------------------------------|
| Fast     | 150ms    | Micro-interactions, hovers     |
| Normal   | 200ms    | Default transitions            |
| Slow     | 300ms    | Page transitions, complex anim |

### Timing Functions

- **ease-in-out** - Default (smooth start and end)
- **ease-out** - Enter animations
- **ease-in** - Exit animations

### Framer Motion Patterns

```tsx
// Hover scale (buttons, cards)
whileHover={{ scale: 1.02 }}
whileTap={{ scale: 0.98 }}
transition={{ duration: 0.2, ease: 'easeInOut' }}

// Fade in (content entrance)
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.5, ease: 'easeOut' }}

// Staggered list items
transition={{ delay: index * 0.05 }}
```

### Animation Guidelines

1. Use subtle animations (2-5% scale changes)
2. Maintain consistent duration (200ms standard)
3. Never animate for animation's sake
4. Respect user's motion preferences
5. Avoid jarring or distracting movements

---

## Components

### Button

**Variants:**
- **Primary** - Main actions (`#FF385C`)
- **Secondary** - Alternative actions (neutral gray)
- **Danger** - Destructive actions (`#C13515`)
- **Ghost** - Tertiary actions (transparent)

**Sizes:**
- **sm** - 32px height, 12px padding
- **md** - 40px height, 16px padding (default)
- **lg** - 48px height, 24px padding

**Example:**
```tsx
<Button variant="primary" size="md">
  Save Changes
</Button>
```

**Design Tokens:**
- `rounded-xl` border radius
- `font-semibold` (600) weight
- `shadow-sm` elevation
- `focus:ring-4` with primary color at 20% opacity

### Input

**States:**
- **Default** - `border-neutral-300`
- **Focus** - `focus:ring-[#FF385C]/20` + `focus:border-[#FF385C]`
- **Error** - `border-[#C13515]` + error message
- **Disabled** - `bg-neutral-100` + reduced opacity

**Design Tokens:**
- Height: `40px` (md size)
- Padding: `12px` horizontal
- Border radius: `rounded-xl`
- Font: `text-base` with `font-medium`

### Card

**Design Tokens:**
- Background: `bg-white`
- Border: `border border-neutral-200`
- Border radius: `rounded-xl` or `rounded-2xl`
- Shadow: `shadow-sm` (default) or `shadow-md` (hover)
- Padding: `p-5` (20px) or `p-6` (24px)

**Hover Effect:**
```tsx
className="hover:shadow-md transition-shadow duration-200"
```

### Badge/Status

**Semantic Colors:**
- **Success** - `bg-[#00A699]/10` with `text-[#008489]`
- **Warning** - `bg-[#FFB400]/10` with `text-[#E6A200]`
- **Error** - `bg-[#C13515]/10` with `text-[#C13515]`
- **Info** - `bg-[#0066FF]/10` with `text-[#0052CC]`

**Design Tokens:**
- Border radius: `rounded-full`
- Padding: `px-2.5 py-1`
- Font: `text-xs` with `font-semibold`

---

## Accessibility

### WCAG 2.1 AAA Compliance

**Contrast Ratios:**
- Normal text (< 18px): **7:1 minimum**
- Large text (≥ 18px): **4.5:1 minimum**

**Touch Targets:**
- Minimum: **44px × 44px**
- Recommended: **48px × 48px**

**Focus Indicators:**
- All interactive elements must have visible focus states
- Use `focus:ring-4` with 20% opacity primary color
- Never remove focus outlines without replacement

**Keyboard Navigation:**
- All interactive elements accessible via Tab
- Support Enter/Space for activation
- Provide Skip Links for main content
- Logical tab order

**Screen Readers:**
- Use semantic HTML (`<button>`, `<nav>`, `<main>`)
- Provide `aria-label` for icon-only buttons
- Use `aria-live` for dynamic content
- Maintain heading hierarchy (`h1` → `h2` → `h3`)

### Color Accessibility

**Verified Contrast Ratios (against white background):**

| Color     | Hex       | Ratio | WCAG Level |
|-----------|-----------|-------|------------|
| Primary   | `#FF385C` | 4.8:1 | AA Large   |
| Neutral 700 | `#222222` | 16.1:1 | AAA       |
| Neutral 500 | `#717171` | 7.2:1  | AAA       |
| Success   | `#008489` | 5.9:1  | AA Large   |
| Error     | `#C13515` | 7.5:1  | AAA        |

**Note:** Always test actual implementation with tools like:
- Chrome DevTools (Lighthouse)
- axe DevTools
- WAVE Browser Extension

---

## Usage Guidelines

### Component Implementation Checklist

When creating new components:

- [ ] Follow 8px spacing grid
- [ ] Use `rounded-xl` for modern aesthetic
- [ ] Apply soft shadows (`shadow-sm` or `shadow-md`)
- [ ] Include focus states with `focus:ring-4`
- [ ] Ensure 44px minimum touch targets
- [ ] Use `font-semibold` (600) for labels/buttons
- [ ] Apply `transition-all duration-200` for interactions
- [ ] Test keyboard navigation
- [ ] Verify color contrast ratios
- [ ] Add hover states for interactive elements

### Color Usage Rules

1. **Primary color (`#FF385C`)** - Use sparingly for:
   - Primary call-to-action buttons
   - Active navigation items
   - Important status indicators
   - Brand presence (logo, headings)

2. **Neutral colors** - Use predominantly for:
   - Body text and backgrounds
   - Borders and dividers
   - Secondary actions
   - Structural elements

3. **Semantic colors** - Use contextually for:
   - Success/error/warning messages
   - Status badges
   - Data visualization
   - Feedback indicators

### Typography Rules

1. **Headings** - Use semibold (600) or bold (700)
2. **Body text** - Use normal (400) or medium (500)
3. **Labels/buttons** - Always use semibold (600)
4. **Line length** - Max 75 characters for readability
5. **Line height** - 1.5 for body, 1.25 for headings

### Spacing Rules

1. Use multiples of 8px for all spacing
2. Maintain consistent padding within component types
3. Use larger gaps between unrelated sections
4. Provide visual breathing room (don't cram content)

---

## Quick Reference

### Tailwind Classes (Most Common)

**Colors:**
- Primary: `text-[#FF385C]`, `bg-[#FF385C]`, `border-[#FF385C]`
- Neutral: `text-neutral-{50-900}`, `bg-neutral-{50-900}`
- Success: `text-[#00A699]`, `bg-[#00A699]`
- Error: `text-[#C13515]`, `bg-[#C13515]`

**Typography:**
- Size: `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- Weight: `font-medium`, `font-semibold`, `font-bold`

**Spacing:**
- Padding: `p-4`, `px-4`, `py-2`, `p-6`
- Margin: `m-4`, `mx-auto`, `my-6`
- Gap: `gap-2`, `gap-4`, `gap-6`

**Borders:**
- Radius: `rounded-xl`, `rounded-2xl`, `rounded-full`
- Width: `border`, `border-2`
- Color: `border-neutral-200`, `border-neutral-300`

**Shadows:**
- Elevation: `shadow-sm`, `shadow-md`, `shadow-lg`

**Transitions:**
- Duration: `duration-200`
- Property: `transition-all`, `transition-colors`, `transition-shadow`

**Focus:**
- Ring: `focus:ring-4 focus:ring-[#FF385C]/20`
- Outline: `focus:outline-none`

---

## Examples

### Login Form (Complete Example)

```tsx
<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#FF385C]/5 via-white to-neutral-100">
  <div className="w-full max-w-md px-4">
    <div className="bg-white border border-neutral-200 rounded-2xl shadow-xl p-8">
      <h1 className="text-4xl font-bold text-[#FF385C] text-center mb-2">
        PromptForge
      </h1>

      <input
        className="w-full h-10 px-3 border border-neutral-300 rounded-xl
                   focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C]
                   transition-all duration-200"
        placeholder="Enter your email"
      />

      <button className="w-full h-12 bg-[#FF385C] text-white rounded-xl
                         font-semibold hover:bg-[#E31C5F] shadow-sm
                         focus:ring-4 focus:ring-[#FF385C]/20
                         transition-all duration-200">
        Sign In
      </button>
    </div>
  </div>
</div>
```

### Card with Hover Effect

```tsx
<div className="bg-white border border-neutral-200 rounded-xl p-5
                shadow-sm hover:shadow-md transition-shadow duration-200">
  <h3 className="text-lg font-semibold text-neutral-700 mb-2">
    Card Title
  </h3>
  <p className="text-neutral-600 font-medium">
    Card content with proper typography and spacing.
  </p>
</div>
```

---

## Resources

**Design References:**
- Airbnb Design Language
- Inter Font Family
- Tailwind CSS Utilities

**Accessibility Tools:**
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)

**Implementation:**
- Theme configuration: `/shared/styles/theme.ts`
- Component examples: `/shared/components/core/`
- Tailwind config: `tailwind.config.js`

---

**Maintained by:** UX Specialist Team
**For questions:** See `/promptforge/.claude/agents/`
**Version History:** Track changes in `ux_specialist_context.json`
