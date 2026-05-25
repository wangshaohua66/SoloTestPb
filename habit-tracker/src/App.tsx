import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { ConfigProvider } from './context/ConfigContext';
import ErrorBoundary from './components/ErrorBoundary';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ToastProvider, useToast } from './components/Toast';
import Dashboard from './pages/Dashboard';
import Habits from './pages/Habits';
import Analytics from './pages/Analytics';
import Achievements from './pages/Achievements';
import Settings from './pages/Settings';
import { useAppStore } from './store/useAppStore';
import { useReminder } from './hooks/useReminder';
import { useDataValidation } from './hooks/useDataValidation';
import { storageManager } from './utils/storage';
import { logger } from './utils/logger';
import { AlertTriangle } from 'lucide-react';
import { cn } from './lib/utils';

const AppContent: React.FC = () => {
  const { initialize, isLoading, isInitialized, settings, updateSettings } = useAppStore();
  const { scheduleNextReminder } = useReminder();
  const { validateAllData } = useDataValidation();
  const { showToast } = useToast();
  const [showSidebar, setShowSidebar] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [storageWarning, setStorageWarning] = useState(false);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (isInitialized) {
      scheduleNextReminder();
      validateAllData();
    }
  }, [isInitialized, scheduleNextReminder, validateAllData]);

  useEffect(() => {
    setIsOnline(navigator.onLine);
    const handleOnline = () => {
      setIsOnline(true);
      if (wasOffline) {
        showToast('网络已恢复，数据已自动同步', 'online', 4000);
        setWasOffline(false);
      }
    };
    const handleOffline = () => {
      setIsOnline(false);
      setWasOffline(true);
      showToast('网络已断开，数据将保存在本地', 'offline', 0);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [wasOffline, showToast]);

  useEffect(() => {
    const checkStorage = () => {
      try {
        const info = storageManager.getStorageInfo();
        if (info.isNearLimit && !storageWarning) {
          setStorageWarning(true);
          logger.warn('Storage space is running low', info);
        } else if (!info.isNearLimit && storageWarning) {
          setStorageWarning(false);
        }
      } catch (error) {
        logger.error('Failed to check storage', error as Error);
      }
    };

    checkStorage();
    const interval = setInterval(checkStorage, 60000);
    return () => clearInterval(interval);
  }, [storageWarning]);

  const handleReminderGlobalToggle = async () => {
    if (settings.reminder.enabled) {
      updateSettings({
        remindersEnabled: false,
        reminder: { ...settings.reminder, enabled: false }
      });
      showToast('已关闭智能提醒', 'info');
    } else {
      if ('Notification' in window && Notification.permission === 'granted') {
        updateSettings({
          remindersEnabled: true,
          reminder: { ...settings.reminder, enabled: true }
        });
        showToast('已开启智能提醒', 'success');
      } else if ('Notification' in window && Notification.permission !== 'denied') {
        try {
          const permission = await Notification.requestPermission();
          if (permission === 'granted') {
            updateSettings({
              remindersEnabled: true,
              reminder: { ...settings.reminder, enabled: true }
            });
            showToast('已开启智能提醒', 'success');
          } else {
            showToast('请在浏览器设置中允许通知权限', 'warning');
          }
        } catch (error) {
          logger.error('Failed to request notification permission', error as Error);
          showToast('通知权限请求失败', 'error');
        }
      } else {
        showToast('请在浏览器设置中允许通知权限', 'warning');
      }
    }
  };

  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-zinc-800 text-white px-4 py-2 flex items-center justify-center gap-2 text-sm font-medium">
          <AlertTriangle className="w-4 h-4" />
          <span>当前处于离线状态，数据将保存在本地</span>
        </div>
      )}

      {storageWarning && (
        <div className={cn(
          'fixed z-50 bg-amber-50 dark:bg-amber-900/30 border-b border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 px-4 py-2 flex items-center justify-center gap-2 text-sm font-medium',
          isOnline ? 'top-0 left-0 right-0' : 'top-9 left-0 right-0'
        )}>
          <AlertTriangle className="w-4 h-4" />
          <span>存储空间即将耗尽，建议导出数据备份或清理旧数据</span>
          <button
            onClick={() => setStorageWarning(false)}
            className="ml-2 px-2 py-0.5 text-xs bg-amber-200 dark:bg-amber-800 rounded hover:bg-amber-300 dark:hover:bg-amber-700 transition-colors"
          >
            知道了
          </button>
        </div>
      )}

      <Sidebar />
      <div className={cn('lg:pl-72', (!isOnline || storageWarning) && 'pt-9')}>
        <Navbar onMenuClick={() => setShowSidebar(!showSidebar)} />
        <main className="px-4 md:px-8 lg:px-12 py-6 pb-24 lg:pb-6">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/habits" element={<Habits />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/achievements" element={<Achievements />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>

      <div
        className={cn(
          'fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300',
          showSidebar ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={() => setShowSidebar(false)}
      />

      <div
        className={cn(
          'fixed left-0 top-0 h-full w-72 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 z-50 lg:hidden transition-transform duration-300',
          showSidebar ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <Sidebar onNavigate={() => setShowSidebar(false)} />
      </div>
    </div>
  );
};

export default function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider>
        <ThemeProvider>
          <ToastProvider>
            <Router>
              <AppContent />
            </Router>
          </ToastProvider>
        </ThemeProvider>
      </ConfigProvider>
    </ErrorBoundary>
  );
}
