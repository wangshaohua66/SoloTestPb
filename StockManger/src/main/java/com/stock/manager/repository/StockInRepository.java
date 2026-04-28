package com.stock.manager.repository;

import com.stock.manager.entity.StockIn;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface StockInRepository extends JpaRepository<StockIn, Long> {
    Optional<StockIn> findByInNo(String inNo);
    List<StockIn> findByInType(String inType);
    List<StockIn> findBySupplier(String supplier);
    List<StockIn> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT s FROM StockIn s LEFT JOIN FETCH s.items WHERE s.id = :id")
    Optional<StockIn> findByIdWithItems(Long id);
    
    @Query("SELECT s FROM StockIn s LEFT JOIN FETCH s.items ORDER BY s.createdAt DESC")
    List<StockIn> findAllWithItems();
}
