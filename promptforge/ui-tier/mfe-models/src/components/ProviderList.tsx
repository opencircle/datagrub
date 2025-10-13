/**
 * Provider List Component
 *
 * Displays configured model providers with their status, masked API keys,
 * and management actions (edit, delete, test connection)
 */
import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Plus,
  Settings,
  Trash2,
  CheckCircle,
  AlertCircle,
  Key,
  TestTube,
  Shield,
} from 'lucide-react';
import clsx from 'clsx';
import {
  ModelProviderConfig,
  ProviderMetadata,
} from '../types/provider';
import {
  listProviderConfigs,
  getProviderCatalog,
  deleteProviderConfig,
  testProviderConfig,
} from '../services/providerService';

interface ProviderListProps {
  onAddProvider: () => void;
  onEditProvider: (config: ModelProviderConfig) => void;
}

export const ProviderList: React.FC<ProviderListProps> = ({
  onAddProvider,
  onEditProvider,
}) => {
  const queryClient = useQueryClient();
  const [testing, setTesting] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  // Fetch provider configs using React Query
  const {
    data: configsData,
    isLoading: isLoadingConfigs,
    error: configsError,
  } = useQuery({
    queryKey: ['provider-configs'],
    queryFn: () => listProviderConfigs({ is_active: true }),
    staleTime: 30000, // 30 seconds
    retry: 2,
  });

  // Fetch provider catalog using React Query
  const {
    data: catalogData,
    isLoading: isLoadingCatalog,
    error: catalogError,
  } = useQuery({
    queryKey: ['provider-catalog'],
    queryFn: getProviderCatalog,
    staleTime: 300000, // 5 minutes (catalog doesn't change often)
    retry: 2,
  });

  const configs = configsData?.configs || [];
  const catalog = catalogData?.providers || [];
  const loading = isLoadingConfigs || isLoadingCatalog;
  const error = configsError || catalogError;

  const handleTestConnection = async (configId: string) => {
    try {
      setTesting(configId);
      const result = await testProviderConfig(configId);

      if (result.success) {
        alert(`✅ Connection successful!\nLatency: ${result.latency_ms}ms`);
      } else {
        alert(`❌ Connection failed:\n${result.message}`);
      }
    } catch (error: any) {
      alert(`❌ Test failed:\n${error.message}`);
    } finally {
      setTesting(null);
    }
  };

  const handleDelete = async (configId: string, displayName: string) => {
    if (!confirm(`Are you sure you want to delete "${displayName}"?`)) {
      return;
    }

    try {
      setDeleting(configId);
      await deleteProviderConfig(configId);
      // Invalidate and refetch provider configs
      await queryClient.invalidateQueries({ queryKey: ['provider-configs'] });
    } catch (error: any) {
      alert(`❌ Delete failed:\n${error.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const getProviderMetadata = (providerName: string): ProviderMetadata | null => {
    return catalog.find((p) => p.provider_name === providerName) || null;
  };

  const filteredConfigs =
    filterType === 'all'
      ? configs
      : configs.filter((c) => c.provider_type === filterType);

  const providerTypes = ['all', ...Array.from(new Set(configs.map((c) => c.provider_type)))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#FF385C]"></div>
      </div>
    );
  }

  if (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-8">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-red-800 mb-2">
              {errorMessage.includes('401') || errorMessage.includes('403') || errorMessage.includes('authenticated')
                ? 'Authentication Required'
                : 'Error Loading Providers'}
            </h3>
            <p className="text-red-700 mb-4">{errorMessage}</p>
            {(errorMessage.includes('401') || errorMessage.includes('403') || errorMessage.includes('authenticated')) && (
              <p className="text-sm text-red-600 mb-4">
                Please log in to view and manage model providers.
              </p>
            )}
            <button
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['provider-configs'] });
                queryClient.invalidateQueries({ queryKey: ['provider-catalog'] });
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-neutral-800">Model Providers</h2>
          <p className="text-neutral-500 mt-2 text-base">
            Manage API keys and configurations for AI model providers
          </p>
        </div>
        <button
          onClick={onAddProvider}
          className="flex items-center gap-2 h-11 bg-[#FF385C] text-white px-4 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
        >
          <Plus className="h-5 w-5" />
          Add Provider
        </button>
      </div>

      {/* Filter Chips */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm font-medium text-neutral-600">Filter by type:</span>
        <div className="flex gap-2">
          {providerTypes.map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                filterType === type
                  ? 'bg-[#FF385C] text-white shadow-sm'
                  : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300'
              )}
            >
              {type === 'all' ? 'All' : type.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Provider Cards */}
      {filteredConfigs.length === 0 ? (
        <div className="bg-white border border-neutral-100 rounded-2xl p-12 text-center">
          <Shield className="h-16 w-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-neutral-800 mb-2">
            No providers configured
          </h3>
          <p className="text-neutral-500 mb-6">
            Add your first AI model provider to get started
          </p>
          <button
            onClick={onAddProvider}
            className="inline-flex items-center gap-2 h-11 bg-[#FF385C] text-white px-4 rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold shadow-sm"
          >
            <Plus className="h-5 w-5" />
            Add Provider
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredConfigs.map((config, index) => {
            const metadata = getProviderMetadata(config.provider_name);

            return (
              <motion.div
                key={config.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white border border-neutral-100 rounded-2xl p-6 hover:shadow-lg transition-all duration-200"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {metadata?.icon_url ? (
                        <>
                          <img
                            src={metadata.icon_url}
                            alt={`${metadata.display_name} logo`}
                            className="h-8 w-8 object-contain"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                              if (fallback) fallback.classList.remove('hidden');
                            }}
                          />
                          <div className="h-8 w-8 rounded-lg bg-neutral-100 flex items-center justify-center hidden">
                            <span className="text-xs font-semibold text-neutral-600">
                              {metadata.display_name.substring(0, 2).toUpperCase()}
                            </span>
                          </div>
                        </>
                      ) : (
                        <div className="h-8 w-8 rounded-lg bg-neutral-100 flex items-center justify-center">
                          <span className="text-xs font-semibold text-neutral-600">
                            {config.provider_name.substring(0, 2).toUpperCase()}
                          </span>
                        </div>
                      )}
                      <div>
                        <h3 className="text-lg font-bold text-neutral-800">
                          {config.display_name}
                        </h3>
                        <p className="text-sm text-neutral-500">
                          {metadata?.display_name || config.provider_name}
                        </p>
                      </div>
                    </div>

                    {/* Provider Type Badge */}
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {config.provider_type}
                    </span>

                    {/* Default Badge */}
                    {config.is_default && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 ml-2">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Default
                      </span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onEditProvider(config)}
                      className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                      title="Edit configuration"
                      aria-label={`Edit ${config.display_name} configuration`}
                    >
                      <Settings className="h-5 w-5 text-neutral-600" />
                    </button>
                    <button
                      onClick={() => handleDelete(config.id, config.display_name)}
                      disabled={deleting === config.id}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      title="Delete configuration"
                      aria-label={`Delete ${config.display_name} configuration`}
                    >
                      <Trash2 className="h-5 w-5 text-red-500" />
                    </button>
                  </div>
                </div>

                {/* API Key (masked) */}
                <div className="bg-neutral-50 rounded-xl p-3 mb-4">
                  <div className="flex items-center gap-2">
                    <Key className="h-4 w-4 text-neutral-400" />
                    <span className="text-sm font-mono text-neutral-600">
                      {config.api_key_masked}
                    </span>
                  </div>
                </div>

                {/* Status & Info */}
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <p className="text-neutral-500 mb-1">Status</p>
                    <div className="flex items-center gap-1">
                      {config.is_active ? (
                        <>
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="font-medium text-neutral-800">Active</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="h-4 w-4 text-neutral-600" />
                          <span className="font-medium text-neutral-800">Inactive</span>
                        </>
                      )}
                    </div>
                  </div>

                  {config.project_id && (
                    <div>
                      <p className="text-neutral-500 mb-1">Scope</p>
                      <span className="font-medium text-neutral-800">Project-level</span>
                    </div>
                  )}
                </div>

                {/* Test Connection Button */}
                <button
                  onClick={() => handleTestConnection(config.id)}
                  disabled={testing === config.id}
                  className="w-full flex items-center justify-center gap-2 h-11 bg-white border border-neutral-200 text-neutral-700 rounded-xl hover:bg-neutral-50 transition-all duration-200 font-medium disabled:opacity-50"
                >
                  <TestTube className="h-4 w-4" />
                  {testing === config.id ? 'Testing...' : 'Test Connection'}
                </button>

                {/* Timestamps */}
                <div className="mt-4 pt-4 border-t border-neutral-50 text-xs text-neutral-500">
                  <p>
                    Created: {new Date(config.created_at).toLocaleDateString()}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};
