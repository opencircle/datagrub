import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Project } from '../../../shared/services/projectService';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProjectFormData) => Promise<void>;
  mode: 'create' | 'edit';
  initialData?: Project;
}

export interface ProjectFormData {
  name: string;
  description: string;
  status: 'active' | 'draft' | 'archived';
  organizationId: string;
}

export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  mode,
  initialData,
}) => {
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    status: 'active',
    organizationId: '', // Will be set from user context
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData && mode === 'edit') {
      setFormData({
        name: initialData.name,
        description: initialData.description || '',
        status: initialData.status,
        organizationId: initialData.organization_id,
      });
    } else if (mode === 'create') {
      // Get organization_id from localStorage/context
      const organizationId = localStorage.getItem('organization_id') || '';
      setFormData({
        name: '',
        description: '',
        status: 'active',
        organizationId,
      });
    }
  }, [initialData, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save project');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop - Design System */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal - Design System */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl">
          {/* Header - Design System */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-200">
            <h2 className="text-2xl font-bold text-neutral-700">
              {mode === 'create' ? 'Create New Project' : 'Edit Project'}
            </h2>
            <button
              onClick={onClose}
              className="text-neutral-500 hover:text-neutral-700 transition-all duration-200 rounded-xl p-2 hover:bg-neutral-100 focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Form - Design System */}
          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
            {error && (
              <div className="bg-[#C13515]/10 border border-[#C13515]/30 text-[#C13515] px-4 py-3 rounded-xl text-sm font-medium">
                {error}
              </div>
            )}

            {/* Project Name - Design System */}
            <div>
              <label htmlFor="name" className="block text-sm font-semibold text-neutral-700 mb-2">
                Project Name <span className="text-[#C13515]">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 focus:outline-none transition-all duration-200 placeholder:text-neutral-400"
                placeholder="e.g., Customer Support Bot"
                required
                maxLength={255}
              />
            </div>

            {/* Description - Design System */}
            <div>
              <label htmlFor="description" className="block text-sm font-semibold text-neutral-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 rounded-xl border border-neutral-300 text-neutral-700 focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 focus:outline-none transition-all duration-200 resize-none placeholder:text-neutral-400"
                placeholder="Describe your project..."
              />
            </div>

            {/* Status - Design System */}
            <div>
              <label htmlFor="status" className="block text-sm font-semibold text-neutral-700 mb-2">
                Status
              </label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                className="w-full h-10 px-3 rounded-xl border border-neutral-300 text-neutral-700 focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/20 focus:outline-none transition-all duration-200"
              >
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            {/* Footer - Design System */}
            <div className="flex items-center gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 h-12 px-4 text-sm font-semibold text-neutral-700 bg-neutral-100 border border-neutral-300 rounded-xl hover:bg-neutral-200 transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !formData.name.trim()}
                className="flex-1 h-12 px-4 text-sm font-semibold text-white bg-[#FF385C] rounded-xl hover:bg-[#E31C5F] transition-all duration-200 disabled:bg-neutral-300 disabled:text-neutral-500 disabled:cursor-not-allowed shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
              >
                {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create Project' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
