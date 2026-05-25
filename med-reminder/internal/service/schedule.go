package service

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"strings"
	"time"

	"med-reminder/internal/logger"
	"med-reminder/internal/models"
	"med-reminder/internal/repository"
)

type ScheduleService struct {
	repo       *repository.ScheduleRepo
	medRepo    *repository.MedicationRepo
	remRepo    *repository.ReminderRepo
	loc        *time.Location
	maxPerMed  int
	leadMin    int
}

func NewScheduleService(repo *repository.ScheduleRepo, medRepo *repository.MedicationRepo, remRepo *repository.ReminderRepo, loc *time.Location, maxPerMed, leadMin int) *ScheduleService {
	return &ScheduleService{repo: repo, medRepo: medRepo, remRepo: remRepo, loc: loc, maxPerMed: maxPerMed, leadMin: leadMin}
}

func (s *ScheduleService) Create(ctx context.Context, sc *models.ReminderSchedule, userID string) error {
	med, err := s.medRepo.GetByID(ctx, sc.MedicationID)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if med.UserID != userID {
		return ErrForbidden
	}
	existing, err := s.repo.ListByMedication(ctx, sc.MedicationID)
	if err != nil {
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if s.maxPerMed > 0 && len(existing) >= s.maxPerMed {
		return fmt.Errorf("%w: max schedules per medication exceeded", ErrConflict)
	}
	if sc.LeadMinutes <= 0 {
		sc.LeadMinutes = s.leadMin
	}
	sc.UserID = userID
	if err := sc.Validate(); err != nil {
		return fmt.Errorf("%w: %v", ErrValidation, err)
	}
	if err := s.repo.Create(ctx, sc); err != nil {
		logger.S().Errorw("create schedule failed", "error", err, "med_id", sc.MedicationID)
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	logger.S().Infow("schedule created", "id", sc.ID, "med_id", sc.MedicationID)
	return nil
}

func (s *ScheduleService) Get(ctx context.Context, id, userID string) (*models.ReminderSchedule, error) {
	sc, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return nil, ErrNotFound
		}
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if sc.UserID != userID {
		return nil, ErrForbidden
	}
	return sc, nil
}

func (s *ScheduleService) ListByMedication(ctx context.Context, medID, userID string) ([]models.ReminderSchedule, error) {
	med, err := s.medRepo.GetByID(ctx, medID)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return nil, ErrNotFound
		}
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if med.UserID != userID {
		return nil, ErrForbidden
	}
	return s.repo.ListByMedication(ctx, medID)
}

func (s *ScheduleService) ListByUser(ctx context.Context, userID string) ([]models.ReminderSchedule, error) {
	return s.repo.ListByUser(ctx, userID)
}

func (s *ScheduleService) Update(ctx context.Context, sc *models.ReminderSchedule, userID string) error {
	existing, err := s.repo.GetByID(ctx, sc.ID)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if existing.UserID != userID {
		return ErrForbidden
	}
	sc.MedicationID = existing.MedicationID
	sc.UserID = existing.UserID
	sc.CreatedAt = existing.CreatedAt
	if sc.LeadMinutes <= 0 {
		sc.LeadMinutes = s.leadMin
	}
	if err := sc.Validate(); err != nil {
		return fmt.Errorf("%w: %v", ErrValidation, err)
	}
	if err := s.repo.Update(ctx, sc); err != nil {
		logger.S().Errorw("update schedule failed", "error", err, "id", sc.ID)
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return nil
}

func (s *ScheduleService) Delete(ctx context.Context, id, userID string) error {
	sc, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if sc.UserID != userID {
		return ErrForbidden
	}
	return s.repo.Delete(ctx, id)
}

func (s *ScheduleService) GenerateUpcoming(ctx context.Context, sc *models.ReminderSchedule, from, to time.Time) ([]time.Time, error) {
	var out []time.Time
	from = from.In(s.loc)
	to = to.In(s.loc)
	start := sc.StartDate.In(s.loc)
	var end *time.Time
	if sc.EndDate != nil {
		e := sc.EndDate.In(s.loc)
		end = &e
	}
	switch sc.Type {
	case models.ScheduleDaily:
		out = append(out, dailyTimes(from, to, sc.Times, s.loc)...)
	case models.ScheduleEveryNDays:
		out = append(out, everyNDays(from, to, start, sc.IntervalDays, sc.Times, s.loc)...)
	case models.ScheduleWeekly:
		out = append(out, weeklyTimes(from, to, sc.Weekdays, sc.Times, s.loc)...)
	case models.ScheduleOnce:
		if len(sc.Times) == 1 {
			t, err := combineDateTime(start, sc.Times[0], s.loc)
			if err != nil {
				return nil, err
			}
			if !t.Before(from) && !t.After(to) {
				out = append(out, t)
			}
		}
	}
	if end != nil {
		filtered := out[:0]
		for _, t := range out {
			if !t.After(*end) {
				filtered = append(filtered, t)
			}
		}
		out = filtered
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Before(out[j]) })
	return out, nil
}

