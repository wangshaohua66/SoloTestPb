package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.dto.StockOutDTO;
import com.stock.manager.service.StockOutService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/stock-out")
@Tag(name = "出库管理", description = "商品出库操作、出库记录查询等接口")
public class StockOutController {

    @Autowired
    private StockOutService stockOutService;

    @PostMapping
    @Operation(summary = "商品出库", description = "创建出库单并更新库存，支持批量出库")
    public ResponseEntity<ApiResponse<StockOutDTO>> createStockOut(
            @Parameter(description = "出库单信息", required = true) 
            @Valid @RequestBody StockOutDTO dto) {
        StockOutDTO created = stockOutService.createStockOut(dto);
        return ResponseEntity.ok(ApiResponse.success("出库操作成功", created));
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询出库单", description = "根据出库单ID获取出库详情")
    public ResponseEntity<ApiResponse<StockOutDTO>> getStockOutById(
            @Parameter(description = "出库单ID", required = true) 
            @PathVariable Long id) {
        StockOutDTO stockOut = stockOutService.getStockOutById(id);
        return ResponseEntity.ok(ApiResponse.success(stockOut));
    }

    @GetMapping("/no/{outNo}")
    @Operation(summary = "根据单号查询出库单", description = "根据出库单号获取出库详情")
    public ResponseEntity<ApiResponse<StockOutDTO>> getStockOutByNo(
            @Parameter(description = "出库单号", required = true) 
            @PathVariable String outNo) {
        StockOutDTO stockOut = stockOutService.getStockOutByNo(outNo);
        return ResponseEntity.ok(ApiResponse.success(stockOut));
    }

    @GetMapping
    @Operation(summary = "查询所有出库记录", description = "获取所有出库单列表")
    public ResponseEntity<ApiResponse<List<StockOutDTO>>> getAllStockOut() {
        List<StockOutDTO> stockOutList = stockOutService.getAllStockOut();
        return ResponseEntity.ok(ApiResponse.success(stockOutList));
    }

    @GetMapping("/date-range")
    @Operation(summary = "按时间范围查询出库记录", description = "根据起始时间和结束时间查询出库记录")
    public ResponseEntity<ApiResponse<List<StockOutDTO>>> getStockOutByDateRange(
            @Parameter(description = "开始时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @Parameter(description = "结束时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<StockOutDTO> stockOutList = stockOutService.getStockOutByDateRange(start, end);
        return ResponseEntity.ok(ApiResponse.success(stockOutList));
    }
}
