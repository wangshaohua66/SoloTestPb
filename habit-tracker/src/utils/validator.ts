import type { Habit, CheckIn, UserSettings, ValidationResult, Frequency } from '../types';
import { isValidTimezone, getLocalTimezone, getTodayISO } from './dateUtils';
import { logger } from './logger';

const VALID_FREQUENCIES: Frequency[] = ['daily', 'weekly'];
const ISO_DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;
const TIME_REGEX = /^\d{2}:\d{2}$/;
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const generateId = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export const validateId = (id: string): ValidationResult => {
  const errors: string[] = [];
  if (!id || typeof id !== 'string') {
    errors.push('ID 不能为空');
  } else if (!UUID_REGEX.test(id)) {
    errors.push(`ID 格式无效: ${id}`);
  }
  return { valid: errors.length === 0, errors };
};

export const validateHabit = (habit: Partial<Habit>): ValidationResult => {
  const errors: string[] = [];

  if (habit.id !== undefined) {
    const idResult = validateId(habit.id);
    if (!idResult.valid) {
      errors.push(...idResult.errors);
    }
  }

  if (!habit.name || typeof habit.name !== 'string') {
    errors.push('习惯名称不能为空');
  } else if (habit.name.trim().length === 0) {
    errors.push('习惯名称不能为空白字符');
  } else if (habit.name.length > 50) {
    errors.push('习惯名称不能超过50个字符');
  }

  if (habit.frequency !== undefined && !VALID_FREQUENCIES.includes(habit.frequency)) {
    errors.push(`频率值无效，必须是以下值之一: ${VALID_FREQUENCIES.join(', ')}`);
  }

  if (habit.targetCount !== undefined) {
    if (typeof habit.targetCount !== 'number' || habit.targetCount < 1) {
      errors.push('目标次数必须大于等于1');
    } else if (habit.frequency === 'daily' && habit.targetCount > 1) {
      errors.push('每日习惯的目标次数必须为1');
    } else if (habit.frequency === 'weekly' && habit.targetCount > 7) {
      errors.push('每周习惯的目标次数不能超过7');
    }
  }

  if (habit.color !== undefined && !/^#[0-9A-Fa-f]{6}$/.test(habit.color)) {
    errors.push(`颜色格式无效: ${habit.color}，必须是十六进制格式`);
  }

  if (habit.createdAt !== undefined && !ISO_DATE_REGEX.test(habit.createdAt)) {
    errors.push(`创建日期格式无效: ${habit.createdAt}，必须是 YYYY-MM-DD 格式`);
  }

  if (habit.timezone !== undefined && !isValidTimezone(habit.timezone)) {
    errors.push(`时区无效: ${habit.timezone}`);
  }

  if (habit.description !== undefined && habit.description.length > 200) {
    errors.push('描述不能超过200个字符');
  }

  return { valid: errors.length === 0, errors };
};

export const validateCheckIn = (checkIn: Partial<CheckIn>): ValidationResult => {
  const errors: string[] = [];

  if (checkIn.id !== undefined) {
    const idResult = validateId(checkIn.id);
    if (!idResult.valid) {
      errors.push(...idResult.errors);
    }
  }

  if (!checkIn.habitId) {
    errors.push('习惯ID不能为空');
  } else {
    const habitIdResult = validateId(checkIn.habitId);
    if (!habitIdResult.valid) {
      errors.push(...habitIdResult.errors.map(e => `habitId: ${e}`));
    }
  }

  if (!checkIn.date || !ISO_DATE_REGEX.test(checkIn.date)) {
    errors.push(`打卡日期格式无效: ${checkIn.date}，必须是 YYYY-MM-DD 格式`);
  }

  if (!checkIn.timestamp || isNaN(Date.parse(checkIn.timestamp))) {
    errors.push(`时间戳格式无效: ${checkIn.timestamp}`);
  }

  if (checkIn.timezone !== undefined && !isValidTimezone(checkIn.timezone)) {
    errors.push(`时区无效: ${checkIn.timezone}`);
  }

  if (checkIn.note !== undefined && checkIn.note.length > 500) {
    errors.push('备注不能超过500个字符');
  }

  return { valid: errors.length === 0, errors };
};

export const validateSettings = (settings: Partial<UserSettings>): ValidationResult => {
  const errors: string[] = [];

  if (settings.theme !== undefined && !['light', 'dark', 'system'].includes(settings.theme)) {
    errors.push(`主题模式无效: ${settings.theme}`);
  }

  if (settings.reminder !== undefined) {
    if (typeof settings.reminder.enabled !== 'boolean') {
      errors.push('提醒开关必须是布尔值');
    }
    if (settings.reminder.defaultTime !== undefined && !TIME_REGEX.test(settings.reminder.defaultTime)) {
      errors.push(`默认提醒时间格式无效: ${settings.reminder.defaultTime}，必须是 HH:MM 格式`);
    }
    if (typeof settings.reminder.smartReminder !== 'boolean') {
      errors.push('智能提醒开关必须是布尔值');
    }
  }

  if (settings.exportFormat !== undefined && !['json', 'csv'].includes(settings.exportFormat)) {
    errors.push(`导出格式无效: ${settings.exportFormat}`);
  }

  if (settings.activeHours !== undefined) {
    if (!Array.isArray(settings.activeHours)) {
      errors.push('活跃时段必须是数组');
    } else if (settings.activeHours.length !== 24) {
      errors.push('活跃时段数组必须包含24个小时的数据');
    } else if (settings.activeHours.some(h => typeof h !== 'number' || h < 0)) {
      errors.push('活跃时段数据必须是非负整数');
    }
  }

  return { valid: errors.length === 0, errors };
};

