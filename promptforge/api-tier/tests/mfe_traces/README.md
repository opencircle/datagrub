# Traces MFE API Tests

Comprehensive integration tests for the Traces API endpoints (`/api/v1/traces`).

## Test Coverage

### Pagination Tests
- ✅ `test_list_traces_with_pagination` - Verify paginated trace listing with page and page_size parameters
  - Tests TraceListResponse structure (traces, total, page, page_size)
  - Validates trace fields: id, trace_id, project_name, status, model_name, total_duration_ms, created_at, user_email
  - Confirms proper pagination math (page 1, size 5, total 10 → 5 results returned)

### Search & Filter Tests
- ✅ `test_list_traces_with_search` - Search traces by trace_id, project name, or user email
  - Creates traces with different IDs and project names
  - Verifies search returns only matching results

- ✅ `test_list_traces_with_model_filter` - Filter traces by AI model name
  - Creates traces using GPT-4 and GPT-3.5
  - Verifies only GPT-4 traces returned when filtering

- ✅ `test_list_traces_with_status_filter` - Filter traces by status (success, error, timeout)
  - Creates success and error traces
  - Verifies only error traces returned when filtering

### Sorting Tests
- ✅ `test_list_traces_with_sorting` - Sort traces by duration, status, timestamp, or requestId
  - Tests ascending and descending sort directions
  - Verifies proper ordering of results

### Organization Scoping Tests
- ✅ `test_create_trace_with_organization_scoping` - Create trace with project validation
  - Verifies project belongs to user's organization before creating trace
  - Returns 201 on success

- ✅ `test_create_trace_wrong_organization` - Prevent creating traces for other organizations
  - Returns 404 when trying to create trace for project in different organization

- ✅ `test_get_trace_by_id` - Get trace with spans by ID
  - Verifies organization scoping on retrieval
  - Includes spans when `include_spans=true`

- ✅ `test_get_trace_wrong_organization` - Prevent accessing other organization's traces
  - Returns 404 when trying to access trace from different organization

- ✅ `test_delete_trace` - Delete trace with organization scoping
  - Returns 204 on successful deletion
  - Verifies trace no longer exists after deletion

- ✅ `test_delete_trace_wrong_organization` - Prevent deleting other organization's traces
  - Returns 404 when trying to delete trace from different organization

### Security Tests
- ✅ `test_list_traces_unauthenticated` - Reject unauthenticated requests
  - Returns 403 when no authentication provided

- ✅ `test_list_traces_organization_isolation` - Multi-tenant data isolation
  - Creates traces in multiple organizations
  - Verifies user can only see traces from their own organization

## Running Tests

### Run All Traces Tests
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
source .venv/bin/activate
python -m pytest tests/mfe_traces/test_traces_api.py -v
```

### Run Specific Test
```bash
python -m pytest tests/mfe_traces/test_traces_api.py::TestTracesAPI::test_list_traces_with_pagination -v
```

### Run with Coverage
```bash
python -m pytest tests/mfe_traces/ --cov=app/api/v1/traces --cov-report=term-missing
```

## Test Data Setup

Each test uses:
- **Organizations**: Demo organization (from fixture) + optional other organizations for isolation tests
- **Users**: Demo user (rohit.iyer@oiiro.com) with organization association
- **Projects**: Test projects linked to organizations
- **Models**: AI models (GPT-4, GPT-3.5) with model providers
- **Traces**: Test traces with various statuses, durations, and metadata
- **Spans**: Optional spans linked to traces

## API Endpoints Tested

### POST /api/v1/traces
- Creates new trace with organization validation
- Validates project belongs to user's organization
- Loads spans relationship to avoid MissingGreenlet errors
- Returns 201 with TraceResponse

### GET /api/v1/traces
- Lists traces with pagination (default: page=1, page_size=20)
- Search by trace_id, project name, or user email
- Filter by model name
- Filter by status (success, error, timeout)
- Sort by requestId, status, duration, or timestamp (asc/desc)
- Organization scoping via Project join
- Returns TraceListResponse with pagination metadata

### GET /api/v1/traces/{trace_id}
- Retrieves single trace by ID
- Optional `include_spans` parameter
- Organization scoping via Project join
- Returns 404 if trace not found or belongs to different organization

### DELETE /api/v1/traces/{trace_id}
- Deletes trace by ID
- Organization scoping via Project join
- Returns 204 on success
- Returns 404 if trace not found or belongs to different organization

## Key Validations

### Organization Scoping
All endpoints enforce multi-tenant data isolation:
- Users can only create traces for projects in their organization
- Users can only view traces from their organization
- Users can only delete traces from their organization

### Response Schemas
- **TraceListResponse**: `{traces: TraceListItem[], total: int, page: int, page_size: int}`
- **TraceListItem**: UI-friendly with project_name, model_name, user_email (instead of UUIDs)
- **TraceResponse**: Full trace with optional spans array

### Error Handling
- 403: Not authenticated
- 404: Trace/project not found or access denied (organization mismatch)
- 201: Trace created successfully

## Dependencies

Tests require:
- PostgreSQL test database (not SQLite - UUID support needed)
- AsyncIO support
- HTTPX async client
- SQLAlchemy with selectinload for relationship loading

## Coverage

Current test coverage:
- **13 test cases** covering all CRUD operations
- **Multi-tenant isolation** verified
- **Search, filter, sort, pagination** fully tested
- **Organization scoping** on all endpoints
- **Authentication/authorization** verified

## Related Files

- **API Implementation**: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/api/v1/traces.py`
- **Schemas**: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/schemas/trace.py`
- **Models**: `/Users/rohitiyer/datagrub/promptforge/api-tier/app/models/trace.py`
- **UI Component**: `/Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces/`

## Notes

- All tests run from **host machine** (not inside Docker) to simulate browser-based API access
- Tests use **PostgreSQL test database** with proper UUID support
- Organization scoping is critical for SaaS multi-tenancy
- MissingGreenlet errors avoided by using `selectinload()` for all relationships
