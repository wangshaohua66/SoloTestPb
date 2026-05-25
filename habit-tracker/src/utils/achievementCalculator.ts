import type { Habit, CheckIn, Achievement, HabitStats, AchievementCondition } from '../types';
import { calculateStreak, calculateLongestStreak, isPerfectWeek, getWeekDates, getTodayISO } from './dateUtils';
import { logger } from './logger';
import appConfig from '../config/appConfig.json';

export const calculateHabitStats = (
  habit: Habit,
  checkIns: CheckIn[],
  timezone?: string
): HabitStats => {
  const habitCheckIns = checkIns
    .filter(c => c.habitId === habit.id)
    .sort((a, b) => a.date.localeCompare(b.date));

  const checkInDates = habitCheckIns.map(c => c.date);
  const currentStreak = calculateStreak(checkInDates, timezone);
  const longestStreak = calculateLongestStreak(checkInDates);
  const totalCheckIns = habitCheckIns.length;

  const daysSinceCreation = Math.max(1, Math.ceil(
    (Date.now() - new Date(habit.createdAt).getTime()) / 86400000
  ));
  const expectedCheckIns = habit.frequency === 'daily'
    ? daysSinceCreation
    : Math.ceil(daysSinceCreation / 7) * habit.targetCount;
  const completionRate = expectedCheckIns > 0
    ? Math.min(100, Math.round((totalCheckIns / expectedCheckIns) * 100))
    : 0;

  const thisWeekDates = getWeekDates(new Date(), timezone);
  const weeklyProgress = thisWeekDates.filter(d => checkInDates.includes(d)).length;

  return {
    habitId: habit.id,
    currentStreak,
    longestStreak,
    totalCheckIns,
    completionRate,
    weeklyProgress,
  };
};

export const checkAchievement = (
  achievement: Omit<Achievement, 'unlockedAt'>,
  habits: Habit[],
  checkIns: CheckIn[],
  stats: Map<string, HabitStats>,
  timezone?: string
): boolean => {
  try {
    switch (achievement.condition as AchievementCondition) {
      case 'streak': {
        const maxStreak = Array.from(stats.values()).reduce(
          (max, s) => Math.max(max, s.currentStreak),
          0
        );
        return maxStreak >= achievement.threshold;
      }
      case 'totalCheckins': {
        const total = checkIns.length;
        return total >= achievement.threshold;
      }
      case 'perfectWeek': {
        const today = getTodayISO(timezone);
        const thisWeekDates = getWeekDates(new Date(), timezone);
        return habits.every(habit => {
          const habitCheckIns = checkIns
            .filter(c => c.habitId === habit.id)
            .map(c => c.date);
          if (habit.frequency === 'daily') {
            return thisWeekDates.every(d => habitCheckIns.includes(d));
          } else {
            const count = thisWeekDates.filter(d => habitCheckIns.includes(d)).length;
            return count >= habit.targetCount;
          }
        });
      }
      case 'habitsCount': {
        return habits.length >= achievement.threshold;
      }
      default:
        return false;
    }
  } catch (error) {
    logger.error('Failed to check achievement', error as Error, { achievement });
    return false;
  }
};

export const checkNewAchievements = (
  existingAchievements: Achievement[],
  habits: Habit[],
  checkIns: CheckIn[],
  timezone?: string
): Achievement[] => {
  const stats = new Map<string, HabitStats>();
  habits.forEach(habit => {
    stats.set(habit.id, calculateHabitStats(habit, checkIns, timezone));
  });

  const unlockedIds = new Set(
    existingAchievements.filter(a => a.unlockedAt).map(a => a.id)
  );
  const newAchievements: Achievement[] = [];

  for (const config of appConfig.achievements) {
    if (!unlockedIds.has(config.id)) {
      const achievementConfig = config as Omit<Achievement, 'unlockedAt'>;
      const unlocked = checkAchievement(achievementConfig, habits, checkIns, stats, timezone);
      if (unlocked) {
        newAchievements.push({
          ...achievementConfig,
          unlockedAt: new Date().toISOString(),
        });
        logger.info('New achievement unlocked!', { achievement: config.name });
      }
    }
  }

  return newAchievements;
};

export const getAchievementProgress = (
  achievement: Omit<Achievement, 'unlockedAt'>,
  habits: Habit[],
  checkIns: CheckIn[],
  stats: Map<string, HabitStats>,
  timezone?: string
): { current: number; percentage: number } => {
  let current = 0;

  switch (achievement.condition as AchievementCondition) {
    case 'streak': {
      current = Array.from(stats.values()).reduce(
        (max, s) => Math.max(max, s.currentStreak),
        0
      );
      break;
    }
    case 'totalCheckins': {
      current = checkIns.length;
      break;
    }
    case 'perfectWeek': {
      const thisWeekDates = getWeekDates(new Date(), timezone);
      const completedHabits = habits.filter(habit => {
        const habitCheckIns = checkIns
          .filter(c => c.habitId === habit.id)
          .map(c => c.date);
        if (habit.frequency === 'daily') {
          return thisWeekDates.every(d => habitCheckIns.includes(d));
        } else {
          const count = thisWeekDates.filter(d => habitCheckIns.includes(d)).length;
          return count >= habit.targetCount;
        }
      }).length;
      current = completedHabits > 0 ? 1 : 0;
      break;
    }
    case 'habitsCount': {
      current = habits.length;
      break;
    }
  }

  const percentage = Math.min(100, Math.round((current / achievement.threshold) * 100));
  return { current, percentage };
};

export const getMotivationalMessage = (
  stats: HabitStats,
  habitName: string
): { type: 'encouragement' | 'milestone' | 'streak'; message: string } => {
  if (stats.currentStreak === 0) {
    return {
      type: 'encouragement',
      message: `开始你的「${habitName}」第一天吧！`,
    };
  }
  if (stats.currentStreak === 7) {
    return {
      type: 'milestone',
      message: `太棒了！「${habitName}」已经坚持一周了！`,
    };
  }
  if (stats.currentStreak === 30) {
    return {
      type: 'milestone',
      message: `🎉 「${habitName}」坚持了整整一个月！你真了不起！`,
    };
  }
  if (stats.currentStreak === 100) {
    return {
      type: 'milestone',
      message: `🏆 「${habitName}」百日成就达成！你是真正的自律达人！`,
    };
  }
  if (stats.currentStreak > 30) {
    return {
      type: 'streak',
      message: `「${habitName}」已经连续 ${stats.currentStreak} 天了，继续保持！`,
    };
  }
  return {
    type: 'streak',
    message: `「${habitName}」连续 ${stats.currentStreak} 天，干得漂亮！`,
  };
};
