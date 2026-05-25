package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"strings"
	"time"

	"med-reminder/internal/db"
	"med-reminder/internal/models"

	"github.com/google/uuid"
)

type MedicationRepo struct {
	db *db.Database
}

func NewMedicationRepo(d *db.Database) *MedicationRepo { return &MedicationRepo{db: d} }

func (r *MedicationRepo) Create(ctx context.Context, m *models.Medication) error {
	if m.ID == "" {
		m.ID = uuid.NewString()
	}
	now := time.Now().In(r.db.Location())
	m.CreatedAt = now
	m.UpdatedAt = now
	m.Expired = m.ExpiryDate.Before(now)
	const q = `INSERT INTO medications
		(id,name,generic_name,dosage,instruction,unit,side_effects,notes,expiry_date,expired,manufacturer,stock_quantity,low_stock_alert,user_id,created_at,updated_at)
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
	_, err := r.db.Conn().ExecContext(ctx, q,
		m.ID, m.Name, m.GenericName, m.Dosage, m.Instruction, m.Unit, m.SideEffects, m.Notes,
		m.ExpiryDate.UTC(), m.Expired, m.Manufacturer, m.StockQuantity, m.LowStockAlert, m.UserID,
		m.CreatedAt.UTC(), m.UpdatedAt.UTC(),
	)
	return err
}

func (r *MedicationRepo) GetByID(ctx context.Context, id string) (*models.Medication, error) {
	const q = `SELECT id,name,generic_name,dosage,instruction,unit,side_effects,notes,expiry_date,expired,manufacturer,stock_quantity,low_stock_alert,user_id,created_at,updated_at
		FROM medications WHERE id=?`
	row := r.db.Conn().QueryRowContext(ctx, q, id)
	return scanMedication(row, r.db.Location())
}

func (r *MedicationRepo) ListByUser(ctx context.Context, userID string, includeExpired bool) ([]models.Medication, error) {
	q := `SELECT id,name,generic_name,dosage,instruction,unit,side_effects,notes,expiry_date,expired,manufacturer,stock_quantity,low_stock_alert,user_id,created_at,updated_at
		FROM medications WHERE user_id=?`
	args := []any{userID}
	if !includeExpired {
		q += " AND expired=0"
	}
	q += " ORDER BY created_at DESC"
	rows, err := r.db.Conn().QueryContext(ctx, q, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []models.Medication
	for rows.Next() {
		m, err := scanMedicationRows(rows, r.db.Location())
		if err != nil {
			return nil, err
		}
		out = append(out, *m)
	}
	return out, rows.Err()
}

func (r *MedicationRepo) Update(ctx context.Context, m *models.Medication) error {
	m.UpdatedAt = time.Now().In(r.db.Location())
	m.Expired = m.ExpiryDate.Before(m.UpdatedAt)
	const q = `UPDATE medications SET
		name=?,generic_name=?,dosage=?,instruction=?,unit=?,side_effects=?,notes=?,expiry_date=?,expired=?,manufacturer=?,stock_quantity=?,low_stock_alert=?,updated_at=?
		WHERE id=?`
	res, err := r.db.Conn().ExecContext(ctx, q,
		m.Name, m.GenericName, m.Dosage, m.Instruction, m.Unit, m.SideEffects, m.Notes,
		m.ExpiryDate.UTC(), m.Expired, m.Manufacturer, m.StockQuantity, m.LowStockAlert, m.UpdatedAt.UTC(), m.ID,
	)
	if err != nil {
		return err
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return ErrNotFound
	}
	return nil
}

func (r *MedicationRepo) Delete(ctx context.Context, id string) error {
	res, err := r.db.Conn().ExecContext(ctx, `DELETE FROM medications WHERE id=?`, id)
	if err != nil {
		return err
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return ErrNotFound
	}
	return nil
}

func (r *MedicationRepo) MarkExpired(ctx context.Context, loc *time.Location) (int, error) {
	now := time.Now().In(loc)
	today := time.Date(now.Year(), now.Month(), now.Day(), 23, 59, 59, 0, loc)
	res, err := r.db.Conn().ExecContext(ctx,
		`UPDATE medications SET expired=1,updated_at=? WHERE expiry_date <= ? AND expired=0`,
		now.UTC(), today.UTC(),
	)
	if err != nil {
		return 0, err
	}
	n, _ := res.RowsAffected()
	return int(n), nil
}

func (r *MedicationRepo) LowStock(ctx context.Context, userID string) ([]models.Medication, error) {
	q := `SELECT id,name,generic_name,dosage,instruction,unit,side_effects,notes,expiry_date,expired,manufacturer,stock_quantity,low_stock_alert,user_id,created_at,updated_at
		FROM medications WHERE user_id=? AND low_stock_alert>0 AND stock_quantity<=low_stock_alert AND expired=0`
	rows, err := r.db.Conn().QueryContext(ctx, q, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []models.Medication
	for rows.Next() {
		m, err := scanMedicationRows(rows, r.db.Location())
		if err != nil {
			return nil, err
		}
		out = append(out, *m)
	}
	return out, rows.Err()
}

type rowScanner interface {
	Scan(dest ...any) error
}

func scanMedication(s rowScanner, loc *time.Location) (*models.Medication, error) {
	var m models.Medication
	var exp, cr, up time.Time
	var expired int
	err := s.Scan(&m.ID, &m.Name, &m.GenericName, &m.Dosage, &m.Instruction, &m.Unit, &m.SideEffects, &m.Notes,
		&exp, &expired, &m.Manufacturer, &m.StockQuantity, &m.LowStockAlert, &m.UserID, &cr, &up)
	if err != nil {
		return nil, err
	}
	m.ExpiryDate = exp.In(loc)
	m.Expired = expired == 1
	m.CreatedAt = cr.In(loc)
	m.UpdatedAt = up.In(loc)
	return &m, nil
}

func scanMedicationRows(rows *sql.Rows, loc *time.Location) (*models.Medication, error) { return scanMedication(rows, loc) }

type ScheduleRepo struct {
	db *db.Database
}

func NewScheduleRepo(d *db.Database) *ScheduleRepo { return &ScheduleRepo{db: d} }

func (r *ScheduleRepo) Create(ctx context.Context, s *models.ReminderSchedule) error {
	if s.ID == "" {
		s.ID = uuid.NewString()
	}
	now := time.Now().In(r.db.Location())
	s.CreatedAt = now
	s.UpdatedAt = now
	times, _ := json.Marshal(s.Times)
	wds, _ := json.Marshal(s.Weekdays)
	var end sql.NullTime
	if s.EndDate != nil {
		end = sql.NullTime{Time: s.EndDate.UTC(), Valid: true}
	}
	const q = `INSERT INTO reminder_schedules
		(id,medication_id,user_id,type,times,interval_days,weekdays,start_date,end_date,lead_minutes,enabled,created_at,updated_at)
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`
	_, err := r.db.Conn().ExecContext(ctx, q, s.ID, s.MedicationID, s.UserID, s.Type, string(times),
		s.IntervalDays, string(wds), s.StartDate.UTC(), end, s.LeadMinutes, s.Enabled, s.CreatedAt.UTC(), s.UpdatedAt.UTC())
	return err
}

func (r *ScheduleRepo) GetByID(ctx context.Context, id string) (*models.ReminderSchedule, error) {
	const q = `SELECT id,medication_id,user_id,type,times,interval_days,weekdays,start_date,end_date,lead_minutes,enabled,created_at,updated_at
		FROM reminder_schedules WHERE id=?`
	return r.scanOne(r.db.Conn().QueryRowContext(ctx, q, id))
}

func (r *ScheduleRepo) ListByMedication(ctx context.Context, medID string) ([]models.ReminderSchedule, error) {
	return r.list(ctx, `medication_id=? ORDER BY created_at`, medID)
}

func (r *ScheduleRepo) ListByUser(ctx context.Context, userID string) ([]models.ReminderSchedule, error) {
	return r.list(ctx, `user_id=? ORDER BY created_at`, userID)
}

func (r *ScheduleRepo) ListAllActive(ctx context.Context) ([]models.ReminderSchedule, error) {
	return r.list(ctx, `enabled=1`, nil)
}

func (r *ScheduleRepo) list(ctx context.Context, where string, arg any) ([]models.ReminderSchedule, error) {
	q := `SELECT id,medication_id,user_id,type,times,interval_days,weekdays,start_date,end_date,lead_minutes,enabled,created_at,updated_at
		FROM reminder_schedules WHERE ` + where
	var rows *sql.Rows
	var err error
	if arg != nil {
		rows, err = r.db.Conn().QueryContext(ctx, q, arg)
	} else {
		rows, err = r.db.Conn().QueryContext(ctx, q)
	}
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []models.ReminderSchedule
	for rows.Next() {
		s, err := r.scanRows(rows)
		if err != nil {
			return nil, err
		}
		out = append(out, *s)
	}
	return out, rows.Err()
}

func (r *ScheduleRepo) Update(ctx context.Context, s *models.ReminderSchedule) error {
	s.UpdatedAt = time.Now().In(r.db.Location())
	times, _ := json.Marshal(s.Times)
	wds, _ := json.Marshal(s.Weekdays)
	var end sql.NullTime
	if s.EndDate != nil {
		end = sql.NullTime{Time: s.EndDate.UTC(), Valid: true}
	}
	const q = `UPDATE reminder_schedules SET
		type=?,times=?,interval_days=?,weekdays=?,start_date=?,end_date=?,lead_minutes=?,enabled=?,updated_at=?
		WHERE id=?`
	res, err := r.db.Conn().ExecContext(ctx, q, s.Type, string(times), s.IntervalDays, string(wds),
		s.StartDate.UTC(), end, s.LeadMinutes, s.Enabled, s.UpdatedAt.UTC(), s.ID)
	if err != nil {
		return err
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return ErrNotFound
	}
	return nil
}

func (r *ScheduleRepo) Delete(ctx context.Context, id string) error {
	res, err := r.db.Conn().ExecContext(ctx, `DELETE FROM reminder_schedules WHERE id=?`, id)
	if err != nil {
		return err
	}
	n, _ := res.RowsAffected()
	if n == 0 {
		return ErrNotFound
	}
	return nil
}

func (r *ScheduleRepo) scanOne(row *sql.Row) (*models.ReminderSchedule, error) {
	var s models.ReminderSchedule
	var times, wds string
	var start time.Time
	var end sql.NullTime
	var cr, up time.Time
	err := row.Scan(&s.ID, &s.MedicationID, &s.UserID, &s.Type, &times, &s.IntervalDays, &wds, &start, &end,
		&s.LeadMinutes, &s.Enabled, &cr, &up)
	if err != nil {
		return nil, err
	}
	_ = json.Unmarshal([]byte(times), &s.Times)
	if strings.TrimSpace(wds) != "" {
		_ = json.Unmarshal([]byte(wds), &s.Weekdays)
	}
	loc := r.db.Location()
	s.StartDate = start.In(loc)
	if end.Valid {
		t := end.Time.In(loc)
		s.EndDate = &t
	}
	s.CreatedAt = cr.In(loc)
	s.UpdatedAt = up.In(loc)
	return &s, nil
}

func (r *ScheduleRepo) scanRows(rows *sql.Rows) (*models.ReminderSchedule, error) {
	var s models.ReminderSchedule
	var times, wds string
	var start time.Time
	var end sql.NullTime
	var cr, up time.Time
	err := rows.Scan(&s.ID, &s.MedicationID, &s.UserID, &s.Type, &times, &s.IntervalDays, &wds, &start, &end,
		&s.LeadMinutes, &s.Enabled, &cr, &up)
	if err != nil {
		return nil, err
	}
	_ = json.Unmarshal([]byte(times), &s.Times)
	if strings.TrimSpace(wds) != "" {
		_ = json.Unmarshal([]byte(wds), &s.Weekdays)
	}
	loc := r.db.Location()
	s.StartDate = start.In(loc)
	if end.Valid {
		t := end.Time.In(loc)
		s.EndDate = &t
	}
	s.CreatedAt = cr.In(loc)
	s.UpdatedAt = up.In(loc)
	return &s, nil
}

type ReminderRepo struct {
	db *db.Database
}

func NewReminderRepo(d *db.Database) *ReminderRepo { return &ReminderRepo{db: d} }

func (r *ReminderRepo) Create(ctx context.Context, rm *models.Reminder) error {
	if rm.ID == "" {
		rm.ID = uuid.NewString()
	}
	now := time.Now().In(r.db.Location())
	rm.CreatedAt = now
	rm.UpdatedAt = now
	conflicts, _ := json.Marshal(rm.ConflictsWith)
	var reminded, ack sql.NullTime
	if rm.RemindedAt != nil {
		reminded = sql.NullTime{Time: rm.RemindedAt.UTC(), Valid: true}
	}
	if rm.AcknowledgedAt != nil {
		ack = sql.NullTime{Time: rm.AcknowledgedAt.UTC(), Valid: true}
	}
	const q = `INSERT INTO reminders
		(id,medication_id,schedule_id,user_id,scheduled_at,reminded_at,acknowledged_at,status,channel,message,retry_count,last_error,conflicts_with,created_at,updated_at)
		VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
	_, err := r.db.Conn().ExecContext(ctx, q,
		rm.ID, rm.MedicationID, rm.ScheduleID, rm.UserID, rm.ScheduledAt.UTC(), reminded, ack,
		rm.Status, rm.Channel, rm.Message, rm.RetryCount, rm.LastError, string(conflicts),
		rm.CreatedAt.UTC(), rm.UpdatedAt.UTC(),
	)
	return err
}

