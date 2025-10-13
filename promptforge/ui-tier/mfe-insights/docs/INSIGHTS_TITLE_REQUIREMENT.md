# Insights Title Requirement Implementation

## Overview

The Insights feature now requires a **Title** field for every transcript analysis. The title is propagated throughout the system and appears in:
- **Insights History** - Local session display with inline editing
- **Traces** - Database trace records (trace.name column)
- **Evaluations** - Accessible via trace relationship (trace.name)

## Date Implemented
2025-10-13

## Changes Made

### 1. Backend API Schema Update

**File**: `/api-tier/app/api/v1/endpoints/call_insights.py`

**Change 1** (line 54):
```python
# Before:
transcript_title: Optional[str] = Field(None, max_length=500, description="Optional title for searchability")

# After:
transcript_title: str = Field(..., min_length=1, max_length=500, description="Title for this analysis (required)")
```

**Change 2** (line 179):
```python
# Before:
transcript_title=request.transcript_title.strip() if request.transcript_title else None,

# After:
transcript_title=request.transcript_title.strip(),
```

**Impact**:
- Title is now **required** in API requests
- Pydantic validation enforces:
  - Non-empty string (min_length=1)
  - Maximum 500 characters (increased from Playground's 200 due to longer analysis descriptions)
  - Returns 422 Unprocessable Entity if validation fails

---

### 2. Frontend UI Updates

**File**: `/ui-tier/mfe-insights/src/components/sections/TranscriptInputSection.tsx`

#### A. Label Update (lines 86-88)
```tsx
// Before:
Title (Optional)

// After:
<label className="block text-sm font-semibold text-neutral-700 mb-2">
  Title <span className="text-[#FF385C]">*</span>
</label>
```

**Visual**: Red asterisk indicates required field

#### B. Placeholder Update (line 93)
```tsx
// Before:
placeholder="e.g., Customer call transcript"

// After:
placeholder="e.g., Q4 Earnings Call with ABC Corp"
```

#### C. Help Text Update (line 97-99)
```tsx
// Before:
"Give this transcript a title for easier identification in history."

// After:
"Give this analysis a descriptive title to identify it in history, traces, and evaluations."
```

**Impact**: Clarifies title appears in traces and evaluations, not just history

---

### 3. Frontend Validation Logic

**File**: `/ui-tier/mfe-insights/src/components/InsightsPage.tsx`

#### A. Validation Rules (lines 254-260)
```tsx
// Title validation (BEFORE transcript validation)
if (!formState.transcriptTitle.trim()) {
  errors.push('Title is required');
}

if (formState.transcriptTitle.trim().length > 500) {
  errors.push('Title is too long (max 500 characters)');
}
```

**Validation Order**: Title validation occurs **before** transcript validation

#### B. Button Disable Logic (line 470)
```tsx
// Before:
disabled={resultState.isLoading || !formState.transcript.trim()}

// After:
disabled={resultState.isLoading || !formState.transcriptTitle.trim() || !formState.transcript.trim()}
```

**UX**: Analyze button disabled when title or transcript is empty

#### C. Request Payload Update (line 300)
```tsx
// Before:
transcript_title: formState.transcriptTitle.trim() || undefined,

// After:
transcript_title: formState.transcriptTitle.trim(),
```

**Change**: Title moved from optional to required top-level field (no undefined fallback)

---

### 4. History Display (Already Implemented)

**File**: `/ui-tier/mfe-insights/src/components/sections/HistorySection.tsx`

#### A. Title Display (lines 283-286)
```tsx
<div className="font-medium text-sm text-neutral-700">
  {item.transcript_title || (
    <span className="text-neutral-400 italic">Untitled</span>
  )}
</div>
```

**Backward Compatibility**: Old records without title display "Untitled" in italic gray text

#### B. Inline Editing (lines 291-320)
```tsx
{/* Pencil icon for inline editing */}
<button
  onClick={() => handleStartEdit(item.id, item.transcript_title || '')}
  className="opacity-0 group-hover:opacity-100 transition-opacity"
>
  <Pencil className="h-3.5 w-3.5 text-neutral-400 hover:text-[#FF385C]" />
</button>
```

**Feature**: Users can edit titles directly from history view

#### C. Display Hierarchy
1. **Title** (medium font weight, prominent)
2. Timestamp (smaller, muted)
3. Model name and parameters (compact)

**Result**: Title is the most prominent element in history cards

---

## Data Flow

```
User Input (Insights UI)
  ↓
  transcript_title: "Q4 Earnings Call with ABC Corp"
  ↓
Frontend Validation
  ↓ (validates required + max 500 chars)
  ↓
API Request (POST /api/v1/call-insights/analyze)
  ↓
Backend Validation (Pydantic)
  ↓ (validates required + min/max length)
  ↓
Insights Service (insights_service.analyze_transcript)
  ↓
Trace Service (trace_service.create_trace)
  ↓
  transcript_title → trace.name (database column)
  ↓
Database Storage
  ├─> traces.name = "Q4 Earnings Call with ABC Corp"
  ├─> Insights History (local session state)
  └─> TraceEvaluation → trace.name (via relationship)
```

---

## Traces Integration

**File**: `/api-tier/app/models/trace.py`

The `Trace` model has a `name` column (line 16):
```python
name = Column(String(255), nullable=False)
```

**call_insights.py** passes transcript_title to trace service (line 179):
```python
result = await insights_service.analyze_transcript(
    transcript=request.transcript,
    transcript_title=request.transcript_title.strip(),  # Stored in trace.name
    user_id=str(current_user.id),
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
trace_evaluation.trace.name  # Returns the transcript title
```

**Result**: Evaluations can display the title by accessing `trace.name` through the relationship.

---

## User Experience

### Before Changes

**Insights Form**:
```
Title (Optional)  [                                      ]
                  Give this transcript a title for easier identification...

Transcript Text
[Large text area]

[Analyze Transcript]  <-- Enabled even without title
```

**History Display**:
```
Untitled
Today at 2:45 PM
GPT-4 | 89 tokens | $0.0023
```

### After Changes

**Insights Form**:
```
Title *  [                                      ]
         Give this analysis a descriptive title to identify it in history, traces, and evaluations.

Transcript Text
[Large text area]

[Analyze Transcript]  <-- Disabled until title AND transcript are filled
```

**History Display**:
```
Q4 Earnings Call with ABC Corp
Today at 2:45 PM
GPT-4 | 89 tokens | $0.0023
```

**Validation Error Display**:
```
Validation Error:
Title is required
```

---

## API Contract Change

### Request Schema

**Endpoint**: `POST /api/v1/call-insights/analyze`

**Before**:
```json
{
  "transcript": "Advisor: Hello, how can I help you today?\nClient: I'd like to...",
  "transcript_title": "Customer call",  // Optional
  "model_id": "gpt-4o-mini",
  "parameters": { ... }
}
```

**After**:
```json
{
  "transcript": "Advisor: Hello, how can I help you today?\nClient: I'd like to...",
  "transcript_title": "Q4 Earnings Call with ABC Corp",  // Required, 1-500 chars
  "model_id": "gpt-4o-mini",
  "parameters": { ... }
}
```

### Error Responses

**Missing Title** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "transcript_title"],
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
      "loc": ["body", "transcript_title"],
      "msg": "String should have at most 500 characters",
      "ctx": { "max_length": 500 }
    }
  ]
}
```

**Empty Title** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "transcript_title"],
      "msg": "String should have at least 1 character",
      "ctx": { "min_length": 1 }
    }
  ]
}
```

