import React from 'react';
import * as Icons from 'lucide-react';
import { cn } from '../lib/utils';

interface BadgeProps {
  name: string;
  description: string;
  iconName: string;
  isUnlocked: boolean;
  progress?: number;
  percentage?: number;
  unlockedAt?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  name,
  description,
  iconName,
  isUnlocked,
  progress,
  percentage,
  unlockedAt,
  size = 'md',
  className,
}) => {
  const IconComponent = (Icons as unknown as Record<string, React.FC<{ className?: string }>>)[iconName] || Icons.Star;

  const sizeClasses = {
    sm: {
      container: 'p-3',
      icon: 'w-5 h-5',
      name: 'text-sm',
    },
    md: {
      container: 'p-4',
      icon: 'w-8 h-8',
      name: 'text-base',
    },
    lg: {
      container: 'p-6',
      icon: 'w-12 h-12',
      name: 'text-lg',
    },
  };

  return (
    <div className={cn(
      'relative rounded-2xl border-2 transition-all duration-300',
      isUnlocked
        ? 'bg-gradient-to-br from-sky-50 to-cyan-50 dark:from-sky-900/20 dark:to-cyan-900/20 border-sky-200 dark:border-sky-700'
        : 'bg-zinc-50 dark:bg-zinc-800/50 border-zinc-200 dark:border-zinc-700',
      sizeClasses[size].container,
      className
    )}>
      <div className="flex flex-col items-center text-center">
        <div className={cn(
          'rounded-full mb-3 transition-all duration-300',
          isUnlocked
            ? 'bg-gradient-to-br from-sky-400 to-cyan-500 text-white p-3 shadow-lg shadow-sky-500/25'
            : 'bg-zinc-200 dark:bg-zinc-700 text-zinc-400 p-3',
          !isUnlocked && 'grayscale opacity-50'
        )}>
          <IconComponent className={sizeClasses[size].icon} />
        </div>

        <h3 className={cn(
          'font-bold',
          isUnlocked ? 'text-zinc-900 dark:text-white' : 'text-zinc-400',
          sizeClasses[size].name
        )}>
          {name}
        </h3>

        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1 line-clamp-2">
          {description}
        </p>

        {!isUnlocked && percentage !== undefined && (
          <div className="w-full mt-3">
            <div className="h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-sky-400 to-cyan-500 rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              />
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              {progress ?? 0} / {percentage > 0 ? Math.ceil((progress ?? 0) / percentage * 100) : '?'}
            </p>
          </div>
        )}

        {isUnlocked && unlockedAt && (
          <p className="text-xs text-sky-500 mt-2 font-medium">
            解锁于 {new Date(unlockedAt).toLocaleDateString('zh-CN')}
          </p>
        )}
      </div>

      {isUnlocked && (
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer pointer-events-none" />
      )}
    </div>
  );
};
