import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  FolderKanban,
  LineChart,
  PlayCircle,
  Activity,
  Shield,
  Brain,
  Sparkles,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react';

const navigation = [
  { name: 'Projects', to: '/projects', icon: FolderKanban },
  { name: 'Evaluations', to: '/evaluations', icon: LineChart },
  { name: 'Playground', to: '/playground', icon: PlayCircle },
  { name: 'Traces', to: '/traces', icon: Activity },
  { name: 'Policy', to: '/policy', icon: Shield },
  { name: 'Models', to: '/models', icon: Brain },
  { name: 'Deep Insights', to: '/insights', icon: Sparkles },
];

// Design System: Claude.ai-inspired collapsible sidebar with modern minimalism
export const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('promptforge_sidebar_collapsed');
    return saved === 'true';
  });

  useEffect(() => {
    localStorage.setItem('promptforge_sidebar_collapsed', String(isCollapsed));
  }, [isCollapsed]);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <aside
      className={`bg-white border-r border-neutral-200 flex flex-col shadow-sm transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header with Logo and Toggle */}
      <div className={`border-b border-neutral-100 ${isCollapsed ? 'p-4' : 'p-6'} transition-all duration-300`}>
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-[#FF385C]">PromptForge</h1>
              <p className="text-sm text-neutral-600 font-medium mt-1">AI Governance Platform</p>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className={`p-2 rounded-lg hover:bg-neutral-100 text-neutral-600 hover:text-neutral-900 transition-colors ${
              isCollapsed ? 'mx-auto' : 'ml-2'
            }`}
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <PanelLeft className="h-5 w-5" /> : <PanelLeftClose className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className={`flex-1 py-6 space-y-1 ${isCollapsed ? 'px-2' : 'px-3'} transition-all duration-300`}>
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center rounded-xl text-sm font-semibold transition-all duration-200 ${
                isCollapsed ? 'justify-center px-3 py-3' : 'gap-3 px-3 py-2.5'
              } ${
                isActive
                  ? 'bg-[#FF385C] text-white shadow-sm'
                  : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-700'
              }`
            }
            title={isCollapsed ? item.name : undefined}
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {!isCollapsed && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Settings at bottom */}
      <div className={`border-t border-neutral-100 ${isCollapsed ? 'p-2' : 'p-3'} transition-all duration-300`}>
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center rounded-xl text-sm font-semibold transition-all duration-200 ${
              isCollapsed ? 'justify-center px-3 py-3' : 'gap-3 px-3 py-2.5'
            } ${
              isActive
                ? 'bg-[#FF385C] text-white shadow-sm'
                : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-700'
            }`
          }
          title={isCollapsed ? 'Settings' : undefined}
        >
          <Settings className="h-5 w-5 flex-shrink-0" />
          {!isCollapsed && <span>Settings</span>}
        </NavLink>
      </div>
    </aside>
  );
};
