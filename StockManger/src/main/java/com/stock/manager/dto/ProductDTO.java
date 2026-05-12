package com.stock.manager.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import javax.validation.constraints.PositiveOrZero;
import java.math.BigDecimal;

@Schema(description = "商品信息DTO")
public class ProductDTO {

    @Schema(description = "商品ID")
    private Long id;

    @Schema(description = "商品编码", required = true, example = "P001")
    @NotBlank(message = "商品编码不能为空")
    private String productCode;

    @Schema(description = "商品名称", required = true, example = "测试商品")
    @NotBlank(message = "商品名称不能为空")
    private String productName;

    @Schema(description = "商品分类", example = "电子产品")
    private String category;

    @Schema(description = "计量单位", example = "个")
    private String unit;

    @Schema(description = "单价", required = true, example = "199.99")
    @NotNull(message = "单价不能为空")
    @Positive(message = "单价必须大于0")
    private BigDecimal unitPrice;

    @Schema(description = "库存下限", example = "10")
    @PositiveOrZero(message = "库存下限不能为负数")
    private Integer minStock;

    @Schema(description = "库存上限", example = "100")
    @PositiveOrZero(message = "库存上限不能为负数")
    private Integer maxStock;

    @Schema(description = "商品描述")
    private String description;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
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

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public BigDecimal getUnitPrice() {
        return unitPrice;
    }

    public void setUnitPrice(BigDecimal unitPrice) {
        this.unitPrice = unitPrice;
    }

    public Integer getMinStock() {
        return minStock;
    }

    public void setMinStock(Integer minStock) {
        this.minStock = minStock;
    }

    public Integer getMaxStock() {
        return maxStock;
    }

    public void setMaxStock(Integer maxStock) {
        this.maxStock = maxStock;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
