package handlers

import (
	"task-scheduler/internal/middleware"

	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	r := gin.New()

	r.Use(middleware.Logger())
	r.Use(middleware.Recovery())
	r.Use(middleware.CORS())

	api := r.Group("/api/v1")
	api.Use(middleware.Auth())
	{
		taskHandler := NewTaskHandler()
		tasks := api.Group("/tasks")
		{
			tasks.POST("", taskHandler.Create)
			tasks.PUT("/:id", taskHandler.Update)
			tasks.DELETE("/:id", taskHandler.Delete)
			tasks.GET("/:id", taskHandler.Get)
			tasks.GET("", taskHandler.List)
			tasks.PATCH("/:id/status", taskHandler.UpdateStatus)
			tasks.POST("/:id/trigger", taskHandler.Trigger)
			tasks.GET("/:id/logs", taskHandler.GetLogs)
		}

		api.POST("/cron/validate", taskHandler.ValidateCron)

		tagHandler := NewTagHandler()
		tags := api.Group("/tags")
		{
			tags.POST("", tagHandler.Create)
			tags.PUT("/:id", tagHandler.Update)
			tags.DELETE("/:id", tagHandler.Delete)
			tags.GET("", tagHandler.List)
		}
	}

	return r
}
