package handler

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"plant-care-reminder/internal/service"
	"plant-care-reminder/pkg/logger"
)

type ReminderHandler struct {
	reminderService *service.ReminderService
}

func NewReminderHandler(reminderService *service.ReminderService) *ReminderHandler {
	return &ReminderHandler{
		reminderService: reminderService,
	}
}

func (h *ReminderHandler) GetAllReminders(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	status := c.Query("status")
	reminders, err := h.reminderService.GetAllReminders(ctx, status)
	if err != nil {
		logger.Error("Failed to get reminders", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get reminders",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data":  reminders,
		"count": len(reminders),
	})
}

func (h *ReminderHandler) GetReminderByID(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	reminder, err := h.reminderService.GetReminderByID(ctx, id)
	if err != nil {
		if err.Error() == "reminder not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to get reminder", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get reminder",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": reminder})
}

func (h *ReminderHandler) GetRemindersByPlantID(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	plantID := c.Param("plant_id")
	reminders, err := h.reminderService.GetRemindersByPlantID(ctx, plantID)
	if err != nil {
		logger.Error("Failed to get reminders for plant", err, map[string]interface{}{"plant_id": plantID})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get reminders",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data":  reminders,
		"count": len(reminders),
	})
}

func (h *ReminderHandler) GetPendingReminders(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	reminders, err := h.reminderService.GetPendingReminders(ctx)
	if err != nil {
		logger.Error("Failed to get pending reminders", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get pending reminders",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data":  reminders,
		"count": len(reminders),
	})
}

func (h *ReminderHandler) GenerateReminders(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	reminders, err := h.reminderService.GenerateReminders(ctx)
	if err != nil {
		logger.Error("Failed to generate reminders", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to generate reminders",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":          "reminders generated successfully",
		"new_reminders":    len(reminders),
		"data":             reminders,
	})
}

func (h *ReminderHandler) MarkReminderCompleted(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	reminder, err := h.reminderService.MarkReminderCompleted(ctx, id)
	if err != nil {
		if err.Error() == "reminder not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to mark reminder completed", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to mark reminder completed",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "reminder marked as completed",
		"data":    reminder,
	})
}

func (h *ReminderHandler) DeleteReminder(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	if err := h.reminderService.DeleteReminder(ctx, id); err != nil {
		if err.Error() == "reminder not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to delete reminder", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to delete reminder",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "reminder deleted successfully",
	})
}

func (h *ReminderHandler) CheckReminders(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	h.reminderService.CheckAndUpdateReminders(ctx)

	overdue := h.reminderService.GetOverdueReminders(ctx)

	c.JSON(http.StatusOK, gin.H{
		"message":           "reminder check completed",
		"overdue_reminders": len(overdue),
		"overdue":           overdue,
	})
}

func (h *ReminderHandler) GetReminderStats(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	stats, err := h.reminderService.GetReminderStats(ctx)
	if err != nil {
		logger.Error("Failed to get reminder stats", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get reminder stats",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": stats})
}
