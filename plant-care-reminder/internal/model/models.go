package model

import (
	"time"

	"github.com/google/uuid"
)

type Plant struct {
	ID              string    `json:"id"`
	Name            string    `json:"name"`
	Species         string    `json:"species"`
	WaterFrequency  int       `json:"water_frequency_days"`
	FertilizeFreq   int       `json:"fertilize_frequency_days"`
	SunlightNeed    string    `json:"sunlight_need"`
	LastWatered     time.Time `json:"last_watered"`
	LastFertilized  time.Time `json:"last_fertilized"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
	Notes           string    `json:"notes,omitempty"`
	Status          string    `json:"status"`
}

type Reminder struct {
	ID         string    `json:"id"`
	PlantID    string    `json:"plant_id"`
	PlantName  string    `json:"plant_name"`
	Type       string    `json:"type"`
	Scheduled  time.Time `json:"scheduled_at"`
	RemindAt   time.Time `json:"remind_at"`
	Status     string    `json:"status"`
	CreatedAt  time.Time `json:"created_at"`
	Notified   bool      `json:"notified"`
	NotifiedAt time.Time `json:"notified_at,omitempty"`
}

type CareHistory struct {
	ID          string    `json:"id"`
	PlantID     string    `json:"plant_id"`
	PlantName   string    `json:"plant_name"`
	Operation   string    `json:"operation"`
	Timestamp   time.Time `json:"timestamp"`
	Operator    string    `json:"operator,omitempty"`
	Notes       string    `json:"notes,omitempty"`
	StatusBefore string   `json:"status_before,omitempty"`
	StatusAfter  string   `json:"status_after,omitempty"`
}

type CreatePlantRequest struct {
	Name           string `json:"name" binding:"required"`
	Species        string `json:"species" binding:"required"`
	WaterFrequency int    `json:"water_frequency_days"`
	FertilizeFreq  int    `json:"fertilize_frequency_days"`
	SunlightNeed   string `json:"sunlight_need"`
	Notes          string `json:"notes"`
}

type UpdatePlantRequest struct {
	Name           string `json:"name"`
	Species        string `json:"species"`
	WaterFrequency *int   `json:"water_frequency_days"`
	FertilizeFreq  *int   `json:"fertilize_frequency_days"`
	SunlightNeed   string `json:"sunlight_need"`
	Status         string `json:"status"`
	Notes          string `json:"notes"`
}

type CareOperationRequest struct {
	Operation string `json:"operation" binding:"required,oneof=water fertilize prune repot"`
	Operator  string `json:"operator"`
	Notes     string `json:"notes"`
}

const (
	PlantStatusHealthy   = "healthy"
	PlantStatusNeedsCare = "needs_care"
	PlantStatusSick      = "sick"
	PlantStatusDormant   = "dormant"

	ReminderTypeWater     = "water"
	ReminderTypeFertilize = "fertilize"

	ReminderStatusPending  = "pending"
	ReminderStatusSent     = "sent"
	ReminderStatusCompleted = "completed"
	ReminderStatusOverdue  = "overdue"
)

func NewPlant(req CreatePlantRequest) *Plant {
	now := time.Now()
	return &Plant{
		ID:             uuid.New().String(),
		Name:           req.Name,
		Species:        req.Species,
		WaterFrequency: req.WaterFrequency,
		FertilizeFreq:  req.FertilizeFreq,
		SunlightNeed:   req.SunlightNeed,
		LastWatered:    now,
		LastFertilized: now,
		CreatedAt:      now,
		UpdatedAt:      now,
		Notes:          req.Notes,
		Status:         PlantStatusHealthy,
	}
}

func NewReminder(plantID, plantName, reminderType string, scheduled, remindAt time.Time) *Reminder {
	return &Reminder{
		ID:        uuid.New().String(),
		PlantID:   plantID,
		PlantName: plantName,
		Type:      reminderType,
		Scheduled: scheduled,
		RemindAt:  remindAt,
		Status:    ReminderStatusPending,
		CreatedAt: time.Now(),
		Notified:  false,
	}
}

func NewCareHistory(plantID, plantName, operation, operator, notes, statusBefore, statusAfter string) *CareHistory {
	return &CareHistory{
		ID:           uuid.New().String(),
		PlantID:      plantID,
		PlantName:    plantName,
		Operation:    operation,
		Timestamp:    time.Now(),
		Operator:     operator,
		Notes:        notes,
		StatusBefore: statusBefore,
		StatusAfter:  statusAfter,
	}
}
