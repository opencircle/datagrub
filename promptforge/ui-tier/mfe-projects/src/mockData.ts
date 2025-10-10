export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'archived' | 'draft';
  promptCount: number;
  lastUpdated: string;
  organization: string;
  tags: string[];
}

export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Customer Support Assistant',
    description: 'AI-powered customer support chatbot with context-aware responses',
    status: 'active',
    promptCount: 45,
    lastUpdated: '2025-01-15',
    organization: 'PromptForge Demo',
    tags: ['customer-service', 'chatbot', 'production'],
  },
  {
    id: '2',
    name: 'Content Generation Pipeline',
    description: 'Automated content generation for marketing materials',
    status: 'active',
    promptCount: 23,
    lastUpdated: '2025-01-14',
    organization: 'PromptForge Demo',
    tags: ['content', 'marketing', 'automation'],
  },
  {
    id: '3',
    name: 'Code Review Assistant',
    description: 'AI code reviewer for pull requests and quality checks',
    status: 'active',
    promptCount: 12,
    lastUpdated: '2025-01-13',
    organization: 'PromptForge Demo',
    tags: ['development', 'code-review', 'automation'],
  },
  {
    id: '4',
    name: 'Data Analysis Agent',
    description: 'Automated data analysis and insights generation',
    status: 'draft',
    promptCount: 8,
    lastUpdated: '2025-01-10',
    organization: 'PromptForge Demo',
    tags: ['analytics', 'data-science', 'experimental'],
  },
  {
    id: '5',
    name: 'Legal Document Summarizer',
    description: 'Summarize and extract key points from legal documents',
    status: 'archived',
    promptCount: 34,
    lastUpdated: '2024-12-20',
    organization: 'PromptForge Demo',
    tags: ['legal', 'summarization', 'archived'],
  },
];
