import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '../../../../shared/components/core/Button';
import { Input } from '../../../../shared/components/forms/Input';
import { Select } from '../../../../shared/components/forms/Select';
import { Textarea } from '../../../../shared/components/forms/Textarea';
import { EVALUATION_CATEGORIES, CustomEvaluationCreate } from '../../types/customEvaluation';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Fetch available models from API
async function fetchAvailableModels(): Promise<Array<{value: string; label: string}>> {
  const token = localStorage.getItem('promptforge_access_token');
  const response = await fetch(`${API_BASE_URL}/api/v1/models/available`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }
  const data = await response.json();
  return data.map((m: any) => ({
    value: m.model_id,
    label: m.display_name,
  }));
}

export interface CreateCustomEvaluationFormProps {
  onCancel: () => void;
  onSuccess: (evaluation: CustomEvaluationCreate) => void;
}

interface FormData {
  name: string;
  category: string;
  description: string;
  prompt_input: string;
  prompt_output: string;
  system_prompt: string;
  model: string;
}

interface FormErrors {
  name?: string;
  category?: string;
  prompt_input?: string;
  prompt_output?: string;
  system_prompt?: string;
  model?: string;
}

const initialFormData: FormData = {
  name: '',
  category: '',
  description: '',
  prompt_input: '',
  prompt_output: '',
  system_prompt: '',
  model: 'gpt-4o-mini',
};

export const CreateCustomEvaluationForm: React.FC<CreateCustomEvaluationFormProps> = ({
  onCancel,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch available models using React Query (prevents duplicate calls, provides caching)
  const { data: availableModels = [], isLoading: isLoadingModels } = useQuery({
    queryKey: ['models', 'available'],
    queryFn: fetchAvailableModels,
    staleTime: 60000, // Cache for 1 minute
    retry: 2,
  });

  // Set initial model when models are loaded
  useEffect(() => {
    if (availableModels.length > 0 && !availableModels.find(m => m.value === formData.model)) {
      setFormData(prev => ({ ...prev, model: availableModels[0].value }));
    }
  }, [availableModels, formData.model]);

  const validateField = (name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'name':
        if (!value.trim()) return 'Evaluation name is required';
        if (value.length < 3) return 'Name must be at least 3 characters';
        if (value.length > 100) return 'Name cannot exceed 100 characters';
        return undefined;

      case 'category':
        if (!value) return 'Please select a category';
        return undefined;

      case 'prompt_input':
        if (!value.trim()) return 'Model input definition is required';
        if (value.length < 10) return 'Model input must be at least 10 characters';
        if (value.length > 2000) return 'Model input cannot exceed 2000 characters';
        return undefined;

      case 'prompt_output':
        if (!value.trim()) return 'Model output definition is required';
        if (value.length < 10) return 'Model output must be at least 10 characters';
        if (value.length > 2000) return 'Model output cannot exceed 2000 characters';
        return undefined;

      case 'system_prompt':
        if (!value.trim()) return 'Evaluation system prompt is required';
        if (value.length < 10) return 'Evaluation system prompt must be at least 10 characters';
        if (value.length > 2000) return 'Evaluation system prompt cannot exceed 2000 characters';
        return undefined;

      case 'model':
        if (!value) return 'Please select a model';
        return undefined;

      case 'description':
        if (value.length > 500) return 'Description cannot exceed 500 characters';
        return undefined;

      default:
        return undefined;
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;

    (Object.keys(formData) as Array<keyof FormData>).forEach((key) => {
      const error = validateField(key, formData[key]);
      if (error) {
        newErrors[key] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));

    const error = validateField(name as keyof FormData, value);
    if (error) {
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    const allTouched = (Object.keys(formData) as Array<keyof FormData>).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {} as Record<string, boolean>);

    setTouched(allTouched);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const evaluationData: CustomEvaluationCreate = {
        name: formData.name,
        category: formData.category,
        description: formData.description || undefined,
        prompt_input: formData.prompt_input,
        prompt_output: formData.prompt_output,
        system_prompt: formData.system_prompt,
        model: formData.model,
      };

      await onSuccess(evaluationData);

      // Reset form
      setFormData(initialFormData);
      setErrors({});
      setTouched({});
    } catch (error) {
      console.error('Failed to create evaluation:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = Object.keys(errors).length === 0 &&
    formData.name &&
    formData.category &&
    formData.prompt_input &&
    formData.prompt_output &&
    formData.system_prompt &&
    formData.model;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name Field */}
      <Input
        label="Name"
        name="name"
        required
        placeholder="e.g., Tone Consistency Check"
        value={formData.name}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.name ? errors.name : undefined}
      />

      {/* Category and Model - Two Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Category"
          name="category"
          required
          value={formData.category}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.category ? errors.category : undefined}
          options={[
            { value: '', label: 'Select a category' },
            ...EVALUATION_CATEGORIES,
          ]}
        />

        <Select
          label="Model"
          name="model"
          required
          value={formData.model}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.model ? errors.model : undefined}
          disabled={isLoadingModels}
          options={
            isLoadingModels
              ? [{ value: '', label: 'Loading models...' }]
              : availableModels.length === 0
              ? [{ value: '', label: 'No models configured' }]
              : availableModels
          }
        />
      </div>

      {/* Description Field */}
      <Textarea
        label="Description"
        name="description"
        placeholder="Describe the purpose of this evaluation..."
        value={formData.description}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.description ? errors.description : undefined}
        helpText="Optional, helps team understand evaluation goals"
        rows={3}
        className="max-h-[120px]"
      />

      {/* Model Input Field */}
      <Textarea
        label="Model Input"
        name="prompt_input"
        required
        placeholder="Reference the model's input with {{model_input}} or use {{variable}} placeholders..."
        value={formData.prompt_input}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.prompt_input ? errors.prompt_input : undefined}
        helpText="Define how to access the model's input for evaluation (use {{model_input}} or custom variables)"
        rows={6}
        className="min-h-[120px] max-h-[200px]"
      />

      {/* Model Output Field */}
      <Textarea
        label="Model Output"
        name="prompt_output"
        required
        placeholder="Reference the model's output with {{model_output}} or use {{variable}} placeholders..."
        value={formData.prompt_output}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.prompt_output ? errors.prompt_output : undefined}
        helpText="Define how to access the model's output for evaluation (use {{model_output}} or custom variables)"
        rows={6}
        className="min-h-[120px] max-h-[200px]"
      />

      {/* System Prompt Field */}
      <Textarea
        label="Evaluation System Prompt"
        name="system_prompt"
        required
        placeholder="You are an expert evaluator. Analyze the model's input and output, then return a score from 0-1 and a pass/fail determination..."
        value={formData.system_prompt}
        onChange={handleChange}
        onBlur={handleBlur}
        error={touched.system_prompt ? errors.system_prompt : undefined}
        helpText="Define the evaluation logic that will receive the model input/output and return a score (0-1) and pass/fail"
        rows={8}
        className="min-h-[160px] max-h-[240px]"
      />

      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-neutral-200">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          disabled={!isValid || isSubmitting}
          loading={isSubmitting}
        >
          Create Evaluation
        </Button>
      </div>
    </form>
  );
};
