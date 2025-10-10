/**
 * Model Provider TypeScript Types
 *
 * Based on API schemas from api-tier/app/schemas/model_provider.py
 */

export interface ProviderMetadataField {
  name: string;
  type: 'string' | 'password' | 'url' | 'select' | 'number' | 'boolean';
  label: string;
  placeholder?: string;
  help_text?: string;
  required: boolean;
  validation?: {
    pattern?: string;
    min_length?: number;
    max_length?: number;
    min?: number;
    max?: number;
  };
  options?: string[];
  default?: any;
}

export interface ProviderMetadata {
  provider_name: string;
  provider_type: 'llm' | 'embeddings' | 'vision' | 'audio' | 'hybrid';
  display_name: string;
  description: string;
  icon_url?: string;
  documentation_url?: string;
  required_fields: ProviderMetadataField[];
  optional_fields: ProviderMetadataField[];
  capabilities: string[];
  supported_models: Array<{
    model_id: string;
    model_name: string;
    context_window?: number;
    supports_functions?: boolean;
  }>;
  is_active: boolean;
}

export interface ProviderMetadataListResponse {
  providers: ProviderMetadata[];
  total: number;
}

export interface ModelProviderConfig {
  id: string;
  organization_id: string;
  project_id?: string;
  provider_name: string;
  provider_type: string;
  display_name: string;
  api_key_masked: string;
  config?: Record<string, any>;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface ModelProviderConfigListResponse {
  configs: ModelProviderConfig[];
  total: number;
}

export interface ModelProviderConfigCreate {
  provider_name: string;
  provider_type: string;
  display_name: string;
  api_key: string;
  project_id?: string;
  config?: Record<string, any>;
  is_default?: boolean;
}

export interface ModelProviderConfigUpdate {
  display_name?: string;
  api_key?: string;
  config?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface ProviderTestResponse {
  success: boolean;
  message: string;
  latency_ms?: number;
  models_available?: string[];
  error?: string;
}

// UI-specific types

export interface ProviderFormData {
  provider_name: string;
  provider_type: string;
  display_name: string;
  project_id?: string;
  is_default: boolean;
  api_key: string;
  // Dynamic fields based on provider metadata
  [key: string]: any;
}

export interface ProviderFilters {
  provider_type?: string;
  is_active?: boolean;
  project_id?: string;
}
