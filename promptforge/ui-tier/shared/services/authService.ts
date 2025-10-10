/**
 * Authentication Service
 */

import { apiClient } from './apiClient';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'developer' | 'viewer';
  is_active: boolean;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials);

    // Store tokens
    apiClient.setAccessToken(response.access_token);
    apiClient.setRefreshToken(response.refresh_token);

    return response;
  },

  /**
   * Logout - clear tokens
   */
  logout(): void {
    apiClient.clearTokens();
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/users/me');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!apiClient.getAccessToken();
  },

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = apiClient.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    // Store new tokens
    apiClient.setAccessToken(response.access_token);
    apiClient.setRefreshToken(response.refresh_token);

    return response;
  },
};

export default authService;
