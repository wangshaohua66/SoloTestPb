package com.taskmanager.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
@Schema(description = "分配任务请求")
public class AssignTaskRequest {
    
    @NotBlank(message = "受让人不能为空")
    @Schema(description = "受让人", example = "zhangsan", required = true)
    private String assignee;
}
