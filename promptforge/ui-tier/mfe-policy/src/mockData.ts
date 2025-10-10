export interface PolicyRule {
  id: string;
  name: string;
  description: string;
  category: 'security' | 'compliance' | 'cost' | 'quality';
  severity: 'critical' | 'high' | 'medium' | 'low';
  enabled: boolean;
  conditions: {
    field: string;
    operator: string;
    value: string | number;
  }[];
  actions: string[];
  violationCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface PolicyViolation {
  id: string;
  ruleId: string;
  ruleName: string;
  timestamp: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  resource: string;
  description: string;
  resolved: boolean;
}

export const mockPolicies: PolicyRule[] = [
  {
    id: '1',
    name: 'PII Detection in Prompts',
    description: 'Block prompts containing personally identifiable information (PII) such as SSN, credit card numbers, or email addresses',
    category: 'security',
    severity: 'critical',
    enabled: true,
    conditions: [
      { field: 'prompt.content', operator: 'contains_pii', value: 'any' },
    ],
    actions: ['block_request', 'notify_admin', 'log_violation'],
    violationCount: 3,
    createdAt: '2025-01-10T10:00:00Z',
    updatedAt: '2025-01-15T08:30:00Z',
  },
  {
    id: '2',
    name: 'Cost Threshold Enforcement',
    description: 'Alert when daily API costs exceed $500 for any single project',
    category: 'cost',
    severity: 'high',
    enabled: true,
    conditions: [
      { field: 'daily_cost', operator: 'greater_than', value: 500 },
    ],
    actions: ['send_alert', 'require_approval'],
    violationCount: 1,
    createdAt: '2025-01-08T14:20:00Z',
    updatedAt: '2025-01-14T16:45:00Z',
  },
  {
    id: '3',
    name: 'Toxic Content Filter',
    description: 'Prevent generation of toxic, harmful, or inappropriate content',
    category: 'compliance',
    severity: 'critical',
    enabled: true,
    conditions: [
      { field: 'content.toxicity_score', operator: 'greater_than', value: 0.7 },
    ],
    actions: ['block_request', 'log_violation', 'quarantine_prompt'],
    violationCount: 7,
    createdAt: '2025-01-05T09:15:00Z',
    updatedAt: '2025-01-15T10:20:00Z',
  },
  {
    id: '4',
    name: 'Model Version Compliance',
    description: 'Require use of approved model versions for production workloads',
    category: 'compliance',
    severity: 'medium',
    enabled: true,
    conditions: [
      { field: 'environment', operator: 'equals', value: 'production' },
      { field: 'model.version', operator: 'not_in', value: 'approved_list' },
    ],
    actions: ['block_request', 'suggest_alternative'],
    violationCount: 2,
    createdAt: '2025-01-12T11:30:00Z',
    updatedAt: '2025-01-15T09:00:00Z',
  },
  {
    id: '5',
    name: 'Response Quality Check',
    description: 'Flag responses with low quality scores for manual review',
    category: 'quality',
    severity: 'low',
    enabled: false,
    conditions: [
      { field: 'response.quality_score', operator: 'less_than', value: 0.6 },
    ],
    actions: ['flag_for_review', 'collect_feedback'],
    violationCount: 12,
    createdAt: '2025-01-07T13:45:00Z',
    updatedAt: '2025-01-13T15:30:00Z',
  },
  {
    id: '6',
    name: 'Rate Limit Enforcement',
    description: 'Enforce rate limits of 100 requests per minute per user',
    category: 'security',
    severity: 'high',
    enabled: true,
    conditions: [
      { field: 'requests_per_minute', operator: 'greater_than', value: 100 },
    ],
    actions: ['throttle_requests', 'log_violation'],
    violationCount: 5,
    createdAt: '2025-01-09T08:00:00Z',
    updatedAt: '2025-01-15T07:15:00Z',
  },
];

export const mockViolations: PolicyViolation[] = [
  {
    id: '1',
    ruleId: '3',
    ruleName: 'Toxic Content Filter',
    timestamp: '2025-01-15T10:30:00Z',
    severity: 'critical',
    resource: 'Project: Customer Support / User: john.doe@example.com',
    description: 'Detected toxic language in prompt with toxicity score of 0.85',
    resolved: false,
  },
  {
    id: '2',
    ruleId: '1',
    ruleName: 'PII Detection in Prompts',
    timestamp: '2025-01-15T09:45:00Z',
    severity: 'critical',
    resource: 'Project: Data Analysis / User: sarah.smith@example.com',
    description: 'Prompt contained credit card number (****-****-****-1234)',
    resolved: true,
  },
  {
    id: '3',
    ruleId: '6',
    ruleName: 'Rate Limit Enforcement',
    timestamp: '2025-01-15T09:15:00Z',
    severity: 'high',
    resource: 'User: api-bot@example.com',
    description: 'User exceeded rate limit with 157 requests in one minute',
    resolved: false,
  },
  {
    id: '4',
    ruleId: '2',
    ruleName: 'Cost Threshold Enforcement',
    timestamp: '2025-01-14T16:30:00Z',
    severity: 'high',
    resource: 'Project: Content Generation Pipeline',
    description: 'Daily cost reached $523.45, exceeding threshold of $500',
    resolved: true,
  },
  {
    id: '5',
    ruleId: '4',
    ruleName: 'Model Version Compliance',
    timestamp: '2025-01-14T14:20:00Z',
    severity: 'medium',
    resource: 'Project: Legal Summarizer / Environment: production',
    description: 'Attempted to use unapproved model version gpt-4-preview in production',
    resolved: true,
  },
];
