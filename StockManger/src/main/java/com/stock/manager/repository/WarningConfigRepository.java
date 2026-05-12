package com.stock.manager.repository;

import com.stock.manager.entity.WarningConfig;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface WarningConfigRepository extends JpaRepository<WarningConfig, Long> {
    
    Optional<WarningConfig> findByConfigKey(String configKey);
    
    boolean existsByConfigKey(String configKey);
}
