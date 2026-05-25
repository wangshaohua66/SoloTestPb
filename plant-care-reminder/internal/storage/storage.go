package storage

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"plant-care-reminder/config"
	"plant-care-reminder/internal/model"
	"plant-care-reminder/pkg/logger"
)

var (
	ErrNotFound      = errors.New("resource not found")
	ErrAlreadyExists = errors.New("resource already exists")
	ErrInvalidData   = errors.New("invalid data")
)

type PlantStore interface {
	GetAll() ([]*model.Plant, error)
	GetByID(id string) (*model.Plant, error)
	Create(plant *model.Plant) error
	Update(plant *model.Plant) error
	Delete(id string) error
}

type ReminderStore interface {
	GetAll() ([]*model.Reminder, error)
	GetByID(id string) (*model.Reminder, error)
	GetByPlantID(plantID string) ([]*model.Reminder, error)
	GetPending() ([]*model.Reminder, error)
	Create(reminder *model.Reminder) error
	Update(reminder *model.Reminder) error
	Delete(id string) error
	Exists(plantID, reminderType string, scheduledAfter time.Time) bool
}

type HistoryStore interface {
	GetAll() ([]*model.CareHistory, error)
	GetByPlantID(plantID string) ([]*model.CareHistory, error)
	GetByDateRange(start, end time.Time) ([]*model.CareHistory, error)
	Create(history *model.CareHistory) error
}

type JSONStore struct {
	plantsFile    string
	remindersFile string
	historyFile   string
	plantMu       sync.RWMutex
	reminderMu    sync.RWMutex
	historyMu     sync.RWMutex
}

func NewJSONStore(cfg *config.StorageConfig) (*JSONStore, error) {
	if err := ensureDir(filepath.Dir(cfg.PlantsFile)); err != nil {
		return nil, fmt.Errorf("ensure plants dir failed: %w", err)
	}
	if err := ensureDir(filepath.Dir(cfg.RemindersFile)); err != nil {
		return nil, fmt.Errorf("ensure reminders dir failed: %w", err)
	}
	if err := ensureDir(filepath.Dir(cfg.HistoryFile)); err != nil {
		return nil, fmt.Errorf("ensure history dir failed: %w", err)
	}

	store := &JSONStore{
		plantsFile:    cfg.PlantsFile,
		remindersFile: cfg.RemindersFile,
		historyFile:   cfg.HistoryFile,
	}

	if err := store.initFiles(); err != nil {
		return nil, fmt.Errorf("init files failed: %w", err)
	}

	return store, nil
}

func ensureDir(dir string) error {
	if dir == "" || dir == "." {
		return nil
	}
	return os.MkdirAll(dir, 0755)
}

func (s *JSONStore) initFiles() error {
	if _, err := os.Stat(s.plantsFile); os.IsNotExist(err) {
		if err := s.writeJSON(s.plantsFile, []*model.Plant{}); err != nil {
			return err
		}
		logger.Info("Created empty plants file", map[string]interface{}{"file": s.plantsFile})
	}
	if _, err := os.Stat(s.remindersFile); os.IsNotExist(err) {
		if err := s.writeJSON(s.remindersFile, []*model.Reminder{}); err != nil {
			return err
		}
		logger.Info("Created empty reminders file", map[string]interface{}{"file": s.remindersFile})
	}
	if _, err := os.Stat(s.historyFile); os.IsNotExist(err) {
		if err := s.writeJSON(s.historyFile, []*model.CareHistory{}); err != nil {
			return err
		}
		logger.Info("Created empty history file", map[string]interface{}{"file": s.historyFile})
	}
	return nil
}

func (s *JSONStore) readJSON(filename string, v interface{}) error {
	data, err := os.ReadFile(filename)
	if err != nil {
		return fmt.Errorf("read file %s failed: %w", filename, err)
	}
	if len(data) == 0 {
		return nil
	}
	if err := json.Unmarshal(data, v); err != nil {
		return fmt.Errorf("unmarshal file %s failed: %w", filename, err)
	}
	return nil
}

func (s *JSONStore) writeJSON(filename string, v interface{}) error {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal json failed: %w", err)
	}
	tmpFile := filename + ".tmp"
	if err := os.WriteFile(tmpFile, data, 0644); err != nil {
		return fmt.Errorf("write temp file failed: %w", err)
	}
	if err := os.Rename(tmpFile, filename); err != nil {
		os.Remove(tmpFile)
		return fmt.Errorf("rename temp file failed: %w", err)
	}
	return nil
}

func (s *JSONStore) GetAllPlants() ([]*model.Plant, error) {
	s.plantMu.RLock()
	defer s.plantMu.RUnlock()

	var plants []*model.Plant
	if err := s.readJSON(s.plantsFile, &plants); err != nil {
		logger.Error("Failed to read plants", err)
		return nil, err
	}
	return plants, nil
}

func (s *JSONStore) GetPlantByID(id string) (*model.Plant, error) {
	plants, err := s.GetAllPlants()
	if err != nil {
		return nil, err
	}
	for _, p := range plants {
		if p.ID == id {
			return p, nil
		}
	}
	return nil, ErrNotFound
}

