package services

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os/exec"
	"strings"
	"task-scheduler/internal/models"
	"task-scheduler/pkg/utils"
	"time"

	"go.uber.org/zap"
)

type TaskExecutor interface {
	Execute(ctx context.Context, task *models.Task) (string, error)
}

type HTTPExecutor struct{}

func NewHTTPExecutor() *HTTPExecutor {
	return &HTTPExecutor{}
}

func (e *HTTPExecutor) Execute(ctx context.Context, task *models.Task) (string, error) {
	var params struct {
		URL     string            `json:"url"`
		Method  string            `json:"method"`
		Headers map[string]string `json:"headers"`
		Body    interface{}       `json:"body"`
	}

	if err := json.Unmarshal([]byte(task.Params), &params); err != nil {
		return "", fmt.Errorf("invalid http params: %w", err)
	}

	if params.URL == "" {
		return "", fmt.Errorf("url is required")
	}

	if params.Method == "" {
		params.Method = http.MethodGet
	}

	var bodyReader io.Reader
	if params.Body != nil {
		bodyBytes, err := json.Marshal(params.Body)
		if err != nil {
			return "", fmt.Errorf("failed to marshal body: %w", err)
		}
		bodyReader = bytes.NewReader(bodyBytes)
	}

	req, err := http.NewRequestWithContext(ctx, params.Method, params.URL, bodyReader)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	for k, v := range params.Headers {
		req.Header.Set(k, v)
	}
	if bodyReader != nil && req.Header.Get("Content-Type") == "" {
		req.Header.Set("Content-Type", "application/json")
	}

	client := &http.Client{
		Timeout: time.Duration(task.Timeout) * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	result := map[string]interface{}{
		"status_code": resp.StatusCode,
		"headers":     resp.Header,
		"body":        string(respBody),
	}

	resultJSON, _ := json.Marshal(result)

	if resp.StatusCode >= 400 {
		return string(resultJSON), fmt.Errorf("request failed with status %d", resp.StatusCode)
	}

	return string(resultJSON), nil
}

type ShellExecutor struct{}

func NewShellExecutor() *ShellExecutor {
	return &ShellExecutor{}
}

func (e *ShellExecutor) Execute(ctx context.Context, task *models.Task) (string, error) {
	var params struct {
		Command string   `json:"command"`
		Args    []string `json:"args"`
		Shell   string   `json:"shell"`
	}

	if err := json.Unmarshal([]byte(task.Params), &params); err != nil {
		return "", fmt.Errorf("invalid shell params: %w", err)
	}

	if params.Command == "" {
		return "", fmt.Errorf("command is required")
	}

	if params.Shell == "" {
		params.Shell = "/bin/bash"
	}

	var cmd *exec.Cmd
	if len(params.Args) > 0 {
		cmd = exec.CommandContext(ctx, params.Command, params.Args...)
	} else {
		cmd = exec.CommandContext(ctx, params.Shell, "-c", params.Command)
	}

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()

	result := map[string]interface{}{
		"stdout": stdout.String(),
		"stderr": stderr.String(),
	}

	if err != nil {
		resultJSON, _ := json.Marshal(result)
		return string(resultJSON), fmt.Errorf("command execution failed: %w, stderr: %s", err, stderr.String())
	}

	resultJSON, _ := json.Marshal(result)
	return string(resultJSON), nil
}

type DatabaseExecutor struct{}

func NewDatabaseExecutor() *DatabaseExecutor {
	return &DatabaseExecutor{}
}

func (e *DatabaseExecutor) Execute(ctx context.Context, task *models.Task) (string, error) {
	var params struct {
		DSN        string   `json:"dsn"`
		Driver     string   `json:"driver"`
		SQL        string   `json:"sql"`
		Args       []interface{} `json:"args"`
		QueryType  string   `json:"query_type"`
	}

	if err := json.Unmarshal([]byte(task.Params), &params); err != nil {
		return "", fmt.Errorf("invalid database params: %w", err)
	}

	if params.DSN == "" || params.Driver == "" || params.SQL == "" {
		return "", fmt.Errorf("dsn, driver and sql are required")
	}

	db, err := sql.Open(params.Driver, params.DSN)
	if err != nil {
		return "", fmt.Errorf("failed to connect database: %w", err)
	}
	defer db.Close()

	if err := db.PingContext(ctx); err != nil {
		return "", fmt.Errorf("failed to ping database: %w", err)
	}

	if params.QueryType == "" {
		params.QueryType = "query"
	}

	switch strings.ToLower(params.QueryType) {
	case "exec":
		result, err := db.ExecContext(ctx, params.SQL, params.Args...)
		if err != nil {
			return "", fmt.Errorf("exec failed: %w", err)
		}
		rowsAffected, _ := result.RowsAffected()
		lastInsertID, _ := result.LastInsertId()
		return fmt.Sprintf(`{"rows_affected": %d, "last_insert_id": %d}`, rowsAffected, lastInsertID), nil

	case "query", "":
		rows, err := db.QueryContext(ctx, params.SQL, params.Args...)
		if err != nil {
			return "", fmt.Errorf("query failed: %w", err)
		}
		defer rows.Close()

		columns, _ := rows.Columns()
		var results []map[string]interface{}

		for rows.Next() {
			values := make([]interface{}, len(columns))
			valuePtrs := make([]interface{}, len(columns))
			for i := range values {
				valuePtrs[i] = &values[i]
			}

			if err := rows.Scan(valuePtrs...); err != nil {
				utils.Logger.Error("scan row failed", zap.Error(err))
				continue
			}

			row := make(map[string]interface{})
			for i, col := range columns {
				val := values[i]
				if b, ok := val.([]byte); ok {
					row[col] = string(b)
				} else {
					row[col] = val
				}
			}
			results = append(results, row)
		}

		resultJSON, _ := json.Marshal(results)
		return string(resultJSON), nil

	default:
		return "", fmt.Errorf("unsupported query type: %s", params.QueryType)
	}
}

func GetExecutor(taskType models.TaskType) TaskExecutor {
	switch taskType {
	case models.TaskTypeHTTP:
		return NewHTTPExecutor()
	case models.TaskTypeShell:
		return NewShellExecutor()
	case models.TaskTypeDatabase:
		return NewDatabaseExecutor()
	default:
		return nil
	}
}
