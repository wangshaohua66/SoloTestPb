package com.taskmanager.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.taskmanager.dto.AssignTaskRequest;
import com.taskmanager.dto.CreateTaskRequest;
import com.taskmanager.dto.UpdateTaskRequest;
import com.taskmanager.entity.Task;
import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import com.taskmanager.repository.TaskRepository;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@Feature("任务管理 API - TaskController")
@DisplayName("TaskController 集成测试")
class TaskControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private TaskRepository taskRepository;

    private ObjectMapper objectMapper;

    private Task testTask;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());

        taskRepository.deleteAll();

        testTask = new Task();
        testTask.setTitle("测试任务");
        testTask.setDescription("测试描述");
        testTask.setStatus(TaskStatus.TODO);
        testTask.setPriority(TaskPriority.MEDIUM);
        testTask.setCreator("user1");
        testTask.setDueDate(LocalDate.now().plusDays(5));
        testTask = taskRepository.save(testTask);
    }

    @Test
    @Story("创建任务")
    @Description("测试创建任务API，验证输入数据正确时返回201 Created")
    @DisplayName("创建任务 - 有效数据应返回201")
    void createTask_WithValidData_ShouldReturnCreated() throws Exception {
        CreateTaskRequest request = new CreateTaskRequest();
        request.setTitle("新任务");
        request.setDescription("新任务描述");
        request.setPriority(TaskPriority.HIGH);
        request.setCreator("user2");
        request.setDueDate(LocalDate.now().plusDays(3));

        mockMvc.perform(post("/api/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.title", is("新任务")))
                .andExpect(jsonPath("$.status", is("TODO")))
                .andExpect(jsonPath("$.priority", is("HIGH")))
                .andExpect(jsonPath("$.creator", is("user2")));
    }

    @Test
    @Story("创建任务")
    @Description("测试创建任务API，验证缺少必填字段时返回400 Bad Request")
    @DisplayName("创建任务 - 缺少标题应返回400")
    void createTask_WithMissingTitle_ShouldReturnBadRequest() throws Exception {
        CreateTaskRequest request = new CreateTaskRequest();
        request.setCreator("user1");

        mockMvc.perform(post("/api/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error", is("Validation Failed")))
                .andExpect(jsonPath("$.errors.title", is("任务标题不能为空")));
    }

    @Test
    @Story("查询任务")
    @Description("测试获取所有任务API")
    @DisplayName("获取所有任务 - 应返回任务列表")
    void getAllTasks_ShouldReturnTasksList() throws Exception {
        mockMvc.perform(get("/api/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].title", is("测试任务")));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据ID获取任务API")
    @DisplayName("获取任务 - 有效ID应返回任务")
    void getTaskById_WithValidId_ShouldReturnTask() throws Exception {
        mockMvc.perform(get("/api/tasks/{id}", testTask.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(testTask.getId().intValue())))
                .andExpect(jsonPath("$.title", is("测试任务")));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据无效ID获取任务API，应返回404")
    @DisplayName("获取任务 - 无效ID应返回404")
    void getTaskById_WithInvalidId_ShouldReturnNotFound() throws Exception {
        mockMvc.perform(get("/api/tasks/{id}", 999L))
                .andExpect(status().isNotFound());
    }

    @Test
    @Story("更新任务")
    @Description("测试更新任务API")
    @DisplayName("更新任务 - 应成功更新")
    void updateTask_ShouldUpdateTask() throws Exception {
        UpdateTaskRequest request = new UpdateTaskRequest();
        request.setTitle("更新后的任务");
        request.setPriority(TaskPriority.HIGH);

        mockMvc.perform(put("/api/tasks/{id}", testTask.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title", is("更新后的任务")))
                .andExpect(jsonPath("$.priority", is("HIGH")));
    }

    @Test
    @Story("删除任务")
    @Description("测试删除任务API")
    @DisplayName("删除任务 - 应返回204")
    void deleteTask_ShouldReturnNoContent() throws Exception {
        mockMvc.perform(delete("/api/tasks/{id}", testTask.getId()))
                .andExpect(status().isNoContent());
    }

    @Test
    @Story("查询任务")
    @Description("测试根据状态查询任务API")
    @DisplayName("获取任务 - 按状态查询")
    void getTasksByStatus_ShouldReturnMatchingTasks() throws Exception {
        mockMvc.perform(get("/api/tasks/status/{status}", TaskStatus.TODO))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据优先级查询任务API")
    @DisplayName("获取任务 - 按优先级查询")
    void getTasksByPriority_ShouldReturnMatchingTasks() throws Exception {
        mockMvc.perform(get("/api/tasks/priority/{priority}", TaskPriority.MEDIUM))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据创建者查询任务API")
    @DisplayName("获取任务 - 按创建者查询")
    void getTasksByCreator_ShouldReturnMatchingTasks() throws Exception {
        mockMvc.perform(get("/api/tasks/creator/{creator}", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    @Story("状态流转")
    @Description("测试开始任务API，将状态从TODO改为IN_PROGRESS")
    @DisplayName("开始任务 - 应将状态改为进行中")
    void startTask_ShouldChangeStatusToInProgress() throws Exception {
        mockMvc.perform(post("/api/tasks/{id}/start", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status", is("IN_PROGRESS")));
    }

    @Test
    @Story("状态流转")
    @Description("测试完成任务API")
    @DisplayName("完成任务 - 应将状态改为已完成")
    void completeTask_ShouldChangeStatusToCompleted() throws Exception {
        testTask.setStatus(TaskStatus.IN_PROGRESS);
        testTask = taskRepository.save(testTask);

        mockMvc.perform(post("/api/tasks/{id}/complete", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status", is("COMPLETED")));
    }

    @Test
    @Story("状态流转")
    @Description("测试取消任务API")
    @DisplayName("取消任务 - 应将状态改为已取消")
    void cancelTask_ShouldChangeStatusToCancelled() throws Exception {
        mockMvc.perform(post("/api/tasks/{id}/cancel", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status", is("CANCELLED")));
    }

    @Test
    @Story("状态流转")
    @Description("测试重新打开已取消的任务API")
    @DisplayName("重新打开任务 - 已取消任务应改为待办")
    void reopenTask_WhenCancelled_ShouldChangeStatusToTodo() throws Exception {
        testTask.setStatus(TaskStatus.CANCELLED);
        testTask = taskRepository.save(testTask);

        mockMvc.perform(post("/api/tasks/{id}/reopen", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status", is("TODO")));
    }

    @Test
    @Story("任务分配")
    @Description("测试分配任务API")
    @DisplayName("分配任务 - 应设置受让人")
    void assignTask_ShouldSetAssignee() throws Exception {
        AssignTaskRequest request = new AssignTaskRequest();
        request.setAssignee("user2");

        mockMvc.perform(post("/api/tasks/{id}/assign", testTask.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.assignee", is("user2")));
    }

    @Test
    @Story("任务认领")
    @Description("测试认领未分配的待办任务API")
    @DisplayName("认领任务 - 未分配任务应设置受让人")
    void claimTask_WhenNotAssigned_ShouldSetAssignee() throws Exception {
        mockMvc.perform(post("/api/tasks/{id}/claim", testTask.getId())
                        .param("assignee", "user2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.assignee", is("user2")));
    }

    @Test
    @Story("任务认领")
    @Description("测试认领非待办状态的任务API，应返回400")
    @DisplayName("认领任务 - 非待办状态应返回400")
    void claimTask_WhenStatusNotTodo_ShouldReturnBadRequest() throws Exception {
        testTask.setStatus(TaskStatus.IN_PROGRESS);
        testTask = taskRepository.save(testTask);

        mockMvc.perform(post("/api/tasks/{id}/claim", testTask.getId())
                        .param("assignee", "user2"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @Story("任务认领")
    @Description("测试认领已分配的任务API，应返回400")
    @DisplayName("认领任务 - 已分配任务应返回400")
    void claimTask_WhenAlreadyAssigned_ShouldReturnBadRequest() throws Exception {
        testTask.setAssignee("user1");
        testTask = taskRepository.save(testTask);

        mockMvc.perform(post("/api/tasks/{id}/claim", testTask.getId())
                        .param("assignee", "user2"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @Story("查询任务")
    @Description("测试根据受让人查询任务API")
    @DisplayName("获取任务 - 按受让人查询")
    void getTasksByAssignee_ShouldReturnMatchingTasks() throws Exception {
        testTask.setAssignee("user1");
        taskRepository.save(testTask);

        mockMvc.perform(get("/api/tasks/assignee/{assignee}", "user1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    @Story("状态历史")
    @Description("测试获取任务状态历史API")
    @DisplayName("获取状态历史 - 应返回历史记录")
    void getTaskStatusHistory_ShouldReturnHistory() throws Exception {
        mockMvc.perform(post("/api/tasks/{id}/start", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/tasks/{id}/history", testTask.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].fromStatus", is("TODO")))
                .andExpect(jsonPath("$[0].toStatus", is("IN_PROGRESS")));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据日期范围查询任务API")
    @DisplayName("获取任务 - 按日期范围查询")
    void getTasksByDateRange_ShouldReturnMatchingTasks() throws Exception {
        LocalDate startDate = LocalDate.now();
        LocalDate endDate = LocalDate.now().plusDays(10);

        mockMvc.perform(get("/api/tasks/date-range")
                        .param("startDate", startDate.toString())
                        .param("endDate", endDate.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    @Test
    @Story("状态流转")
    @Description("测试无效的状态转换API，应返回400")
    @DisplayName("状态转换 - 无效转换应返回400")
    void invalidStatusTransition_ShouldReturnBadRequest() throws Exception {
        testTask.setStatus(TaskStatus.COMPLETED);
        testTask = taskRepository.save(testTask);

        mockMvc.perform(post("/api/tasks/{id}/start", testTask.getId())
                        .param("changedBy", "user1"))
                .andExpect(status().isBadRequest());
    }
}
