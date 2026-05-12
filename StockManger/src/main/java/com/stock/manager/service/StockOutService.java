package com.stock.manager.service;

import com.stock.manager.dto.StockOutDTO;
import com.stock.manager.entity.Product;
import com.stock.manager.entity.StockOut;
import com.stock.manager.entity.StockOutItem;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.ProductRepository;
import com.stock.manager.repository.StockOutRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

@Service
public class StockOutService {

    @Autowired
    private StockOutRepository stockOutRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryService inventoryService;

    private final AtomicInteger outNoCounter = new AtomicInteger(0);

    @Transactional
    public StockOutDTO createStockOut(StockOutDTO dto) {
        String outNo = generateOutNo();

        StockOut stockOut = new StockOut();
        stockOut.setOutNo(outNo);
        stockOut.setOutType(dto.getOutType());
        stockOut.setCustomer(dto.getCustomer());
        stockOut.setWarehouse(dto.getWarehouse());
        stockOut.setOperator(dto.getOperator());
        stockOut.setRemark(dto.getRemark());

        AtomicInteger totalQty = new AtomicInteger(0);
        AtomicReference<BigDecimal> totalAmount = new AtomicReference<>(BigDecimal.ZERO);

        for (StockOutDTO.StockOutItemDTO itemDto : dto.getItems()) {
            Product product = productRepository.findById(itemDto.getProductId())
                    .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + itemDto.getProductId()));

            StockOutItem item = new StockOutItem();
            item.setProduct(product);
            item.setQuantity(itemDto.getQuantity());
            item.setUnitPrice(itemDto.getUnitPrice());
            item.setBatchNo(itemDto.getBatchNo());

            stockOut.addItem(item);

            totalQty.addAndGet(itemDto.getQuantity());
            totalAmount.set(totalAmount.get().add(
                    itemDto.getUnitPrice().multiply(new BigDecimal(itemDto.getQuantity()))
            ));
        }

        stockOut.setTotalQuantity(totalQty.get());
        stockOut.setTotalAmount(totalAmount.get());

        stockOut = stockOutRepository.save(stockOut);

        for (StockOutItem item : stockOut.getItems()) {
            inventoryService.decreaseStock(
                    item.getProduct().getId(),
                    item.getQuantity(),
                    "STOCK_OUT",
                    stockOut.getOutNo(),
                    item.getUnitPrice(),
                    stockOut.getOperator(),
                    "出库操作"
            );
        }

        return convertToDTO(stockOut);
    }

    @Transactional(readOnly = true)
    public StockOutDTO getStockOutById(Long id) {
        StockOut stockOut = stockOutRepository.findByIdWithItems(id)
                .orElseThrow(() -> new ResourceNotFoundException("出库记录不存在: " + id));
        return convertToDTO(stockOut);
    }

    @Transactional(readOnly = true)
    public StockOutDTO getStockOutByNo(String outNo) {
        StockOut stockOut = stockOutRepository.findByOutNo(outNo)
                .orElseThrow(() -> new ResourceNotFoundException("出库记录不存在: " + outNo));
        return convertToDTO(stockOut);
    }

    @Transactional(readOnly = true)
    public List<StockOutDTO> getAllStockOut() {
        return stockOutRepository.findAllWithItems().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<StockOutDTO> getStockOutByDateRange(LocalDateTime start, LocalDateTime end) {
        return stockOutRepository.findByCreatedAtBetween(start, end).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private String generateOutNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int seq = outNoCounter.incrementAndGet();
        return "OUT" + dateStr + String.format("%04d", seq);
    }

    private StockOutDTO convertToDTO(StockOut stockOut) {
        StockOutDTO dto = new StockOutDTO();
        dto.setId(stockOut.getId());
        dto.setOutNo(stockOut.getOutNo());
        dto.setOutType(stockOut.getOutType());
        dto.setCustomer(stockOut.getCustomer());
        dto.setWarehouse(stockOut.getWarehouse());
        dto.setOperator(stockOut.getOperator());
        dto.setTotalQuantity(stockOut.getTotalQuantity());
        dto.setTotalAmount(stockOut.getTotalAmount());
        dto.setRemark(stockOut.getRemark());

        if (stockOut.getItems() != null) {
            List<StockOutDTO.StockOutItemDTO> itemDTOs = stockOut.getItems().stream()
                    .map(item -> {
                        StockOutDTO.StockOutItemDTO itemDto = new StockOutDTO.StockOutItemDTO();
                        itemDto.setId(item.getId());
                        itemDto.setProductId(item.getProduct().getId());
                        itemDto.setQuantity(item.getQuantity());
                        itemDto.setUnitPrice(item.getUnitPrice());
                        itemDto.setBatchNo(item.getBatchNo());
                        return itemDto;
                    })
                    .collect(Collectors.toList());
            dto.setItems(itemDTOs);
        }

        return dto;
    }
}
