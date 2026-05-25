package middleware

import (
	"context"
	"fmt"
	"net/http"
	"runtime/debug"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"plant-care-reminder/pkg/concurrency"
	"plant-care-reminder/pkg/logger"
)

func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if r := recover(); r != nil {
				stack := debug.Stack()
				logger.Error("Panic recovered", fmt.Errorf("panic: %v", r), map[string]interface{}{
					"stack": string(stack),
					"path":  c.Request.URL.Path,
					"method": c.Request.Method,
				})

				c.JSON(http.StatusInternalServerError, gin.H{
					"error":   "internal server error",
					"message": "an unexpected error occurred",
				})
				c.Abort()
			}
		}()
		c.Next()
	}
}

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		latency := time.Since(start)
		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()

		logger.Info("HTTP Request", map[string]interface{}{
			"method":     method,
			"path":       path,
			"status":     statusCode,
			"latency":    latency,
			"client_ip":  clientIP,
			"user_agent": c.Request.UserAgent(),
		})
	}
}

func RateLimit() gin.HandlerFunc {
	return func(c *gin.Context) {
		limiter := concurrency.GetLimiter()
		ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
		defer cancel()

		if err := limiter.Acquire(ctx); err != nil {
			logger.Warn("Rate limit exceeded", map[string]interface{}{
				"path":   c.Request.URL.Path,
				"method": c.Request.Method,
				"error":  err.Error(),
			})
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error":   "too many requests",
				"message": "please try again later",
			})
			c.Abort()
			return
		}
		defer limiter.Release()

		c.Next()
	}
}

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

func Timeout(timeout time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
		defer cancel()

		c.Request = c.Request.WithContext(ctx)

		done := make(chan struct{})
		go func() {
			defer close(done)
			c.Next()
		}()

		select {
		case <-done:
		case <-ctx.Done():
			logger.Warn("Request timeout", map[string]interface{}{
				"path":    c.Request.URL.Path,
				"method":  c.Request.Method,
				"timeout": timeout,
			})
			c.JSON(http.StatusRequestTimeout, gin.H{
				"error":   "request timeout",
				"message": "the request took too long to process",
			})
			c.Abort()
		}
	}
}

func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := uuid.New().String()
		c.Set("request_id", requestID)
		c.Writer.Header().Set("X-Request-ID", requestID)
		c.Next()
	}
}

func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		if len(c.Errors) > 0 {
			err := c.Errors.Last()
			logger.Error("Request error", err.Err, map[string]interface{}{
				"path":   c.Request.URL.Path,
				"method": c.Request.Method,
			})

			if !c.Writer.Written() {
				c.JSON(http.StatusInternalServerError, gin.H{
					"error":   "internal server error",
					"message": err.Error(),
				})
			}
		}
	}
}