func (s *JSONStore) CreatePlant(plant *model.Plant) error {
	s.plantMu.Lock()
	defer s.plantMu.Unlock()

	var plants []*model.Plant
	if err := s.readJSON(s.plantsFile, &plants); err != nil {
		return err
	}

	for _, p := range plants {
		if p.ID == plant.ID {
			return ErrAlreadyExists
		}
	}

	plants = append(plants, plant)
	if err := s.writeJSON(s.plantsFile, plants); err != nil {
		return err
	}
	logger.Info("Plant created", map[string]interface{}{"id": plant.ID, "name": plant.Name})
	return nil
}

func (s *JSONStore) UpdatePlant(plant *model.Plant) error {
	s.plantMu.Lock()
	defer s.plantMu.Unlock()

	var plants []*model.Plant
	if err := s.readJSON(s.plantsFile, &plants); err != nil {
		return err
	}

	found := false
	for i, p := range plants {
		if p.ID == plant.ID {
			plants[i] = plant
			found = true
			break
		}
	}

	if !found {
		return ErrNotFound
	}

	if err := s.writeJSON(s.plantsFile, plants); err != nil {
		return err
	}
	logger.Info("Plant updated", map[string]interface{}{"id": plant.ID, "name": plant.Name})
	return nil
}

func (s *JSONStore) DeletePlant(id string) error {
	s.plantMu.Lock()
	defer s.plantMu.Unlock()

	var plants []*model.Plant
	if err := s.readJSON(s.plantsFile, &plants); err != nil {
		return err
	}

	found := false
	var result []*model.Plant
	for _, p := range plants {
		if p.ID != id {
			result = append(result, p)
		} else {
			found = true
		}
	}

	if !found {
		return ErrNotFound
	}

	if err := s.writeJSON(s.plantsFile, result); err != nil {
		return err
	}
	logger.Info("Plant deleted", map[string]interface{}{"id": id})
	return nil
}

func (s *JSONStore) GetAllReminders() ([]*model.Reminder, error) {
	s.reminderMu.RLock()
	defer s.reminderMu.RUnlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		logger.Error("Failed to read reminders", err)
		return nil, err
	}
	return reminders, nil
}

func (s *JSONStore) GetReminderByID(id string) (*model.Reminder, error) {
	reminders, err := s.GetAllReminders()
	if err != nil {
		return nil, err
	}
	for _, r := range reminders {
		if r.ID == id {
			return r, nil
		}
	}
	return nil, ErrNotFound
}

func (s *JSONStore) GetRemindersByPlantID(plantID string) ([]*model.Reminder, error) {
	reminders, err := s.GetAllReminders()
	if err != nil {
		return nil, err
	}
	var result []*model.Reminder
	for _, r := range reminders {
		if r.PlantID == plantID {
			result = append(result, r)
		}
	}
	return result, nil
}

func (s *JSONStore) GetPendingReminders() ([]*model.Reminder, error) {
	reminders, err := s.GetAllReminders()
	if err != nil {
		return nil, err
	}
	var result []*model.Reminder
	for _, r := range reminders {
		if r.Status == model.ReminderStatusPending || r.Status == model.ReminderStatusSent {
			result = append(result, r)
		}
	}
	return result, nil
}

func (s *JSONStore) CreateReminder(reminder *model.Reminder) error {
	s.reminderMu.Lock()
	defer s.reminderMu.Unlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		return err
	}

	for _, r := range reminders {
		if r.ID == reminder.ID {
			return ErrAlreadyExists
		}
	}

	reminders = append(reminders, reminder)
	if err := s.writeJSON(s.remindersFile, reminders); err != nil {
		return err
	}
	logger.Info("Reminder created", map[string]interface{}{
		"id":       reminder.ID,
		"plant_id": reminder.PlantID,
		"type":     reminder.Type,
		"scheduled": reminder.Scheduled,
	})
	return nil
}

func (s *JSONStore) UpdateReminder(reminder *model.Reminder) error {
	s.reminderMu.Lock()
	defer s.reminderMu.Unlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		return err
	}

	found := false
	for i, r := range reminders {
		if r.ID == reminder.ID {
			reminders[i] = reminder
			found = true
			break
		}
	}

	if !found {
		return ErrNotFound
	}

	if err := s.writeJSON(s.remindersFile, reminders); err != nil {
		return err
	}
	logger.Info("Reminder updated", map[string]interface{}{"id": reminder.ID, "status": reminder.Status})
	return nil
}

func (s *JSONStore) DeleteReminder(id string) error {
	s.reminderMu.Lock()
	defer s.reminderMu.Unlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		return err
	}

	found := false
	var result []*model.Reminder
	for _, r := range reminders {
		if r.ID != id {
			result = append(result, r)
		} else {
			found = true
		}
	}

	if !found {
		return ErrNotFound
	}

	if err := s.writeJSON(s.remindersFile, result); err != nil {
		return err
	}
	logger.Info("Reminder deleted", map[string]interface{}{"id": id})
	return nil
}

