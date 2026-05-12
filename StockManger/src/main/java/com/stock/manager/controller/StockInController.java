package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.dto.StockInDTO;
import com.stock.manager.service.StockInService;
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
@RequestMapping("/api/stock-in")
@Tag(name = "入库管理", description = "商品入库操作、入库记录查询等接口")
public class StockInController {

    @Autowired
    private StockInService stockInService;

    @PostMapping
    @Operation(summary = "商品入库", description = "创建入库单并更新库存，支持批量入库")
    public ResponseEntity<ApiResponse<StockInDTO>> createStockIn(
            @Parameter(description = "入库单信息", required = true) 
            @Valid @RequestBody StockInDTO dto) {
        StockInDTO created = stockInService.createStockIn(dto);
        return ResponseEntity.ok(ApiResponse.success("入库操作成功", created));
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询入库单", description = "根据入库单ID获取入库详情")
    public ResponseEntity<ApiResponse<StockInDTO>> getStockInById(
            @Parameter(description = "入库单ID", required = true) 
            @PathVariable Long id) {
        StockInDTO stockIn = stockInService.getStockInById(id);
        return ResponseEntity.ok(ApiResponse.success(stockIn));
    }

    @GetMapping("/no/{inNo}")
    @Operation(summary = "根据单号查询入库单", description = "根据入库单号获取入库详情")
    public ResponseEntity<ApiResponse<StockInDTO>> getStockInByNo(
            @Parameter(description = "入库单号", required = true) 
            @PathVariable String inNo) {
        StockInDTO stockIn = stockInService.getStockInByNo(inNo);
        return ResponseEntity.ok(ApiResponse.success(stockIn));
    }

    @GetMapping
    @Operation(summary = "查询所有入库记录", description = "获取所有入库单列表")
    public ResponseEntity<ApiResponse<List<StockInDTO>>> getAllStockIn() {
        List<StockInDTO> stockInList = stockInService.getAllStockIn();
        return ResponseEntity.ok(ApiResponse.success(stockInList));
    }

    @GetMapping("/date-range")
    @Operation(summary = "按时间范围查询入库记录", description = "根据起始时间和结束时间查询入库记录")
    public ResponseEntity<ApiResponse<List<StockInDTO>>> getStockInByDateRange(
            @Parameter(description = "开始时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @Parameter(description = "结束时间 (格式: yyyy-MM-dd'T'HH:mm:ss)", required = true) 
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<StockInDTO> stockInList = stockInService.getStockInByDateRange(start, end);
        return ResponseEntity.ok(ApiResponse.success(stockInList));
    }
}
