package handlers

import "task-scheduler/internal/models"

type TaskUpdateRequest struct {
	Name           *string        `json:"name" binding:"omitempty,max=255"`
	Description    *string        `json:"description"`
	Type           *models.TaskType `json:"type" binding:"omitempty,oneof=http shell database"`
	CronExpression *string        `json:"cron_expression" binding:"omitempty,max=100"`
	Params         *string        `json:"params"`
	Timeout        *int           `json:"timeout" binding:"omitempty,min=1"`
	MaxRetryCount  *int           `json:"max_retry_count" binding:"omitempty,min=0,max=10"`
	RetryInterval  *int           `json:"retry_interval" binding:"omitempty,min=1"`
	Status         *models.TaskStatus `json:"status" binding:"omitempty,oneof=pending running paused cancelled"`
	WebhookURL     *string        `json:"webhook_url" binding:"omitempty,url,max=500"`
	RateLimit      *int           `json:"rate_limit" binding:"omitempty,min=0"`
	CircuitBreaker *bool          `json:"circuit_breaker"`
	Tags           []models.Tag   `json:"tags"`
	Dependencies   []string       `json:"dependencies"`
}
