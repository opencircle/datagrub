import React, { useState } from 'react';
import { Modal } from '../../../../shared/components/core/Modal';
import { Button } from '../../../../shared/components/core/Button';
import { Input } from '../../../../shared/components/forms/Input';
import { Select } from '../../../../shared/components/forms/Select';
import { Textarea } from '../../../../shared/components/forms/Textarea';
import { EVALUATION_CATEGORIES, EVALUATION_MODELS, CustomEvaluationCreate } from '../../types/customEvaluation';

export interface CreateCustomEvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
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

export const CreateCustomEvaluationModal: React.FC<CreateCustomEvaluationModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    const error = validateField(name as keyof FormData, value);
    if (error) {
      setErrors((prev) => ({ ...prev, [name]: error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    const allTouched = Object.keys(formData).reduce((acc, key) => ({ ...acc, [key]: true }), {});
    setTouched(allTouched);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Call onSuccess with form data
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

      // Reset form and close modal
      setFormData(initialFormData);
      setErrors({});
      setTouched({});
      onClose();
    } catch (error) {
      console.error('Failed to create evaluation:', error);
      // Error handling is done in parent component
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData(initialFormData);
      setErrors({});
      setTouched({});
      onClose();
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
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create Custom Evaluation"
      size="lg"
      footer={
        <div className="flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!isValid || isSubmitting}
            loading={isSubmitting}
          >
            Create Evaluation
          </Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5">
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
            options={EVALUATION_MODELS}
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
          placeholder="Reference the model's output with {{model_output}} or define expected format..."
          value={formData.prompt_output}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.prompt_output ? errors.prompt_output : undefined}
          helpText="Define how to access the model's output for evaluation (use {{model_output}} or specify schema)"
          rows={6}
          className="min-h-[120px] max-h-[200px]"
        />

        {/* System Prompt Field */}
        <Textarea
          label="Evaluation System Prompt"
          name="system_prompt"
          required
          placeholder="You are an expert evaluator. Analyze the model's input and output to assess {{criteria}}..."
          value={formData.system_prompt}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.system_prompt ? errors.system_prompt : undefined}
          helpText="System prompt that evaluates the model's input/output after invocation. Return score (0-1) and pass/fail."
          rows={6}
          className="min-h-[120px] max-h-[200px]"
        />
      </form>
    </Modal>
  );
};
