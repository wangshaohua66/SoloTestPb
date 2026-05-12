package com.taskmanager.dto;

import com.taskmanager.enums.TaskPriority;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.time.LocalDate;

@Data
@Schema(description = "更新任务请求")
public class UpdateTaskRequest {
    
    @Schema(description = "任务标题", example = "更新后的任务标题")
    private String title;

    @Schema(description = "任务描述", example = "更新后的任务描述")
    private String description;

    @Schema(description = "任务优先级", example = "HIGH")
    private TaskPriority priority;

    @Schema(description = "截止日期", example = "2026-05-10")
    private LocalDate dueDate;
}
