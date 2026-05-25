import type { LogEntry } from '../types';

const LOG_STORAGE_KEY = 'habit_tracker_logs';
const MAX_LOG_ENTRIES = 500;

class Logger {
  private logs: LogEntry[] = [];

  constructor() {
    this.loadLogs();
  }

  private loadLogs(): void {
    try {
      const stored = localStorage.getItem(LOG_STORAGE_KEY);
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load logs from localStorage:', error);
      this.logs = [];
    }
  }

  private saveLogs(): void {
    try {
      if (this.logs.length > MAX_LOG_ENTRIES) {
        this.logs = this.logs.slice(-MAX_LOG_ENTRIES);
      }
      localStorage.setItem(LOG_STORAGE_KEY, JSON.stringify(this.logs));
    } catch (error) {
      console.warn('Failed to save logs to localStorage:', error);
    }
  }

  private addLog(level: LogEntry['level'], message: string, context?: Record<string, unknown>): void {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      context,
    };
    this.logs.push(entry);
    this.saveLogs();

    if (level === 'error') {
      console.error(`[${level.toUpperCase()}] ${message}`, context || '');
    } else if (level === 'warn') {
      console.warn(`[${level.toUpperCase()}] ${message}`, context || '');
    } else {
      console.info(`[${level.toUpperCase()}] ${message}`, context || '');
    }
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.addLog('info', message, context);
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.addLog('warn', message, context);
  }

  error(message: string, error?: Error, context?: Record<string, unknown>): void {
    this.addLog('error', message, {
      ...context,
      stack: error?.stack,
      errorMessage: error?.message,
    });
  }

  getLogs(level?: LogEntry['level']): LogEntry[] {
    if (level) {
      return this.logs.filter(log => log.level === level);
    }
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
    localStorage.removeItem(LOG_STORAGE_KEY);
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

export const logger = new Logger();
