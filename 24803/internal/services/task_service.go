package services

import (
	"encoding/json"
	"fmt"
	"task-scheduler/internal/models"
	"task-scheduler/pkg/errors"
	"task-scheduler/pkg/utils"
	"time"

	"go.uber.org/zap"
	"gorm.io/gorm"
)

type TaskService struct{}

func NewTaskService() *TaskService {
	return &TaskService{}
}

func (s *TaskService) Create(task *models.Task, operatorID, operatorName, ip, userAgent string) (*models.Task, *errors.AppError) {
	var existing models.Task
	if err := models.DB.Where("name = ?", task.Name).First(&existing).Error; err == nil {
		return nil, errors.Conflict("任务名称已存在")
	}

	if task.Status == "" {
		task.Status = models.TaskStatusPending
	}

	if task.Timeout <= 0 {
		task.Timeout = 300
	}

	if task.MaxRetryCount <= 0 {
		task.MaxRetryCount = 3
	}

	if task.RetryInterval <= 0 {
		task.RetryInterval = 60
	}

	tx := models.DB.Begin()
	if tx.Error != nil {
		return nil, errors.InternalServerWithErr("启动事务失败", tx.Error)
	}

	if len(task.Tags) > 0 {
		var tags []models.Tag
		for _, tag := range task.Tags {
			var existingTag models.Tag
			if err := tx.Where("name = ?", tag.Name).First(&existingTag).Error; err == nil {
				tags = append(tags, existingTag)
			} else {
				if tag.Color == "" {
					tag.Color = "#3b82f6"
				}
				tags = append(tags, tag)
			}
		}
		task.Tags = tags
	}

	if err := tx.Create(task).Error; err != nil {
		tx.Rollback()
		return nil, errors.InternalServerWithErr("创建任务失败", err)
	}

	if len(task.Dependencies) > 0 {
		if err := s.saveDependencies(tx, task.ID, task.Dependencies); err != nil {
			tx.Rollback()
			return nil, errors.InternalServerWithErr("保存依赖失败", err)
		}
	}

	tx.Commit()

	oldValue, _ := json.Marshal(nil)
	newValue, _ := json.Marshal(task)
	RecordAuditLog(operatorID, operatorName, "create", "task", task.ID, string(oldValue), string(newValue), ip, userAgent)

	return task, nil
}

type TaskUpdateRequest struct {
	Name           *string
	Description    *string
	Type           *models.TaskType
	CronExpression *string
	Params         *string
	Timeout        *int
	MaxRetryCount  *int
	RetryInterval  *int
	Status         *models.TaskStatus
	WebhookURL     *string
	RateLimit      *int
	CircuitBreaker *bool
	Tags           []models.Tag
	Dependencies   []string
}

func (s *TaskService) Update(id string, req *TaskUpdateRequest, operatorID, operatorName, ip, userAgent string) (*models.Task, *errors.AppError) {
	var existing models.Task
	if err := models.DB.Preload("Tags").Preload("DependencyTasks").First(&existing, "id = ?", id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.NotFound("任务不存在")
		}
		return nil, errors.InternalServerWithErr("查询任务失败", err)
	}

	oldValue, _ := json.Marshal(existing)

	if req.Name != nil && *req.Name != existing.Name {
		var nameCheck models.Task
		if err := models.DB.Where("name = ? AND id != ?", *req.Name, id).First(&nameCheck).Error; err == nil {
			return nil, errors.Conflict("任务名称已存在")
		}
		existing.Name = *req.Name
	}

	if req.Description != nil {
		existing.Description = *req.Description
	}
	if req.Type != nil {
		existing.Type = *req.Type
	}
	if req.CronExpression != nil {
		existing.CronExpression = *req.CronExpression
	}
	if req.Params != nil {
		existing.Params = *req.Params
	}
	if req.Timeout != nil {
		existing.Timeout = *req.Timeout
	}
	if req.MaxRetryCount != nil {
		existing.MaxRetryCount = *req.MaxRetryCount
	}
	if req.RetryInterval != nil {
		existing.RetryInterval = *req.RetryInterval
	}
	if req.Status != nil {
		existing.Status = *req.Status
	}
	if req.WebhookURL != nil {
		existing.WebhookURL = *req.WebhookURL
	}
	if req.RateLimit != nil {
		existing.RateLimit = *req.RateLimit
	}
	if req.CircuitBreaker != nil {
		existing.CircuitBreaker = *req.CircuitBreaker
	}

	tx := models.DB.Begin()
	if tx.Error != nil {
		return nil, errors.InternalServerWithErr("启动事务失败", tx.Error)
	}

	if req.Tags != nil {
		var tags []models.Tag
		for _, tag := range req.Tags {
			var existingTag models.Tag
			if err := tx.Where("name = ?", tag.Name).First(&existingTag).Error; err == nil {
				tags = append(tags, existingTag)
			} else {
				if tag.Color == "" {
					tag.Color = "#3b82f6"
				}
				tags = append(tags, tag)
			}
		}
		if err := tx.Model(&existing).Association("Tags").Replace(tags); err != nil {
			tx.Rollback()
			return nil, errors.InternalServerWithErr("更新标签失败", err)
		}
	}

	if req.Dependencies != nil {
		if err := s.saveDependencies(tx, id, req.Dependencies); err != nil {
			tx.Rollback()
			return nil, errors.InternalServerWithErr("保存依赖失败", err)
		}
	}

	if err := tx.Save(&existing).Error; err != nil {
		tx.Rollback()
		return nil, errors.InternalServerWithErr("更新任务失败", err)
	}

	tx.Commit()

	newValue, _ := json.Marshal(existing)
	RecordAuditLog(operatorID, operatorName, "update", "task", id, string(oldValue), string(newValue), ip, userAgent)

	return &existing, nil
}

