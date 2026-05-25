import React, { useState } from 'react';
import { Trophy, Lock, Sparkles, Star, Target, Flame, Calendar, Award, TrendingUp } from 'lucide-react';
import { Badge } from '../components/Badge';
import { useAchievements } from '../hooks/useAchievements';
import { useHabits } from '../hooks/useHabits';
import { cn } from '../lib/utils';
import type { Achievement } from '../types';

const Achievements: React.FC = () => {
  const { unlockedAchievements, lockedAchievements, totalProgress, categorizedAchievements } = useAchievements();
  const { longestStreak, currentMaxStreak, habits } = useHabits();
  const [activeTab, setActiveTab] = useState<'all' | 'unlocked' | 'locked'>('all');

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'streak':
        return Flame;
      case 'total':
        return Target;
      case 'milestone':
        return Star;
      case 'special':
        return Award;
      default:
        return Trophy;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'streak':
        return 'orange';
      case 'total':
        return 'blue';
      case 'milestone':
        return 'purple';
      case 'special':
        return 'green';
      default:
        return 'blue';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'streak':
        return '连续打卡';
      case 'total':
        return '累计打卡';
      case 'milestone':
        return '里程碑';
      case 'special':
        return '特殊成就';
      default:
        return category;
    }
  };

  const getFilteredAchievements = () => {
    const all = [...unlockedAchievements, ...lockedAchievements];
    if (activeTab === 'unlocked') return unlockedAchievements;
    if (activeTab === 'locked') return lockedAchievements;
    return all;
  };

  const filteredAchievements = getFilteredAchievements();

  const totalCheckIns = unlockedAchievements.length > 0
    ? Math.max(...unlockedAchievements.map(a => a.progress?.current || 0), 0)
    : 0;

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
            成就系统
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            收集徽章，见证你的成长之旅
          </p>
        </div>

        <div className="flex gap-2 bg-white dark:bg-zinc-900 p-1 rounded-xl border border-zinc-200 dark:border-zinc-800">
          {(['all', 'unlocked', 'locked'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-4 py-2 rounded-lg font-medium transition-all duration-200',
                activeTab === tab
                  ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-md'
                  : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-white'
              )}
            >
              {tab === 'all' ? '全部' : tab === 'unlocked' ? '已解锁' : '未解锁'}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl p-6 border border-amber-100 dark:border-amber-800">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          <div className="relative">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
              <Trophy className="w-10 h-10 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 bg-white dark:bg-zinc-900 px-2 py-1 rounded-lg text-xs font-bold text-orange-500 border border-zinc-200 dark:border-zinc-800">
              {totalProgress.unlocked}/{totalProgress.total}
            </div>
          </div>

          <div className="flex-1">
            <h3 className="text-xl font-bold text-zinc-900 dark:text-white mb-1">
              成就进度
            </h3>
            <p className="text-zinc-600 dark:text-zinc-400 mb-3">
              已解锁 {totalProgress.unlocked} 个成就，还有 {totalProgress.locked} 个等待解锁
            </p>
            <div className="h-3 bg-white dark:bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all duration-700"
                style={{ width: `${totalProgress.percentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-4 border border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
              <Flame className="w-5 h-5 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">当前连续</p>
              <p className="text-xl font-bold text-zinc-900 dark:text-white">{currentMaxStreak} 天</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-4 border border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">历史最长</p>
              <p className="text-xl font-bold text-zinc-900 dark:text-white">{longestStreak} 天</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-4 border border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <Star className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">习惯数量</p>
              <p className="text-xl font-bold text-zinc-900 dark:text-white">{habits.length} 个</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-4 border border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">完成率</p>
              <p className="text-xl font-bold text-zinc-900 dark:text-white">{totalProgress.percentage}%</p>
            </div>
          </div>
        </div>
      </div>

      {Object.entries(categorizedAchievements).map(([category, achievements]) => {
        const unlockedInCategory = achievements.filter(a => a.unlockedAt).length;
        const filteredInCategory = achievements.filter(a =>
          activeTab === 'all' ||
          (activeTab === 'unlocked' && a.unlockedAt) ||
          (activeTab === 'locked' && !a.unlockedAt)
        );

        if (filteredInCategory.length === 0) return null;

        const CategoryIcon = getCategoryIcon(category);

        return (
          <div key={category} className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white flex items-center gap-2">
                <CategoryIcon className={cn('w-6 h-6', `text-${getCategoryColor(category)}-500`)} />
                {getCategoryLabel(category)}
              </h2>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">
                {unlockedInCategory}/{achievements.length} 已解锁
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredInCategory.map((achievement, index) => (
                <div
                  key={achievement.id}
                  className="transform transition-all duration-300 hover:-translate-y-1"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <Badge
                    name={achievement.name}
                    description={achievement.description}
                    iconName={achievement.icon}
                    isUnlocked={!!achievement.unlockedAt}
                    unlockedAt={achievement.unlockedAt}
                    progress={achievement.progress}
                    size="lg"
                  />
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {filteredAchievements.length === 0 && (
        <div className="bg-white dark:bg-zinc-900 rounded-2xl p-12 text-center border border-zinc-100 dark:border-zinc-800">
          <Lock className="w-16 h-16 text-zinc-300 dark:text-zinc-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
            没有成就显示
          </h3>
          <p className="text-zinc-500 dark:text-zinc-400">
            {activeTab === 'unlocked'
              ? '还没有解锁任何成就，坚持打卡吧！'
              : '所有成就都已解锁，太厉害了！'}
          </p>
        </div>
      )}

      {activeTab === 'all' && unlockedAchievements.length > 0 && (
        <div className="bg-gradient-to-br from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 rounded-2xl p-6 border border-sky-100 dark:border-sky-800">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-white dark:bg-zinc-900 flex items-center justify-center shadow-sm">
              <Sparkles className="w-6 h-6 text-yellow-500" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-sky-700 dark:text-sky-400 mb-1">
                💪 继续加油！
              </h3>
              <p className="text-sky-600 dark:text-sky-300">
                你已经解锁了 {totalProgress.unlocked} 个成就！
                {totalProgress.locked > 0
                  ? `还有 ${totalProgress.locked} 个成就等待解锁，继续保持你的好习惯吧！`
                  : ' 你已经完成了所有成就，太了不起了！'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Achievements;
