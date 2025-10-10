import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import { motion } from 'framer-motion';
import { FolderKanban, LineChart, Activity, Shield } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);

  const stats = [
    { name: 'Active Projects', value: '12', icon: FolderKanban, change: '+3 this week' },
    { name: 'Evaluations Run', value: '1,234', icon: LineChart, change: '+12% from last week' },
    { name: 'Traces Captured', value: '45.2K', icon: Activity, change: '+8.1% from yesterday' },
    { name: 'Policy Violations', value: '3', icon: Shield, change: '-2 from last week' },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold">Welcome back, {user?.name}!</h1>
        <p className="text-muted-foreground mt-2">
          Here's what's happening with your AI systems today.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="bg-card border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.name}</p>
                <p className="text-3xl font-bold mt-2">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-2">{stat.change}</p>
              </div>
              <div className="bg-primary/10 p-3 rounded-full">
                <stat.icon className="h-6 w-6 text-primary" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
            Create New Project
          </button>
          <button className="p-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
            Run Evaluation
          </button>
          <button className="p-4 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
            View Recent Traces
          </button>
        </div>
      </motion.div>
    </div>
  );
};