func (s *TaskService) Delete(id string, operatorID, operatorName, ip, userAgent string) *errors.AppError {
	var task models.Task
	if err := models.DB.First(&task, "id = ?", id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return errors.NotFound("任务不存在")
		}
		return errors.InternalServerWithErr("查询任务失败", err)
	}

	var dependentTasks []models.Task
	models.DB.Raw(`
		SELECT t.* FROM tasks t
		INNER JOIN task_dependencies td ON t.id = td.task_id
		WHERE td.dependency_id = ? AND t.deleted_at IS NULL
	`, id).Scan(&dependentTasks)

	for _, dt := range dependentTasks {
		utils.Logger.Warn("Dependent task will be affected by deletion",
			zap.String("deleted_task_id", id),
			zap.String("deleted_task_name", task.Name),
			zap.String("dependent_task_id", dt.ID),
			zap.String("dependent_task_name", dt.Name),
		)
	}

	tx := models.DB.Begin()
	if tx.Error != nil {
		return errors.InternalServerWithErr("启动事务失败", tx.Error)
	}

	if err := tx.Model(&task).Association("Tags").Clear(); err != nil {
		tx.Rollback()
		return errors.InternalServerWithErr("清除标签关联失败", err)
	}

	if err := tx.Model(&task).Association("DependencyTasks").Clear(); err != nil {
		tx.Rollback()
		return errors.InternalServerWithErr("清除依赖关联失败", err)
	}

	if err := tx.Exec("DELETE FROM task_dependencies WHERE dependency_id = ?", id).Error; err != nil {
		tx.Rollback()
		return errors.InternalServerWithErr("清除反向依赖关联失败", err)
	}

	if err := tx.Delete(&task).Error; err != nil {
		tx.Rollback()
		return errors.InternalServerWithErr("删除任务失败", err)
	}

	tx.Commit()

	oldValue, _ := json.Marshal(task)
	newValue, _ := json.Marshal(map[string]interface{}{
		"affected_dependent_tasks": len(dependentTasks),
		"dependent_task_ids":       dependentTasks,
	})
	RecordAuditLog(operatorID, operatorName, "delete", "task", id, string(oldValue), string(newValue), ip, userAgent)

	return nil
}

func (s *TaskService) GetByID(id string) (*models.Task, error) {
	var task models.Task
	if err := models.DB.Preload("Tags").First(&task, "id = ?", id).Error; err != nil {
		return nil, err
	}

	var dependencies []string
	var depErrors []string
	rows, err := models.DB.Table("task_dependencies").
		Select("dependency_id").
		Where("task_id = ?", id).
		Rows()
	if err == nil {
		func() {
			defer rows.Close()
			for rows.Next() {
				var depID string
				if err := rows.Scan(&depID); err == nil {
					dependencies = append(dependencies, depID)

					var depTask models.Task
					if err := models.DB.Where("id = ?", depID).First(&depTask).Error; err != nil {
						if err == gorm.ErrRecordNotFound {
							depErrors = append(depErrors, fmt.Sprintf("依赖任务 %s 不存在或已被删除", depID))
						}
					}
				}
			}
		}()
	}
	task.Dependencies = dependencies
	task.DependencyErrors = depErrors

	return &task, nil
}

