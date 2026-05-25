package service

import (
	"context"
	"errors"
	"fmt"
	"time"

	"plant-care-reminder/config"
	"plant-care-reminder/internal/model"
	"plant-care-reminder/internal/storage"
	"plant-care-reminder/pkg/concurrency"
	"plant-care-reminder/pkg/logger"
	"plant-care-reminder/pkg/reminder"
	"plant-care-reminder/pkg/validator"
)

type PlantService struct {
	store       *storage.JSONStore
	reminderEng *reminder.Engine
	cfg         *config.ReminderConfig
}

func NewPlantService(store *storage.JSONStore, reminderEng *reminder.Engine, cfg *config.ReminderConfig) *PlantService {
	return &PlantService{
		store:       store,
		reminderEng: reminderEng,
		cfg:         cfg,
	}
}

func (s *PlantService) GetAllPlants(ctx context.Context) ([]*model.Plant, error) {
	limiter := concurrency.GetLimiter()
	var plants []*model.Plant
	err := limiter.WithLimit(ctx, func() error {
		var err error
		plants, err = s.store.GetAllPlants()
		return err
	})
	if err != nil {
		logger.Error("Failed to get all plants", err)
		return nil, err
	}
	return plants, nil
}

func (s *PlantService) GetPlantByID(ctx context.Context, id string) (*model.Plant, error) {
	if !validator.ValidateID(id) {
		return nil, fmt.Errorf("invalid plant id")
	}

	limiter := concurrency.GetLimiter()
	var plant *model.Plant
	err := limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithRead(id, func() error {
			var err error
			plant, err = s.store.GetPlantByID(id)
			return err
		})
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return nil, fmt.Errorf("plant not found: %s", id)
		}
		logger.Error("Failed to get plant", err, map[string]interface{}{"id": id})
		return nil, err
	}
	return plant, nil
}

func (s *PlantService) CreatePlant(ctx context.Context, req *model.CreatePlantRequest) (*model.Plant, error) {
	verrs := validator.ValidatePlant(req, s.cfg.DefaultWaterDays, s.cfg.DefaultFertilizeDays, s.cfg.DefaultSunlight)
	if verrs.HasErrors() {
		return nil, verrs
	}

	limiter := concurrency.GetLimiter()
	var plant *model.Plant
	err := limiter.WithLimit(ctx, func() error {
		plant = model.NewPlant(*req)
		return s.store.CreatePlant(plant)
	})
	if err != nil {
		if errors.Is(err, storage.ErrAlreadyExists) {
			return nil, fmt.Errorf("plant already exists")
		}
		logger.Error("Failed to create plant", err, map[string]interface{}{"name": req.Name})
		return nil, err
	}

	go func() {
		defer func() {
			if r := recover(); r != nil {
				logger.Error("Panic in post-create reminder generation", fmt.Errorf("panic: %v", r))
			}
		}()
		s.generatePlantReminders(context.Background(), plant)
	}()

	return plant, nil
}

func (s *PlantService) UpdatePlant(ctx context.Context, id string, req *model.UpdatePlantRequest) (*model.Plant, error) {
	if !validator.ValidateID(id) {
		return nil, fmt.Errorf("invalid plant id")
	}

	verrs := validator.ValidateUpdatePlant(req)
	if verrs.HasErrors() {
		return nil, verrs
	}

	limiter := concurrency.GetLimiter()
	var updatedPlant *model.Plant
	err := limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithWrite(id, func() error {
			plant, err := s.store.GetPlantByID(id)
			if err != nil {
				return err
			}

			oldWaterFreq := plant.WaterFrequency
			oldFertilizeFreq := plant.FertilizeFreq

			if req.Name != "" {
				plant.Name = req.Name
			}
			if req.Species != "" {
				plant.Species = req.Species
			}
			if req.WaterFrequency != nil {
				plant.WaterFrequency = *req.WaterFrequency
			}
			if req.FertilizeFreq != nil {
				plant.FertilizeFreq = *req.FertilizeFreq
			}
			if req.SunlightNeed != "" {
				plant.SunlightNeed = req.SunlightNeed
			}
			if req.Status != "" {
				plant.Status = req.Status
			}
			if req.Notes != "" {
				plant.Notes = req.Notes
			}
			plant.UpdatedAt = time.Now()

			if err := s.store.UpdatePlant(plant); err != nil {
				return err
			}

			if req.WaterFrequency != nil && *req.WaterFrequency != oldWaterFreq {
				if _, err := s.store.DeletePendingRemindersByPlantAndType(id, model.ReminderTypeWater); err != nil {
					logger.Warn("Failed to delete old water reminders", map[string]interface{}{
						"plant_id": id,
						"error":    err.Error(),
					})
				}
			}
			if req.FertilizeFreq != nil && *req.FertilizeFreq != oldFertilizeFreq {
				if _, err := s.store.DeletePendingRemindersByPlantAndType(id, model.ReminderTypeFertilize); err != nil {
					logger.Warn("Failed to delete old fertilize reminders", map[string]interface{}{
						"plant_id": id,
						"error":    err.Error(),
					})
				}
			}

			updatedPlant = plant
			return nil
		})
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return nil, fmt.Errorf("plant not found: %s", id)
		}
		logger.Error("Failed to update plant", err, map[string]interface{}{"id": id})
		return nil, err
	}

	go func() {
		defer func() {
			if r := recover(); r != nil {
				logger.Error("Panic in post-update reminder generation", fmt.Errorf("panic: %v", r))
			}
		}()
		s.generatePlantReminders(context.Background(), updatedPlant)
	}()

	return updatedPlant, nil
}

