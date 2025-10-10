/// <reference types="node" />

declare namespace NodeJS {
  interface ProcessEnv {
    readonly NODE_ENV: 'development' | 'production' | 'test';
    readonly REACT_APP_API_BASE_URL?: string;
  }
}

// Extend process for webpack DefinePlugin
declare const process: {
  env: NodeJS.ProcessEnv;
};
