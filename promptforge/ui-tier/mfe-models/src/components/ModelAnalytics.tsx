import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import {
  Cpu, Activity, DollarSign, TrendingUp, Clock,
  CheckCircle, XCircle, AlertCircle
} from 'lucide-react';

// API Types
interface ModelUsageStats {
  model_name: string;
  provider_name: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate: number;
  avg_latency_ms: number | null;
  total_tokens: number;
  total_cost: number;
  last_used: string | null;
}

interface ModelAnalytics {
  total_models_available: number;
  total_requests_7d: number;
  total_cost_7d: number;
  avg_success_rate: number;
  most_used_model: string | null;
  top_models: ModelUsageStats[];
}

interface ModelsAnalyticsResponse {
  analytics: ModelAnalytics;
  by_model: ModelUsageStats[];
  total: number;
}

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  subtitle?: string;
  iconBg?: string;
  iconColor?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon: Icon,
  label,
  value,
  subtitle,
  iconBg = 'bg-neutral-50',
  iconColor = 'text-neutral-600'
}) => (
  <div className="bg-white border border-neutral-100 rounded-2xl p-6 hover:shadow-md transition-all">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-neutral-500">{label}</p>
        <p className="text-2xl font-bold mt-2 text-neutral-800">{value}</p>
        {subtitle && <p className="text-xs text-neutral-400 mt-1">{subtitle}</p>}
      </div>
      <div className={`${iconBg} p-3 rounded-xl`}>
        <Icon className={`h-6 w-6 ${iconColor}`} />
      </div>
    </div>
  </div>
);

const ModelRow: React.FC<{ model: ModelUsageStats; index: number }> = ({ model, index }) => {
  const successRateColor =
    model.success_rate >= 95 ? 'text-green-600' :
    model.success_rate >= 80 ? 'text-yellow-600' :
    'text-red-600';

  return (
    <motion.tr
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="border-b border-neutral-100 hover:bg-neutral-50 transition-colors"
    >
      <td className="px-6 py-4">
        <div>
          <p className="font-medium text-neutral-800">{model.model_name}</p>
          <p className="text-xs text-neutral-500 mt-1">{model.provider_name}</p>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          <Activity className="h-4 w-4 text-neutral-400" />
          <span className="font-medium text-neutral-800">
            {model.total_requests.toLocaleString()}
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          <CheckCircle className="h-4 w-4 text-green-500" />
          <span className={`font-medium ${successRateColor}`}>
            {model.success_rate.toFixed(1)}%
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          <Clock className="h-4 w-4 text-neutral-400" />
          <span className="font-medium text-neutral-800">
            {model.avg_latency_ms ? `${model.avg_latency_ms.toFixed(0)}ms` : 'N/A'}
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <span className="font-medium text-neutral-800">
          {model.total_tokens.toLocaleString()}
        </span>
      </td>
      <td className="px-6 py-4 text-right">
        <div className="flex items-center justify-end gap-2">
          <DollarSign className="h-4 w-4 text-neutral-400" />
          <span className="font-medium text-neutral-800">
            ${model.total_cost.toFixed(2)}
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-right text-sm text-neutral-500">
        {model.last_used ? new Date(model.last_used).toLocaleDateString() : 'Never'}
      </td>
    </motion.tr>
  );
};

// Fetch function for analytics
const fetchAnalytics = async (days: number): Promise<ModelsAnalyticsResponse> => {
  const token = localStorage.getItem('promptforge_access_token');
  if (!token) {
    throw new Error('No access token found');
  }

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  const response = await fetch(
    `${API_BASE_URL}/api/v1/models/analytics?days=${days}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication failed. Please log in again.');
    }
    throw new Error(`Failed to fetch analytics: ${response.statusText}`);
  }

  return response.json();
};

export const ModelAnalytics: React.FC = () => {
  const [days, setDays] = useState(7);

  // Fetch analytics using React Query
  const {
    data: analytics,
    isLoading: loading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['model-analytics', days],
    queryFn: () => fetchAnalytics(days),
    staleTime: 60000, // 1 minute
    retry: 2,
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#FF385C] mx-auto mb-4"></div>
          <p className="text-neutral-500">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Analytics</h3>
        <p className="text-red-600 mb-4">{errorMessage}</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  const { analytics: stats, by_model } = analytics;

  return (
    <div className="space-y-8">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-neutral-800">Model Analytics</h2>
          <p className="text-neutral-500 mt-1">Performance and usage metrics across all models</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-neutral-600">Time range:</span>
          {[7, 14, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                days === d
                  ? 'bg-[#FF385C] text-white shadow-sm'
                  : 'bg-white text-neutral-600 border border-neutral-200 hover:border-neutral-300'
              )}
            >
              {d} days
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          icon={Cpu}
          label="Available Models"
          value={stats.total_models_available}
        />
        <StatCard
          icon={Activity}
          label="Total Requests"
          value={stats.total_requests_7d.toLocaleString()}
          subtitle={`Last ${days} days`}
        />
        <StatCard
          icon={DollarSign}
          label="Total Cost"
          value={`$${stats.total_cost_7d.toFixed(2)}`}
          subtitle={`Last ${days} days`}
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Success Rate"
          value={`${stats.avg_success_rate.toFixed(1)}%`}
          subtitle={stats.most_used_model ? `Most used: ${stats.most_used_model}` : undefined}
        />
      </div>

      {/* Models Table */}
      {by_model.length > 0 ? (
        <div className="bg-white border border-neutral-100 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-neutral-100">
            <h3 className="text-lg font-semibold text-neutral-800">Model Usage Breakdown</h3>
            <p className="text-sm text-neutral-500 mt-1">
              Detailed performance metrics for each model
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50">
                <tr className="text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  <th className="px-6 py-3">Model</th>
                  <th className="px-6 py-3 text-right">Requests</th>
                  <th className="px-6 py-3 text-right">Success Rate</th>
                  <th className="px-6 py-3 text-right">Avg Latency</th>
                  <th className="px-6 py-3 text-right">Total Tokens</th>
                  <th className="px-6 py-3 text-right">Total Cost</th>
                  <th className="px-6 py-3 text-right">Last Used</th>
                </tr>
              </thead>
              <tbody>
                {by_model.map((model, index) => (
                  <ModelRow key={`${model.model_name}-${model.provider_name}`} model={model} index={index} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-neutral-50 border border-neutral-100 rounded-2xl p-12 text-center">
          <Activity className="h-16 w-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-neutral-600 mb-2">No Usage Data</h3>
          <p className="text-neutral-500">
            No model usage has been recorded in the last {days} days.
          </p>
        </div>
      )}
    </div>
  );
};
