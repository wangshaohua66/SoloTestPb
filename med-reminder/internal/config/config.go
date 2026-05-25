package config

import (
	"fmt"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Server    ServerConfig    `mapstructure:"server"`
	Database  DatabaseConfig  `mapstructure:"database"`
	Reminder  ReminderConfig  `mapstructure:"reminder"`
	Logging   LoggingConfig   `mapstructure:"logging"`
	Analytics AnalyticsConfig `mapstructure:"analytics"`
}

type ServerConfig struct {
	Port         int           `mapstructure:"port"`
	Mode         string        `mapstructure:"mode"`
	ReadTimeout  time.Duration `mapstructure:"read_timeout"`
	WriteTimeout time.Duration `mapstructure:"write_timeout"`
	Timezone     string        `mapstructure:"timezone"`
}

type DatabaseConfig struct {
	Path           string        `mapstructure:"path"`
	BackupPath     string        `mapstructure:"backup_path"`
	BackupInterval time.Duration `mapstructure:"backup_interval"`
	MaxBackups     int           `mapstructure:"max_backups"`
}

type ReminderConfig struct {
	CheckFrequency            time.Duration `mapstructure:"check_frequency"`
	DefaultLeadMinutes        int           `mapstructure:"default_lead_minutes"`
	MaxRemindersPerMed        int           `mapstructure:"max_reminders_per_med"`
	ConflictMergeWindowMin    int           `mapstructure:"conflict_merge_window_minutes"`
	DispatchWorkers           int           `mapstructure:"dispatch_workers"`
	MaxRetry                  int           `mapstructure:"max_retry"`
	MissedWindow              time.Duration `mapstructure:"missed_window"`
}

type LoggingConfig struct {
	Level       string `mapstructure:"level"`
	File        string `mapstructure:"file"`
	MaxSizeMB   int    `mapstructure:"max_size_mb"`
	MaxBackups  int    `mapstructure:"max_backups"`
	MaxAgeDays  int    `mapstructure:"max_age_days"`
}

type AnalyticsConfig struct {
	AdherenceWindowDays int     `mapstructure:"adherence_window_days"`
	MissRiskThreshold   float64 `mapstructure:"miss_risk_threshold"`
}

func Load(path string) (*Config, error) {
	v := viper.New()
	v.SetConfigFile(path)
	v.SetConfigType("yaml")

	if err := v.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("read config: %w", err)
	}

	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("unmarshal config: %w", err)
	}

	if err := cfg.validate(); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func (c *Config) validate() error {
	if c.Server.Port <= 0 {
		c.Server.Port = 8080
	}
	if c.Server.Timezone == "" {
		c.Server.Timezone = "UTC"
	}
	if c.Database.Path == "" {
		return fmt.Errorf("database.path is required")
	}
	if c.Reminder.DefaultLeadMinutes <= 0 {
		c.Reminder.DefaultLeadMinutes = 5
	}
	if c.Reminder.DispatchWorkers <= 0 {
		c.Reminder.DispatchWorkers = 3
	}
	if c.Reminder.MissedWindow <= 0 {
		c.Reminder.MissedWindow = 2 * time.Hour
	}
	if c.Analytics.AdherenceWindowDays <= 0 {
		c.Analytics.AdherenceWindowDays = 30
	}
	if c.Analytics.MissRiskThreshold <= 0 || c.Analytics.MissRiskThreshold > 1 {
		c.Analytics.MissRiskThreshold = 0.8
	}
	return nil
}
