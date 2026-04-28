package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.entity.StockWarning;
import com.stock.manager.service.StockWarningService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/warnings")
@Tag(name = "预警通知", description = "库存预警查询、预警处理等接口")
public class StockWarningController {

    @Autowired
    private StockWarningService stockWarningService;

    @GetMapping
    @Operation(summary = "查询所有预警", description = "获取所有库存预警记录列表")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getAllWarnings() {
        List<StockWarning> warnings = stockWarningService.getAllWarnings();
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @GetMapping("/unresolved")
    @Operation(summary = "查询未处理预警", description = "获取所有未处理的库存预警记录列表")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getUnresolvedWarnings() {
        List<StockWarning> warnings = stockWarningService.getUnresolvedWarnings();
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @GetMapping("/resolved")
    @Operation(summary = "查询已处理预警", description = "获取所有已处理的库存预警记录列表")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getResolvedWarnings() {
        List<StockWarning> warnings = stockWarningService.getResolvedWarnings();
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @GetMapping("/low-stock")
    @Operation(summary = "查询库存下限预警", description = "获取所有库存下限预警记录列表")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getLowStockWarnings() {
        List<StockWarning> warnings = stockWarningService.getLowStockWarnings();
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @GetMapping("/high-stock")
    @Operation(summary = "查询库存上限预警", description = "获取所有库存上限预警记录列表")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getHighStockWarnings() {
        List<StockWarning> warnings = stockWarningService.getHighStockWarnings();
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @GetMapping("/product/{productId}")
    @Operation(summary = "按商品查询预警", description = "根据商品ID获取该商品的所有预警记录")
    public ResponseEntity<ApiResponse<List<StockWarning>>> getWarningsByProductId(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long productId) {
        List<StockWarning> warnings = stockWarningService.getWarningsByProductId(productId);
        return ResponseEntity.ok(ApiResponse.success(warnings));
    }

    @PutMapping("/{id}/resolve")
    @Operation(summary = "处理预警", description = "将指定预警标记为已处理")
    public ResponseEntity<ApiResponse<StockWarning>> resolveWarning(
            @Parameter(description = "预警ID", required = true) 
            @PathVariable Long id,
            @Parameter(description = "处理人") 
            @RequestParam(required = false) String resolvedBy) {
        StockWarning warning = stockWarningService.resolveWarning(id, resolvedBy != null ? resolvedBy : "system");
        return ResponseEntity.ok(ApiResponse.success("预警已处理", warning));
    }

    @PutMapping("/resolve-all")
    @Operation(summary = "处理所有预警", description = "将所有未处理预警标记为已处理")
    public ResponseEntity<ApiResponse<Void>> resolveAllWarnings(
            @Parameter(description = "处理人") 
            @RequestParam(required = false) String resolvedBy) {
        stockWarningService.resolveAllWarnings(resolvedBy != null ? resolvedBy : "system");
        return ResponseEntity.ok(ApiResponse.success("所有预警已处理", null));
    }
}
