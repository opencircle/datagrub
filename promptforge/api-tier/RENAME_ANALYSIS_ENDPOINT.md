# Rename Call Insights Analysis - API Endpoint

## Endpoint Added

**PATCH** `/api/v1/call-insights/{analysis_id}/title`

## Description

Updates the `transcript_title` field of a call insights analysis for better organization and searchability.

## Request

### Path Parameters
- `analysis_id` (string, required): UUID of the analysis to update

### Headers
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json` (required)

### Body
```json
{
  "transcript_title": "New Title Here"
}
```

**Constraints:**
- `transcript_title`: string, 1-500 characters

## Response

Returns the full `CallInsightsHistoryResponse` with the updated title.

```json
{
  "id": "9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4",
  "transcript_title": "New Title Here",
  "transcript_input": "...",
  "summary_output": "...",
  "insights_output": "...",
  "facts_output": "...",
  "pii_redacted": false,
  "total_tokens": 1234,
  "total_cost": 0.0056,
  "project_id": null,
  "system_prompt_stage1": null,
  "system_prompt_stage2": null,
  "system_prompt_stage3": null,
  "model_stage1": "gpt-4o-mini",
  "model_stage2": "gpt-4o-mini",
  "model_stage3": "gpt-4o-mini",
  "analysis_metadata": {...},
  "created_at": "2025-01-15T10:30:00"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Analysis not found"
}
```

**Causes:**
- Analysis ID doesn't exist
- Analysis belongs to a different organization (organization-scoped access)

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Cause:** Missing or invalid authentication token

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "transcript_title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Cause:** Validation error (e.g., empty title, title too long)

## Example Usage

### cURL
```bash
curl -X PATCH "http://localhost:8000/api/v1/call-insights/9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4/title" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{"transcript_title": "Ro ClSonet-4.5 1"}'
```

### JavaScript (fetch)
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/call-insights/9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4/title',
  {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      transcript_title: 'Ro ClSonet-4.5 1'
    })
  }
);

const updatedAnalysis = await response.json();
console.log(updatedAnalysis.transcript_title); // "Ro ClSonet-4.5 1"
```

### Python
```python
import requests

response = requests.patch(
    "http://localhost:8000/api/v1/call-insights/9d1feeef-2525-4d08-9aa3-ad5b1c9f12b4/title",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    },
    json={
        "transcript_title": "Ro ClSonet-4.5 1"
    }
)

updated_analysis = response.json()
print(updated_analysis["transcript_title"])  # "Ro ClSonet-4.5 1"
```

## Security

- **Organization-scoped**: Users can only update analyses belonging to their organization
- **Authentication required**: Must provide valid JWT token
- **Input validation**: Title length constrained to 1-500 characters

## Implementation Details

**File**: `promptforge/api-tier/app/api/v1/endpoints/call_insights.py`

**Location**: Lines 462-521

**Schema**:
```python
class UpdateAnalysisTitleRequest(BaseModel):
    """Request to update analysis title"""
    transcript_title: str = Field(..., min_length=1, max_length=500, description="New title for the analysis")
```

## Testing

The endpoint can be tested via:
1. **Swagger UI**: http://localhost:8000/docs (look for PATCH `/api/v1/call-insights/{analysis_id}/title`)
2. **Automated tests**: Create test in `tests/mfe_insights/test_call_insights_api.py`
3. **Manual testing**: Use cURL or Postman with valid authentication

## Next Steps

To use this endpoint from the UI:

1. Add a rename button/icon next to analysis titles in the history view
2. Show an inline edit field or modal to capture the new title
3. Call this endpoint with the new title
4. Refresh the UI to show the updated title
