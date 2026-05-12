package com.taskmanager.scheduler;

import com.taskmanager.dto.TaskResponse;
import com.taskmanager.service.TaskService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class TaskReminderScheduler {

    private static final Logger logger = LoggerFactory.getLogger(TaskReminderScheduler.class);

    @Autowired
    private TaskService taskService;

    @Scheduled(cron = "0 0 9 * * ?")
    public void checkOverdueTasks() {
        logger.info("========== 执行逾期任务检查 ==========");
        
        List<TaskResponse> overdueTasks = taskService.getOverdueTasks();
        
        if (overdueTasks.isEmpty()) {
            logger.info("当前没有逾期任务");
            return;
        }

        logger.warn("发现 {} 个逾期任务:", overdueTasks.size());
        for (TaskResponse task : overdueTasks) {
            String assignee = task.getAssignee() != null ? task.getAssignee() : "未分配";
            logger.warn("任务ID: {}, 标题: {}, 受让人: {}, 截止日期: {}, 优先级: {}",
                    task.getId(),
                    task.getTitle(),
                    assignee,
                    task.getDueDate(),
                    task.getPriority());
            sendOverdueReminder(task);
        }
        
        logger.info("========== 逾期任务检查完成 ==========");
    }

    @Scheduled(cron = "0 0 10 * * ?")
    public void checkHighPriorityTasks() {
        logger.info("========== 执行高优先级任务提醒 ==========");
        
        List<TaskResponse> highPriorityTasks = taskService.getTasksByStatus(
                com.taskmanager.enums.TaskStatus.TODO);
        
        long highPriorityCount = highPriorityTasks.stream()
                .filter(t -> t.getPriority() == com.taskmanager.enums.TaskPriority.HIGH)
                .count();

        if (highPriorityCount == 0) {
            logger.info("当前没有待办的高优先级任务");
            return;
        }

        logger.warn("发现 {} 个高优先级待办任务:", highPriorityCount);
        highPriorityTasks.stream()
                .filter(t -> t.getPriority() == com.taskmanager.enums.TaskPriority.HIGH)
                .forEach(task -> {
                    String assignee = task.getAssignee() != null ? task.getAssignee() : "未分配";
                    logger.warn("高优先级任务ID: {}, 标题: {}, 受让人: {}, 截止日期: {}",
                            task.getId(),
                            task.getTitle(),
                            assignee,
                            task.getDueDate());
                    sendPriorityReminder(task);
                });
        
        logger.info("========== 高优先级任务提醒完成 ==========");
    }

    private void sendOverdueReminder(TaskResponse task) {
        logger.info("发送逾期提醒: 任务 [{}] 已逾期，请尽快处理！", task.getTitle());
    }

    private void sendPriorityReminder(TaskResponse task) {
        logger.info("发送高优先级提醒: 任务 [{}] 是高优先级任务，请优先处理！", task.getTitle());
    }
}
