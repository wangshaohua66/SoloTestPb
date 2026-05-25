package scheduler

import (
	"context"
	"fmt"
	"sync"
	"time"

	"plant-care-reminder/config"
	"plant-care-reminder/internal/model"
	"plant-care-reminder/internal/service"
	"plant-care-reminder/pkg/logger"
)

type Scheduler struct {
	cfg             *config.ReminderConfig
	reminderService *service.ReminderService
	plantService    *service.PlantService
	ticker          *time.Ticker
	stopChan        chan struct{}
	wg              sync.WaitGroup
	running         bool
	mu              sync.Mutex
}

func NewScheduler(cfg *config.ReminderConfig, reminderService *service.ReminderService, plantService *service.PlantService) *Scheduler {
	interval := time.Duration(cfg.CheckInterval) * time.Second
	if interval < time.Minute {
		interval = time.Minute
	}

	return &Scheduler{
		cfg:             cfg,
		reminderService: reminderService,
		plantService:    plantService,
		ticker:          time.NewTicker(interval),
		stopChan:        make(chan struct{}),
	}
}

func (s *Scheduler) Start() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.running {
		return fmt.Errorf("scheduler already running")
	}

	s.running = true
	s.wg.Add(1)

	go func() {
		defer s.wg.Done()
		defer func() {
			if r := recover(); r != nil {
				logger.Error("Scheduler panic recovered", fmt.Errorf("panic: %v", r))
			}
		}()

		logger.Info("Scheduler started", map[string]interface{}{
			"interval_seconds": s.cfg.CheckInterval,
		})

		s.runChecks(context.Background())

		for {
			select {
			case <-s.ticker.C:
				s.runChecks(context.Background())
			case <-s.stopChan:
				logger.Info("Scheduler stopping")
				return
			}
		}
	}()

	return nil
}

func (s *Scheduler) Stop() {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.running {
		return
	}

	s.ticker.Stop()
	close(s.stopChan)
	s.wg.Wait()
	s.running = false
	logger.Info("Scheduler stopped")
}

func (s *Scheduler) runChecks(ctx context.Context) {
	defer func() {
		if r := recover(); r != nil {
			logger.Error("Panic in scheduler runChecks", fmt.Errorf("panic: %v", r))
		}
	}()

	logger.Debug("Running scheduled reminder checks")

	s.reminderService.CheckAndUpdateReminders(ctx)

	reminders, err := s.reminderService.GenerateReminders(ctx)
	if err != nil {
		logger.Error("Failed to generate reminders in scheduler", err)
	} else if len(reminders) > 0 {
		logger.Info("Generated new reminders in scheduler", map[string]interface{}{
			"count": len(reminders),
		})
	}

	overdue := s.reminderService.GetOverdueReminders(ctx)
	if len(overdue) > 0 {
		logger.Warn("Overdue reminders detected", map[string]interface{}{
			"count": len(overdue),
		})
		for _, r := range overdue {
			logger.Warn("Overdue reminder details", map[string]interface{}{
				"reminder_id": r.ID,
				"plant_name":  r.PlantName,
				"type":        r.Type,
				"scheduled":   r.Scheduled,
			})
		}
	}

	s.checkPlantHealth(ctx)
}

func (s *Scheduler) checkPlantHealth(ctx context.Context) {
	plants, err := s.plantService.GetAllPlants(ctx)
	if err != nil {
		logger.Error("Failed to get plants for health check", err)
		return
	}

	now := time.Now()
	for _, plant := range plants {
		if plant.Status == model.PlantStatusDormant {
			continue
		}

		nextWater := plant.LastWatered.Add(time.Duration(plant.WaterFrequency) * 24 * time.Hour)
		nextFertilize := plant.LastFertilized.Add(time.Duration(plant.FertilizeFreq) * 24 * time.Hour)

		needsCare := false
		newStatus := plant.Status

		if nextWater.Before(now.Add(-24 * time.Hour)) {
			needsCare = true
			newStatus = model.PlantStatusNeedsCare
		}

		if nextFertilize.Before(now.Add(-72 * time.Hour)) {
			needsCare = true
			newStatus = model.PlantStatusNeedsCare
		}

		if !needsCare && plant.Status == model.PlantStatusNeedsCare {
			nextWaterOk := nextWater.After(now) || nextWater.Equal(now)
			nextFertilizeOk := nextFertilize.After(now) || nextFertilize.Equal(now)
			if nextWaterOk && nextFertilizeOk {
				newStatus = model.PlantStatusHealthy
			}
		}

		if plant.Status != newStatus {
			oldStatus := plant.Status
			plant.Status = newStatus
			plant.UpdatedAt = now
			
			if err := s.plantService.UpdatePlantStatus(ctx, plant.ID, newStatus); err != nil {
				logger.Error("Failed to update plant status", err, map[string]interface{}{
					"plant_id":   plant.ID,
					"plant_name": plant.Name,
					"old_status": oldStatus,
					"new_status": newStatus,
				})
			} else {
				logger.Warn("Plant status updated", map[string]interface{}{
					"plant_id":   plant.ID,
					"plant_name": plant.Name,
					"old_status": oldStatus,
					"new_status": newStatus,
				})
			}
		}
	}
}

func (s *Scheduler) IsRunning() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.running
}

func (s *Scheduler) RunNow(ctx context.Context) {
	logger.Info("Manual scheduler run triggered")
	s.runChecks(ctx)
}
