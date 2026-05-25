package service

import (
	"context"
	"errors"
	"fmt"
	"time"

	"plant-care-reminder/internal/model"
	"plant-care-reminder/internal/storage"
	"plant-care-reminder/pkg/concurrency"
	"plant-care-reminder/pkg/logger"
	"plant-care-reminder/pkg/reminder"
)

type ReminderService struct {
	store       *storage.JSONStore
	reminderEng *reminder.Engine
}

func NewReminderService(store *storage.JSONStore, reminderEng *reminder.Engine) *ReminderService {
	return &ReminderService{
		store:       store,
		reminderEng: reminderEng,
	}
}

func (s *ReminderService) GetAllReminders(ctx context.Context, status string) ([]*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var reminders []*model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		var err error
		reminders, err = s.store.GetAllReminders()
		return err
	})
	if err != nil {
		logger.Error("Failed to get all reminders", err)
		return nil, err
	}

	if status != "" {
		var filtered []*model.Reminder
		for _, r := range reminders {
			if r.Status == status {
				filtered = append(filtered, r)
			}
		}
		return filtered, nil
	}

	return reminders, nil
}

func (s *ReminderService) GetReminderByID(ctx context.Context, id string) (*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var reminder *model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		var err error
		reminder, err = s.store.GetReminderByID(id)
		return err
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return nil, fmt.Errorf("reminder not found: %s", id)
		}
		logger.Error("Failed to get reminder", err, map[string]interface{}{"id": id})
		return nil, err
	}
	return reminder, nil
}

func (s *ReminderService) GetRemindersByPlantID(ctx context.Context, plantID string) ([]*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var reminders []*model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		var err error
		reminders, err = s.store.GetRemindersByPlantID(plantID)
		return err
	})
	if err != nil {
		logger.Error("Failed to get reminders for plant", err, map[string]interface{}{"plant_id": plantID})
		return nil, err
	}
	return reminders, nil
}

func (s *ReminderService) GetPendingReminders(ctx context.Context) ([]*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var reminders []*model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		var err error
		reminders, err = s.store.GetPendingReminders()
		return err
	})
	if err != nil {
		logger.Error("Failed to get pending reminders", err)
		return nil, err
	}
	return reminders, nil
}

func (s *ReminderService) GenerateReminders(ctx context.Context) ([]*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var newReminders []*model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		var err error
		newReminders, err = s.reminderEng.GenerateAllReminders()
		if err != nil {
			return err
		}

		for _, r := range newReminders {
			if err := s.store.CreateReminder(r); err != nil {
				if !errors.Is(err, storage.ErrAlreadyExists) {
					logger.Error("Failed to persist reminder", err, map[string]interface{}{
						"reminder_id": r.ID,
					})
				}
			}
		}
		return nil
	})
	if err != nil {
		logger.Error("Failed to generate reminders", err)
		return nil, err
	}
	return newReminders, nil
}

func (s *ReminderService) MarkReminderCompleted(ctx context.Context, id string) (*model.Reminder, error) {
	limiter := concurrency.GetLimiter()
	var reminder *model.Reminder
	err := limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithWrite(id, func() error {
			var err error
			reminder, err = s.store.GetReminderByID(id)
			if err != nil {
				return err
			}

			reminder.Status = model.ReminderStatusCompleted
			reminder.Notified = true
			if err := s.store.UpdateReminder(reminder); err != nil {
				return err
			}
			return nil
		})
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return nil, fmt.Errorf("reminder not found: %s", id)
		}
		logger.Error("Failed to mark reminder completed", err, map[string]interface{}{"id": id})
		return nil, err
	}
	return reminder, nil
}

func (s *ReminderService) DeleteReminder(ctx context.Context, id string) error {
	limiter := concurrency.GetLimiter()
	err := limiter.WithLimit(ctx, func() error {
		return s.store.DeleteReminder(id)
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return fmt.Errorf("reminder not found: %s", id)
		}
		logger.Error("Failed to delete reminder", err, map[string]interface{}{"id": id})
		return err
	}
	return nil
}

func (s *ReminderService) CheckAndUpdateReminders(ctx context.Context) {
	s.reminderEng.UpdateReminderStatuses()
}

func (s *ReminderService) GetOverdueReminders(ctx context.Context) []*model.Reminder {
	return s.reminderEng.CheckOverdueReminders()
}

func (s *ReminderService) GetReminderStats(ctx context.Context) (map[string]interface{}, error) {
	reminders, err := s.GetAllReminders(ctx, "")
	if err != nil {
		return nil, err
	}

	var pending, sent, completed, overdue, waterCount, fertilizeCount, dueToday int
	total := len(reminders)

	now := time.Now()
	for _, r := range reminders {
		switch r.Status {
		case model.ReminderStatusPending:
			pending++
		case model.ReminderStatusSent:
			sent++
		case model.ReminderStatusCompleted:
			completed++
		case model.ReminderStatusOverdue:
			overdue++
		}

		if r.Scheduled.After(now) && r.Scheduled.Before(now.Add(24*time.Hour)) {
			dueToday++
		}

		switch r.Type {
		case model.ReminderTypeWater:
			waterCount++
		case model.ReminderTypeFertilize:
			fertilizeCount++
		}
	}

	stats := map[string]interface{}{
		"total":     total,
		"pending":   pending,
		"sent":      sent,
		"completed": completed,
		"overdue":   overdue,
		"water":     waterCount,
		"fertilize": fertilizeCount,
		"due_today": dueToday,
	}

	return stats, nil
}
