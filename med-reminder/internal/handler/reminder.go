package handler

import (
	"net/http"
	"strconv"

	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

type ReminderHandler struct {
	svc *service.ReminderService
}

func NewReminderHandler(svc *service.ReminderService) *ReminderHandler {
	return &ReminderHandler{svc: svc}
}

func (h *ReminderHandler) Register(r *gin.RouterGroup) {
	g := r.Group("/reminders")
	{
		g.GET("", h.List)
		g.GET("/:id", h.Get)
		g.POST("/:id/acknowledge", h.Acknowledge)
		g.POST("/:id/skip", h.Skip)
	}
}

func (h *ReminderHandler) List(c *gin.Context) {
	userID := c.GetString("user_id")
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
	list, err := h.svc.ListByUser(c.Request.Context(), userID, limit, offset)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, list)
}

func (h *ReminderHandler) Get(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	list, err := h.svc.ListByUser(c.Request.Context(), userID, 1, 0)
	if err != nil {
		RespondError(c, err)
		return
	}
	for _, rm := range list {
		if rm.ID == id {
			c.JSON(http.StatusOK, rm)
			return
		}
	}
	c.AbortWithStatusJSON(http.StatusNotFound, gin.H{"error": "reminder not found"})
}

func (h *ReminderHandler) Acknowledge(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	if err := h.svc.Acknowledge(c.Request.Context(), id, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "acknowledged"})
}

type skipRequest struct {
	Reason string `json:"reason"`
}

func (h *ReminderHandler) Skip(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	var req skipRequest
	_ = c.ShouldBindJSON(&req)
	if err := h.svc.Skip(c.Request.Context(), id, userID, req.Reason); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "skipped"})
}
