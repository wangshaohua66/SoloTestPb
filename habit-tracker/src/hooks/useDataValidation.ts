import { useCallback, useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { validateHabit, validateCheckIn, validateSettings, validateDataConsistency, validateAndRepairAllData } from '../utils/validator';
import type { Habit, CheckIn, UserSettings, ValidationResult } from '../types';
import { logger } from '../utils/logger';

export const useDataValidation = () => {
  const { habits, checkIns, settings } = useAppStore();
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [lastValidation, setLastValidation] = useState<Date | null>(null);

  const validateAllData = useCallback((): {
    isValid: boolean;
    errors: string[];
    habitErrors: Map<string, string[]>;
    checkInErrors: Map<string, string[]>;
    settingsErrors: string[];
  } => {
    const errors: string[] = [];
    const habitErrors = new Map<string, string[]>();
    const checkInErrors = new Map<string, string[]>();

    habits.forEach(habit => {
      const result = validateHabit(habit);
      if (!result.valid) {
        habitErrors.set(habit.id, result.errors);
        errors.push(...result.errors.map(e => `习惯 "${habit.name}": ${e}`));
      }
    });

    checkIns.forEach(checkIn => {
      const result = validateCheckIn(checkIn);
      if (!result.valid) {
        checkInErrors.set(checkIn.id, result.errors);
        errors.push(...result.errors.map(e => `打卡记录 ${checkIn.date}: ${e}`));
      }
    });

    const settingsResult = validateSettings(settings);
    const settingsErrors = settingsResult.errors;
    if (!settingsResult.valid) {
      errors.push(...settingsResult.errors.map(e => `设置: ${e}`));
    }

    const consistencyResult = validateDataConsistency(habits, checkIns);
    if (!consistencyResult.valid) {
      errors.push(...consistencyResult.errors.map(e => `数据一致性: ${e}`));
    }

    setValidationErrors(errors);
    setLastValidation(new Date());
    logger.info('Data validation completed', {
      totalErrors: errors.length,
      habitErrors: habitErrors.size,
      checkInErrors: checkInErrors.size,
      settingsErrors: settingsErrors.length,
    });

    return {
      isValid: errors.length === 0,
      errors,
      habitErrors,
      checkInErrors,
      settingsErrors,
    };
  }, [habits, checkIns, settings]);

  const validateSingleHabit = useCallback((habit: Partial<Habit>): ValidationResult => {
    return validateHabit(habit);
  }, []);

  const validateSingleCheckIn = useCallback((checkIn: Partial<CheckIn>): ValidationResult => {
    return validateCheckIn(checkIn);
  }, []);

  const validateSingleSettings = useCallback((settings: Partial<UserSettings>): ValidationResult => {
    return validateSettings(settings);
  }, []);

  useEffect(() => {
    const result = validateAllData();
    if (result.errors.length > 0) {
      logger.warn('Data validation issues detected on mount', { errors: result.errors });
    }
  }, []);

  const repairData = useCallback((): { repaired: number; messages: string[] } => {
    const { habits: currentHabits, checkIns: currentCheckIns, settings: currentSettings } = useAppStore.getState();
    const result = validateAndRepairAllData(currentHabits, currentCheckIns, currentSettings);

    if (result.repairedHabits.length > 0) {
      useAppStore.getState().setHabits(result.repairedHabits);
    }
    if (result.repairedCheckIns.length > 0) {
      useAppStore.getState().setCheckIns(result.repairedCheckIns);
    }
    if (result.repairedSettings) {
      useAppStore.getState().updateSettings(result.repairedSettings);
    }

    validateAllData();

    logger.info('Data repair completed', {
      repairedHabits: result.repairedHabits.length,
      repairedCheckIns: result.repairedCheckIns.length,
      repairedSettings: !!result.repairedSettings,
      messages: result.messages,
    });

    return {
      repaired: result.repairedHabits.length + result.repairedCheckIns.length + (result.repairedSettings ? 1 : 0),
      messages: result.messages,
    };
  }, [validateAllData]);

  return {
    validateAllData,
    validateSingleHabit,
    validateSingleCheckIn,
    validateSingleSettings,
    validationErrors,
    lastValidation,
    hasErrors: validationErrors.length > 0,
    errorCount: validationErrors.length,
    repairData,
  };
};
