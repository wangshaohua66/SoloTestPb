package validator

import (
	"task-scheduler/pkg/errors"

	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/validator/v10"
	"github.com/robfig/cron/v3"
)

var Validate *validator.Validate

func Init() error {
	if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
		Validate = v
		if err := v.RegisterValidation("cron", validateCron); err != nil {
			return err
		}
	}
	return nil
}

func validateCron(fl validator.FieldLevel) bool {
	expression := fl.Field().String()
	if expression == "" {
		return false
	}
	parser := cron.NewParser(cron.Second | cron.Minute | cron.Hour | cron.Dom | cron.Month | cron.Dow | cron.Descriptor)
	_, err := parser.Parse(expression)
	return err == nil
}

func Struct(s interface{}) *errors.AppError {
	if err := Validate.Struct(s); err != nil {
		if errs, ok := err.(validator.ValidationErrors); ok {
			for _, e := range errs {
				return errors.BadRequest(getValidationMessage(e))
			}
		}
		return errors.BadRequest(err.Error())
	}
	return nil
}

func getValidationMessage(e validator.FieldError) string {
	switch e.Tag() {
	case "required":
		return e.Field() + " 是必填字段"
	case "max":
		return e.Field() + " 长度不能超过 " + e.Param() + " 个字符"
	case "min":
		return e.Field() + " 长度不能小于 " + e.Param()
	case "oneof":
		return e.Field() + " 必须是以下值之一: " + e.Param()
	case "url":
		return e.Field() + " 必须是有效的 URL"
	case "cron":
		return e.Field() + " 必须是有效的 Cron 表达式"
	case "email":
		return e.Field() + " 必须是有效的邮箱地址"
	default:
		return e.Field() + " 验证失败: " + e.Tag()
	}
}
