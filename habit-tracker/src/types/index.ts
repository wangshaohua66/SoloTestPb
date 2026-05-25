export type Frequency = 'daily' | 'weekly';
export type ThemeMode = 'light' | 'dark' | 'system';
export type ExportFormat = 'json' | 'csv';
export type AchievementCondition = 'streak' | 'totalCheckins' | 'perfectWeek' | 'habitsCount';

export interface Habit {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  frequency: Frequency;
  targetCount: number;
  createdAt: string;
  timezone: string;
}

export interface CheckIn {
  id: string;
  habitId: string;
  date: string;
  timestamp: string;
  timezone: string;
  note?: string;
}

export interface AchievementProgress {
  current: number;
  target: number;
  percentage: number;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  condition: AchievementCondition;
  threshold: number;
  category?: string;
  unlockedAt?: string;
  progress?: AchievementProgress;
}

export interface UserSettings {
  theme: ThemeMode;
  remindersEnabled: boolean;
  defaultReminderTime: string;
  reminder: {
    enabled: boolean;
    defaultTime: string;
    smartReminder: boolean;
  };
  exportFormat: ExportFormat;
  activeHours: number[];
}

export interface AppConfig {
  defaultReminderTime: string;
  themeColors: Record<string, { primary: string; secondary: string; accent: string }>;
  exportFormats: ExportFormat[];
  achievements: Omit<Achievement, 'unlockedAt'>[];
}

export interface HabitStats {
  habitId: string;
  currentStreak: number;
  longestStreak: number;
  totalCheckIns: number;
  completionRate: number;
  weeklyProgress: number;
}

export interface SyncConflict {
  id: string;
  type: 'habit' | 'checkin';
  localData: unknown;
  remoteData: unknown;
  resolved: boolean;
  timestamp: string;
}

export interface StorageWarning {
  type: 'quota' | 'corruption' | 'version';
  message: string;
  timestamp: string;
}

export interface LogEntry {
  level: 'info' | 'warn' | 'error';
  message: string;
  timestamp: string;
  stack?: string;
  context?: Record<string, unknown>;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export type DateRange = '7d' | '30d' | '90d' | '1y' | 'all';
