## API Integration Tests

Comprehensive API integration tests organized by MFE (Micro Frontend) modules for clear test ownership and maintainability.

### Directory Structure

```
tests/
├── conftest.py                    # Shared fixtures (demo user, auth, db)
├── __init__.py
├── README.md                      # This file
├── mfe_playground/                # Playground MFE tests
│   ├── __init__.py
│   └── test_playground_api.py    # POST /api/v1/playground/execute
├── mfe_projects/                  # Projects MFE tests
│   ├── __init__.py
│   └── test_projects_api.py      # /api/v1/projects/* (TODO)
├── mfe_evaluations/               # Evaluations MFE tests
│   ├── __init__.py
│   └── test_evaluations_api.py   # /api/v1/evaluations/* (TODO)
├── mfe_traces/                    # Traces MFE tests
│   ├── __init__.py
│   └── test_traces_api.py        # /api/v1/traces/* (TODO)
├── mfe_policy/                    # Policy MFE tests
│   ├── __init__.py
│   └── test_policy_api.py        # /api/v1/policy/* (TODO)
└── mfe_models/                    # Models MFE tests
    ├── __init__.py
    └── test_models_api.py         # /api/v1/models/* (TODO)
```

### Test Organization Principles

1. **MFE Ownership**: Each MFE owns its API test suite
   - `mfe_playground` tests → `/api/v1/playground/*` endpoints
   - `mfe_projects` tests → `/api/v1/projects/*` endpoints
   - etc.

2. **Clear Mapping**: MFE UI changes trigger corresponding API tests
   - UI Architect updates `ui-tier/mfe-playground` → Run `tests/mfe_playground/`
   - API Architect updates `api-tier/app/api/v1/endpoints/playground.py` → Run `tests/mfe_playground/`

3. **Shared Fixtures**: Common test utilities in `conftest.py`
   - `demo_user`: Pre-configured test user (demo@promptforge.ai / demo123)
   - `auth_headers`: Authentication headers with valid JWT
   - `client`: Async HTTP client with test database
   - `db_session`: Fresh database for each test

### Running Tests

#### Install Dependencies
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
pip install pytest pytest-asyncio httpx
```

#### Run All Tests
```bash
pytest tests/ -v
```

#### Run Specific MFE Tests
```bash
# Playground MFE tests only
pytest tests/mfe_playground/ -v

# Projects MFE tests only
pytest tests/mfe_projects/ -v

# Evaluations MFE tests only
pytest tests/mfe_evaluations/ -v
```

#### Run Single Test
```bash
pytest tests/mfe_playground/test_playground_api.py::TestPlaygroundExecute::test_execute_prompt_success -v
```

#### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Patterns

#### Authentication Test
```python
@pytest.mark.asyncio
async def test_endpoint_unauthenticated(client: AsyncClient):
    """Test endpoint without authentication"""
    response = await client.post("/api/v1/endpoint", json={...})
    assert response.status_code == 403
```

#### Validation Test
```python
@pytest.mark.asyncio
async def test_endpoint_validation(client: AsyncClient, auth_headers: dict):
    """Test input validation"""
    response = await client.post(
        "/api/v1/endpoint",
        json={"invalid": "data"},
        headers=auth_headers
    )
    assert response.status_code == 422
```

#### Success Test
```python
@pytest.mark.asyncio
async def test_endpoint_success(client: AsyncClient, auth_headers: dict, demo_user: User):
    """Test successful endpoint execution"""
    response = await client.post(
        "/api/v1/endpoint",
        json={"valid": "data"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Demo User Credentials

For manual testing or UI integration:
- **Email**: `demo@promptforge.ai`
- **Password**: `demo123`
- **Organization**: Demo Organization
- **Plan**: Free

### Automated Test Triggers

#### API QA Agent Integration

The API QA agent automatically runs relevant tests when:
1. **MFE UI Changes**: UI Architect updates `mfe-playground/` → Run `tests/mfe_playground/`
2. **API Changes**: API Architect updates `endpoints/playground.py` → Run `tests/mfe_playground/`
3. **Before Deployment**: Checker Agent validates all tests pass

#### Checker Agent Validation

Before approving any MFE UI or API changes, Checker Agent must verify:
```bash
# Run MFE-specific tests
pytest tests/mfe_{module}/ -v

# Expect: All tests PASS
# Block deployment if: Any test FAILS
```

### Test Coverage Goals

- **Unit Tests**: >80% coverage for business logic
- **Integration Tests**: 100% coverage for critical paths
  - Authentication flows
  - CRUD operations
  - Error handling
  - Validation rules

### Writing New Tests

When adding new API endpoints:

1. **Create test file** in appropriate MFE directory:
   ```bash
   touch tests/mfe_{module}/test_{feature}_api.py
   ```

2. **Use shared fixtures** from `conftest.py`:
   ```python
   async def test_feature(client: AsyncClient, auth_headers: dict, demo_user: User):
       ...
   ```

3. **Follow test pattern**:
   - Test unauthenticated access (403)
   - Test validation errors (422)
   - Test success case (200)
   - Test edge cases

4. **Add to CI pipeline** (TODO):
   ```yaml
   - name: Run MFE Tests
     run: pytest tests/mfe_{module}/ -v
   ```

### Known Issues

1. **Playground Execution Tests**: Currently return 500 because model provider is not configured
   - Fix: Set up OpenAI/Anthropic API key in organization settings
   - Expected: Tests will pass once provider is configured

2. **SQLAlchemy Async Relationship Loading**: Some endpoints fail with MissingGreenlet error
   - Fix: Use `selectinload` or `joinedload` for relationships in queries
   - Pattern: `stmt.options(selectinload(Prompt.current_version))`

### Future Enhancements

- [ ] Add E2E tests with Playwright for full UI → API → DB flow
- [ ] Add performance tests with load testing (Locust)
- [ ] Add contract tests (Pact) for API versioning
- [ ] Add mutation testing (mutmut) for test quality
- [ ] Add CI/CD integration with GitHub Actions
- [ ] Add test reporting dashboard (Allure)

### Maintenance

- **Update fixtures** when adding new models or test data requirements
- **Add new MFE directories** as micro frontends are added
- **Keep tests fast** (use in-memory SQLite, mock external APIs)
- **Keep tests isolated** (no shared state between tests)

---

**Last Updated**: 2025-10-06
**Status**: ✅ Playground MFE tests complete, other MFEs pending implementation
