package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

type Config struct {
	Server   ServerConfig   `mapstructure:"server"`
	Database DatabaseConfig `mapstructure:"database"`
	Log      LogConfig      `mapstructure:"log"`
	Scheduler SchedulerConfig `mapstructure:"scheduler"`
}

type ServerConfig struct {
	Port int    `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

type DatabaseConfig struct {
	Driver string `mapstructure:"driver"`
	DSN    string `mapstructure:"dsn"`
}

type LogConfig struct {
	Level    string `mapstructure:"level"`
	Filename string `mapstructure:"filename"`
}

type SchedulerConfig struct {
	MaxConcurrentTasks int `mapstructure:"max_concurrent_tasks"`
	DefaultTimeout   int `mapstructure:"default_timeout"`
	MaxRetryCount    int `mapstructure:"max_retry_count"`
}

var AppConfig *Config

func Load(configPath string) error {
	viper.SetConfigFile(configPath)
	viper.SetConfigType("yaml")
	viper.AutomaticEnv()
	viper.SetEnvPrefix("TASK_SCHEDULER")
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	setDefaults()

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			return fmt.Errorf("config file not found: %w", err)
		}
		return fmt.Errorf("failed to read config: %w", err)
	}

	AppConfig = &Config{}
	if err := viper.Unmarshal(AppConfig); err != nil {
		return fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return nil
}

func setDefaults() {
	viper.SetDefault("server.port", 8080)
	viper.SetDefault("server.mode", "debug")
	viper.SetDefault("database.driver", "sqlite")
	viper.SetDefault("database.dsn", "task_scheduler.db")
	viper.SetDefault("log.level", "info")
	viper.SetDefault("log.filename", "logs/task-scheduler.log")
	viper.SetDefault("scheduler.max_concurrent_tasks", 10)
	viper.SetDefault("scheduler.default_timeout", 300)
	viper.SetDefault("scheduler.max_retry_count", 3)
}
