package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"task-scheduler/internal/config"
	"task-scheduler/internal/models"
	"task-scheduler/pkg/utils"
	"time"

	"github.com/robfig/cron/v3"
	"github.com/sony/gobreaker"
	"go.uber.org/zap"
	"golang.org/x/time/rate"
	"gorm.io/gorm"
)

type Scheduler struct {
	cron         *cron.Cron
	jobEntries   map[string]cron.EntryID
	limiter      *rate.Limiter
	breakers     map[string]*gobreaker.CircuitBreaker
	runningTasks map[string]bool
	mu           sync.RWMutex
	taskService  *TaskService
}

var scheduler *Scheduler
var schedulerOnce sync.Once

func GetScheduler() *Scheduler {
	schedulerOnce.Do(func() {
		scheduler = &Scheduler{
			cron:         cron.New(cron.WithParser(cron.NewParser(cron.Second | cron.Minute | cron.Hour | cron.Dom | cron.Month | cron.Dow | cron.Descriptor))),
			jobEntries:   make(map[string]cron.EntryID),
			limiter:      rate.NewLimiter(rate.Limit(config.AppConfig.Scheduler.MaxConcurrentTasks), config.AppConfig.Scheduler.MaxConcurrentTasks),
			breakers:     make(map[string]*gobreaker.CircuitBreaker),
			runningTasks: make(map[string]bool),
			taskService:  NewTaskService(),
		}
	})
	return scheduler
}

func (s *Scheduler) Start() error {
	utils.Logger.Info("Starting scheduler...")

	tasks, err := s.taskService.GetAllActiveTasks()
	if err != nil {
		return fmt.Errorf("failed to load active tasks: %w", err)
	}

	for _, task := range tasks {
		if err := s.RegisterTask(task); err != nil {
			utils.Logger.Error("Failed to register task", zap.String("task_id", task.ID), zap.String("task_name", task.Name), zap.Error(err))
		}
	}

	s.cron.Start()
	utils.Logger.Info("Scheduler started", zap.Int("task_count", len(tasks)))
	return nil
}

func (s *Scheduler) Stop() {
	utils.Logger.Info("Stopping scheduler...")
	s.cron.Stop()
	utils.Logger.Info("Scheduler stopped")
}

func (s *Scheduler) RegisterTask(task *models.Task) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if entryID, exists := s.jobEntries[task.ID]; exists {
		s.cron.Remove(entryID)
		delete(s.jobEntries, task.ID)
	}

	if task.Status != models.TaskStatusPending && task.Status != models.TaskStatusRunning {
		return nil
	}

	if task.CircuitBreaker {
		if _, exists := s.breakers[task.ID]; !exists {
			s.breakers[task.ID] = gobreaker.NewCircuitBreaker(gobreaker.Settings{
				Name:        task.ID,
				MaxRequests: 1,
				Interval:    60 * time.Second,
				Timeout:     30 * time.Second,
				ReadyToTrip: func(counts gobreaker.Counts) bool {
					failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
					return counts.Requests >= 3 && failureRatio >= 0.6
				},
				OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
					utils.Logger.Warn("Circuit breaker state changed",
						zap.String("task_id", name),
						zap.String("from", from.String()),
						zap.String("to", to.String()),
					)
				},
			})
		}
	}

	entryID, err := s.cron.AddFunc(task.CronExpression, func() {
		s.executeTask(task.ID)
	})
	if err != nil {
		return fmt.Errorf("failed to add cron job: %w", err)
	}

	s.jobEntries[task.ID] = entryID

	nextTime := s.cron.Entry(entryID).Next
	task.NextRunAt = &nextTime
	if err := models.DB.Model(task).Update("next_run_at", nextTime).Error; err != nil {
		utils.Logger.Error("Failed to update next run time", zap.Error(err))
	}

	utils.Logger.Info("Task registered",
		zap.String("task_id", task.ID),
		zap.String("task_name", task.Name),
		zap.String("cron", task.CronExpression),
		zap.Time("next_run", nextTime),
	)

	return nil
}

func (s *Scheduler) UnregisterTask(taskID string) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if entryID, exists := s.jobEntries[taskID]; exists {
		s.cron.Remove(entryID)
		delete(s.jobEntries, taskID)
		utils.Logger.Info("Task unregistered", zap.String("task_id", taskID))
	}

	delete(s.breakers, taskID)
}

