# Evaluation Dashboard Tests

This directory contains comprehensive unit and integration tests for the Evaluation Dashboard components.

## Test Coverage

### EvaluationTable Component Tests
**Location**: `src/components/EvaluationTable/EvaluationTable.test.tsx`

**Coverage**:
- ✅ Rendering with mock data
- ✅ Filter interactions (prompt title, vendor, category, status)
- ✅ Sort interactions (all sortable columns)
- ✅ Pagination (next/previous)
- ✅ Row click to open modal
- ✅ Loading and error states
- ✅ Empty state handling
- ✅ Pass/fail status icons
- ✅ Score color coding
- ✅ Clear filters functionality
- ✅ Debounced search (300ms)

**Test Count**: 14 tests

### EvaluationDetailModal Component Tests
**Location**: `src/components/EvaluationDetailModal/EvaluationDetailModal.test.tsx`

**Coverage**:
- ✅ Loading state
- ✅ Error state
- ✅ Score display and formatting
- ✅ Pass/fail badge display
- ✅ Execution metrics display
- ✅ Trace context display
- ✅ Navigation to trace page
- ✅ Collapsible input/output sections
- ✅ Expand all functionality
- ✅ Modal close functionality (X button, Close button, click outside)
- ✅ Null value handling (N/A display)
- ✅ Trace identifier display

**Test Count**: 16 tests

## Running Tests

### Install Dependencies
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-evaluations
npm install
```

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests with Coverage Report
```bash
npm run test:coverage
```

## Test Configuration

### Jest Configuration
**File**: `jest.config.js`

Key settings:
- Preset: `ts-jest`
- Environment: `jsdom`
- Coverage thresholds: 80% for branches, functions, lines, statements
- Module name mapper for CSS imports
- Setup file for test environment configuration

### Setup File
**File**: `jest.setup.js`

Includes:
- `@testing-library/jest-dom` matchers
- `window.matchMedia` mock
- `IntersectionObserver` mock

## Test Dependencies

### Testing Libraries
- **jest**: Test runner and framework
- **ts-jest**: TypeScript support for Jest
- **@testing-library/react**: React testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers for DOM
- **@testing-library/user-event**: User interaction simulation
- **jest-environment-jsdom**: Browser-like environment for tests

### Additional Dependencies
- **identity-obj-proxy**: CSS module mocking
- **react-router-dom**: Required for navigation testing

## Writing New Tests

### Test Structure
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// Mock services
jest.mock('../../../../shared/services/evaluationService', () => ({
  evaluationService: {
    getEvaluationsList: jest.fn(),
    getEvaluationDetail: jest.fn(),
  },
}));

// Test wrapper
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('YourComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should do something', async () => {
    render(
      <TestWrapper>
        <YourComponent />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Expected Text')).toBeInTheDocument();
    });
  });
});
```

### Best Practices
1. **Always wrap components** with necessary providers (QueryClientProvider, BrowserRouter)
2. **Mock API services** to avoid real network calls
3. **Use waitFor** for async operations
4. **Clear mocks** before each test
5. **Test user interactions** with fireEvent or userEvent
6. **Test error states** and loading states
7. **Test accessibility** features when applicable
8. **Keep tests focused** on a single behavior

## Coverage Goals

- **Minimum**: 80% coverage across all metrics
- **Target**: 90%+ coverage for critical components
- **Focus areas**:
  - User interactions (clicks, form inputs)
  - Loading and error states
  - Navigation and routing
  - Data transformation and display
  - Edge cases (null values, empty states)

## Continuous Integration

Tests should be run:
- Before every commit (via pre-commit hook)
- In CI/CD pipeline before deployment
- When updating dependencies
- When modifying component logic

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "Cannot find module 'react-router-dom'"
**Solution**: Ensure react-router-dom is installed in dependencies

**Issue**: Tests timeout waiting for data
**Solution**: Check mock implementations and ensure promises resolve/reject

**Issue**: CSS-related errors
**Solution**: Verify identity-obj-proxy is configured in jest.config.js

**Issue**: "window.matchMedia is not a function"
**Solution**: Ensure jest.setup.js is properly configured

## Future Enhancements

- [ ] Add visual regression tests (e.g., Percy, Chromatic)
- [ ] Add E2E tests with Playwright
- [ ] Add performance tests
- [ ] Add accessibility tests (axe-core)
- [ ] Increase coverage to 95%+
- [ ] Add mutation testing

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
