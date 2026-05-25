import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  ListTodo,
  BarChart3,
  Trophy,
  Settings,
  Moon,
  Sun,
  Bell,
  BellOff,
  Flame,
  Target,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useTheme } from '../context/ThemeContext';
import { useReminder } from '../hooks/useReminder';
import { useHabits } from '../hooks/useHabits';
import { useAchievements } from '../hooks/useAchievements';

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/habits', icon: ListTodo, label: '习惯管理' },
  { path: '/analytics', icon: BarChart3, label: '数据统计' },
  { path: '/achievements', icon: Trophy, label: '成就中心' },
  { path: '/settings', icon: Settings, label: '系统设置' },
];

interface SidebarProps {
  onNavigate?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onNavigate }) => {
  const location = useLocation();
  const { resolvedTheme, toggleTheme } = useTheme();
  const { isEnabled, enableReminders, disableReminders } = useReminder();
  const { todayProgress, currentMaxStreak } = useHabits();
  const { totalProgress } = useAchievements();

  const handleReminderToggle = async () => {
    if (isEnabled) {
      disableReminders();
    } else {
      await enableReminders();
    }
  };

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-72 z-40 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 flex flex-col">
      <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-sky-500/25">
            H
          </div>
          <div>
            <h1 className="text-xl font-bold text-zinc-900 dark:text-white">
              Habit Tracker
            </h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              自律让你更自由
            </p>
          </div>
        </div>
      </div>

      <div className="px-4 py-4 space-y-2">
        <div className="bg-gradient-to-br from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 rounded-2xl p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-white dark:bg-zinc-800 rounded-xl">
              <Target className="w-5 h-5 text-sky-500" />
            </div>
            <div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">今日进度</p>
              <p className="text-lg font-bold text-zinc-900 dark:text-white">
                {todayProgress.completed} / {todayProgress.total}
              </p>
            </div>
          </div>
          <div className="h-2 bg-white dark:bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-sky-400 to-cyan-500 rounded-full transition-all duration-500"
              style={{ width: `${todayProgress.percentage}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="bg-orange-50 dark:bg-orange-900/20 rounded-xl p-3">
            <div className="flex items-center gap-2 mb-1">
              <Flame className="w-4 h-4 text-orange-500" />
              <span className="text-xs text-zinc-500 dark:text-zinc-400">连续</span>
            </div>
            <p className="text-xl font-bold text-zinc-900 dark:text-white">
              {currentMaxStreak}
              <span className="text-xs font-normal text-zinc-500 ml-1">天</span>
            </p>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-3">
            <div className="flex items-center gap-2 mb-1">
              <Trophy className="w-4 h-4 text-purple-500" />
              <span className="text-xs text-zinc-500 dark:text-zinc-400">成就</span>
            </div>
            <p className="text-xl font-bold text-zinc-900 dark:text-white">
              {totalProgress.unlocked}
              <span className="text-xs font-normal text-zinc-500 ml-1">/{totalProgress.total}</span>
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onNavigate}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-sky-500 to-cyan-500 text-white shadow-lg shadow-sky-500/25'
                  : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800'
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 space-y-2">
        <button
          onClick={handleReminderToggle}
          className={cn(
            'w-full flex items-center justify-between px-4 py-3 rounded-xl font-medium transition-all duration-200',
            isEnabled
              ? 'bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400'
              : 'hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
          )}
        >
          <div className="flex items-center gap-3">
            {isEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
            <span>智能提醒</span>
          </div>
          <div className={cn(
            'w-10 h-6 rounded-full transition-colors duration-200 relative',
            isEnabled ? 'bg-orange-500' : 'bg-zinc-300 dark:bg-zinc-600'
          )}>
            <div className={cn(
              'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200',
              isEnabled ? 'translate-x-5' : 'translate-x-1'
            )} />
          </div>
        </button>

        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-4 py-3 rounded-xl font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors text-zinc-600 dark:text-zinc-400"
        >
          <div className="flex items-center gap-3">
            {resolvedTheme === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
            <span>{resolvedTheme === 'dark' ? '深色模式' : '浅色模式'}</span>
          </div>
          <div className="w-10 h-6 rounded-full bg-zinc-300 dark:bg-zinc-600 relative">
            <div className={cn(
              'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200',
              resolvedTheme === 'dark' ? 'translate-x-5' : 'translate-x-1'
            )} />
          </div>
        </button>
      </div>
    </aside>
  );
};
