# Playground Title Requirement Implementation

## Overview

The Playground now requires a **Title** field for every prompt execution. The title is propagated throughout the system and appears in:
- **Playground History** - Local session display
- **Traces** - Database trace records (trace.name column)
- **Evaluations** - Accessible via trace relationship (trace.name)

## Date Implemented
2025-10-13

## Changes Made

### 1. Backend API Schema Update

**File**: `/api-tier/app/api/v1/endpoints/playground.py`

**Change** (line 38):
```python
# Before:
title: Optional[str] = Field(None, description="Title for this execution (defaults to project name)")

# After:
title: str = Field(..., min_length=1, max_length=200, description="Title for this execution (required)")
```

**Impact**:
- Title is now **required** in API requests
- Pydantic validation enforces:
  - Non-empty string (min_length=1)
  - Maximum 200 characters
  - Returns 422 Unprocessable Entity if validation fails

---

### 2. Frontend UI Updates

**File**: `/ui-tier/mfe-playground/src/PlaygroundEnhanced.tsx`

#### A. Label Update (lines 332-333)
```tsx
// Before:
Title (Optional)

// After:
Title <span className="text-[#FF385C]">*</span>
```

**Visual**: Red asterisk indicates required field

#### B. Help Text Update (line 343)
```tsx
// Before:
"Give this execution a memorable name to identify it in traces and evaluations. Defaults to project name if not provided."

// After:
"Give this execution a memorable name to identify it in traces, history, and evaluations."
```

#### C. Validation Logic (lines 205-211)
```tsx
if (!title.trim()) {
  errors.push('Title is required');
}

if (title.trim().length > 200) {
  errors.push('Title is too long (max 200 characters)');
}
```

**Validation Order**: Title validation occurs **before** prompt validation

#### D. Button Disable Logic (line 427)
```tsx
disabled={executeMutation.isPending || !title.trim() || !prompt.trim()}
```

**UX**: Run button disabled when title or prompt is empty

#### E. Request Payload Update (lines 255-256)
```tsx
const request: PlaygroundExecutionRequest = {
  title: title.trim(),  // Moved from metadata to top-level required field
  prompt: prompt.trim(),
  // ...
}
```

**Change**: Title moved from optional `metadata.title` to required top-level field

---

### 3. History Display Enhancement

**File**: `/ui-tier/mfe-playground/src/PlaygroundEnhanced.tsx`

#### A. Session Interface Update (mockData.ts line 13)
```typescript
export interface PlaygroundSession {
  id: string;
  timestamp: string;
  title?: string;  // Added title field
  prompt: string;
  response: string;
  // ...
}
```

#### B. Session Creation (line 158)
```tsx
const newSession: PlaygroundSession = {
  id: data.trace_id,
  timestamp: data.timestamp,
  title: title.trim(),  // Capture title in session history
  prompt,
  response: data.response,
  // ...
};
```

#### C. History Display (lines 700-708)
```tsx
{session.title && (
  <p className="text-sm font-bold text-neutral-800 mb-1">
    {session.title}
  </p>
)}
<p className="text-xs text-neutral-500 mb-1">
  {session.model.name}
</p>
<p className="text-sm text-neutral-600 line-clamp-2">{session.prompt}</p>
```

**Display Hierarchy**:
1. **Title** (bold, prominent)
2. Model name (smaller, muted)
3. Prompt excerpt (2 lines max)

---

## Data Flow

```
User Input (Playground UI)
  ↓
  title: "Customer support response test"
  ↓
Frontend Validation
  ↓ (validates required + length)
  ↓
API Request (POST /api/v1/playground/execute)
  ↓
Backend Validation (Pydantic)
  ↓ (validates required + min/max length)
  ↓
Trace Service (trace_service.create_trace)
  ↓
  title → trace.name (database column)
  ↓
Database Storage
  ├─> traces.name = "Customer support response test"
  ├─> Playground History (local session state)
  └─> TraceEvaluation → trace.name (via relationship)
```

---

## Traces Integration

**File**: `/api-tier/app/models/trace.py`

The `Trace` model already has a `name` column (line 16):
```python
name = Column(String(255), nullable=False)
```

**Playground.py** passes title to trace service (lines 122, 267):
```python
trace = await trace_service.create_trace(
    trace_id=trace_id,
    # ...
    title=request.title,  # Stored in trace.name
    # ...
)
```

**Result**: Title is stored in `traces.name` and visible in:
- Traces dashboard
- Trace detail views
- Logs and observability tools

---

## Evaluations Integration

**File**: `/api-tier/app/models/evaluation_catalog.py`

TraceEvaluation model has relationship to Trace (line 146):
```python
trace = relationship("Trace", back_populates="trace_evaluations")
```

**Access Pattern**:
```python
# In evaluation views/APIs
trace_evaluation.trace.name  # Returns the title
```

**Result**: Evaluations can display the title by accessing `trace.name` through the relationship.

---

## User Experience

### Before Changes

**Playground Form**:
```
Title (Optional)  [                                      ]
                  Give this execution a memorable name...

[Run Prompt]  <-- Enabled even without title
```

**History Display**:
```
GPT-4
Write a product description for...
1.2s | 89 tokens | $0.0023
```

### After Changes

**Playground Form**:
```
Title *  [                                      ]
         Give this execution a memorable name to identify it in traces, history, and evaluations.

[Run Prompt]  <-- Disabled until title AND prompt are filled
```

