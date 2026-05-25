package config

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Server      ServerConfig      `yaml:"server"`
	Reminder    ReminderConfig    `yaml:"reminder"`
	Storage     StorageConfig     `yaml:"storage"`
	Log         LogConfig         `yaml:"log"`
	Concurrency ConcurrencyConfig `yaml:"concurrency"`
}

type ServerConfig struct {
	Port         int `yaml:"port"`
	ReadTimeout  int `yaml:"read_timeout"`
	WriteTimeout int `yaml:"write_timeout"`
	IdleTimeout  int `yaml:"idle_timeout"`
}

type ReminderConfig struct {
	CheckInterval       int    `yaml:"check_interval"`
	DefaultWaterDays    int    `yaml:"default_water_days"`
	DefaultFertilizeDays int   `yaml:"default_fertilize_days"`
	DefaultSunlight     string `yaml:"default_sunlight"`
	RemindBeforeHours   int    `yaml:"remind_before_hours"`
}

type StorageConfig struct {
	PlantsFile    string `yaml:"plants_file"`
	RemindersFile string `yaml:"reminders_file"`
	HistoryFile   string `yaml:"history_file"`
}

type LogConfig struct {
	Level      string `yaml:"level"`
	File       string `yaml:"file"`
	MaxSize    int    `yaml:"max_size"`
	MaxBackups int    `yaml:"max_backups"`
	MaxAge     int    `yaml:"max_age"`
	Compress   bool   `yaml:"compress"`
}

type ConcurrencyConfig struct {
	MaxRequests    int `yaml:"max_requests"`
	TimeoutSeconds int `yaml:"timeout_seconds"`
}

var (
	instance *Config
	once     sync.Once
	mu       sync.RWMutex
)

func Load() (*Config, error) {
	var err error
	once.Do(func() {
		instance, err = loadConfig()
	})
	if err != nil {
		return nil, fmt.Errorf("load config failed: %w", err)
	}
	return instance, nil
}

func loadConfig() (*Config, error) {
	configPath := getConfigPath()
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("read config file failed: %w", err)
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse config yaml failed: %w", err)
	}

	if err := validate(&cfg); err != nil {
		return nil, fmt.Errorf("validate config failed: %w", err)
	}

	return &cfg, nil
}

func getConfigPath() string {
	path := os.Getenv("PLANT_CARE_CONFIG")
	if path != "" {
		return path
	}
	return filepath.Join("config", "config.yaml")
}

func validate(cfg *Config) error {
	if cfg.Server.Port <= 0 || cfg.Server.Port > 65535 {
		return fmt.Errorf("invalid server port: %d", cfg.Server.Port)
	}
	if cfg.Reminder.CheckInterval <= 0 {
		return fmt.Errorf("reminder check interval must be positive: %d", cfg.Reminder.CheckInterval)
	}
	if cfg.Reminder.DefaultWaterDays <= 0 {
		return fmt.Errorf("default water days must be positive: %d", cfg.Reminder.DefaultWaterDays)
	}
	if cfg.Reminder.DefaultFertilizeDays <= 0 {
		return fmt.Errorf("default fertilize days must be positive: %d", cfg.Reminder.DefaultFertilizeDays)
	}
	if cfg.Concurrency.MaxRequests <= 0 {
		return fmt.Errorf("max requests must be positive: %d", cfg.Concurrency.MaxRequests)
	}
	return nil
}

func Get() *Config {
	mu.RLock()
	defer mu.RUnlock()
	return instance
}

func Reload() (*Config, error) {
	mu.Lock()
	defer mu.Unlock()

	newCfg, err := loadConfig()
	if err != nil {
		return nil, err
	}
	instance = newCfg
	return instance, nil
}
