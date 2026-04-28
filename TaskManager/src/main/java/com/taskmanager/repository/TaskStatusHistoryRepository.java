package com.taskmanager.repository;

import com.taskmanager.entity.TaskStatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TaskStatusHistoryRepository extends JpaRepository<TaskStatusHistory, Long> {

    List<TaskStatusHistory> findByTaskIdOrderByChangedAtDesc(Long taskId);

    List<TaskStatusHistory> findByTaskId(Long taskId);
}
