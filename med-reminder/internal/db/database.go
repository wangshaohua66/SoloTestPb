package db

import (
	"context"
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"med-reminder/internal/config"
	"med-reminder/internal/logger"

	_ "modernc.org/sqlite"
)

type Database struct {
	mu     sync.RWMutex
	conn   *sql.DB
	path   string
	cfg    config.DatabaseConfig
	loc    *time.Location
}

func New(cfg config.DatabaseConfig, loc *time.Location) (*Database, error) {
	if err := os.MkdirAll(filepath.Dir(cfg.Path), 0o755); err != nil {
		return nil, fmt.Errorf("create db dir: %w", err)
	}

	dsn := fmt.Sprintf("file:%s?_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)&_pragma=foreign_keys(on)", cfg.Path)
	conn, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, fmt.Errorf("open db: %w", err)
	}
	conn.SetMaxOpenConns(1)
	conn.SetMaxIdleConns(1)

	if err := conn.Ping(); err != nil {
		return nil, fmt.Errorf("ping db: %w", err)
	}

	db := &Database{conn: conn, path: cfg.Path, cfg: cfg, loc: loc}
	if err := db.migrate(); err != nil {
		return nil, err
	}
	return db, nil
}

func (d *Database) Conn() *sql.DB { return d.conn }
func (d *Database) Location() *time.Location { return d.loc }

func (d *Database) migrate() error {
	stmts := []string{
		`CREATE TABLE IF NOT EXISTS medications (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			generic_name TEXT,
			dosage TEXT NOT NULL,
			instruction TEXT NOT NULL,
			unit TEXT,
			side_effects TEXT,
			notes TEXT,
			expiry_date DATETIME NOT NULL,
			expired INTEGER NOT NULL DEFAULT 0,
			manufacturer TEXT,
			stock_quantity INTEGER NOT NULL DEFAULT 0,
			low_stock_alert INTEGER NOT NULL DEFAULT 0,
			user_id TEXT NOT NULL,
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL
		)`,
		`CREATE INDEX IF NOT EXISTS idx_medications_user ON medications(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_medications_expiry ON medications(expiry_date)`,

		`CREATE TABLE IF NOT EXISTS reminder_schedules (
			id TEXT PRIMARY KEY,
			medication_id TEXT NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
			user_id TEXT NOT NULL,
			type TEXT NOT NULL,
			times TEXT NOT NULL,
			interval_days INTEGER NOT NULL DEFAULT 0,
			weekdays TEXT,
			start_date DATETIME NOT NULL,
			end_date DATETIME,
			lead_minutes INTEGER NOT NULL DEFAULT 5,
			enabled INTEGER NOT NULL DEFAULT 1,
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL
		)`,
		`CREATE INDEX IF NOT EXISTS idx_sched_user ON reminder_schedules(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_sched_med ON reminder_schedules(medication_id)`,

		`CREATE TABLE IF NOT EXISTS reminders (
			id TEXT PRIMARY KEY,
			medication_id TEXT NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
			schedule_id TEXT NOT NULL REFERENCES reminder_schedules(id) ON DELETE CASCADE,
			user_id TEXT NOT NULL,
			scheduled_at DATETIME NOT NULL,
			reminded_at DATETIME,
			acknowledged_at DATETIME,
			status TEXT NOT NULL,
			channel TEXT NOT NULL,
			message TEXT NOT NULL,
			retry_count INTEGER NOT NULL DEFAULT 0,
			last_error TEXT,
			conflicts_with TEXT,
			created_at DATETIME NOT NULL,
			updated_at DATETIME NOT NULL
		)`,
		`CREATE INDEX IF NOT EXISTS idx_rem_user ON reminders(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_rem_status ON reminders(status, scheduled_at)`,
		`CREATE INDEX IF NOT EXISTS idx_rem_med ON reminders(medication_id)`,

		`CREATE TABLE IF NOT EXISTS medication_logs (
			id TEXT PRIMARY KEY,
			medication_id TEXT NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
			reminder_id TEXT REFERENCES reminders(id) ON DELETE SET NULL,
			user_id TEXT NOT NULL,
			action TEXT NOT NULL,
			dosage_taken TEXT,
			occurred_at DATETIME NOT NULL,
			on_time INTEGER NOT NULL DEFAULT 0,
			notes TEXT,
			created_at DATETIME NOT NULL
		)`,
		`CREATE INDEX IF NOT EXISTS idx_logs_user ON medication_logs(user_id)`,
		`CREATE INDEX IF NOT EXISTS idx_logs_occurred ON medication_logs(occurred_at)`,
	}
	for _, s := range stmts {
		if _, err := d.conn.Exec(s); err != nil {
			return fmt.Errorf("migrate: %w (sql=%s)", err, s)
		}
	}
	return nil
}

func (d *Database) WithTx(ctx context.Context, fn func(tx *sql.Tx) error) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	tx, err := d.conn.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	if err := fn(tx); err != nil {
		if rb := tx.Rollback(); rb != nil {
			logger.S().Errorw("rollback failed", "error", rb)
		}
		return err
	}
	return tx.Commit()
}

func (d *Database) Close() error {
	return d.conn.Close()
}

func (d *Database) Backup() (string, error) {
	if err := os.MkdirAll(d.cfg.BackupPath, 0o755); err != nil {
		return "", err
	}
	name := fmt.Sprintf("med_reminder_%s.db", time.Now().UTC().Format("20060102T150405Z"))
	dst := filepath.Join(d.cfg.BackupPath, name)

	d.mu.Lock()
	defer d.mu.Unlock()

	if _, err := d.conn.Exec("SELECT 1 FROM pragma_wal_checkpoint('TRUNCATE')"); err != nil {
		_, _ = d.conn.Exec("PRAGMA wal_checkpoint(TRUNCATE)")
	}

	src, err := os.Open(d.path)
	if err != nil {
		return "", fmt.Errorf("open source db: %w", err)
	}
	defer src.Close()

	out, err := os.Create(dst)
	if err != nil {
		return "", fmt.Errorf("create backup: %w", err)
	}
	defer out.Close()

	if _, err := out.ReadFrom(src); err != nil {
		_ = os.Remove(dst)
		return "", fmt.Errorf("copy db: %w", err)
	}

	if err := out.Sync(); err != nil {
		_ = os.Remove(dst)
		return "", fmt.Errorf("sync backup: %w", err)
	}

	d.pruneBackups()
	return dst, nil
}

func (d *Database) pruneBackups() {
	entries, err := os.ReadDir(d.cfg.BackupPath)
	if err != nil {
		return
	}
	type f struct{ name string; mod time.Time }
	var files []f
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		info, err := e.Info()
		if err != nil {
			continue
		}
		files = append(files, f{name: filepath.Join(d.cfg.BackupPath, e.Name()), mod: info.ModTime()})
	}
	if d.cfg.MaxBackups <= 0 || len(files) <= d.cfg.MaxBackups {
		return
	}
	for i := 0; i < len(files); i++ {
		for j := i + 1; j < len(files); j++ {
			if files[i].mod.After(files[j].mod) {
				files[i], files[j] = files[j], files[i]
			}
		}
	}
	excess := len(files) - d.cfg.MaxBackups
	for i := 0; i < excess; i++ {
		_ = os.Remove(files[i].name)
	}
}