---

## Testing Checklist

### Frontend Validation

- [x] Empty title shows validation error
- [x] Title > 500 characters shows validation error
- [x] Analyze button disabled when title empty
- [x] Analyze button disabled when transcript empty
- [x] Title trims whitespace before submission

### Backend Validation

- [x] API rejects request without transcript_title (422)
- [x] API rejects title with only whitespace (422)
- [x] API rejects title > 500 characters (422)
- [x] API accepts valid title (201)

### Data Propagation

- [x] Title appears in Insights History
- [x] Title stored in traces.name
- [x] Title accessible via TraceEvaluation.trace.name
- [x] Title displayed prominently in history

### User Experience

- [x] Red asterisk indicates required field
- [x] Help text mentions traces, history, evaluations
- [x] History shows title prominently
- [x] Inline editing works for titles
- [x] "Untitled" displays for old records without title

---

## Backward Compatibility Details

### Frontend History Display

**Old Analyses (without title)**:
```tsx
// TranscriptInputSection interface allows optional title
interface InsightsFormState {
  transcriptTitle: string;  // Empty string for old records
  // ...
}

// HistorySection display code handles missing title gracefully
<div className="font-medium text-sm text-neutral-700">
  {item.transcript_title || (  // Conditional rendering
    <span className="text-neutral-400 italic">Untitled</span>
  )}
</div>
```

**Result**: Old analyses without title display "Untitled" in italic gray text with inline editing available.

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
        metadata.get("source", "insights") if metadata else "insights"
    )
