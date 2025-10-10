import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProjectList } from './views/ProjectList';
import { ProjectDetail } from './views/ProjectDetail';
import { PromptDetail } from './views/PromptDetail';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<ProjectList />} />
      <Route path="/:projectId" element={<ProjectDetail />} />
      <Route path="/prompt/:promptId" element={<PromptDetail />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
