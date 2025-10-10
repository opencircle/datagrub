/**
 * Project Service
 */

import { apiClient } from './apiClient';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: 'active' | 'archived' | 'draft';
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  status?: 'active' | 'archived' | 'draft';
  organization_id: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'archived' | 'draft';
}

export const projectService = {
  /**
   * Get all projects
   */
  async getProjects(params?: {
    skip?: number;
    limit?: number;
    status_filter?: string;
  }): Promise<Project[]> {
    return apiClient.get<Project[]>('/projects', { params });
  },

  /**
   * Get project by ID
   */
  async getProject(id: string): Promise<Project> {
    return apiClient.get<Project>(`/projects/${id}`);
  },

  /**
   * Create new project
   */
  async createProject(data: CreateProjectRequest): Promise<Project> {
    return apiClient.post<Project>('/projects', data);
  },

  /**
   * Update project
   */
  async updateProject(id: string, data: UpdateProjectRequest): Promise<Project> {
    return apiClient.patch<Project>(`/projects/${id}`, data);
  },

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    return apiClient.delete<void>(`/projects/${id}`);
  },
};

export default projectService;