func (r *ReminderRepo) UpdateStatus(ctx context.Context, id string, status models.ReminderStatus, errMsg string) error {
	now := time.Now().In(r.db.Location()).UTC()
	q := `UPDATE reminders SET status=?, updated_at=?`
	args := []any{status, now}
	if status == models.ReminderSent {
		q += `, reminded_at=?`
		args = append(args, now)
	}
	if status == models.ReminderAcknowledged {
		q += `, acknowledged_at=?`
		args = append(args, now)
	}
	if errMsg != "" {
		q += `, last_error=?`
		args = append(args, errMsg)
	}
	q += ` WHERE id=?`
	args = append(args, id)
	_, err := r.db.Conn().ExecContext(ctx, q, args...)
	return err
}

func (r *ReminderRepo) IncrementRetry(ctx context.Context, id string, errMsg string) error {
	now := time.Now().In(r.db.Location()).UTC()
	_, err := r.db.Conn().ExecContext(ctx,
		`UPDATE reminders SET retry_count=retry_count+1, last_error=?, updated_at=? WHERE id=?`,
		errMsg, now, id,
	)
	return err
}

func (r *ReminderRepo) ListPendingByWindow(ctx context.Context, from, to time.Time) ([]models.Reminder, error) {
	const q = `SELECT id,medication_id,schedule_id,user_id,scheduled_at,reminded_at,acknowledged_at,status,channel,message,retry_count,last_error,conflicts_with,created_at,updated_at
		FROM reminders WHERE status IN ('pending','failed') AND scheduled_at BETWEEN ? AND ? ORDER BY scheduled_at ASC`
	rows, err := r.db.Conn().QueryContext(ctx, q, from.UTC(), to.UTC())
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return r.scanAll(rows)
}