func (s *PlantService) DeletePlant(ctx context.Context, id string) error {
	if !validator.ValidateID(id) {
		return fmt.Errorf("invalid plant id")
	}

	limiter := concurrency.GetLimiter()
	err := limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithWrite(id, func() error {
			if _, err := s.store.DeleteRemindersByPlantID(id); err != nil {
				logger.Warn("Failed to delete reminders for plant", map[string]interface{}{
					"plant_id": id,
					"error":    err.Error(),
				})
			}
			if _, err := s.store.DeleteHistoryByPlantID(id); err != nil {
				logger.Warn("Failed to delete history for plant", map[string]interface{}{
					"plant_id": id,
					"error":    err.Error(),
				})
			}
			return s.store.DeletePlant(id)
		})
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return fmt.Errorf("plant not found: %s", id)
		}
		logger.Error("Failed to delete plant", err, map[string]interface{}{"id": id})
		return err
	}
	return nil
}

func (s *PlantService) PerformCareOperation(ctx context.Context, plantID string, req *model.CareOperationRequest) (*model.CareHistory, error) {
	if !validator.ValidateID(plantID) {
		return nil, fmt.Errorf("invalid plant id")
	}

	verrs := validator.ValidateCareOperation(req)
	if verrs.HasErrors() {
		return nil, verrs
	}

	limiter := concurrency.GetLimiter()
	var history *model.CareHistory
	err := limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithWrite(plantID, func() error {
			plant, err := s.store.GetPlantByID(plantID)
			if err != nil {
				return err
			}

			statusBefore := plant.Status

			now := time.Now()
			switch req.Operation {
			case "water":
				plant.LastWatered = now
			case "fertilize":
				plant.LastFertilized = now
			}
			plant.Status = model.PlantStatusHealthy
			plant.UpdatedAt = now

			if err := s.store.UpdatePlant(plant); err != nil {
				return err
			}

			history = model.NewCareHistory(
				plant.ID,
				plant.Name,
				req.Operation,
				req.Operator,
				req.Notes,
				statusBefore,
				plant.Status,
			)
			if err := s.store.CreateHistory(history); err != nil {
				return err
			}

			if err := s.completeRelatedReminders(plant.ID, req.Operation); err != nil {
				logger.Warn("Failed to complete related reminders", map[string]interface{}{
					"plant_id":  plantID,
					"operation": req.Operation,
					"error":     err.Error(),
				})
			}

			if req.Operation == "water" {
				if _, err := s.store.DeletePendingRemindersByPlantAndType(plantID, model.ReminderTypeWater); err != nil {
					logger.Warn("Failed to delete old pending water reminders", map[string]interface{}{
						"plant_id": plantID,
						"error":    err.Error(),
					})
				}
			} else if req.Operation == "fertilize" {
				if _, err := s.store.DeletePendingRemindersByPlantAndType(plantID, model.ReminderTypeFertilize); err != nil {
					logger.Warn("Failed to delete old pending fertilize reminders", map[string]interface{}{
						"plant_id": plantID,
						"error":    err.Error(),
					})
				}
			}

			return nil
		})
	})
	if err != nil {
		if errors.Is(err, storage.ErrNotFound) {
			return nil, fmt.Errorf("plant not found: %s", plantID)
		}
		logger.Error("Failed to perform care operation", err, map[string]interface{}{
			"plant_id":  plantID,
			"operation": req.Operation,
		})
		return nil, err
	}

	go func() {
		defer func() {
			if r := recover(); r != nil {
				logger.Error("Panic in post-operation reminder generation", fmt.Errorf("panic: %v", r))
			}
		}()
		plant, _ := s.store.GetPlantByID(plantID)
		if plant != nil {
			s.generatePlantReminders(context.Background(), plant)
		}
	}()

	return history, nil
}

func (s *PlantService) GetCareHistory(ctx context.Context, plantID string) ([]*model.CareHistory, error) {
	if plantID != "" && !validator.ValidateID(plantID) {
		return nil, fmt.Errorf("invalid plant id")
	}

	limiter := concurrency.GetLimiter()
	var history []*model.CareHistory
	err := limiter.WithLimit(ctx, func() error {
		var err error
		if plantID != "" {
			history, err = s.store.GetHistoryByPlantID(plantID)
		} else {
			history, err = s.store.GetAllHistory()
		}
		return err
	})
	if err != nil {
		logger.Error("Failed to get care history", err, map[string]interface{}{"plant_id": plantID})
		return nil, err
	}
	return history, nil
}

