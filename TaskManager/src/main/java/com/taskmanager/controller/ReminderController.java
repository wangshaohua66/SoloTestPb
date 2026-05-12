package com.taskmanager.controller;

import com.taskmanager.scheduler.TaskReminderScheduler;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/reminders")
@Tag(name = "提醒管理", description = "手动触发提醒检查的API")
public class ReminderController {

    @Autowired
    private TaskReminderScheduler reminderScheduler;

    @PostMapping("/check-overdue")
    @Operation(summary = "手动触发逾期任务检查", description = "立即执行逾期任务检查和提醒")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "逾期检查执行成功")
    })
    public ResponseEntity<Map<String, Object>> checkOverdueTasks() {
        reminderScheduler.checkOverdueTasks();
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "逾期任务检查已执行，请查看日志输出");
        response.put("timestamp", java.time.LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }

    @PostMapping("/check-priority")
    @Operation(summary = "手动触发高优先级任务提醒", description = "立即执行高优先级任务提醒")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "高优先级提醒执行成功")
    })
    public ResponseEntity<Map<String, Object>> checkHighPriorityTasks() {
        reminderScheduler.checkHighPriorityTasks();
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "高优先级任务提醒已执行，请查看日志输出");
        response.put("timestamp", java.time.LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }

    @PostMapping("/check-all")
    @Operation(summary = "手动触发所有提醒检查", description = "立即执行所有提醒检查（逾期和高优先级）")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "所有提醒检查执行成功")
    })
    public ResponseEntity<Map<String, Object>> checkAllReminders() {
        reminderScheduler.checkOverdueTasks();
        reminderScheduler.checkHighPriorityTasks();
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("message", "所有提醒检查已执行，请查看日志输出");
        response.put("timestamp", java.time.LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }
}
