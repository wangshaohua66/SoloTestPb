package com.stock.manager.repository;

import com.stock.manager.entity.CheckItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CheckItemRepository extends JpaRepository<CheckItem, Long> {
    List<CheckItem> findByCheckRecordId(Long checkRecordId);
    List<CheckItem> findByProductId(Long productId);
    List<CheckItem> findByCheckRecordIdAndAdjusted(Long checkRecordId, Boolean adjusted);
}
