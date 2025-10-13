import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Edit,
  Play,
  Clock,
  User,
  GitBranch,
  Tag,
} from 'lucide-react';
import { UpdatePromptRequest, CreatePromptVersionRequest } from '../../../shared/services/promptService';
import { PromptBuilderModal } from '../components/PromptBuilder/PromptBuilderModal';
import { PromptFormData } from '../types/prompt';
import { Button } from '../../../shared/components/core/Button';
import { Badge } from '../../../shared/components/core/Badge';
import {
  usePrompt,
  usePromptVersions,
  useUpdatePrompt,
  useCreatePromptVersion,
} from '../../../shared/hooks/usePrompts';

export const PromptDetail: React.FC = () => {
  const { promptId } = useParams<{ promptId: string }>();
  const navigate = useNavigate();

  // UI State - separated from server state
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'details' | 'versions'>('details');

  // Server State - using centralized hooks with REACT-QUERY-001 pattern
  const { data: prompt, isLoading: promptLoading } = usePrompt(promptId);
  const { data: versions = [], isLoading: versionsLoading } = usePromptVersions(
    selectedTab === 'versions' ? promptId : undefined
  );
  const updatePromptMutation = useUpdatePrompt();
  const createVersionMutation = useCreatePromptVersion();

  // Calculate invocation metrics from current version
  const invocationMetrics = prompt?.current_version
    ? {
        totalInvocations: prompt.current_version.usage_count || 0,
        avgLatency: prompt.current_version.avg_latency_ms || 0,
        avgCost: prompt.current_version.avg_cost || 0,
      }
    : null;

  const handleUpdatePrompt = async (formData: PromptFormData) => {
    if (!promptId || !prompt) {
      throw new Error('No prompt ID available');
    }

    // Create a new version with the updated data
    const versionData: CreatePromptVersionRequest = {
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
    };

    await createVersionMutation.mutateAsync({ promptId, data: versionData });

    // Also update the prompt metadata
    const updateData: UpdatePromptRequest = {
      name: formData.name,
      description: formData.description,
      category: formData.intent,
    };

    await updatePromptMutation.mutateAsync({ id: promptId, data: updateData });

    // Close modal after success (mutations handle cache updates and optimistic updates)
    setIsEditMode(false);
  };

  const handleStatusChange = async (status: 'draft' | 'active' | 'archived') => {
    if (!promptId) return;

    await updatePromptMutation.mutateAsync({
      id: promptId,
      data: { status },
    });
  };

  if (promptLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-600">Loading prompt...</div>
      </div>
    );
  }

  if (!prompt) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">Prompt not found</div>
      </div>
    );
  }

  const currentVersion = prompt.current_version;

  // Convert prompt to form data for editing
  const promptToFormData = (): Partial<PromptFormData> => {
    if (!currentVersion) return {};

    const variables = currentVersion.variables
      ? Object.entries(currentVersion.variables).map(([name, config]: [string, any]) => ({
          name,
          type: config.type || 'string',
          required: config.required || false,
          defaultValue: config.defaultValue,
          description: config.description,
        }))
      : [];

    return {
      name: prompt.name,
      description: prompt.description || '',
      systemPrompt: currentVersion.system_message || '',
      userPrompt: currentVersion.template,
      intent: prompt.category || '',
      tone: currentVersion.model_config?.tone || 'professional',
      variables,
      fewShotExamples: [],
    };
  };

  const statusColors = {
    active: 'green',
    draft: 'yellow',
    archived: 'gray',
  } as const;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate(`/projects/${prompt.project_id}`)}
          className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Project
        </button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{prompt.name}</h1>
              <Badge variant={statusColors[prompt.status]}>
                {prompt.status}
              </Badge>
            </div>
            <p className="text-neutral-600">{prompt.description || 'No description'}</p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={() => setIsEditMode(true)}
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                // TODO: Navigate to evaluation wizard
                console.log('Run evaluation');
              }}
            >
              <Play className="h-4 w-4 mr-2" />
              Run Evaluation
            </Button>
          </div>
        </div>

        {/* Metadata */}
        <div className="mt-6 flex items-center gap-6 text-sm text-neutral-600">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span>Created by {prompt.created_by}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>Updated {new Date(prompt.updated_at).toLocaleDateString()}</span>
          </div>
          {currentVersion && (
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4" />
              <span>Version {currentVersion.version_number}</span>
            </div>
          )}
        </div>

        {/* Status Selector */}
        <div className="mt-4 flex items-center gap-2">
          <span className="text-sm text-neutral-600">Status:</span>
          <select
            value={prompt.status}
            onChange={(e) => handleStatusChange(e.target.value as any)}
            className="text-sm border border-neutral-300 rounded px-2 py-1"
          >
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        {/* Invocation Metrics */}
        {invocationMetrics && invocationMetrics.totalInvocations > 0 && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-neutral-50 rounded-lg p-4">
              <div className="text-sm text-neutral-600 mb-1">Total Invocations</div>
              <div className="text-2xl font-semibold text-neutral-900">
                {invocationMetrics.totalInvocations.toLocaleString()}
              </div>
            </div>
            <div className="bg-neutral-50 rounded-lg p-4">
              <div className="text-sm text-neutral-600 mb-1">Avg Latency</div>
              <div className="text-2xl font-semibold text-neutral-900">
                {invocationMetrics.avgLatency.toFixed(0)}ms
              </div>
            </div>
            <div className="bg-neutral-50 rounded-lg p-4">
              <div className="text-sm text-neutral-600 mb-1">Avg Cost</div>
              <div className="text-2xl font-semibold text-neutral-900">
                ${invocationMetrics.avgCost.toFixed(4)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs - Design System: Improved spacing and sizing */}
      <div className="border-b border-neutral-200">
        <nav className="flex gap-3">
          <button
            onClick={() => setSelectedTab('details')}
            className={`h-11 px-4 py-2.5 border-b-2 font-semibold text-sm transition-all duration-200 ${
              selectedTab === 'details'
                ? 'border-[#FF385C] text-[#FF385C]'
                : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
            }`}
          >
            Details
          </button>
          <button
            onClick={() => setSelectedTab('versions')}
            className={`h-11 px-4 py-2.5 border-b-2 font-semibold text-sm transition-all duration-200 ${
              selectedTab === 'versions'
                ? 'border-[#FF385C] text-[#FF385C]'
                : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
            }`}
          >
            Version History ({versions.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {selectedTab === 'details' && currentVersion && (
        <div className="space-y-6">
          {/* System Prompt */}
          {currentVersion.system_message && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">System Prompt</h3>
              <pre className="bg-neutral-50 p-4 rounded text-sm whitespace-pre-wrap font-mono">
                {currentVersion.system_message}
              </pre>
            </div>
          )}

          {/* User Prompt Template */}
          <div className="bg-white border border-neutral-200 rounded-lg p-6">
            <h3 className="font-semibold text-lg mb-3">User Prompt Template</h3>
            <pre className="bg-neutral-50 p-4 rounded text-sm whitespace-pre-wrap font-mono">
              {currentVersion.template}
            </pre>
          </div>

          {/* Variables */}
          {currentVersion.variables && Object.keys(currentVersion.variables).length > 0 && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Variables</h3>
              <div className="space-y-3">
                {Object.entries(currentVersion.variables).map(([name, config]: [string, any]) => (
                  <div key={name} className="bg-neutral-50 p-4 rounded">
                    <div className="flex items-start justify-between">
                      <div>
                        <code className="text-sm font-mono text-blue-600">{name}</code>
                        {config.description && (
                          <p className="text-sm text-neutral-600 mt-1">{config.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="gray">{config.type}</Badge>
                        {config.required && <Badge variant="blue">Required</Badge>}
                      </div>
                    </div>
                    {config.defaultValue && (
                      <div className="mt-2 text-sm text-neutral-600">
                        Default: <code className="bg-white px-2 py-1 rounded">{config.defaultValue}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {currentVersion.tags && currentVersion.tags.length > 0 && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {currentVersion.tags.map((tag) => (
                  <Badge key={tag} variant="blue">
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Model Config */}
          {currentVersion.model_config && Object.keys(currentVersion.model_config).length > 0 && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-3">Model Configuration</h3>
              <pre className="bg-neutral-50 p-4 rounded text-sm">
                {JSON.stringify(currentVersion.model_config, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'versions' && (
        <div className="space-y-4">
          {versionsLoading ? (
            <div className="text-center py-8 text-neutral-600">Loading versions...</div>
          ) : versions.length === 0 ? (
            <div className="text-center py-8 text-neutral-600">No versions found</div>
          ) : (
            versions.map((version) => (
              <div
                key={version.id}
                className="bg-white border border-neutral-200 rounded-lg p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">Version {version.version_number}</h3>
                    <p className="text-sm text-neutral-600">
                      Created {new Date(version.created_at).toLocaleString()}
                    </p>
                  </div>
                  {version.id === prompt.current_version_id && (
                    <Badge variant="green">Current</Badge>
                  )}
                </div>

                {version.tags && version.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {version.tags.map((tag) => (
                      <Badge key={tag} variant="gray">{tag}</Badge>
                    ))}
                  </div>
                )}

                <div className="space-y-3">
                  {version.system_message && (
                    <div>
                      <h4 className="text-sm font-medium text-neutral-700 mb-1">System Message</h4>
                      <pre className="bg-neutral-50 p-3 rounded text-xs whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">
                        {version.system_message}
                      </pre>
                    </div>
                  )}
                  <div>
                    <h4 className="text-sm font-medium text-neutral-700 mb-1">Template</h4>
                    <pre className="bg-neutral-50 p-3 rounded text-xs whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">
                      {version.template}
                    </pre>
                  </div>
                </div>

                {version.usage_count > 0 && (
                  <div className="mt-4 pt-4 border-t border-neutral-200 text-sm text-neutral-600">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <span className="font-medium">Usage:</span> {version.usage_count}
                      </div>
                      {version.avg_latency_ms && (
                        <div>
                          <span className="font-medium">Avg Latency:</span> {version.avg_latency_ms}ms
                        </div>
                      )}
                      {version.avg_cost && (
                        <div>
                          <span className="font-medium">Avg Cost:</span> ${version.avg_cost.toFixed(4)}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      <PromptBuilderModal
        isOpen={isEditMode}
        onClose={() => setIsEditMode(false)}
        onSubmit={handleUpdatePrompt}
        initialData={promptToFormData()}
        mode="edit"
      />
    </div>
  );
};