func dailyTimes(from, to time.Time, times []string, loc *time.Location) []time.Time {
	var out []time.Time
	date := time.Date(from.Year(), from.Month(), from.Day(), 0, 0, 0, 0, loc)
	end := time.Date(to.Year(), to.Month(), to.Day(), 23, 59, 59, 0, loc)
	for !date.After(end) {
		for _, tm := range times {
			t, err := combineDateTime(date, tm, loc)
			if err != nil {
				continue
			}
			if !t.Before(from) && !t.After(to) {
				out = append(out, t)
			}
		}
		date = date.AddDate(0, 0, 1)
	}
	return out
}

func everyNDays(from, to, start time.Time, interval int, times []string, loc *time.Location) []time.Time {
	var out []time.Time
	startDay := time.Date(start.Year(), start.Month(), start.Day(), 0, 0, 0, 0, loc)
	fromDay := time.Date(from.Year(), from.Month(), from.Day(), 0, 0, 0, 0, loc)

	daysDiff := daysBetween(startDay, fromDay)
	var currentDay time.Time
	if daysDiff <= 0 {
		currentDay = startDay
	} else {
		remainder := daysDiff % interval
		if remainder == 0 {
			currentDay = fromDay
		} else {
			currentDay = fromDay.AddDate(0, 0, interval-remainder)
		}
	}

	toDay := time.Date(to.Year(), to.Month(), to.Day(), 23, 59, 59, 0, loc)
	for !currentDay.After(toDay) {
		for _, tm := range times {
			t, err := combineDateTime(currentDay, tm, loc)
			if err != nil {
				continue
			}
			if !t.Before(from) && !t.Before(start) && !t.After(to) {
				out = append(out, t)
			}
		}
		currentDay = currentDay.AddDate(0, 0, interval)
	}
	return out
}

func daysBetween(a, b time.Time) int {
	a = time.Date(a.Year(), a.Month(), a.Day(), 0, 0, 0, 0, a.Location())
	b = time.Date(b.Year(), b.Month(), b.Day(), 0, 0, 0, 0, b.Location())

	sign := 1
	if a.After(b) {
		a, b = b, a
		sign = -1
	}
	days := 0
	for d := a; d.Before(b); d = d.AddDate(0, 0, 1) {
		days++
	}
	return days * sign
}

func weeklyTimes(from, to time.Time, weekdays []int, times []string, loc *time.Location) []time.Time {
	var out []time.Time
	date := time.Date(from.Year(), from.Month(), from.Day(), 0, 0, 0, 0, loc)
	end := time.Date(to.Year(), to.Month(), to.Day(), 23, 59, 59, 0, loc)
	for !date.After(end) {
		wd := int(date.Weekday())
		for _, target := range weekdays {
			if target == wd {
				for _, tm := range times {
					t, err := combineDateTime(date, tm, loc)
					if err != nil {
						continue
					}
					if !t.Before(from) && !t.After(to) {
						out = append(out, t)
					}
				}
			}
		}
		date = date.AddDate(0, 0, 1)
	}
	return out
}

func combineDateTime(date time.Time, tm string, loc *time.Location) (time.Time, error) {
	tm = strings.TrimSpace(tm)
	var h, m int
	if _, err := fmt.Sscanf(tm, "%d:%d", &h, &m); err != nil {
		return time.Time{}, fmt.Errorf("invalid time format %q: %w", tm, err)
	}
	if h < 0 || h > 23 || m < 0 || m > 59 {
		return time.Time{}, fmt.Errorf("invalid time %q", tm)
	}
	return time.Date(date.Year(), date.Month(), date.Day(), h, m, 0, 0, loc), nil
}
