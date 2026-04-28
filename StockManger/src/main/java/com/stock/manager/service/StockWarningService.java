package com.stock.manager.service;

import com.stock.manager.entity.StockWarning;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.StockWarningRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class StockWarningService {

    @Autowired
    private StockWarningRepository stockWarningRepository;

    @Transactional(readOnly = true)
    public List<StockWarning> getAllWarnings() {
        return stockWarningRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<StockWarning> getUnresolvedWarnings() {
        return stockWarningRepository.findByResolved(false);
    }

    @Transactional(readOnly = true)
    public List<StockWarning> getResolvedWarnings() {
        return stockWarningRepository.findByResolved(true);
    }

    @Transactional(readOnly = true)
    public List<StockWarning> getLowStockWarnings() {
        return stockWarningRepository.findByWarningTypeAndResolved("LOW_STOCK", false);
    }

    @Transactional(readOnly = true)
    public List<StockWarning> getHighStockWarnings() {
        return stockWarningRepository.findByWarningTypeAndResolved("HIGH_STOCK", false);
    }

    @Transactional(readOnly = true)
    public List<StockWarning> getWarningsByProductId(Long productId) {
        return stockWarningRepository.findByProductId(productId);
    }

    @Transactional
    public StockWarning resolveWarning(Long id, String resolvedBy) {
        StockWarning warning = stockWarningRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("预警记录不存在: " + id));

        warning.setResolved(true);
        warning.setResolvedAt(LocalDateTime.now());
        warning.setResolvedBy(resolvedBy);

        return stockWarningRepository.save(warning);
    }

    @Transactional
    public void resolveAllWarnings(String resolvedBy) {
        List<StockWarning> warnings = stockWarningRepository.findByResolved(false);
        for (StockWarning warning : warnings) {
            warning.setResolved(true);
            warning.setResolvedAt(LocalDateTime.now());
            warning.setResolvedBy(resolvedBy);
        }
        stockWarningRepository.saveAll(warnings);
    }
}
