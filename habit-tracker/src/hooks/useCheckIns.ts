import { useCallback, useMemo } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { CheckIn, DateRange } from '../types';
import { getDateRange, getLocalTimezone, getTodayISO } from '../utils/dateUtils';
import { logger } from '../utils/logger';

export const useCheckIns = () => {
  const { checkIns, addCheckIn, removeCheckIn } = useAppStore();

  const checkIn = useCallback((habitId: string, note?: string) => {
    const result = addCheckIn(habitId, note);

    if (result.isDuplicate) {
      logger.info('Duplicate check-in attempt', { habitId });
    } else if (result.success) {
      logger.info('Check-in successful', { habitId, newAchievements: result.newAchievements.length });
    }

    return result;
  }, [addCheckIn]);

  const uncheck = useCallback((habitId: string, date?: string) => {
    const targetDate = date || getTodayISO(getLocalTimezone());
    return removeCheckIn(habitId, targetDate);
  }, [removeCheckIn]);

  const getCheckInsByHabit = useCallback((habitId: string): CheckIn[] => {
    return checkIns
      .filter(c => c.habitId === habitId)
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [checkIns]);

  const getCheckInsByDate = useCallback((date: string): CheckIn[] => {
    return checkIns.filter(c => c.date === date);
  }, [checkIns]);

  const getCheckInsInRange = useCallback((range: DateRange): CheckIn[] => {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : range === '90d' ? 90 : range === '1y' ? 365 : checkIns.length;
    const dateRange = getDateRange(days, getLocalTimezone());
    return checkIns.filter(c => dateRange.includes(c.date));
  }, [checkIns]);

  const checkInDates = useMemo(() => {
    return [...new Set(checkIns.map(c => c.date))].sort();
  }, [checkIns]);

  const heatmapData = useMemo(() => {
    const dateMap = new Map<string, number>();
    const allDates = getDateRange(365, getLocalTimezone());

    allDates.forEach(date => dateMap.set(date, 0));
    checkIns.forEach(c => {
      const current = dateMap.get(c.date) || 0;
      dateMap.set(c.date, current + 1);
    });

    return Array.from(dateMap.entries()).map(([date, count]) => ({ date, count }));
  }, [checkIns]);

  const trendData = useMemo(() => {
    const days = 30;
    const dateRange = getDateRange(days, getLocalTimezone());
    const habitCount = useAppStore.getState().habits.length;

    return dateRange.map(date => {
      const completed = checkIns.filter(c => c.date === date).length;
      const target = habitCount;
      const rate = target > 0 ? Math.round((completed / target) * 100) : 0;
      return { date, completed, target, rate };
    });
  }, [checkIns]);

  const weeklyData = useMemo(() => {
    const weeks = 12;
    const result: { weekStart: string; completionRate: number; totalCheckIns: number }[] = [];
    const timezone = getLocalTimezone();

    for (let w = weeks - 1; w >= 0; w--) {
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - w * 7);
      const weekDates = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + i);
        return new Intl.DateTimeFormat('en-CA', {
          timeZone: timezone,
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
        }).format(d);
      });

      const weekCheckIns = checkIns.filter(c => weekDates.includes(c.date));
      const habitCount = useAppStore.getState().habits.length;
      const expected = habitCount * 7;
      const completionRate = expected > 0 ? Math.round((weekCheckIns.length / expected) * 100) : 0;

      result.push({
        weekStart: weekDates[0],
        completionRate,
        totalCheckIns: weekCheckIns.length,
      });
    }

    return result;
  }, [checkIns]);

  return {
    checkIns,
    checkIn,
    uncheck,
    getCheckInsByHabit,
    getCheckInsByDate,
    getCheckInsInRange,
    checkInDates,
    heatmapData,
    trendData,
    weeklyData,
  };
};
