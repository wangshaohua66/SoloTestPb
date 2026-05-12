package com.stock.manager.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Schema(description = "出库单DTO")
public class StockOutDTO {

    @Schema(description = "出库单ID")
    private Long id;

    @Schema(description = "出库单号", example = "OUT202604260001")
    private String outNo;

    @Schema(description = "出库类型", required = true, example = "SALE", allowableValues = {"SALE", "RETURN", "TRANSFER_OUT", "OTHER"})
    @NotBlank(message = "出库类型不能为空")
    private String outType;

    @Schema(description = "客户", example = "客户A")
    private String customer;

    @Schema(description = "仓库", example = "主仓库")
    private String warehouse;

    @Schema(description = "操作人", example = "admin")
    private String operator;

    @Schema(description = "出库明细列表", required = true)
    @NotEmpty(message = "出库明细不能为空")
    private List<StockOutItemDTO> items = new ArrayList<>();

    @Schema(description = "总数量", example = "50")
    private Integer totalQuantity;

    @Schema(description = "总金额", example = "15000.00")
    private BigDecimal totalAmount;

    @Schema(description = "备注")
    private String remark;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getOutNo() {
        return outNo;
    }

    public void setOutNo(String outNo) {
        this.outNo = outNo;
    }

    public String getOutType() {
        return outType;
    }

    public void setOutType(String outType) {
        this.outType = outType;
    }

    public String getCustomer() {
        return customer;
    }

    public void setCustomer(String customer) {
        this.customer = customer;
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

    public List<StockOutItemDTO> getItems() {
        return items;
    }

    public void setItems(List<StockOutItemDTO> items) {
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

    @Schema(description = "出库明细DTO")
    public static class StockOutItemDTO {

        @Schema(description = "明细ID")
        private Long id;

        @Schema(description = "商品ID", required = true, example = "1")
        @NotNull(message = "商品ID不能为空")
        private Long productId;

        @Schema(description = "出库数量", required = true, example = "20")
        @NotNull(message = "出库数量不能为空")
        private Integer quantity;

        @Schema(description = "单价", required = true, example = "250.00")
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
