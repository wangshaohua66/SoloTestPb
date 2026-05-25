import React, { useState } from 'react';
import { Check, Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';
import { useReminder } from '../hooks/useReminder';
import { useToast } from './Toast';
import type { Achievement } from '../types';

interface CheckInButtonProps {
  habitId: string;
  isCheckedIn: boolean;
  color: string;
  onCheckIn: () => { success: boolean; isDuplicate: boolean; newAchievements: Achievement[] };
  onUncheck?: () => void;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}

export const CheckInButton: React.FC<CheckInButtonProps> = ({
  habitId,
  isCheckedIn,
  color,
  onCheckIn,
  onUncheck,
  size = 'md',
  disabled = false,
  className,
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [showSparkles, setShowSparkles] = useState(false);
  const { sendAchievementNotification } = useReminder();
  const { showToast } = useToast();

  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-12 h-12',
    lg: 'w-14 h-14',
  };

  const iconSizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-7 h-7',
  };

  const handleClick = async () => {
    if (disabled || isAnimating) return;

    if (isCheckedIn) {
      onUncheck?.();
      return;
    }

    setIsAnimating(true);

    const result = onCheckIn();

    if (result.success) {
      setShowSparkles(true);

      result.newAchievements.forEach(achievement => {
        setTimeout(() => {
          sendAchievementNotification(achievement.name);
        }, 1000);
      });

      setTimeout(() => {
        setShowSparkles(false);
        setIsAnimating(false);
      }, 1500);
    } else if (result.isDuplicate) {
      setIsAnimating(false);
      showToast('今天已经打过卡啦，明天继续加油！', 'warning', 2500);
    } else {
      setIsAnimating(false);
      showToast('打卡失败，请稍后重试', 'error', 3000);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isAnimating}
      className={cn(
        'relative rounded-full flex items-center justify-center transition-all duration-300',
        'font-semibold border-2',
        isCheckedIn
          ? 'text-white border-transparent shadow-lg'
          : 'border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 hover:border-transparent hover:shadow-md',
        isAnimating && 'scale-90',
        !isCheckedIn && !disabled && 'hover:scale-110 active:scale-95',
        disabled && 'opacity-50 cursor-not-allowed',
        sizeClasses[size],
        className
      )}
      style={{
        backgroundColor: isCheckedIn ? color : undefined,
        borderColor: isCheckedIn ? color : undefined,
      }}
      aria-label={isCheckedIn ? '取消打卡' : '打卡'}
    >
      {isCheckedIn ? (
        <Check className={cn(iconSizeClasses[size], 'text-white')} />
      ) : (
        <span
          className={cn(iconSizeClasses[size], 'rounded-full border-2 border-current')}
          style={{ color }}
        />
      )}

      {showSparkles && (
        <>
          <Sparkles
            className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <Sparkles
            className="absolute -top-1 -left-3 w-5 h-5 text-cyan-400 animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <Sparkles
            className="absolute -bottom-2 -right-1 w-4 h-4 text-pink-400 animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </>
      )}
    </button>
  );
};
