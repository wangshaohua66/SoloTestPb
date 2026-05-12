package com.stock.manager.service;

import com.stock.manager.dto.CheckRecordDTO;
import com.stock.manager.dto.CheckReportDTO;
import com.stock.manager.entity.CheckItem;
import com.stock.manager.entity.CheckRecord;
import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.CheckItemRepository;
import com.stock.manager.repository.CheckRecordRepository;
import com.stock.manager.repository.InventoryRepository;
import com.stock.manager.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

@Service
public class CheckRecordService {

    @Autowired
    private CheckRecordRepository checkRecordRepository;

    @Autowired
    private CheckItemRepository checkItemRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private InventoryService inventoryService;

    private final AtomicInteger checkNoCounter = new AtomicInteger(0);

    @Transactional
    public CheckRecordDTO createCheckRecord(CheckRecordDTO dto) {
        String checkNo = generateCheckNo();

        CheckRecord checkRecord = new CheckRecord();
        checkRecord.setCheckNo(checkNo);
        checkRecord.setCheckName(dto.getCheckName());
        checkRecord.setWarehouse(dto.getWarehouse());
        checkRecord.setOperator(dto.getOperator());
        checkRecord.setCompleted(false);
        checkRecord.setRemark(dto.getRemark());

        for (CheckRecordDTO.CheckItemDTO itemDto : dto.getItems()) {
            Product product = productRepository.findById(itemDto.getProductId())
                    .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + itemDto.getProductId()));

            Inventory inventory = inventoryRepository.findByProductId(product.getId())
                    .orElseThrow(() -> new ResourceNotFoundException("库存不存在: 商品ID=" + product.getId()));

            CheckItem item = new CheckItem();
            item.setProduct(product);
            item.setBookQuantity(inventory.getQuantity());
            item.setActualQuantity(itemDto.getActualQuantity() != null ? itemDto.getActualQuantity() : inventory.getQuantity());
            item.setUnitPrice(product.getUnitPrice());

