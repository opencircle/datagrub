export interface Evaluation {
  id: string;
  name: string;
  project: string;
  status: 'running' | 'completed' | 'failed';
  score: number;
  metrics: {
    accuracy: number;
    latency: number;
    cost: number;
  };
  runDate: string;
  promptVersion: string;
}

export const mockEvaluations: Evaluation[] = [
  {
    id: '1',
    name: 'Customer Support Response Quality',
    project: 'Customer Support Assistant',
    status: 'completed',
    score: 92,
    metrics: {
      accuracy: 94,
      latency: 1.2,
      cost: 0.045,
    },
    runDate: '2025-01-15T10:30:00Z',
    promptVersion: 'v2.3.1',
  },
  {
    id: '2',
    name: 'Content Generation Benchmark',
    project: 'Content Generation Pipeline',
    status: 'completed',
    score: 88,
    metrics: {
      accuracy: 89,
      latency: 2.1,
      cost: 0.067,
    },
    runDate: '2025-01-14T15:45:00Z',
    promptVersion: 'v1.8.0',
  },
  {
    id: '3',
    name: 'Code Review Accuracy Test',
    project: 'Code Review Assistant',
    status: 'running',
    score: 0,
    metrics: {
      accuracy: 0,
      latency: 0,
      cost: 0,
    },
    runDate: '2025-01-15T14:00:00Z',
    promptVersion: 'v3.0.0-beta',
  },
  {
    id: '4',
    name: 'Data Analysis Precision',
    project: 'Data Analysis Agent',
    status: 'completed',
    score: 85,
    metrics: {
      accuracy: 87,
      latency: 3.5,
      cost: 0.092,
    },
    runDate: '2025-01-13T09:15:00Z',
    promptVersion: 'v1.2.0',
  },
  {
    id: '5',
    name: 'Legal Summarization Test',
    project: 'Legal Document Summarizer',
    status: 'failed',
    score: 0,
    metrics: {
      accuracy: 0,
      latency: 0,
      cost: 0,
    },
    runDate: '2025-01-12T11:00:00Z',
    promptVersion: 'v2.1.0',
  },
];
