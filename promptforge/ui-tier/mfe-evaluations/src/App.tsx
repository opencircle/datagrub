import React, { useState, useEffect } from 'react';
import { mockEvaluations, Evaluation as MockEvaluation } from './mockData';
import { LineChart, Play, CheckCircle, XCircle, Loader, TrendingUp, AlertCircle, BookOpen, Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import evaluationService, { Evaluation, EvaluationResultDetailed, CustomEvaluationCreate } from '../../shared/services/evaluationService';
import { CatalogBrowser } from './components/EvaluationCatalog/CatalogBrowser';
import { Button } from '../../shared/components/core/Button';
import { CreateCustomEvaluationModal } from './components/CustomEvaluationForm/CreateCustomEvaluationModal';
import { CreateCustomEvaluationForm } from './components/CustomEvaluationForm/CreateCustomEvaluationForm';
import { EvaluationTable } from './components/EvaluationTable/EvaluationTable';
import { EvaluationStats } from './components/EvaluationDashboard/EvaluationStats';
import { EvaluationFilters } from './types/customEvaluation';

type EvaluationStatus = 'pending' | 'running' | 'completed' | 'failed';
type Tab = 'results' | 'catalog' | 'create';

// Design System: Status badges with Airbnb-inspired colors
const StatusBadge: React.FC<{ status: EvaluationStatus }> = ({ status }) => {
  const config = {
    pending: { bg: 'bg-neutral-100', text: 'text-neutral-700', icon: Loader },
    running: { bg: 'bg-[#0066FF]/10', text: 'text-[#0052CC]', icon: Loader },
    completed: { bg: 'bg-[#00A699]/10', text: 'text-[#008489]', icon: CheckCircle },
    failed: { bg: 'bg-[#C13515]/10', text: 'text-[#C13515]', icon: XCircle },
  };

  const { bg, text, icon: Icon } = config[status];

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${bg} ${text}`}>
      <Icon className="h-3 w-3" />
      {status}
    </span>
  );
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('results');
  const [selectedEvaluations, setSelectedEvaluations] = useState<string[]>([]);

  // State for modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleRunEvaluation = () => {
    setActiveTab('catalog');
  };

  const handleCatalogContinue = () => {
    // TODO: Navigate to wizard or execution
    console.log('Continue with selected evaluations:', selectedEvaluations);
  };

  const handleCreateCustomEvaluation = async (data: CustomEvaluationCreate) => {
    try {
      await evaluationService.createCustomEvaluation(data);
      // Show success toast or notification
      console.log('Custom evaluation created successfully');
      // Switch back to catalog tab
      setActiveTab('catalog');
      // Optionally refresh catalog
    } catch (err) {
      console.error('Failed to create custom evaluation:', err);
      throw err; // Re-throw to let form handle it
    }
  };


  return (
    <div className="space-y-6">
      {/* Tabs */}
      {/* Tab Navigation - Design System: Improved spacing and sizing */}
      <div className="border-b border-neutral-200">
        <div className="flex items-center justify-between mb-4">
          <nav className="flex gap-3">
            <button
              onClick={() => setActiveTab('results')}
              className={`
                h-11 px-4 py-2.5 border-b-2 font-semibold text-sm flex items-center gap-2 transition-all duration-200
                ${activeTab === 'results'
                  ? 'border-[#FF385C] text-[#FF385C]'
                  : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
                }
              `}
            >
              <LineChart className="h-5 w-5" />
              Evaluation Results
            </button>
            <button
              onClick={() => setActiveTab('catalog')}
              className={`
                h-11 px-4 py-2.5 border-b-2 font-semibold text-sm flex items-center gap-2 transition-all duration-200
                ${activeTab === 'catalog'
                  ? 'border-[#FF385C] text-[#FF385C]'
                  : 'border-transparent text-neutral-600 hover:text-neutral-800 hover:border-neutral-300'
                }
              `}
            >
              <BookOpen className="h-5 w-5" />
              Browse Catalog
              {selectedEvaluations.length > 0 && (
                <span className="ml-1 px-2 py-0.5 bg-[#FF385C] text-white text-xs font-semibold rounded-full">
                  {selectedEvaluations.length}
                </span>
              )}
            </button>
          </nav>
          {activeTab === 'results' && (
            <Button variant="primary" onClick={handleRunEvaluation}>
              <Play className="h-4 w-4 mr-2" />
              Run Evaluation
            </Button>
          )}
          {activeTab === 'catalog' && (
            <Button variant="primary" onClick={() => setActiveTab('create')}>
              <Plus className="h-4 w-4" />
              Create Custom Evaluation
            </Button>
          )}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-neutral-700">Evaluations</h1>
              <p className="text-neutral-600 mt-1 font-medium">
                Monitor and analyze prompt performance
              </p>
            </div>
          </div>

          {/* Compact Stats Dashboard - 1/4th of page */}
          <EvaluationStats />

          {/* New P0 Evaluation Table with Filters */}
          <EvaluationTable refreshTrigger={Date.now()} />
        </div>
      )}

      {activeTab === 'catalog' && (
        <CatalogBrowser
          selectedEvaluations={selectedEvaluations}
          onSelectionChange={setSelectedEvaluations}
          onContinue={selectedEvaluations.length > 0 ? handleCatalogContinue : undefined}
        />
      )}

      {activeTab === 'create' && (
        <div className="max-w-4xl mx-auto">
          <div className="bg-white border border-neutral-100 rounded-2xl p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-neutral-800 mb-2">Create Custom Evaluation</h2>
              <p className="text-sm text-neutral-500">
                Define a custom evaluation that runs after model invocation to assess input and output quality
              </p>
            </div>

            <CreateCustomEvaluationForm
              onCancel={() => setActiveTab('catalog')}
              onSuccess={handleCreateCustomEvaluation}
            />
          </div>
        </div>
      )}

      {/* Modals */}
      <CreateCustomEvaluationModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleCreateCustomEvaluation}
      />
    </div>
  );
};

export default App;
