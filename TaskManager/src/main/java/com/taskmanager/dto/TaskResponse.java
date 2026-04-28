package com.taskmanager.dto;

import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@Schema(description = "任务响应对象")
public class TaskResponse {
    
    @Schema(description = "任务ID", example = "1")
    private Long id;
    
    @Schema(description = "任务标题", example = "完成项目需求文档")
    private String title;
    
    @Schema(description = "任务描述", example = "编写项目详细需求文档")
    private String description;
    
    @Schema(description = "任务状态", example = "TODO")
    private TaskStatus status;
    
    @Schema(description = "任务优先级", example = "HIGH")
    private TaskPriority priority;
    
    @Schema(description = "受让人", example = "zhangsan")
    private String assignee;
    
    @Schema(description = "创建人", example = "admin")
    private String creator;
    
    @Schema(description = "截止日期", example = "2026-05-01")
    private LocalDate dueDate;
    
    @Schema(description = "创建时间", example = "2026-04-26T10:00:00")
    private LocalDateTime createdAt;
    
    @Schema(description = "更新时间", example = "2026-04-26T10:30:00")
    private LocalDateTime updatedAt;
    
    @Schema(description = "是否逾期", example = "false")
    private boolean overdue;
}
