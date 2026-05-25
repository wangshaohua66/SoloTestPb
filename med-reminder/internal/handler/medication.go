package handler

import (
	"net/http"

	"med-reminder/internal/models"
	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

type MedicationHandler struct {
	svc *service.MedicationService
}

func NewMedicationHandler(svc *service.MedicationService) *MedicationHandler {
	return &MedicationHandler{svc: svc}
}

func (h *MedicationHandler) Register(r *gin.RouterGroup) {
	g := r.Group("/medications")
	{
		g.POST("", h.Create)
		g.GET("", h.List)
		g.GET("/alerts/low-stock", h.LowStock)
		g.GET("/:id", h.Get)
		g.PUT("/:id", h.Update)
		g.DELETE("/:id", h.Delete)
	}
}

func (h *MedicationHandler) Create(c *gin.Context) {
	userID := c.GetString("user_id")
	var m models.Medication
	if err := c.ShouldBindJSON(&m); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	m.UserID = userID
	if err := h.svc.Create(c.Request.Context(), &m); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusCreated, m)
}

func (h *MedicationHandler) List(c *gin.Context) {
	userID := c.GetString("user_id")
	include := c.Query("include_expired") == "true"
	list, err := h.svc.List(c.Request.Context(), userID, include)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, list)
}

func (h *MedicationHandler) Get(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	m, err := h.svc.Get(c.Request.Context(), id, userID)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, m)
}

func (h *MedicationHandler) Update(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	var m models.Medication
	if err := c.ShouldBindJSON(&m); err != nil {
		c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	m.ID = id
	if err := h.svc.Update(c.Request.Context(), &m, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, m)
}

func (h *MedicationHandler) Delete(c *gin.Context) {
	userID := c.GetString("user_id")
	id := c.Param("id")
	if err := h.svc.Delete(c.Request.Context(), id, userID); err != nil {
		RespondError(c, err)
		return
	}
	c.Status(http.StatusNoContent)
}

func (h *MedicationHandler) LowStock(c *gin.Context) {
	userID := c.GetString("user_id")
	list, err := h.svc.LowStock(c.Request.Context(), userID)
	if err != nil {
		RespondError(c, err)
		return
	}
	c.JSON(http.StatusOK, list)
}
