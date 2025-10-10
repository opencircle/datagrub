import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { loginStart, loginSuccess, loginFailure } from '@/store/slices/authSlice';
import { authService } from '../../../shared/services/authService';
import { motion } from 'framer-motion';

/**
 * Login Page with Real API Integration
 *
 * This component uses the real backend API via authService
 * instead of mock authentication.
 */
export const LoginReal: React.FC = () => {
  const [email, setEmail] = useState('admin@promptforge.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    dispatch(loginStart());

    try {
      // Use real API authentication
      const tokenResponse = await authService.login({ email, password });

      // Get user info
      const user = await authService.getCurrentUser();

      dispatch(loginSuccess({
        id: user.id,
        email: user.email,
        name: user.full_name || user.email,
        organization: user.organization_id,
        role: user.role,
      }));

      navigate('/projects');
    } catch (err: any) {
      console.error('Login error:', err);

      // Handle different error types
      if (err.response?.status === 401) {
        setError('Invalid email or password');
      } else if (err.response?.status === 500) {
        setError('Server error. Please try again later.');
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('Login failed. Please check your connection and try again.');
      }

      dispatch(loginFailure());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#FF385C]/5 via-white to-neutral-100">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md px-4"
      >
        <div className="bg-white border border-neutral-200 rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-[#FF385C] mb-2">PromptForge</h1>
            <p className="text-neutral-600 font-medium">AI Governance Platform</p>
            <p className="text-xs text-[#00A699] mt-3 font-medium">🔗 Connected to Real API</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-neutral-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-10 px-3 border border-neutral-300 rounded-xl bg-white text-neutral-700 focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C] transition-all duration-200 placeholder:text-neutral-400"
                placeholder="Enter your email"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-neutral-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-10 px-3 border border-neutral-300 rounded-xl bg-white text-neutral-700 focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20 focus:border-[#FF385C] transition-all duration-200 placeholder:text-neutral-400"
                placeholder="Enter your password"
                required
                disabled={loading}
              />
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-[#C13515] bg-[#C13515]/10 px-4 py-3 rounded-xl font-medium"
              >
                {error}
              </motion.div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-[#FF385C] text-white rounded-xl font-semibold hover:bg-[#E31C5F] transition-all duration-200 disabled:bg-neutral-300 disabled:text-neutral-500 disabled:cursor-not-allowed shadow-sm focus:outline-none focus:ring-4 focus:ring-[#FF385C]/20"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm font-semibold text-neutral-700 mb-3">Test Credentials</p>
            <div className="text-xs space-y-2 bg-neutral-50 rounded-xl p-4 text-left">
              <p className="text-neutral-600"><span className="font-semibold text-neutral-700">Admin:</span> admin@promptforge.com / admin123</p>
              <p className="text-neutral-600"><span className="font-semibold text-neutral-700">Developer:</span> developer@promptforge.com / dev123</p>
              <p className="text-neutral-600"><span className="font-semibold text-neutral-700">Viewer:</span> viewer@promptforge.com / viewer123</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
