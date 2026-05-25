import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../lib/utils';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'orange' | 'purple';
  className?: string;
}

const colorClasses = {
  blue: 'bg-sky-500/10 text-sky-500',
  green: 'bg-emerald-500/10 text-emerald-500',
  orange: 'bg-orange-500/10 text-orange-500',
  purple: 'bg-purple-500/10 text-purple-500',
};

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  color = 'blue',
  className,
}) => {
  return (
    <div className={cn(
      'bg-white dark:bg-zinc-900 rounded-2xl p-6 shadow-sm border border-zinc-100 dark:border-zinc-800',
      'hover:shadow-md transition-all duration-300',
      'animate-fade-in',
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 font-medium">
            {title}
          </p>
          <p className="text-3xl font-bold text-zinc-900 dark:text-white mt-2">
            {value}
          </p>
          {trend && (
            <div className={cn(
              'flex items-center gap-1 mt-2 text-sm font-medium',
              trend.isPositive ? 'text-emerald-500' : 'text-rose-500'
            )}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{Math.abs(trend.value)}%</span>
              <span className="text-zinc-400 ml-1">较上周</span>
            </div>
          )}
        </div>
        <div className={cn(
          'p-3 rounded-xl',
          colorClasses[color]
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};
