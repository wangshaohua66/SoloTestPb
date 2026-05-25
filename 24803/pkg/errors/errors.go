package errors

import (
	"fmt"
	"net/http"
)

type AppError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Err     error  `json:"-"`
}

func (e *AppError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

func New(code int, message string) *AppError {
	return &AppError{Code: code, Message: message}
}

func NewWithErr(code int, message string, err error) *AppError {
	return &AppError{Code: code, Message: message, Err: err}
}

func BadRequest(message string) *AppError {
	return New(http.StatusBadRequest, message)
}

func BadRequestWithErr(message string, err error) *AppError {
	return NewWithErr(http.StatusBadRequest, message, err)
}

func Unauthorized(message string) *AppError {
	return New(http.StatusUnauthorized, message)
}

func Forbidden(message string) *AppError {
	return New(http.StatusForbidden, message)
}

func NotFound(message string) *AppError {
	return New(http.StatusNotFound, message)
}

func InternalServer(message string) *AppError {
	return New(http.StatusInternalServerError, message)
}

func InternalServerWithErr(message string, err error) *AppError {
	return NewWithErr(http.StatusInternalServerError, message, err)
}

func Conflict(message string) *AppError {
	return New(http.StatusConflict, message)
}
