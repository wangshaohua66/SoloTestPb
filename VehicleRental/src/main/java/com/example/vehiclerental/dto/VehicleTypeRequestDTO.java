package com.example.vehiclerental.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;

public class VehicleTypeRequestDTO {

    @NotBlank(message = "车型名称不能为空")
    private String name;

    @NotBlank(message = "车型描述不能为空")
    private String description;

    @NotNull(message = "基础价格不能为空")
    private BigDecimal basePricePerDay;

    private BigDecimal basePricePerHour;

    private boolean available = true;

    public VehicleTypeRequestDTO() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public BigDecimal getBasePricePerDay() {
        return basePricePerDay;
    }

    public void setBasePricePerDay(BigDecimal basePricePerDay) {
        this.basePricePerDay = basePricePerDay;
    }

    public BigDecimal getBasePricePerHour() {
        return basePricePerHour;
    }

    public void setBasePricePerHour(BigDecimal basePricePerHour) {
        this.basePricePerHour = basePricePerHour;
    }

    public boolean isAvailable() {
        return available;
    }

    public void setAvailable(boolean available) {
        this.available = available;
    }
}
