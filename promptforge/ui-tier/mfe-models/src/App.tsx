import React, { useState } from 'react';
import { Cpu, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { ProviderList } from './components/ProviderList';
import { AddProviderModal } from './components/AddProviderModal';
import { ModelAnalytics } from './components/ModelAnalytics';
import type { ModelProviderConfig } from './types/provider';

type TabType = 'providers' | 'models';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('providers');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<ModelProviderConfig | null>(null);

  const handleAddProvider = () => {
    setIsAddModalOpen(true);
  };

  const handleEditProvider = (config: ModelProviderConfig) => {
    setEditingProvider(config);
    setIsAddModalOpen(true);
  };

  const handleModalClose = () => {
    setIsAddModalOpen(false);
    setEditingProvider(null);
  };

  const handleProviderSuccess = () => {
    // This will trigger a refresh in the ProviderList component
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Header - Design System: Increased spacing, clearer hierarchy */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-800">Model Dashboard</h1>
        <p className="text-neutral-500 mt-2 text-base">Manage providers, models, and configurations</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-neutral-200">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab('providers')}
            className={clsx(
              'pb-4 px-2 font-medium text-sm transition-all relative',
              activeTab === 'providers'
                ? 'text-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800'
            )}
          >
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Providers
            </div>
            {activeTab === 'providers' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF385C]"
              />
            )}
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={clsx(
              'pb-4 px-2 font-medium text-sm transition-all relative',
              activeTab === 'models'
                ? 'text-[#FF385C]'
                : 'text-neutral-600 hover:text-neutral-800'
            )}
          >
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Models
            </div>
            {activeTab === 'models' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF385C]"
              />
            )}
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'providers' ? (
        <>
          <ProviderList
            onAddProvider={handleAddProvider}
            onEditProvider={handleEditProvider}
          />
          <AddProviderModal
            isOpen={isAddModalOpen}
            onClose={handleModalClose}
            onSuccess={handleProviderSuccess}
            editingProvider={editingProvider}
          />
        </>
      ) : (
        <ModelAnalytics />
      )}
    </div>
  );
};

export default App;
