package reminder

import (
	"math"
	"time"

	"plant-care-reminder/config"
	"plant-care-reminder/internal/model"
	"plant-care-reminder/internal/storage"
	"plant-care-reminder/pkg/logger"
)

type Engine struct {
	cfg    *config.ReminderConfig
	store  *storage.JSONStore
}

func NewEngine(cfg *config.ReminderConfig, store *storage.JSONStore) *Engine {
	return &Engine{
		cfg:   cfg,
		store: store,
	}
}

func (e *Engine) CalculateNextWaterDate(plant *model.Plant) (time.Time, error) {
	lastWatered := plant.LastWatered
	frequency := plant.WaterFrequency

	if frequency <= 0 {
		frequency = e.cfg.DefaultWaterDays
		logger.Warn("Invalid water frequency, using default", map[string]interface{}{
			"plant_id": plant.ID,
			"frequency": frequency,
		})
	}

	nextDate, ok := safeAddDays(lastWatered, frequency)
	if !ok {
		logger.Warn("Date overflow detected, capping to max date", map[string]interface{}{
			"plant_id":  plant.ID,
			"operation": "water",
		})
		nextDate = getMaxDate()
	}

	return nextDate, nil
}

func (e *Engine) CalculateNextFertilizeDate(plant *model.Plant) (time.Time, error) {
	lastFertilized := plant.LastFertilized
	frequency := plant.FertilizeFreq

	if frequency <= 0 {
		frequency = e.cfg.DefaultFertilizeDays
		logger.Warn("Invalid fertilize frequency, using default", map[string]interface{}{
			"plant_id": plant.ID,
			"frequency": frequency,
		})
	}

	nextDate, ok := safeAddDays(lastFertilized, frequency)
	if !ok {
		logger.Warn("Date overflow detected, capping to max date", map[string]interface{}{
			"plant_id":  plant.ID,
			"operation": "fertilize",
		})
		nextDate = getMaxDate()
	}

	return nextDate, nil
}

func (e *Engine) GenerateReminderForPlant(plant *model.Plant, reminderType string) (*model.Reminder, error) {
	var scheduledDate time.Time
	var err error

	switch reminderType {
	case model.ReminderTypeWater:
		scheduledDate, err = e.CalculateNextWaterDate(plant)
	case model.ReminderTypeFertilize:
		scheduledDate, err = e.CalculateNextFertilizeDate(plant)
	default:
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	dedupWindow := time.Duration(e.cfg.RemindBeforeHours) * time.Hour
	dedupThreshold := scheduledDate.Add(-dedupWindow)

	if e.store.ReminderExists(plant.ID, reminderType, dedupThreshold) {
		logger.Debug("Duplicate reminder detected, skipping", map[string]interface{}{
			"plant_id": plant.ID,
			"type":     reminderType,
			"scheduled": scheduledDate,
		})
		return nil, nil
	}

	remindAt := scheduledDate.Add(-time.Duration(e.cfg.RemindBeforeHours) * time.Hour)
	now := time.Now()
	if remindAt.Before(now) {
		remindAt = now
	}

	reminder := model.NewReminder(plant.ID, plant.Name, reminderType, scheduledDate, remindAt)
	return reminder, nil
}

func (e *Engine) GenerateAllReminders() ([]*model.Reminder, error) {
	plants, err := e.store.GetAllPlants()
	if err != nil {
		return nil, err
	}

	var reminders []*model.Reminder
	for _, plant := range plants {
		if plant.Status == model.PlantStatusDormant {
			continue
		}

		waterReminder, err := e.GenerateReminderForPlant(plant, model.ReminderTypeWater)
		if err != nil {
			logger.Error("Failed to generate water reminder", err, map[string]interface{}{
				"plant_id": plant.ID,
			})
			continue
		}
		if waterReminder != nil {
			reminders = append(reminders, waterReminder)
		}

		fertilizeReminder, err := e.GenerateReminderForPlant(plant, model.ReminderTypeFertilize)
		if err != nil {
			logger.Error("Failed to generate fertilize reminder", err, map[string]interface{}{
				"plant_id": plant.ID,
			})
			continue
		}
		if fertilizeReminder != nil {
			reminders = append(reminders, fertilizeReminder)
		}
	}

	return reminders, nil
}

func (e *Engine) CheckOverdueReminders() []*model.Reminder {
	reminders, err := e.store.GetPendingReminders()
	if err != nil {
		logger.Error("Failed to get pending reminders", err)
		return nil
	}

	now := time.Now()
	var overdue []*model.Reminder
	for _, r := range reminders {
		if r.Scheduled.Before(now) && r.Status == model.ReminderStatusPending {
			overdue = append(overdue, r)
		}
	}
	return overdue
}

func (e *Engine) UpdateReminderStatuses() {
	reminders, err := e.store.GetPendingReminders()
	if err != nil {
		logger.Error("Failed to get pending reminders for status update", err)
		return
	}

	now := time.Now()
	for _, r := range reminders {
		if r.Status == model.ReminderStatusPending && r.RemindAt.Before(now) {
			r.Status = model.ReminderStatusSent
			r.Notified = true
			r.NotifiedAt = now
			if err := e.store.UpdateReminder(r); err != nil {
				logger.Error("Failed to update reminder status", err, map[string]interface{}{
					"reminder_id": r.ID,
				})
				continue
			}
			logger.Info("Reminder sent", map[string]interface{}{
				"reminder_id": r.ID,
				"plant_name":  r.PlantName,
				"type":        r.Type,
			})
		}

		if (r.Status == model.ReminderStatusPending || r.Status == model.ReminderStatusSent) &&
			r.Scheduled.Before(now.Add(-24*time.Hour)) {
			r.Status = model.ReminderStatusOverdue
			if err := e.store.UpdateReminder(r); err != nil {
				logger.Error("Failed to mark reminder as overdue", err, map[string]interface{}{
					"reminder_id": r.ID,
				})
				continue
			}
			logger.Warn("Reminder overdue", map[string]interface{}{
				"reminder_id": r.ID,
				"plant_name":  r.PlantName,
				"type":        r.Type,
			})
		}
	}
}

func safeAddDays(t time.Time, days int) (time.Time, bool) {
	if days <= 0 {
		return t, true
	}

	maxDate := getMaxDate()
	duration := time.Duration(days) * 24 * time.Hour

	if t.After(maxDate.Add(-duration)) {
		return maxDate, false
	}

	return t.Add(duration), true
}

func getMaxDate() time.Time {
	return time.Date(2199, 12, 31, 23, 59, 59, 999999999, time.UTC)
}

func GetDaysUntil(date time.Time) int {
	now := time.Now()
	diff := date.Sub(now)
	days := int(math.Ceil(diff.Hours() / 24))
	return days
}
