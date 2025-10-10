import React from 'react';
import PlaygroundEnhanced from './PlaygroundEnhanced';

// Bootstrap file for Module Federation
// Shell provides QueryClientProvider, so we don't wrap here
const App: React.FC = () => {
  return <PlaygroundEnhanced />;
};

export default App;
