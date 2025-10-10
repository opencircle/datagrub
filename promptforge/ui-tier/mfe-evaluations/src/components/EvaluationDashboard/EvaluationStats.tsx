/**
 * Evaluation Statistics Dashboard
 *
 * Compact dashboard showing:
 * - Overall metrics (total runs, avg score, pass rate)
 * - Breakdown by category
 * - Breakdown by vendor
 * - Breakdown by project
 *
 * Takes up 1/4th of page height
 */

import React, { useMemo } from 'react';
import { useEvaluationsList } from '../../hooks/useEvaluations';

interface StatsBreakdown {
  name: string;
  count: number;
  avgScore: number;
  passRate: number;
}

interface EvaluationStats {
  totalRuns: number;
  avgScore: number;
  passRate: number;
  byCategory: StatsBreakdown[];
  byVendor: StatsBreakdown[];
  byProject: StatsBreakdown[];
}

export const EvaluationStats: React.FC = () => {
  // Fetch evaluations using React Query (shares cache with EvaluationTable)
  const { data, isLoading: loading } = useEvaluationsList({ limit: 100, offset: 0 });

  // Compute stats from fetched data
  const stats = useMemo(() => {
    if (!data) return null;

    const evaluations = data.evaluations;
      const total = evaluations.length;

      // Overall metrics
      const avgScore = total > 0
        ? evaluations.reduce((sum, e) => sum + (e.avg_score || 0), 0) / total
        : 0;

      const passed = evaluations.filter(e => e.passed === true).length;
      const passRate = total > 0 ? (passed / total) * 100 : 0;

      // Group by category
      const categoryMap = new Map<string, { count: number; totalScore: number; passed: number }>();
      evaluations.forEach(e => {
        const cat = e.category || 'uncategorized';
        const existing = categoryMap.get(cat) || { count: 0, totalScore: 0, passed: 0 };
        categoryMap.set(cat, {
          count: existing.count + 1,
          totalScore: existing.totalScore + (e.avg_score || 0),
          passed: existing.passed + (e.passed ? 1 : 0),
        });
      });

      const byCategory = Array.from(categoryMap.entries()).map(([name, data]) => ({
        name,
        count: data.count,
        avgScore: data.totalScore / data.count,
        passRate: (data.passed / data.count) * 100,
      })).sort((a, b) => b.count - a.count);

      // Group by vendor
      const vendorMap = new Map<string, { count: number; totalScore: number; passed: number }>();
      evaluations.forEach(e => {
        const vendor = e.vendor_name || 'N/A';
        const existing = vendorMap.get(vendor) || { count: 0, totalScore: 0, passed: 0 };
        vendorMap.set(vendor, {
          count: existing.count + 1,
          totalScore: existing.totalScore + (e.avg_score || 0),
          passed: existing.passed + (e.passed ? 1 : 0),
        });
      });

      const byVendor = Array.from(vendorMap.entries()).map(([name, data]) => ({
        name,
        count: data.count,
        avgScore: data.totalScore / data.count,
        passRate: (data.passed / data.count) * 100,
      })).sort((a, b) => b.count - a.count);

      // Group by project
      const projectMap = new Map<string, { count: number; totalScore: number; passed: number }>();
      evaluations.forEach(e => {
        const project = e.project_id || 'Unknown';
        const existing = projectMap.get(project) || { count: 0, totalScore: 0, passed: 0 };
        projectMap.set(project, {
          count: existing.count + 1,
          totalScore: existing.totalScore + (e.avg_score || 0),
          passed: existing.passed + (e.passed ? 1 : 0),
        });
      });

      const byProject = Array.from(projectMap.entries()).map(([name, data]) => ({
        name,
        count: data.count,
        avgScore: data.totalScore / data.count,
        passRate: (data.passed / data.count) * 100,
      })).sort((a, b) => b.count - a.count).slice(0, 5); // Top 5 projects

      return {
        totalRuns: total,
        avgScore,
        passRate,
        byCategory,
        byVendor,
        byProject,
      };
  }, [data]);

  if (loading) {
    return (
      <div className="h-48 flex items-center justify-center">
        <div className="text-gray-500">Loading statistics...</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden">
      {/* Ultra-Compact 4-Column Stats Bar */}
      <div className="grid grid-cols-4 gap-0 divide-x divide-neutral-200" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
        {/* Column 1: Overall Metrics (Horizontal) */}
        <div className="px-4 py-3 flex gap-6">
          {/* Total Runs */}
          <div className="flex flex-col">
            <div className="text-xs text-gray-500 mb-0.5">Total Runs</div>
            <div className="text-xl font-bold text-gray-900">{stats.totalRuns}</div>
          </div>
          {/* Avg Score */}
          <div className="flex flex-col">
            <div className="text-xs text-gray-500 mb-0.5">Avg Score</div>
            <div className="text-xl font-bold text-gray-900">{stats.avgScore.toFixed(2)}</div>
          </div>
          {/* Pass Rate */}
          <div className="flex flex-col">
            <div className="text-xs text-gray-500 mb-0.5">Pass Rate</div>
            <div className="text-xl font-bold text-gray-900">{stats.passRate.toFixed(0)}%</div>
          </div>
        </div>

        {/* Column 2: By Category */}
        <div className="px-4 py-3">
          <div className="text-xs text-gray-500 font-semibold mb-1.5">By Category</div>
          <div className="space-y-0.5">
            {stats.byCategory.slice(0, 2).map((item) => (
              <div key={item.name} className="text-xs">
                <span className="text-gray-900 capitalize">{item.name}</span>
                <span className="text-gray-500 ml-2">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Column 3: By Vendor */}
        <div className="px-4 py-3">
          <div className="text-xs text-gray-500 font-semibold mb-1.5">By Source</div>
          <div className="space-y-0.5">
            {stats.byVendor.slice(0, 2).map((item) => (
              <div key={item.name} className="text-xs">
                <span className="text-gray-900">{item.name}</span>
                <span className="text-gray-500 ml-2">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Column 4: By Project */}
        <div className="px-4 py-3">
          <div className="text-xs text-gray-500 font-semibold mb-1.5">By Project</div>
          <div className="space-y-0.5">
            {stats.byProject.slice(0, 2).map((item) => (
              <div key={item.name} className="text-xs">
                <span className="text-gray-900 truncate inline-block max-w-[120px]" title={item.name}>
                  {item.name.length > 15 ? item.name.substring(0, 15) + '...' : item.name}
                </span>
                <span className="text-gray-500 ml-2">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
