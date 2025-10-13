import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Plus,
  FileText,
  Calendar,
  User,
  Play,
  Edit,
  Trash2,
} from 'lucide-react';
import { CreatePromptRequest } from '../../../shared/services/promptService';
import { PromptBuilderModal } from '../components/PromptBuilder/PromptBuilderModal';
import { PromptFormData } from '../types/prompt';
import { Button } from '../../../shared/components/core/Button';
import { Badge } from '../../../shared/components/core/Badge';
import { useProject } from '../../../shared/hooks/useProjects';
import { usePrompts, useCreatePrompt } from '../../../shared/hooks/usePrompts';

export const ProjectDetail: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // UI State - separated from server state
  const [isPromptBuilderOpen, setIsPromptBuilderOpen] = useState(false);

  // Server State - using centralized hooks with REACT-QUERY-001 pattern
  const { data: project, isLoading: projectLoading } = useProject(projectId);
  const { data: prompts = [], isLoading: promptsLoading } = usePrompts({ project_id: projectId });
  const createPromptMutation = useCreatePrompt();

  const handleCreatePrompt = async (formData: PromptFormData) => {
    if (!projectId) {
      throw new Error('No project ID available');
    }

    const createRequest: CreatePromptRequest = {
      name: formData.name,
      description: formData.description,
      category: formData.intent,
      status: 'draft',
      project_id: projectId,
      initial_version: {
        template: formData.userPrompt,
        system_message: formData.systemPrompt,
        variables: formData.variables.reduce((acc, v) => {
          acc[v.name] = {
            type: v.type,
            required: v.required,
            defaultValue: v.defaultValue,
            description: v.description,
          };
          return acc;
        }, {} as Record<string, any>),
        model_config: {
          tone: formData.tone,
        },
        tags: [formData.tone, formData.intent].filter(Boolean),
      },
    };

    await createPromptMutation.mutateAsync(createRequest);
    // Close modal after success (mutation handles cache updates and optimistic updates)
    setIsPromptBuilderOpen(false);
  };

  if (projectLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading project...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">Project not found</div>
      </div>
    );
  }

  const statusColors = {
    active: 'green',
    draft: 'yellow',
    archived: 'gray',
  } as const;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/projects')}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Projects
        </button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-semibold text-neutral-900">{project.name}</h1>
              <Badge variant={statusColors[project.status]}>
                {project.status}
              </Badge>
            </div>
            <p className="text-neutral-600">{project.description || 'No description'}</p>
          </div>

          <button
            onClick={() => setIsPromptBuilderOpen(true)}
            className="flex items-center gap-2 bg-neutral-900 text-white px-5 py-2.5 rounded-lg hover:bg-neutral-800 transition-colors font-medium"
          >
            <Plus className="h-5 w-5" />
            New Prompt
          </button>
        </div>

        {/* Project Metadata */}
        <div className="mt-6 flex items-center gap-6 text-sm text-neutral-600">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span>Created by {project.created_by}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Updated {new Date(project.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      {/* Prompts Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Prompts ({prompts.length})</h2>
        </div>

        {promptsLoading ? (
          <div className="text-center py-8 text-neutral-600">Loading prompts...</div>
        ) : prompts.length === 0 ? (
          <div className="text-center py-16 bg-neutral-50 rounded-2xl">
            <FileText className="h-16 w-16 text-neutral-400 mx-auto mb-4" />
            <p className="text-neutral-600 mb-6 text-lg">No prompts in this project yet</p>
            <button
              onClick={() => setIsPromptBuilderOpen(true)}
              className="inline-flex items-center gap-2 bg-neutral-900 text-white px-6 py-3 rounded-lg hover:bg-neutral-800 transition-colors font-medium"
            >
              <Plus className="h-5 w-5" />
              Create Your First Prompt
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {prompts.map((prompt) => (
              <div
                key={prompt.id}
                className="bg-white border border-neutral-200 rounded-xl p-5 hover:border-neutral-900 hover:shadow-md transition-all cursor-pointer"
                onClick={() => navigate(`/projects/prompt/${prompt.id}`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-lg text-neutral-900">{prompt.name}</h3>
                  <Badge variant={statusColors[prompt.status]}>
                    {prompt.status}
                  </Badge>
                </div>

                <p className="text-sm text-neutral-600 mb-4 line-clamp-2 min-h-[2.5rem]">
                  {prompt.description || 'No description'}
                </p>

                {prompt.category && (
                  <div className="mb-3">
                    <Badge variant="gray">{prompt.category}</Badge>
                  </div>
                )}

                <div className="text-xs text-neutral-500 space-y-1.5 mb-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>Updated {new Date(prompt.updated_at).toLocaleDateString()}</span>
                  </div>
                  {prompt.current_version && (
                    <div className="flex items-center gap-2">
                      <FileText className="h-3.5 w-3.5" />
                      <span>Version {prompt.current_version.version_number}</span>
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-neutral-100 flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/projects/prompt/${prompt.id}`);
                    }}
                    className="flex-1 text-sm text-neutral-900 hover:text-neutral-700 font-medium py-2 px-3 rounded-lg hover:bg-neutral-50 transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Edit className="h-3.5 w-3.5" />
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: Navigate to evaluation page
                      console.log('Run evaluation for', prompt.id);
                    }}
                    className="flex-1 text-sm text-neutral-900 hover:text-neutral-700 font-medium py-2 px-3 rounded-lg hover:bg-neutral-50 transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Play className="h-3.5 w-3.5" />
                    Evaluate
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <PromptBuilderModal
        isOpen={isPromptBuilderOpen}
        onClose={() => setIsPromptBuilderOpen(false)}
        onSubmit={handleCreatePrompt}
        mode="create"
      />
    </div>
  );
};
