import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ThemeMode } from '../types';
import { logger } from '../utils/logger';

interface ThemeContextType {
  theme: ThemeMode;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeMode>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  const getSystemTheme = useCallback((): 'light' | 'dark' => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  }, []);

  const applyTheme = useCallback((mode: ThemeMode) => {
    const actualTheme = mode === 'system' ? getSystemTheme() : mode;
    setResolvedTheme(actualTheme);

    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(actualTheme);
      root.style.colorScheme = actualTheme;
    }
  }, [getSystemTheme]);

  const setTheme = useCallback((newTheme: ThemeMode) => {
    try {
      setThemeState(newTheme);
      applyTheme(newTheme);
      localStorage.setItem('habit_tracker_theme', newTheme);
      logger.info('Theme changed', { theme: newTheme });
    } catch (error) {
      logger.error('Failed to set theme', error as Error);
    }
  }, [applyTheme]);

  const toggleTheme = useCallback(() => {
    const nextTheme: ThemeMode = resolvedTheme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
  }, [resolvedTheme, setTheme]);

  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem('habit_tracker_theme') as ThemeMode | null;
      if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
        setThemeState(savedTheme);
        applyTheme(savedTheme);
      } else {
        applyTheme('system');
      }
    } catch (error) {
      logger.error('Failed to load theme from storage', error as Error);
      applyTheme('system');
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      if (theme === 'system') {
        applyTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [theme, applyTheme]);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
