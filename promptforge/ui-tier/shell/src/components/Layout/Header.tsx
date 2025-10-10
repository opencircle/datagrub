import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { logout } from '@/store/slices/authSlice';
import { toggleTheme } from '@/store/slices/themeSlice';
import { authService } from '../../../../shared/services/authService';
import { Moon, Sun, LogOut, User } from 'lucide-react';

// Design System: Airbnb-inspired header with clean aesthetics
export const Header: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { mode } = useSelector((state: RootState) => state.theme);

  const handleLogout = () => {
    authService.logout();
    dispatch(logout());
  };

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };

  return (
    <header className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-bold text-neutral-700">Dashboard</h2>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleToggleTheme}
          className="p-2 rounded-xl hover:bg-neutral-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
          aria-label="Toggle theme"
        >
          {mode === 'light' ? (
            <Moon className="h-5 w-5 text-neutral-600" />
          ) : (
            <Sun className="h-5 w-5 text-neutral-600" />
          )}
        </button>

        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-neutral-100 border border-neutral-200">
          <User className="h-4 w-4 text-neutral-600" />
          <span className="text-sm font-semibold text-neutral-700">{user?.name}</span>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 rounded-xl hover:bg-neutral-100 transition-all duration-200 text-sm font-semibold text-neutral-600 hover:text-neutral-700 focus:outline-none focus:ring-2 focus:ring-[#FF385C]/20"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </header>
  );
};
