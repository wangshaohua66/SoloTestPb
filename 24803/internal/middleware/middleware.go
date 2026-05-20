package middleware

import (
	"bytes"
	"io"
	"net/http"
	"strconv"
	"task-scheduler/pkg/errors"
	"task-scheduler/pkg/utils"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type responseBodyWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

func (r responseBodyWriter) Write(b []byte) (int, error) {
	r.body.Write(b)
	return r.ResponseWriter.Write(b)
}

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		var bodyBytes []byte
		if c.Request.Body != nil {
			bodyBytes, _ = io.ReadAll(c.Request.Body)
		}
		c.Request.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

		w := &responseBodyWriter{
			ResponseWriter: c.Writer,
			body:           bytes.NewBufferString(""),
		}
		c.Writer = w

		c.Next()

		cost := time.Since(start)
		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()
		method := c.Request.Method
		userAgent := c.Request.UserAgent()

		fields := []zap.Field{
			zap.Int("status", statusCode),
			zap.String("method", method),
			zap.String("path", path),
			zap.String("query", query),
			zap.String("ip", clientIP),
			zap.String("user_agent", userAgent),
			zap.Duration("cost", cost),
		}

		if len(bodyBytes) > 0 && len(bodyBytes) < 1024 {
			fields = append(fields, zap.String("request_body", string(bodyBytes)))
		}

		responseBody := w.body.String()
		if len(responseBody) > 0 && len(responseBody) < 1024 {
			fields = append(fields, zap.String("response_body", responseBody))
		}

		if statusCode >= 500 {
			utils.Logger.Error("Server error", fields...)
		} else if statusCode >= 400 {
			utils.Logger.Warn("Client error", fields...)
		} else {
			utils.Logger.Info("Request", fields...)
		}
	}
}

func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				utils.Logger.Error("Panic recovered",
					zap.Any("error", err),
					zap.String("path", c.Request.URL.Path),
					zap.Stack("stack"),
				)
				utils.Fail(c, errors.InternalServer("服务器内部错误"))
				c.Abort()
			}
		}()
		c.Next()
	}
}

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Max-Age", "86400")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

func Auth() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			utils.Fail(c, errors.Unauthorized("未提供认证令牌"))
			c.Abort()
			return
		}

		userID := "system"
		username := "admin"

		c.Set("user_id", userID)
		c.Set("username", username)

		c.Next()
	}
}

func Pagination() gin.HandlerFunc {
	return func(c *gin.Context) {
		page := 1
		pageSize := 10

		if p := c.Query("page"); p != "" {
			if val, err := strconv.Atoi(p); err == nil && val > 0 {
				page = val
			}
		}

		if ps := c.Query("page_size"); ps != "" {
			if val, err := strconv.Atoi(ps); err == nil && val > 0 {
				pageSize = val
				if pageSize > 100 {
					pageSize = 100
				}
			}
		}

		c.Set("page", page)
		c.Set("page_size", pageSize)

		c.Next()
	}
}

func GetUserInfo(c *gin.Context) (string, string) {
	userID, _ := c.Get("user_id")
	username, _ := c.Get("username")
	return userID.(string), username.(string)
}

func GetPagination(c *gin.Context) (int, int) {
	page, _ := c.Get("page")
	pageSize, _ := c.Get("page_size")
	return page.(int), pageSize.(int)
}
