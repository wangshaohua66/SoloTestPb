package com.example.vehiclerental.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class VehicleTypeResponseDTO {

    private Long id;
    private String name;
    private String description;
    private BigDecimal basePricePerDay;
    private BigDecimal basePricePerHour;
    private boolean available;

    public VehicleTypeResponseDTO() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
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
