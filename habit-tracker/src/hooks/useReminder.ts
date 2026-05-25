import { useCallback, useEffect, useRef } from 'react';
import { useAppStore } from '../store/useAppStore';
import { logger } from '../utils/logger';
import { getBestReminderHour, getLocalTimezone, getTodayISO } from '../utils/dateUtils';

export const useReminder = () => {
  const { settings, habits, checkIns, updateSettings, isCheckedInToday } = useAppStore();
  const notificationTimerRef = useRef<number | null>(null);
  const permissionRequestedRef = useRef(false);

  const requestNotificationPermission = useCallback(async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      logger.warn('Notifications are not supported in this browser');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      logger.warn('Notification permission was denied');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      permissionRequestedRef.current = true;
      logger.info('Notification permission status:', { permission });
      return permission === 'granted';
    } catch (error) {
      logger.error('Failed to request notification permission', error as Error);
      return false;
    }
  }, []);

  const getReminderTime = useCallback((): string => {
    if (settings.reminder.smartReminder) {
      const bestHour = getBestReminderHour(settings.activeHours);
      return `${bestHour.toString().padStart(2, '0')}:00`;
    }
    return settings.reminder.defaultTime;
  }, [settings]);

  const sendNotification = useCallback((title: string, options?: NotificationOptions) => {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      return false;
    }

    try {
      const notification = new Notification(title, {
        icon: '/favicon.svg',
        badge: '/favicon.svg',
        ...options,
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
      };

      setTimeout(() => notification.close(), 10000);
      logger.info('Notification sent', { title });
      return true;
    } catch (error) {
      logger.error('Failed to send notification', error as Error);
      return false;
    }
  }, []);

  const checkAndSendReminders = useCallback(() => {
    if (!settings.reminder.enabled) return;

    const incompleteHabits = habits.filter(h => !isCheckedInToday(h.id));
    if (incompleteHabits.length === 0) return;

    const habitNames = incompleteHabits.map(h => h.name).join('、');
    const title = incompleteHabits.length === 1
      ? `别忘了「${habitNames}」`
      : `还有 ${incompleteHabits.length} 个习惯待完成`;

    const body = incompleteHabits.length === 1
      ? '今天的习惯还没完成，来打卡吧！'
      : `包括：${habitNames}`;

    sendNotification(title, { body });
  }, [settings.reminder.enabled, habits, isCheckedInToday, sendNotification]);

  const sendAchievementNotification = useCallback((achievementName: string) => {
    sendNotification('🎉 成就解锁！', {
      body: `恭喜你获得「${achievementName}」成就！`,
    });
  }, [sendNotification]);

  const sendMotivationalMessage = useCallback(() => {
    const today = getTodayISO(getLocalTimezone());
    const todayCheckIns = checkIns.filter(c => c.date === today);

    if (todayCheckIns.length > 0) {
      const messages = [
        '今天做得很棒！继续保持！',
        '每一次打卡都是进步的一步！',
        '坚持就是胜利，你做得很好！',
        '自律给你自由，继续加油！',
        '你的努力看得见，为自己骄傲吧！',
      ];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      sendNotification('💪 每日激励', { body: randomMessage });
    }
  }, [checkIns, sendNotification]);

  const scheduleReminder = useCallback(() => {
    if (notificationTimerRef.current) {
      clearInterval(notificationTimerRef.current);
    }

    if (!settings.reminder.enabled) return;

    const checkTime = () => {
      const now = new Date();
      const [reminderHour, reminderMinute] = getReminderTime().split(':').map(Number);

      if (now.getHours() === reminderHour && now.getMinutes() === reminderMinute) {
        checkAndSendReminders();
      }
    };

    checkTime();
    notificationTimerRef.current = window.setInterval(checkTime, 60000);

    return () => {
      if (notificationTimerRef.current) {
        clearInterval(notificationTimerRef.current);
      }
    };
  }, [settings.reminder.enabled, getReminderTime, checkAndSendReminders]);

  const enableReminders = useCallback(async () => {
    const granted = await requestNotificationPermission();
    if (granted) {
      updateSettings({
        reminder: { ...settings.reminder, enabled: true },
      });
      return true;
    }
    return false;
  }, [requestNotificationPermission, settings.reminder, updateSettings]);

  const disableReminders = useCallback(() => {
    if (notificationTimerRef.current) {
      clearInterval(notificationTimerRef.current);
      notificationTimerRef.current = null;
    }
    updateSettings({
      reminder: { ...settings.reminder, enabled: false },
    });
  }, [settings.reminder, updateSettings]);

  const setDefaultReminderTime = useCallback((time: string) => {
    updateSettings({
      reminder: { ...settings.reminder, defaultTime: time },
    });
  }, [settings.reminder, updateSettings]);

  const toggleSmartReminder = useCallback((enabled: boolean) => {
    updateSettings({
      reminder: { ...settings.reminder, smartReminder: enabled },
    });
  }, [settings.reminder, updateSettings]);

  useEffect(() => {
    const cleanup = scheduleReminder();
    return cleanup;
  }, [scheduleReminder]);

  const notificationPermission = 'Notification' in window ? Notification.permission : 'denied';

  const scheduleNextReminder = useCallback(() => {
    scheduleReminder();
  }, [scheduleReminder]);

  return {
    isSupported: 'Notification' in window,
    permission: notificationPermission,
    notificationPermission,
    isEnabled: settings.reminder.enabled,
    smartReminderEnabled: settings.reminder.smartReminder,
    reminderTime: getReminderTime(),
    defaultReminderTime: settings.reminder.defaultTime,
    requestNotificationPermission,
    requestPermission: requestNotificationPermission,
    scheduleNextReminder,
    enableReminders,
    disableReminders,
    setDefaultReminderTime,
    toggleSmartReminder,
    sendNotification,
    sendAchievementNotification,
    sendMotivationalMessage,
    checkAndSendReminders,
  };
};
