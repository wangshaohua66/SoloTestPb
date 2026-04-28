package com.taskmanager.service;

import com.taskmanager.dto.CreateTaskRequest;
import com.taskmanager.dto.TaskResponse;
import com.taskmanager.dto.UpdateTaskRequest;
import com.taskmanager.entity.Task;
import com.taskmanager.entity.TaskStatusHistory;
import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import com.taskmanager.exception.InvalidTaskStatusTransitionException;
import com.taskmanager.exception.ResourceNotFoundException;
import com.taskmanager.repository.TaskRepository;
import com.taskmanager.repository.TaskStatusHistoryRepository;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@Feature("任务服务 - TaskService")
@DisplayName("TaskService 单元测试")
class TaskServiceTest {

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private TaskStatusHistoryRepository statusHistoryRepository;

    @InjectMocks
    private TaskService taskService;

    private Task task;

    @BeforeEach
    void setUp() {
        task = new Task();
        task.setId(1L);
        task.setTitle("测试任务");
        task.setDescription("测试描述");
        task.setStatus(TaskStatus.TODO);
        task.setPriority(TaskPriority.MEDIUM);
        task.setCreator("user1");
        task.setAssignee(null);
        task.setDueDate(LocalDate.now().plusDays(3));
    }

    @Test
    @Story("创建任务")
    @Description("测试创建任务功能，验证任务是否正确保存")
    @DisplayName("创建任务 - 应返回创建的任务")
    void createTask_ShouldReturnCreatedTask() {
        CreateTaskRequest request = new CreateTaskRequest();
        request.setTitle("新任务");
        request.setDescription("新描述");
        request.setPriority(TaskPriority.HIGH);
        request.setCreator("user1");
        request.setDueDate(LocalDate.now().plusDays(5));

        Task savedTask = new Task();
        savedTask.setId(1L);
        savedTask.setTitle("新任务");
        savedTask.setStatus(TaskStatus.TODO);
        savedTask.setPriority(TaskPriority.HIGH);
        savedTask.setCreator("user1");

        when(taskRepository.save(any(Task.class))).thenReturn(savedTask);

        TaskResponse result = taskService.createTask(request);

        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("新任务", result.getTitle());
        assertEquals(TaskStatus.TODO, result.getStatus());
        assertEquals(TaskPriority.HIGH, result.getPriority());
        verify(taskRepository, times(1)).save(any(Task.class));
    }

