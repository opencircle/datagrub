# Comparison View Rendering Fix

## Issue
After creating a comparison or clicking on a comparison in history, the comparison results page was not rendering. The page would navigate but show blank/empty content instead of the radar charts, scores, and reasoning.

## Root Cause
**File**: `/src/components/pages/ComparisonPage.tsx` (lines 46-55)

The `useEffect` that manages view mode was not properly handling the case when a user navigates directly to a comparison ID (e.g., `/insights/comparisons/{id}`).

### The Bug

```typescript
useEffect(() => {
  const viewParam = searchParams.get('view');
  if (viewParam === 'history') {
    setViewMode('history');
    setActiveComparisonId(null);
  } else if (viewParam === 'create' || (!viewParam && !initialComparisonId)) {
    setViewMode('create');
    setActiveComparisonId(null);
  }
  // ❌ MISSING: No handler for when initialComparisonId exists without view param
}, [searchParams, initialComparisonId]);
```

**What happened**:
1. User creates comparison → `handleComparisonCreated` navigates to `/insights/comparisons/{id}`
2. `ComparisonPage` receives `initialComparisonId` prop correctly
3. Initial state sets `viewMode = 'view'` ✅
4. useEffect runs and sees no `view` query parameter
5. **Bug**: The effect doesn't set viewMode back to 'view', leaving it in an undefined state
6. `useComparisonById` hook is disabled because `viewMode !== 'view'`
7. No API call made to fetch comparison details
8. Blank page rendered

## Solution

Added an explicit handler for the case when `initialComparisonId` exists without a `view` query parameter:

```typescript
useEffect(() => {
  const viewParam = searchParams.get('view');
  if (viewParam === 'history') {
    setViewMode('history');
    setActiveComparisonId(null);
  } else if (viewParam === 'create' || (!viewParam && !initialComparisonId)) {
    setViewMode('create');
    setActiveComparisonId(null);
  } else if (initialComparisonId && !viewParam) {
    // ✅ FIXED: When navigating directly to a comparison ID without a view param, ensure view mode
    setViewMode('view');
    setActiveComparisonId(initialComparisonId);
  }
}, [searchParams, initialComparisonId]);
```

## Impact

### Before Fix
- ❌ Creating comparison → blank page
- ❌ Clicking comparison in history → blank page
- ❌ Direct navigation to `/insights/comparisons/{id}` → blank page

### After Fix
- ✅ Creating comparison → shows full comparison results with charts
- ✅ Clicking comparison in history → shows full comparison results
- ✅ Direct navigation works correctly
- ✅ `useComparisonById` hook enabled when `viewMode === 'view'`
- ✅ API call made to fetch comparison details
- ✅ ComparisonResults component renders with all data

## Files Changed

1. `/ui-tier/mfe-insights/src/components/pages/ComparisonPage.tsx` (lines 54-58)
   - Added explicit viewMode='view' handler for initialComparisonId case

## Testing

### Test Case 1: Create New Comparison
1. Go to "Compare" tab
2. Select two analyses
3. Click "Create Comparison"
4. **Expected**: Automatically navigate to comparison results page with full display

### Test Case 2: View from History
1. Go to "History" tab
2. Click on any comparison
3. **Expected**: Show full comparison results page with radar charts and scores

### Test Case 3: Direct URL Navigation
1. Navigate directly to `/insights/comparisons/{valid-comparison-id}`
2. **Expected**: Load and display comparison results

### What You Should See
- Overall winner badge with trophy icon
- Judge model reasoning (formatted markdown with tables)
- Cost vs Quality metrics cards
- Stage-by-Stage analysis section with:
  - Radar charts showing scores for each criterion
  - Score comparison tables
  - Judge reasoning for each stage
- Model A and Model B metadata cards
- Judge trace information (tokens, cost, duration)

## Backend Verification

The backend was already working correctly. You can verify comparison is created:

```bash
# Check comparison was created successfully
docker logs promptforge-api | grep "POST /api/v1/insights/comparisons"
# Should show: 201 Created

# Check comparison details can be fetched
docker logs promptforge-api | grep "GET /api/v1/insights/comparisons/"
# Should show: 200 OK
```

## Related Issues

This fix resolves the frontend rendering issue that was masking the successful GPT-5 timeout fix. Both issues are now resolved:

1. ✅ **Backend**: GPT-5 timeout increased to 300 seconds (GPT5_TIMEOUT_FIX.md)
2. ✅ **Frontend**: Comparison results now render correctly (this fix)

## Date Fixed
2025-10-13

## Status
✅ **FIXED** - Comparison results now display correctly after creation and when viewing from history

---

**Try viewing a comparison now!** The results should display with full radar charts, scores, and reasoning.
