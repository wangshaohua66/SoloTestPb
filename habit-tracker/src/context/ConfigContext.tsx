import React, { createContext, useContext, useMemo } from 'react';
import appConfig from '../config/appConfig.json';
import type { AppConfig } from '../types';

interface ConfigContextType {
  config: AppConfig;
  getThemeColors: (themeName: string) => { primary: string; secondary: string; accent: string };
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const config = useMemo(() => appConfig as AppConfig, []);

  const getThemeColors = useMemo(() => {
    return (themeName: string) => {
      return config.themeColors[themeName] || config.themeColors.ocean;
    };
  }, [config]);

  const value = useMemo(() => ({
    config,
    getThemeColors,
  }), [config, getThemeColors]);

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfig = (): ConfigContextType => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};
