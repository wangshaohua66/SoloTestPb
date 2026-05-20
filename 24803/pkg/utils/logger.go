package utils

import (
	"os"
	"path/filepath"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"gopkg.in/natefinch/lumberjack.v2"
)

var Logger *zap.Logger
var Sugar *zap.SugaredLogger

func InitLogger(level string, filename string) error {
	if err := os.MkdirAll(filepath.Dir(filename), 0755); err != nil {
		return err
	}

	logLevel := parseLogLevel(level)

	fileWriter := zapcore.AddSync(&lumberjack.Logger{
		Filename:   filename,
		MaxSize:    100,
		MaxBackups: 30,
		MaxAge:     7,
		Compress:   true,
	})

	consoleWriter := zapcore.AddSync(os.Stdout)

	encoderConfig := zapcore.EncoderConfig{
		TimeKey:        "time",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		FunctionKey:    zapcore.OmitKey,
		MessageKey:     "message",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.CapitalLevelEncoder,
		EncodeTime:     zapcore.ISO8601TimeEncoder,
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}

	core := zapcore.NewTee(
		zapcore.NewCore(zapcore.NewJSONEncoder(encoderConfig), fileWriter, logLevel),
		zapcore.NewCore(zapcore.NewConsoleEncoder(encoderConfig), consoleWriter, logLevel),
	)

	Logger = zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))
	Sugar = Logger.Sugar()

	return nil
}

func parseLogLevel(level string) zapcore.Level {
	switch level {
	case "debug":
		return zapcore.DebugLevel
	case "info":
		return zapcore.InfoLevel
	case "warn":
		return zapcore.WarnLevel
	case "error":
		return zapcore.ErrorLevel
	default:
		return zapcore.InfoLevel
	}
}

func SyncLogger() {
	if Logger != nil {
		_ = Logger.Sync()
	}
	if Sugar != nil {
		_ = Sugar.Sync()
	}
}
