package service

import (
	"context"
	"errors"
	"fmt"
	"time"

	"med-reminder/internal/logger"
	"med-reminder/internal/models"
	"med-reminder/internal/repository"
)

type MedicationService struct {
	repo *repository.MedicationRepo
	loc  *time.Location
}

func NewMedicationService(r *repository.MedicationRepo, loc *time.Location) *MedicationService {
	return &MedicationService{repo: r, loc: loc}
}

func (s *MedicationService) Create(ctx context.Context, m *models.Medication) error {
	if err := m.Validate(); err != nil {
		return fmt.Errorf("%w: %v", ErrValidation, err)
	}
	m.Expired = m.ExpiryDate.In(s.loc).Before(time.Now().In(s.loc))
	if err := s.repo.Create(ctx, m); err != nil {
		logger.S().Errorw("create medication failed", "error", err, "name", m.Name, "user", m.UserID)
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	logger.S().Infow("medication created", "id", m.ID, "name", m.Name, "user", m.UserID)
	return nil
}

func (s *MedicationService) Get(ctx context.Context, id, userID string) (*models.Medication, error) {
	m, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return nil, ErrNotFound
		}
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if m.UserID != userID {
		return nil, ErrForbidden
	}
	return m, nil
}

func (s *MedicationService) List(ctx context.Context, userID string, includeExpired bool) ([]models.Medication, error) {
	out, err := s.repo.ListByUser(ctx, userID, includeExpired)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return out, nil
}

func (s *MedicationService) Update(ctx context.Context, m *models.Medication, userID string) error {
	existing, err := s.repo.GetByID(ctx, m.ID)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if existing.UserID != userID {
		return ErrForbidden
	}
	if err := m.Validate(); err != nil {
		return fmt.Errorf("%w: %v", ErrValidation, err)
	}
	m.UserID = existing.UserID
	m.CreatedAt = existing.CreatedAt
	if err := s.repo.Update(ctx, m); err != nil {
		logger.S().Errorw("update medication failed", "error", err, "id", m.ID)
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	logger.S().Infow("medication updated", "id", m.ID)
	return nil
}

func (s *MedicationService) Delete(ctx context.Context, id, userID string) error {
	m, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, repository.ErrNotFound) {
			return ErrNotFound
		}
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if m.UserID != userID {
		return ErrForbidden
	}
	if err := s.repo.Delete(ctx, id); err != nil {
		logger.S().Errorw("delete medication failed", "error", err, "id", id)
		return fmt.Errorf("%w: %v", ErrInternal, err)
	}
	logger.S().Infow("medication deleted", "id", id)
	return nil
}

func (s *MedicationService) RefreshExpiry(ctx context.Context) (int, error) {
	n, err := s.repo.MarkExpired(ctx, s.loc)
	if err != nil {
		return 0, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	if n > 0 {
		logger.S().Infow("expired medications marked", "count", n)
	}
	return n, nil
}

func (s *MedicationService) LowStock(ctx context.Context, userID string) ([]models.Medication, error) {
	out, err := s.repo.LowStock(ctx, userID)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInternal, err)
	}
	return out, nil
}

type ServiceError struct{ Msg string }

func (e *ServiceError) Error() string { return e.Msg }

var (
	ErrNotFound   = &ServiceError{Msg: "resource not found"}
	ErrValidation = &ServiceError{Msg: "validation error"}
	ErrForbidden  = &ServiceError{Msg: "forbidden"}
	ErrConflict   = &ServiceError{Msg: "conflict"}
	ErrInternal   = &ServiceError{Msg: "internal error"}
)
