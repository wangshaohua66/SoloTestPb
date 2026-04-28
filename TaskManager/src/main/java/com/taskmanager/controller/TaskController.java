package com.taskmanager.controller;

import com.taskmanager.dto.AssignTaskRequest;
import com.taskmanager.dto.CreateTaskRequest;
import com.taskmanager.dto.TaskResponse;
import com.taskmanager.dto.UpdateTaskRequest;
import com.taskmanager.entity.TaskStatusHistory;
import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import com.taskmanager.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/tasks")
@Tag(name = "任务管理", description = "任务管理相关的REST API")
public class TaskController {

    @Autowired
    private TaskService taskService;

    @PostMapping
    @Operation(summary = "创建任务", description = "创建一个新的任务")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "任务创建成功",
                    content = {@Content(mediaType = "application/json",
                            schema = @Schema(implementation = TaskResponse.class))}),
            @ApiResponse(responseCode = "400", description = "输入参数验证失败")
    })
    public ResponseEntity<TaskResponse> createTask(
            @Parameter(description = "创建任务的请求体") 
            @Valid @RequestBody CreateTaskRequest request) {
        TaskResponse task = taskService.createTask(request);
        return new ResponseEntity<>(task, HttpStatus.CREATED);
    }

    @GetMapping
    @Operation(summary = "获取所有任务", description = "获取所有任务列表，按优先级和截止日期排序")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getAllTasks() {
        List<TaskResponse> tasks = taskService.getAllTasks();
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取任务详情", description = "根据任务ID获取任务详情")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "成功获取任务详情"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> getTaskById(
            @Parameter(description = "任务ID") @PathVariable Long id) {
        TaskResponse task = taskService.getTaskById(id);
        return ResponseEntity.ok(task);
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新任务", description = "更新任务信息")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务更新成功"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> updateTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "更新任务的请求体") @RequestBody UpdateTaskRequest request) {
        TaskResponse task = taskService.updateTask(id, request);
        return ResponseEntity.ok(task);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除任务", description = "删除指定的任务")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "204", description = "任务删除成功"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<Void> deleteTask(
            @Parameter(description = "任务ID") @PathVariable Long id) {
        taskService.deleteTask(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/assignee/{assignee}")
    @Operation(summary = "获取用户任务", description = "获取分配给指定用户的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getTasksByAssignee(
            @Parameter(description = "受让人") @PathVariable String assignee) {
        List<TaskResponse> tasks = taskService.getTasksByAssignee(assignee);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/creator/{creator}")
    @Operation(summary = "获取创建者任务", description = "获取指定创建者创建的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getTasksByCreator(
            @Parameter(description = "创建者") @PathVariable String creator) {
        List<TaskResponse> tasks = taskService.getTasksByCreator(creator);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "按状态获取任务", description = "获取指定状态的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getTasksByStatus(
            @Parameter(description = "任务状态") @PathVariable TaskStatus status) {
        List<TaskResponse> tasks = taskService.getTasksByStatus(status);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/priority/{priority}")
    @Operation(summary = "按优先级获取任务", description = "获取指定优先级的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getTasksByPriority(
            @Parameter(description = "任务优先级") @PathVariable TaskPriority priority) {
        List<TaskResponse> tasks = taskService.getTasksByPriority(priority);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/date-range")
    @Operation(summary = "按日期范围获取任务", description = "获取截止日期在指定范围内的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取任务列表")
    public ResponseEntity<List<TaskResponse>> getTasksByDateRange(
            @Parameter(description = "开始日期") 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @Parameter(description = "结束日期") 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        List<TaskResponse> tasks = taskService.getTasksByDateRange(startDate, endDate);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/overdue")
    @Operation(summary = "获取逾期任务", description = "获取所有已逾期的任务列表")
    @ApiResponse(responseCode = "200", description = "成功获取逾期任务列表")
    public ResponseEntity<List<TaskResponse>> getOverdueTasks() {
        List<TaskResponse> tasks = taskService.getOverdueTasks();
        return ResponseEntity.ok(tasks);
    }

    @PostMapping("/{id}/assign")
    @Operation(summary = "分配任务", description = "将任务分配给指定用户")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务分配成功"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> assignTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "分配请求体") @Valid @RequestBody AssignTaskRequest request,
            @Parameter(description = "操作人") @RequestParam(required = false) String changedBy) {
        TaskResponse task = taskService.assignTask(id, request.getAssignee(), changedBy);
        return ResponseEntity.ok(task);
    }

    @PostMapping("/{id}/claim")
    @Operation(summary = "认领任务", description = "认领待办状态且未被认领的任务")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务认领成功"),
            @ApiResponse(responseCode = "400", description = "任务状态无效或已被认领"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> claimTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "认领人") @RequestParam String assignee) {
        TaskResponse task = taskService.claimTask(id, assignee);
        return ResponseEntity.ok(task);
    }

    @PostMapping("/{id}/start")
    @Operation(summary = "开始任务", description = "将任务状态从待办改为进行中")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务状态更新成功"),
            @ApiResponse(responseCode = "400", description = "无效的状态转换"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> startTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "操作人") @RequestParam(required = false) String changedBy) {
        TaskResponse task = taskService.startTask(id, changedBy);
        return ResponseEntity.ok(task);
    }

    @PostMapping("/{id}/complete")
    @Operation(summary = "完成任务", description = "将任务状态从进行中改为已完成")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务状态更新成功"),
            @ApiResponse(responseCode = "400", description = "无效的状态转换"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> completeTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "操作人") @RequestParam(required = false) String changedBy) {
        TaskResponse task = taskService.completeTask(id, changedBy);
        return ResponseEntity.ok(task);
    }

    @PostMapping("/{id}/cancel")
    @Operation(summary = "取消任务", description = "取消待办或进行中的任务")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务取消成功"),
            @ApiResponse(responseCode = "400", description = "无效的状态转换"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> cancelTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "操作人") @RequestParam(required = false) String changedBy) {
        TaskResponse task = taskService.cancelTask(id, changedBy);
        return ResponseEntity.ok(task);
    }

    @PostMapping("/{id}/reopen")
    @Operation(summary = "重新打开任务", description = "重新打开已完成或已取消的任务")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "任务重新打开成功"),
            @ApiResponse(responseCode = "400", description = "无效的状态转换"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<TaskResponse> reopenTask(
            @Parameter(description = "任务ID") @PathVariable Long id,
            @Parameter(description = "操作人") @RequestParam(required = false) String changedBy) {
        TaskResponse task = taskService.reopenTask(id, changedBy);
        return ResponseEntity.ok(task);
    }

    @GetMapping("/{id}/history")
    @Operation(summary = "获取任务状态历史", description = "获取任务的状态变更历史记录")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "成功获取状态历史"),
            @ApiResponse(responseCode = "404", description = "任务不存在")
    })
    public ResponseEntity<List<TaskStatusHistory>> getTaskStatusHistory(
            @Parameter(description = "任务ID") @PathVariable Long id) {
        List<TaskStatusHistory> history = taskService.getTaskStatusHistory(id);
        return ResponseEntity.ok(history);
    }
}
