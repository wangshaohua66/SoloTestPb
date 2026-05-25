import React, { useState } from 'react';
import { Flame, Edit2, Trash2, MoreVertical, Calendar, Target } from 'lucide-react';
import { cn } from '../lib/utils';
import { CheckInButton } from './CheckInButton';
import { useHabits } from '../hooks/useHabits';
import { useCheckIns } from '../hooks/useCheckIns';
import type { Habit, HabitStats } from '../types';
import { getMotivationalMessage } from '../utils/achievementCalculator';

interface HabitCardProps {
  habit: Habit;
  stats: HabitStats | null;
  isCheckedInToday: boolean;
  weeklyCount: number;
  onEdit?: () => void;
  onDelete?: () => void;
  className?: string;
}

export const HabitCard: React.FC<HabitCardProps> = ({
  habit,
  stats,
  isCheckedInToday,
  weeklyCount,
  onEdit,
  onDelete,
  className,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const { deleteHabit } = useHabits();
  const { checkIn, uncheck } = useCheckIns();

  const motivationalMessage = stats ? getMotivationalMessage(stats, habit.name) : null;

  const handleDelete = () => {
    if (window.confirm(`确定要删除习惯「${habit.name}」吗？相关的打卡记录也会被删除。`)) {
      deleteHabit(habit.id);
    }
    setShowMenu(false);
  };

  const frequencyText = habit.frequency === 'daily'
    ? '每日'
    : `每周 ${habit.targetCount} 次`;

  const weeklyProgress = habit.frequency === 'daily'
    ? { current: weeklyCount, target: 7 }
    : { current: weeklyCount, target: habit.targetCount };

  const weeklyPercentage = Math.min(100, Math.round((weeklyProgress.current / weeklyProgress.target) * 100));

  return (
    <div className={cn(
      'group relative bg-white dark:bg-zinc-900 rounded-2xl p-5',
      'border border-zinc-100 dark:border-zinc-800',
      'shadow-sm hover:shadow-lg transition-all duration-300',
      'animate-fade-in',
      className
    )}>
      <div className="flex items-start gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${habit.color}15` }}
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-lg"
            style={{ backgroundColor: habit.color, color: 'white' }}
          >
            {habit.name.charAt(0)}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-bold text-zinc-900 dark:text-white text-lg">
                {habit.name}
              </h3>
              <div className="flex items-center gap-3 mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {frequencyText}
                </span>
                {stats && stats.currentStreak > 0 && (
                  <span className="flex items-center gap-1 text-orange-500 font-medium">
                    <Flame className="w-4 h-4" />
                    {stats.currentStreak} 天
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <CheckInButton
                habitId={habit.id}
                isCheckedIn={isCheckedInToday}
                color={habit.color}
                onCheckIn={() => checkIn(habit.id)}
                onUncheck={() => uncheck(habit.id)}
              />

              <div className="relative">
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-2 rounded-xl hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors text-zinc-400 opacity-0 group-hover:opacity-100"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>

                {showMenu && (
                  <div className="absolute right-0 top-full mt-2 bg-white dark:bg-zinc-800 rounded-xl shadow-lg border border-zinc-200 dark:border-zinc-700 py-2 min-w-32 z-10 animate-fade-in">
                    <button
                      onClick={() => { onEdit?.(); setShowMenu(false); }}
                      className="w-full px-4 py-2 text-left hover:bg-zinc-100 dark:hover:bg-zinc-700 flex items-center gap-2 text-zinc-700 dark:text-zinc-300"
                    >
                      <Edit2 className="w-4 h-4" />
                      编辑
                    </button>
                    <button
                      onClick={handleDelete}
                      className="w-full px-4 py-2 text-left hover:bg-rose-50 dark:hover:bg-rose-900/20 flex items-center gap-2 text-rose-500"
                    >
                      <Trash2 className="w-4 h-4" />
                      删除
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {motivationalMessage && (
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              {motivationalMessage.message}
            </p>
          )}

          {stats && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-zinc-500 dark:text-zinc-400 flex items-center gap-1">
                  <Target className="w-4 h-4" />
                  本周进度
                </span>
                <span className="font-medium text-zinc-700 dark:text-zinc-300">
                  {weeklyProgress.current} / {weeklyProgress.target}
                </span>
              </div>
              <div className="h-2 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${weeklyPercentage}%`,
                    backgroundColor: habit.color,
                  }}
                />
              </div>
            </div>
          )}

          {stats && (
            <div className="mt-4 flex gap-4 text-xs">
              <div>
                <span className="text-zinc-400">完成率</span>
                <p className="font-bold text-zinc-900 dark:text-white">{stats.completionRate}%</p>
              </div>
              <div>
                <span className="text-zinc-400">总打卡</span>
                <p className="font-bold text-zinc-900 dark:text-white">{stats.totalCheckIns} 次</p>
              </div>
              <div>
                <span className="text-zinc-400">最长连续</span>
                <p className="font-bold text-zinc-900 dark:text-white">{stats.longestStreak} 天</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