func (r *ReminderRepo) ListByUser(ctx context.Context, userID string, limit, offset int) ([]models.Reminder, error) {
	q := `SELECT id,medication_id,schedule_id,user_id,scheduled_at,reminded_at,acknowledged_at,status,channel,message,retry_count,last_error,conflicts_with,created_at,updated_at
		FROM reminders WHERE user_id=? ORDER BY scheduled_at DESC LIMIT ? OFFSET ?`
	rows, err := r.db.Conn().QueryContext(ctx, q, userID, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return r.scanAll(rows)
}

func (r *ReminderRepo) ListByMedication(ctx context.Context, medID string, from, to time.Time) ([]models.Reminder, error) {
	q := `SELECT id,medication_id,schedule_id,user_id,scheduled_at,reminded_at,acknowledged_at,status,channel,message,retry_count,last_error,conflicts_with,created_at,updated_at
		FROM reminders WHERE medication_id=? AND scheduled_at BETWEEN ? AND ? ORDER BY scheduled_at`
	rows, err := r.db.Conn().QueryContext(ctx, q, medID, from.UTC(), to.UTC())
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return r.scanAll(rows)
}

func (r *ReminderRepo) ExistsScheduled(ctx context.Context, scheduleID string, scheduledAt time.Time) (bool, error) {
	var cnt int
	err := r.db.Conn().QueryRowContext(ctx,
		`SELECT COUNT(*) FROM reminders WHERE schedule_id=? AND scheduled_at=?`,
		scheduleID, scheduledAt.UTC(),
	).Scan(&cnt)
	return cnt > 0, err
}

func (r *ReminderRepo) MarkMissed(ctx context.Context, before time.Time) (int, error) {
	now := time.Now().In(r.db.Location()).UTC()
	res, err := r.db.Conn().ExecContext(ctx,
		`UPDATE reminders SET status='missed', updated_at=? WHERE status='pending' AND scheduled_at<?`,
		now, before.UTC(),
	)
	if err != nil {
		return 0, err
	}
	n, _ := res.RowsAffected()
	return int(n), nil
}

func (r *ReminderRepo) GetByID(ctx context.Context, id string) (*models.Reminder, error) {
	const q = `SELECT id,medication_id,schedule_id,user_id,scheduled_at,reminded_at,acknowledged_at,status,channel,message,retry_count,last_error,conflicts_with,created_at,updated_at
		FROM reminders WHERE id=?`
	row := r.db.Conn().QueryRowContext(ctx, q, id)
	return r.scanRow(row)
}

func (r *ReminderRepo) scanAll(rows *sql.Rows) ([]models.Reminder, error) {
	var out []models.Reminder
	for rows.Next() {
		rm, err := r.scanRow(rows)
		if err != nil {
			return nil, err
		}
		out = append(out, *rm)
	}
	return out, rows.Err()
}

type reminderScanner interface {
	Scan(dest ...any) error
}

func (r *ReminderRepo) scanRow(s reminderScanner) (*models.Reminder, error) {
	var rm models.Reminder
	var sched, cr, up time.Time
	var remindedN, ackN sql.NullTime
	var conflicts string
	err := s.Scan(&rm.ID, &rm.MedicationID, &rm.ScheduleID, &rm.UserID, &sched, &remindedN, &ackN,
		&rm.Status, &rm.Channel, &rm.Message, &rm.RetryCount, &rm.LastError, &conflicts, &cr, &up)
	if err != nil {
		return nil, err
	}
	loc := r.db.Location()
	rm.ScheduledAt = sched.In(loc)
	if remindedN.Valid {
		t := remindedN.Time.In(loc)
		rm.RemindedAt = &t
	}
	if ackN.Valid {
		t := ackN.Time.In(loc)
		rm.AcknowledgedAt = &t
	}
	_ = json.Unmarshal([]byte(conflicts), &rm.ConflictsWith)
	rm.CreatedAt = cr.In(loc)
	rm.UpdatedAt = up.In(loc)
	return &rm, nil
}

type LogRepo struct {
	db *db.Database
}

func NewLogRepo(d *db.Database) *LogRepo { return &LogRepo{db: d} }

func (r *LogRepo) Create(ctx context.Context, l *models.MedicationLog) error {
	if l.ID == "" {
		l.ID = uuid.NewString()
	}
	l.CreatedAt = time.Now().In(r.db.Location())
	const q = `INSERT INTO medication_logs
		(id,medication_id,reminder_id,user_id,action,dosage_taken,occurred_at,on_time,notes,created_at)
		VALUES (?,?,?,?,?,?,?,?,?,?)`
	var rid sql.NullString
	if l.ReminderID != "" {
		rid = sql.NullString{String: l.ReminderID, Valid: true}
	}
	_, err := r.db.Conn().ExecContext(ctx, q, l.ID, l.MedicationID, rid, l.UserID, l.Action,
		l.DosageTaken, l.OccurredAt.UTC(), l.OnTime, l.Notes, l.CreatedAt.UTC())
	return err
}

func (r *LogRepo) ListByUser(ctx context.Context, userID string, from, to time.Time) ([]models.MedicationLog, error) {
	q := `SELECT id,medication_id,reminder_id,user_id,action,dosage_taken,occurred_at,on_time,notes,created_at
		FROM medication_logs WHERE user_id=? AND occurred_at BETWEEN ? AND ? ORDER BY occurred_at DESC`
	rows, err := r.db.Conn().QueryContext(ctx, q, userID, from.UTC(), to.UTC())
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []models.MedicationLog
	for rows.Next() {
		var l models.MedicationLog
		var occ, cr time.Time
		var rid sql.NullString
		if err := rows.Scan(&l.ID, &l.MedicationID, &rid, &l.UserID, &l.Action, &l.DosageTaken, &occ, &l.OnTime, &l.Notes, &cr); err != nil {
			return nil, err
		}
		if rid.Valid {
			l.ReminderID = rid.String
		}
		loc := r.db.Location()
		l.OccurredAt = occ.In(loc)
		l.CreatedAt = cr.In(loc)
		out = append(out, l)
	}
	return out, rows.Err()
}

func (r *LogRepo) CountByStatus(ctx context.Context, userID string, from, to time.Time) (onTime, late, missed, total int, err error) {
	q := `SELECT 
		SUM(CASE WHEN action='taken' AND on_time=1 THEN 1 ELSE 0 END),
		SUM(CASE WHEN action='taken' AND on_time=0 THEN 1 ELSE 0 END),
		SUM(CASE WHEN action='missed' THEN 1 ELSE 0 END),
		COUNT(*)
		FROM medication_logs WHERE user_id=? AND occurred_at BETWEEN ? AND ?`
	err = r.db.Conn().QueryRowContext(ctx, q, userID, from.UTC(), to.UTC()).Scan(&onTime, &late, &missed, &total)
	return
}

var ErrNotFound = errors.New("not found")
