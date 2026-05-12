package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.dto.CheckRecordDTO;
import com.stock.manager.dto.CheckReportDTO;
import com.stock.manager.service.CheckRecordService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/check-records")
@Tag(name = "库存盘点", description = "盘点记录创建、盘点差异处理、库存调整等接口")
public class CheckRecordController {

    @Autowired
    private CheckRecordService checkRecordService;

    @PostMapping
    @Operation(summary = "创建盘点记录", description = "创建新的库存盘点记录，初始化盘点明细")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> createCheckRecord(
            @Parameter(description = "盘点记录信息", required = true) 
            @Valid @RequestBody CheckRecordDTO dto) {
        CheckRecordDTO created = checkRecordService.createCheckRecord(dto);
        return ResponseEntity.ok(ApiResponse.success("盘点记录创建成功", created));
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询盘点记录", description = "根据盘点记录ID获取盘点详情")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> getCheckRecordById(
            @Parameter(description = "盘点记录ID", required = true) 
            @PathVariable Long id) {
        CheckRecordDTO checkRecord = checkRecordService.getCheckRecordById(id);
        return ResponseEntity.ok(ApiResponse.success(checkRecord));
    }

    @GetMapping("/no/{checkNo}")
    @Operation(summary = "根据单号查询盘点记录", description = "根据盘点单号获取盘点详情")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> getCheckRecordByNo(
            @Parameter(description = "盘点单号", required = true) 
            @PathVariable String checkNo) {
        CheckRecordDTO checkRecord = checkRecordService.getCheckRecordByNo(checkNo);
        return ResponseEntity.ok(ApiResponse.success(checkRecord));
    }

    @GetMapping
    @Operation(summary = "查询所有盘点记录", description = "获取所有盘点记录列表")
    public ResponseEntity<ApiResponse<List<CheckRecordDTO>>> getAllCheckRecords() {
        List<CheckRecordDTO> checkRecords = checkRecordService.getAllCheckRecords();
        return ResponseEntity.ok(ApiResponse.success(checkRecords));
    }

    @GetMapping("/pending")
    @Operation(summary = "查询待处理盘点", description = "获取所有未完成的盘点记录列表")
    public ResponseEntity<ApiResponse<List<CheckRecordDTO>>> getPendingCheckRecords() {
        List<CheckRecordDTO> checkRecords = checkRecordService.getPendingCheckRecords();
        return ResponseEntity.ok(ApiResponse.success(checkRecords));
    }

    @PutMapping("/{checkRecordId}/items/{itemId}")
    @Operation(summary = "更新盘点明细", description = "更新指定盘点明细的实际库存数量")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> updateCheckItem(
            @Parameter(description = "盘点记录ID", required = true) 
            @PathVariable Long checkRecordId,
            @Parameter(description = "盘点明细ID", required = true) 
            @PathVariable Long itemId,
            @Parameter(description = "实际库存数量", required = true) 
            @RequestParam Integer actualQuantity) {
        CheckRecordDTO updated = checkRecordService.updateCheckItem(checkRecordId, itemId, actualQuantity);
        return ResponseEntity.ok(ApiResponse.success("盘点明细更新成功", updated));
    }

    @PutMapping("/{id}/complete")
    @Operation(summary = "完成盘点", description = "标记盘点记录为已完成状态")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> completeCheck(
            @Parameter(description = "盘点记录ID", required = true) 
            @PathVariable Long id) {
        CheckRecordDTO completed = checkRecordService.completeCheck(id);
        return ResponseEntity.ok(ApiResponse.success("盘点完成", completed));
    }

    @PutMapping("/{checkRecordId}/items/{itemId}/adjust")
    @Operation(summary = "调整库存", description = "根据盘点差异调整实际库存数量")
    public ResponseEntity<ApiResponse<CheckRecordDTO>> adjustInventory(
            @Parameter(description = "盘点记录ID", required = true) 
            @PathVariable Long checkRecordId,
            @Parameter(description = "盘点明细ID", required = true) 
            @PathVariable Long itemId,
            @Parameter(description = "调整操作人") 
            @RequestParam(required = false) String adjustedBy) {
        CheckRecordDTO updated = checkRecordService.adjustInventory(
                checkRecordId, itemId, adjustedBy != null ? adjustedBy : "system");
        return ResponseEntity.ok(ApiResponse.success("库存调整成功", updated));
    }

    @GetMapping("/{id}/report")
    @Operation(summary = "获取盘点报告", description = "获取盘点记录的盘盈盘亏统计报告")
    public ResponseEntity<ApiResponse<CheckReportDTO>> getCheckReport(
            @Parameter(description = "盘点记录ID", required = true) 
            @PathVariable Long id) {
        CheckReportDTO report = checkRecordService.getCheckReport(id);
        return ResponseEntity.ok(ApiResponse.success("盘点报告获取成功", report));
    }
}
