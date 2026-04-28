package com.taskmanager.dto;

import com.taskmanager.enums.TaskPriority;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.time.LocalDate;

@Data
@Schema(description = "创建任务请求")
public class CreateTaskRequest {
    
    @NotBlank(message = "任务标题不能为空")
    @Schema(description = "任务标题", example = "完成项目需求文档", required = true)
    private String title;

    @Schema(description = "任务描述", example = "编写项目详细需求文档，包括功能需求和非功能需求")
    private String description;

    @Schema(description = "任务优先级", example = "MEDIUM", defaultValue = "MEDIUM")
    private TaskPriority priority = TaskPriority.MEDIUM;

    @Schema(description = "截止日期", example = "2026-05-01")
    private LocalDate dueDate;

    @Schema(description = "受让人", example = "zhangsan")
    private String assignee;

    @NotBlank(message = "创建人不能为空")
    @Schema(description = "创建人", example = "admin", required = true)
    private String creator;
}
