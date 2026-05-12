package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.entity.WarningConfig;
import com.stock.manager.service.WarningConfigService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/warning-config")
@Tag(name = "预警设置", description = "预警开关配置、预警参数设置等接口")
public class WarningConfigController {

    @Autowired
    private WarningConfigService warningConfigService;

    @GetMapping
    @Operation(summary = "查询所有配置", description = "获取所有预警配置项列表")
    public ResponseEntity<ApiResponse<List<WarningConfig>>> getAllConfigs() {
        List<WarningConfig> configs = warningConfigService.getAllConfigs();
        return ResponseEntity.ok(ApiResponse.success(configs));
    }

    @GetMapping("/switches")
    @Operation(summary = "查询预警开关状态", description = "获取所有预警功能开关的当前状态")
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> getWarningSwitches() {
        Map<String, Boolean> switches = warningConfigService.getAllWarningSwitches();
        return ResponseEntity.ok(ApiResponse.success(switches));
    }

    @GetMapping("/{key}")
    @Operation(summary = "根据Key查询配置", description = "根据配置Key获取配置项详情")
    public ResponseEntity<ApiResponse<WarningConfig>> getConfigByKey(
            @Parameter(description = "配置Key", required = true) 
            @PathVariable String key) {
        return warningConfigService.getConfigByKey(key)
                .map(config -> ResponseEntity.ok(ApiResponse.success(config)))
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{key}")
    @Operation(summary = "更新配置", description = "根据配置Key更新配置值")
    public ResponseEntity<ApiResponse<WarningConfig>> updateConfig(
            @Parameter(description = "配置Key", required = true) 
            @PathVariable String key,
            @Parameter(description = "配置值JSON", required = true) 
            @RequestBody Map<String, String> body,
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        String value = body.get("value");
        if (value == null) {
            return ResponseEntity.badRequest().body(ApiResponse.error("value不能为空"));
        }
        WarningConfig config = warningConfigService.updateConfig(key, value, operator);
        return ResponseEntity.ok(ApiResponse.success("配置更新成功", config));
    }

    @PutMapping("/{key}/toggle")
    @Operation(summary = "切换开关状态", description = "切换布尔类型配置的开关状态")
    public ResponseEntity<ApiResponse<WarningConfig>> toggleConfig(
            @Parameter(description = "配置Key", required = true) 
            @PathVariable String key,
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        try {
            WarningConfig config = warningConfigService.toggleConfig(key, operator);
            return ResponseEntity.ok(ApiResponse.success("配置切换成功", config));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(ApiResponse.error(e.getMessage()));
        }
    }

    @PutMapping("/low-stock/enable")
    @Operation(summary = "开启库存下限预警", description = "启用库存下限预警功能")
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> enableLowStockWarning(
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        warningConfigService.updateConfig(
                WarningConfigService.LOW_STOCK_WARNING_ENABLED, "true", operator);
        return ResponseEntity.ok(ApiResponse.success("库存下限预警已开启", warningConfigService.getAllWarningSwitches()));
    }

    @PutMapping("/low-stock/disable")
    @Operation(summary = "关闭库存下限预警", description = "停用库存下限预警功能")
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> disableLowStockWarning(
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        warningConfigService.updateConfig(
                WarningConfigService.LOW_STOCK_WARNING_ENABLED, "false", operator);
        return ResponseEntity.ok(ApiResponse.success("库存下限预警已关闭", warningConfigService.getAllWarningSwitches()));
    }

    @PutMapping("/high-stock/enable")
    @Operation(summary = "开启库存上限预警", description = "启用库存上限预警功能")
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> enableHighStockWarning(
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        warningConfigService.updateConfig(
                WarningConfigService.HIGH_STOCK_WARNING_ENABLED, "true", operator);
        return ResponseEntity.ok(ApiResponse.success("库存上限预警已开启", warningConfigService.getAllWarningSwitches()));
    }

    @PutMapping("/high-stock/disable")
    @Operation(summary = "关闭库存上限预警", description = "停用库存上限预警功能")
    public ResponseEntity<ApiResponse<Map<String, Boolean>>> disableHighStockWarning(
            @Parameter(description = "操作人") 
            @RequestParam(required = false) String operator) {
        warningConfigService.updateConfig(
                WarningConfigService.HIGH_STOCK_WARNING_ENABLED, "false", operator);
        return ResponseEntity.ok(ApiResponse.success("库存上限预警已关闭", warningConfigService.getAllWarningSwitches()));
    }
}
