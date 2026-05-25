package utils

import (
	"net/http"
	"task-scheduler/pkg/errors"

	"github.com/gin-gonic/gin"
)

type Response struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code:    0,
		Message: "success",
		Data:    data,
	})
}

func SuccessWithMessage(c *gin.Context, message string, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code:    0,
		Message: message,
		Data:    data,
	})
}

func Fail(c *gin.Context, err *errors.AppError) {
	c.JSON(err.Code, Response{
		Code:    err.Code,
		Message: err.Message,
	})
}

func FailWithCode(c *gin.Context, code int, message string) {
	c.JSON(code, Response{
		Code:    code,
		Message: message,
	})
}

type Pagination struct {
	Page     int   `json:"page"`
	PageSize int   `json:"page_size"`
	Total    int64 `json:"total"`
	Pages    int   `json:"pages"`
}

type PaginatedResponse struct {
	List       interface{} `json:"list"`
	Pagination Pagination  `json:"pagination"`
}

func Paginated(c *gin.Context, list interface{}, page, pageSize int, total int64) {
	pages := int(total) / pageSize
	if int(total)%pageSize > 0 {
		pages++
	}

	c.JSON(http.StatusOK, Response{
		Code:    0,
		Message: "success",
		Data: PaginatedResponse{
			List: list,
			Pagination: Pagination{
				Page:     page,
				PageSize: pageSize,
				Total:    total,
				Pages:    pages,
			},
		},
	})
}
