import React, { useState } from 'react';
import { Calendar, TrendingUp, Target, Activity, Download } from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { HeatMap } from '../components/HeatMap';
import { TrendChart } from '../components/TrendChart';
import { CompletionRateChart } from '../components/CompletionRateChart';
import { useHabits } from '../hooks/useHabits';
import { useCheckIns } from '../hooks/useCheckIns';
import { useDataValidation } from '../hooks/useDataValidation';
import { exportData, downloadFile } from '../utils/exportUtils';
import { cn } from '../lib/utils';
import type { DateRange, ExportFormat } from '../types';

const Analytics: React.FC = () => {
  const { habits, todayProgress, longestStreak, currentMaxStreak, getAllStats } = useHabits();
  const { heatmapData, trendData, weeklyData, checkIns } = useCheckIns();
  const { validationErrors, validateAllData } = useDataValidation();
  const [dateRange, setDateRange] = useState<DateRange>('30d');
  const [exportFormat, setExportFormat] = useState<ExportFormat>('json');

  const totalCheckIns = checkIns.length;
  const uniqueDays = new Set(checkIns.map(c => c.date)).size;
  const avgCompletionRate = habits.length > 0
    ? Math.round(
        Array.from(getAllStats().values()).reduce((sum, s) => sum + (s as { completionRate: number }).completionRate, 0) / habits.length
      )
    : 0;

  const handleExport = () => {
    const allStats = getAllStats();
    const result = exportData(exportFormat, habits, checkIns);
    downloadFile(result.content, result.filename, result.mimeType);
  };

  const dateRangeOptions: { value: DateRange; label: string }[] = [
    { value: '7d', label: '7天' },
    { value: '30d', label: '30天' },
    { value: '90d', label: '90天' },
    { value: '1y', label: '1年' },
    { value: 'all', label: '全部' },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
            数据统计
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            可视化分析你的习惯养成进度
          </p>
        </div>

        <div className="flex gap-3">
          <div className="flex items-center gap-2 bg-white dark:bg-zinc-900 p-1 rounded-xl border border-zinc-200 dark:border-zinc-800">
            {dateRangeOptions.map(option => (
              <button
                key={option.value}
                onClick={() => setDateRange(option.value)}
                className={cn(
                  'px-4 py-2 rounded-lg font-medium transition-all duration-200 text-sm',
                  dateRange === option.value
                    ? 'bg-sky-500 text-white shadow-md'
                    : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-white'
                )}
              >
                {option.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
              className="px-3 py-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-zinc-900 dark:text-white"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
            </select>
            <button
              onClick={handleExport}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 font-medium rounded-xl hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
            >
              <Download className="w-4 h-4" />
              导出
            </button>
          </div>
        </div>
      </div>

      {validationErrors.length > 0 && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Activity className="w-5 h-5 text-amber-500 mt-0.5" />
            <div>
              <h4 className="font-semibold text-amber-700 dark:text-amber-400">
                发现 {validationErrors.length} 个数据问题
              </h4>
              <button
                onClick={validateAllData}
                className="text-sm text-amber-600 dark:text-amber-500 hover:underline mt-1"
              >
                查看详情并修复
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="总打卡次数"
          value={totalCheckIns}
          icon={Activity}
          color="blue"
        />
        <StatsCard
          title="坚持天数"
          value={`${uniqueDays} 天`}
          icon={Calendar}
          color="green"
        />
        <StatsCard
          title="当前连续"
          value={`${currentMaxStreak} 天`}
          icon={TrendingUp}
          color="orange"
        />
        <StatsCard
          title="平均完成率"
          value={`${avgCompletionRate}%`}
          icon={Target}
          color="purple"
        />
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
            打卡热力图
          </h2>
          <span className="text-sm text-zinc-500 dark:text-zinc-400">
            过去一年
          </span>
        </div>
        <HeatMap data={heatmapData} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-800">
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white mb-6">
            完成趋势
          </h2>
          <TrendChart data={trendData} />
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-800">
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-4">
              今日完成率
            </h3>
            <div className="flex justify-center">
              <CompletionRateChart
                completed={todayProgress.completed}
                total={todayProgress.total}
                size="lg"
              />
            </div>
          </div>

          <div className="bg-gradient-to-br from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 rounded-2xl p-6 border border-sky-100 dark:border-sky-800">
            <h3 className="text-lg font-bold text-sky-700 dark:text-sky-400 mb-4">
              每周统计
            </h3>
            <div className="space-y-4">
              {weeklyData.slice(-4).reverse().map((week, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-600 dark:text-zinc-400">
                      {week.weekStart}
                    </span>
                    <span className="font-semibold text-sky-600 dark:text-sky-400">
                      {week.completionRate}% · {week.totalCheckIns} 次
                    </span>
                  </div>
                  <div className="h-2 bg-white dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-sky-400 to-cyan-500 rounded-full transition-all duration-500"
                      style={{ width: `${week.completionRate}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {habits.length > 0 && (
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-800">
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white mb-6">
            各习惯统计
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-800">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">习惯</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">频率</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">当前连续</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">最长连续</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">总打卡</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-zinc-500 dark:text-zinc-400">完成率</th>
                </tr>
              </thead>
              <tbody>
                {habits.map(habit => {
                  const stats = getAllStats().get(habit.id);
                  return (
                    <tr key={habit.id} className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/50">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                            style={{ backgroundColor: habit.color }}
                          >
                            {habit.name.charAt(0)}
                          </div>
                          <span className="font-medium text-zinc-900 dark:text-white">
                            {habit.name}
                          </span>
                        </div>
                      </td>
                      <td className="text-center py-4 px-4 text-zinc-600 dark:text-zinc-400">
                        {habit.frequency === 'daily' ? '每日' : `每周 ${habit.targetCount} 次`}
                      </td>
                      <td className="text-center py-4 px-4">
                        <span className="inline-flex items-center gap-1 text-orange-500 font-semibold">
                          {stats?.currentStreak || 0} 天
                        </span>
                      </td>
                      <td className="text-center py-4 px-4 text-zinc-600 dark:text-zinc-400">
                        {stats?.longestStreak || 0} 天
                      </td>
                      <td className="text-center py-4 px-4 text-zinc-600 dark:text-zinc-400">
                        {stats?.totalCheckIns || 0} 次
                      </td>
                      <td className="text-center py-4 px-4">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-24 h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${stats?.completionRate || 0}%`,
                                backgroundColor: habit.color,
                              }}
                            />
                          </div>
                          <span className="text-sm font-medium text-zinc-900 dark:text-white min-w-[40px]">
                            {stats?.completionRate || 0}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
