package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"med-reminder/internal/config"
	"med-reminder/internal/db"
	"med-reminder/internal/handler"
	"med-reminder/internal/logger"
	"med-reminder/internal/repository"
	"med-reminder/internal/scheduler"
	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "fatal: %v\n", err)
		os.Exit(1)
	}
}

func run() error {
	cfgPath := "config.yaml"
	if v := os.Getenv("CONFIG_PATH"); v != "" {
		cfgPath = v
	}
	cfg, err := config.Load(cfgPath)
	if err != nil {
		return fmt.Errorf("load config: %w", err)
	}

	if err := logger.Init(cfg.Logging); err != nil {
		return fmt.Errorf("init logger: %w", err)
	}
	defer logger.Sync()

	loc, err := time.LoadLocation(cfg.Server.Timezone)
	if err != nil {
		return fmt.Errorf("load timezone %s: %w", cfg.Server.Timezone, err)
	}
	logger.S().Infow("timezone loaded", "timezone", cfg.Server.Timezone)

	database, err := db.New(cfg.Database, loc)
	if err != nil {
		return fmt.Errorf("init database: %w", err)
	}
	defer database.Close()

	medRepo := repository.NewMedicationRepo(database)
	schedRepo := repository.NewScheduleRepo(database)
	remRepo := repository.NewReminderRepo(database)
	logRepo := repository.NewLogRepo(database)

	medSvc := service.NewMedicationService(medRepo, loc)

	schedSvc := service.NewScheduleService(schedRepo, medRepo, remRepo, loc,
		cfg.Reminder.MaxRemindersPerMed, cfg.Reminder.DefaultLeadMinutes)

	remSvc := service.NewReminderService(remRepo, schedRepo, medRepo, logRepo, schedSvc,
		service.LogDispatcher{}, loc,
		cfg.Reminder.MaxRetry, cfg.Reminder.ConflictMergeWindowMin, cfg.Reminder.DispatchWorkers)

	analyticsSvc := service.NewAnalyticsService(logRepo, medRepo,
		cfg.Analytics.AdherenceWindowDays, cfg.Analytics.MissRiskThreshold, loc)

	medH := handler.NewMedicationHandler(medSvc)
	schedH := handler.NewScheduleHandler(schedSvc)
	remH := handler.NewReminderHandler(remSvc)
	analyticsH := handler.NewAnalyticsHandler(analyticsSvc)

	gin.SetMode(cfg.Server.Mode)
	engine := gin.New()
	engine.Use(handler.Recovery(), handler.RequestID(), handler.AccessLog(), handler.ErrorHandler())

	api := engine.Group("/api/v1")
	api.Use(handler.ResolveUser())
	{
		medH.Register(api)
		schedH.Register(api)
		remH.Register(api)
		analyticsH.Register(api)
	}

	engine.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "time": time.Now().In(loc).Format(time.RFC3339)})
	})

	sched := scheduler.New(remSvc, medSvc, database,
		cfg.Reminder.CheckFrequency, cfg.Database.BackupInterval,
		cfg.Reminder.MissedWindow)
	sched.Start()
	defer sched.Stop()

	srv := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Server.Port),
		Handler:      engine,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
	}

	errCh := make(chan error, 1)
	go func() {
		logger.S().Infow("server starting", "port", cfg.Server.Port, "mode", cfg.Server.Mode)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			errCh <- err
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	select {
	case err := <-errCh:
		return fmt.Errorf("server error: %w", err)
	case sig := <-quit:
		logger.S().Infow("shutting down", "signal", sig)
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := srv.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("server shutdown: %w", err)
	}
	logger.S().Info("server stopped gracefully")
	return nil
}
