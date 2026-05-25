import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { useTheme } from '../context/ThemeContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface TrendDataPoint {
  date: string;
  completed: number;
  target: number;
  rate: number;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  className?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({ data, className }) => {
  const { resolvedTheme } = useTheme();

  const chartData = useMemo(() => ({
    labels: data.map(d => {
      const date = new Date(d.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [
      {
        label: '完成数',
        data: data.map(d => d.completed),
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#0ea5e9',
        pointBorderColor: resolvedTheme === 'dark' ? '#18181b' : '#ffffff',
        pointBorderWidth: 2,
      },
      {
        label: '完成率',
        data: data.map(d => d.rate),
        borderColor: '#f97316',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointBackgroundColor: '#f97316',
        yAxisID: 'y1',
      },
    ],
  }), [data, resolvedTheme]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: resolvedTheme === 'dark' ? '#a1a1aa' : '#71717a',
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: resolvedTheme === 'dark' ? '#27272a' : '#ffffff',
        titleColor: resolvedTheme === 'dark' ? '#ffffff' : '#18181b',
        bodyColor: resolvedTheme === 'dark' ? '#d4d4d8' : '#52525b',
        borderColor: resolvedTheme === 'dark' ? '#3f3f46' : '#e4e4e7',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: (context: { dataset: { label?: string }; parsed: { y: number } }) => {
            return `${context.dataset.label}: ${context.parsed.y}${context.dataset.label === '完成率' ? '%' : ''}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: resolvedTheme === 'dark' ? '#27272a' : '#f4f4f5',
          drawBorder: false,
        },
        ticks: {
          color: resolvedTheme === 'dark' ? '#71717a' : '#a1a1aa',
          maxRotation: 0,
          autoSkip: true,
          maxTicksLimit: 10,
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        beginAtZero: true,
        grid: {
          color: resolvedTheme === 'dark' ? '#27272a' : '#f4f4f5',
          drawBorder: false,
        },
        ticks: {
          color: resolvedTheme === 'dark' ? '#71717a' : '#a1a1aa',
          precision: 0,
        },
        title: {
          display: true,
          text: '完成数量',
          color: resolvedTheme === 'dark' ? '#71717a' : '#a1a1aa',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        beginAtZero: true,
        max: 100,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: resolvedTheme === 'dark' ? '#71717a' : '#a1a1aa',
          callback: (value: number | string) => `${value}%`,
        },
        title: {
          display: true,
          text: '完成率',
          color: resolvedTheme === 'dark' ? '#71717a' : '#a1a1aa',
        },
      },
    },
  }), [resolvedTheme]);

  return (
    <div className={className} style={{ height: '300px' }}>
      <Line data={chartData} options={options} />
    </div>
  );
};
