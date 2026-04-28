package com.stock.manager.repository;

import com.stock.manager.entity.StockOut;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface StockOutRepository extends JpaRepository<StockOut, Long> {
    Optional<StockOut> findByOutNo(String outNo);
    List<StockOut> findByOutType(String outType);
    List<StockOut> findByCustomer(String customer);
    List<StockOut> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT s FROM StockOut s LEFT JOIN FETCH s.items WHERE s.id = :id")
    Optional<StockOut> findByIdWithItems(Long id);
    
    @Query("SELECT s FROM StockOut s LEFT JOIN FETCH s.items ORDER BY s.createdAt DESC")
    List<StockOut> findAllWithItems();
}
