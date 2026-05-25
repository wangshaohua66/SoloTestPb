import { create } from 'zustand';
import type { Habit, CheckIn, Achievement, UserSettings, HabitStats, StorageWarning } from '../types';
import { storage } from '../utils/storage';
import { logger } from '../utils/logger';
import { syncManager } from '../utils/syncManager';
import { validateDataConsistency } from '../utils/validator';
import { checkNewAchievements, calculateHabitStats } from '../utils/achievementCalculator';
import { getLocalTimezone, getTodayISO, updateActiveHours } from '../utils/dateUtils';
import { generateId } from '../utils/validator';
import appConfig from '../config/appConfig.json';

interface AppState {
  habits: Habit[];
  checkIns: CheckIn[];
  achievements: Achievement[];
  settings: UserSettings;
  isLoading: boolean;
  isInitialized: boolean;
  storageWarnings: StorageWarning[];
  lastSyncVersion: number;
  error: string | null;

  initialize: () => Promise<void>;
  addHabit: (habit: Omit<Habit, 'id' | 'createdAt' | 'timezone'>) => boolean;
  updateHabit: (id: string, updates: Partial<Habit>) => boolean;
  deleteHabit: (id: string) => boolean;
  addCheckIn: (habitId: string, note?: string) => { success: boolean; isDuplicate: boolean; newAchievements: Achievement[] };
  removeCheckIn: (habitId: string, date: string) => boolean;
  updateSettings: (updates: Partial<UserSettings>) => boolean;
  getHabitStats: (habitId: string) => HabitStats | null;
  getAllStats: () => Map<string, HabitStats>;
  isCheckedInToday: (habitId: string) => boolean;
  getWeeklyCheckInCount: (habitId: string) => number;
  clearData: () => boolean;
  resetAllData: () => void;
  setHabits: (habits: Habit[]) => void;
  setCheckIns: (checkIns: CheckIn[]) => void;
  refreshStorageWarnings: () => void;
}

const defaultSettings: UserSettings = {
  theme: 'system',
  remindersEnabled: false,
  defaultReminderTime: appConfig.defaultReminderTime,
  reminder: {
    enabled: false,
    defaultTime: appConfig.defaultReminderTime,
    smartReminder: true,
  },
  exportFormat: 'json',
  activeHours: new Array(24).fill(0),
};

const initializeAchievements = (): Achievement[] => {
  return appConfig.achievements.map(a => ({
    ...a,
    condition: a.condition as Achievement['condition'],
  }));
};

