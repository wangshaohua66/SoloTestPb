import React, { useMemo } from 'react';
import { cn } from '../lib/utils';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { useTheme } from '../context/ThemeContext';

ChartJS.register(ArcElement, Tooltip, Legend);

interface CompletionRateChartProps {
  completed: number;
  total: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const CompletionRateChart: React.FC<CompletionRateChartProps> = ({
  completed,
  total,
  className,
  size = 'md',
}) => {
  const { resolvedTheme } = useTheme();

  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const remaining = total - completed;

  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-48 h-48',
  };

  const data = useMemo(() => ({
    labels: ['已完成', '未完成'],
    datasets: [
      {
        data: [completed, remaining],
        backgroundColor: [
          '#0ea5e9',
          resolvedTheme === 'dark' ? '#3f3f46' : '#e4e4e7',
        ],
        borderWidth: 0,
        hoverOffset: 4,
        cutout: '70%',
      },
    ],
  }), [completed, remaining, resolvedTheme]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: resolvedTheme === 'dark' ? '#27272a' : '#ffffff',
        titleColor: resolvedTheme === 'dark' ? '#ffffff' : '#18181b',
        bodyColor: resolvedTheme === 'dark' ? '#d4d4d8' : '#52525b',
        borderColor: resolvedTheme === 'dark' ? '#3f3f46' : '#e4e4e7',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (context: { label: string; parsed: number }) => {
            return `${context.label}: ${context.parsed}`;
          },
        },
      },
    },
  }), [resolvedTheme]);

  return (
    <div className={cn('relative', sizeClasses[size], className)}>
      <Doughnut data={data} options={options} />
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-zinc-900 dark:text-white">
          {percentage}%
        </span>
        <span className="text-xs text-zinc-500 dark:text-zinc-400">
          {completed}/{total}
        </span>
      </div>
    </div>
  );
};
