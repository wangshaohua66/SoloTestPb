import type { Habit, CheckIn, ExportFormat } from '../types';
import { logger } from './logger';
import { formatDate } from './dateUtils';

export const exportToJSON = (
  habits: Habit[],
  checkIns: CheckIn[],
  options: { includeAchievements?: boolean; includeSettings?: boolean } = {}
): string => {
  const data: Record<string, unknown> = {
    habits,
    checkIns,
    exportedAt: new Date().toISOString(),
    version: '1.0',
  };

  if (options.includeAchievements) {
    data.achievements = [];
  }
  if (options.includeSettings) {
    data.settings = {};
  }

  return JSON.stringify(data, null, 2);
};

export const exportToCSV = (habits: Habit[], checkIns: CheckIn[]): string => {
  const habitMap = new Map(habits.map(h => [h.id, h]));

  const headers = ['日期', '习惯名称', '习惯频率', '打卡时间', '时区', '备注'];
  const rows = checkIns.map(checkIn => {
    const habit = habitMap.get(checkIn.habitId);
    return [
      checkIn.date,
      habit?.name || '未知习惯',
      habit?.frequency || '',
      new Date(checkIn.timestamp).toLocaleString('zh-CN'),
      checkIn.timezone,
      checkIn.note || '',
    ];
  });

  const csvContent = [
    headers.join(','),
    ...rows.map(row =>
      row.map(cell => {
        const escaped = String(cell).replace(/"/g, '""');
        return `"${escaped}"`;
      }).join(',')
    ),
  ].join('\n');

  return '\uFEFF' + csvContent;
};

export const exportData = (
  format: ExportFormat,
  habits: Habit[],
  checkIns: CheckIn[],
  _achievements?: unknown
): { content: string; filename: string; mimeType: string } => {
  const timestamp = new Date().toISOString().split('T')[0];
  let content: string;
  let filename: string;
  let mimeType: string;

  switch (format) {
    case 'json':
      content = exportToJSON(habits, checkIns);
      filename = `habit-tracker-${timestamp}.json`;
      mimeType = 'application/json';
      break;
    case 'csv':
      content = exportToCSV(habits, checkIns);
      filename = `habit-tracker-${timestamp}.csv`;
      mimeType = 'text/csv;charset=utf-8';
      break;
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }

  return { content, filename, mimeType };
};

export const downloadFile = (content: string, filename: string, mimeType: string): void => {
  try {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    logger.info('File downloaded successfully', { filename, mimeType });
  } catch (error) {
    logger.error('Failed to download file', error as Error, { filename });
    throw error;
  }
};

export const readFileAsText = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
};

export const parseImportData = (content: string): {
  habits: Habit[];
  checkIns: CheckIn[];
  settings?: unknown;
} => {
  try {
    const parsed = JSON.parse(content);
    return {
      habits: Array.isArray(parsed.habits) ? parsed.habits : [],
      checkIns: Array.isArray(parsed.checkIns) ? parsed.checkIns : [],
      settings: parsed.settings,
    };
  } catch (error) {
    logger.error('Failed to parse import data', error as Error);
    throw new Error('数据格式错误，请确保是有效的JSON文件');
  }
};

export const generateBackupSummary = (habits: Habit[], checkIns: CheckIn[]): string => {
  const uniqueDates = new Set(checkIns.map(c => c.date));
  const totalDays = uniqueDates.size;
  const earliestDate = checkIns.length > 0
    ? formatDate(checkIns.reduce((a, b) => (a.date < b.date ? a : b)).date)
    : '无数据';
  const latestDate = checkIns.length > 0
    ? formatDate(checkIns.reduce((a, b) => (a.date > b.date ? a : b)).date)
    : '无数据';

  return `数据备份摘要
==========
习惯数量: ${habits.length}
打卡记录: ${checkIns.length} 条
覆盖天数: ${totalDays} 天
最早记录: ${earliestDate}
最近记录: ${latestDate}
导出时间: ${new Date().toLocaleString('zh-CN')}`;
};
