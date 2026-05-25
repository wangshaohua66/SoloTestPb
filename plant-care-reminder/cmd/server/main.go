package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"plant-care-reminder/config"
	"plant-care-reminder/internal/handler"
	"plant-care-reminder/internal/middleware"
	"plant-care-reminder/internal/scheduler"
	"plant-care-reminder/internal/service"
	"plant-care-reminder/internal/storage"
	"plant-care-reminder/pkg/concurrency"
	"plant-care-reminder/pkg/logger"
	"plant-care-reminder/pkg/reminder"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "server failed: %v\n", err)
		os.Exit(1)
	}
}

func run() error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("load config failed: %w", err)
	}

	if err := logger.Init(); err != nil {
		return fmt.Errorf("init logger failed: %w", err)
	}
	defer logger.Close()

	concurrency.Init()

	store, err := storage.NewJSONStore(&cfg.Storage)
	if err != nil {
		return fmt.Errorf("init storage failed: %w", err)
	}

	reminderEng := reminder.NewEngine(&cfg.Reminder, store)

	plantService := service.NewPlantService(store, reminderEng, &cfg.Reminder)
	reminderService := service.NewReminderService(store, reminderEng)

	plantHandler := handler.NewPlantHandler(plantService)
	reminderHandler := handler.NewReminderHandler(reminderService)

	sched := scheduler.NewScheduler(&cfg.Reminder, reminderService, plantService)

	gin.SetMode(gin.ReleaseMode)
	r := gin.New()

	r.Use(middleware.Recovery())
	r.Use(middleware.Logger())
	r.Use(middleware.CORS())
	r.Use(middleware.RequestID())
	r.Use(middleware.RateLimit())
	r.Use(middleware.ErrorHandler())

	api := r.Group("/api/v1")
	{
		health := api.Group("/health")
		{
			health.GET("", func(c *gin.Context) {
				c.JSON(http.StatusOK, gin.H{
					"status": "ok",
					"time":   time.Now(),
				})
			})
		}

		plants := api.Group("/plants")
		{
			plants.GET("", plantHandler.GetAllPlants)
			plants.POST("", plantHandler.CreatePlant)
			plants.GET("/:id", plantHandler.GetPlantByID)
			plants.PUT("/:id", plantHandler.UpdatePlant)
			plants.DELETE("/:id", plantHandler.DeletePlant)
			plants.GET("/:id/status", plantHandler.GetPlantStatus)
			plants.POST("/:id/care", plantHandler.PerformCareOperation)
		}

		reminders := api.Group("/reminders")
		{
			reminders.GET("", reminderHandler.GetAllReminders)
			reminders.GET("/pending", reminderHandler.GetPendingReminders)
			reminders.GET("/stats", reminderHandler.GetReminderStats)
			reminders.POST("/generate", reminderHandler.GenerateReminders)
			reminders.POST("/check", reminderHandler.CheckReminders)
			reminders.GET("/:id", reminderHandler.GetReminderByID)
			reminders.PUT("/:id/complete", reminderHandler.MarkReminderCompleted)
			reminders.DELETE("/:id", reminderHandler.DeleteReminder)
			reminders.GET("/plant/:plant_id", reminderHandler.GetRemindersByPlantID)
		}

		history := api.Group("/history")
		{
			history.GET("", plantHandler.GetCareHistory)
		}
	}

	addr := fmt.Sprintf(":%d", cfg.Server.Port)
	srv := &http.Server{
		Addr:         addr,
		Handler:      r,
		ReadTimeout:  time.Duration(cfg.Server.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(cfg.Server.WriteTimeout) * time.Second,
		IdleTimeout:  time.Duration(cfg.Server.IdleTimeout) * time.Second,
	}

	go func() {
		logger.Info("Starting HTTP server", map[string]interface{}{"addr": addr})
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Server failed to start", err)
		}
	}()

	if err := sched.Start(); err != nil {
		logger.Error("Failed to start scheduler", err)
	}
	defer sched.Stop()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", err)
		return err
	}

	logger.Info("Server exited gracefully")
	return nil
}
