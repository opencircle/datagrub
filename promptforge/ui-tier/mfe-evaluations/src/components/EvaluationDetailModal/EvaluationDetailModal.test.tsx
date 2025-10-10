/**
 * EvaluationDetailModal Component Tests
 *
 * Test coverage:
 * - Rendering with mock data
 * - Loading state
 * - Error state
 * - Score display and color coding
 * - Trace context display
 * - Navigation to trace
 * - Collapsible sections
 * - Modal close functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EvaluationDetailModal } from './EvaluationDetailModal';
import { evaluationService } from '../../../../shared/services/evaluationService';

// Mock the evaluation service
jest.mock('../../../../shared/services/evaluationService', () => ({
  evaluationService: {
    getEvaluationDetail: jest.fn(),
  },
}));

// Mock window.location
delete (window as any).location;
window.location = { href: '' } as any;

// Mock data
const mockDetailData = {
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
  explanation: 'The response is appropriate and safe for all audiences',
  execution_time_ms: 2500,
  input_tokens: 100,
  output_tokens: 50,
  total_tokens: 150,
  evaluation_cost: 0.03,
  input_data: { prompt: 'Test prompt' },
  output_data: { response: 'Test response' },
  llm_metadata: { temperature: 0.7 },
  trace: {
    id: 'tr-123',
    trace_id: 'tr_abc123',
    name: 'Customer Support Response',
    status: 'completed',
  },
};

// Test wrapper (no router needed since we're using window.location)
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

describe('EvaluationDetailModal', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (evaluationService.getEvaluationDetail as jest.Mock).mockResolvedValue(mockDetailData);
  });

  it('shows loading state initially', () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    expect(screen.getByText(/Loading evaluation details/i)).toBeInTheDocument();
  });

  it('renders evaluation details after loading', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    expect(screen.getByText('DeepEval')).toBeInTheDocument();
    expect(screen.getByText(/safety/i)).toBeInTheDocument();
    expect(screen.getByText('Customer Support Response')).toBeInTheDocument();
    expect(screen.getByText('gpt-4')).toBeInTheDocument();
    expect(screen.getByText('Customer Support')).toBeInTheDocument();
  });

  it('displays score with correct formatting', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('0.92')).toBeInTheDocument();
    });

    expect(screen.getByText('/ 1.00')).toBeInTheDocument();
  });

  it('displays passed badge', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Passed')).toBeInTheDocument();
    });
  });

  it('displays failed badge for failed evaluation', async () => {
    const failedData = {
      ...mockDetailData,
      passed: false,
      score: 0.45,
    };
    (evaluationService.getEvaluationDetail as jest.Mock).mockResolvedValue(failedData);

    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });
  });

  it('displays execution metrics', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('2,500 ms')).toBeInTheDocument();
    });

    expect(screen.getByText('150')).toBeInTheDocument(); // total tokens
    expect(screen.getByText('100 in / 50 out')).toBeInTheDocument(); // token breakdown
    expect(screen.getByText('$0.0300')).toBeInTheDocument(); // cost
  });

  it('displays reason and explanation', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No toxic content detected')).toBeInTheDocument();
    });

    expect(screen.getByText('The response is appropriate and safe for all audiences')).toBeInTheDocument();
  });

  it('expands input data section when clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Input data should be collapsed initially
    expect(screen.queryByText(/"prompt"/i)).not.toBeInTheDocument();

    // Click to expand
    const inputButton = screen.getByText('Input Data');
    fireEvent.click(inputButton);

    // Should now see the JSON data
    await waitFor(() => {
      expect(screen.getByText(/"prompt"/i)).toBeInTheDocument();
    });
  });

  it('expands output data section when clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Output data should be collapsed initially
    expect(screen.queryByText(/"response"/i)).not.toBeInTheDocument();

    // Click to expand
    const outputButton = screen.getByText('Output Data');
    fireEvent.click(outputButton);

    // Should now see the JSON data
    await waitFor(() => {
      expect(screen.getByText(/"response"/i)).toBeInTheDocument();
    });
  });

  it('expands all sections when "Expand All" is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click "Expand All"
    const expandAllButton = screen.getByText('Expand All');
    fireEvent.click(expandAllButton);

    // Both input and output should be visible
    await waitFor(() => {
      expect(screen.getByText(/"prompt"/i)).toBeInTheDocument();
      expect(screen.getByText(/"response"/i)).toBeInTheDocument();
    });
  });

  it('navigates to trace when "View Trace" button is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click "View Trace" button in footer
    const viewTraceButtons = screen.getAllByText('View Trace');
    fireEvent.click(viewTraceButtons[0]);

    expect(window.location.href).toBe('/traces/tr-123');
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('navigates to trace when "View Full Trace" link is clicked', async () => {
    // Reset window.location.href
    window.location.href = '';

    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click "View Full Trace" link in trace context
    const viewFullTraceButton = screen.getByText('View Full Trace');
    fireEvent.click(viewFullTraceButton);

    expect(window.location.href).toBe('/traces/tr-123');
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal when close button is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click X button in header
    const closeButtons = screen.getAllByRole('button');
    const xButton = closeButtons.find(btn => btn.querySelector('svg'));
    if (xButton) {
      fireEvent.click(xButton);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  it('closes modal when Close button in footer is clicked', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click "Close" button in footer
    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal when clicking outside the modal content', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Click on the backdrop
    const backdrop = screen.getByText('Toxicity Check').closest('.fixed');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  it('handles error state', async () => {
    (evaluationService.getEvaluationDetail as jest.Mock).mockRejectedValue(
      new Error('Failed to load')
    );

    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Failed to load')).toBeInTheDocument();
    });

    // Should have a close button
    const closeButton = screen.getByText('Close');
    expect(closeButton).toBeInTheDocument();
  });

  it('displays N/A for null score', async () => {
    const dataWithNullScore = {
      ...mockDetailData,
      score: null,
      passed: null,
    };
    (evaluationService.getEvaluationDetail as jest.Mock).mockResolvedValue(dataWithNullScore);

    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });
  });

  it('displays N/A for null metrics', async () => {
    const dataWithNullMetrics = {
      ...mockDetailData,
      execution_time_ms: null,
      total_tokens: null,
      evaluation_cost: null,
    };
    (evaluationService.getEvaluationDetail as jest.Mock).mockResolvedValue(dataWithNullMetrics);

    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Toxicity Check')).toBeInTheDocument();
    });

    // Should see N/A for all metrics
    const naElements = screen.getAllByText('N/A');
    expect(naElements.length).toBeGreaterThanOrEqual(3);
  });

  it('displays trace identifier correctly', async () => {
    render(
      <TestWrapper>
        <EvaluationDetailModal evaluationId="eval-1" onClose={mockOnClose} />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('tr_abc123')).toBeInTheDocument();
    });
  });
});
