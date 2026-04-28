package com.stock.manager.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Schema(description = "盘点报告DTO")
public class CheckReportDTO {

    @Schema(description = "盘点记录ID")
    private Long checkRecordId;

    @Schema(description = "盘点单号")
    private String checkNo;

    @Schema(description = "盘点名称")
    private String checkName;

    @Schema(description = "仓库")
    private String warehouse;

    @Schema(description = "是否完成")
    private Boolean completed;

    @Schema(description = "统计信息")
    private CheckStatistics statistics;

    @Schema(description = "盘盈明细列表")
    private List<CheckItemDetail> overageItems = new ArrayList<>();

    @Schema(description = "盘亏明细列表")
    private List<CheckItemDetail> shortageItems = new ArrayList<>();

    @Schema(description = "无差异明细列表")
    private List<CheckItemDetail> normalItems = new ArrayList<>();

    public Long getCheckRecordId() {
        return checkRecordId;
    }

    public void setCheckRecordId(Long checkRecordId) {
        this.checkRecordId = checkRecordId;
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

    public Boolean getCompleted() {
        return completed;
    }

    public void setCompleted(Boolean completed) {
        this.completed = completed;
    }

    public CheckStatistics getStatistics() {
        return statistics;
    }

    public void setStatistics(CheckStatistics statistics) {
        this.statistics = statistics;
    }

    public List<CheckItemDetail> getOverageItems() {
        return overageItems;
    }

    public void setOverageItems(List<CheckItemDetail> overageItems) {
        this.overageItems = overageItems;
    }

    public List<CheckItemDetail> getShortageItems() {
        return shortageItems;
    }

    public void setShortageItems(List<CheckItemDetail> shortageItems) {
        this.shortageItems = shortageItems;
    }

    public List<CheckItemDetail> getNormalItems() {
        return normalItems;
    }

    public void setNormalItems(List<CheckItemDetail> normalItems) {
        this.normalItems = normalItems;
    }

    @Schema(description = "盘点统计信息")
    public static class CheckStatistics {
        @Schema(description = "总商品数")
        private Integer totalItems;
        
        @Schema(description = "盘盈商品数")
        private Integer overageCount;
        
        @Schema(description = "盘亏商品数")
        private Integer shortageCount;
        
        @Schema(description = "无差异商品数")
        private Integer normalCount;
        
        @Schema(description = "盘盈总数量")
        private Integer overageTotalQuantity;
        
        @Schema(description = "盘亏总数量")
        private Integer shortageTotalQuantity;
        
        @Schema(description = "盘盈总金额")
        private BigDecimal overageTotalAmount;
        
        @Schema(description = "盘亏总金额")
        private BigDecimal shortageTotalAmount;
        
        @Schema(description = "盈亏相抵金额")
        private BigDecimal netAmount;

        public Integer getTotalItems() {
            return totalItems;
        }

        public void setTotalItems(Integer totalItems) {
            this.totalItems = totalItems;
        }

        public Integer getOverageCount() {
            return overageCount;
        }

        public void setOverageCount(Integer overageCount) {
            this.overageCount = overageCount;
        }

        public Integer getShortageCount() {
            return shortageCount;
        }

        public void setShortageCount(Integer shortageCount) {
            this.shortageCount = shortageCount;
        }

        public Integer getNormalCount() {
            return normalCount;
        }

        public void setNormalCount(Integer normalCount) {
            this.normalCount = normalCount;
        }

        public Integer getOverageTotalQuantity() {
            return overageTotalQuantity;
        }

        public void setOverageTotalQuantity(Integer overageTotalQuantity) {
            this.overageTotalQuantity = overageTotalQuantity;
        }

        public Integer getShortageTotalQuantity() {
            return shortageTotalQuantity;
        }

        public void setShortageTotalQuantity(Integer shortageTotalQuantity) {
            this.shortageTotalQuantity = shortageTotalQuantity;
        }

        public BigDecimal getOverageTotalAmount() {
            return overageTotalAmount;
        }

        public void setOverageTotalAmount(BigDecimal overageTotalAmount) {
            this.overageTotalAmount = overageTotalAmount;
        }

        public BigDecimal getShortageTotalAmount() {
            return shortageTotalAmount;
        }

        public void setShortageTotalAmount(BigDecimal shortageTotalAmount) {
            this.shortageTotalAmount = shortageTotalAmount;
        }

        public BigDecimal getNetAmount() {
            return netAmount;
        }

        public void setNetAmount(BigDecimal netAmount) {
            this.netAmount = netAmount;
        }
    }

    @Schema(description = "盘点明细")
    public static class CheckItemDetail {
        @Schema(description = "明细ID")
        private Long id;
        
        @Schema(description = "商品ID")
        private Long productId;
        
        @Schema(description = "商品编码")
        private String productCode;
        
        @Schema(description = "商品名称")
        private String productName;
        
        @Schema(description = "账面数量")
        private Integer bookQuantity;
        
        @Schema(description = "实际数量")
        private Integer actualQuantity;
        
        @Schema(description = "差异数量")
        private Integer differenceQuantity;
        
        @Schema(description = "差异类型")
        private String differenceType;
        
        @Schema(description = "单价")
        private BigDecimal unitPrice;
        
        @Schema(description = "差异金额")
        private BigDecimal differenceAmount;
        
        @Schema(description = "是否已调整")
        private Boolean adjusted;

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
    }
}
