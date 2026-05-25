package handler

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"plant-care-reminder/internal/model"
	"plant-care-reminder/internal/service"
	"plant-care-reminder/pkg/logger"
	"plant-care-reminder/pkg/validator"
)

type PlantHandler struct {
	plantService *service.PlantService
}

func NewPlantHandler(plantService *service.PlantService) *PlantHandler {
	return &PlantHandler{
		plantService: plantService,
	}
}

func (h *PlantHandler) GetAllPlants(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	plants, err := h.plantService.GetAllPlants(ctx)
	if err != nil {
		logger.Error("Failed to get plants", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get plants",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data":  plants,
		"count": len(plants),
	})
}

func (h *PlantHandler) GetPlantByID(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	plant, err := h.plantService.GetPlantByID(ctx, id)
	if err != nil {
		if err.Error() == "plant not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to get plant", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get plant",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": plant})
}

func (h *PlantHandler) CreatePlant(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	var req model.CreatePlantRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		logger.Error("Invalid request body", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid request body",
			"message": err.Error(),
		})
		return
	}

	plant, err := h.plantService.CreatePlant(ctx, &req)
	if err != nil {
		if verrs, ok := err.(validator.ValidationErrors); ok {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":              "validation failed",
				"validation_errors":  verrs.Error(),
			})
			return
		}
		logger.Error("Failed to create plant", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to create plant",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message": "plant created successfully",
		"data":    plant,
	})
}

func (h *PlantHandler) UpdatePlant(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	var req model.UpdatePlantRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		logger.Error("Invalid request body", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid request body",
			"message": err.Error(),
		})
		return
	}

	plant, err := h.plantService.UpdatePlant(ctx, id, &req)
	if err != nil {
		if verrs, ok := err.(validator.ValidationErrors); ok {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":              "validation failed",
				"validation_errors":  verrs.Error(),
			})
			return
		}
		if err.Error() == "plant not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to update plant", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to update plant",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "plant updated successfully",
		"data":    plant,
	})
}

func (h *PlantHandler) DeletePlant(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	if err := h.plantService.DeletePlant(ctx, id); err != nil {
		if err.Error() == "plant not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to delete plant", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to delete plant",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "plant deleted successfully",
	})
}

func (h *PlantHandler) PerformCareOperation(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	var req model.CareOperationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		logger.Error("Invalid request body", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "invalid request body",
			"message": err.Error(),
		})
		return
	}

	history, err := h.plantService.PerformCareOperation(ctx, id, &req)
	if err != nil {
		if verrs, ok := err.(validator.ValidationErrors); ok {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":              "validation failed",
				"validation_errors":  verrs.Error(),
			})
			return
		}
		if err.Error() == "plant not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to perform care operation", err, map[string]interface{}{
			"plant_id":  id,
			"operation": req.Operation,
		})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to perform care operation",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "care operation recorded successfully",
		"data":    history,
	})
}

func (h *PlantHandler) GetCareHistory(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	plantID := c.Query("plant_id")
	history, err := h.plantService.GetCareHistory(ctx, plantID)
	if err != nil {
		logger.Error("Failed to get care history", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get care history",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data":  history,
		"count": len(history),
	})
}

func (h *PlantHandler) GetPlantStatus(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	id := c.Param("id")
	status, err := h.plantService.GetPlantStatus(ctx, id)
	if err != nil {
		if err.Error() == "plant not found: "+id {
			c.JSON(http.StatusNotFound, gin.H{
				"error":   "not found",
				"message": err.Error(),
			})
			return
		}
		logger.Error("Failed to get plant status", err, map[string]interface{}{"id": id})
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "failed to get plant status",
			"message": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": status})
}
