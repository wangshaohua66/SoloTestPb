import { logger } from './logger';
import type { StorageWarning } from '../types';

const STORAGE_KEYS = {
  HABITS: 'habit_tracker_habits',
  CHECKINS: 'habit_tracker_checkins',
  ACHIEVEMENTS: 'habit_tracker_achievements',
  SETTINGS: 'habit_tracker_settings',
  SYNC_VERSION: 'habit_tracker_sync_version',
  WARNINGS: 'habit_tracker_warnings',
} as const;

const STORAGE_QUOTA_THRESHOLD = 0.8;

class StorageManager {
  private listeners: Map<string, Set<() => void>> = new Map();
  private warnings: StorageWarning[] = [];

  constructor() {
    this.loadWarnings();
    this.setupStorageListener();
  }

  private setupStorageListener(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (e) => {
        if (e.key && this.listeners.has(e.key)) {
          this.listeners.get(e.key)?.forEach(callback => callback());
        }
      });
    }
  }

  private loadWarnings(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.WARNINGS);
      if (stored) {
        this.warnings = JSON.parse(stored);
      }
    } catch (error) {
      logger.warn('Failed to load storage warnings', { error });
      this.warnings = [];
    }
  }

  private saveWarnings(): void {
    try {
      localStorage.setItem(STORAGE_KEYS.WARNINGS, JSON.stringify(this.warnings));
    } catch (error) {
      logger.error('Failed to save storage warnings', error as Error);
    }
  }

  private addWarning(type: StorageWarning['type'], message: string): void {
    const warning: StorageWarning = {
      type,
      message,
      timestamp: new Date().toISOString(),
    };
    this.warnings.push(warning);
    this.saveWarnings();
  }

  getStorageInfo(): {
    usedBytes: number;
    availableBytes: number;
    percentage: number;
    isNearLimit: boolean;
  } {
    const { used, total, percentage } = this.getStorageUsage();
    return {
      usedBytes: used,
      availableBytes: total - used,
      percentage: Math.round(percentage * 100),
      isNearLimit: percentage >= 0.8,
    };
  }

  getStorageUsage(): { used: number; total: number; percentage: number } {
    try {
      let used = 0;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          const value = localStorage.getItem(key);
          if (value) {
            used += new Blob([key + value]).size;
          }
        }
      }

      const total = 5 * 1024 * 1024;
      const percentage = used / total;

      if (percentage >= STORAGE_QUOTA_THRESHOLD) {
        this.addWarning('quota', `存储空间已使用 ${(percentage * 100).toFixed(1)}%，即将达到上限`);
      }

      return { used, total, percentage };
    } catch (error) {
      logger.error('Failed to calculate storage usage', error as Error);
      return { used: 0, total: 5 * 1024 * 1024, percentage: 0 };
    }
  }

  get<T>(key: string, defaultValue: T): T {
    try {
      const stored = localStorage.getItem(key);
      if (stored === null) {
        return defaultValue;
      }
      return JSON.parse(stored) as T;
    } catch (error) {
      logger.error(`Failed to get item from storage: ${key}`, error as Error);
      this.addWarning('corruption', `数据 "${key}" 损坏，已使用默认值`);
      return defaultValue;
    }
  }

  set<T>(key: string, value: T): boolean {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);

      if (this.listeners.has(key)) {
        this.listeners.get(key)?.forEach(callback => callback());
      }

      this.getStorageUsage();
      return true;
    } catch (error) {
      if (error instanceof Error && error.name === 'QuotaExceededError') {
        this.addWarning('quota', '存储空间不足，请清理数据后重试');
        logger.error('Storage quota exceeded', error);
      } else {
        logger.error(`Failed to set item in storage: ${key}`, error as Error);
      }
      return false;
    }
  }

  remove(key: string): boolean {
    try {
      localStorage.removeItem(key);
      if (this.listeners.has(key)) {
        this.listeners.get(key)?.forEach(callback => callback());
      }
      return true;
    } catch (error) {
      logger.error(`Failed to remove item from storage: ${key}`, error as Error);
      return false;
    }
  }

  clearAll(): boolean {
    try {
      Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
      this.warnings = [];
      return true;
    } catch (error) {
      logger.error('Failed to clear storage', error as Error);
      return false;
    }
  }

  subscribe(key: string, callback: () => void): () => void {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set());
    }
    this.listeners.get(key)?.add(callback);

    return () => {
      this.listeners.get(key)?.delete(callback);
    };
  }

  getSyncVersion(): number {
    return this.get<number>(STORAGE_KEYS.SYNC_VERSION, 0);
  }

  incrementSyncVersion(): void {
    const version = this.getSyncVersion() + 1;
    this.set(STORAGE_KEYS.SYNC_VERSION, version);
  }

  getWarnings(): StorageWarning[] {
    return [...this.warnings];
  }

  clearWarnings(): void {
    this.warnings = [];
    this.remove(STORAGE_KEYS.WARNINGS);
  }

  exportAll(): string {
    const data = {
      habits: this.getHabits(),
      checkIns: this.getCheckIns(),
      achievements: this.getAchievements(),
      settings: this.getSettings(),
      syncVersion: this.getSyncVersion(),
      exportedAt: new Date().toISOString(),
    };
    return JSON.stringify(data, null, 2);
  }

  importAll(data: string): { success: boolean; conflicts: string[] } {
    try {
      const parsed = JSON.parse(data);
      const conflicts: string[] = [];
      const localVersion = this.getSyncVersion();
      const importVersion = parsed.syncVersion || 0;

      if (importVersion < localVersion) {
        conflicts.push('导入数据版本低于本地版本，可能存在数据冲突');
      }

      if (parsed.habits) this.setHabits(parsed.habits);
      if (parsed.checkIns) this.setCheckIns(parsed.checkIns);
      if (parsed.achievements) this.setAchievements(parsed.achievements);
      if (parsed.settings) this.setSettings(parsed.settings);

      this.incrementSyncVersion();
      logger.info('Data imported successfully', { importVersion, localVersion });

      return { success: true, conflicts };
    } catch (error) {
      logger.error('Failed to import data', error as Error);
      return { success: false, conflicts: ['数据格式错误'] };
    }
  }

  getHabits() { return this.get(STORAGE_KEYS.HABITS, []); }
  setHabits(value: unknown) { return this.set(STORAGE_KEYS.HABITS, value); }
  getCheckIns() { return this.get(STORAGE_KEYS.CHECKINS, []); }
  setCheckIns(value: unknown) { return this.set(STORAGE_KEYS.CHECKINS, value); }
  getAchievements() { return this.get(STORAGE_KEYS.ACHIEVEMENTS, []); }
  setAchievements(value: unknown) { return this.set(STORAGE_KEYS.ACHIEVEMENTS, value); }
  getSettings() { return this.get(STORAGE_KEYS.SETTINGS, null); }
  setSettings(value: unknown) { return this.set(STORAGE_KEYS.SETTINGS, value); }
}

export const storage = new StorageManager();
export const storageManager = storage;