func (s *Scheduler) executeTask(taskID string) {
	if !s.limiter.Allow() {
		utils.Logger.Warn("Rate limit exceeded, skipping task", zap.String("task_id", taskID))
		return
	}

	s.mu.Lock()
	if s.runningTasks[taskID] {
		s.mu.Unlock()
		utils.Logger.Warn("Task already running, skipping", zap.String("task_id", taskID))
		return
	}
	s.runningTasks[taskID] = true
	s.mu.Unlock()

	go func() {
		defer func() {
			s.mu.Lock()
			delete(s.runningTasks, taskID)
			s.mu.Unlock()
		}()

		if err := s.runTaskWithRetry(taskID); err != nil {
			utils.Logger.Error("Task execution failed", zap.String("task_id", taskID), zap.Error(err))
		}
	}()
}

func (s *Scheduler) runTaskWithRetry(taskID string) error {
	task, err := s.taskService.GetByID(taskID)
	if err != nil {
		return fmt.Errorf("failed to get task: %w", err)
	}

	if task.Status == models.TaskStatusPaused || task.Status == models.TaskStatusCancelled {
		utils.Logger.Info("Task is paused or cancelled, skipping", zap.String("task_id", taskID))
		return nil
	}

	if err := s.checkDependencies(task); err != nil {
		utils.Logger.Warn("Task dependencies not satisfied", zap.String("task_id", taskID), zap.Error(err))
		return nil
	}

	executor := GetExecutor(task.Type)
	if executor == nil {
		return fmt.Errorf("unsupported task type: %s", task.Type)
	}

	timeout := task.Timeout
	if timeout <= 0 {
		timeout = config.AppConfig.Scheduler.DefaultTimeout
	}

	var lastErr error
	var result string

	maxRetry := task.MaxRetryCount
	if maxRetry <= 0 {
		maxRetry = config.AppConfig.Scheduler.MaxRetryCount
	}

	for attempt := 0; attempt <= maxRetry; attempt++ {
		if attempt > 0 {
			utils.Logger.Info("Retrying task",
				zap.String("task_id", taskID),
				zap.Int("attempt", attempt),
				zap.Int("max_retry", maxRetry),
			)
			time.Sleep(time.Duration(task.RetryInterval) * time.Second)
		}

		taskLog := &models.TaskLog{
			TaskID:     task.ID,
			TaskName:   task.Name,
			Status:     models.TaskStatusRunning,
			StartTime:  time.Now(),
			RetryCount: attempt,
		}
		models.DB.Create(taskLog)

		runFunc := func() (string, error) {
			ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)
			defer cancel()
			return executor.Execute(ctx, task)
		}

		startTime := time.Now()
		if task.CircuitBreaker {
			breaker := s.breakers[taskID]
			if breaker != nil {
				execResult, execErr := breaker.Execute(func() (interface{}, error) {
					return runFunc()
				})
				lastErr = execErr
				if lastErr == gobreaker.ErrOpenState || lastErr == gobreaker.ErrTooManyRequests {
					utils.Logger.Warn("Circuit breaker is open", zap.String("task_id", taskID))
					result = ""
				} else if execResult != nil {
					result = execResult.(string)
				}
			} else {
				result, lastErr = runFunc()
			}
		} else {
			result, lastErr = runFunc()
		}

		duration := time.Since(startTime).Milliseconds()
		now := time.Now()

		taskLog.EndTime = &now
		taskLog.DurationMs = duration
		taskLog.Result = result

		if lastErr != nil {
			taskLog.Status = models.TaskStatusFailed
			taskLog.Error = lastErr.Error()
			models.DB.Save(taskLog)
			continue
		}

		taskLog.Status = models.TaskStatusSuccess
		models.DB.Save(taskLog)

		now = time.Now()
		task.LastRunAt = &now
		models.DB.Model(task).Updates(map[string]interface{}{
			"last_run_at": now,
			"status":      models.TaskStatusPending,
		})

		if task.WebhookURL != "" {
			go s.sendWebhook(task, taskLog)
		}

		s.scheduleDependentTasks(task)

		return nil
	}

	models.DB.Model(task).Update("status", models.TaskStatusPending)
	return lastErr
}

func (s *Scheduler) checkDependencies(task *models.Task) error {
	if len(task.Dependencies) == 0 {
		return nil
	}

	for _, depID := range task.Dependencies {
		var depTask models.Task
		if err := models.DB.Unscoped().Where("id = ?", depID).First(&depTask).Error; err != nil {
			if err == gorm.ErrRecordNotFound {
				utils.Logger.Error("Dependency task not found",
					zap.String("task_id", task.ID),
					zap.String("dependency_id", depID),
				)
				return fmt.Errorf("依赖任务 %s 不存在或已被删除", depID)
			}
			return err
		}

		if depTask.DeletedAt.Valid {
			utils.Logger.Error("Dependency task has been deleted",
				zap.String("task_id", task.ID),
				zap.String("dependency_id", depID),
			)
			return fmt.Errorf("依赖任务 %s 已被删除", depID)
		}

		var depLog models.TaskLog
		if err := models.DB.Where("task_id = ?", depID).
			Order("created_at desc").
			First(&depLog).Error; err != nil {
			if err == gorm.ErrRecordNotFound {
				return fmt.Errorf("依赖任务 %s 尚未执行", depID)
			}
			return err
		}

		if depLog.Status != models.TaskStatusSuccess {
			return fmt.Errorf("依赖任务 %s 上次执行失败", depID)
		}
	}

	return nil
}

