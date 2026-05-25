package service

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"sync"
	"time"

	"med-reminder/internal/logger"
	"med-reminder/internal/models"
	"med-reminder/internal/repository"
)

type Dispatcher interface {
	Send(ctx context.Context, rm *models.Reminder) error
}

type ReminderService struct {
	remRepo      *repository.ReminderRepo
	schedRepo    *repository.ScheduleRepo
	medRepo      *repository.MedicationRepo
	logRepo      *repository.LogRepo
	schedSvc     *ScheduleService
	dispatcher   Dispatcher
	loc          *time.Location
	maxRetry     int
	mergeWindow  time.Duration
	workers      int

	mu       sync.Mutex
	sending  map[string]struct{}
	sem      chan struct{}
}

func NewReminderService(
	remRepo *repository.ReminderRepo,
	schedRepo *repository.ScheduleRepo,
	medRepo *repository.MedicationRepo,
	logRepo *repository.LogRepo,
	schedSvc *ScheduleService,
	dispatcher Dispatcher,
	loc *time.Location,
	maxRetry int,
	mergeWindowMin int,
	workers int,
) *ReminderService {
	if workers <= 0 {
		workers = 3
	}
	return &ReminderService{
		remRepo:     remRepo,
		schedRepo:   schedRepo,
		medRepo:     medRepo,
		logRepo:     logRepo,
		schedSvc:    schedSvc,
		dispatcher:  dispatcher,
		loc:         loc,
		maxRetry:    maxRetry,
		mergeWindow: time.Duration(mergeWindowMin) * time.Minute,
		workers:     workers,
		sending:     map[string]struct{}{},
		sem:         make(chan struct{}, workers),
	}
}

func (r *ReminderService) GenerateForSchedule(ctx context.Context, sc *models.ReminderSchedule, horizon time.Duration) (int, error) {
	from := time.Now().In(r.loc)
	to := from.Add(horizon)
	times, err := r.schedSvc.GenerateUpcoming(ctx, sc, from, to)
	if err != nil {
		return 0, err
	}
	med, err := r.medRepo.GetByID(ctx, sc.MedicationID)
	if err != nil {
		return 0, err
	}
	created := 0
	for _, t := range times {
		exists, err := r.remRepo.ExistsScheduled(ctx, sc.ID, t)
		if err != nil {
			logger.S().Errorw("check reminder exists failed", "error", err)
			continue
		}
		if exists {
			continue
		}
		rem := &models.Reminder{
			MedicationID: sc.MedicationID,
			ScheduleID:   sc.ID,
			UserID:       sc.UserID,
			ScheduledAt:  t.Add(-time.Duration(sc.LeadMinutes) * time.Minute),
			Status:       models.ReminderPending,
			Channel:      "system",
			Message:      fmt.Sprintf("请服用 %s，剂量：%s。%s", med.Name, med.Dosage, med.Instruction),
		}
		if err := r.remRepo.Create(ctx, rem); err != nil {
			logger.S().Errorw("create reminder failed", "error", err, "schedule", sc.ID, "at", t)
			continue
		}
		created++
	}
	return created, nil
}

func (r *ReminderService) GenerateAllUpcoming(ctx context.Context, horizon time.Duration) (int, error) {
	all, err := r.schedRepo.ListAllActive(ctx)
	if err != nil {
		return 0, err
	}
	total := 0
	for _, sc := range all {
		n, err := r.GenerateForSchedule(ctx, &sc, horizon)
		if err != nil {
			logger.S().Errorw("generate reminders failed", "error", err, "schedule", sc.ID)
			continue
		}
		total += n
	}
	return total, nil
}

func (r *ReminderService) CheckAndDispatch(ctx context.Context) (int, error) {
	now := time.Now().In(r.loc)
	from := now.Add(-24 * time.Hour)
	to := now.Add(2 * time.Minute)

	pending, err := r.remRepo.ListPendingByWindow(ctx, from, to)
	if err != nil {
		return 0, err
	}

	groups := r.mergeConflicts(ctx, pending)

	dispatched := 0
	for _, group := range groups {
		if len(group) == 0 {
			continue
		}
		r.mu.Lock()
		skip := false
		for _, rm := range group {
			if _, ok := r.sending[rm.ID]; ok {
				skip = true
				break
			}
		}
		if skip {
			r.mu.Unlock()
			continue
		}
		for _, rm := range group {
			r.sending[rm.ID] = struct{}{}
		}
		r.mu.Unlock()

		r.sem <- struct{}{}
		go func(g []models.Reminder) {
			defer func() { <-r.sem }()
			defer func() {
				r.mu.Lock()
				for _, rm := range g {
					delete(r.sending, rm.ID)
				}
				r.mu.Unlock()
			}()
			if err := r.dispatchGroup(ctx, g); err != nil {
				logger.S().Errorw("dispatch group failed", "error", err, "count", len(g))
			}
		}(group)
		dispatched++
	}
	return dispatched, nil
}

