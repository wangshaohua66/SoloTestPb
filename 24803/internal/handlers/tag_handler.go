package handlers

import (
	"task-scheduler/internal/models"
	"task-scheduler/pkg/errors"
	"task-scheduler/pkg/utils"
	"task-scheduler/pkg/validator"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type TagHandler struct{}

func NewTagHandler() *TagHandler {
	return &TagHandler{}
}

func (h *TagHandler) Create(c *gin.Context) {
	var tag models.Tag
	if err := c.ShouldBindJSON(&tag); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	if err := validator.Struct(&tag); err != nil {
		utils.Fail(c, err)
		return
	}

	if tag.Color == "" {
		tag.Color = "#3b82f6"
	}

	var existing models.Tag
	if err := models.DB.Where("name = ?", tag.Name).First(&existing).Error; err == nil {
		utils.Fail(c, errors.Conflict("标签名称已存在"))
		return
	}

	if err := models.DB.Create(&tag).Error; err != nil {
		utils.Fail(c, errors.InternalServerWithErr("创建标签失败", err))
		return
	}

	utils.Success(c, tag)
}

func (h *TagHandler) Update(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("标签ID不能为空"))
		return
	}

	var tag models.Tag
	if err := models.DB.First(&tag, "id = ?", id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			utils.Fail(c, errors.NotFound("标签不存在"))
			return
		}
		utils.Fail(c, errors.InternalServerWithErr("查询标签失败", err))
		return
	}

	var req struct {
		Name  string `json:"name" binding:"max=100"`
		Color string `json:"color" binding:"max=50"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		utils.Fail(c, errors.BadRequestWithErr("请求参数错误", err))
		return
	}

	if req.Name != "" {
		var existing models.Tag
		if err := models.DB.Where("name = ? AND id != ?", req.Name, id).First(&existing).Error; err == nil {
			utils.Fail(c, errors.Conflict("标签名称已存在"))
			return
		}
		tag.Name = req.Name
	}

	if req.Color != "" {
		tag.Color = req.Color
	}

	if err := models.DB.Save(&tag).Error; err != nil {
		utils.Fail(c, errors.InternalServerWithErr("更新标签失败", err))
		return
	}

	utils.Success(c, tag)
}

func (h *TagHandler) Delete(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		utils.Fail(c, errors.BadRequest("标签ID不能为空"))
		return
	}

	var tag models.Tag
	if err := models.DB.First(&tag, "id = ?", id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			utils.Fail(c, errors.NotFound("标签不存在"))
			return
		}
		utils.Fail(c, errors.InternalServerWithErr("查询标签失败", err))
		return
	}

	tx := models.DB.Begin()
	if err := tx.Model(&tag).Association("Tasks").Clear(); err != nil {
		tx.Rollback()
		utils.Fail(c, errors.InternalServerWithErr("清除标签关联失败", err))
		return
	}

	if err := tx.Delete(&tag).Error; err != nil {
		tx.Rollback()
		utils.Fail(c, errors.InternalServerWithErr("删除标签失败", err))
		return
	}

	tx.Commit()

	utils.SuccessWithMessage(c, "删除成功", nil)
}

func (h *TagHandler) List(c *gin.Context) {
	var tags []models.Tag
	if err := models.DB.Order("created_at desc").Find(&tags).Error; err != nil {
		utils.Fail(c, errors.InternalServerWithErr("查询标签列表失败", err))
		return
	}

	utils.Success(c, tags)
}