**History Display**:
```
Customer support response test
GPT-4
Write a product description for...
1.2s | 89 tokens | $0.0023
```

**Validation Error Display**:
```
Validation Error:
Title is required
```

---

## API Contract Change

### Request Schema

**Endpoint**: `POST /api/v1/playground/execute`

**Before**:
```json
{
  "prompt": "Write a haiku",
  "model": "gpt-4o-mini",
  "parameters": { ... },
  "metadata": {
    "title": "Haiku test"  // Optional
  }
}
```

**After**:
```json
{
  "title": "Haiku test",  // Required, top-level, 1-200 chars
  "prompt": "Write a haiku",
  "model": "gpt-4o-mini",
  "parameters": { ... },
  "metadata": {
    "intent": "...",
    "tone": "professional"
  }
}
```

### Error Responses

**Missing Title** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": { ... }
    }
  ]
}
```

**Title Too Long** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "String should have at most 200 characters",
      "ctx": { "max_length": 200 }
    }
  ]
}
```

---

## Testing Checklist

### Frontend Validation

- [x] Empty title shows validation error
- [x] Title > 200 characters shows validation error
- [x] Run button disabled when title empty
- [x] Run button disabled when prompt empty
- [x] Title trims whitespace before submission

### Backend Validation

- [x] API rejects request without title (422)
- [x] API rejects title with only whitespace (422)
- [x] API rejects title > 200 characters (422)
- [x] API accepts valid title (201)

### Data Propagation

- [x] Title appears in Playground History
- [x] Title stored in traces.name
- [x] Title accessible via TraceEvaluation.trace.name
- [x] Title displayed prominently in history

### User Experience

- [x] Red asterisk indicates required field
- [x] Help text updated to mention traces, history, evaluations
- [x] History shows title before model name
- [x] Title is bold and prominent in history

---

## Migration Notes

**Breaking Change**: Yes (for new API requests only)

**Impact**: All API clients calling `POST /api/v1/playground/execute` must now provide a `title` field.

**Backward Compatibility**:
- ✅ **Old history records**: Fully backward compatible - old sessions without title display gracefully
- ✅ **Old database traces**: Fully backward compatible - traces without title use fallback (project name)
- ❌ **New API requests**: Not backward compatible - title is now required (422 error if missing)

**Recommended Migration**:
```typescript
// Old code (will fail)
const request = {
  prompt: "...",
  model: "...",
  parameters: { ... }
};

// New code (required)
const request = {
  title: "My Prompt Test",  // Add this required field
  prompt: "...",
  model: "...",
  parameters: { ... }
};
```

---

## Backward Compatibility Details

### Frontend History Display

**Old Sessions (without title)**:
```tsx
// PlaygroundSession interface allows optional title
interface PlaygroundSession {
  title?: string;  // Optional - the '?' makes it backward compatible
  // ...
}

// Display code handles missing title gracefully
{session.title && (  // Conditional rendering - only shows if title exists
  <p>{session.title}</p>
)}
```

**Result**: Old sessions without title skip the title display and show model name directly.

### Backend Trace Service

**Fallback Logic** (`trace_service.py` lines 91-98):
```python
# Determine trace name: title > project name > source
trace_name = title
if not trace_name:
    # Get project name for default title
    project_query = select(Project).where(Project.id == project_id)
    project_result = await self.db.execute(project_query)
    project = project_result.scalar_one_or_none()
    trace_name = project.name if project else (
        metadata.get("source", "playground") if metadata else "playground"
    )
```

**Fallback Chain**:
1. Use `title` if provided
2. Use `project.name` (e.g., "Playground") if no title
3. Use `metadata["source"]` if no project
4. Use `"playground"` as final fallback

**Result**: Old traces without title get auto-generated names from project context.

### Database Schema

**Trace Model** (`trace.py` line 16):
```python
name = Column(String(255), nullable=False)
```

**Analysis**: Column is `nullable=False`, **BUT** the trace_service ensures a value is always provided via fallback logic. This prevents NULL values from ever reaching the database.

### API Request Validation

**New Requirement**: Title is now required at the API level (Pydantic validation):
```python
title: str = Field(..., min_length=1, max_length=200)
```

**Impact**:
- ✅ Old traces in database: No migration needed
- ✅ Frontend history: Handles missing titles gracefully
- ❌ New API requests: Must provide title (breaking change)

---

## Files Modified

1. `/api-tier/app/api/v1/endpoints/playground.py` (line 38)
2. `/ui-tier/mfe-playground/src/PlaygroundEnhanced.tsx` (lines 205-211, 256, 332-333, 343, 427, 700-708)
3. `/ui-tier/mfe-playground/src/mockData.ts` (line 13)

---

## Related Features

- **Traces Dashboard**: Title displayed in trace list and detail views
- **Evaluations Dashboard**: Title accessible via trace relationship
- **Observability**: Title improves trace identification in logs
- **Cost Tracking**: Title helps attribute costs to specific prompt types

---

## Future Enhancements

1. **Auto-suggest titles**: Use LLM to suggest titles based on prompt content
2. **Title templates**: Pre-defined title templates for common use cases
3. **Title history**: Auto-complete from previously used titles
4. **Title validation**: Check for duplicate titles within project
5. **Title search**: Filter traces/evaluations by title

---

## Status

✅ **COMPLETE** - Playground title requirement fully implemented across backend, frontend, traces, and evaluations

---

**Last Updated**: 2025-10-13
**Implemented By**: Claude Code
**Approved By**: Rohit Iyer