    @Test
    @Story("查询任务")
    @Description("测试根据ID获取任务功能")
    @DisplayName("获取任务 - 有效ID应返回任务")
    void getTaskById_WithValidId_ShouldReturnTask() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        TaskResponse result = taskService.getTaskById(1L);

        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("测试任务", result.getTitle());
    }

    @Test
    @Story("查询任务")
    @Description("测试根据无效ID获取任务功能，应抛出异常")
    @DisplayName("获取任务 - 无效ID应抛出异常")
    void getTaskById_WithInvalidId_ShouldThrowException() {
        when(taskRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> taskService.getTaskById(99L));
    }

    @Test
    @Story("查询任务")
    @Description("测试获取所有任务功能")
    @DisplayName("获取所有任务 - 应返回任务列表")
    void getAllTasks_ShouldReturnAllTasks() {
        Task task2 = new Task();
        task2.setId(2L);
        task2.setTitle("任务2");
        task2.setStatus(TaskStatus.IN_PROGRESS);
        task2.setPriority(TaskPriority.HIGH);

        when(taskRepository.findAllOrderedByPriorityAndDueDate()).thenReturn(Arrays.asList(task2, task));

        List<TaskResponse> result = taskService.getAllTasks();

        assertEquals(2, result.size());
    }

    @Test
    @Story("更新任务")
    @Description("测试更新任务信息功能")
    @DisplayName("更新任务 - 应更新任务信息")
    void updateTask_ShouldUpdateTask() {
        UpdateTaskRequest request = new UpdateTaskRequest();
        request.setTitle("更新后的任务");
        request.setPriority(TaskPriority.HIGH);

        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.updateTask(1L, request);

        assertEquals("更新后的任务", result.getTitle());
        assertEquals(TaskPriority.HIGH, result.getPriority());
    }

    @Test
    @Story("状态流转")
    @Description("测试将任务从待办状态改为进行中")
    @DisplayName("开始任务 - 应将状态改为进行中")
    void startTask_ShouldChangeStatusToInProgress() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.startTask(1L, "user1");

        assertEquals(TaskStatus.IN_PROGRESS, result.getStatus());
        verify(statusHistoryRepository, times(1)).save(any(TaskStatusHistory.class));
    }

    @Test
    @Story("状态流转")
    @Description("测试将任务从进行中状态改为已完成")
    @DisplayName("完成任务 - 应将状态改为已完成")
    void completeTask_ShouldChangeStatusToCompleted() {
        task.setStatus(TaskStatus.IN_PROGRESS);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.completeTask(1L, "user1");

        assertEquals(TaskStatus.COMPLETED, result.getStatus());
    }

    @Test
    @Story("状态流转")
    @Description("测试取消待办任务")
    @DisplayName("取消任务 - 应将状态改为已取消")
    void cancelTask_ShouldChangeStatusToCancelled() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.cancelTask(1L, "user1");

        assertEquals(TaskStatus.CANCELLED, result.getStatus());
    }

    @Test
    @Story("状态流转")
    @Description("测试重新打开已取消的任务")
    @DisplayName("重新打开任务 - 已取消任务应改为待办")
    void reopenTask_WhenCancelled_ShouldChangeStatusToTodo() {
        task.setStatus(TaskStatus.CANCELLED);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.reopenTask(1L, "user1");

        assertEquals(TaskStatus.TODO, result.getStatus());
    }

    @Test
    @Story("状态流转")
    @Description("测试重新打开进行中的任务，应抛出异常")
    @DisplayName("重新打开任务 - 非取消/完成状态应抛出异常")
    void reopenTask_WhenNotCancelledOrCompleted_ShouldThrowException() {
        task.setStatus(TaskStatus.IN_PROGRESS);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        assertThrows(InvalidTaskStatusTransitionException.class, () -> taskService.reopenTask(1L, "user1"));
    }

    @Test
    @Story("任务分配")
    @Description("测试分配任务给指定用户")
    @DisplayName("分配任务 - 应设置受让人")
    void assignTask_ShouldSetAssignee() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.assignTask(1L, "user2", "user1");

        assertEquals("user2", result.getAssignee());
    }

    @Test
    @Story("任务认领")
    @Description("测试认领未分配的待办任务")
    @DisplayName("认领任务 - 未分配任务应设置受让人")
    void claimTask_WhenNotAssigned_ShouldSetAssignee() {
        task.setAssignee(null);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.claimTask(1L, "user2");

        assertEquals("user2", result.getAssignee());
    }

    @Test
    @Story("任务认领")
    @Description("测试认领已分配的任务，应抛出异常")
    @DisplayName("认领任务 - 已分配任务应抛出异常")
    void claimTask_WhenAlreadyAssigned_ShouldThrowException() {
        task.setAssignee("user2");
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        assertThrows(InvalidTaskStatusTransitionException.class, () -> taskService.claimTask(1L, "user3"));
    }

    @Test
    @Story("任务认领")
    @Description("测试认领非待办状态的任务，应抛出异常")
    @DisplayName("认领任务 - 非待办状态应抛出异常")
    void claimTask_WhenStatusNotTodo_ShouldThrowException() {
        task.setStatus(TaskStatus.IN_PROGRESS);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        assertThrows(InvalidTaskStatusTransitionException.class, () -> taskService.claimTask(1L, "user2"));
    }

    @Test
    @Story("任务认领")
    @Description("测试认领已完成状态的任务，应抛出异常")
    @DisplayName("认领任务 - 已完成状态应抛出异常")
    void claimTask_WhenStatusCompleted_ShouldThrowException() {
        task.setStatus(TaskStatus.COMPLETED);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        assertThrows(InvalidTaskStatusTransitionException.class, () -> taskService.claimTask(1L, "user2"));
    }

    @Test
    @Story("删除任务")
    @Description("测试删除任务功能")
    @DisplayName("删除任务 - 应成功删除")
    void deleteTask_ShouldDeleteTask() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));
        doNothing().when(taskRepository).delete(task);

        taskService.deleteTask(1L);

        verify(taskRepository, times(1)).delete(task);
    }

    @Test
    @Story("查询任务")
    @Description("测试根据受让人查询任务")
    @DisplayName("查询任务 - 按受让人查询")
    void getTasksByAssignee_ShouldReturnTasks() {
        task.setAssignee("user1");
        when(taskRepository.findByAssignee("user1")).thenReturn(Arrays.asList(task));

        List<TaskResponse> result = taskService.getTasksByAssignee("user1");

        assertEquals(1, result.size());
        assertEquals("user1", result.get(0).getAssignee());
    }

    @Test
    @Story("查询任务")
    @Description("测试根据状态查询任务")
    @DisplayName("查询任务 - 按状态查询")
    void getTasksByStatus_ShouldReturnTasks() {
        when(taskRepository.findByStatusInOrderByPriorityAndDueDate(anyList())).thenReturn(Arrays.asList(task));

        List<TaskResponse> result = taskService.getTasksByStatus(TaskStatus.TODO);

        assertEquals(1, result.size());
    }

    @Test
    @Story("查询任务")
    @Description("测试根据优先级查询任务")
    @DisplayName("查询任务 - 按优先级查询")
    void getTasksByPriority_ShouldReturnTasks() {
        when(taskRepository.findByPriority(TaskPriority.HIGH)).thenReturn(Arrays.asList(task));

        List<TaskResponse> result = taskService.getTasksByPriority(TaskPriority.HIGH);

        assertEquals(1, result.size());
    }

    @Test
    @Story("状态流转")
    @Description("测试无效的状态转换，应抛出异常")
    @DisplayName("状态转换 - 无效转换应抛出异常")
    void invalidStatusTransition_ShouldThrowException() {
        task.setStatus(TaskStatus.COMPLETED);
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        assertThrows(InvalidTaskStatusTransitionException.class, () -> taskService.startTask(1L, "user1"));
    }
}
