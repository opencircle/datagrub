export interface Model {
  id: string;
  name: string;
  provider: string;
  input_cost?: number;
  output_cost?: number;
  costMultiplier?: number;
}

export interface PlaygroundSession {
  id: string;
  timestamp: string;
  prompt: string;
  response: string;
  model: Model;
  parameters: {
    temperature: number;
    maxTokens: number;
    topP: number;
  };
  metrics: {
    latency: number;
    tokens: number;
    cost: number;
  };
}

export const availableModels: Model[] = [
  // OpenAI Models (2025 - Latest)
  { id: 'gpt-4.1', name: 'GPT-4.1', provider: 'OpenAI' },
  { id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini', provider: 'OpenAI' },
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI' },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'OpenAI' },
  { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI' },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI' },

  // Anthropic Claude Models (2025 - Latest)
  { id: 'claude-sonnet-4-5-20250929', name: 'Claude Sonnet 4.5', provider: 'Anthropic' },
  { id: 'claude-opus-4-1-20250805', name: 'Claude Opus 4.1', provider: 'Anthropic' },
  { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet', provider: 'Anthropic' },
  { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku', provider: 'Anthropic' },
  { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus', provider: 'Anthropic' },
  { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet', provider: 'Anthropic' },
  { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku', provider: 'Anthropic' },

  // Google Models
  { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', provider: 'Google' },
  { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google' },
  { id: 'gemini-pro', name: 'Gemini Pro', provider: 'Google' },
];

export const mockSessions: PlaygroundSession[] = [
  {
    id: '1',
    timestamp: '2025-01-15T10:30:00Z',
    prompt: 'Write a product description for a smart home thermostat.',
    response: 'Introducing the SmartTemp Pro - your intelligent climate control solution. This advanced thermostat learns your preferences and automatically adjusts to your schedule, ensuring optimal comfort while reducing energy costs by up to 30%. With WiFi connectivity, voice control compatibility, and an intuitive touchscreen interface, managing your home\'s climate has never been easier.',
    model: { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI' },
    parameters: {
      temperature: 0.7,
      maxTokens: 500,
      topP: 0.9,
    },
    metrics: {
      latency: 1.2,
      tokens: 89,
      cost: 0.0023,
    },
  },
  {
    id: '2',
    timestamp: '2025-01-15T09:15:00Z',
    prompt: 'Explain quantum computing to a 10-year-old.',
    response: 'Imagine if your brain could think about many different answers to a puzzle all at the same time, instead of trying them one by one. That\'s kind of what quantum computers do! Regular computers use tiny switches that are either on or off (like light switches), but quantum computers use special "quantum switches" that can be both on AND off at the same time. This helps them solve really hard problems much faster than normal computers.',
    model: { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'Anthropic' },
    parameters: {
      temperature: 0.8,
      maxTokens: 300,
      topP: 0.95,
    },
    metrics: {
      latency: 0.9,
      tokens: 102,
      cost: 0.0018,
    },
  },
  {
    id: '3',
    timestamp: '2025-01-15T08:45:00Z',
    prompt: 'Generate a tagline for a sustainable fashion brand.',
    response: 'Style with conscience, fashion with future.',
    model: { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI' },
    parameters: {
      temperature: 0.9,
      maxTokens: 50,
      topP: 1.0,
    },
    metrics: {
      latency: 0.4,
      tokens: 9,
      cost: 0.0001,
    },
  },
];
