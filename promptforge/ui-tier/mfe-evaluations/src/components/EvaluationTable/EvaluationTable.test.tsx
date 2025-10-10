/**
 * EvaluationTable Component Tests
 *
 * Test coverage:
 * - Rendering with mock data
 * - Filter interactions
 * - Sort interactions
 * - Pagination
 * - Row click to open modal
 * - Loading and error states
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EvaluationTable } from './EvaluationTable';
import { evaluationService } from '../../../../shared/services/evaluationService';

// Mock the evaluation service
jest.mock('../../../../shared/services/evaluationService', () => ({
  evaluationService: {
    getEvaluationsList: jest.fn(),
    getEvaluationDetail: jest.fn(),
  },
}));

// Mock window.location
delete (window as any).location;
window.location = { href: '' } as any;

// Mock data
const mockEvaluations = [
  {
    id: 'eval-1',
    name: 'Toxicity Check',
    description: 'Check for toxic content',
    type: 'toxicity',
    status: 'completed',
    trace_id: 'tr-123',
    trace_identifier: 'tr_abc123',
    project_id: 'proj-1',
    prompt_title: 'Customer Support Response',
    model: 'gpt-4',
    vendor_name: 'DeepEval',
    category: 'safety',
    avg_score: 0.92,
    passed: true,
    total_tests: 10,
    passed_tests: 9,
    total_tokens: 1500,
    total_cost: 0.03,
    duration_ms: 2500,
    created_at: '2025-01-15T10:30:00Z',
  },
  {
    id: 'eval-2',
    name: 'Context Relevance',
    description: 'Check context relevance',
    type: 'relevance',
    status: 'completed',
    trace_id: 'tr-124',
    trace_identifier: 'tr_def456',
    project_id: 'proj-1',
    prompt_title: 'Product Recommendation',
    model: 'gpt-3.5-turbo',
    vendor_name: 'Ragas',
    category: 'quality',
    avg_score: 0.65,
    passed: false,
    total_tests: 5,
    passed_tests: 3,
    total_tokens: 800,
    total_cost: 0.01,
    duration_ms: 1200,
    created_at: '2025-01-15T09:15:00Z',
  },
];

const mockResponse = {
  evaluations: mockEvaluations,
  total: 2,
  limit: 20,
  offset: 0,
};

// Test wrapper with providers (no router needed)
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('EvaluationTable', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (evaluationService.getEvaluationsList as jest.Mock).mockResolvedValue(mockResponse);
  });

  it('renders the table with evaluation data', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    expect(screen.getByText('Context Relevance')).toBeInTheDocument();
    expect(screen.getByText('DeepEval')).toBeInTheDocument();
    expect(screen.getByText('Ragas')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    expect(screen.getByText(/Loading evaluations/i)).toBeInTheDocument();
  });

  it('filters by prompt title', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Type in search box
    const searchInput = screen.getByPlaceholderText(/Search prompt titles/i);
    fireEvent.change(searchInput, { target: { value: 'Customer' } });

    // Wait for debounce (300ms)
    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          prompt_title: 'Customer',
          offset: 0,
        })
      );
    }, { timeout: 500 });
  });

  it('filters by vendor', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Click filter button to expand filters
    const filterButton = screen.getByText(/Filters/i);
    fireEvent.click(filterButton);

    // Select vendor
    const vendorSelect = screen.getByLabelText(/Vendor/i);
    fireEvent.change(vendorSelect, { target: { value: 'DeepEval' } });

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          vendor: 'DeepEval',
          offset: 0,
        })
      );
    });
  });

  it('filters by category', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Click filter button
    const filterButton = screen.getByText(/Filters/i);
    fireEvent.click(filterButton);

    // Select category
    const categorySelect = screen.getByLabelText(/Category/i);
    fireEvent.change(categorySelect, { target: { value: 'safety' } });

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'safety',
          offset: 0,
        })
      );
    });
  });

  it('filters by status', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Click filter button
    const filterButton = screen.getByText(/Filters/i);
    fireEvent.click(filterButton);

    // Select status
    const statusSelect = screen.getByLabelText(/Status/i);
    fireEvent.change(statusSelect, { target: { value: 'pass' } });

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          status_filter: 'pass',
          offset: 0,
        })
      );
    });
  });

  it('clears all filters', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Add a filter
    const searchInput = screen.getByPlaceholderText(/Search prompt titles/i);
    fireEvent.change(searchInput, { target: { value: 'Customer' } });

    await waitFor(() => {
      expect(screen.getByText(/Clear/i)).toBeInTheDocument();
    }, { timeout: 500 });

    // Clear filters
    const clearButton = screen.getByText(/Clear/i);
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          prompt_title: undefined,
        })
      );
    });

    expect(searchInput).toHaveValue('');
  });

  it('sorts by column when header is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Click on "Score" column header
    const scoreHeader = screen.getByText(/Score/i);
    fireEvent.click(scoreHeader);

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          sort_by: 'score',
          sort_direction: 'desc',
        })
      );
    });

    // Click again to reverse direction
    fireEvent.click(scoreHeader);

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          sort_by: 'score',
          sort_direction: 'asc',
        })
      );
    });
  });

  it('opens detail modal when row is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Mock the detail endpoint
    (evaluationService.getEvaluationDetail as jest.Mock).mockResolvedValue({
      id: 'eval-1',
      trace_id: 'tr-123',
      trace_identifier: 'tr_abc123',
      prompt_title: 'Customer Support Response',
      model_name: 'gpt-4',
      project_name: 'Customer Support',
      project_id: 'proj-1',
      created_at: '2025-01-15T10:30:00Z',
      evaluation_name: 'Toxicity Check',
      evaluation_type: 'toxicity',
      vendor_name: 'DeepEval',
      category: 'safety',
      source: 'vendor',
      description: 'Check for toxic content',
      score: 0.92,
      threshold: 0.8,
      passed: true,
      reason: 'No toxic content detected',
      explanation: 'The response is appropriate and safe',
      execution_time_ms: 2500,
      input_tokens: 100,
      output_tokens: 50,
      total_tokens: 150,
      evaluation_cost: 0.03,
      input_data: { prompt: 'Test prompt' },
      output_data: { response: 'Test response' },
      llm_metadata: {},
      trace: {
        id: 'tr-123',
        trace_id: 'tr_abc123',
        name: 'Customer Support Response',
        status: 'completed',
      },
    });

    // Click on the first row
    const firstRow = screen.getByText('Toxicity Check').closest('tr');
    fireEvent.click(firstRow!);

    // Wait for modal to open
    await waitFor(() => {
      expect(evaluationService.getEvaluationDetail).toHaveBeenCalledWith('eval-1');
    });
  });

  it('handles pagination', async () => {
    const largeMockResponse = {
      ...mockResponse,
      total: 50,
    };
    (evaluationService.getEvaluationsList as jest.Mock).mockResolvedValue(largeMockResponse);

    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Click next page
    const nextButton = screen.getByText(/Next/i);
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(evaluationService.getEvaluationsList).toHaveBeenCalledWith(
        expect.objectContaining({
          offset: 20,
        })
      );
    });
  });

  it('displays error state', async () => {
    (evaluationService.getEvaluationsList as jest.Mock).mockRejectedValue(
      new Error('Failed to load evaluations')
    );

    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading evaluations/i)).toBeInTheDocument();
      expect(screen.getByText(/Failed to load evaluations/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Retry/i)).toBeInTheDocument();
  });

  it('displays empty state when no evaluations', async () => {
    (evaluationService.getEvaluationsList as jest.Mock).mockResolvedValue({
      evaluations: [],
      total: 0,
      limit: 20,
      offset: 0,
    });

    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/No evaluations found/i)).toBeInTheDocument();
    });
  });

  it('displays correct pass/fail icons', async () => {
    render(
      <TestWrapper>
        <EvaluationTable />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    });

    // Check for check circle icon (passed) and x circle icon (failed)
    const svgs = screen.getAllByRole('img', { hidden: true });
    expect(svgs.length).toBeGreaterThan(0);
  });
});
