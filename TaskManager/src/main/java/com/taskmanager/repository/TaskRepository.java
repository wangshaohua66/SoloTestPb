package com.taskmanager.repository;

import com.taskmanager.entity.Task;
import com.taskmanager.enums.TaskPriority;
import com.taskmanager.enums.TaskStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {

    List<Task> findByAssignee(String assignee);

    List<Task> findByCreator(String creator);

    List<Task> findByStatus(TaskStatus status);

    List<Task> findByPriority(TaskPriority priority);

    List<Task> findByStatusIn(List<TaskStatus> statuses);

    List<Task> findByDueDateBetween(LocalDate startDate, LocalDate endDate);

    List<Task> findByDueDateBeforeAndStatusNotIn(LocalDate date, List<TaskStatus> statuses);

    @Query("SELECT t FROM Task t ORDER BY " +
           "CASE t.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, " +
           "t.dueDate ASC")
    List<Task> findAllOrderedByPriorityAndDueDate();

    @Query("SELECT t FROM Task t WHERE t.status IN :statuses ORDER BY " +
           "CASE t.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, " +
           "t.dueDate ASC")
    List<Task> findByStatusInOrderByPriorityAndDueDate(@Param("statuses") List<TaskStatus> statuses);

    @Query("SELECT t FROM Task t WHERE t.assignee = :assignee AND t.status IN :statuses")
    List<Task> findByAssigneeAndStatusIn(@Param("assignee") String assignee, @Param("statuses") List<TaskStatus> statuses);

    @Query("SELECT t FROM Task t WHERE t.dueDate IS NOT NULL AND t.dueDate = :tomorrow AND t.status NOT IN :completedStatuses")
    List<Task> findTasksDueTomorrow(@Param("tomorrow") LocalDate tomorrow, @Param("completedStatuses") List<TaskStatus> completedStatuses);

    @Query("SELECT t FROM Task t WHERE t.dueDate IS NOT NULL AND t.dueDate < :today AND t.status NOT IN :completedStatuses")
    List<Task> findOverdueTasks(@Param("today") LocalDate today, @Param("completedStatuses") List<TaskStatus> completedStatuses);
}
