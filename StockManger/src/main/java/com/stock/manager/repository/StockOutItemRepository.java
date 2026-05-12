package com.stock.manager.repository;

import com.stock.manager.entity.StockOutItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface StockOutItemRepository extends JpaRepository<StockOutItem, Long> {
    List<StockOutItem> findByStockOutId(Long stockOutId);
    List<StockOutItem> findByProductId(Long productId);
}
