package com.example.vehiclerental.dto;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class DTOConverter {

    public VehicleTypeResponseDTO toVehicleTypeResponse(VehicleType vehicleType) {
        if (vehicleType == null) {
            return null;
        }
        VehicleTypeResponseDTO dto = new VehicleTypeResponseDTO();
        dto.setId(vehicleType.getId());
        dto.setName(vehicleType.getName());
        dto.setDescription(vehicleType.getDescription());
        dto.setBasePricePerDay(vehicleType.getBasePricePerDay());
        dto.setBasePricePerHour(vehicleType.getBasePricePerHour());
        dto.setAvailable(vehicleType.isAvailable());
        return dto;
    }

    public List<VehicleTypeResponseDTO> toVehicleTypeResponseList(List<VehicleType> vehicleTypes) {
        if (vehicleTypes == null) {
            return new ArrayList<>();
        }
        return vehicleTypes.stream()
                .map(this::toVehicleTypeResponse)
                .collect(Collectors.toList());
    }

    public VehicleType toVehicleTypeEntity(VehicleTypeRequestDTO dto) {
        if (dto == null) {
            return null;
        }
        VehicleType vehicleType = new VehicleType();
        vehicleType.setName(dto.getName());
        vehicleType.setDescription(dto.getDescription());
        vehicleType.setBasePricePerDay(dto.getBasePricePerDay());
        vehicleType.setBasePricePerHour(dto.getBasePricePerHour());
        vehicleType.setAvailable(dto.isAvailable());
        return vehicleType;
    }

    public VehicleResponseDTO toVehicleResponse(Vehicle vehicle) {
        if (vehicle == null) {
            return null;
        }
        VehicleResponseDTO dto = new VehicleResponseDTO();
        dto.setId(vehicle.getId());
        dto.setPlateNumber(vehicle.getPlateNumber());
        dto.setBrand(vehicle.getBrand());
        dto.setModel(vehicle.getModel());
        dto.setYear(vehicle.getYear());
        dto.setColor(vehicle.getColor());
        dto.setStatus(vehicle.getStatus());
        dto.setRemarks(vehicle.getRemarks());
        dto.setVehicleType(toVehicleTypeResponse(vehicle.getVehicleType()));
        return dto;
    }

    public List<VehicleResponseDTO> toVehicleResponseList(List<Vehicle> vehicles) {
        if (vehicles == null) {
            return new ArrayList<>();
        }
        return vehicles.stream()
                .map(this::toVehicleResponse)
                .collect(Collectors.toList());
    }

    public Vehicle toVehicleEntity(VehicleRequestDTO dto) {
        if (dto == null) {
            return null;
        }
        Vehicle vehicle = new Vehicle();
        vehicle.setPlateNumber(dto.getPlateNumber());
        vehicle.setBrand(dto.getBrand());
        vehicle.setModel(dto.getModel());
        vehicle.setYear(dto.getYear());
        vehicle.setColor(dto.getColor());
        vehicle.setRemarks(dto.getRemarks());
        return vehicle;
    }

    public RentalPriceResponseDTO toRentalPriceResponse(RentalPrice rentalPrice) {
        if (rentalPrice == null) {
            return null;
        }
        RentalPriceResponseDTO dto = new RentalPriceResponseDTO();
        dto.setId(rentalPrice.getId());
        dto.setVehicleType(toVehicleTypeResponse(rentalPrice.getVehicleType()));
        dto.setPricePerDay(rentalPrice.getPricePerDay());
        dto.setPricePerHour(rentalPrice.getPricePerHour());
        dto.setPricePerWeek(rentalPrice.getPricePerWeek());
        dto.setPricePerMonth(rentalPrice.getPricePerMonth());
        dto.setDepositAmount(rentalPrice.getDepositAmount());
        dto.setActive(rentalPrice.isActive());
        dto.setEffectiveDate(rentalPrice.getEffectiveDate());
        dto.setExpiryDate(rentalPrice.getExpiryDate());
        dto.setRemarks(rentalPrice.getRemarks());
        dto.setCreatedAt(rentalPrice.getCreatedAt());
        dto.setUpdatedAt(rentalPrice.getUpdatedAt());
        return dto;
    }

    public List<RentalPriceResponseDTO> toRentalPriceResponseList(List<RentalPrice> rentalPrices) {
        if (rentalPrices == null) {
            return new ArrayList<>();
        }
        return rentalPrices.stream()
                .map(this::toRentalPriceResponse)
                .collect(Collectors.toList());
    }

    public RentalPrice toRentalPriceEntity(RentalPriceRequestDTO dto) {
        if (dto == null) {
            return null;
        }
        RentalPrice rentalPrice = new RentalPrice();
        rentalPrice.setPricePerDay(dto.getPricePerDay());
        rentalPrice.setPricePerHour(dto.getPricePerHour());
        rentalPrice.setPricePerWeek(dto.getPricePerWeek());
        rentalPrice.setPricePerMonth(dto.getPricePerMonth());
        rentalPrice.setDepositAmount(dto.getDepositAmount());
        rentalPrice.setActive(dto.isActive());
        rentalPrice.setEffectiveDate(dto.getEffectiveDate());
        rentalPrice.setExpiryDate(dto.getExpiryDate());
        rentalPrice.setRemarks(dto.getRemarks());
        return rentalPrice;
    }

    public RentalOrderResponseDTO toRentalOrderResponse(RentalOrder rentalOrder) {
        if (rentalOrder == null) {
            return null;
        }
        RentalOrderResponseDTO dto = new RentalOrderResponseDTO();
        dto.setId(rentalOrder.getId());
        dto.setOrderNumber(rentalOrder.getOrderNumber());
        dto.setVehicle(toVehicleResponse(rentalOrder.getVehicle()));
        dto.setCustomerName(rentalOrder.getCustomerName());
        dto.setCustomerPhone(rentalOrder.getCustomerPhone());
        dto.setCustomerIdCard(rentalOrder.getCustomerIdCard());
        dto.setPickupTime(rentalOrder.getPickupTime());
        dto.setReturnTime(rentalOrder.getReturnTime());
        dto.setActualReturnTime(rentalOrder.getActualReturnTime());
        dto.setUnitPrice(rentalOrder.getUnitPrice());
        dto.setRentalUnit(rentalOrder.getRentalUnit());
        dto.setTotalAmount(rentalOrder.getTotalAmount());
        dto.setDepositAmount(rentalOrder.getDepositAmount());
        dto.setExtraCharge(rentalOrder.getExtraCharge());
        dto.setStatus(rentalOrder.getStatus());
        dto.setPickupLocation(rentalOrder.getPickupLocation());
        dto.setReturnLocation(rentalOrder.getReturnLocation());
        dto.setRemarks(rentalOrder.getRemarks());
        dto.setCancelReason(rentalOrder.getCancelReason());
        dto.setCreatedAt(rentalOrder.getCreatedAt());
        dto.setUpdatedAt(rentalOrder.getUpdatedAt());
        return dto;
    }

    public List<RentalOrderResponseDTO> toRentalOrderResponseList(List<RentalOrder> rentalOrders) {
        if (rentalOrders == null) {
            return new ArrayList<>();
        }
        return rentalOrders.stream()
                .map(this::toRentalOrderResponse)
                .collect(Collectors.toList());
    }

    public RentalOrder toRentalOrderEntity(RentalOrderRequestDTO dto) {
        if (dto == null) {
            return null;
        }
        RentalOrder rentalOrder = new RentalOrder();
        rentalOrder.setCustomerName(dto.getCustomerName());
        rentalOrder.setCustomerPhone(dto.getCustomerPhone());
        rentalOrder.setCustomerIdCard(dto.getCustomerIdCard());
        rentalOrder.setPickupTime(dto.getPickupTime());
        rentalOrder.setReturnTime(dto.getReturnTime());
        rentalOrder.setRentalUnit(dto.getRentalUnit());
        rentalOrder.setDepositAmount(dto.getDepositAmount());
        rentalOrder.setPickupLocation(dto.getPickupLocation());
        rentalOrder.setReturnLocation(dto.getReturnLocation());
        rentalOrder.setRemarks(dto.getRemarks());
        return rentalOrder;
    }
}
