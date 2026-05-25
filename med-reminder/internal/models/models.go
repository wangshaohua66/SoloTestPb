package models

import (
	"errors"
	"fmt"
	"time"
)

type Medication struct {
	ID             string    `json:"id" db:"id"`
	Name           string    `json:"name" db:"name"`
	GenericName    string    `json:"generic_name,omitempty" db:"generic_name"`
	Dosage         string    `json:"dosage" db:"dosage"`
	Instruction    string    `json:"instruction" db:"instruction"`
	Unit           string    `json:"unit,omitempty" db:"unit"`
	SideEffects    string    `json:"side_effects,omitempty" db:"side_effects"`
	Notes          string    `json:"notes,omitempty" db:"notes"`
	ExpiryDate     time.Time `json:"expiry_date" db:"expiry_date"`
	Expired        bool      `json:"expired" db:"expired"`
	Manufacturer   string    `json:"manufacturer,omitempty" db:"manufacturer"`
	StockQuantity  int       `json:"stock_quantity" db:"stock_quantity"`
	LowStockAlert  int       `json:"low_stock_alert" db:"low_stock_alert"`
	UserID         string    `json:"user_id" db:"user_id"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time `json:"updated_at" db:"updated_at"`
}

func (m *Medication) Validate() error {
	if m.Name == "" {
		return errors.New("medication name is required")
	}
	if m.Dosage == "" {
		return errors.New("dosage is required")
	}
	if m.Instruction == "" {
		return errors.New("instruction is required")
	}
	if m.ExpiryDate.IsZero() {
		return errors.New("expiry_date is required")
	}
	if m.StockQuantity < 0 {
		return errors.New("stock_quantity cannot be negative")
	}
	return nil
}

type ScheduleType string

const (
	ScheduleDaily     ScheduleType = "daily"
	ScheduleEveryNDays ScheduleType = "every_n_days"
	ScheduleWeekly    ScheduleType = "weekly"
	ScheduleOnce      ScheduleType = "once"
)

type ReminderSchedule struct {
	ID              string       `json:"id" db:"id"`
	MedicationID    string       `json:"medication_id" db:"medication_id"`
	UserID          string       `json:"user_id" db:"user_id"`
	Type            ScheduleType `json:"type" db:"type"`
	Times           StringList   `json:"times" db:"times"`
	IntervalDays    int          `json:"interval_days,omitempty" db:"interval_days"`
	Weekdays        IntList      `json:"weekdays,omitempty" db:"weekdays"`
	StartDate       time.Time    `json:"start_date" db:"start_date"`
	EndDate         *time.Time   `json:"end_date,omitempty" db:"end_date"`
	LeadMinutes     int          `json:"lead_minutes" db:"lead_minutes"`
	Enabled         bool         `json:"enabled" db:"enabled"`
	CreatedAt       time.Time    `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time    `json:"updated_at" db:"updated_at"`
}

func (s *ReminderSchedule) Validate() error {
	if s.MedicationID == "" {
		return errors.New("medication_id is required")
	}
	switch s.Type {
	case ScheduleDaily:
		if len(s.Times) == 0 {
			return errors.New("at least one time required for daily schedule")
		}
	case ScheduleEveryNDays:
		if s.IntervalDays <= 0 {
			return errors.New("interval_days must be positive")
		}
		if len(s.Times) == 0 {
			return errors.New("at least one time required")
		}
	case ScheduleWeekly:
		if len(s.Weekdays) == 0 {
			return errors.New("at least one weekday required")
		}
		if len(s.Times) == 0 {
			return errors.New("at least one time required")
		}
	case ScheduleOnce:
		if len(s.Times) != 1 {
			return errors.New("exactly one time required for once schedule")
		}
	default:
		return fmt.Errorf("invalid schedule type: %s", s.Type)
	}
	if s.StartDate.IsZero() {
		return errors.New("start_date is required")
	}
	return nil
}

type ReminderStatus string

const (
	ReminderPending   ReminderStatus = "pending"
	ReminderSent      ReminderStatus = "sent"
	ReminderAcknowledged ReminderStatus = "acknowledged"
	ReminderMissed    ReminderStatus = "missed"
	ReminderCancelled ReminderStatus = "cancelled"
	ReminderFailed    ReminderStatus = "failed"
)

type Reminder struct {
	ID            string         `json:"id" db:"id"`
	MedicationID  string         `json:"medication_id" db:"medication_id"`
	ScheduleID    string         `json:"schedule_id" db:"schedule_id"`
	UserID        string         `json:"user_id" db:"user_id"`
	ScheduledAt   time.Time      `json:"scheduled_at" db:"scheduled_at"`
	RemindedAt    *time.Time     `json:"reminded_at,omitempty" db:"reminded_at"`
	AcknowledgedAt *time.Time    `json:"acknowledged_at,omitempty" db:"acknowledged_at"`
	Status        ReminderStatus `json:"status" db:"status"`
	Channel       string         `json:"channel" db:"channel"`
	Message       string         `json:"message" db:"message"`
	RetryCount    int            `json:"retry_count" db:"retry_count"`
	LastError     string         `json:"last_error,omitempty" db:"last_error"`
	ConflictsWith StringList     `json:"conflicts_with,omitempty" db:"conflicts_with"`
	CreatedAt     time.Time      `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time      `json:"updated_at" db:"updated_at"`
}

type MedicationLog struct {
	ID            string     `json:"id" db:"id"`
	MedicationID  string     `json:"medication_id" db:"medication_id"`
	ReminderID    string     `json:"reminder_id,omitempty" db:"reminder_id"`
	UserID        string     `json:"user_id" db:"user_id"`
	Action        string     `json:"action" db:"action"`
	DosageTaken   string     `json:"dosage_taken,omitempty" db:"dosage_taken"`
	OccurredAt    time.Time  `json:"occurred_at" db:"occurred_at"`
	OnTime        bool       `json:"on_time" db:"on_time"`
	Notes         string     `json:"notes,omitempty" db:"notes"`
	CreatedAt     time.Time  `json:"created_at" db:"created_at"`
}

type AdherenceReport struct {
	UserID          string  `json:"user_id"`
	PeriodStart     time.Time `json:"period_start"`
	PeriodEnd       time.Time `json:"period_end"`
	TotalDoses      int     `json:"total_doses"`
	TakenOnTime     int     `json:"taken_on_time"`
	TakenLate       int     `json:"taken_late"`
	Missed          int     `json:"missed"`
	AdherenceRate   float64 `json:"adherence_rate"`
	AtRisk          bool    `json:"at_risk"`
	Breakdown       []AdherenceBreakdown `json:"breakdown,omitempty"`
}

type AdherenceBreakdown struct {
	MedicationID  string  `json:"medication_id"`
	MedicationName string `json:"medication_name"`
	Total         int     `json:"total"`
	TakenOnTime   int     `json:"taken_on_time"`
	Missed        int     `json:"missed"`
	Rate          float64 `json:"rate"`
}

type StringList []string
type IntList []int
