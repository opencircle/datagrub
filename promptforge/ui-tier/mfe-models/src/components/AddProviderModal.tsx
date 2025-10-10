/**
 * Add Provider Modal Component
 *
 * Dynamic form modal for adding new model provider configurations.
 * Form fields are generated based on provider metadata from the catalog.
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Eye, EyeOff, ExternalLink, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import {
  ProviderMetadata,
  ProviderMetadataField,
  ProviderFormData,
} from '../types/provider';
import {
  getProviderCatalog,
  createProviderConfig,
} from '../services/providerService';

interface AddProviderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddProviderModal: React.FC<AddProviderModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [step, setStep] = useState<'select' | 'configure'>('select');
  const [catalog, setCatalog] = useState<ProviderMetadata[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<ProviderMetadata | null>(null);
  const [formData, setFormData] = useState<ProviderFormData>({
    provider_name: '',
    provider_type: 'llm',
    display_name: '',
    is_default: false,
    api_key: '',
  });
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadCatalog();
    }
  }, [isOpen]);

  const loadCatalog = async () => {
    try {
      const data = await getProviderCatalog();
      setCatalog(data.providers);
    } catch (error) {
      console.error('Error loading provider catalog:', error);
    }
  };

  const handleProviderSelect = (provider: ProviderMetadata) => {
    setSelectedProvider(provider);
    setFormData({
      provider_name: provider.provider_name,
      provider_type: provider.provider_type,
      display_name: `${provider.display_name} Config`,
      is_default: false,
      api_key: '',
    });
    setStep('configure');
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));

    // Clear error for this field
    if (errors[fieldName]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };

  const validateField = (field: ProviderMetadataField, value: any): string | null => {
    if (field.required && !value) {
      return `${field.label} is required`;
    }

    if (field.validation) {
      const { pattern, min_length, max_length, min, max } = field.validation;

      if (typeof value === 'string') {
        if (min_length && value.length < min_length) {
          return `${field.label} must be at least ${min_length} characters`;
        }
        if (max_length && value.length > max_length) {
          return `${field.label} must be at most ${max_length} characters`;
        }
        if (pattern && !new RegExp(pattern).test(value)) {
          // Provide helpful error message for specific patterns
          if (pattern.includes('sk-ant-')) {
            return `${field.label} must start with "sk-ant-" or "sk-ant-api03-" (total: 102-108 chars)`;
          } else if (pattern.includes('sk-proj-') || pattern.includes('sk-')) {
            return `${field.label} must start with "${field.placeholder?.split('...')[0] || 'sk-'}"`;
          }
          return `${field.label} format is invalid. Expected format: ${field.placeholder || 'see help text'}`;
        }
      }

      if (typeof value === 'number') {
        if (min !== undefined && value < min) {
          return `${field.label} must be at least ${min}`;
        }
        if (max !== undefined && value > max) {
          return `${field.label} must be at most ${max}`;
        }
      }
    }

    return null;
  };

  const validateForm = (): boolean => {
    if (!selectedProvider) return false;

    const newErrors: Record<string, string> = {};

    // Validate required fields
    [...selectedProvider.required_fields, ...selectedProvider.optional_fields].forEach(
      (field) => {
        const value = formData[field.name];
        const error = validateField(field, value);
        if (error) {
          newErrors[field.name] = error;
        }
      }
    );

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setSubmitting(true);

      // Build config object from optional fields
      const config: Record<string, any> = {};
      selectedProvider?.optional_fields.forEach((field) => {
        if (formData[field.name] !== undefined && formData[field.name] !== '') {
          config[field.name] = formData[field.name];
        }
      });

      await createProviderConfig({
        provider_name: formData.provider_name,
        provider_type: formData.provider_type,
        display_name: formData.display_name,
        api_key: formData.api_key,
        config: Object.keys(config).length > 0 ? config : undefined,
        is_default: formData.is_default,
      });

      onSuccess();
      handleClose();
    } catch (error: any) {
      setErrors({ submit: error.message || 'Failed to create provider configuration' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setStep('select');
    setSelectedProvider(null);
    setFormData({
      provider_name: '',
      provider_type: 'llm',
      display_name: '',
      is_default: false,
      api_key: '',
    });
    setErrors({});
    setShowPassword({});
    onClose();
  };

  const renderField = (field: ProviderMetadataField) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];

    switch (field.type) {
      case 'password':
        return (
          <div key={field.name} className="space-y-2">
            <label className="block text-sm font-medium text-neutral-700">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.help_text && (
              <p className="text-xs text-neutral-500">{field.help_text}</p>
            )}
            <div className="relative">
              <input
                type={showPassword[field.name] ? 'text' : 'password'}
                value={value}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                className={clsx(
                  'w-full h-12 px-4 pr-12 rounded-xl border transition-all',
                  error
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                    : 'border-neutral-200 focus:border-[#FF385C] focus:ring-[#FF385C]/20',
                  'focus:outline-none focus:ring-4'
                )}
              />
              <button
                type="button"
                onClick={() =>
                  setShowPassword((prev) => ({
                    ...prev,
                    [field.name]: !prev[field.name],
                  }))
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
              >
                {showPassword[field.name] ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
            {error && (
              <p className="text-xs text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
          </div>
        );

      case 'select':
        return (
          <div key={field.name} className="space-y-2">
            <label className="block text-sm font-medium text-neutral-700">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.help_text && (
              <p className="text-xs text-neutral-500">{field.help_text}</p>
            )}
            <select
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              className={clsx(
                'w-full h-12 px-4 rounded-xl border transition-all',
                error
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                  : 'border-neutral-200 focus:border-[#FF385C] focus:ring-[#FF385C]/20',
                'focus:outline-none focus:ring-4'
              )}
            >
              <option value="">Select {field.label}</option>
              {field.options?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {error && (
              <p className="text-xs text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
          </div>
        );

      case 'boolean':
        return (
          <div key={field.name} className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={value === true}
              onChange={(e) => handleFieldChange(field.name, e.target.checked)}
              className="h-5 w-5 rounded border-neutral-300 text-[#FF385C] focus:ring-[#FF385C]/20"
            />
            <div>
              <label className="block text-sm font-medium text-neutral-700">
                {field.label}
              </label>
              {field.help_text && (
                <p className="text-xs text-neutral-500">{field.help_text}</p>
              )}
            </div>
          </div>
        );

      case 'number':
        return (
          <div key={field.name} className="space-y-2">
            <label className="block text-sm font-medium text-neutral-700">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.help_text && (
              <p className="text-xs text-neutral-500">{field.help_text}</p>
            )}
            <input
              type="number"
              value={value}
              onChange={(e) => handleFieldChange(field.name, Number(e.target.value))}
              placeholder={field.placeholder}
              min={field.validation?.min}
              max={field.validation?.max}
              className={clsx(
                'w-full h-12 px-4 rounded-xl border transition-all',
                error
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                  : 'border-neutral-200 focus:border-[#FF385C] focus:ring-[#FF385C]/20',
                'focus:outline-none focus:ring-4'
              )}
            />
            {error && (
              <p className="text-xs text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
          </div>
        );

      default: // string, url
        return (
          <div key={field.name} className="space-y-2">
            <label className="block text-sm font-medium text-neutral-700">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {field.help_text && (
              <p className="text-xs text-neutral-500">{field.help_text}</p>
            )}
            <input
              type={field.type === 'url' ? 'url' : 'text'}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              placeholder={field.placeholder || field.default}
              className={clsx(
                'w-full h-12 px-4 rounded-xl border transition-all',
                error
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                  : 'border-neutral-200 focus:border-[#FF385C] focus:ring-[#FF385C]/20',
                'focus:outline-none focus:ring-4'
              )}
            />
            {error && (
              <p className="text-xs text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
          </div>
        );
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/50 z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-neutral-100">
                <h2 className="text-xl font-bold text-neutral-800">
                  {step === 'select' ? 'Select Provider' : 'Configure Provider'}
                </h2>
                <button
                  onClick={handleClose}
                  className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                  aria-label="Close modal"
                >
                  <X className="h-5 w-5 text-neutral-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                {step === 'select' ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {catalog.map((provider) => (
                      <button
                        key={`${provider.provider_name}-${provider.provider_type}`}
                        onClick={() => handleProviderSelect(provider)}
                        className="bg-white border-2 border-neutral-200 hover:border-[#FF385C] rounded-xl p-6 text-left transition-all hover:shadow-md"
                      >
                        <div className="flex items-start gap-4">
                          {provider.icon_url ? (
                            <>
                              <img
                                src={provider.icon_url}
                                alt={`${provider.display_name} logo`}
                                className="h-12 w-12 object-contain"
                                onError={(e) => {
                                  e.currentTarget.style.display = 'none';
                                  const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                                  if (fallback) fallback.classList.remove('hidden');
                                }}
                              />
                              <div className="h-12 w-12 rounded-lg bg-neutral-100 flex items-center justify-center hidden">
                                <span className="text-sm font-semibold text-neutral-600">
                                  {provider.display_name.substring(0, 2).toUpperCase()}
                                </span>
                              </div>
                            </>
                          ) : (
                            <div className="h-12 w-12 rounded-lg bg-neutral-100 flex items-center justify-center">
                              <span className="text-sm font-semibold text-neutral-600">
                                {provider.provider_name.substring(0, 2).toUpperCase()}
                              </span>
                            </div>
                          )}
                          <div className="flex-1">
                            <h3 className="font-semibold text-neutral-800 mb-1">
                              {provider.display_name}
                            </h3>
                            <p className="text-sm text-neutral-500 mb-2">
                              {provider.description}
                            </p>
                            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                              {provider.provider_type}
                            </span>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Provider Info */}
                    <div className="bg-neutral-50 rounded-xl p-4 flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        {selectedProvider?.icon_url && (
                          <img
                            src={selectedProvider.icon_url}
                            alt={selectedProvider.display_name}
                            className="h-10 w-10"
                          />
                        )}
                        <div>
                          <h3 className="font-semibold text-neutral-800">
                            {selectedProvider?.display_name}
                          </h3>
                          <p className="text-sm text-neutral-500">
                            {selectedProvider?.description}
                          </p>
                        </div>
                      </div>
                      {selectedProvider?.documentation_url && (
                        <a
                          href={selectedProvider.documentation_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#FF385C] hover:text-[#E31C5F] text-sm flex items-center gap-1"
                        >
                          Docs <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>

                    {/* Basic Fields */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-neutral-700">
                          Configuration Name<span className="text-red-500 ml-1">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.display_name}
                          onChange={(e) => handleFieldChange('display_name', e.target.value)}
                          placeholder="e.g., Production OpenAI"
                          className="w-full h-12 px-4 rounded-xl border border-neutral-200 focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 focus:outline-none transition-all"
                        />
                      </div>

                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={formData.is_default}
                          onChange={(e) => handleFieldChange('is_default', e.target.checked)}
                          className="h-5 w-5 rounded border-neutral-300 text-[#FF385C] focus:ring-[#FF385C]/20"
                        />
                        <label className="text-sm font-medium text-neutral-700">
                          Set as default provider
                        </label>
                      </div>
                    </div>

                    {/* Required Fields */}
                    <div className="space-y-4">
                      <h4 className="font-semibold text-neutral-800">Required Fields</h4>
                      {selectedProvider?.required_fields.map(renderField)}
                    </div>

                    {/* Optional Fields */}
                    {selectedProvider?.optional_fields && selectedProvider.optional_fields.length > 0 && (
                      <div className="space-y-4">
                        <h4 className="font-semibold text-neutral-800">Optional Fields</h4>
                        {selectedProvider.optional_fields.map(renderField)}
                      </div>
                    )}

                    {/* Submit Error */}
                    {errors.submit && (
                      <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                        <p className="text-sm text-red-700 flex items-center gap-2">
                          <AlertCircle className="h-4 w-4" />
                          {errors.submit}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Footer */}
              {step === 'configure' && (
                <div className="flex items-center justify-between p-6 border-t border-neutral-100">
                  <button
                    onClick={() => setStep('select')}
                    className="h-11 px-4 rounded-xl border border-neutral-200 text-neutral-700 hover:bg-neutral-50 transition-all font-medium"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="h-11 px-4 rounded-xl bg-[#FF385C] text-white hover:bg-[#E31C5F] transition-all font-semibold shadow-sm disabled:opacity-50"
                  >
                    {submitting ? 'Creating...' : 'Create Provider'}
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
