import { useCallback, useMemo } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Achievement } from '../types';
import { getAchievementProgress } from '../utils/achievementCalculator';
import { useConfig } from '../context/ConfigContext';

export const useAchievements = () => {
  const { achievements, habits, checkIns, getAllStats } = useAppStore();
  const { config } = useConfig();

  const unlockedAchievements = useMemo(() => {
    return achievements.filter(a => a.unlockedAt);
  }, [achievements]);

  const lockedAchievements = useMemo(() => {
    return achievements.filter(a => !a.unlockedAt);
  }, [achievements]);

  const achievementsWithProgress = useMemo(() => {
    const stats = getAllStats();
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    return achievements.map(achievement => {
      const configAchievement = config.achievements.find(a => a.id === achievement.id);
      const base = configAchievement || achievement;
      const progress = getAchievementProgress(base, habits, checkIns, stats, timezone);

      return {
        ...achievement,
        name: base.name,
        description: base.description,
        icon: base.icon,
        condition: base.condition,
        threshold: base.threshold,
        progress: progress.current,
        percentage: progress.percentage,
        isUnlocked: !!achievement.unlockedAt,
      };
    });
  }, [achievements, habits, checkIns, getAllStats, config]);

  const recentAchievements = useMemo(() => {
    return unlockedAchievements
      .sort((a, b) => (b.unlockedAt || '').localeCompare(a.unlockedAt || ''))
      .slice(0, 5);
  }, [unlockedAchievements]);

  const totalProgress = useMemo(() => {
    const total = achievements.length;
    const unlocked = unlockedAchievements.length;
    return {
      unlocked,
      total,
      percentage: total > 0 ? Math.round((unlocked / total) * 100) : 0,
    };
  }, [achievements, unlockedAchievements]);

  const getAchievementById = useCallback((id: string): Achievement | undefined => {
    return achievements.find(a => a.id === id);
  }, [achievements]);

  const achievementsByType = useMemo(() => {
    return {
      streak: achievementsWithProgress.filter(a => a.condition === 'streak'),
      totalCheckins: achievementsWithProgress.filter(a => a.condition === 'totalCheckins'),
      perfectWeek: achievementsWithProgress.filter(a => a.condition === 'perfectWeek'),
      habitsCount: achievementsWithProgress.filter(a => a.condition === 'habitsCount'),
    };
  }, [achievementsWithProgress]);

  const categorizedAchievements = useMemo(() => {
    return {
      streak: achievementsWithProgress.filter(a => a.condition === 'streak'),
      total: achievementsWithProgress.filter(a => a.condition === 'totalCheckins'),
      milestone: achievementsWithProgress.filter(a => a.condition === 'perfectWeek'),
      special: achievementsWithProgress.filter(a => a.condition === 'habitsCount'),
    };
  }, [achievementsWithProgress]);

  const totalProgressWithLocked = useMemo(() => {
    const total = achievements.length;
    const unlocked = unlockedAchievements.length;
    return {
      unlocked,
      total,
      locked: total - unlocked,
      percentage: total > 0 ? Math.round((unlocked / total) * 100) : 0,
    };
  }, [achievements, unlockedAchievements]);

  return {
    achievements,
    achievementsWithProgress,
    unlockedAchievements,
    lockedAchievements,
    recentAchievements,
    totalProgress: totalProgressWithLocked,
    getAchievementById,
    achievementsByType,
    categorizedAchievements,
  };
};
