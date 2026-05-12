package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.entity.StockTransaction;
import com.stock.manager.service.InventoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/transactions")
@Tag(name = "库存流水", description = "库存出入库流水记录查询接口")
public class StockTransactionController {

    @Autowired
    private InventoryService inventoryService;

    @GetMapping
    @Operation(summary = "查询所有流水", description = "获取所有库存流水记录列表")
    public ResponseEntity<ApiResponse<List<StockTransaction>>> getAllTransactions() {
        List<StockTransaction> transactions = inventoryService.getAllTransactions();
        return ResponseEntity.ok(ApiResponse.success(transactions));
    }

    @GetMapping("/product/{productId}")
    @Operation(summary = "按商品查询流水", description = "根据商品ID获取该商品的库存流水历史")
    public ResponseEntity<ApiResponse<List<StockTransaction>>> getTransactionHistory(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long productId) {
        List<StockTransaction> transactions = inventoryService.getTransactionHistory(productId);
        return ResponseEntity.ok(ApiResponse.success(transactions));
    }

    @GetMapping("/date-range")
    @Operation(summary = "按时间范围查询流水", description = "根据起始时间和结束时间查询库存流水记录")
    public ResponseEntity<ApiResponse<List<StockTransaction>>> getTransactionsByDateRange(
            @Parameter(description = "开始时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @Parameter(description = "结束时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<StockTransaction> transactions = inventoryService.getTransactionsByDateRange(start, end);
        return ResponseEntity.ok(ApiResponse.success(transactions));
    }
}
