import React from 'react';
import { Flame, Target, Calendar, Trophy, TrendingUp, Sparkles } from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { HabitCard } from '../components/HabitCard';
import { CompletionRateChart } from '../components/CompletionRateChart';
import { Badge } from '../components/Badge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useHabits } from '../hooks/useHabits';
import { useCheckIns } from '../hooks/useCheckIns';
import { useAchievements } from '../hooks/useAchievements';
import { useAppStore } from '../store/useAppStore';

const Dashboard: React.FC = () => {
  const { isLoading, isInitialized } = useAppStore();
  const { habitsWithStats, todayProgress, currentMaxStreak, longestStreak, habits } = useHabits();
  const { checkIns, heatmapData, trendData } = useCheckIns();
  const { recentAchievements, totalProgress } = useAchievements();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 6) return '夜深了';
    if (hour < 12) return '早上好';
    if (hour < 18) return '下午好';
    return '晚上好';
  };

  const thisWeekCheckIns = checkIns.filter(c => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return new Date(c.date) >= weekAgo;
  }).length;

  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white flex items-center gap-3">
            {getGreeting()}！
            <Sparkles className="w-8 h-8 text-yellow-500 animate-pulse" />
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 mt-2">
            {habits.length === 0
              ? '开始创建你的第一个习惯吧！'
              : todayProgress.completed === todayProgress.total && todayProgress.total > 0
              ? '🎉 太棒了！今天的任务全部完成！'
              : `还有 ${todayProgress.total - todayProgress.completed} 个习惯等待完成`}
          </p>
        </div>

        <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 rounded-2xl border border-sky-100 dark:border-sky-800">
          <CompletionRateChart
            completed={todayProgress.completed}
            total={todayProgress.total}
            size="md"
          />
          <div>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">今日完成</p>
            <p className="text-2xl font-bold text-zinc-900 dark:text-white">
              {todayProgress.percentage}%
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="当前连续"
          value={`${currentMaxStreak} 天`}
          icon={Flame}
          color="orange"
        />
        <StatsCard
          title="历史最长"
          value={`${longestStreak} 天`}
          icon={Trophy}
          color="purple"
        />
        <StatsCard
          title="本周打卡"
          value={`${thisWeekCheckIns} 次`}
          icon={Calendar}
          color="green"
        />
        <StatsCard
          title="成就进度"
          value={`${totalProgress.unlocked}/${totalProgress.total}`}
          icon={TrendingUp}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
              今日习惯
            </h2>
            <span className="text-sm text-zinc-500 dark:text-zinc-400">
              {habits.length} 个习惯
            </span>
          </div>

          {habitsWithStats.length === 0 ? (
            <div className="bg-white dark:bg-zinc-900 rounded-2xl p-12 text-center border border-zinc-100 dark:border-zinc-800">
              <Target className="w-16 h-16 text-zinc-300 dark:text-zinc-700 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
                还没有习惯
              </h3>
              <p className="text-zinc-500 dark:text-zinc-400">
                点击「习惯」页面创建你的第一个习惯吧
              </p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
              {habitsWithStats.map((item, index) => (
                <div key={item.habit.id} style={{ animationDelay: `${index * 100}ms` }}>
                  <HabitCard
                    habit={item.habit}
                    stats={item.stats}
                    isCheckedInToday={item.isCheckedInToday}
                    weeklyCount={item.weeklyCount}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-zinc-900 rounded-2xl p-6 border border-zinc-100 dark:border-zinc-800">
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              最近成就
            </h3>

            {recentAchievements.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-zinc-500 dark:text-zinc-400">
                  还没有解锁成就
                </p>
                <p className="text-sm text-zinc-400 dark:text-zinc-500 mt-1">
                  坚持打卡解锁更多成就
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentAchievements.slice(0, 3).map(achievement => (
                  <Badge
                    key={achievement.id}
                    name={achievement.name}
                    description={achievement.description}
                    iconName={achievement.icon}
                    isUnlocked={true}
                    unlockedAt={achievement.unlockedAt}
                    size="sm"
                  />
                ))}
              </div>
            )}
          </div>

          <div className="bg-gradient-to-br from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 rounded-2xl p-6 border border-sky-100 dark:border-sky-800">
            <h3 className="text-lg font-bold text-sky-700 dark:text-sky-400 mb-2">
              💡 今日提示
            </h3>
            <p className="text-sky-600 dark:text-sky-300 text-sm leading-relaxed">
              {currentMaxStreak === 0
                ? '好习惯的养成从第一次打卡开始，现在就行动起来吧！'
                : currentMaxStreak < 7
                ? `你已经坚持了 ${currentMaxStreak} 天，继续保持，一周成就就在眼前！`
                : `太棒了！你已经连续 ${currentMaxStreak} 天坚持打卡，你的自律值得称赞！`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
