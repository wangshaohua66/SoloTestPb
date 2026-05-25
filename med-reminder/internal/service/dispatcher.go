package service

import (
	"context"

	"med-reminder/internal/logger"
	"med-reminder/internal/models"
)

type LogDispatcher struct{}

func (LogDispatcher) Send(ctx context.Context, rm *models.Reminder) error {
	logger.S().Infow("dispatching reminder",
		"id", rm.ID,
		"user", rm.UserID,
		"medication", rm.MedicationID,
		"scheduled_at", rm.ScheduledAt,
		"message", rm.Message,
	)
	return nil
}
