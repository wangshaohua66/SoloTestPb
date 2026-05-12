package com.stock.manager.service;

import com.stock.manager.dto.StockInDTO;
import com.stock.manager.entity.Product;
import com.stock.manager.entity.StockIn;
import com.stock.manager.entity.StockInItem;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.ProductRepository;
import com.stock.manager.repository.StockInRepository;
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
public class StockInService {

    @Autowired
    private StockInRepository stockInRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryService inventoryService;

    private final AtomicInteger inNoCounter = new AtomicInteger(0);

    @Transactional
    public StockInDTO createStockIn(StockInDTO dto) {
        String inNo = generateInNo();

        StockIn stockIn = new StockIn();
        stockIn.setInNo(inNo);
        stockIn.setInType(dto.getInType());
        stockIn.setSupplier(dto.getSupplier());
        stockIn.setWarehouse(dto.getWarehouse());
        stockIn.setOperator(dto.getOperator());
        stockIn.setRemark(dto.getRemark());

        AtomicInteger totalQty = new AtomicInteger(0);
        AtomicReference<BigDecimal> totalAmount = new AtomicReference<>(BigDecimal.ZERO);

        for (StockInDTO.StockInItemDTO itemDto : dto.getItems()) {
            Product product = productRepository.findById(itemDto.getProductId())
                    .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + itemDto.getProductId()));

            StockInItem item = new StockInItem();
            item.setProduct(product);
            item.setQuantity(itemDto.getQuantity());
            item.setUnitPrice(itemDto.getUnitPrice());
            item.setBatchNo(itemDto.getBatchNo());

            stockIn.addItem(item);

            totalQty.addAndGet(itemDto.getQuantity());
            totalAmount.set(totalAmount.get().add(
                    itemDto.getUnitPrice().multiply(new BigDecimal(itemDto.getQuantity()))
            ));
        }

        stockIn.setTotalQuantity(totalQty.get());
        stockIn.setTotalAmount(totalAmount.get());

        stockIn = stockInRepository.save(stockIn);

        for (StockInItem item : stockIn.getItems()) {
            inventoryService.increaseStock(
                    item.getProduct().getId(),
                    item.getQuantity(),
                    "STOCK_IN",
                    stockIn.getInNo(),
                    item.getUnitPrice(),
                    stockIn.getOperator(),
                    "入库操作"
            );
        }

        return convertToDTO(stockIn);
    }

    @Transactional(readOnly = true)
    public StockInDTO getStockInById(Long id) {
        StockIn stockIn = stockInRepository.findByIdWithItems(id)
                .orElseThrow(() -> new ResourceNotFoundException("入库记录不存在: " + id));
        return convertToDTO(stockIn);
    }

    @Transactional(readOnly = true)
    public StockInDTO getStockInByNo(String inNo) {
        StockIn stockIn = stockInRepository.findByInNo(inNo)
                .orElseThrow(() -> new ResourceNotFoundException("入库记录不存在: " + inNo));
        return convertToDTO(stockIn);
    }

    @Transactional(readOnly = true)
    public List<StockInDTO> getAllStockIn() {
        return stockInRepository.findAllWithItems().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<StockInDTO> getStockInByDateRange(LocalDateTime start, LocalDateTime end) {
        return stockInRepository.findByCreatedAtBetween(start, end).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private String generateInNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int seq = inNoCounter.incrementAndGet();
        return "IN" + dateStr + String.format("%04d", seq);
    }

    private StockInDTO convertToDTO(StockIn stockIn) {
        StockInDTO dto = new StockInDTO();
        dto.setId(stockIn.getId());
        dto.setInNo(stockIn.getInNo());
        dto.setInType(stockIn.getInType());
        dto.setSupplier(stockIn.getSupplier());
        dto.setWarehouse(stockIn.getWarehouse());
        dto.setOperator(stockIn.getOperator());
        dto.setTotalQuantity(stockIn.getTotalQuantity());
        dto.setTotalAmount(stockIn.getTotalAmount());
        dto.setRemark(stockIn.getRemark());

        if (stockIn.getItems() != null) {
            List<StockInDTO.StockInItemDTO> itemDTOs = stockIn.getItems().stream()
                    .map(item -> {
                        StockInDTO.StockInItemDTO itemDto = new StockInDTO.StockInItemDTO();
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
