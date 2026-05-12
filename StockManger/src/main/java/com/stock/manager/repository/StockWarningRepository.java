package com.stock.manager.repository;

import com.stock.manager.entity.StockWarning;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StockWarningRepository extends JpaRepository<StockWarning, Long> {
    List<StockWarning> findByResolved(Boolean resolved);
    List<StockWarning> findByWarningTypeAndResolved(String warningType, Boolean resolved);
    List<StockWarning> findByProductId(Long productId);
    
    Optional<StockWarning> findTopByProductIdAndWarningTypeAndResolvedOrderByCreatedAtDesc(
            Long productId, String warningType, Boolean resolved);
}
