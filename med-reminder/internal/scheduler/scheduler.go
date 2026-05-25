package scheduler

import (
	"context"
	"time"

	"med-reminder/internal/db"
	"med-reminder/internal/logger"
	"med-reminder/internal/service"
)

type Scheduler struct {
	reminderSvc   *service.ReminderService
	medSvc        *service.MedicationService
	database      *db.Database
	checkFreq     time.Duration
	backupInt     time.Duration
	missedWindow  time.Duration
	stopCh        chan struct{}
}

func New(reminderSvc *service.ReminderService, medSvc *service.MedicationService, database *db.Database, checkFreq, backupInt, missedWindow time.Duration) *Scheduler {
	return &Scheduler{
		reminderSvc:  reminderSvc,
		medSvc:       medSvc,
		database:     database,
		checkFreq:    checkFreq,
		backupInt:    backupInt,
		missedWindow: missedWindow,
		stopCh:       make(chan struct{}),
	}
}

func (s *Scheduler) Start() {
	go s.loop()
	logger.S().Infow("scheduler started", "check_frequency", s.checkFreq, "backup_interval", s.backupInt)
}

func (s *Scheduler) Stop() {
	close(s.stopCh)
}

func (s *Scheduler) loop() {
	checkT := time.NewTicker(s.checkFreq)
	defer checkT.Stop()
	backupT := time.NewTicker(s.backupInt)
	defer backupT.Stop()

	s.tickOnce()

	for {
		select {
		case <-s.stopCh:
			return
		case <-checkT.C:
			s.tickOnce()
		case <-backupT.C:
			s.doBackup()
		}
	}
}

func (s *Scheduler) tickOnce() {
	ctx := context.Background()
	if _, err := s.medSvc.RefreshExpiry(ctx); err != nil {
		logger.S().Errorw("refresh expiry failed", "error", err)
	}
	if _, err := s.reminderSvc.MarkMissed(ctx, s.missedWindow); err != nil {
		logger.S().Errorw("mark missed failed", "error", err)
	}
	horizon := s.checkFreq + 30*time.Minute
	if n, err := s.reminderSvc.GenerateAllUpcoming(ctx, horizon); err != nil {
		logger.S().Errorw("generate reminders failed", "error", err)
	} else if n > 0 {
		logger.S().Infow("reminders generated", "count", n)
	}
	if n, err := s.reminderSvc.CheckAndDispatch(ctx); err != nil {
		logger.S().Errorw("dispatch reminders failed", "error", err)
	} else if n > 0 {
		logger.S().Infow("reminders dispatched", "count", n)
	}
}

func (s *Scheduler) doBackup() {
	path, err := s.database.Backup()
	if err != nil {
		logger.S().Errorw("backup failed", "error", err)
		return
	}
	logger.S().Infow("backup completed", "path", path)
}
