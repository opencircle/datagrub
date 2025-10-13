import React, { useState } from 'react';
import { mockPolicies, mockViolations, PolicyRule, PolicyViolation } from './mockData';
import { Shield, AlertTriangle, CheckCircle, XCircle, Plus, Settings, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const SeverityBadge: React.FC<{ severity: PolicyRule['severity'] }> = ({ severity }) => {
  const config = {
    critical: { bg: 'bg-red-100', text: 'text-red-800' },
    high: { bg: 'bg-orange-100', text: 'text-orange-800' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
    low: { bg: 'bg-blue-100', text: 'text-blue-800' },
  };

  const { bg, text } = config[severity];

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${bg} ${text}`}>
      {severity}
    </span>
  );
};

const CategoryBadge: React.FC<{ category: PolicyRule['category'] }> = ({ category }) => {
  const config = {
    security: { bg: 'bg-purple-100', text: 'text-purple-800', icon: Shield },
    compliance: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
    cost: { bg: 'bg-blue-100', text: 'text-blue-800', icon: Activity },
    quality: { bg: 'bg-neutral-100', text: 'text-neutral-800', icon: Settings },
  };

  const { bg, text, icon: Icon } = config[category];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${bg} ${text}`}>
      <Icon className="h-3 w-3" />
      {category}
    </span>
  );
};

const App: React.FC = () => {
  const [policies] = useState<PolicyRule[]>(mockPolicies);
  const [violations] = useState<PolicyViolation[]>(mockViolations);
  const [activeTab, setActiveTab] = useState<'policies' | 'violations'>('policies');

  const enabledPolicies = policies.filter(p => p.enabled).length;
  const criticalViolations = violations.filter(v => v.severity === 'critical' && !v.resolved).length;
  const unresolvedViolations = violations.filter(v => !v.resolved).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Policy & Governance</h1>
          <p className="text-neutral-600 mt-1">Define and enforce AI governance rules</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          Create Policy
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-neutral-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-neutral-600">Total Policies</p>
              <p className="text-2xl font-bold mt-1">{policies.length}</p>
            </div>
            <Shield className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white border border-neutral-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-neutral-600">Active Policies</p>
              <p className="text-2xl font-bold mt-1 text-green-600">{enabledPolicies}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white border border-neutral-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-neutral-600">Critical Violations</p>
              <p className="text-2xl font-bold mt-1 text-red-600">{criticalViolations}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>
        <div className="bg-white border border-neutral-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-neutral-600">Unresolved</p>
              <p className="text-2xl font-bold mt-1 text-orange-600">{unresolvedViolations}</p>
            </div>
            <XCircle className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      <div className="bg-white border border-neutral-200 rounded-lg overflow-hidden">
        <div className="border-b border-neutral-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('policies')}
              className={clsx(
                'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'policies'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-neutral-600 hover:text-neutral-900'
              )}
            >
              Policies ({policies.length})
            </button>
            <button
              onClick={() => setActiveTab('violations')}
              className={clsx(
                'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'violations'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-neutral-600 hover:text-neutral-900'
              )}
            >
              Violations ({violations.length})
            </button>
          </nav>
        </div>

        {activeTab === 'policies' ? (
          <div className="divide-y divide-gray-200">
            {policies.map((policy, index) => (
              <motion.div
                key={policy.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="p-6 hover:bg-neutral-50 cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-neutral-900">{policy.name}</h3>
                      <CategoryBadge category={policy.category} />
                      <SeverityBadge severity={policy.severity} />
                      {policy.enabled ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3" />
                          Enabled
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-neutral-100 text-neutral-800">
                          <XCircle className="h-3 w-3" />
                          Disabled
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-neutral-600 mb-3">{policy.description}</p>
                    <div className="flex items-center gap-4 text-xs text-neutral-500">
                      <span>{policy.violationCount} violations</span>
                      <span>•</span>
                      <span>Updated {new Date(policy.updatedAt).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{policy.actions.length} actions configured</span>
                    </div>
                  </div>
                  <button className="ml-4 p-2 hover:bg-neutral-100 rounded-md transition-colors">
                    <Settings className="h-5 w-5 text-neutral-500" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {violations.map((violation, index) => (
              <motion.div
                key={violation.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="p-6 hover:bg-neutral-50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-neutral-900">{violation.ruleName}</h3>
                      <SeverityBadge severity={violation.severity} />
                      {violation.resolved ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3" />
                          Resolved
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <AlertTriangle className="h-3 w-3" />
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-neutral-900 mb-2">{violation.description}</p>
                    <div className="flex items-center gap-4 text-xs text-neutral-500">
                      <span>{violation.resource}</span>
                      <span>•</span>
                      <span>{new Date(violation.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                  {!violation.resolved && (
                    <button className="ml-4 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors">
                      Resolve
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