func (s *Scheduler) sendWebhook(task *models.Task, log *models.TaskLog) {
	payload := map[string]interface{}{
		"task_id":     task.ID,
		"task_name":   task.Name,
		"status":      log.Status,
		"start_time":  log.StartTime,
		"end_time":    log.EndTime,
		"duration_ms": log.DurationMs,
		"result":      log.Result,
		"error":       log.Error,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		utils.Logger.Error("Failed to marshal webhook payload", zap.Error(err))
		return
	}

	maxRetries := 3
	retryInterval := []time.Duration{1 * time.Second, 3 * time.Second, 5 * time.Second}

	for attempt := 0; attempt < maxRetries; attempt++ {
		if attempt > 0 {
			time.Sleep(retryInterval[attempt-1])
			utils.Logger.Info("Retrying webhook",
				zap.String("task_id", task.ID),
				zap.Int("attempt", attempt+1),
				zap.Int("max_retries", maxRetries),
			)
		}

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		req, err := http.NewRequestWithContext(ctx, http.MethodPost, task.WebhookURL, bytes.NewReader(body))
		if err != nil {
			cancel()
			utils.Logger.Error("Failed to create webhook request", zap.Error(err))
			continue
		}
		req.Header.Set("Content-Type", "application/json")

		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			cancel()
			utils.Logger.Error("Failed to send webhook",
				zap.String("task_id", task.ID),
				zap.Int("attempt", attempt+1),
				zap.Error(err),
			)
			continue
		}
		resp.Body.Close()
		cancel()

		if resp.StatusCode >= 200 && resp.StatusCode < 400 {
			utils.Logger.Info("Webhook sent successfully",
				zap.String("task_id", task.ID),
				zap.Int("status_code", resp.StatusCode),
				zap.Int("attempt", attempt+1),
			)
			return
		}

		utils.Logger.Warn("Webhook returned non-success status",
			zap.String("task_id", task.ID),
			zap.Int("status_code", resp.StatusCode),
			zap.Int("attempt", attempt+1),
		)
	}

	utils.Logger.Error("Webhook failed after all retries",
		zap.String("task_id", task.ID),
		zap.String("webhook_url", task.WebhookURL),
		zap.Int("max_retries", maxRetries),
	)
}

func (s *Scheduler) scheduleDependentTasks(task *models.Task) {
	var dependentTasks []models.Task
	if err := models.DB.Raw(`
		SELECT t.* FROM tasks t
		INNER JOIN task_dependencies td ON t.id = td.task_id
		WHERE td.dependency_id = ? AND t.deleted_at IS NULL
	`, task.ID).Scan(&dependentTasks).Error; err != nil {
		utils.Logger.Error("Failed to find dependent tasks", zap.Error(err))
		return
	}

	for _, depTask := range dependentTasks {
		if depTask.Status == models.TaskStatusPending || depTask.Status == models.TaskStatusRunning {
			go func(t models.Task) {
				utils.Logger.Info("Triggering dependent task",
					zap.String("task_id", t.ID),
					zap.String("task_name", t.Name),
					zap.String("triggered_by", task.ID),
				)
				s.executeTask(t.ID)
			}(depTask)
		}
	}
}

func (s *Scheduler) TriggerTask(taskID string) error {
	s.mu.Lock()
	if s.runningTasks[taskID] {
		s.mu.Unlock()
		return fmt.Errorf("task is already running")
	}
	s.runningTasks[taskID] = true
	s.mu.Unlock()

	go func() {
		defer func() {
			s.mu.Lock()
			delete(s.runningTasks, taskID)
			s.mu.Unlock()
		}()

		if !s.limiter.Allow() {
			utils.Logger.Warn("Rate limit exceeded, skipping task", zap.String("task_id", taskID))
			return
		}

		if err := s.runTaskWithRetry(taskID); err != nil {
			utils.Logger.Error("Task execution failed", zap.String("task_id", taskID), zap.Error(err))
		}
	}()
	return nil
}

func (s *Scheduler) GetNextRunTime(taskID string) (*time.Time, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	entryID, exists := s.jobEntries[taskID]
	if !exists {
		return nil, fmt.Errorf("task not registered")
	}

	entry := s.cron.Entry(entryID)
	return &entry.Next, nil
}
