/**
 * Policy Service
 */

import { apiClient } from './apiClient';

export type PolicySeverity = 'low' | 'medium' | 'high' | 'critical';
export type PolicyAction = 'log' | 'warn' | 'block' | 'alert';

export interface PolicyViolation {
  id: string;
  policy_id: string;
  trace_id: string | null;
  violation_type: string;
  severity: PolicySeverity;
  detected_value: Record<string, any> | null;
  threshold_value: Record<string, any> | null;
  confidence_score: number | null;
  message: string | null;
  violation_metadata: Record<string, any> | null;
  status: string;
  resolution_notes: string | null;
  resolved_at: string | null;
  resolved_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: string;
  name: string;
  description: string | null;
  policy_type: string;
  rules: Record<string, any>;
  threshold: Record<string, any> | null;
  severity: PolicySeverity;
  action: PolicyAction;
  is_active: boolean;
  is_enforced: boolean;
  project_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreatePolicyRequest {
  name: string;
  description?: string;
  policy_type: string;
  rules: Record<string, any>;
  threshold?: Record<string, any>;
  severity?: PolicySeverity;
  action?: PolicyAction;
  is_active?: boolean;
  is_enforced?: boolean;
  project_id: string;
}

export interface UpdatePolicyRequest {
  name?: string;
  description?: string;
  rules?: Record<string, any>;
  threshold?: Record<string, any>;
  severity?: PolicySeverity;
  action?: PolicyAction;
  is_active?: boolean;
  is_enforced?: boolean;
}

export const policyService = {
  /**
   * Get all policies
   */
  async getPolicies(params?: {
    project_id?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<Policy[]> {
    return apiClient.get<Policy[]>('/policies', { params });
  },

  /**
   * Get policy by ID
   */
  async getPolicy(id: string): Promise<Policy> {
    return apiClient.get<Policy>(`/policies/${id}`);
  },

  /**
   * Create new policy
   */
  async createPolicy(data: CreatePolicyRequest): Promise<Policy> {
    return apiClient.post<Policy>('/policies', data);
  },

  /**
   * Update policy
   */
  async updatePolicy(id: string, data: UpdatePolicyRequest): Promise<Policy> {
    return apiClient.patch<Policy>(`/policies/${id}`, data);
  },

  /**
   * Delete policy
   */
  async deletePolicy(id: string): Promise<void> {
    return apiClient.delete<void>(`/policies/${id}`);
  },

  /**
   * Get policy violations
   */
  async getPolicyViolations(
    policyId: string,
    params?: {
      status_filter?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<PolicyViolation[]> {
    return apiClient.get<PolicyViolation[]>(`/policies/${policyId}/violations`, { params });
  },
};

export default policyService;