func (s *TaskService) List(page, pageSize int, keyword string, tagIDs []string, status string) ([]models.Task, int64, *errors.AppError) {
	var tasks []models.Task
	var total int64

	query := models.DB.Model(&models.Task{}).Preload("Tags")

	if keyword != "" {
		query = query.Where("name LIKE ? OR description LIKE ?", "%"+keyword+"%", "%"+keyword+"%")
	}

	if status != "" {
		query = query.Where("status = ?", status)
	}

	if len(tagIDs) > 0 {
		query = query.Joins("JOIN task_tags ON tasks.id = task_tags.task_id").
			Where("task_tags.tag_id IN ?", tagIDs)
	}

	if err := query.Count(&total).Error; err != nil {
		return nil, 0, errors.InternalServerWithErr("统计任务数量失败", err)
	}

	offset := (page - 1) * pageSize
	if err := query.Offset(offset).Limit(pageSize).Order("created_at desc").Find(&tasks).Error; err != nil {
		return nil, 0, errors.InternalServerWithErr("查询任务列表失败", err)
	}

	for i := range tasks {
		var dependencies []string
		rows, err := models.DB.Table("task_dependencies").
			Select("dependency_id").
			Where("task_id = ?", tasks[i].ID).
			Rows()
		if err == nil {
			func() {
				defer rows.Close()
				for rows.Next() {
					var depID string
					if err := rows.Scan(&depID); err == nil {
						dependencies = append(dependencies, depID)
					}
				}
			}()
		}
		tasks[i].Dependencies = dependencies
	}

	return tasks, total, nil
}

func (s *TaskService) GetAllActiveTasks() ([]*models.Task, error) {
	var tasks []*models.Task
	if err := models.DB.Preload("Tags").
		Where("status IN ?", []models.TaskStatus{models.TaskStatusPending, models.TaskStatusRunning}).
		Find(&tasks).Error; err != nil {
		return nil, err
	}

	for _, task := range tasks {
		var dependencies []string
		rows, err := models.DB.Table("task_dependencies").
			Select("dependency_id").
			Where("task_id = ?", task.ID).
			Rows()
		if err == nil {
			func() {
				defer rows.Close()
				for rows.Next() {
					var depID string
					if err := rows.Scan(&depID); err == nil {
						dependencies = append(dependencies, depID)
					}
				}
			}()
		}
		task.Dependencies = dependencies
	}

	return tasks, nil
}

func (s *TaskService) UpdateStatus(id string, status models.TaskStatus, operatorID, operatorName, ip, userAgent string) *errors.AppError {
	var task models.Task
	if err := models.DB.First(&task, "id = ?", id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return errors.NotFound("任务不存在")
		}
		return errors.InternalServerWithErr("查询任务失败", err)
	}

	oldStatus := task.Status
	task.Status = status

	if err := models.DB.Save(&task).Error; err != nil {
		return errors.InternalServerWithErr("更新状态失败", err)
	}

	oldValue, _ := json.Marshal(map[string]interface{}{"status": oldStatus})
	newValue, _ := json.Marshal(map[string]interface{}{"status": status})
	RecordAuditLog(operatorID, operatorName, "update_status", "task", id, string(oldValue), string(newValue), ip, userAgent)

	return nil
}

func (s *TaskService) GetTaskLogs(taskID string, page, pageSize int) ([]models.TaskLog, int64, *errors.AppError) {
	var logs []models.TaskLog
	var total int64

	query := models.DB.Model(&models.TaskLog{}).Where("task_id = ?", taskID)

	if err := query.Count(&total).Error; err != nil {
		return nil, 0, errors.InternalServerWithErr("统计日志数量失败", err)
	}

	offset := (page - 1) * pageSize
	if err := query.Offset(offset).Limit(pageSize).Order("created_at desc").Find(&logs).Error; err != nil {
		return nil, 0, errors.InternalServerWithErr("查询日志失败", err)
	}

	return logs, total, nil
}

func (s *TaskService) saveDependencies(tx *gorm.DB, taskID string, dependencies []string) error {
	if err := tx.Exec("DELETE FROM task_dependencies WHERE task_id = ?", taskID).Error; err != nil {
		return fmt.Errorf("删除旧依赖失败: %w", err)
	}

	for _, depID := range dependencies {
		var depTask models.Task
		if err := tx.First(&depTask, "id = ?", depID).Error; err != nil {
			return fmt.Errorf("依赖任务不存在: %s", depID)
		}

		if depID == taskID {
			return fmt.Errorf("不能依赖自己")
		}

		if err := tx.Exec("INSERT INTO task_dependencies (task_id, dependency_id) VALUES (?, ?)", taskID, depID).Error; err != nil {
			return fmt.Errorf("插入依赖失败: %w", err)
		}
	}

	return nil
}

func RecordAuditLog(userID, username, action, resource, resourceID, oldValue, newValue, ip, userAgent string) {
	auditLog := &models.AuditLog{
		UserID:     userID,
		Username:   username,
		Action:     action,
		Resource:   resource,
		ResourceID: resourceID,
		OldValue:   oldValue,
		NewValue:   newValue,
		IPAddress:  ip,
		UserAgent:  userAgent,
		CreatedAt:  time.Now(),
	}

	if err := models.DB.Create(auditLog).Error; err != nil {
		utils.Logger.Error("Failed to create audit log", zap.Error(err))
	}
}
