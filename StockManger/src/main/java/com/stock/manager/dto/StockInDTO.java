package com.stock.manager.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Schema(description = "入库单DTO")
public class StockInDTO {

    @Schema(description = "入库单ID")
    private Long id;

    @Schema(description = "入库单号", example = "IN202604260001")
    private String inNo;

    @Schema(description = "入库类型", required = true, example = "PURCHASE", allowableValues = {"PURCHASE", "RETURN", "TRANSFER_IN", "OTHER"})
    @NotBlank(message = "入库类型不能为空")
    private String inType;

    @Schema(description = "供应商", example = "供应商A")
    private String supplier;

    @Schema(description = "仓库", example = "主仓库")
    private String warehouse;

    @Schema(description = "操作人", example = "admin")
    private String operator;

    @Schema(description = "入库明细列表", required = true)
    @NotEmpty(message = "入库明细不能为空")
    private List<StockInItemDTO> items = new ArrayList<>();

    @Schema(description = "总数量", example = "100")
    private Integer totalQuantity;

    @Schema(description = "总金额", example = "19999.00")
    private BigDecimal totalAmount;

    @Schema(description = "备注")
    private String remark;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getInNo() {
        return inNo;
    }

    public void setInNo(String inNo) {
        this.inNo = inNo;
    }

    public String getInType() {
        return inType;
    }

    public void setInType(String inType) {
        this.inType = inType;
    }

    public String getSupplier() {
        return supplier;
    }

    public void setSupplier(String supplier) {
        this.supplier = supplier;
    }

    public String getWarehouse() {
        return warehouse;
    }

    public void setWarehouse(String warehouse) {
        this.warehouse = warehouse;
    }

    public String getOperator() {
        return operator;
    }

    public void setOperator(String operator) {
        this.operator = operator;
    }

    public List<StockInItemDTO> getItems() {
        return items;
    }

    public void setItems(List<StockInItemDTO> items) {
        this.items = items;
    }

    public Integer getTotalQuantity() {
        return totalQuantity;
    }

    public void setTotalQuantity(Integer totalQuantity) {
        this.totalQuantity = totalQuantity;
    }

    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    @Schema(description = "入库明细DTO")
    public static class StockInItemDTO {

        @Schema(description = "明细ID")
        private Long id;

        @Schema(description = "商品ID", required = true, example = "1")
        @NotNull(message = "商品ID不能为空")
        private Long productId;

        @Schema(description = "入库数量", required = true, example = "50")
        @NotNull(message = "入库数量不能为空")
        private Integer quantity;

        @Schema(description = "单价", required = true, example = "180.00")
        @NotNull(message = "单价不能为空")
        private BigDecimal unitPrice;

        @Schema(description = "批次号", example = "B20260426001")
        private String batchNo;

        public Long getId() {
            return id;
        }

        public void setId(Long id) {
            this.id = id;
        }

        public Long getProductId() {
            return productId;
        }

        public void setProductId(Long productId) {
            this.productId = productId;
        }

        public Integer getQuantity() {
            return quantity;
        }

        public void setQuantity(Integer quantity) {
            this.quantity = quantity;
        }

        public BigDecimal getUnitPrice() {
            return unitPrice;
        }

        public void setUnitPrice(BigDecimal unitPrice) {
            this.unitPrice = unitPrice;
        }

        public String getBatchNo() {
            return batchNo;
        }

        public void setBatchNo(String batchNo) {
            this.batchNo = batchNo;
        }
    }
}
