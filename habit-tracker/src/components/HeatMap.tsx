import React, { useMemo, useState } from 'react';
import { cn } from '../lib/utils';
import { parseISODate, formatDate } from '../utils/dateUtils';

interface HeatMapData {
  date: string;
  count: number;
}

interface HeatMapProps {
  data: HeatMapData[];
  className?: string;
}

export const HeatMap: React.FC<HeatMapProps> = ({ data, className }) => {
  const weeks = useMemo(() => {
    const weekMap = new Map<number, HeatMapData[]>();
    data.forEach((item, index) => {
      const weekNum = Math.floor(index / 7);
      if (!weekMap.has(weekNum)) {
        weekMap.set(weekNum, []);
      }
      weekMap.get(weekNum)?.push(item);
    });
    return Array.from(weekMap.values());
  }, [data]);

  const getIntensity = (count: number): string => {
    if (count === 0) return 'bg-zinc-100 dark:bg-zinc-800';
    if (count === 1) return 'bg-sky-200 dark:bg-sky-900/50';
    if (count === 2) return 'bg-sky-300 dark:bg-sky-800';
    if (count === 3) return 'bg-sky-400 dark:bg-sky-600';
    return 'bg-sky-500 dark:bg-sky-500';
  };

  const monthLabels = useMemo(() => {
    const months: { label: string; weekIndex: number }[] = [];
    let lastMonth = -1;

    weeks.forEach((week, weekIndex) => {
      if (week.length > 0) {
        const firstDay = parseISODate(week[0].date);
        const month = firstDay.getMonth();
        if (month !== lastMonth) {
          months.push({
            label: firstDay.toLocaleDateString('zh-CN', { month: 'short' }),
            weekIndex,
          });
          lastMonth = month;
        }
      }
    });

    return months;
  }, [weeks]);

  const dayLabels = ['一', '', '三', '', '五', '', '日'];

  const [hoveredItem, setHoveredItem] = useState<HeatMapData | null>(null);

  return (
    <div className={cn('w-full overflow-x-auto', className)}>
      <div className="min-w-[800px] p-4">
        <div className="flex mb-2">
          <div className="w-8" />
          {monthLabels.map((month, i) => (
            <div
              key={i}
              className="text-xs text-zinc-500 dark:text-zinc-400 flex-1 text-center"
              style={{ marginLeft: i === 0 ? `${month.weekIndex * 14}px` : undefined }}
            >
              {month.label}
            </div>
          ))}
        </div>

        <div className="flex gap-1">
          <div className="flex flex-col gap-1 mr-2">
            {dayLabels.map((day, i) => (
              <div
                key={i}
                className="h-3 text-xs text-zinc-500 dark:text-zinc-400 flex items-center justify-end pr-1"
                style={{ visibility: day ? 'visible' : 'hidden' }}
              >
                {day}
              </div>
            ))}
          </div>

          <div className="flex gap-1">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {week.map((item, dayIndex) => (
                  <div
                    key={`${weekIndex}-${dayIndex}`}
                    className={cn(
                      'w-3 h-3 rounded-sm cursor-pointer transition-all duration-200',
                      getIntensity(item.count),
                      'hover:ring-2 hover:ring-sky-400 hover:ring-offset-1 dark:hover:ring-offset-zinc-900'
                    )}
                    onMouseEnter={() => setHoveredItem(item)}
                    onMouseLeave={() => setHoveredItem(null)}
                    title={`${formatDate(item.date)}: ${item.count} 次打卡`}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 mt-4 text-xs text-zinc-500 dark:text-zinc-400">
          <span>少</span>
          <div className="flex gap-1">
            {[0, 1, 2, 3, 4].map(level => (
              <div
                key={level}
                className={cn('w-3 h-3 rounded-sm', getIntensity(level))}
              />
            ))}
          </div>
          <span>多</span>
        </div>

        {hoveredItem && (
          <div className="fixed z-50 px-3 py-2 bg-zinc-900 text-white text-xs rounded-lg shadow-xl pointer-events-none animate-fade-in">
            <div className="font-medium">{formatDate(hoveredItem.date)}</div>
            <div>{hoveredItem.count} 次打卡</div>
          </div>
        )}
      </div>
    </div>
  );
};
