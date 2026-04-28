package com.example.vehiclerental.entity;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;

@Entity
@Table(name = "vehicle_types")
public class VehicleType {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "车型名称不能为空")
    @Column(unique = true, nullable = false)
    private String name;

    @NotBlank(message = "车型描述不能为空")
    private String description;

    @NotNull(message = "基础价格不能为空")
    @Column(precision = 10, scale = 2)
    private BigDecimal basePricePerDay;

    @Column(precision = 10, scale = 2)
    private BigDecimal basePricePerHour;

    private boolean available = true;

    public VehicleType() {
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
