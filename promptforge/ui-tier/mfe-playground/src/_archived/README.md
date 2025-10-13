# Archived Components

This directory contains deprecated/replaced components that have been removed from the active codebase.

---

## App.tsx.backup

**Archived**: 2025-10-13
**Reason**: Replaced by `PlaygroundEnhanced.tsx`

### Why Replaced

The original `App.tsx` component had a limited feature set:
- Single "Prompt" field (no separation of system/user prompts)
- Missing: Title, System Prompt, Intent, Tone, Top K parameter
- Missing: Evaluation selector
- Basic history view (no expand/collapse)
- Path-based deep linking (`/session/:id`)

### Replacement

`PlaygroundEnhanced.tsx` provides all requested features:
- ✅ Prompt Title (required field)
- ✅ System Prompt (separate multi-line textarea)
- ✅ User Prompt (separate multi-line textarea)
- ✅ Intent & Tone (metadata fields)
- ✅ All parameters (Temperature, Max Tokens, Top P, Top K)
- ✅ Evaluation selector (multi-select)
- ✅ Enhanced history view (expandable cards showing all 15+ fields)
- ✅ Query param deep linking (`?session=id`)
- ✅ Complete session restoration

### Router Change

**Before** (`src/AppRouter.tsx`):
```typescript
import App from './App';
<Route index element={<App />} />
```

**After**:
```typescript
import PlaygroundEnhanced from './PlaygroundEnhanced';
<Route index element={<PlaygroundEnhanced />} />
```

### Recovery

If you need to restore the old component:
```bash
cp src/_archived/App.tsx.backup src/App.tsx
# Then update AppRouter.tsx to import './App' instead of './PlaygroundEnhanced'
```

---

**Documentation**:
- Implementation details: `/PLAYGROUND_REFINEMENTS_IMPLEMENTATION.md`
- Router fix: `/ROUTER_FIX_SUMMARY.md`
- Deep link fix: `/DEEP_LINK_FIX.md`
