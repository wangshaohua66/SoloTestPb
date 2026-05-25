import { logger } from './logger';

export const isValidTimezone = (timezone: string): boolean => {
  try {
    Intl.DateTimeFormat(undefined, { timeZone: timezone });
    return true;
  } catch {
    return false;
  }
};

export const getLocalTimezone = (): string => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch (error) {
    logger.warn('Failed to get local timezone, falling back to UTC', { error });
    return 'UTC';
  }
};

export const toISODate = (date: Date, timezone?: string): string => {
  const tz = timezone || getLocalTimezone();
  if (!isValidTimezone(tz)) {
    logger.warn('Invalid timezone, using local timezone', { timezone: tz });
    return date.toISOString().split('T')[0];
  }

  try {
    const formatter = new Intl.DateTimeFormat('en-CA', {
      timeZone: tz,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
    return formatter.format(date);
  } catch (error) {
    logger.error('Failed to format date with timezone', error as Error, { timezone: tz });
    return date.toISOString().split('T')[0];
  }
};

export const getTodayISO = (timezone?: string): string => {
  return toISODate(new Date(), timezone);
};

export const parseISODate = (isoDate: string): Date => {
  const [year, month, day] = isoDate.split('-').map(Number);
  return new Date(year, month - 1, day);
};

export const formatDate = (isoDate: string, locale = 'zh-CN'): string => {
  try {
    const date = parseISODate(isoDate);
    return date.toLocaleDateString(locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long',
    });
  } catch (error) {
    logger.error('Failed to format date', error as Error, { isoDate });
    return isoDate;
  }
};

export const getDateRange = (days: number, timezone?: string): string[] => {
  const dates: string[] = [];
  const today = parseISODate(getTodayISO(timezone));

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    dates.push(toISODate(date, timezone));
  }

  return dates;
};

export const isSameDay = (date1: string, date2: string): boolean => {
  return date1 === date2;
};

export const isToday = (isoDate: string, timezone?: string): boolean => {
  return isSameDay(isoDate, getTodayISO(timezone));
};

export const calculateStreak = (checkInDates: string[], timezone?: string): number => {
  if (checkInDates.length === 0) return 0;

  const sortedDates = [...new Set(checkInDates)].sort().reverse();
  const today = getTodayISO(timezone);
  const yesterday = toISODate(new Date(Date.now() - 86400000), timezone);

  if (!isSameDay(sortedDates[0], today) && !isSameDay(sortedDates[0], yesterday)) {
    return 0;
  }

  let streak = 1;
  for (let i = 1; i < sortedDates.length; i++) {
    const current = parseISODate(sortedDates[i - 1]);
    const prev = parseISODate(sortedDates[i]);
    const diffDays = Math.round((current.getTime() - prev.getTime()) / 86400000);

    if (diffDays === 1) {
      streak++;
    } else if (diffDays > 1) {
      break;
    }
  }

  return streak;
};

export const calculateLongestStreak = (checkInDates: string[]): number => {
  if (checkInDates.length === 0) return 0;

  const sortedDates = [...new Set(checkInDates)].sort();
  let longest = 1;
  let current = 1;

  for (let i = 1; i < sortedDates.length; i++) {
    const prev = parseISODate(sortedDates[i - 1]);
    const curr = parseISODate(sortedDates[i]);
    const diffDays = Math.round((curr.getTime() - prev.getTime()) / 86400000);

    if (diffDays === 1) {
      current++;
      longest = Math.max(longest, current);
    } else if (diffDays > 1) {
      current = 1;
    }
  }

  return longest;
};

export const getWeekDates = (date: Date, timezone?: string): string[] => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(d.setDate(diff));

  const weekDates: string[] = [];
  for (let i = 0; i < 7; i++) {
    const weekDay = new Date(monday);
    weekDay.setDate(monday.getDate() + i);
    weekDates.push(toISODate(weekDay, timezone));
  }

  return weekDates;
};

export const isPerfectWeek = (habitCheckIns: string[], weekStart: string): boolean => {
  const weekDates = getWeekDates(parseISODate(weekStart));
  return weekDates.every(date => habitCheckIns.includes(date));
};

export const getHourFromTime = (time: string): number => {
  const [hours] = time.split(':').map(Number);
  return hours;
};

export const updateActiveHours = (activeHours: number[], timestamp: string): number[] => {
  const hour = new Date(timestamp).getHours();
  const newHours = [...activeHours];
  newHours[hour] = (newHours[hour] || 0) + 1;
  return newHours;
};

export const getBestReminderHour = (activeHours: number[]): number => {
  const maxCount = Math.max(...activeHours, 1);
  const bestHour = activeHours.indexOf(maxCount);
  return bestHour >= 0 ? bestHour : 20;
};
