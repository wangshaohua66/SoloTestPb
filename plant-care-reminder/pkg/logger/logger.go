package logger

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sync"

	"github.com/rs/zerolog"
	"plant-care-reminder/config"
)

var (
	log  zerolog.Logger
	once sync.Once
	mu   sync.RWMutex
	file *os.File
)

func Init() error {
	var err error
	once.Do(func() {
		err = initLogger()
	})
	return err
}

func initLogger() error {
	cfg := config.Get()
	if cfg == nil {
		return fmt.Errorf("config not loaded")
	}

	logDir := filepath.Dir(cfg.Log.File)
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return fmt.Errorf("create log directory failed: %w", err)
	}

	var err error
	file, err = os.OpenFile(cfg.Log.File, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("open log file failed: %w", err)
	}

	level, err := zerolog.ParseLevel(cfg.Log.Level)
	if err != nil {
		level = zerolog.InfoLevel
	}

	consoleWriter := zerolog.ConsoleWriter{
		Out:        os.Stdout,
		TimeFormat: "2006-01-02 15:04:05",
	}

	multi := zerolog.MultiLevelWriter(consoleWriter, file)
	zerolog.SetGlobalLevel(level)

	log = zerolog.New(multi).With().
		Timestamp().
		Str("service", "plant-care-reminder").
		Logger()

	return nil
}

func Get() zerolog.Logger {
	mu.RLock()
	defer mu.RUnlock()
	return log
}

func Debug(msg string, fields ...map[string]interface{}) {
	mu.RLock()
	logEvent := log.Debug()
	mu.RUnlock()
	for _, f := range fields {
		for k, v := range f {
			logEvent = logEvent.Interface(k, v)
		}
	}
	logEvent.Msg(msg)
}

func Info(msg string, fields ...map[string]interface{}) {
	mu.RLock()
	logEvent := log.Info()
	mu.RUnlock()
	for _, f := range fields {
		for k, v := range f {
			logEvent = logEvent.Interface(k, v)
		}
	}
	logEvent.Msg(msg)
}

func Warn(msg string, fields ...map[string]interface{}) {
	mu.RLock()
	logEvent := log.Warn()
	mu.RUnlock()
	for _, f := range fields {
		for k, v := range f {
			logEvent = logEvent.Interface(k, v)
		}
	}
	logEvent.Msg(msg)
}

func Error(msg string, err error, fields ...map[string]interface{}) {
	mu.RLock()
	logEvent := log.Error().Err(err)
	mu.RUnlock()
	for _, f := range fields {
		for k, v := range f {
			logEvent = logEvent.Interface(k, v)
		}
	}
	logEvent.Msg(msg)
}

func Fatal(msg string, err error, fields ...map[string]interface{}) {
	mu.RLock()
	logEvent := log.Fatal().Err(err)
	mu.RUnlock()
	for _, f := range fields {
		for k, v := range f {
			logEvent = logEvent.Interface(k, v)
		}
	}
	logEvent.Msg(msg)
}

func WithFields(fields map[string]interface{}) zerolog.Logger {
	l := Get()
	ctx := l.With()
	for k, v := range fields {
		ctx = ctx.Interface(k, v)
	}
	return ctx.Logger()
}

func SetOutput(w io.Writer) {
	mu.Lock()
	defer mu.Unlock()
	log = log.Output(w)
}

func Close() error {
	mu.Lock()
	defer mu.Unlock()
	if file != nil {
		return file.Close()
	}
	return nil
}
