package handlers

import (
	"strconv"
	"task-scheduler/internal/middleware"
	"task-scheduler/internal/models"
	"task-scheduler/internal/services"
	"task-scheduler/pkg/errors"
	"task-scheduler/pkg/utils"
	"task-scheduler/pkg/validator"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
	"gorm.io/gorm"
)

type TaskHandler struct {
	taskService *services.TaskService
	scheduler   *services.Scheduler
}

func NewTaskHandler() *TaskHandler {
	return &TaskHandler{
		taskService: services.NewTaskService(),
		scheduler:   services.GetScheduler(),
	}
}

func (h *TaskHandler) Create(c *gin.Context) {
	var task models.Task
	if err := c.ShouldBindJSON(&task); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	if err := validator.Struct(&task); err != nil {
		utils.Fail(c, err)
		return
	}

	userID, username := middleware.GetUserInfo(c)
	ip := c.ClientIP()
	userAgent := c.Request.UserAgent()

	createdTask, appErr := h.taskService.Create(&task, userID, username, ip, userAgent)
	if appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	if createdTask.Status == models.TaskStatusPending || createdTask.Status == models.TaskStatusRunning {
		if err := h.scheduler.RegisterTask(createdTask); err != nil {
			utils.Logger.Error("Failed to register task to scheduler", zap.Error(err))
		}
	}

	utils.Success(c, createdTask)
}

func (h *TaskHandler) Update(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	var req TaskUpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	if err := validator.Struct(&req); err != nil {
		utils.Fail(c, err)
		return
	}

	if req.CronExpression != nil {
		if err := validator.Validate.Var(*req.CronExpression, "cron"); err != nil {
			utils.Fail(c, errors.BadRequest("无效的 Cron 表达式"))
			return
		}
	}

	serviceReq := &services.TaskUpdateRequest{
		Name:           req.Name,
		Description:    req.Description,
		Type:           req.Type,
		CronExpression: req.CronExpression,
		Params:         req.Params,
		Timeout:        req.Timeout,
		MaxRetryCount:  req.MaxRetryCount,
		RetryInterval:  req.RetryInterval,
		Status:         req.Status,
		WebhookURL:     req.WebhookURL,
		RateLimit:      req.RateLimit,
		CircuitBreaker: req.CircuitBreaker,
		Tags:           req.Tags,
		Dependencies:   req.Dependencies,
	}

	userID, username := middleware.GetUserInfo(c)
	ip := c.ClientIP()
	userAgent := c.Request.UserAgent()

	updatedTask, appErr := h.taskService.Update(id, serviceReq, userID, username, ip, userAgent)
	if appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	h.scheduler.UnregisterTask(id)
	if updatedTask.Status == models.TaskStatusPending || updatedTask.Status == models.TaskStatusRunning {
		if err := h.scheduler.RegisterTask(updatedTask); err != nil {
			utils.Logger.Error("Failed to register task to scheduler", zap.Error(err))
		}
	}

	utils.Success(c, updatedTask)
}

func (h *TaskHandler) Delete(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	userID, username := middleware.GetUserInfo(c)
	ip := c.ClientIP()
	userAgent := c.Request.UserAgent()

	if appErr := h.taskService.Delete(id, userID, username, ip, userAgent); appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	h.scheduler.UnregisterTask(id)

	utils.SuccessWithMessage(c, "删除成功", nil)
}

func (h *TaskHandler) Get(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	task, err := h.taskService.GetByID(id)
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			utils.Fail(c, errors.NotFound("任务不存在"))
			return
		}
		utils.Fail(c, errors.InternalServerWithErr("查询任务失败", err))
		return
	}

	utils.Success(c, task)
}

func (h *TaskHandler) List(c *gin.Context) {
	page, pageSize := getPagination(c)
	keyword := c.Query("keyword")
	status := c.Query("status")
	tagIDs := c.QueryArray("tag_ids")

	tasks, total, appErr := h.taskService.List(page, pageSize, keyword, tagIDs, status)
	if appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	utils.Paginated(c, tasks, page, pageSize, total)
}

func (h *TaskHandler) UpdateStatus(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	var req struct {
		Status models.TaskStatus `json:"status" binding:"required,oneof=pending running paused cancelled"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	userID, username := middleware.GetUserInfo(c)
	ip := c.ClientIP()
	userAgent := c.Request.UserAgent()

	if appErr := h.taskService.UpdateStatus(id, req.Status, userID, username, ip, userAgent); appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	if req.Status == models.TaskStatusPaused || req.Status == models.TaskStatusCancelled {
		h.scheduler.UnregisterTask(id)
	} else if req.Status == models.TaskStatusPending || req.Status == models.TaskStatusRunning {
		task, err := h.taskService.GetByID(id)
		if err == nil {
			h.scheduler.RegisterTask(task)
		}
	}

	utils.SuccessWithMessage(c, "状态更新成功", nil)
}

func (h *TaskHandler) Trigger(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	if err := h.scheduler.TriggerTask(id); err != nil {
		utils.Fail(c, errors.BadRequest(err.Error()))
		return
	}

	utils.SuccessWithMessage(c, "任务已触发", nil)
}

func (h *TaskHandler) GetLogs(c *gin.Context) {
	taskID := c.Param("id")
	if taskID == "" {
		utils.Fail(c, errors.BadRequest("任务ID不能为空"))
		return
	}

	page, pageSize := getPagination(c)

	logs, total, appErr := h.taskService.GetTaskLogs(taskID, page, pageSize)
	if appErr != nil {
		utils.Fail(c, appErr)
		return
	}

	utils.Paginated(c, logs, page, pageSize, total)
}

func (h *TaskHandler) ValidateCron(c *gin.Context) {
	var req struct {
		Expression string `json:"expression" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	if err := validator.Validate.Var(req.Expression, "cron"); err != nil {
		utils.Fail(c, errors.BadRequest("无效的 Cron 表达式"))
		return
	}

	utils.Success(c, gin.H{"valid": true})
}

func getPagination(c *gin.Context) (int, int) {
	page := 1
	pageSize := 10

	if p := c.Query("page"); p != "" {
		if val, err := strconv.Atoi(p); err == nil && val > 0 {
			page = val
		}
	}

	if ps := c.Query("page_size"); ps != "" {
		if val, err := strconv.Atoi(ps); err == nil && val > 0 {
			pageSize = val
			if pageSize > 100 {
				pageSize = 100
			}
		}
	}

	return page, pageSize
}
