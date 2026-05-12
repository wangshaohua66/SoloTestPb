package com.taskmanager.config;

import com.taskmanager.entity.Task;
import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import com.taskmanager.repository.TaskRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

@Component
@Profile("!test")
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private TaskRepository taskRepository;

    @Override
    public void run(String... args) {
        if (taskRepository.count() > 0) {
            logger.info("数据库中已有数据，跳过示例数据初始化");
            return;
        }

        logger.info("========== 开始初始化示例数据 ==========");

        Task task1 = createTask(
                "完成项目需求文档",
                "编写项目详细需求文档，包括功能需求和非功能需求",
                TaskPriority.HIGH,
                TaskStatus.IN_PROGRESS,
                "admin",
                "zhangsan",
                LocalDate.now().plusDays(2)
        );

        Task task2 = createTask(
                "数据库设计",
                "设计系统数据库表结构，包括ER图和DDL语句",
                TaskPriority.HIGH,
                TaskStatus.TODO,
                "admin",
                null,
                LocalDate.now().plusDays(3)
        );

        Task task3 = createTask(
                "API接口开发",
                "开发用户管理模块的REST API接口",
                TaskPriority.MEDIUM,
                TaskStatus.TODO,
                "admin",
                "lisi",
                LocalDate.now().plusDays(5)
        );

        Task task4 = createTask(
                "单元测试编写",
                "为Service层编写单元测试用例",
                TaskPriority.MEDIUM,
                TaskStatus.COMPLETED,
                "admin",
                "zhangsan",
                LocalDate.now().minusDays(1)
        );

        Task task5 = createTask(
                "修复代码审查问题",
                "处理代码审查中发现的问题",
                TaskPriority.HIGH,
                TaskStatus.TODO,
                "zhangsan",
                null,
                LocalDate.now().minusDays(2)
        );

        Task task6 = createTask(
                "接口文档编写",
                "编写REST API接口文档",
                TaskPriority.LOW,
                TaskStatus.TODO,
                "admin",
                "lisi",
                LocalDate.now().plusDays(7)
        );

        Task task7 = createTask(
                "性能测试",
                "对关键业务接口进行性能测试",
                TaskPriority.MEDIUM,
                TaskStatus.CANCELLED,
                "admin",
                "zhangsan",
                LocalDate.now().plusDays(10)
        );

        logger.info("========== 示例数据初始化完成，共创建 {} 条任务 ==========", taskRepository.count());
    }

    private Task createTask(String title, String description, TaskPriority priority, 
                            TaskStatus status, String creator, String assignee, LocalDate dueDate) {
        Task task = new Task();
        task.setTitle(title);
        task.setDescription(description);
        task.setPriority(priority);
        task.setStatus(status);
        task.setCreator(creator);
        task.setAssignee(assignee);
        task.setDueDate(dueDate);
        Task savedTask = taskRepository.save(task);
        logger.info("创建任务: ID={}, 标题={}, 状态={}, 优先级={}", 
                savedTask.getId(), savedTask.getTitle(), savedTask.getStatus(), savedTask.getPriority());
        return savedTask;
    }
}
