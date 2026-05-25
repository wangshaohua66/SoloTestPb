package handler

import (
	"net/http"
	"strconv"
	"time"

	"med-reminder/internal/models"
	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

type ScheduleHandler struct {
	svc *service.ScheduleService
}

func NewScheduleHandler(svc *service.ScheduleService) *ScheduleHandler {
	return &ScheduleHandler{svc: svc}
}

func (h *ScheduleHandler) Register(r *gin.RouterGroup) {
	g := r.Group("/schedules")
	{
		g.POST("", h.Create)
		g.GET("", h.List)
		g.GET("/:id", h.Get)
		g.PUT("/:id", h.Update)
		g.DELETE("/:id", h.Delete)
		g.GET("/:id/upcoming", h.Upcoming)
	}
}

func (h *ScheduleHandler) Create(c *gin.Context) {
	userID := c.GetString("user_id")
	var sc models.ReminderSchedule
	if err := c.ShouldBindJSON(&sc); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := h.svc.Create(c.Request.Context(), &sc, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusCreated, sc)
}

func (h *ScheduleHandler) List(c *gin.Context) {
	userID := c.GetString("user_id")
	medID := c.Query("medication_id")
	var (
		list []models.ReminderSchedule
		err  error
	)
	if medID != "" {
		list, err = h.svc.ListByMedication(c.Request.Context(), medID, userID)
	} else {
		list, err = h.svc.ListByUser(c.Request.Context(), userID)
	}
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, list)
}

func (h *ScheduleHandler) Get(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	sc, err := h.svc.Get(c.Request.Context(), id, userID)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, sc)
}

func (h *ScheduleHandler) Update(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	var sc models.ReminderSchedule
	if err := c.ShouldBindJSON(&sc); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	sc.ID = id
	if err := h.svc.Update(c.Request.Context(), &sc, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, sc)
}

func (h *ScheduleHandler) Delete(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	if err := h.svc.Delete(c.Request.Context(), id, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.Status(http.StatusNoContent)
}

func (h *ScheduleHandler) Upcoming(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	sc, err := h.svc.Get(c.Request.Context(), id, userID)
	if err != nil {
		RespondError(c, err)
		return
	}
	days := 7
	if v := c.Query("days"); v != "" {
		if n, err := parseInt(v); err == nil && n > 0 && n <= 365 {
			days = n
		}
	}
	from := time.Now()
	to := from.AddDate(0, 0, days)
	times, err := h.svc.GenerateUpcoming(c.Request.Context(), sc, from, to)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"schedule_id": id, "upcoming": times})
}

func parseInt(s string) (int, error) {
	return strconv.Atoi(s)
}
