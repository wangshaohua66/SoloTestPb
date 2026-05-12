package com.stock.manager.repository;

import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Long> {
    Optional<Inventory> findByProduct(Product product);
    Optional<Inventory> findByProductId(Long productId);
    
    @Query("SELECT i FROM Inventory i JOIN FETCH i.product p WHERE i.quantity <= p.minStock")
    List<Inventory> findLowStockItems();
    
    @Query("SELECT i FROM Inventory i JOIN FETCH i.product p WHERE i.quantity >= p.maxStock")
    List<Inventory> findHighStockItems();
}
