import type { Habit, CheckIn, SyncConflict } from '../types';
import { logger } from './logger';
import { generateId, validateHabit, validateCheckIn, validateAndRepairData } from './validator';
import { getLocalTimezone, getTodayISO } from './dateUtils';

class SyncManager {
  private conflicts: SyncConflict[] = [];

  constructor() {
    this.loadConflicts();
  }

  private loadConflicts(): void {
    try {
      const stored = localStorage.getItem('habit_tracker_conflicts');
      if (stored) {
        this.conflicts = JSON.parse(stored);
      }
    } catch (error) {
      logger.warn('Failed to load sync conflicts', { error });
      this.conflicts = [];
    }
  }

  private saveConflicts(): void {
    try {
      localStorage.setItem('habit_tracker_conflicts', JSON.stringify(this.conflicts));
    } catch (error) {
      logger.error('Failed to save sync conflicts', error as Error);
    }
  }

  private addConflict(
    type: SyncConflict['type'],
    localData: unknown,
    remoteData: unknown
  ): SyncConflict {
    const conflict: SyncConflict = {
      id: generateId(),
      type,
      localData,
      remoteData,
      resolved: false,
      timestamp: new Date().toISOString(),
    };
    this.conflicts.push(conflict);
    this.saveConflicts();
    return conflict;
  }

  resolveConflict(conflictId: string, choice: 'local' | 'remote'): boolean {
    const conflict = this.conflicts.find(c => c.id === conflictId);
    if (!conflict) {
      logger.warn('Conflict not found for resolution', { conflictId });
      return false;
    }
    conflict.resolved = true;
    this.saveConflicts();
    logger.info('Conflict resolved', { conflictId, choice });
    return true;
  }

  getUnresolvedConflicts(): SyncConflict[] {
    return this.conflicts.filter(c => !c.resolved);
  }

  getAllConflicts(): SyncConflict[] {
    return [...this.conflicts];
  }

  clearResolvedConflicts(): void {
    this.conflicts = this.conflicts.filter(c => !c.resolved);
    this.saveConflicts();
  }

  mergeHabits(localHabits: Habit[], remoteHabits: Habit[]): {
    merged: Habit[];
    data: Habit[];
    conflicts: SyncConflict[];
    added: number;
    updated: number;
  } {
    const merged = new Map<string, Habit>();
    const conflicts: SyncConflict[] = [];
    let added = 0;
    let updated = 0;

    localHabits.forEach(h => merged.set(h.id, h));

    for (const remote of remoteHabits) {
      const local = merged.get(remote.id);
      if (!local) {
        merged.set(remote.id, remote);
        added++;
      } else if (JSON.stringify(local) !== JSON.stringify(remote)) {
        const conflict = this.addConflict('habit', local, remote);
        conflicts.push(conflict);
        merged.set(remote.id, remote);
        updated++;
      }
    }

    const mergedData = Array.from(merged.values());
    return { merged: mergedData, data: mergedData, conflicts, added, updated };
  }

  mergeCheckIns(localCheckIns: CheckIn[], remoteCheckIns: CheckIn[]): {
    merged: CheckIn[];
    data: CheckIn[];
    conflicts: SyncConflict[];
    duplicatesRemoved: number;
    added: number;
    updated: number;
  } {
    const merged = new Map<string, CheckIn>();
    const conflicts: SyncConflict[] = [];
    let duplicatesRemoved = 0;
    let added = 0;
    let updated = 0;

    const getKey = (c: CheckIn) => `${c.habitId}-${c.date}`;

    for (const local of localCheckIns) {
      const key = getKey(local);
      if (merged.has(key)) {
        duplicatesRemoved++;
        continue;
      }
      merged.set(key, local);
    }

    for (const remote of remoteCheckIns) {
      const key = getKey(remote);
      const local = merged.get(key);

      if (!local) {
        merged.set(key, remote);
        added++;
      } else if (local.id !== remote.id) {
        const localTime = new Date(local.timestamp).getTime();
        const remoteTime = new Date(remote.timestamp).getTime();

        if (Math.abs(localTime - remoteTime) < 1000) {
          duplicatesRemoved++;
          logger.info('Duplicate check-in detected and removed', { habitId: remote.habitId, date: remote.date });
        } else {
          const conflict = this.addConflict('checkin', local, remote);
          conflicts.push(conflict);
          merged.set(key, remoteTime > localTime ? remote : local);
          updated++;
        }
      }
    }

    const mergedData = Array.from(merged.values());
    return {
      merged: mergedData,
      data: mergedData,
      conflicts,
      duplicatesRemoved,
      added,
      updated,
    };
  }

  repairHabit(partial: Partial<Habit>): Habit | null {
    try {
      const timezone = getLocalTimezone();
      const repaired: Habit = {
        id: partial.id || generateId(),
        name: partial.name?.trim() || '未命名习惯',
        description: partial.description || '',
        icon: partial.icon || 'Target',
        color: partial.color || '#0ea5e9',
        frequency: partial.frequency || 'daily',
        targetCount: partial.targetCount || 1,
        createdAt: partial.createdAt || getTodayISO(timezone),
        timezone: partial.timezone || timezone,
      };

      const validation = validateHabit(repaired);
      return validation.valid ? repaired : null;
    } catch (error) {
      logger.error('Failed to repair habit', error as Error, { partial });
      return null;
    }
  }

  repairCheckIn(partial: Partial<CheckIn>): CheckIn | null {
    try {
      const timezone = getLocalTimezone();
      const timestamp = partial.timestamp || new Date().toISOString();
      const repaired: CheckIn = {
        id: partial.id || generateId(),
        habitId: partial.habitId || generateId(),
        date: partial.date || getTodayISO(timezone),
        timestamp,
        timezone: partial.timezone || timezone,
        note: partial.note,
      };

      const validation = validateCheckIn(repaired);
      return validation.valid ? repaired : null;
    } catch (error) {
      logger.error('Failed to repair check-in', error as Error, { partial });
      return null;
    }
  }

  validateAndRepairHabits(habits: Partial<Habit>[]): {
    validData: Habit[];
    repairedCount: number;
    removedCount: number;
  } {
    return validateAndRepairData<Habit>(
      habits as Habit[],
      validateHabit,
      this.repairHabit.bind(this)
    );
  }

  validateAndRepairCheckIns(checkIns: Partial<CheckIn>[]): {
    validData: CheckIn[];
    repairedCount: number;
    removedCount: number;
  } {
    return validateAndRepairData<CheckIn>(
      checkIns as CheckIn[],
      validateCheckIn,
      this.repairCheckIn.bind(this)
    );
  }
}

export const syncManager = new SyncManager();
