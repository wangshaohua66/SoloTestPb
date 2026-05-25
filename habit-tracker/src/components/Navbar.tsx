import React, { useState } from 'react';
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
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useTheme } from '../context/ThemeContext';
import { useReminder } from '../hooks/useReminder';

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/habits', icon: ListTodo, label: '习惯' },
  { path: '/analytics', icon: BarChart3, label: '统计' },
  { path: '/achievements', icon: Trophy, label: '成就' },
  { path: '/settings', icon: Settings, label: '设置' },
];

interface NavbarProps {
  onMenuClick?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const location = useLocation();
  const { resolvedTheme, toggleTheme } = useTheme();
  const { isEnabled, enableReminders, disableReminders } = useReminder();
  const [isMobile, setIsMobile] = useState(false);

  React.useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleReminderToggle = async () => {
    if (isEnabled) {
      disableReminders();
    } else {
      await enableReminders();
    }
  };

  if (isMobile) {
    return (
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border-t border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center justify-around h-16 px-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={cn(
                  'flex flex-col items-center justify-center gap-1 p-2 rounded-xl transition-all duration-200',
                  isActive
                    ? 'text-sky-500'
                    : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-white'
                )}
              >
                <Icon className={cn('w-6 h-6', isActive && 'scale-110')} />
                <span className="text-xs font-medium">{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>
    );
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border-b border-zinc-200 dark:border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-sky-500/25">
            H
          </div>
          <span className="text-xl font-bold text-zinc-900 dark:text-white">
            Habit Tracker
          </span>
        </div>

        <div className="flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all duration-200',
                  isActive
                    ? 'bg-sky-50 text-sky-600 dark:bg-sky-900/30 dark:text-sky-400'
                    : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800'
                )}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReminderToggle}
            className={cn(
              'p-3 rounded-xl transition-all duration-200',
              isEnabled
                ? 'bg-orange-50 text-orange-500 dark:bg-orange-900/30 dark:text-orange-400'
                : 'hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-500'
            )}
            title={isEnabled ? '关闭提醒' : '开启提醒'}
          >
            {isEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
          </button>

          <button
            onClick={toggleTheme}
            className="p-3 rounded-xl hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors text-zinc-500"
            title={resolvedTheme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
          >
            {resolvedTheme === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </nav>
  );
};