func (s *JSONStore) ReminderExists(plantID, reminderType string, scheduledAfter time.Time) bool {
	reminders, err := s.GetAllReminders()
	if err != nil {
		return false
	}
	for _, r := range reminders {
		if r.PlantID == plantID && r.Type == reminderType &&
			(r.Status == model.ReminderStatusPending || r.Status == model.ReminderStatusSent) &&
			(r.Scheduled.Equal(scheduledAfter) || r.Scheduled.After(scheduledAfter)) {
			return true
		}
	}
	return false
}

func (s *JSONStore) GetAllHistory() ([]*model.CareHistory, error) {
	s.historyMu.RLock()
	defer s.historyMu.RUnlock()

	var history []*model.CareHistory
	if err := s.readJSON(s.historyFile, &history); err != nil {
		logger.Error("Failed to read history", err)
		return nil, err
	}
	return history, nil
}

func (s *JSONStore) GetHistoryByPlantID(plantID string) ([]*model.CareHistory, error) {
	history, err := s.GetAllHistory()
	if err != nil {
		return nil, err
	}
	var result []*model.CareHistory
	for _, h := range history {
		if h.PlantID == plantID {
			result = append(result, h)
		}
	}
	return result, nil
}

func (s *JSONStore) GetHistoryByDateRange(start, end time.Time) ([]*model.CareHistory, error) {
	history, err := s.GetAllHistory()
	if err != nil {
		return nil, err
	}
	var result []*model.CareHistory
	for _, h := range history {
		if (h.Timestamp.Equal(start) || h.Timestamp.After(start)) &&
			(h.Timestamp.Equal(end) || h.Timestamp.Before(end)) {
			result = append(result, h)
		}
	}
	return result, nil
}

func (s *JSONStore) CreateHistory(history *model.CareHistory) error {
	s.historyMu.Lock()
	defer s.historyMu.Unlock()

	var histories []*model.CareHistory
	if err := s.readJSON(s.historyFile, &histories); err != nil {
		return err
	}

	histories = append(histories, history)
	if err := s.writeJSON(s.historyFile, histories); err != nil {
		return err
	}
	logger.Info("Care history recorded", map[string]interface{}{
		"id":        history.ID,
		"plant_id":  history.PlantID,
		"operation": history.Operation,
	})
	return nil
}

func (s *JSONStore) DeleteRemindersByPlantID(plantID string) (int, error) {
	s.reminderMu.Lock()
	defer s.reminderMu.Unlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		return 0, err
	}

	count := 0
	var result []*model.Reminder
	for _, r := range reminders {
		if r.PlantID != plantID {
			result = append(result, r)
		} else {
			count++
		}
	}

	if count == 0 {
		return 0, nil
	}

	if err := s.writeJSON(s.remindersFile, result); err != nil {
		return 0, err
	}
	logger.Info("Deleted reminders for plant", map[string]interface{}{
		"plant_id": plantID,
		"count":    count,
	})
	return count, nil
}

func (s *JSONStore) DeleteHistoryByPlantID(plantID string) (int, error) {
	s.historyMu.Lock()
	defer s.historyMu.Unlock()

	var histories []*model.CareHistory
	if err := s.readJSON(s.historyFile, &histories); err != nil {
		return 0, err
	}

	count := 0
	var result []*model.CareHistory
	for _, h := range histories {
		if h.PlantID != plantID {
			result = append(result, h)
		} else {
			count++
		}
	}

	if count == 0 {
		return 0, nil
	}

	if err := s.writeJSON(s.historyFile, result); err != nil {
		return 0, err
	}
	logger.Info("Deleted history for plant", map[string]interface{}{
		"plant_id": plantID,
		"count":    count,
	})
	return count, nil
}

func (s *JSONStore) DeletePendingRemindersByPlantAndType(plantID, reminderType string) (int, error) {
	s.reminderMu.Lock()
	defer s.reminderMu.Unlock()

	var reminders []*model.Reminder
	if err := s.readJSON(s.remindersFile, &reminders); err != nil {
		return 0, err
	}

	count := 0
	var result []*model.Reminder
	for _, r := range reminders {
		if r.PlantID == plantID && r.Type == reminderType &&
			(r.Status == model.ReminderStatusPending || r.Status == model.ReminderStatusSent) {
			count++
			logger.Debug("Deleting old pending reminder", map[string]interface{}{
				"reminder_id": r.ID,
				"plant_id":    plantID,
				"type":        reminderType,
				"scheduled":   r.Scheduled,
			})
		} else {
			result = append(result, r)
		}
	}

	if count == 0 {
		return 0, nil
	}

	if err := s.writeJSON(s.remindersFile, result); err != nil {
		return 0, err
	}
	logger.Info("Deleted pending reminders", map[string]interface{}{
		"plant_id": plantID,
		"type":     reminderType,
		"count":    count,
	})
	return count, nil
}
