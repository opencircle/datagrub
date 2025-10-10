export interface Model {
  id: string;
  name: string;
  provider: 'OpenAI' | 'Anthropic' | 'Google' | 'Meta' | 'Cohere';
  version: string;
  description: string;
  status: 'active' | 'deprecated' | 'beta';
  capabilities: string[];
  pricing: {
    inputTokens: number; // per 1M tokens
    outputTokens: number; // per 1M tokens
  };
  limits: {
    maxTokens: number;
    rateLimit: number; // requests per minute
  };
  performance: {
    avgLatency: number; // in ms
    successRate: number; // percentage
  };
  usage: {
    totalRequests: number;
    totalCost: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface ModelConfig {
  id: string;
  modelId: string;
  environment: 'development' | 'staging' | 'production';
  enabled: boolean;
  defaultParameters: {
    temperature: number;
    maxTokens: number;
    topP: number;
  };
  customSettings?: Record<string, any>;
}

export const mockModels: Model[] = [
  {
    id: '1',
    name: 'GPT-4 Turbo',
    provider: 'OpenAI',
    version: 'gpt-4-turbo-2024-04-09',
    description: 'Most capable GPT-4 model with 128K context window and improved instruction following',
    status: 'active',
    capabilities: ['text-generation', 'code', 'analysis', 'reasoning'],
    pricing: {
      inputTokens: 10.00,
      outputTokens: 30.00,
    },
    limits: {
      maxTokens: 128000,
      rateLimit: 500,
    },
    performance: {
      avgLatency: 1247,
      successRate: 99.8,
    },
    usage: {
      totalRequests: 45623,
      totalCost: 1234.56,
    },
    createdAt: '2024-04-09T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '2',
    name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    version: 'gpt-3.5-turbo-0125',
    description: 'Fast and cost-effective model for simpler tasks',
    status: 'active',
    capabilities: ['text-generation', 'conversation', 'summarization'],
    pricing: {
      inputTokens: 0.50,
      outputTokens: 1.50,
    },
    limits: {
      maxTokens: 16385,
      rateLimit: 1000,
    },
    performance: {
      avgLatency: 523,
      successRate: 99.9,
    },
    usage: {
      totalRequests: 128456,
      totalCost: 456.78,
    },
    createdAt: '2024-01-25T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '3',
    name: 'Claude 3 Opus',
    provider: 'Anthropic',
    version: 'claude-3-opus-20240229',
    description: 'Most powerful Claude model for highly complex tasks',
    status: 'active',
    capabilities: ['text-generation', 'analysis', 'reasoning', 'code', 'vision'],
    pricing: {
      inputTokens: 15.00,
      outputTokens: 75.00,
    },
    limits: {
      maxTokens: 200000,
      rateLimit: 400,
    },
    performance: {
      avgLatency: 1856,
      successRate: 99.7,
    },
    usage: {
      totalRequests: 23456,
      totalCost: 2345.67,
    },
    createdAt: '2024-02-29T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '4',
    name: 'Claude 3 Sonnet',
    provider: 'Anthropic',
    version: 'claude-3-sonnet-20240229',
    description: 'Balanced performance and speed for scaled deployments',
    status: 'active',
    capabilities: ['text-generation', 'analysis', 'reasoning', 'vision'],
    pricing: {
      inputTokens: 3.00,
      outputTokens: 15.00,
    },
    limits: {
      maxTokens: 200000,
      rateLimit: 500,
    },
    performance: {
      avgLatency: 892,
      successRate: 99.8,
    },
    usage: {
      totalRequests: 67890,
      totalCost: 890.12,
    },
    createdAt: '2024-02-29T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '5',
    name: 'Gemini Pro',
    provider: 'Google',
    version: 'gemini-1.0-pro',
    description: 'Google\'s most capable multimodal model',
    status: 'active',
    capabilities: ['text-generation', 'multimodal', 'code', 'vision'],
    pricing: {
      inputTokens: 0.50,
      outputTokens: 1.50,
    },
    limits: {
      maxTokens: 32768,
      rateLimit: 600,
    },
    performance: {
      avgLatency: 1123,
      successRate: 99.5,
    },
    usage: {
      totalRequests: 34567,
      totalCost: 234.56,
    },
    createdAt: '2023-12-13T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '6',
    name: 'Llama 2 70B',
    provider: 'Meta',
    version: 'llama-2-70b-chat',
    description: 'Open source large language model optimized for dialogue',
    status: 'active',
    capabilities: ['text-generation', 'conversation', 'reasoning'],
    pricing: {
      inputTokens: 0.70,
      outputTokens: 0.90,
    },
    limits: {
      maxTokens: 4096,
      rateLimit: 300,
    },
    performance: {
      avgLatency: 2145,
      successRate: 98.9,
    },
    usage: {
      totalRequests: 12345,
      totalCost: 123.45,
    },
    createdAt: '2023-07-18T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '7',
    name: 'Command R+',
    provider: 'Cohere',
    version: 'command-r-plus',
    description: 'Optimized for RAG and tool use applications',
    status: 'beta',
    capabilities: ['text-generation', 'retrieval', 'tool-use'],
    pricing: {
      inputTokens: 3.00,
      outputTokens: 15.00,
    },
    limits: {
      maxTokens: 128000,
      rateLimit: 400,
    },
    performance: {
      avgLatency: 1456,
      successRate: 99.2,
    },
    usage: {
      totalRequests: 5678,
      totalCost: 67.89,
    },
    createdAt: '2024-03-15T00:00:00Z',
    updatedAt: '2025-01-15T10:00:00Z',
  },
  {
    id: '8',
    name: 'GPT-4',
    provider: 'OpenAI',
    version: 'gpt-4-0613',
    description: 'Previous generation GPT-4 model',
    status: 'deprecated',
    capabilities: ['text-generation', 'code', 'analysis'],
    pricing: {
      inputTokens: 30.00,
      outputTokens: 60.00,
    },
    limits: {
      maxTokens: 8192,
      rateLimit: 200,
    },
    performance: {
      avgLatency: 2341,
      successRate: 99.6,
    },
    usage: {
      totalRequests: 89012,
      totalCost: 3456.78,
    },
    createdAt: '2023-06-13T00:00:00Z',
    updatedAt: '2024-11-20T00:00:00Z',
  },
];

export const mockConfigs: ModelConfig[] = [
  {
    id: '1',
    modelId: '1',
    environment: 'production',
    enabled: true,
    defaultParameters: {
      temperature: 0.7,
      maxTokens: 2000,
      topP: 0.9,
    },
  },
  {
    id: '2',
    modelId: '2',
    environment: 'development',
    enabled: true,
    defaultParameters: {
      temperature: 0.8,
      maxTokens: 1000,
      topP: 0.95,
    },
  },
  {
    id: '3',
    modelId: '4',
    environment: 'production',
    enabled: true,
    defaultParameters: {
      temperature: 0.6,
      maxTokens: 3000,
      topP: 0.9,
    },
  },
];