func (r *ReminderService) dispatchGroup(ctx context.Context, group []models.Reminder) error {
	if len(group) == 1 {
		return r.dispatchOne(ctx, &group[0])
	}
	primary := group[0]
	var parts []string
	for _, rm := range group {
		parts = append(parts, fmt.Sprintf("- %s", rm.Message))
	}
	primary.Message = strings.Join(parts, "\n")
	primary.ConflictsWith = nil
	for _, rm := range group[1:] {
		primary.ConflictsWith = append(primary.ConflictsWith, rm.ID)
	}
	if err := r.dispatchOne(ctx, &primary); err != nil {
		return err
	}
	for _, rm := range group[1:] {
		_ = r.remRepo.UpdateStatus(ctx, rm.ID, models.ReminderCancelled, "merged into "+primary.ID)
	}
	return nil
}

func (r *ReminderService) dispatchOne(ctx context.Context, rm *models.Reminder) error {
	if r.dispatcher == nil {
		return r.remRepo.UpdateStatus(ctx, rm.ID, models.ReminderSent, "")
	}
	if err := r.dispatcher.Send(ctx, rm); err != nil {
		_ = r.remRepo.IncrementRetry(ctx, rm.ID, err.Error())
		if rm.RetryCount+1 >= r.maxRetry {
			return r.remRepo.UpdateStatus(ctx, rm.ID, models.ReminderFailed, err.Error())
		}
		return err
	}
	return r.remRepo.UpdateStatus(ctx, rm.ID, models.ReminderSent, "")
}

func (r *ReminderService) mergeConflicts(ctx context.Context, pending []models.Reminder) [][]models.Reminder {
	if r.mergeWindow <= 0 || len(pending) < 2 {
		var groups [][]models.Reminder
		for _, rm := range pending {
			groups = append(groups, []models.Reminder{rm})
		}
		return groups
	}

	byUser := map[string][]int{}
	for i, rm := range pending {
		byUser[rm.UserID] = append(byUser[rm.UserID], i)
	}

	grouped := make([]bool, len(pending))
	var result [][]models.Reminder

	for _, idxs := range byUser {
		for _, i := range idxs {
			if grouped[i] {
				continue
			}
			grouped[i] = true
			group := []models.Reminder{pending[i]}
			a := pending[i]
			for _, j := range idxs {
				if i == j || grouped[j] {
					continue
				}
				b := pending[j]
				if a.ScheduledAt.Sub(b.ScheduledAt).Abs() <= r.mergeWindow {
					group = append(group, b)
					grouped[j] = true
				}
			}
			result = append(result, group)
		}
	}
	for i := range pending {
		if !grouped[i] {
			result = append(result, []models.Reminder{pending[i]})
		}
	}
	return result
}

func (r *ReminderService) Acknowledge(ctx context.Context, id, userID string) error {
	rm, err := r.remRepo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if rm.UserID != userID {
		return ErrForbidden
	}
	now := time.Now().In(r.loc)
	onTime := now.Sub(rm.ScheduledAt) <= 30*time.Minute
	log := &models.MedicationLog{
		MedicationID: rm.MedicationID,
		ReminderID:   rm.ID,
		UserID:       rm.UserID,
		Action:       "taken",
		OccurredAt:   now,
		OnTime:       onTime,
	}
	if err := r.logRepo.Create(ctx, log); err != nil {
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return r.remRepo.UpdateStatus(ctx, id, models.ReminderAcknowledged, "")
}

func (r *ReminderService) Skip(ctx context.Context, id, userID string, reason string) error {
	rm, err := r.remRepo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if rm.UserID != userID {
		return ErrForbidden
	}
	log := &models.MedicationLog{
		MedicationID: rm.MedicationID,
		ReminderID:   rm.ID,
		UserID:       rm.UserID,
		Action:       "missed",
		OccurredAt:   time.Now().In(r.loc),
		OnTime:       false,
		Notes:        reason,
	}
	if err := r.logRepo.Create(ctx, log); err != nil {
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return r.remRepo.UpdateStatus(ctx, id, models.ReminderMissed, reason)
}

func (r *ReminderService) ListByUser(ctx context.Context, userID string, limit, offset int) ([]models.Reminder, error) {
	if limit <= 0 || limit > 200 {
		limit = 50
	}
	return r.remRepo.ListByUser(ctx, userID, limit, offset)
}

func (r *ReminderService) MarkMissed(ctx context.Context, overdueWindow time.Duration) (int, error) {
	cutoff := time.Now().In(r.loc).Add(-overdueWindow)
	n, err := r.remRepo.MarkMissed(ctx, cutoff)
	if err != nil {
		return 0, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return n, nil
}