export const useAppStore = create<AppState>((set, get) => ({
  habits: [],
  checkIns: [],
  achievements: [],
  settings: defaultSettings,
  isLoading: true,
  isInitialized: false,
  storageWarnings: [],
  lastSyncVersion: 0,
  error: null,

  initialize: async () => {
    try {
      logger.info('Initializing app state...');

      const timezone = getLocalTimezone();
      const storedHabits = storage.getHabits() as Habit[];
      const storedCheckIns = storage.getCheckIns() as CheckIn[];
      const storedAchievements = storage.getAchievements() as Achievement[];
      const storedSettings = storage.getSettings() as UserSettings | null;

      const { validData: validHabits, repairedCount: habitsRepaired } = syncManager.validateAndRepairHabits(storedHabits);
      const { validData: validCheckIns, repairedCount: checkInsRepaired } = syncManager.validateAndRepairCheckIns(storedCheckIns);

      const consistencyCheck = validateDataConsistency(validHabits, validCheckIns);
      if (!consistencyCheck.valid) {
        logger.warn('Data consistency issues found', { errors: consistencyCheck.errors });
      }

      const { merged: mergedCheckIns, duplicatesRemoved } = syncManager.mergeCheckIns(validCheckIns, validCheckIns);

      if (habitsRepaired > 0 || checkInsRepaired > 0 || duplicatesRemoved > 0) {
        logger.info('Data repair completed', { habitsRepaired, checkInsRepaired, duplicatesRemoved });
        storage.setHabits(validHabits);
        storage.setCheckIns(mergedCheckIns);
      }

      const achievements = storedAchievements.length > 0 ? storedAchievements : initializeAchievements();

      set({
        habits: validHabits,
        checkIns: mergedCheckIns,
        achievements,
        settings: storedSettings || defaultSettings,
        isLoading: false,
        isInitialized: true,
        lastSyncVersion: storage.getSyncVersion(),
        storageWarnings: storage.getWarnings(),
      });

      logger.info('App state initialized successfully', {
        habitsCount: validHabits.length,
        checkInsCount: mergedCheckIns.length,
        achievementsCount: achievements.length,
      });
    } catch (error) {
      logger.error('Failed to initialize app state', error as Error);
      set({
        isLoading: false,
        isInitialized: true,
        error: '数据加载失败，已使用默认设置',
        habits: [],
        checkIns: [],
        achievements: initializeAchievements(),
        settings: defaultSettings,
      });
    }
  },

  addHabit: (habitData) => {
    try {
      const timezone = getLocalTimezone();
      const newHabit: Habit = {
        ...habitData,
        id: generateId(),
        createdAt: getTodayISO(timezone),
        timezone,
      };

      const { habits, checkIns, achievements } = get();
      const updatedHabits = [...habits, newHabit];

      const newAchievements = checkNewAchievements(achievements, updatedHabits, checkIns, timezone);
      const updatedAchievements = [...achievements, ...newAchievements];

      storage.setHabits(updatedHabits);
      storage.setAchievements(updatedAchievements);
      storage.incrementSyncVersion();

      set({ habits: updatedHabits, achievements: updatedAchievements, lastSyncVersion: storage.getSyncVersion() });
      logger.info('Habit added', { habit: newHabit.name, newAchievements: newAchievements.length });

      return true;
    } catch (error) {
      logger.error('Failed to add habit', error as Error);
      return false;
    }
  },

  updateHabit: (id, updates) => {
    try {
      const { habits } = get();
      const habitIndex = habits.findIndex(h => h.id === id);
      if (habitIndex === -1) {
        logger.warn('Habit not found for update', { id });
        return false;
      }

      const updatedHabit = { ...habits[habitIndex], ...updates };
      const updatedHabits = [...habits];
      updatedHabits[habitIndex] = updatedHabit;

      storage.setHabits(updatedHabits);
      storage.incrementSyncVersion();

      set({ habits: updatedHabits, lastSyncVersion: storage.getSyncVersion() });
      logger.info('Habit updated', { id, name: updatedHabit.name });

      return true;
    } catch (error) {
      logger.error('Failed to update habit', error as Error);
      return false;
    }
  },

  deleteHabit: (id) => {
    try {
      const { habits, checkIns } = get();
      const updatedHabits = habits.filter(h => h.id !== id);
      const updatedCheckIns = checkIns.filter(c => c.habitId !== id);

      storage.setHabits(updatedHabits);
      storage.setCheckIns(updatedCheckIns);
      storage.incrementSyncVersion();

      set({
        habits: updatedHabits,
        checkIns: updatedCheckIns,
        lastSyncVersion: storage.getSyncVersion(),
      });
      logger.info('Habit deleted', { id });

      return true;
    } catch (error) {
      logger.error('Failed to delete habit', error as Error);
      return false;
    }
  },

  addCheckIn: (habitId, note) => {
    const timezone = getLocalTimezone();
    const today = getTodayISO(timezone);
    const { checkIns, habits, achievements, settings } = get();

    const habit = habits.find(h => h.id === habitId);
    if (!habit) {
      logger.warn('Habit not found for check-in', { habitId });
      return { success: false, isDuplicate: false, newAchievements: [] };
    }

    const existingCheckIn = checkIns.find(c => c.habitId === habitId && c.date === today);
    if (existingCheckIn) {
      logger.info('Duplicate check-in prevented', { habitId, date: today });
      return { success: false, isDuplicate: true, newAchievements: [] };
    }

    const timestamp = new Date().toISOString();
    const newCheckIn: CheckIn = {
      id: generateId(),
      habitId,
      date: today,
      timestamp,
      timezone,
      note,
    };

    const updatedCheckIns = [...checkIns, newCheckIn];
    const newAchievements = checkNewAchievements(achievements, habits, updatedCheckIns, timezone);
    const updatedAchievements = [...achievements, ...newAchievements];

    const updatedActiveHours = updateActiveHours(settings.activeHours, timestamp);
    const updatedSettings = { ...settings, activeHours: updatedActiveHours };

    storage.setCheckIns(updatedCheckIns);
    storage.setAchievements(updatedAchievements);
    storage.setSettings(updatedSettings);
    storage.incrementSyncVersion();

    set({
      checkIns: updatedCheckIns,
      achievements: updatedAchievements,
      settings: updatedSettings,
      lastSyncVersion: storage.getSyncVersion(),
    });

    logger.info('Check-in added', {
      habit: habit.name,
      date: today,
      newAchievements: newAchievements.length,
    });

    return { success: true, isDuplicate: false, newAchievements };
  },

  removeCheckIn: (habitId, date) => {
    try {
      const { checkIns } = get();
      const updatedCheckIns = checkIns.filter(
        c => !(c.habitId === habitId && c.date === date)
      );

      storage.setCheckIns(updatedCheckIns);
      storage.incrementSyncVersion();

      set({ checkIns: updatedCheckIns, lastSyncVersion: storage.getSyncVersion() });
      logger.info('Check-in removed', { habitId, date });

      return true;
    } catch (error) {
      logger.error('Failed to remove check-in', error as Error);
      return false;
    }
  },

  updateSettings: (updates) => {
    try {
      const { settings } = get();
      const updatedSettings = { ...settings, ...updates };

      storage.setSettings(updatedSettings);
      storage.incrementSyncVersion();

      set({ settings: updatedSettings, lastSyncVersion: storage.getSyncVersion() });
      logger.info('Settings updated', { updates: Object.keys(updates) });

      return true;
    } catch (error) {
      logger.error('Failed to update settings', error as Error);
      return false;
    }
  },

  getHabitStats: (habitId) => {
    const { habits, checkIns } = get();
    const habit = habits.find(h => h.id === habitId);
    if (!habit) return null;
    return calculateHabitStats(habit, checkIns, getLocalTimezone());
  },

  getAllStats: () => {
    const { habits, checkIns } = get();
    const stats = new Map<string, HabitStats>();
    const timezone = getLocalTimezone();
    habits.forEach(habit => {
      stats.set(habit.id, calculateHabitStats(habit, checkIns, timezone));
    });
    return stats;
  },

  isCheckedInToday: (habitId) => {
    const today = getTodayISO(getLocalTimezone());
    const { checkIns } = get();
    return checkIns.some(c => c.habitId === habitId && c.date === today);
  },

  getWeeklyCheckInCount: (habitId) => {
    const { habits, checkIns } = get();
    const habit = habits.find(h => h.id === habitId);
    if (!habit) return 0;

    const timezone = getLocalTimezone();
    const weekDates = Array.from({ length: 7 }, (_, i) => {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const tzDate = new Intl.DateTimeFormat('en-CA', {
        timeZone: timezone,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      }).format(d);
      return tzDate;
    });

    return checkIns.filter(c => c.habitId === habitId && weekDates.includes(c.date)).length;
  },

  clearData: () => {
    try {
      storage.clearAll();
      set({
        habits: [],
        checkIns: [],
        achievements: initializeAchievements(),
        settings: defaultSettings,
        lastSyncVersion: 0,
        storageWarnings: [],
      });
      logger.info('All data cleared');
      return true;
    } catch (error) {
      logger.error('Failed to clear data', error as Error);
      return false;
    }
  },

  refreshStorageWarnings: () => {
    storage.getStorageUsage();
    set({ storageWarnings: storage.getWarnings() });
  },

  setHabits: (habits: Habit[]) => {
    storage.setHabits(habits);
    storage.incrementSyncVersion();
    set({ habits, lastSyncVersion: storage.getSyncVersion() });
  },

  setCheckIns: (checkIns: CheckIn[]) => {
    storage.setCheckIns(checkIns);
    storage.incrementSyncVersion();
    set({ checkIns, lastSyncVersion: storage.getSyncVersion() });
  },

  resetAllData: () => {
    storage.clearAll();
    set({
      habits: [],
      checkIns: [],
      achievements: initializeAchievements(),
      settings: defaultSettings,
      lastSyncVersion: 0,
      storageWarnings: [],
      error: null,
    });
    logger.info('All data reset');
  },
}));
