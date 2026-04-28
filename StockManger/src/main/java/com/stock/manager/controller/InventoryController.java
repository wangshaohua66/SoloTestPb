package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.entity.Inventory;
import com.stock.manager.service.InventoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/inventory")
@Tag(name = "库存管理", description = "库存查询、库存预警等接口")
public class InventoryController {

    @Autowired
    private InventoryService inventoryService;

    @GetMapping
    @Operation(summary = "查询所有库存", description = "获取所有商品的库存信息列表")
    public ResponseEntity<ApiResponse<List<Inventory>>> getAllInventory() {
        List<Inventory> inventoryList = inventoryService.getAllInventory();
        return ResponseEntity.ok(ApiResponse.success(inventoryList));
    }

    @GetMapping("/product/{productId}")
    @Operation(summary = "根据商品ID查询库存", description = "根据商品ID获取该商品的库存信息")
    public ResponseEntity<ApiResponse<Inventory>> getInventoryByProductId(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long productId) {
        Inventory inventory = inventoryService.getInventoryByProductId(productId);
        return ResponseEntity.ok(ApiResponse.success(inventory));
    }

    @GetMapping("/low-stock")
    @Operation(summary = "查询库存下限商品", description = "获取所有库存数量低于或等于下限的商品列表")
    public ResponseEntity<ApiResponse<List<Inventory>>> getLowStockItems() {
        List<Inventory> inventoryList = inventoryService.getLowStockItems();
        return ResponseEntity.ok(ApiResponse.success(inventoryList));
    }

    @GetMapping("/high-stock")
    @Operation(summary = "查询库存上限商品", description = "获取所有库存数量高于或等于上限的商品列表")
    public ResponseEntity<ApiResponse<List<Inventory>>> getHighStockItems() {
        List<Inventory> inventoryList = inventoryService.getHighStockItems();
        return ResponseEntity.ok(ApiResponse.success(inventoryList));
    }
}
