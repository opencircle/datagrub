# PromptForge UX Quick Wins
**Date**: 2025-10-12
**Priority**: Immediate Actions for Next Sprint

---

## Critical Fixes (Must Do - 2 Days)

### 1. Primary Color Conflict
**File**: `/promptforge/ui-tier/shell/src/index.css`
**Issue**: Shell uses dark blue (`hsl(222.2 47.4% 11.2%)`), MFEs use pink (`#FF385C`)

**Fix**:
```css
/* Line 13-14: Change from dark blue to brand pink */
--primary: 0 66% 60%;              /* #FF385C in HSL */
--primary-foreground: 210 40% 98%; /* Keep white */
```

**Impact**: Immediate brand consistency, 262 components affected

---

### 2. Color Naming Standardization
**Files**: All `*.tsx` files in ui-tier
**Issue**: `gray-*` and `neutral-*` used interchangeably

**Fix**: Global find/replace
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier

# Replace in all TSX files
find . -name "*.tsx" -type f -exec sed -i '' 's/text-gray-/text-neutral-/g' {} +
find . -name "*.tsx" -type f -exec sed -i '' 's/bg-gray-/bg-neutral-/g' {} +
find . -name "*.tsx" -type f -exec sed -i '' 's/border-gray-/border-neutral-/g' {} +
find . -name "*.tsx" -type f -exec sed -i '' 's/hover:bg-gray-/hover:bg-neutral-/g' {} +
```

**Impact**: Developer clarity, 45 files affected

---

### 3. Accessibility - ARIA Live Regions
**Files**:
- `/mfe-insights/src/components/InsightsPage.tsx`
- `/mfe-insights/src/components/sections/HistorySection.tsx`
- `/mfe-playground/src/PlaygroundEnhanced.tsx`

**Fix**: Add screen reader announcements
```tsx
// Add to InsightsPage (after line 85)
<div role="status" aria-live="polite" className="sr-only">
  {resultState.isLoading && "Analyzing transcript, please wait"}
  {resultState.error && `Error: ${resultState.error}`}
  {resultState.summary && "Analysis complete"}
</div>
```

**Impact**: Screen reader users can track progress (WCAG AAA compliance)

---

### 4. Colorblind Accessibility - Icon Indicators
**File**: `/mfe-insights/src/components/comparison/ComparisonResults.tsx`

**Fix**: Add directional icons to cost/quality differences
```tsx
// Line 166-169: Add TrendingUp/TrendingDown icons
import { TrendingUp, TrendingDown } from 'lucide-react';

<div className="flex items-baseline gap-2">
  {costDiff > 0 ? (
    <TrendingUp className="h-4 w-4 text-red-600" />
  ) : (
    <TrendingDown className="h-4 w-4 text-green-600" />
  )}
  <span className={`text-2xl font-bold ${
    costDiff > 0 ? 'text-red-600' : 'text-green-600'
  }`}>
    {costDiff > 0 ? '+' : ''}${costDiff.toFixed(4)}
  </span>
</div>
```

**Impact**: 8% of male population (colorblind users) can differentiate metrics

---

## High Priority (Should Do - 3 Days)

### 5. Shared Button Component
**File**: `/promptforge/ui-tier/shared/components/core/Button.tsx`

**Action**: Update existing component with design system patterns
```tsx
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'neutral' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  // ... existing props
}

const variants = {
  primary: 'bg-[#FF385C] text-white hover:bg-[#E31C5F] focus:ring-[#FF385C]/20',
  secondary: 'bg-white border-2 border-[#FF385C] text-[#FF385C] hover:bg-pink-50',
  neutral: 'bg-neutral-100 border border-neutral-300 text-neutral-700 hover:bg-neutral-200',
  destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500/20',
};

const sizes = {
  sm: 'h-10 px-4 text-sm',
  md: 'h-12 px-6 text-base',
  lg: 'h-14 px-8 text-lg',
};
```

**Migration**: Replace inline button classes in 45+ files

---

### 6. Border Radius Standardization
**Files**: All component files
**Issue**: Mix of `rounded-lg`, `rounded-xl`, `rounded-2xl`

**Decision Matrix**:
```
rounded-full  → Badges, avatars, pills
rounded-lg    → Small tags, chips (< 32px height)
rounded-xl    → DEFAULT: Buttons, inputs, cards, modals
rounded-2xl   → Large hero cards only (reserved)
```

**Find/Replace**:
```bash
# Cards and modals: lg → xl
sed -i '' 's/rounded-lg p-6/rounded-xl p-6/g' **/*.tsx
sed -i '' 's/rounded-lg shadow/rounded-xl shadow/g' **/*.tsx
```

---

## Medium Priority (Nice to Have - 1 Week)

### 7. Create Shared Card Component
**File**: `/promptforge/ui-tier/shared/components/core/Card.tsx` (NEW)

```tsx
export interface CardProps {
  variant?: 'default' | 'hover' | 'outlined';
  padding?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  children,
  className,
}) => {
  const variants = {
    default: 'bg-white border border-neutral-200 rounded-xl',
    hover: 'bg-white border border-neutral-100 rounded-xl hover:shadow-lg transition-all',
    outlined: 'bg-transparent border-2 border-neutral-200 rounded-xl',
  };

  const paddings = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div className={`${variants[variant]} ${paddings[padding]} ${className}`}>
      {children}
    </div>
  );
};
```

---

### 8. Typography Scale Documentation
**File**: `/promptforge/ui-tier/shared/docs/TYPOGRAPHY.md` (NEW)

Create reference guide:
```md
# Typography System

## Usage

### Headings
text-3xl font-bold text-neutral-800     // Page titles (H1)
text-2xl font-bold text-neutral-700     // Section headers (H2)
text-xl font-bold text-neutral-700      // Card titles (H3)
text-lg font-semibold text-neutral-700  // Subsections (H4)

### Body
text-base text-neutral-700              // Primary body
text-sm text-neutral-600                // Secondary text
text-xs text-neutral-500                // Captions, helper text

### Monospace
font-mono text-sm text-neutral-700      // Code, IDs, technical data
```

---

## Effort Estimate

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Fix primary color | Critical | 0.5 days | High |
| Standardize gray→neutral | Critical | 0.5 days | High |
| Add ARIA live regions | Critical | 0.5 days | Critical (A11y) |
| Add colorblind icons | Critical | 0.5 days | High (A11y) |
| Update Button component | High | 1.5 days | High |
| Standardize border radius | High | 1 day | Medium |
| Create Card component | Medium | 1 day | Medium |
| Document typography | Medium | 0.5 days | Low |

**Total**: 6 days for all quick wins

---

## Validation Checklist

After implementing fixes:

### Visual QA
- [ ] Shell sidebar uses `#FF385C` for active links
- [ ] All buttons use `rounded-xl` consistently
- [ ] No `gray-*` classes remain (use `neutral-*`)
- [ ] Cost/quality indicators have icons AND color

### Accessibility QA
- [ ] Screen reader announces "Analyzing transcript" during loading
- [ ] Screen reader announces errors
- [ ] Colorblind simulator shows icons for cost differences
- [ ] All interactive elements have focus rings

### Browser Testing
- [ ] Chrome, Firefox, Safari
- [ ] Dark mode (if Shell implements it)
- [ ] Mobile responsive (320px, 768px, 1024px)

---

**Created**: 2025-10-12
**Owner**: UX Specialist Agent
**Review**: Quarterly