func (s *PlantService) completeRelatedReminders(plantID, operation string) error {
	var reminderType string
	switch operation {
	case "water":
		reminderType = model.ReminderTypeWater
	case "fertilize":
		reminderType = model.ReminderTypeFertilize
	default:
		return nil
	}

	reminders, err := s.store.GetRemindersByPlantID(plantID)
	if err != nil {
		return err
	}

	now := time.Now()
	gracePeriod := 1 * time.Hour
	for _, r := range reminders {
		if r.Type == reminderType && r.Status != model.ReminderStatusCompleted {
			scheduled := r.Scheduled
			isDueOrPast := scheduled.Before(now) || scheduled.Equal(now)
			isWithinGracePeriod := scheduled.After(now.Add(-gracePeriod)) && scheduled.Before(now.Add(gracePeriod))
			
			if isDueOrPast || isWithinGracePeriod {
				r.Status = model.ReminderStatusCompleted
				if err := s.store.UpdateReminder(r); err != nil {
					logger.Warn("Failed to complete reminder", map[string]interface{}{
						"reminder_id": r.ID,
						"scheduled":   scheduled,
						"error":       err.Error(),
					})
				}
			} else {
				logger.Debug("Skipping future reminder", map[string]interface{}{
					"reminder_id": r.ID,
					"scheduled":   scheduled,
					"now":         now,
				})
			}
		}
	}
	return nil
}

func (s *PlantService) generatePlantReminders(ctx context.Context, plant *model.Plant) {
	reminders, err := s.reminderEng.GenerateAllReminders()
	if err != nil {
		logger.Error("Failed to generate reminders", err)
		return
	}

	for _, r := range reminders {
		if r.PlantID == plant.ID {
			if err := s.store.CreateReminder(r); err != nil {
				if !errors.Is(err, storage.ErrAlreadyExists) {
					logger.Error("Failed to create reminder", err, map[string]interface{}{
						"plant_id": plant.ID,
						"type":     r.Type,
					})
				}
			}
		}
	}
}

func (s *PlantService) UpdatePlantStatus(ctx context.Context, id string, newStatus string) error {
	if !validator.ValidateID(id) {
		return fmt.Errorf("invalid plant id")
	}
	if !validator.ValidateStatus(newStatus) {
		return fmt.Errorf("invalid status: %s", newStatus)
	}

	limiter := concurrency.GetLimiter()
	return limiter.WithLimit(ctx, func() error {
		keyLock := concurrency.GetKeyLock()
		return keyLock.WithWrite(id, func() error {
			plant, err := s.store.GetPlantByID(id)
			if err != nil {
				return err
			}
			plant.Status = newStatus
			plant.UpdatedAt = time.Now()
			return s.store.UpdatePlant(plant)
		})
	})
}

func (s *PlantService) GetPlantStatus(ctx context.Context, id string) (map[string]interface{}, error) {
	plant, err := s.GetPlantByID(ctx, id)
	if err != nil {
		return nil, err
	}

	nextWater, err := s.reminderEng.CalculateNextWaterDate(plant)
	if err != nil {
		return nil, err
	}
	nextFertilize, err := s.reminderEng.CalculateNextFertilizeDate(plant)
	if err != nil {
		return nil, err
	}

	daysUntilWater := reminder.GetDaysUntil(nextWater)
	daysUntilFertilize := reminder.GetDaysUntil(nextFertilize)
	needsCare := daysUntilWater <= 0 || daysUntilFertilize <= 0

	if needsCare && plant.Status == model.PlantStatusHealthy {
		plant.Status = model.PlantStatusNeedsCare
		plant.UpdatedAt = time.Now()
		if err := s.store.UpdatePlant(plant); err != nil {
			logger.Warn("Failed to update plant status to needs_care", map[string]interface{}{
				"plant_id": id,
				"error":    err.Error(),
			})
		}
	} else if !needsCare && plant.Status == model.PlantStatusNeedsCare {
		plant.Status = model.PlantStatusHealthy
		plant.UpdatedAt = time.Now()
		if err := s.store.UpdatePlant(plant); err != nil {
			logger.Warn("Failed to update plant status to healthy", map[string]interface{}{
				"plant_id": id,
				"error":    err.Error(),
			})
		}
	}

	status := map[string]interface{}{
		"plant":                plant,
		"next_water_date":      nextWater,
		"next_fertilize_date":  nextFertilize,
		"days_until_water":     daysUntilWater,
		"days_until_fertilize": daysUntilFertilize,
		"needs_care":           needsCare,
	}

	return status, nil
}
