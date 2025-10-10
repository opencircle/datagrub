export interface Variable {
  name: string;
  type: 'string' | 'number' | 'boolean';
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export interface FewShotExample {
  id: string;
  input: string;
  output: string;
}

export interface PromptFormData {
  name: string;
  description: string;
  systemPrompt: string;
  userPrompt: string;
  intent: string;
  tone: string;
  variables: Variable[];
  fewShotExamples: FewShotExample[];
}

export interface Prompt extends PromptFormData {
  id: string;
  projectId: string;
  version: number;
  status: 'draft' | 'active' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export interface PromptVersion {
  id: string;
  promptId: string;
  version: number;
  data: PromptFormData;
  createdAt: string;
  createdBy: string;
}
