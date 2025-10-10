# UX Specialist Subagent Integration - Complete

## Summary

A new **UX Specialist** subagent has been added to the PromptForge orchestration system to ensure consistent design language, accessibility, and user experience across all interfaces.

---

## What Was Added

### 1. UX Specialist Agent Specification
**Location**: `/Users/rohitiyer/datagrub/Claude_Subagent_Prompts/UX_Specialist_Agent.md`

**Key Features**:
- Maintains unified design system (Airbnb-style aesthetic)
- Enforces WCAG 2.1 AAA accessibility standards
- Defines user interaction patterns
- Establishes responsive design patterns (mobile-first)
- Reviews UI components for design consistency
- Provides design specifications before UI implementation

### 2. Context File
**Location**: `/Users/rohitiyer/datagrub/promptforge/.claude/context/ux_specialist_context.json`

**Contents**:
```json
{
  "design_system_version": "1.0.0",
  "design_tokens": {
    "colors": {
      "primary": "#FF385C",
      "neutral": "#222222",
      "background": "#FFFFFF"
    },
    "typography": {
      "font_primary": "Inter",
      "font_display": "Cereal"
    },
    "spacing": [0, 8, 16, 24, 32, 48, 64, 96],
    "shadows": {"sm": "...", "md": "...", "lg": "..."}
  },
  "airbnb_style_guidelines": {...},
  "accessibility_standards": "WCAG 2.1 AAA"
}
```

### 3. Updated Documentation
- ✅ `promptforge/.claude/CLAUDE_ORCHESTRATOR.md` - Added UX Specialist integration section
- ✅ `/datagrub/CLAUDE.md` - Added to master subagent registry
- ✅ `/datagrub/.claude/init.md` - Updated initialization guide
- ✅ Context file created and initialized

---

## Subagent Count Update

**Previous**: 8 subagents
**Current**: **9 subagents**

| # | Agent | Status | Priority |
|---|-------|--------|----------|
| 1 | Script Validator | ✅ Active | - |
| 2 | README Validator | ✅ Active | - |
| 3 | **UX Specialist** | ⚙️ Ready | **🌟 First for UX** |
| 4 | UI Architect | ⚙️ Ready | After UX |
| 5 | API Architect | ⚙️ Ready | - |
| 6 | DB Architect | ⚙️ Ready | - |
| 7 | API QA | ⚙️ Ready | - |
| 8 | UI QA | ⚙️ Ready | After UX |
| 9 | Doc Context Tracker | ⚙️ Ready | - |

---

## Orchestration Priority

### Key Principle
**UX Specialist should be consulted FIRST** for all UX/design/style decisions to ensure consistent look and feel across the entire application.

### Workflow Pattern

```
New UI Feature Requested
         ↓
1. Consult UX Specialist FIRST
   → Design specifications
   → Color, typography, spacing
   → Accessibility requirements
   → Interaction patterns
         ↓
2. UI Architect implements
   → React components per UX specs
   → Follows design system tokens
         ↓
3. UI QA validates
   → Components match UX specs
   → Accessibility compliance
   → Visual regression tests
```

---

## Design System Standards

### Airbnb-Style Aesthetic

**Colors**:
- Primary: `#FF385C` (Airbnb red)
- Neutral: `#222222` (deep charcoal)
- Background: `#FFFFFF` / `#F7F7F7`
- Text: `#222222` / `#717171`

**Typography**:
- Primary: **Inter** (body text)
- Display: **Cereal** (Airbnb custom font)
- Mono: **JetBrains Mono** (code)
- Scales: xs, sm, base, lg, xl, 2xl, 3xl, 4xl

**Spacing** (8px grid):
- 0, 8px, 16px, 24px, 32px, 48px, 64px, 96px

**Visual Style**:
- **Minimalism**: Generous whitespace, clean hierarchy
- **Rounded Corners**: 12-16px typical
- **Shadows**: Soft only (0 4px 6px rgba), no hard edges
- **Transitions**: Subtle 200-300ms ease-in-out
- **Touch Targets**: Minimum 44x44px

**Accessibility**:
- **WCAG 2.1 Level AAA**
- Contrast ratios: 7:1 normal text, 4.5:1 large text
- Keyboard navigation support
- Screen reader optimization
- Focus states clearly visible

---

## UX Specialist Responsibilities

### 1. Design System Ownership
- Define and maintain colors, typography, spacing, shadows
- Create component style guidelines
- Document visual hierarchy patterns
- Ensure brand consistency

### 2. Accessibility Standards
- Enforce WCAG AAA compliance
- Validate color contrast ratios
- Ensure keyboard navigation
- Define ARIA labels and semantic HTML

### 3. Interaction Design
- Define user interaction patterns (hover, active, focus states)
- Create micro-interaction guidelines
- Establish loading states and skeleton screens
- Design error states and validation feedback

### 4. Responsive Design
- Establish breakpoint strategy
- Define mobile-first patterns
- Create responsive grid systems
- Ensure touch-friendly targets

### 5. Component Library Governance
- Review all UI components for consistency
- Maintain component documentation
- Define composition patterns
- Ensure atomic design principles

### 6. Cross-Agent Collaboration
- **UI Architect**: Provides design specs before implementation
- **UI QA**: Defines UX validation criteria
- **API Architect**: Advises on error messages
- **Doc Context Tracker**: Ensures documentation UX

