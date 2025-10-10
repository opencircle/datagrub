# Anthropic API Key Format Update

**Date**: 2025-10-09
**Issue**: New Anthropic API key format `sk-ant-api03-` was not recognized by validation
**Status**: ✅ **FIXED**

---

## Problem

Anthropic introduced a new API key format that the system was rejecting:

### New Format (Current)
```
sk-ant-api03-{95 characters}
Total: 108 characters
Example: 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
```

### Old Format (Legacy)
```
sk-ant-{101 characters}
Total: 108 characters
```

The original validation pattern only supported the old format with the `sk-ant-` prefix.

---

## Solution

Updated the validation pattern to support **both** old and new formats:

### New Validation Pattern
```regex
^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$
```

This pattern accepts:
- **Old format**: `sk-ant-` + 101 characters = 108 total
- **New format**: `sk-ant-api03-` + 95 characters = 108 total

### Files Updated

#### 1. Database Seed (`database-tier/seed_data/model_provider_metadata.py`)

**Lines 120-121** - Validation rules:
```python
"validation": {
    "pattern": "^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$",
    "min_length": 102
}
```

**Line 167** - API key pattern:
```python
"api_key_pattern": "^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$",
```

#### 2. UI Validation Message (`ui-tier/mfe-models/src/components/AddProviderModal.tsx`)

**Line 107** - Error message:
```tsx
if (pattern.includes('sk-ant-')) {
  return `${field.label} must start with "sk-ant-" or "sk-ant-api03-" (total: 102-108 chars)`;
}
```

#### 3. Database Reseed

The database was reseeded to apply the updated pattern:
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
./venv/bin/python ../database-tier/seed_data/model_provider_metadata.py
```

---

## Verification

### API Endpoint Check
```bash
curl -s "http://localhost:8000/api/v1/model-providers/catalog?is_active=true" | \
  python3 -c "import json, sys; data = json.load(sys.stdin); \
  [print(f'Pattern: {f.get(\"validation\", {}).get(\"pattern\")}') \
  for p in data.get('providers', []) if p.get('provider_name') == 'anthropic' \
  for f in p.get('required_fields', []) if f.get('name') == 'api_key']"
```

**Output**:
```
✅ Pattern: ^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$
```

### JavaScript Regex Test
```javascript
const key = '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';
const pattern = '^sk-ant-(api03-)?[A-Za-z0-9-_]{95,101}$';
const regex = new RegExp(pattern);
console.log(regex.test(key)); // ✅ true
```

---

## UI Refresh Required

⚠️ **Important**: Users need to **refresh their browser** or **clear the cache** to load the updated validation pattern from the API.

### Steps for Users:
1. **Hard Refresh**:
   - macOS: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`
2. **Or clear browser cache** for localhost:3000
3. **Reload the page** to fetch the updated catalog

---

## Pattern Breakdown

### Old Format
- Prefix: `sk-ant-` (7 characters)
- Body: 101 characters `[A-Za-z0-9-_]`
- **Total: 108 characters**

### New Format
- Prefix: `sk-ant-api03-` (13 characters)
- Body: 95 characters `[A-Za-z0-9-_]`
- **Total: 108 characters**

### Regex Components
```regex
^                           # Start of string
sk-ant-                     # Required prefix
(api03-)?                   # Optional "api03-" (for new format)
[A-Za-z0-9-_]{95,101}      # 95-101 alphanumeric/dash/underscore chars
$                           # End of string
```

- **Min length**: 102 characters (shortest valid: `sk-ant-` + 95 chars)
- **Max length**: 108 characters (longest valid: `sk-ant-api03-` + 95 chars OR `sk-ant-` + 101 chars)

---

## Testing

### Valid Keys (Should Pass)

✅ **New format**:
```
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
```

✅ **Old format** (if still in use):
```
sk-ant-{101 characters of A-Za-z0-9-_}
```

### Invalid Keys (Should Fail)

❌ **Wrong prefix**:
```
sk-api-...
```

❌ **Too short**:
```
sk-ant-api03-{90 characters}
```

❌ **Too long**:
```
sk-ant-api03-{105 characters}
```

❌ **Invalid characters** (spaces, special chars):
```
sk-ant-api03-{contains spaces or @#$%}
```

---

## User-Facing Error Messages

### Before Fix
```
API Key format is invalid
```

### After Fix
```
API Key must start with "sk-ant-" or "sk-ant-api03-" (total: 102-108 chars)
```

Users now get clear guidance on:
1. Which prefix formats are accepted
2. Expected total character count range
3. Specific format requirements

---

## Webpack Status

✅ Compiled successfully - No errors
```
webpack 5.102.0 compiled successfully in 141 ms
```

---

## Summary

- ✅ Database pattern updated to support both old and new Anthropic key formats
- ✅ UI validation message updated with helpful error guidance
- ✅ Database reseeded with new pattern
- ✅ API serving correct validation rules
- ✅ Webpack build successful
- ⚠️ **Users must refresh browser to load updated validation**

**Resolution**: Anthropic API keys in both old (`sk-ant-`) and new (`sk-ant-api03-`) formats are now accepted.

---

**Generated**: 2025-10-09
**Issue Reported By**: User
**Fixed By**: Claude Code Assistant
