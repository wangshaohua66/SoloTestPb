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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class TaskService {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private TaskStatusHistoryRepository statusHistoryRepository;

    private static final List<TaskStatus> COMPLETED_STATUSES = Arrays.asList(TaskStatus.COMPLETED, TaskStatus.CANCELLED);

    @Transactional
    public TaskResponse createTask(CreateTaskRequest request) {
        Task task = new Task();
        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setPriority(request.getPriority() != null ? request.getPriority() : TaskPriority.MEDIUM);
        task.setDueDate(request.getDueDate());
        task.setAssignee(request.getAssignee());
        task.setCreator(request.getCreator());
        task.setStatus(TaskStatus.TODO);

        Task savedTask = taskRepository.save(task);
        return toResponse(savedTask);
    }

    public TaskResponse getTaskById(Long id) {
        Task task = findTaskById(id);
        return toResponse(task);
    }

    public List<TaskResponse> getAllTasks() {
        List<Task> tasks = taskRepository.findAllOrderedByPriorityAndDueDate();
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getTasksByAssignee(String assignee) {
        List<Task> tasks = taskRepository.findByAssignee(assignee);
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getTasksByCreator(String creator) {
        List<Task> tasks = taskRepository.findByCreator(creator);
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getTasksByStatus(TaskStatus status) {
        List<Task> tasks = taskRepository.findByStatusInOrderByPriorityAndDueDate(Arrays.asList(status));
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getTasksByPriority(TaskPriority priority) {
        List<Task> tasks = taskRepository.findByPriority(priority);
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getTasksByDateRange(LocalDate startDate, LocalDate endDate) {
        List<Task> tasks = taskRepository.findByDueDateBetween(startDate, endDate);
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    public List<TaskResponse> getOverdueTasks() {
        LocalDate today = LocalDate.now();
        List<Task> tasks = taskRepository.findOverdueTasks(today, COMPLETED_STATUSES);
        return tasks.stream().map(this::toResponse).collect(Collectors.toList());
    }

    @Transactional
    public TaskResponse updateTask(Long id, UpdateTaskRequest request) {
        Task task = findTaskById(id);

        if (request.getTitle() != null) {
            task.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            task.setDescription(request.getDescription());
        }
        if (request.getPriority() != null) {
            task.setPriority(request.getPriority());
        }
        if (request.getDueDate() != null) {
            task.setDueDate(request.getDueDate());
        }

        Task updatedTask = taskRepository.save(task);
        return toResponse(updatedTask);
    }

    @Transactional
    public TaskResponse assignTask(Long id, String assignee, String changedBy) {
        Task task = findTaskById(id);
        task.setAssignee(assignee);
        Task updatedTask = taskRepository.save(task);
        return toResponse(updatedTask);
    }

    @Transactional
    public TaskResponse claimTask(Long id, String assignee) {
        Task task = findTaskById(id);
        if (task.getStatus() != TaskStatus.TODO) {
            throw new InvalidTaskStatusTransitionException("只能认领待办状态的任务");
        }
        if (task.getAssignee() != null && !task.getAssignee().isEmpty()) {
            throw new InvalidTaskStatusTransitionException("任务已被认领，无法重复认领");
        }
        task.setAssignee(assignee);
        Task updatedTask = taskRepository.save(task);
        return toResponse(updatedTask);
    }

    @Transactional
    public TaskResponse startTask(Long id, String changedBy) {
        return changeStatus(id, TaskStatus.IN_PROGRESS, changedBy);
    }

    @Transactional
    public TaskResponse completeTask(Long id, String changedBy) {
        return changeStatus(id, TaskStatus.COMPLETED, changedBy);
    }

    @Transactional
    public TaskResponse cancelTask(Long id, String changedBy) {
        return changeStatus(id, TaskStatus.CANCELLED, changedBy);
    }

    @Transactional
    public TaskResponse reopenTask(Long id, String changedBy) {
        Task task = findTaskById(id);
        if (task.getStatus() != TaskStatus.CANCELLED && task.getStatus() != TaskStatus.COMPLETED) {
            throw new InvalidTaskStatusTransitionException("只有已完成或已取消的任务才能重新打开");
        }
        return changeStatus(id, TaskStatus.TODO, changedBy);
    }

    private TaskResponse changeStatus(Long id, TaskStatus newStatus, String changedBy) {
        Task task = findTaskById(id);
        TaskStatus oldStatus = task.getStatus();

        if (oldStatus == newStatus) {
            return toResponse(task);
        }

        validateStatusTransition(oldStatus, newStatus);

        task.setStatus(newStatus);
        Task updatedTask = taskRepository.save(task);

        saveStatusHistory(task.getId(), oldStatus, newStatus, changedBy);

        return toResponse(updatedTask);
    }

    private void validateStatusTransition(TaskStatus fromStatus, TaskStatus toStatus) {
        switch (fromStatus) {
            case TODO:
                if (toStatus != TaskStatus.IN_PROGRESS && toStatus != TaskStatus.CANCELLED) {
                    throw new InvalidTaskStatusTransitionException("无效的状态转换: " + fromStatus + " -> " + toStatus);
                }
                break;
            case IN_PROGRESS:
                if (toStatus != TaskStatus.COMPLETED && toStatus != TaskStatus.CANCELLED) {
                    throw new InvalidTaskStatusTransitionException("无效的状态转换: " + fromStatus + " -> " + toStatus);
                }
                break;
            case COMPLETED:
            case CANCELLED:
                if (toStatus != TaskStatus.TODO) {
                    throw new InvalidTaskStatusTransitionException("无效的状态转换: " + fromStatus + " -> " + toStatus);
                }
                break;
        }
    }

    private void saveStatusHistory(Long taskId, TaskStatus fromStatus, TaskStatus toStatus, String changedBy) {
        TaskStatusHistory history = new TaskStatusHistory();
        history.setTaskId(taskId);
        history.setFromStatus(fromStatus);
        history.setToStatus(toStatus);
        history.setChangedBy(changedBy);
        statusHistoryRepository.save(history);
    }

    @Transactional
    public void deleteTask(Long id) {
        Task task = findTaskById(id);
        taskRepository.delete(task);
    }

    public List<TaskStatusHistory> getTaskStatusHistory(Long taskId) {
        return statusHistoryRepository.findByTaskIdOrderByChangedAtDesc(taskId);
    }

    private Task findTaskById(Long id) {
        return taskRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("任务不存在: " + id));
    }

    private TaskResponse toResponse(Task task) {
        boolean overdue = false;
        if (task.getDueDate() != null && !COMPLETED_STATUSES.contains(task.getStatus())) {
            overdue = task.getDueDate().isBefore(LocalDate.now());
        }

        return TaskResponse.builder()
                .id(task.getId())
                .title(task.getTitle())
                .description(task.getDescription())
                .status(task.getStatus())
                .priority(task.getPriority())
                .assignee(task.getAssignee())
                .creator(task.getCreator())
                .dueDate(task.getDueDate())
                .createdAt(task.getCreatedAt())
                .updatedAt(task.getUpdatedAt())
                .overdue(overdue)
                .build();
    }
}
