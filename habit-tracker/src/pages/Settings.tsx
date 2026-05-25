import React, { useState, useRef } from 'react';
import {
  Bell, Moon, Sun, Download, Upload, Trash2, Database,
  Clock, Info, AlertTriangle, Check, Settings as SettingsIcon,
  FileJson, RefreshCw, Shield, HelpCircle
} from 'lucide-react';
import { Modal } from '../components/Modal';
import { useAppStore } from '../store/useAppStore';
import { useHabits } from '../hooks/useHabits';
import { useCheckIns } from '../hooks/useCheckIns';
import { useAchievements } from '../hooks/useAchievements';
import { useDataValidation } from '../hooks/useDataValidation';
import { useReminder } from '../hooks/useReminder';
import { exportData, downloadFile, parseImportData } from '../utils/exportUtils';
import { syncManager } from '../utils/syncManager';
import { storageManager } from '../utils/storage';
import { logger } from '../utils/logger';
import { cn } from '../lib/utils';
import type { ExportFormat, UserSettings } from '../types';

const Settings: React.FC = () => {
  const { settings, updateSettings, resetAllData } = useAppStore();
  const { habits } = useHabits();
  const { checkIns } = useCheckIns();
  const { achievements } = useAchievements();
  const { validateAllData, validationErrors, repairData } = useDataValidation();
  const { notificationPermission, enableReminders, disableReminders, isEnabled } = useReminder();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [showResetModal, setShowResetModal] = useState(false);
  const [showStorageInfo, setShowStorageInfo] = useState(false);
  const [importResult, setImportResult] = useState<{ success: boolean; message: string } | null>(null);
  const [storageInfo, setStorageInfo] = useState<{
    usedBytes: number;
    availableBytes: number;
    percentage: number;
    isNearLimit: boolean;
  } | null>(null);

  const handleThemeToggle = () => {
    const newTheme = settings.theme === 'light' ? 'dark' : 'light';
    updateSettings({ theme: newTheme });
  };

  const handleReminderToggle = async () => {
    if (isEnabled) {
      disableReminders();
    } else {
      await enableReminders();
    }
  };

  const handleExport = (format: ExportFormat) => {
    const result = exportData(format, habits, checkIns, achievements);
    downloadFile(result.content, result.filename, result.mimeType);
    logger.info('Data exported', { format, filename: result.filename });
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = parseImportData(text);

      const result = syncManager.mergeHabits(habits, data.habits || []);
      const checkInResult = syncManager.mergeCheckIns(checkIns, data.checkIns || []);

      useAppStore.getState().setHabits(result.data);
      useAppStore.getState().setCheckIns(checkInResult.data);

      if (data.settings) {
        updateSettings(data.settings);
      }

      setImportResult({
        success: true,
        message: `导入成功！${result.added} 个习惯，${checkInResult.added} 条打卡记录${result.updated > 0 ? `，更新 ${result.updated} 个习惯` : ''}${checkInResult.updated > 0 ? `，更新 ${checkInResult.updated} 条记录` : ''}`
      });
    } catch (error) {
      setImportResult({
        success: false,
        message: error instanceof Error ? error.message : '导入失败，请检查文件格式'
      });
    }

    e.target.value = '';
    setTimeout(() => setImportResult(null), 5000);
  };

  const handleCheckStorage = () => {
    const info = storageManager.getStorageInfo();
    setStorageInfo(info);
    setShowStorageInfo(true);
  };

  const handleReset = () => {
    resetAllData();
    setShowResetModal(false);
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const settingSections = [
    {
      id: 'appearance',
      title: '外观设置',
      icon: Moon,
      items: [
        {
          key: 'theme',
          label: '深色模式',
          description: '切换深色/浅色主题',
          type: 'toggle' as const,
          value: settings.theme === 'dark',
          onChange: handleThemeToggle,
          icon: settings.theme === 'dark' ? Moon : Sun,
        },
      ],
    },
    {
      id: 'notifications',
      title: '提醒设置',
      icon: Bell,
      items: [
        {
          key: 'reminders',
          label: '智能提醒',
          description: '根据你的活跃时段推送个性化提醒',
          type: 'toggle' as const,
          value: isEnabled,
          onChange: handleReminderToggle,
          disabled: notificationPermission === 'denied',
          disabledText: notificationPermission === 'denied' ? '已禁用通知权限' : undefined,
        },
        {
          key: 'defaultReminderTime',
          label: '默认提醒时间',
          description: '每日习惯的默认提醒时间',
          type: 'time' as const,
          value: settings.defaultReminderTime,
          onChange: (value: string) => updateSettings({
            defaultReminderTime: value,
            reminder: { ...settings.reminder, defaultTime: value }
          }),
          icon: Clock,
        },
      ],
    },
    {
      id: 'data',
      title: '数据管理',
      icon: Database,
      items: [
        {
          key: 'exportJson',
          label: '导出 JSON',
          description: '导出所有数据为 JSON 格式备份',
          type: 'button' as const,
          onClick: () => handleExport('json'),
          icon: FileJson,
        },
        {
          key: 'exportCsv',
          label: '导出 CSV',
          description: '导出打卡记录为 CSV 格式',
          type: 'button' as const,
          onClick: () => handleExport('csv'),
          icon: FileJson,
        },
        {
          key: 'import',
          label: '导入数据',
          description: '从备份文件导入数据',
          type: 'button' as const,
          onClick: handleImportClick,
          icon: Upload,
        },
        {
          key: 'storage',
          label: '存储空间',
          description: '查看本地存储使用情况',
          type: 'button' as const,
          onClick: handleCheckStorage,
          icon: Database,
        },
      ],
    },
    {
      id: 'maintenance',
      title: '系统维护',
      icon: SettingsIcon,
      items: [
        {
          key: 'validate',
          label: '数据校验',
          description: validationErrors.length > 0
            ? `发现 ${validationErrors.length} 个问题`
            : '检查数据完整性和一致性',
          type: 'button' as const,
          onClick: validateAllData,
          icon: Shield,
          variant: validationErrors.length > 0 ? 'warning' : 'default',
        },
        {
          key: 'repair',
          label: '修复数据',
          description: '尝试自动修复发现的数据问题',
          type: 'button' as const,
          onClick: repairData,
          icon: RefreshCw,
          disabled: validationErrors.length === 0,
        },
      ],
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
          设置
        </h1>
        <p className="text-zinc-500 dark:text-zinc-400 mt-2">
          个性化你的习惯追踪体验
        </p>
      </div>

      {importResult && (
        <div className={cn(
          'rounded-xl p-4 flex items-start gap-3',
          importResult.success
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
            : 'bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800'
        )}>
          {importResult.success ? (
            <Check className={cn('w-5 h-5 mt-0.5', 'text-green-500')} />
          ) : (
            <AlertTriangle className={cn('w-5 h-5 mt-0.5', 'text-rose-500')} />
          )}
          <p className={cn(
            'font-medium',
            importResult.success ? 'text-green-700 dark:text-green-400' : 'text-rose-700 dark:text-rose-400'
          )}>
            {importResult.message}
          </p>
        </div>
      )}

      <div className="space-y-6">
        {settingSections.map(section => (
          <div
            key={section.id}
            className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-100 dark:border-zinc-800 overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-zinc-100 dark:border-zinc-800">
              <h2 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
                <section.icon className="w-5 h-5 text-sky-500" />
                {section.title}
              </h2>
            </div>

            <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {section.items.map(item => (
                <div
                  key={item.key}
                  className={cn(
                    'px-6 py-4 flex items-center justify-between',
                    item.disabled && 'opacity-50'
                  )}
                >
                  <div className="flex items-center gap-4">
                    {item.icon && (
                      <div className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center">
                        <item.icon className="w-5 h-5 text-zinc-500" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-white">
                        {item.label}
                      </h3>
                      <p className="text-sm text-zinc-500 dark:text-zinc-400">
                        {item.disabledText || item.description}
                      </p>
                    </div>
                  </div>

                  {item.type === 'toggle' && (
                    <button
                      onClick={item.onChange}
                      disabled={item.disabled}
                      className={cn(
                        'relative w-12 h-7 rounded-full transition-colors duration-300',
                        item.value
                          ? 'bg-sky-500'
                          : 'bg-zinc-300 dark:bg-zinc-700'
                      )}
                    >
                      <div
                        className={cn(
                          'absolute top-1 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300',
                          item.value ? 'translate-x-6' : 'translate-x-1'
                        )}
                      />
                    </button>
                  )}

                  {item.type === 'time' && (
                    <input
                      type="time"
                      value={item.value}
                      onChange={(e) => item.onChange?.(e.target.value)}
                      className="px-3 py-2 bg-zinc-100 dark:bg-zinc-800 border-0 rounded-lg text-zinc-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  )}

                  {item.type === 'button' && (
                    <button
                      onClick={item.onClick}
                      disabled={item.disabled}
                      className={cn(
                        'px-4 py-2 rounded-lg font-medium transition-all duration-200',
                        item.variant === 'warning'
                          ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-900/50'
                          : 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400 hover:bg-sky-200 dark:hover:bg-sky-900/50',
                        item.disabled && 'opacity-50 cursor-not-allowed'
                      )}
                    >
                      操作
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-rose-200 dark:border-rose-900 overflow-hidden">
        <div className="px-6 py-4 border-b border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-900/10">
          <h2 className="text-lg font-bold text-rose-700 dark:text-rose-400 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            危险操作
          </h2>
        </div>
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
              <Trash2 className="w-5 h-5 text-rose-500" />
            </div>
            <div>
              <h3 className="font-medium text-zinc-900 dark:text-white">
                重置所有数据
              </h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                清除所有习惯、打卡记录和成就数据
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowResetModal(true)}
            className="px-4 py-2 bg-rose-500 text-white rounded-lg font-medium hover:bg-rose-600 transition-colors"
          >
            重置
          </button>
        </div>
      </div>

      <div className="bg-zinc-50 dark:bg-zinc-900/50 rounded-2xl p-6 border border-zinc-200 dark:border-zinc-800">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-zinc-200 dark:bg-zinc-800 flex items-center justify-center">
            <HelpCircle className="w-5 h-5 text-zinc-500" />
          </div>
          <div>
            <h3 className="font-semibold text-zinc-900 dark:text-white mb-1">
              关于数据存储
            </h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
              本应用使用浏览器 localStorage 存储您的数据。所有数据仅保存在您的本地设备上，
              不会上传到任何服务器。建议定期导出数据进行备份，以免数据丢失。
            </p>
          </div>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        className="hidden"
      />

      <Modal
        isOpen={showResetModal}
        onClose={() => setShowResetModal(false)}
        title="确认重置"
        size="md"
      >
        <div className="space-y-6">
          <div className="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-500 mt-0.5" />
              <div>
                <h4 className="font-semibold text-rose-700 dark:text-rose-400">
                  此操作不可撤销
                </h4>
                <p className="text-sm text-rose-600 dark:text-rose-500 mt-1">
                  所有习惯、打卡记录、成就数据和设置都将被永久删除。
                </p>
              </div>
            </div>
          </div>

          <p className="text-zinc-600 dark:text-zinc-400">
            您确定要继续吗？建议先导出数据备份。
          </p>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => setShowResetModal(false)}
              className="flex-1 px-6 py-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-xl hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
            >
              取消
            </button>
            <button
              onClick={handleReset}
              className="flex-1 px-6 py-3 bg-rose-500 text-white font-semibold rounded-xl hover:bg-rose-600 transition-colors"
            >
              确认重置
            </button>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={showStorageInfo}
        onClose={() => setShowStorageInfo(false)}
        title="存储空间使用情况"
        size="md"
      >
        {storageInfo && (
          <div className="space-y-6">
            <div className="flex items-center justify-center">
              <div className="relative w-40 h-40">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="12"
                    className="text-zinc-200 dark:text-zinc-800"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="12"
                    strokeDasharray={2 * Math.PI * 70}
                    strokeDashoffset={2 * Math.PI * 70 * (1 - storageInfo.percentage / 100)}
                    strokeLinecap="round"
                    className={storageInfo.isNearLimit ? 'text-rose-500' : 'text-sky-500'}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-zinc-900 dark:text-white">
                    {storageInfo.percentage}%
                  </span>
                  <span className="text-sm text-zinc-500 dark:text-zinc-400">已使用</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-zinc-100 dark:border-zinc-800">
                <span className="text-zinc-600 dark:text-zinc-400">已使用空间</span>
                <span className="font-semibold text-zinc-900 dark:text-white">
                  {formatBytes(storageInfo.usedBytes)}
                </span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-zinc-100 dark:border-zinc-800">
                <span className="text-zinc-600 dark:text-zinc-400">可用空间</span>
                <span className="font-semibold text-zinc-900 dark:text-white">
                  {formatBytes(storageInfo.availableBytes)}
                </span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-zinc-600 dark:text-zinc-400">总容量</span>
                <span className="font-semibold text-zinc-900 dark:text-white">
                  {formatBytes(storageInfo.usedBytes + storageInfo.availableBytes)}
                </span>
              </div>
            </div>

            {storageInfo.isNearLimit && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-amber-700 dark:text-amber-400">
                      存储空间不足
                    </h4>
                    <p className="text-sm text-amber-600 dark:text-amber-500 mt-1">
                      存储空间即将耗尽，建议导出旧数据备份或清理数据。
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <button
                onClick={() => setShowStorageInfo(false)}
                className="flex-1 px-6 py-3 bg-sky-500 text-white font-semibold rounded-xl hover:bg-sky-600 transition-colors"
              >
                确定
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Settings;
