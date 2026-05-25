import { useState, useEffect, useCallback } from 'react';
import { logger } from '../utils/logger';
import { storage } from '../utils/storage';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      return storage.get<T>(key, initialValue);
    } catch (error) {
      logger.error(`Failed to read localStorage key: ${key}`, error as Error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      storage.set(key, valueToStore);
    } catch (error) {
      logger.error(`Failed to set localStorage key: ${key}`, error as Error);
    }
  }, [key, storedValue]);

  const removeValue = useCallback(() => {
    try {
      storage.remove(key);
      setStoredValue(initialValue);
    } catch (error) {
      logger.error(`Failed to remove localStorage key: ${key}`, error as Error);
    }
  }, [key, initialValue]);

  useEffect(() => {
    const unsubscribe = storage.subscribe(key, () => {
      const newValue = storage.get<T>(key, initialValue);
      setStoredValue(newValue);
    });

    return unsubscribe;
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}