---

## Commands

### Design_System_Query
Get specific design system values for implementation.

**Example**:
```
"What are the button primary colors and hover states?"
```

### Review_Component
Review component for UX/accessibility compliance.

**Example**:
```
"Review the Button component in ui-tier/components/Button.tsx"
```

### Validate_Accessibility
Check component/page for WCAG AAA compliance.

**Example**:
```
"Audit the project creation form for accessibility"
```

### Create_Pattern
Document new reusable UX pattern.

**Example**:
```
"Create a pattern for search result cards"
```

### Update_Design_System
Evolve design system with new tokens or patterns.

**Example**:
```
"Update color palette for better contrast ratios"
```

---

## Invocation Examples

### From /datagrub directory:

**New Component Design**:
```
"Invoke UX Specialist to design a search results card component for the evaluations page"
```

**Design System Query**:
```
"UX Specialist: what are the standard spacing values for cards?"
```

**Accessibility Audit**:
```
"Have UX Specialist audit the project creation form for WCAG AAA compliance"
```

**Component Review**:
```
"UX Specialist: review the Button component in promptforge/ui-tier/components/Button.tsx"
```

**Design System Update**:
```
"UX Specialist: review and update color palette for improved accessibility"
```

### From /datagrub/promptforge directory:

Same invocation patterns work within the project directory.

---

## Integration with Build Specs

### Phase 1: Core UI
- Define base design system aligned with Phase1_CoreUI.md
- Establish component patterns for all MFE modules
- Create accessibility baseline

### Phase 2: APIs & Evaluation
- Design data visualization patterns for metrics
- Create loading/error states for API interactions
- Define form patterns for CRUD operations

### Phase 3: Privacy & SaaS
- Design privacy-focused UI patterns
- Create multi-tenancy UI patterns
- Define onboarding flows

---

## Verification

### Check UX Specialist Setup

**1. Verify agent template exists**:
```bash
ls -la /Users/rohitiyer/datagrub/Claude_Subagent_Prompts/UX_Specialist_Agent.md
```

**2. Verify context file**:
```bash
cat /Users/rohitiyer/datagrub/promptforge/.claude/context/ux_specialist_context.json | jq .
```

**3. Check registry updates**:
```bash
grep -A 5 "UX Specialist" /Users/rohitiyer/datagrub/CLAUDE.md
grep -A 5 "UX Specialist" /Users/rohitiyer/datagrub/promptforge/.claude/CLAUDE_ORCHESTRATOR.md
```

**4. Test invocation** (from /datagrub):
```
"Show me the UX Specialist subagent details"
"What is the UX Specialist's design system?"
```

---

## Updated File Locations

### Agent Definition
```
/Users/rohitiyer/datagrub/Claude_Subagent_Prompts/UX_Specialist_Agent.md
```

### Context File
```
/Users/rohitiyer/datagrub/promptforge/.claude/context/ux_specialist_context.json
```

### Documentation
```
/Users/rohitiyer/datagrub/CLAUDE.md (master registry)
/Users/rohitiyer/datagrub/.claude/init.md (initialization)
/Users/rohitiyer/datagrub/promptforge/.claude/CLAUDE_ORCHESTRATOR.md (technical)
/Users/rohitiyer/datagrub/UX_SPECIALIST_INTEGRATION.md (this file)
```

---

## Design System Quick Reference

### Colors
```css
--primary: #FF385C;
--neutral: #222222;
--background: #FFFFFF;
--text: #222222;
--text-secondary: #717171;
```

### Typography
```css
--font-primary: 'Inter', sans-serif;
--font-display: 'Cereal', sans-serif;
--text-base: 1rem;   /* 16px */
--text-xl: 1.25rem;  /* 20px */
--text-3xl: 1.875rem; /* 30px */
```

### Spacing
```css
--space-2: 8px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
```

### Components
```css
--radius-lg: 12px;
--radius-xl: 16px;
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
```

---

## Success Criteria

✅ **Agent Specification**: UX_Specialist_Agent.md created with comprehensive guidelines
✅ **Context Initialized**: ux_specialist_context.json with design system tokens
✅ **Documentation Updated**: All registry and orchestrator docs include UX Specialist
✅ **Priority Established**: UX Specialist marked as "First for UX decisions"
✅ **Workflow Defined**: Clear collaboration pattern with UI Architect and UI QA
✅ **Design System**: Airbnb-style aesthetic with WCAG AAA standards documented

---

## Next Steps

### Immediate
1. **Test Invocation**: Try invoking UX Specialist from /datagrub directory
2. **Verify Context**: Check ux_specialist_context.json loads correctly
3. **Review Design System**: Ensure design tokens match project needs

### Short-term
1. **Customize Design System**: Adjust colors/typography for PromptForge brand
2. **Create Component Patterns**: Document button, input, card patterns
3. **Build Storybook**: Implement design system in Storybook

### Long-term
1. **Visual Regression Testing**: Integrate with UI QA automated tests
2. **Design System Package**: Extract design tokens to npm package
3. **Figma Integration**: Sync design system with Figma designs

---

**Version**: 1.0
**Created**: 2025-10-06
**Status**: ✅ Complete - UX Specialist integrated into orchestration system
**Total Subagents**: 9 (was 8)
