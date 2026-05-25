package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"task-scheduler/internal/config"
	"task-scheduler/internal/handlers"
	"task-scheduler/internal/models"
	"task-scheduler/internal/services"
	"task-scheduler/pkg/utils"
	"task-scheduler/pkg/validator"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	configPath := "config.yaml"
	if len(os.Args) > 1 {
		configPath = os.Args[1]
	}

	if err := config.Load(configPath); err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}

	if err := utils.InitLogger(config.AppConfig.Log.Level, config.AppConfig.Log.Filename); err != nil {
		fmt.Printf("Failed to init logger: %v\n", err)
		os.Exit(1)
	}
	defer utils.SyncLogger()

	if err := models.InitDB(); err != nil {
		utils.Logger.Fatal("Failed to init database", zap.Error(err))
	}

	if err := validator.Init(); err != nil {
		utils.Logger.Fatal("Failed to init validator", zap.Error(err))
	}

	scheduler := services.GetScheduler()
	if err := scheduler.Start(); err != nil {
		utils.Logger.Fatal("Failed to start scheduler", zap.Error(err))
	}
	defer scheduler.Stop()

	gin.SetMode(config.AppConfig.Server.Mode)
	r := handlers.SetupRouter()

	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", config.AppConfig.Server.Port),
		Handler: r,
	}

	go func() {
		utils.Logger.Info("Server starting", zap.Int("port", config.AppConfig.Server.Port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			utils.Logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	utils.Logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		utils.Logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	utils.Logger.Info("Server exited")
}