            checkRecord.addItem(item);
        }

        checkRecord = checkRecordRepository.save(checkRecord);

        return convertToDTO(checkRecord);
    }

    @Transactional(readOnly = true)
    public CheckRecordDTO getCheckRecordById(Long id) {
        CheckRecord checkRecord = checkRecordRepository.findByIdWithItems(id)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + id));
        return convertToDTO(checkRecord);
    }

    @Transactional(readOnly = true)
    public CheckRecordDTO getCheckRecordByNo(String checkNo) {
        CheckRecord checkRecord = checkRecordRepository.findByCheckNo(checkNo)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + checkNo));
        return convertToDTO(checkRecord);
    }

    @Transactional(readOnly = true)
    public List<CheckRecordDTO> getAllCheckRecords() {
        return checkRecordRepository.findAllWithItems().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<CheckRecordDTO> getPendingCheckRecords() {
        return checkRecordRepository.findByCompleted(false).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional
    public CheckRecordDTO updateCheckItem(Long checkRecordId, Long itemId, Integer actualQuantity) {
        CheckRecord checkRecord = checkRecordRepository.findByIdWithItems(checkRecordId)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + checkRecordId));

        if (checkRecord.getCompleted()) {
            throw new IllegalStateException("盘点已完成，无法修改");
        }

        CheckItem item = checkItemRepository.findById(itemId)
                .orElseThrow(() -> new ResourceNotFoundException("盘点明细不存在: " + itemId));

        item.setActualQuantity(actualQuantity);
        checkItemRepository.save(item);

        return convertToDTO(checkRecordRepository.findByIdWithItems(checkRecordId).get());
    }

    @Transactional
    public CheckRecordDTO completeCheck(Long id) {
        CheckRecord checkRecord = checkRecordRepository.findByIdWithItems(id)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + id));

        if (checkRecord.getCompleted()) {
            throw new IllegalStateException("盘点已完成");
        }

        checkRecord.setCompleted(true);
        checkRecord.setCompletedAt(LocalDateTime.now());
        checkRecord = checkRecordRepository.save(checkRecord);

        return convertToDTO(checkRecord);
    }

    @Transactional
    public CheckRecordDTO adjustInventory(Long checkRecordId, Long itemId, String adjustedBy) {
        CheckRecord checkRecord = checkRecordRepository.findByIdWithItems(checkRecordId)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + checkRecordId));

        CheckItem item = checkItemRepository.findById(itemId)
                .orElseThrow(() -> new ResourceNotFoundException("盘点明细不存在: " + itemId));

        if (item.getAdjusted()) {
            throw new IllegalStateException("该商品已调整过库存");
        }

        int diff = item.getDifferenceQuantity();
        if (diff == 0) {
            throw new IllegalStateException("库存无差异，无需调整");
        }

        Product product = item.getProduct();

        if (diff > 0) {
            inventoryService.increaseStock(
                    product.getId(),
                    diff,
                    "CHECK_ADJUST_OVER",
                    checkRecord.getCheckNo(),
                    product.getUnitPrice(),
                    adjustedBy,
                    "盘点盘盈调整"
            );
        } else {
            inventoryService.decreaseStock(
                    product.getId(),
                    -diff,
                    "CHECK_ADJUST_SHORT",
                    checkRecord.getCheckNo(),
                    product.getUnitPrice(),
                    adjustedBy,
                    "盘点盘亏调整"
            );
        }

        item.setAdjusted(true);
        item.setAdjustedAt(LocalDateTime.now());
        item.setAdjustedBy(adjustedBy);
        checkItemRepository.save(item);

        return convertToDTO(checkRecordRepository.findByIdWithItems(checkRecordId).get());
    }

    private String generateCheckNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        int seq = checkNoCounter.incrementAndGet();
        return "CK" + dateStr + String.format("%04d", seq);
    }

    private CheckRecordDTO convertToDTO(CheckRecord checkRecord) {
        CheckRecordDTO dto = new CheckRecordDTO();
        dto.setId(checkRecord.getId());
        dto.setCheckNo(checkRecord.getCheckNo());
        dto.setCheckName(checkRecord.getCheckName());
        dto.setWarehouse(checkRecord.getWarehouse());
        dto.setOperator(checkRecord.getOperator());
        dto.setCompleted(checkRecord.getCompleted());
        dto.setRemark(checkRecord.getRemark());

        if (checkRecord.getItems() != null) {
            List<CheckRecordDTO.CheckItemDTO> itemDTOs = checkRecord.getItems().stream()
                    .map(item -> {
                        CheckRecordDTO.CheckItemDTO itemDto = new CheckRecordDTO.CheckItemDTO();
                        itemDto.setId(item.getId());
                        itemDto.setProductId(item.getProduct().getId());
                        itemDto.setProductCode(item.getProduct().getProductCode());
                        itemDto.setProductName(item.getProduct().getProductName());
                        itemDto.setBookQuantity(item.getBookQuantity());
                        itemDto.setActualQuantity(item.getActualQuantity());
                        itemDto.setDifferenceQuantity(item.getDifferenceQuantity());
                        itemDto.setDifferenceType(item.getDifferenceType());
                        itemDto.setUnitPrice(item.getUnitPrice());
                        itemDto.setDifferenceAmount(item.getDifferenceAmount());
                        itemDto.setAdjusted(item.getAdjusted());
                        itemDto.setRemark(item.getRemark());
                        return itemDto;
                    })
                    .collect(Collectors.toList());
            dto.setItems(itemDTOs);
        }

        return dto;
    }

    @Transactional(readOnly = true)
    public CheckReportDTO getCheckReport(Long id) {
        CheckRecord checkRecord = checkRecordRepository.findByIdWithItems(id)
                .orElseThrow(() -> new ResourceNotFoundException("盘点记录不存在: " + id));

        CheckReportDTO report = new CheckReportDTO();
        report.setCheckRecordId(checkRecord.getId());
        report.setCheckNo(checkRecord.getCheckNo());
        report.setCheckName(checkRecord.getCheckName());
        report.setWarehouse(checkRecord.getWarehouse());
        report.setCompleted(checkRecord.getCompleted());

        CheckReportDTO.CheckStatistics statistics = new CheckReportDTO.CheckStatistics();
        int totalItems = 0;
        int overageCount = 0;
        int shortageCount = 0;
        int normalCount = 0;
        int overageTotalQuantity = 0;
        int shortageTotalQuantity = 0;
        BigDecimal overageTotalAmount = BigDecimal.ZERO;
        BigDecimal shortageTotalAmount = BigDecimal.ZERO;

        if (checkRecord.getItems() != null) {
            totalItems = checkRecord.getItems().size();

            for (CheckItem item : checkRecord.getItems()) {
                CheckReportDTO.CheckItemDetail detail = convertToCheckItemDetail(item);
                
                if ("OVER".equals(item.getDifferenceType())) {
                    overageCount++;
                    if (item.getDifferenceQuantity() != null) {
                        overageTotalQuantity += item.getDifferenceQuantity();
                    }
                    if (item.getDifferenceAmount() != null) {
                        overageTotalAmount = overageTotalAmount.add(item.getDifferenceAmount());
                    }
                    report.getOverageItems().add(detail);
                } else if ("SHORT".equals(item.getDifferenceType())) {
                    shortageCount++;
                    if (item.getDifferenceQuantity() != null) {
                        shortageTotalQuantity += Math.abs(item.getDifferenceQuantity());
                    }
                    if (item.getDifferenceAmount() != null) {
                        shortageTotalAmount = shortageTotalAmount.add(item.getDifferenceAmount().abs());
                    }
                    report.getShortageItems().add(detail);
                } else {
                    normalCount++;
                    report.getNormalItems().add(detail);
                }
            }
        }

        statistics.setTotalItems(totalItems);
        statistics.setOverageCount(overageCount);
        statistics.setShortageCount(shortageCount);
        statistics.setNormalCount(normalCount);
        statistics.setOverageTotalQuantity(overageTotalQuantity);
        statistics.setShortageTotalQuantity(shortageTotalQuantity);
        statistics.setOverageTotalAmount(overageTotalAmount);
        statistics.setShortageTotalAmount(shortageTotalAmount);
        statistics.setNetAmount(overageTotalAmount.subtract(shortageTotalAmount));

        report.setStatistics(statistics);

        return report;
    }

    private CheckReportDTO.CheckItemDetail convertToCheckItemDetail(CheckItem item) {
        CheckReportDTO.CheckItemDetail detail = new CheckReportDTO.CheckItemDetail();
        detail.setId(item.getId());
        detail.setProductId(item.getProduct().getId());
        detail.setProductCode(item.getProduct().getProductCode());
        detail.setProductName(item.getProduct().getProductName());
        detail.setBookQuantity(item.getBookQuantity());
        detail.setActualQuantity(item.getActualQuantity());
        detail.setDifferenceQuantity(item.getDifferenceQuantity());
        detail.setDifferenceType(item.getDifferenceType());
        detail.setUnitPrice(item.getUnitPrice());
        detail.setDifferenceAmount(item.getDifferenceAmount());
        detail.setAdjusted(item.getAdjusted());
        return detail;
    }
}
