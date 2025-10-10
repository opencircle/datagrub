import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderKanban, Search, Plus, Edit2, Trash2, FileText, Loader } from 'lucide-react';
import { motion } from 'framer-motion';
import { Project } from '../../../shared/services/projectService';
import { CreatePromptRequest } from '../../../shared/services/promptService';
import { PromptBuilderModal } from '../components/PromptBuilder/PromptBuilderModal';
import { PromptFormData } from '../types/prompt';
import { ProjectModal, ProjectFormData } from '../components/ProjectModal';
import { useProjects, useCreateProject, useUpdateProject, useDeleteProject } from '../../../shared/hooks/useProjects';
import { useCreatePrompt } from '../../../shared/hooks/usePrompts';

// Design System: Status badges with semantic colors
const StatusBadge: React.FC<{ status: Project['status'] }> = ({ status }) => {
  const styles = {
    active: 'bg-[#00A699]/10 text-[#008489]',
    draft: 'bg-[#FFB400]/10 text-[#E6A200]',
    archived: 'bg-neutral-100 text-neutral-700',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
};

export const ProjectList: React.FC = () => {
  const navigate = useNavigate();

  // UI State - separated from server state
  const [searchTerm, setSearchTerm] = useState('');
  const [isPromptBuilderOpen, setIsPromptBuilderOpen] = useState(false);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [projectModalMode, setProjectModalMode] = useState<'create' | 'edit'>('create');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Server State - using centralized hooks with REACT-QUERY-001 pattern
  const { data: projects = [], isLoading, error } = useProjects();
  const createProjectMutation = useCreateProject();
  const updateProjectMutation = useUpdateProject();
  const deleteProjectMutation = useDeleteProject();
  const createPromptMutation = useCreatePrompt();

  const handleCreatePrompt = async (formData: PromptFormData) => {
    if (!selectedProjectId) {
      throw new Error('No project selected');
    }

    const createRequest: CreatePromptRequest = {
      name: formData.name,
      description: formData.description,
      category: formData.intent,
      status: 'draft',
      project_id: selectedProjectId,
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
    // Close modal after success (mutation handles cache updates)
    setIsPromptBuilderOpen(false);
    setSelectedProjectId(null);
  };

  const openPromptBuilder = (projectId: string) => {
    setSelectedProjectId(projectId);
    setIsPromptBuilderOpen(true);
  };

  const handleProjectSubmit = async (formData: ProjectFormData) => {
    if (projectModalMode === 'create') {
      await createProjectMutation.mutateAsync({
        name: formData.name,
        description: formData.description,
        status: formData.status,
        organization_id: formData.organizationId,
      });
    } else if (selectedProject) {
      await updateProjectMutation.mutateAsync({
        id: selectedProject.id,
        data: {
          name: formData.name,
          description: formData.description,
          status: formData.status,
        },
      });
    }
    // Close modal after success (mutation handles cache updates and optimistic updates)
    setIsProjectModalOpen(false);
    setSelectedProject(null);
  };

  const handleEditProject = (project: Project) => {
    setSelectedProject(project);
    setProjectModalMode('edit');
    setIsProjectModalOpen(true);
  };

  const handleDeleteProject = async (projectId: string) => {
    if (confirm('Are you sure you want to delete this project? All prompts and data will be permanently removed.')) {
      await deleteProjectMutation.mutateAsync(projectId);
    }
  };

  const filteredProjects = projects.filter(
    (project) =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (project.description?.toLowerCase() || '').includes(searchTerm.toLowerCase())
  );

  // Loading State - Design System
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="h-8 w-8 text-[#FF385C] animate-spin" />
        <span className="ml-3 text-neutral-600 font-medium">Loading projects...</span>
      </div>
    );
  }

  // Error State - Design System
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-[#C13515]/5 rounded-2xl mx-6">
        <div className="text-[#C13515] font-semibold mb-2">Error loading projects</div>
        <div className="text-neutral-600 text-sm">{(error as Error).message}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Header - Design System: Increased spacing, clearer hierarchy */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-800">Projects</h1>
          <p className="text-neutral-500 mt-2 text-base">Manage your AI prompt projects</p>
        </div>
        <button
          className="flex items-center gap-2 h-11 bg-[#FF385C] text-white px-5 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
          onClick={() => {
            setProjectModalMode('create');
            setSelectedProject(null);
            setIsProjectModalOpen(true);
          }}
        >
          <Plus className="h-5 w-5" />
          New Project
        </button>
      </div>

      {/* Search Bar - Enhanced Prominence - Design System: Softer borders, more subtle */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 h-5 w-5" />
        <input
          type="text"
          placeholder="Search projects by name or description..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full h-12 pl-14 pr-4 border border-neutral-200 rounded-xl text-neutral-700 text-base bg-white focus:outline-none focus:border-[#FF385C] focus:ring-4 focus:ring-[#FF385C]/10 transition-all duration-200 placeholder:text-neutral-400"
        />
      </div>

      {/* Projects Grid - Design System: Increased gap, softer cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="bg-white rounded-2xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group relative border border-neutral-100"
            onClick={() => navigate(`/projects/${project.id}`)}
          >
            {/* Direct Action Icons - Design System (replaces three-dot menu) */}
            <div className="absolute top-4 right-4 z-10 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditProject(project);
                }}
                className="p-2 rounded-lg hover:bg-neutral-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
                aria-label="Edit project"
                title="Edit project"
              >
                <Edit2 className="h-4 w-4 text-neutral-600" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteProject(project.id);
                }}
                className="p-2 rounded-lg hover:bg-[#C13515]/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#C13515]/20"
                aria-label="Delete project"
                title="Delete project"
              >
                <Trash2 className="h-4 w-4 text-[#C13515]" />
              </button>
            </div>

            {/* Card Interior - Design System: More generous spacing */}
            <div className="flex items-start justify-between mb-4">
              <div className="bg-neutral-50 p-3 rounded-xl">
                <FolderKanban className="h-6 w-6 text-neutral-600" />
              </div>
              <StatusBadge status={project.status} />
            </div>

            <h3 className="text-lg font-bold text-neutral-800 mb-2 leading-snug">{project.name}</h3>
            <p className="text-sm text-neutral-500 mb-4 line-clamp-2 min-h-[2.5rem] leading-relaxed">
              {project.description || 'No description'}
            </p>

            {/* View prompts indicator */}
            <div className="text-sm text-neutral-400 mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>View prompts</span>
              </div>
            </div>

            {/* Create Prompt Button - Design System: Softer separator */}
            <div className="pt-4 border-t border-neutral-50">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  openPromptBuilder(project.id);
                }}
                className="w-full h-10 text-sm text-[#FF385C] hover:text-[#E31C5F] hover:bg-[#FF385C]/5 font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
              >
                Create Prompt
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State - Design System: More spacious, warmer feel */}
      {filteredProjects.length === 0 && (
        <div className="text-center py-20 bg-white rounded-2xl border border-neutral-100">
          <FolderKanban className="h-16 w-16 text-neutral-300 mx-auto mb-5" />
          <p className="text-neutral-700 font-semibold mb-2 text-lg">No projects found</p>
          <p className="text-sm text-neutral-400">Try adjusting your search or create a new project</p>
        </div>
      )}

      <PromptBuilderModal
        isOpen={isPromptBuilderOpen}
        onClose={() => {
          setIsPromptBuilderOpen(false);
          setSelectedProjectId(null);
        }}
        onSubmit={handleCreatePrompt}
        mode="create"
      />

      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setSelectedProject(null);
        }}
        onSubmit={handleProjectSubmit}
        mode={projectModalMode}
        initialData={selectedProject || undefined}
      />
    </div>
  );
};