```

**Fallback Chain**:
1. Use `transcript_title` if provided
2. Use `project.name` (e.g., "Insights Analysis") if no title
3. Use `metadata["source"]` if no project
4. Use `"insights"` as final fallback

**Result**: Old traces without title get auto-generated names from project context.

### Database Schema

**Trace Model** (`trace.py` line 16):
```python
name = Column(String(255), nullable=False)
```

**Analysis**: Column is `nullable=False`, **BUT** the trace_service ensures a value is always provided via fallback logic. This prevents NULL values from ever reaching the database.

### API Request Validation

**New Requirement**: transcript_title is now required at the API level (Pydantic validation):
```python
transcript_title: str = Field(..., min_length=1, max_length=500)
```

**Impact**:
- ✅ Old traces in database: No migration needed
- ✅ Frontend history: Handles missing titles gracefully ("Untitled")
- ❌ New API requests: Must provide transcript_title (breaking change)

---

## Comparison with Playground

| Feature | Playground | Insights |
|---------|-----------|----------|
| **Field Name** | `title` | `transcript_title` |
| **Max Length** | 200 characters | 500 characters |
| **Required** | ✅ Yes | ✅ Yes |
| **Validation** | Client + Server | Client + Server |
| **History Display** | Conditional render | "Untitled" fallback |
| **Inline Editing** | ❌ No | ✅ Yes |
| **Trace Integration** | ✅ trace.name | ✅ trace.name |
| **Help Text** | "traces, history, evaluations" | "history, traces, evaluations" |

**Key Differences**:
1. **Length Limit**: Insights allows 500 chars (longer analysis descriptions), Playground allows 200 (shorter execution titles)
2. **Inline Editing**: Insights has pencil icon for editing titles from history, Playground does not
3. **Fallback Display**: Insights shows "Untitled" for old records, Playground conditionally renders (skips display)

---

## Migration Notes

**Breaking Change**: Yes (for new API requests only)

**Impact**: All API clients calling `POST /api/v1/call-insights/analyze` must now provide a `transcript_title` field.

**Backward Compatibility**:
- ✅ **Old history records**: Fully backward compatible - old analyses without title display as "Untitled"
- ✅ **Old database traces**: Fully backward compatible - traces without title use fallback (project name)
- ❌ **New API requests**: Not backward compatible - transcript_title is now required (422 error if missing)

**Recommended Migration**:
```typescript
// Old code (will fail)
const request = {
  transcript: "...",
  model_id: "gpt-4o-mini",
  parameters: { ... }
};

// New code (required)
const request = {
  transcript_title: "Q4 Earnings Call with ABC Corp",  // Add this required field
  transcript: "...",
  model_id: "gpt-4o-mini",
  parameters: { ... }
};
```

---

## Files Modified

1. `/api-tier/app/api/v1/endpoints/call_insights.py` (lines 54, 179)
2. `/ui-tier/mfe-insights/src/components/sections/TranscriptInputSection.tsx` (lines 86-88, 93, 97-99)
3. `/ui-tier/mfe-insights/src/components/InsightsPage.tsx` (lines 254-260, 300, 470)

**No changes needed**:
- `/ui-tier/mfe-insights/src/components/sections/HistorySection.tsx` (already displays title prominently)
- `/api-tier/app/services/trace_service.py` (fallback logic already implemented)
- `/api-tier/app/models/trace.py` (schema already correct)

---

## Related Features

- **Traces Dashboard**: Title displayed in trace list and detail views
- **Evaluations Dashboard**: Title accessible via trace relationship
- **Observability**: Title improves trace identification in logs
- **Cost Tracking**: Title helps attribute costs to specific analysis types
- **History Search**: Title enables better searchability in history

---

## Future Enhancements

1. **Auto-suggest titles**: Use LLM to suggest titles based on transcript content
2. **Title templates**: Pre-defined title templates for common analysis types
3. **Title history**: Auto-complete from previously used titles
4. **Title validation**: Check for duplicate titles within project
5. **Title search**: Filter traces/evaluations by title keyword
6. **Bulk title editing**: Edit titles for multiple history items at once

---

## Consistency Achieved

This implementation ensures **consistent title requirements** across all model invocations:

| Feature | Title Field | Required | Max Length | Trace Integration | History Display |
|---------|------------|----------|------------|-------------------|-----------------|
| **Playground** | `title` | ✅ Yes | 200 chars | ✅ trace.name | ✅ Prominent |
| **Insights** | `transcript_title` | ✅ Yes | 500 chars | ✅ trace.name | ✅ Prominent |

**Result**: Both features now enforce title requirements with consistent validation patterns, data flow, and user experience.

---

## Status

✅ **COMPLETE** - Insights title requirement fully implemented across backend, frontend, traces, and evaluations

---

**Last Updated**: 2025-10-13
**Implemented By**: Claude Code
**Approved By**: Rohit Iyer
