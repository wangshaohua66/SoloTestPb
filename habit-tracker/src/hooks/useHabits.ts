import { useCallback, useMemo } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Habit, HabitStats, Frequency } from '../types';
import { validateHabit } from '../utils/validator';
import { logger } from '../utils/logger';

export const useHabits = () => {
  const {
    habits,
    addHabit: storeAddHabit,
    updateHabit: storeUpdateHabit,
    deleteHabit: storeDeleteHabit,
    getHabitStats,
    getAllStats,
    isCheckedInToday,
    getWeeklyCheckInCount,
  } = useAppStore();

  const addHabit = useCallback((habitData: {
    name: string;
    description?: string;
    icon?: string;
    color?: string;
    frequency: Frequency;
    targetCount?: number;
  }) => {
    const validation = validateHabit(habitData);
    if (!validation.valid) {
      logger.warn('Habit validation failed', { errors: validation.errors });
      return { success: false, errors: validation.errors };
    }

    const success = storeAddHabit({
      name: habitData.name.trim(),
      description: habitData.description || '',
      icon: habitData.icon || 'Target',
      color: habitData.color || '#0ea5e9',
      frequency: habitData.frequency,
      targetCount: habitData.frequency === 'weekly' ? (habitData.targetCount || 3) : 1,
    });

    return { success, errors: [] };
  }, [storeAddHabit]);

  const updateHabit = useCallback((id: string, updates: Partial<Habit>) => {
    const validation = validateHabit(updates);
    if (!validation.valid) {
      logger.warn('Habit update validation failed', { errors: validation.errors, id });
      return { success: false, errors: validation.errors };
    }

    const success = storeUpdateHabit(id, updates);
    return { success, errors: [] };
  }, [storeUpdateHabit]);

  const deleteHabit = useCallback((id: string) => {
    return storeDeleteHabit(id);
  }, [storeDeleteHabit]);

  const getHabitById = useCallback((id: string): Habit | undefined => {
    return habits.find(h => h.id === id);
  }, [habits]);

  const stats = useMemo(() => getAllStats(), [habits, getAllStats]);

  const habitsWithStats = useMemo(() => {
    return habits.map(habit => ({
      habit,
      stats: stats.get(habit.id) || null,
      isCheckedInToday: isCheckedInToday(habit.id),
      weeklyCount: getWeeklyCheckInCount(habit.id),
    }));
  }, [habits, stats, isCheckedInToday, getWeeklyCheckInCount]);

  const dailyHabits = useMemo(() => habits.filter(h => h.frequency === 'daily'), [habits]);
  const weeklyHabits = useMemo(() => habits.filter(h => h.frequency === 'weekly'), [habits]);

  const todayProgress = useMemo(() => {
    const totalHabits = habits.length;
    if (totalHabits === 0) return { completed: 0, total: 0, percentage: 0 };

    const completed = habits.filter(h => isCheckedInToday(h.id)).length;
    const percentage = Math.round((completed / totalHabits) * 100);

    return { completed, total: totalHabits, percentage };
  }, [habits, isCheckedInToday]);

  const longestStreak = useMemo(() => {
    let maxStreak = 0;
    stats.forEach(s => {
      maxStreak = Math.max(maxStreak, s.longestStreak);
    });
    return maxStreak;
  }, [stats]);

  const currentMaxStreak = useMemo(() => {
    let maxStreak = 0;
    stats.forEach(s => {
      maxStreak = Math.max(maxStreak, s.currentStreak);
    });
    return maxStreak;
  }, [stats]);

  return {
    habits,
    habitsWithStats,
    dailyHabits,
    weeklyHabits,
    addHabit,
    updateHabit,
    deleteHabit,
    getHabitById,
    getHabitStats,
    getAllStats,
    todayProgress,
    longestStreak,
    currentMaxStreak,
    isCheckedInToday,
  };
};
