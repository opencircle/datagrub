import React, { useState } from 'react';
import { PromptFormData, Variable, FewShotExample } from '../../types/prompt';
import { Modal } from '../../../../shared/components/core/Modal';
import { Button } from '../../../../shared/components/core/Button';
import { Input } from '../../../../shared/components/forms/Input';
import { Textarea } from '../../../../shared/components/forms/Textarea';
import { Select } from '../../../../shared/components/forms/Select';
import { VariableEditor } from './VariableEditor';
import { FewShotExamples } from './FewShotExamples';

interface PromptBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PromptFormData) => Promise<void>;
  initialData?: Partial<PromptFormData>;
  mode?: 'create' | 'edit';
}

type Tab = 'basic' | 'system' | 'user' | 'variables' | 'examples';

const TABS: { id: Tab; label: string }[] = [
  { id: 'basic', label: 'Basic Info' },
  { id: 'system', label: 'System Prompt' },
  { id: 'user', label: 'User Prompt' },
  { id: 'variables', label: 'Variables' },
  { id: 'examples', label: 'Few-Shot Examples' },
];

export const PromptBuilderModal: React.FC<PromptBuilderModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode = 'create',
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('basic');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<PromptFormData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    systemPrompt: initialData?.systemPrompt || '',
    userPrompt: initialData?.userPrompt || '',
    intent: initialData?.intent || '',
    tone: initialData?.tone || 'professional',
    variables: initialData?.variables || [],
    fewShotExamples: initialData?.fewShotExamples || [],
  });

  const updateField = <K extends keyof PromptFormData>(
    field: K,
    value: PromptFormData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.systemPrompt.trim() && !formData.userPrompt.trim()) {
      newErrors.systemPrompt = 'At least one prompt (system or user) is required';
    }

    // Validate variables
    formData.variables.forEach((variable, index) => {
      if (!variable.name.trim()) {
        newErrors[`variable-${index}`] = 'Variable name is required';
      }
    });

    // Validate few-shot examples
    formData.fewShotExamples.forEach((example, index) => {
      if (!example.input.trim() || !example.output.trim()) {
        newErrors[`example-${index}`] = 'Both input and output are required';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) {
      // Switch to first tab with error
      if (errors.name || errors.systemPrompt) {
        setActiveTab('basic');
      }
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Failed to submit prompt:', error);
      setErrors({ submit: 'Failed to save prompt. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'basic':
        return (
          <div className="space-y-4">
            <Input
              label="Prompt Name"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="e.g., Customer Support Assistant"
              error={errors.name}
              required
            />

            <Textarea
              label="Description"
              value={formData.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Describe the purpose and use case for this prompt..."
              rows={3}
            />

            <Input
              label="Intent"
              value={formData.intent}
              onChange={(e) => updateField('intent', e.target.value)}
              placeholder="e.g., Answer customer questions, Generate code"
            />

            <Select
              label="Tone"
              value={formData.tone}
              onChange={(e) => updateField('tone', e.target.value)}
              options={[
                { value: 'professional', label: 'Professional' },
                { value: 'casual', label: 'Casual' },
                { value: 'friendly', label: 'Friendly' },
                { value: 'formal', label: 'Formal' },
                { value: 'technical', label: 'Technical' },
                { value: 'empathetic', label: 'Empathetic' },
              ]}
            />
          </div>
        );

      case 'system':
        return (
          <div className="space-y-4">
            <Textarea
              label="System Prompt"
              value={formData.systemPrompt}
              onChange={(e) => updateField('systemPrompt', e.target.value)}
              placeholder="You are a helpful assistant that..."
              rows={10}
              error={errors.systemPrompt}
              helpText="Define the model's role, behavior, and constraints"
            />
            <div className="text-xs text-gray-500">
              Use {'{variable_name}'} syntax to reference variables
            </div>
          </div>
        );

      case 'user':
        return (
          <div className="space-y-4">
            <Textarea
              label="User Prompt Template"
              value={formData.userPrompt}
              onChange={(e) => updateField('userPrompt', e.target.value)}
              placeholder="Please help me with {user_query}..."
              rows={10}
              helpText="Template for user messages with variable placeholders"
            />
            <div className="text-xs text-gray-500">
              Use {'{variable_name}'} syntax to reference variables
            </div>
          </div>
        );

      case 'variables':
        return (
          <VariableEditor
            variables={formData.variables}
            onChange={(variables) => updateField('variables', variables)}
          />
        );

      case 'examples':
        return (
          <FewShotExamples
            examples={formData.fewShotExamples}
            onChange={(examples) => updateField('fewShotExamples', examples)}
          />
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === 'create' ? 'Create New Prompt' : 'Edit Prompt'}
      size="xl"
    >
      <div className="flex flex-col h-[600px]">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px space-x-4 px-6" aria-label="Tabs">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
                aria-current={activeTab === tab.id ? 'page' : undefined}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {renderTabContent()}
        </div>

        {/* Error Display */}
        {errors.submit && (
          <div className="px-6 py-3 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 flex items-center justify-between bg-gray-50">
          <div className="text-sm text-gray-600">
            Step {TABS.findIndex((t) => t.id === activeTab) + 1} of {TABS.length}
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            {activeTab !== 'basic' && (
              <Button
                variant="secondary"
                onClick={() => {
                  const currentIndex = TABS.findIndex((t) => t.id === activeTab);
                  if (currentIndex > 0) {
                    setActiveTab(TABS[currentIndex - 1].id);
                  }
                }}
                disabled={isSubmitting}
              >
                Previous
              </Button>
            )}
            {activeTab !== 'examples' ? (
              <Button
                variant="primary"
                onClick={() => {
                  const currentIndex = TABS.findIndex((t) => t.id === activeTab);
                  if (currentIndex < TABS.length - 1) {
                    setActiveTab(TABS[currentIndex + 1].id);
                  }
                }}
                disabled={isSubmitting}
              >
                Next
              </Button>
            ) : (
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create Prompt' : 'Save Changes'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};
