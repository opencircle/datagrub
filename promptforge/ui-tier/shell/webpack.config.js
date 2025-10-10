const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const path = require('path');

module.exports = {
  entry: './src/index.tsx',
  mode: 'development',
  devServer: {
    port: 3000,
    historyApiFallback: true,
    hot: true,
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    modules: [
      path.resolve(__dirname, 'node_modules'),
      'node_modules',
    ],
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-react',
              '@babel/preset-typescript',
            ],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.REACT_APP_API_BASE_URL': JSON.stringify(
        process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
      ),
      'process.env.NODE_ENV': JSON.stringify(
        process.env.NODE_ENV || 'development'
      ),
    }),
    new ModuleFederationPlugin({
      name: 'shell',
      remotes: {
        projects: 'projects@http://localhost:3001/remoteEntry.js',
        evaluations: 'evaluations@http://localhost:3002/remoteEntry.js',
        playground: 'playground@http://localhost:3003/remoteEntry.js',
        traces: 'traces@http://localhost:3004/remoteEntry.js',
        policy: 'policy@http://localhost:3005/remoteEntry.js',
        models: 'models@http://localhost:3006/remoteEntry.js',
        insights: 'insights@http://localhost:3007/remoteEntry.js',
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^18.2.0',
        },
        'react-dom': {
          singleton: true,
          requiredVersion: '^18.2.0',
        },
        'react-router-dom': {
          singleton: true,
        },
        '@reduxjs/toolkit': {
          singleton: true,
        },
        'react-redux': {
          singleton: true,
        },
        '@tanstack/react-query': {
          singleton: true,
          requiredVersion: '^5.12.0',
        },
        axios: {
          singleton: true,
          requiredVersion: '^1.12.0',
        },
      },
    }),
    new HtmlWebpackPlugin({
      template: './public/index.html',
      favicon: './public/favicon.ico',
    }),
  ],
};
