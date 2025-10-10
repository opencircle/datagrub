import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, Home, Search } from 'lucide-react';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleGoHome = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        {/* 404 Illustration */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="text-9xl font-bold text-neutral-200">404</div>
            <div className="absolute inset-0 flex items-center justify-center">
              <AlertTriangle className="h-24 w-24 text-[#FF385C]" />
            </div>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-neutral-800 mb-4">
          Page Not Found
        </h1>

        {/* Description */}
        <p className="text-lg text-neutral-600 mb-2">
          Sorry, we couldn't find the page you're looking for.
        </p>

        {/* Attempted URL (Development) */}
        {process.env.NODE_ENV === 'development' && (
          <p className="text-sm text-neutral-500 mb-8 font-mono bg-neutral-100 rounded-lg p-3 inline-block">
            Attempted path: <span className="font-semibold">{location.pathname}</span>
          </p>
        )}

        {/* Suggestions */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8 text-left">
          <h2 className="text-lg font-semibold text-neutral-800 mb-3 flex items-center gap-2">
            <Search className="h-5 w-5 text-[#FF385C]" />
            Here's what you can do:
          </h2>
          <ul className="space-y-2 text-neutral-600">
            <li className="flex items-start gap-2">
              <span className="text-[#FF385C] mt-1">•</span>
              <span>Check the URL for typos or errors</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#FF385C] mt-1">•</span>
              <span>Use the navigation menu to find what you need</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#FF385C] mt-1">•</span>
              <span>Return to the homepage and start fresh</span>
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleGoBack}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-neutral-100 text-neutral-700 rounded-xl hover:bg-neutral-200 transition-all duration-200 font-semibold focus:outline-none focus:ring-4 focus:ring-neutral-300"
          >
            <ArrowLeft className="h-5 w-5" />
            Go Back
          </button>
          <button
            onClick={handleGoHome}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-[#FF385C] text-white rounded-xl hover:bg-[#E31C5F] transition-all duration-200 font-semibold focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
          >
            <Home className="h-5 w-5" />
            Go to Dashboard
          </button>
        </div>

        {/* Quick Links */}
        <div className="mt-12 pt-8 border-t border-neutral-200">
          <p className="text-sm text-neutral-500 mb-4">Quick Links:</p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate('/projects')}
              className="text-[#FF385C] hover:text-[#E31C5F] font-medium text-sm transition-colors"
            >
              Projects
            </button>
            <span className="text-neutral-300">•</span>
            <button
              onClick={() => navigate('/evaluations')}
              className="text-[#FF385C] hover:text-[#E31C5F] font-medium text-sm transition-colors"
            >
              Evaluations
            </button>
            <span className="text-neutral-300">•</span>
            <button
              onClick={() => navigate('/playground')}
              className="text-[#FF385C] hover:text-[#E31C5F] font-medium text-sm transition-colors"
            >
              Playground
            </button>
            <span className="text-neutral-300">•</span>
            <button
              onClick={() => navigate('/traces')}
              className="text-[#FF385C] hover:text-[#E31C5F] font-medium text-sm transition-colors"
            >
              Traces
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
