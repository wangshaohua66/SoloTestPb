package com.stock.manager.repository;

import com.stock.manager.entity.CheckRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface CheckRecordRepository extends JpaRepository<CheckRecord, Long> {
    Optional<CheckRecord> findByCheckNo(String checkNo);
    List<CheckRecord> findByCompleted(Boolean completed);
    List<CheckRecord> findByWarehouse(String warehouse);
    List<CheckRecord> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT c FROM CheckRecord c LEFT JOIN FETCH c.items WHERE c.id = :id")
    Optional<CheckRecord> findByIdWithItems(Long id);
    
    @Query("SELECT c FROM CheckRecord c LEFT JOIN FETCH c.items ORDER BY c.createdAt DESC")
    List<CheckRecord> findAllWithItems();
}
