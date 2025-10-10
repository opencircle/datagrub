export interface TraceSpan {
  id: string;
  name: string;
  duration: number;
  startTime: string;
  status: 'success' | 'error' | 'pending';
  metadata?: Record<string, any>;
}

export interface Trace {
  id: string;
  requestId: string;
  timestamp: string;
  status: 'success' | 'error' | 'timeout';
  duration: number;
  model: string;
  user: string;
  project: string;
  spans: TraceSpan[];
  metadata: {
    promptTokens: number;
    completionTokens: number;
    totalCost: number;
    statusCode: number;
  };
}

export const mockTraces: Trace[] = [
  {
    id: '1',
    requestId: 'req_8a9b7c6d5e4f',
    timestamp: '2025-01-15T10:30:22Z',
    status: 'success',
    duration: 1247,
    model: 'gpt-4',
    user: 'john.doe@example.com',
    project: 'Customer Support Assistant',
    spans: [
      {
        id: 'span_1',
        name: 'Request Validation',
        duration: 45,
        startTime: '2025-01-15T10:30:22.000Z',
        status: 'success',
      },
      {
        id: 'span_2',
        name: 'Prompt Template Processing',
        duration: 123,
        startTime: '2025-01-15T10:30:22.045Z',
        status: 'success',
      },
      {
        id: 'span_3',
        name: 'Model Inference',
        duration: 1012,
        startTime: '2025-01-15T10:30:22.168Z',
        status: 'success',
      },
      {
        id: 'span_4',
        name: 'Response Post-Processing',
        duration: 67,
        startTime: '2025-01-15T10:30:23.180Z',
        status: 'success',
      },
    ],
    metadata: {
      promptTokens: 234,
      completionTokens: 456,
      totalCost: 0.0234,
      statusCode: 200,
    },
  },
  {
    id: '2',
    requestId: 'req_1f2e3d4c5b6a',
    timestamp: '2025-01-15T10:28:15Z',
    status: 'error',
    duration: 523,
    model: 'claude-3-opus',
    user: 'sarah.smith@example.com',
    project: 'Content Generation Pipeline',
    spans: [
      {
        id: 'span_1',
        name: 'Request Validation',
        duration: 38,
        startTime: '2025-01-15T10:28:15.000Z',
        status: 'success',
      },
      {
        id: 'span_2',
        name: 'Prompt Template Processing',
        duration: 156,
        startTime: '2025-01-15T10:28:15.038Z',
        status: 'success',
      },
      {
        id: 'span_3',
        name: 'Model Inference',
        duration: 329,
        startTime: '2025-01-15T10:28:15.194Z',
        status: 'error',
        metadata: {
          error: 'Rate limit exceeded',
          errorCode: 429,
        },
      },
    ],
    metadata: {
      promptTokens: 189,
      completionTokens: 0,
      totalCost: 0.0089,
      statusCode: 429,
    },
  },
  {
    id: '3',
    requestId: 'req_9g8h7i6j5k4l',
    timestamp: '2025-01-15T10:25:48Z',
    status: 'success',
    duration: 892,
    model: 'gpt-3.5-turbo',
    user: 'mike.johnson@example.com',
    project: 'Code Review Assistant',
    spans: [
      {
        id: 'span_1',
        name: 'Request Validation',
        duration: 42,
        startTime: '2025-01-15T10:25:48.000Z',
        status: 'success',
      },
      {
        id: 'span_2',
        name: 'Prompt Template Processing',
        duration: 98,
        startTime: '2025-01-15T10:25:48.042Z',
        status: 'success',
      },
      {
        id: 'span_3',
        name: 'Model Inference',
        duration: 687,
        startTime: '2025-01-15T10:25:48.140Z',
        status: 'success',
      },
      {
        id: 'span_4',
        name: 'Response Post-Processing',
        duration: 65,
        startTime: '2025-01-15T10:25:48.827Z',
        status: 'success',
      },
    ],
    metadata: {
      promptTokens: 567,
      completionTokens: 342,
      totalCost: 0.0156,
      statusCode: 200,
    },
  },
  {
    id: '4',
    requestId: 'req_3m4n5o6p7q8r',
    timestamp: '2025-01-15T10:23:12Z',
    status: 'timeout',
    duration: 30000,
    model: 'gemini-pro',
    user: 'emily.davis@example.com',
    project: 'Data Analysis Agent',
    spans: [
      {
        id: 'span_1',
        name: 'Request Validation',
        duration: 51,
        startTime: '2025-01-15T10:23:12.000Z',
        status: 'success',
      },
      {
        id: 'span_2',
        name: 'Prompt Template Processing',
        duration: 134,
        startTime: '2025-01-15T10:23:12.051Z',
        status: 'success',
      },
      {
        id: 'span_3',
        name: 'Model Inference',
        duration: 29815,
        startTime: '2025-01-15T10:23:12.185Z',
        status: 'error',
        metadata: {
          error: 'Request timeout',
          errorCode: 504,
        },
      },
    ],
    metadata: {
      promptTokens: 892,
      completionTokens: 0,
      totalCost: 0.0445,
      statusCode: 504,
    },
  },
  {
    id: '5',
    requestId: 'req_7s8t9u0v1w2x',
    timestamp: '2025-01-15T10:20:35Z',
    status: 'success',
    duration: 1456,
    model: 'claude-3-sonnet',
    user: 'alex.brown@example.com',
    project: 'Legal Document Summarizer',
    spans: [
      {
        id: 'span_1',
        name: 'Request Validation',
        duration: 48,
        startTime: '2025-01-15T10:20:35.000Z',
        status: 'success',
      },
      {
        id: 'span_2',
        name: 'Prompt Template Processing',
        duration: 178,
        startTime: '2025-01-15T10:20:35.048Z',
        status: 'success',
      },
      {
        id: 'span_3',
        name: 'Model Inference',
        duration: 1167,
        startTime: '2025-01-15T10:20:35.226Z',
        status: 'success',
      },
      {
        id: 'span_4',
        name: 'Response Post-Processing',
        duration: 63,
        startTime: '2025-01-15T10:20:36.393Z',
        status: 'success',
      },
    ],
    metadata: {
      promptTokens: 1234,
      completionTokens: 678,
      totalCost: 0.0567,
      statusCode: 200,
    },
  },
];
