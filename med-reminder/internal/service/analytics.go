package service

import (
	"context"
	"fmt"
	"time"

	"med-reminder/internal/models"
	"med-reminder/internal/repository"
)

type AnalyticsService struct {
	logRepo    *repository.LogRepo
	medRepo    *repository.MedicationRepo
	windowDays int
	riskThresh float64
	loc        *time.Location
}

func NewAnalyticsService(logRepo *repository.LogRepo, medRepo *repository.MedicationRepo, windowDays int, riskThresh float64, loc *time.Location) *AnalyticsService {
	if windowDays <= 0 {
		windowDays = 30
	}
	if riskThresh <= 0 || riskThresh > 1 {
		riskThresh = 0.8
	}
	return &AnalyticsService{logRepo: logRepo, medRepo: medRepo, windowDays: windowDays, riskThresh: riskThresh, loc: loc}
}

func (a *AnalyticsService) AdherenceReport(ctx context.Context, userID string, window time.Duration) (*models.AdherenceReport, error) {
	now := time.Now().In(a.loc)
	if window <= 0 {
		window = time.Duration(a.windowDays) * 24 * time.Hour
	}
	from := now.Add(-window)
	onTime, late, missed, total, err := a.logRepo.CountByStatus(ctx, userID, from, now)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	report := &models.AdherenceReport{
		UserID:      userID,
		PeriodStart: from,
		PeriodEnd:   now,
		TotalDoses:  total,
		TakenOnTime: onTime,
		TakenLate:   late,
		Missed:      missed,
	}
	if total > 0 {
		report.AdherenceRate = float64(onTime+late) / float64(total)
	}
	report.AtRisk = report.AdherenceRate < a.riskThresh

	meds, err := a.medRepo.ListByUser(ctx, userID, true)
	if err != nil {
		return report, nil
	}
	allLogs, err := a.logRepo.ListByUser(ctx, userID, from, now)
	if err == nil {
		for _, m := range meds {
			b := models.AdherenceBreakdown{
				MedicationID:   m.ID,
				MedicationName: m.Name,
			}
			taken := 0
			for _, l := range allLogs {
				if l.MedicationID != m.ID {
					continue
				}
				b.Total++
				if l.Action == "taken" {
					taken++
					if l.OnTime {
						b.TakenOnTime++
					}
				}
				if l.Action == "missed" {
					b.Missed++
				}
			}
			if b.Total > 0 {
				b.Rate = float64(taken) / float64(b.Total)
			}
			report.Breakdown = append(report.Breakdown, b)
		}
	}
	return report, nil
}

func (a *AnalyticsService) History(ctx context.Context, userID string, from, to time.Time) ([]models.MedicationLog, error) {
	if from.IsZero() {
		from = time.Now().In(a.loc).Add(-30 * 24 * time.Hour)
	}
	if to.IsZero() {
		to = time.Now().In(a.loc)
	}
	return a.logRepo.ListByUser(ctx, userID, from, to)
}
