package com.stock.manager.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import javax.validation.constraints.NotEmpty;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Schema(description = "盘点记录DTO")
public class CheckRecordDTO {

    @Schema(description = "盘点记录ID")
    private Long id;

    @Schema(description = "盘点单号", example = "CHECK20260426001")
    private String checkNo;

    @Schema(description = "盘点名称", example = "4月库存盘点")
    private String checkName;

    @Schema(description = "仓库", example = "主仓库")
    private String warehouse;

    @Schema(description = "操作人", example = "admin")
    private String operator;

    @Schema(description = "盘点明细列表", required = true)
    @NotEmpty(message = "盘点明细不能为空")
    private List<CheckItemDTO> items = new ArrayList<>();

    @Schema(description = "是否完成", example = "false")
    private Boolean completed;

    @Schema(description = "备注")
    private String remark;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCheckNo() {
        return checkNo;
    }

    public void setCheckNo(String checkNo) {
        this.checkNo = checkNo;
    }

    public String getCheckName() {
        return checkName;
    }

    public void setCheckName(String checkName) {
        this.checkName = checkName;
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

    public List<CheckItemDTO> getItems() {
        return items;
    }

    public void setItems(List<CheckItemDTO> items) {
        this.items = items;
    }

    public Boolean getCompleted() {
        return completed;
    }

    public void setCompleted(Boolean completed) {
        this.completed = completed;
    }

    public String getRemark() {
        return remark;
    }

    public void setRemark(String remark) {
        this.remark = remark;
    }

    @Schema(description = "盘点明细DTO")
    public static class CheckItemDTO {

        @Schema(description = "明细ID")
        private Long id;

        @Schema(description = "商品ID", required = true, example = "1")
        private Long productId;

        @Schema(description = "商品编码", example = "P001")
        private String productCode;

        @Schema(description = "商品名称", example = "测试商品")
        private String productName;

        @Schema(description = "账面数量", example = "50")
        private Integer bookQuantity;

        @Schema(description = "实际数量", example = "48")
        private Integer actualQuantity;

        @Schema(description = "差异数量", example = "-2")
        private Integer differenceQuantity;

        @Schema(description = "差异类型", example = "LOSS", allowableValues = {"OVERAGE", "LOSS", "NONE"})
        private String differenceType;

        @Schema(description = "单价", example = "199.99")
        private BigDecimal unitPrice;

        @Schema(description = "差异金额", example = "-399.98")
        private BigDecimal differenceAmount;

        @Schema(description = "是否已调整", example = "false")
        private Boolean adjusted;

        @Schema(description = "备注")
        private String remark;

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

        public String getProductCode() {
            return productCode;
        }

        public void setProductCode(String productCode) {
            this.productCode = productCode;
        }

        public String getProductName() {
            return productName;
        }

        public void setProductName(String productName) {
            this.productName = productName;
        }

        public Integer getBookQuantity() {
            return bookQuantity;
        }

        public void setBookQuantity(Integer bookQuantity) {
            this.bookQuantity = bookQuantity;
        }

        public Integer getActualQuantity() {
            return actualQuantity;
        }

        public void setActualQuantity(Integer actualQuantity) {
            this.actualQuantity = actualQuantity;
        }

        public Integer getDifferenceQuantity() {
            return differenceQuantity;
        }

        public void setDifferenceQuantity(Integer differenceQuantity) {
            this.differenceQuantity = differenceQuantity;
        }

        public String getDifferenceType() {
            return differenceType;
        }

        public void setDifferenceType(String differenceType) {
            this.differenceType = differenceType;
        }

        public BigDecimal getUnitPrice() {
            return unitPrice;
        }

        public void setUnitPrice(BigDecimal unitPrice) {
            this.unitPrice = unitPrice;
        }

        public BigDecimal getDifferenceAmount() {
            return differenceAmount;
        }

        public void setDifferenceAmount(BigDecimal differenceAmount) {
            this.differenceAmount = differenceAmount;
        }

        public Boolean getAdjusted() {
            return adjusted;
        }

        public void setAdjusted(Boolean adjusted) {
            this.adjusted = adjusted;
        }

        public String getRemark() {
            return remark;
        }

        public void setRemark(String remark) {
            this.remark = remark;
        }
    }
}
