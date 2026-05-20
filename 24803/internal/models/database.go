package models

import (
	"fmt"
	"task-scheduler/internal/config"

	"gorm.io/driver/mysql"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() error {
	var dialector gorm.Dialector

	switch config.AppConfig.Database.Driver {
	case "mysql":
		dialector = mysql.Open(config.AppConfig.Database.DSN)
	case "sqlite":
		dialector = sqlite.Open(config.AppConfig.Database.DSN)
	default:
		return fmt.Errorf("unsupported database driver: %s", config.AppConfig.Database.Driver)
	}

	db, err := gorm.Open(dialector, &gorm.Config{})
	if err != nil {
		return fmt.Errorf("failed to connect database: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("failed to get database instance: %w", err)
	}

	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)

	DB = db

	if err := autoMigrate(); err != nil {
		return fmt.Errorf("failed to migrate database: %w", err)
	}

	return nil
}

func autoMigrate() error {
	return DB.AutoMigrate(
		&Task{},
		&TaskLog{},
		&AuditLog{},
		&Tag{},
	)
}
