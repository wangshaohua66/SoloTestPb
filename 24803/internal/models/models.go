package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type TaskType string

const (
	TaskTypeHTTP      TaskType = "http"
	TaskTypeShell     TaskType = "shell"
	TaskTypeDatabase  TaskType = "database"
)

type TaskStatus string

const (
	TaskStatusPending   TaskStatus = "pending"
	TaskStatusRunning   TaskStatus = "running"
	TaskStatusSuccess   TaskStatus = "success"
	TaskStatusFailed    TaskStatus = "failed"
	TaskStatusPaused    TaskStatus = "paused"
	TaskStatusCancelled TaskStatus = "cancelled"
)

type Task struct {
	ID                string         `gorm:"primaryKey;type:varchar(36)" json:"id"`
	Name              string         `gorm:"type:varchar(255);not null" json:"name" binding:"required,max=255"`
	Description       string         `gorm:"type:text" json:"description"`
	Type              TaskType       `gorm:"type:varchar(50);not null" json:"type" binding:"required,oneof=http shell database"`
	CronExpression    string         `gorm:"type:varchar(100);not null" json:"cron_expression" binding:"required,max=100"`
	Params            string         `gorm:"type:text" json:"params"`
	Timeout           int            `gorm:"default:300" json:"timeout" binding:"min=1"`
	MaxRetryCount     int            `gorm:"default:3" json:"max_retry_count" binding:"min=0,max=10"`
	RetryInterval     int            `gorm:"default:60" json:"retry_interval" binding:"min=1"`
	Status            TaskStatus     `gorm:"type:varchar(50);default:pending" json:"status"`
	Tags              []Tag          `gorm:"many2many:task_tags;" json:"tags"`
	Dependencies      []string       `gorm:"-" json:"dependencies"`
	DependencyTasks   []*Task        `gorm:"many2many:task_dependencies;joinForeignKey:TaskID;joinReferences:DependencyID" json:"-"`
	WebhookURL        string         `gorm:"type:varchar(500)" json:"webhook_url" binding:"omitempty,url,max=500"`
	RateLimit         int            `gorm:"default:0" json:"rate_limit" binding:"min=0"`
	CircuitBreaker    bool           `gorm:"default:false" json:"circuit_breaker"`
	LastRunAt         *time.Time     `json:"last_run_at"`
	NextRunAt         *time.Time     `json:"next_run_at"`
	CreatedAt         time.Time      `json:"created_at"`
	UpdatedAt         time.Time      `json:"updated_at"`
	DeletedAt         gorm.DeletedAt `gorm:"index" json:"-"`
	DependencyErrors  []string       `gorm:"-" json:"dependency_errors,omitempty"`
}

func (t *Task) BeforeCreate(tx *gorm.DB) error {
	if t.ID == "" {
		t.ID = uuid.NewString()
	}
	return nil
}

type TaskLog struct {
	ID            string    `gorm:"primaryKey;type:varchar(36)" json:"id"`
	TaskID        string    `gorm:"type:varchar(36);index;not null" json:"task_id"`
	TaskName      string    `gorm:"type:varchar(255);not null" json:"task_name"`
	Status        TaskStatus `gorm:"type:varchar(50);not null" json:"status"`
	StartTime     time.Time `json:"start_time"`
	EndTime       *time.Time `json:"end_time"`
	DurationMs    int64     `json:"duration_ms"`
	Result        string    `gorm:"type:text" json:"result"`
	Error         string    `gorm:"type:text" json:"error"`
	RetryCount    int       `gorm:"default:0" json:"retry_count"`
	CreatedAt     time.Time `json:"created_at"`
}

func (tl *TaskLog) BeforeCreate(tx *gorm.DB) error {
	if tl.ID == "" {
		tl.ID = uuid.NewString()
	}
	return nil
}

type AuditLog struct {
	ID         string    `gorm:"primaryKey;type:varchar(36)" json:"id"`
	UserID     string    `gorm:"type:varchar(36);index" json:"user_id"`
	Username   string    `gorm:"type:varchar(100)" json:"username"`
	Action     string    `gorm:"type:varchar(100);not null" json:"action"`
	Resource   string    `gorm:"type:varchar(100);not null" json:"resource"`
	ResourceID string    `gorm:"type:varchar(36)" json:"resource_id"`
	OldValue   string    `gorm:"type:text" json:"old_value"`
	NewValue   string    `gorm:"type:text" json:"new_value"`
	IPAddress  string    `gorm:"type:varchar(50)" json:"ip_address"`
	UserAgent  string    `gorm:"type:varchar(500)" json:"user_agent"`
	CreatedAt  time.Time `json:"created_at"`
}

func (al *AuditLog) BeforeCreate(tx *gorm.DB) error {
	if al.ID == "" {
		al.ID = uuid.NewString()
	}
	return nil
}

type Tag struct {
	ID        string    `gorm:"primaryKey;type:varchar(36)" json:"id"`
	Name      string    `gorm:"type:varchar(100);uniqueIndex;not null" json:"name" binding:"required,max=100"`
	Color     string    `gorm:"type:varchar(50);default:#3b82f6" json:"color"`
	CreatedAt time.Time `json:"created_at"`
	Tasks     []Task    `gorm:"many2many:task_tags;" json:"-"`
}

func (t *Tag) BeforeCreate(tx *gorm.DB) error {
	if t.ID == "" {
		t.ID = uuid.NewString()
	}
	return nil
}
