package com.stock.manager.service;

import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.entity.StockTransaction;
import com.stock.manager.entity.StockWarning;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.InventoryRepository;
import com.stock.manager.repository.ProductRepository;
import com.stock.manager.repository.StockTransactionRepository;
import com.stock.manager.repository.StockWarningRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class InventoryService {

    private static final Logger log = LoggerFactory.getLogger(InventoryService.class);

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private StockWarningRepository stockWarningRepository;

    @Autowired
    private StockTransactionRepository stockTransactionRepository;

    @Autowired
    private WarningConfigService warningConfigService;

    @Transactional(readOnly = true)
    public Inventory getInventoryByProductId(Long productId) {
        return inventoryRepository.findByProductId(productId)
                .orElseThrow(() -> new ResourceNotFoundException("库存不存在: 商品ID=" + productId));
    }

    @Transactional(readOnly = true)
    public List<Inventory> getAllInventory() {
        return inventoryRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<Inventory> getLowStockItems() {
        return inventoryRepository.findLowStockItems();
    }

    @Transactional(readOnly = true)
    public List<Inventory> getHighStockItems() {
        return inventoryRepository.findHighStockItems();
    }

    @Transactional
    public void increaseStock(Long productId, int quantity, String transactionType, 
                               String referenceNo, BigDecimal unitPrice, String operator, String remark) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("入库数量必须大于0");
        }

        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + productId));

        Inventory inventory = inventoryRepository.findByProduct(product)
                .orElseThrow(() -> new ResourceNotFoundException("库存不存在: 商品ID=" + productId));

        int beforeQuantity = inventory.getQuantity();
        int afterQuantity = beforeQuantity + quantity;

        inventory.setQuantity(afterQuantity);
        inventoryRepository.save(inventory);

        StockTransaction transaction = new StockTransaction();
        transaction.setTransactionType(transactionType);
        transaction.setReferenceNo(referenceNo);
        transaction.setProduct(product);
        transaction.setBeforeQuantity(beforeQuantity);
        transaction.setChangeQuantity(quantity);
        transaction.setAfterQuantity(afterQuantity);
        transaction.setUnitPrice(unitPrice);
        transaction.setAmount(unitPrice != null ? unitPrice.multiply(new BigDecimal(quantity)) : null);
        transaction.setOperator(operator);
        transaction.setRemark(remark);
        stockTransactionRepository.save(transaction);

        checkStockWarning(product, afterQuantity);
    }

    @Transactional
    public void decreaseStock(Long productId, int quantity, String transactionType,
                               String referenceNo, BigDecimal unitPrice, String operator, String remark) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("出库数量必须大于0");
        }

        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + productId));

        Inventory inventory = inventoryRepository.findByProduct(product)
                .orElseThrow(() -> new ResourceNotFoundException("库存不存在: 商品ID=" + productId));

        int beforeQuantity = inventory.getQuantity();
        if (beforeQuantity < quantity) {
            throw new IllegalStateException("库存不足: 当前库存=" + beforeQuantity + ", 出库数量=" + quantity);
        }

        int afterQuantity = beforeQuantity - quantity;

        inventory.setQuantity(afterQuantity);
        inventoryRepository.save(inventory);

        StockTransaction transaction = new StockTransaction();
        transaction.setTransactionType(transactionType);
        transaction.setReferenceNo(referenceNo);
        transaction.setProduct(product);
        transaction.setBeforeQuantity(beforeQuantity);
        transaction.setChangeQuantity(-quantity);
        transaction.setAfterQuantity(afterQuantity);
        transaction.setUnitPrice(unitPrice);
        transaction.setAmount(unitPrice != null ? unitPrice.multiply(new BigDecimal(quantity)) : null);
        transaction.setOperator(operator);
        transaction.setRemark(remark);
        stockTransactionRepository.save(transaction);

        checkStockWarning(product, afterQuantity);
    }

    private void checkStockWarning(Product product, int currentStock) {
        Integer minStock = product.getMinStock();
        Integer maxStock = product.getMaxStock();

        if (warningConfigService.isLowStockWarningEnabled() 
                && minStock != null && currentStock <= minStock) {
            Optional<StockWarning> existingWarning = stockWarningRepository
                    .findTopByProductIdAndWarningTypeAndResolvedOrderByCreatedAtDesc(
                            product.getId(), "LOW_STOCK", false);
            
            if (!existingWarning.isPresent()) {
                StockWarning warning = new StockWarning();
                warning.setProduct(product);
                warning.setWarningType("LOW_STOCK");
                warning.setCurrentStock(currentStock);
                warning.setThreshold(minStock);
                String warningMsg = "商品[" + product.getProductName() + "(" + product.getProductCode() + ")]库存低于下限: 当前=" + currentStock + ", 下限=" + minStock;
                warning.setMessage(warningMsg);
                warning.setResolved(false);
                stockWarningRepository.save(warning);
                log.warn("[库存预警-下限] {}", warningMsg);
            }
        }

        if (warningConfigService.isHighStockWarningEnabled() 
                && maxStock != null && currentStock >= maxStock) {
            Optional<StockWarning> existingWarning = stockWarningRepository
                    .findTopByProductIdAndWarningTypeAndResolvedOrderByCreatedAtDesc(
                            product.getId(), "HIGH_STOCK", false);
            
            if (!existingWarning.isPresent()) {
                StockWarning warning = new StockWarning();
                warning.setProduct(product);
                warning.setWarningType("HIGH_STOCK");
                warning.setCurrentStock(currentStock);
                warning.setThreshold(maxStock);
                String warningMsg = "商品[" + product.getProductName() + "(" + product.getProductCode() + ")]库存超过上限: 当前=" + currentStock + ", 上限=" + maxStock;
                warning.setMessage(warningMsg);
                warning.setResolved(false);
                stockWarningRepository.save(warning);
                log.warn("[库存预警-上限] {}", warningMsg);
            }
        }
    }

    @Transactional(readOnly = true)
    public List<StockTransaction> getTransactionHistory(Long productId) {
        return stockTransactionRepository.findByProductIdOrderByCreatedAtDesc(productId);
    }

    @Transactional(readOnly = true)
    public List<StockTransaction> getAllTransactions() {
        return stockTransactionRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<StockTransaction> getTransactionsByDateRange(LocalDateTime start, LocalDateTime end) {
        return stockTransactionRepository.findByCreatedAtBetweenOrderByCreatedAtDesc(start, end);
    }
}
