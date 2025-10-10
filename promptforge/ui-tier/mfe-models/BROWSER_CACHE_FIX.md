# Browser Cache Fix for Model Dropdowns

**Issue**: New models (GPT-4.1, GPT-4o, Claude Opus 4.1) not appearing in model selection dropdowns
**Root Cause**: Browser caching the API catalog response
**Status**: ✅ **FIXED**

---

## Problem

After updating the database with new OpenAI and Anthropic models, the UI dropdowns were still showing the old model lists. The browser was caching the `/api/v1/model-providers/catalog` endpoint response.

---

## Solution

### 1. Added Cache-Busting to API Calls

**File**: `/ui-tier/mfe-models/src/services/providerService.ts`

**Changes** (Lines 64-77):
```typescript
export const getProviderCatalog = async (
  providerType?: string,
  isActive: boolean = true
): Promise<ProviderMetadataListResponse> => {
  const params = new URLSearchParams();
  if (providerType) params.append('provider_type', providerType);
  params.append('is_active', String(isActive));
  // Add timestamp to prevent browser caching
  params.append('_t', Date.now().toString());

  const url = `${API_V1}/model-providers/catalog?${params.toString()}`;
  const response = await fetch(url, {
    cache: 'no-store', // Prevent browser from caching the response
  });
```

**What Changed**:
1. ✅ Added `_t` timestamp parameter to make each request unique
2. ✅ Added `cache: 'no-store'` option to fetch() to disable browser cache
3. ✅ Ensures fresh data on every modal open

---

## How to See the New Models

### Option 1: Hard Refresh (Recommended)
**macOS**: `Cmd + Shift + R`
**Windows/Linux**: `Ctrl + Shift + R`

This will:
- Clear cached JavaScript bundles
- Reload the updated `providerService.ts` code
- Fetch fresh catalog data with new models

### Option 2: Clear Browser Cache
1. Open browser DevTools (`F12`)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click **Clear site data** or **Clear storage**
4. Refresh the page

### Option 3: Incognito/Private Window
- Open the application in an incognito/private browsing window
- Fresh session with no cache

---

## Verification Steps

### 1. Check API Returns New Models
```bash
curl -s "http://localhost:8000/api/v1/model-providers/catalog?is_active=true" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data['providers']:
    if p['provider_name'] == 'openai':
        print('OpenAI models:', len([f for f in p['optional_fields'] if f['name']=='default_model'][0]['options']))
    if p['provider_name'] == 'anthropic':
        print('Anthropic models:', len([f for f in p['optional_fields'] if f['name']=='default_model'][0]['options']))
"
```

**Expected Output**:
```
OpenAI models: 7
Anthropic models: 7
```

### 2. Check Browser Network Tab
1. Open browser DevTools (`F12`)
2. Go to **Network** tab
3. Open "Add Provider" modal
4. Look for request to `/api/v1/model-providers/catalog?is_active=true&_t=1234567890`
5. Verify the `_t` timestamp parameter is present
6. Check response shows new models

### 3. Check Dropdown Content
After hard refresh, when configuring a provider:

**OpenAI Dropdown** should show:
```
- gpt-4.1               ← NEW
- gpt-4.1-mini          ← NEW
- gpt-4o                ← NEW
- gpt-4o-mini           ← NEW
- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo
```

**Anthropic Dropdown** should show:
```
- claude-sonnet-4-5-20250929
- claude-opus-4-1-20250805      ← NEW
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307
```

---

## Why This Happens

### Browser Caching Behavior
1. **GET requests** to the same URL are cached by default
2. The `/api/v1/model-providers/catalog?is_active=true` URL doesn't change
3. Browser returns cached response instead of fetching fresh data
4. UI shows old model list even though database is updated

### Our Fix
1. **Timestamp parameter** (`_t`) makes each request unique
2. **cache: 'no-store'** tells browser not to cache the response
3. **Fresh data** on every modal open

---

## Technical Details

### Fetch API Cache Options
```typescript
fetch(url, {
  cache: 'no-store'  // Never cache, always fetch from network
})
```

Available cache options:
- `default` - Standard HTTP caching
- `no-store` - Never cache (what we use)
- `reload` - Always fetch from network, update cache
- `no-cache` - Check with server if cached version is valid
- `force-cache` - Use cache, fetch if not available
- `only-if-cached` - Use cache only, fail if not available

### Timestamp Cache-Busting
```typescript
params.append('_t', Date.now().toString());
// Results in: ?is_active=true&_t=1728495123456
```

Each request gets a unique timestamp, ensuring:
- No two requests have the same URL
- Browser can't return cached response
- Fresh data every time

---

## Webpack Hot Reload Note

The `providerService.ts` change requires:
- **Webpack rebuild** to bundle new code
- **Browser refresh** to load new bundle
- **Hard refresh** recommended to clear all caches

If webpack watch doesn't auto-rebuild:
```bash
# Restart webpack dev server
npm start
```

---

## Testing Checklist

- [ ] Hard refresh browser (`Cmd + Shift + R` or `Ctrl + Shift + R`)
- [ ] Open "Add Provider" modal
- [ ] Select OpenAI - verify 7 models in dropdown
- [ ] Verify GPT-4.1 and GPT-4.1-mini are present
- [ ] Select Anthropic - verify 7 models in dropdown
- [ ] Verify Claude Opus 4.1 is present
- [ ] Check Network tab - verify `_t` parameter in request
- [ ] Verify no cached response (Status should be 200, not "from disk cache")

---

## Summary

✅ **Root Cause**: Browser caching API responses
✅ **Fix**: Added timestamp cache-busting + `cache: 'no-store'`
✅ **File Changed**: `src/services/providerService.ts`
✅ **User Action**: Hard refresh browser to see new models
✅ **Prevention**: All future catalog requests will fetch fresh data

**New models will appear after hard refresh!** 🎉

---

**Generated**: 2025-10-09
**Issue**: Browser cache preventing new models from appearing
**Resolution**: Cache-busting implemented in providerService.ts
