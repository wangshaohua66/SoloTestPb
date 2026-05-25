package handler

import (
	"net/http"
	"strconv"
	"time"

	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

type AnalyticsHandler struct {
	svc *service.AnalyticsService
}

func NewAnalyticsHandler(svc *service.AnalyticsService) *AnalyticsHandler {
	return &AnalyticsHandler{svc: svc}
}

func (h *AnalyticsHandler) Register(r *gin.RouterGroup) {
	g := r.Group("/analytics")
	{
		g.GET("/adherence", h.Adherence)
		g.GET("/history", h.History)
	}
}

func (h *AnalyticsHandler) Adherence(c *gin.Context) {
	userID := c.GetString("user_id")
	var window time.Duration
	if v := c.Query("days"); v != "" {
		if d, err := strconv.Atoi(v); err == nil && d > 0 {
			window = time.Duration(d) * 24 * time.Hour
		}
	}
	report, err := h.svc.AdherenceReport(c.Request.Context(), userID, window)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, report)
}

func (h *AnalyticsHandler) History(c *gin.Context) {
	userID := c.GetString("user_id")
	var from, to time.Time
	if v := c.Query("from"); v != "" {
		if t, err := time.Parse(time.RFC3339, v); err == nil {
			from = t
		}
	}
	if v := c.Query("to"); v != "" {
		if t, err := time.Parse(time.RFC3339, v); err == nil {
			to = t
		}
	}
	logs, err := h.svc.History(c.Request.Context(), userID, from, to)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, logs)
}
