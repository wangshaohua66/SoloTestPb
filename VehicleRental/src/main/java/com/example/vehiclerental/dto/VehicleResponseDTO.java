package com.example.vehiclerental.dto;

import com.example.vehiclerental.entity.Vehicle;

public class VehicleResponseDTO {

    private Long id;
    private String plateNumber;
    private String brand;
    private String model;
    private Integer year;
    private String color;
    private Vehicle.VehicleStatus status;
    private String remarks;
    private VehicleTypeResponseDTO vehicleType;

    public VehicleResponseDTO() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getPlateNumber() {
        return plateNumber;
    }

    public void setPlateNumber(String plateNumber) {
        this.plateNumber = plateNumber;
    }

    public String getBrand() {
        return brand;
    }

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public Integer getYear() {
        return year;
    }

    public void setYear(Integer year) {
        this.year = year;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public Vehicle.VehicleStatus getStatus() {
        return status;
    }

    public void setStatus(Vehicle.VehicleStatus status) {
        this.status = status;
    }

    public String getRemarks() {
        return remarks;
    }

    public void setRemarks(String remarks) {
        this.remarks = remarks;
    }

    public VehicleTypeResponseDTO getVehicleType() {
        return vehicleType;
    }

    public void setVehicleType(VehicleTypeResponseDTO vehicleType) {
        this.vehicleType = vehicleType;
    }
}
