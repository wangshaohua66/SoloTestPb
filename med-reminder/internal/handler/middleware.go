package handler

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"net/http"
	"time"

	"med-reminder/internal/logger"
	"med-reminder/internal/service"

	"github.com/gin-gonic/gin"
)

type APIError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Detail  string `json:"detail,omitempty"`
	TraceID string `json:"trace_id,omitempty"`
}

func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()
		if len(c.Errors) == 0 {
			return
		}
		last := c.Errors.Last()
		code := http.StatusInternalServerError
		if c.Writer.Status() != 200 && c.Writer.Status() != 0 {
			code = c.Writer.Status()
		}
		resp := APIError{Code: code, Message: http.StatusText(code), Detail: last.Error()}
		if v, ok := c.Get("trace_id"); ok {
			resp.TraceID = v.(string)
		}
		if !c.Writer.Written() {
			c.AbortWithStatusJSON(code, gin.H{"error": resp})
		}
	}
}

func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		traceID := c.GetHeader("X-Trace-ID")
		if traceID == "" {
			traceID = newID()
		}
		c.Set("trace_id", traceID)
		c.Writer.Header().Set("X-Trace-ID", traceID)
		c.Next()
	}
}

func AccessLog() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery
		c.Next()
		logger.S().Infow("request",
			"method", c.Request.Method,
			"path", path,
			"query", query,
			"status", c.Writer.Status(),
			"latency_ms", time.Since(start).Milliseconds(),
			"client_ip", c.ClientIP(),
			"user_agent", c.Request.UserAgent(),
		)
	}
}

func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if r := recover(); r != nil {
				logger.S().Errorw("panic recovered", "panic", r, "path", c.Request.URL.Path)
				c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": APIError{
					Code:    http.StatusInternalServerError,
					Message: "internal server error",
				}})
			}
		}()
		c.Next()
	}
}

func ResolveUser() gin.HandlerFunc {
	return func(c *gin.Context) {
		userID := c.GetHeader("X-User-ID")
		if userID == "" {
			userID = c.Query("user_id")
		}
		if userID == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing user id"})
			return
		}
		c.Set("user_id", userID)
		c.Next()
	}
}

func RespondError(c *gin.Context, err error) {
	var svcErr *service.ServiceError
	if errors.As(err, &svcErr) {
		status := http.StatusInternalServerError
		switch svcErr {
		case service.ErrNotFound:
			status = http.StatusNotFound
		case service.ErrValidation:
			status = http.StatusBadRequest
		case service.ErrForbidden:
			status = http.StatusForbidden
		case service.ErrConflict:
			status = http.StatusConflict
		}
		c.AbortWithStatusJSON(status, gin.H{"error": svcErr.Error(), "detail": err.Error()})
		return
	}
	logger.S().Errorw("unexpected error", "error", err, "path", c.Request.URL.Path)
	c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
}

func newID() string {
	b := make([]byte, 12)
	_, _ = rand.Read(b)
	return time.Now().UTC().Format("20060102150405.") + hex.EncodeToString(b)
}