export const validateDataConsistency = (
  habits: Habit[],
  checkIns: CheckIn[]
): ValidationResult => {
  const errors: string[] = [];
  const habitIds = new Set(habits.map(h => h.id));

  for (const checkIn of checkIns) {
    if (!habitIds.has(checkIn.habitId)) {
      errors.push(`打卡记录引用了不存在的习惯ID: ${checkIn.habitId}`);
    }
  }

  const habitNameSet = new Set<string>();
  for (const habit of habits) {
    if (habitNameSet.has(habit.name.toLowerCase())) {
      errors.push(`存在重复的习惯名称: ${habit.name}`);
    }
    habitNameSet.add(habit.name.toLowerCase());
  }

  const checkInKeySet = new Set<string>();
  for (const checkIn of checkIns) {
    const key = `${checkIn.habitId}-${checkIn.date}`;
    if (checkInKeySet.has(key)) {
      errors.push(`存在重复的打卡记录: 习惯 ${checkIn.habitId} 在 ${checkIn.date}`);
    }
    checkInKeySet.add(key);
  }

  return { valid: errors.length === 0, errors };
};

export const validateAndRepairData = <T>(
  data: T[],
  validator: (item: Partial<T>) => ValidationResult,
  repairFn: (item: Partial<T>) => T | null
): { validData: T[]; repairedCount: number; removedCount: number } => {
  const validData: T[] = [];
  let repairedCount = 0;
  let removedCount = 0;

  for (const item of data) {
    const result = validator(item as Partial<T>);
    if (result.valid) {
      validData.push(item);
    } else {
      logger.warn(`Invalid data detected, attempting repair`, { errors: result.errors, item });
      const repaired = repairFn(item as Partial<T>);
      if (repaired) {
        validData.push(repaired);
        repairedCount++;
        logger.info(`Data repaired successfully`, { item });
      } else {
        removedCount++;
        logger.warn(`Data removed due to invalid state`, { item });
      }
    }
  }

  return { validData, repairedCount, removedCount };
};

export const validateAndRepairAllData = (
  habits: Habit[],
  checkIns: CheckIn[],
  settings: UserSettings
): {
  repairedHabits: Habit[];
  repairedCheckIns: CheckIn[];
  repairedSettings: Partial<UserSettings> | null;
  messages: string[];
} => {
  const messages: string[] = [];
  const habitsResult = validateAndRepairData<Habit>(habits, validateHabit, (partial) => {
    const timezone = getLocalTimezone();
    return {
      id: partial.id || generateId(),
      name: partial.name?.trim() || '未命名习惯',
      description: partial.description || '',
      icon: partial.icon || 'Target',
      color: partial.color || '#0ea5e9',
      frequency: (partial.frequency as Frequency) || 'daily',
      targetCount: partial.targetCount || 1,
      createdAt: partial.createdAt || getTodayISO(timezone),
      timezone: partial.timezone || timezone,
    };
  });

  const checkInsResult = validateAndRepairData<CheckIn>(checkIns, validateCheckIn, (partial) => {
    const timezone = getLocalTimezone();
    const timestamp = partial.timestamp || new Date().toISOString();
    return {
      id: partial.id || generateId(),
      habitId: partial.habitId || generateId(),
      date: partial.date || getTodayISO(timezone),
      timestamp,
      timezone: partial.timezone || timezone,
      note: partial.note,
    };
  });

  const settingsResult = validateSettings(settings);
  let repairedSettings: Partial<UserSettings> | null = null;

  if (!settingsResult.valid) {
    repairedSettings = {
      theme: settings.theme || 'system',
      remindersEnabled: settings.remindersEnabled ?? false,
      defaultReminderTime: settings.defaultReminderTime || '09:00',
      reminder: {
        enabled: settings.reminder?.enabled ?? false,
        defaultTime: settings.reminder?.defaultTime || '09:00',
        smartReminder: settings.reminder?.smartReminder ?? true,
      },
      exportFormat: settings.exportFormat || 'json',
      activeHours: settings.activeHours || new Array(24).fill(0),
    };
    messages.push('设置数据已修复');
  }

  if (habitsResult.repairedCount > 0) {
    messages.push(`修复了 ${habitsResult.repairedCount} 个习惯数据`);
  }
  if (habitsResult.removedCount > 0) {
    messages.push(`移除了 ${habitsResult.removedCount} 个无法修复的习惯数据`);
  }
  if (checkInsResult.repairedCount > 0) {
    messages.push(`修复了 ${checkInsResult.repairedCount} 条打卡记录`);
  }
  if (checkInsResult.removedCount > 0) {
    messages.push(`移除了 ${checkInsResult.removedCount} 条无法修复的打卡记录`);
  }

  return {
    repairedHabits: habitsResult.validData,
    repairedCheckIns: checkInsResult.validData,
    repairedSettings,
    messages,
  };
};
