package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.repository.RentalOrderRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class StatisticsService {

    @Autowired
    private RentalOrderRepository rentalOrderRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private VehicleTypeRepository vehicleTypeRepository;

    public Map<String, Object> getRentalStatistics(LocalDateTime startDate, LocalDateTime endDate) {
        Map<String, Object> stats = new LinkedHashMap<>();
        
        List<RentalOrder> orders;
        if (startDate != null && endDate != null) {
            orders = rentalOrderRepository.findByPickupTimeBetween(startDate, endDate);
        } else {
            orders = rentalOrderRepository.findAll();
        }

        long totalRentals = orders.size();
        stats.put("totalRentals", totalRentals);

        long completedRentals = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                .count();
        stats.put("completedRentals", completedRentals);

        long activeRentals = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.ACTIVE)
                .count();
        stats.put("activeRentals", activeRentals);

        long cancelledRentals = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.CANCELLED)
                .count();
        stats.put("cancelledRentals", cancelledRentals);

        BigDecimal totalRevenue = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                .map(RentalOrder::getTotalAmount)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("totalRevenue", totalRevenue);

        BigDecimal totalExtraCharge = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                .map(RentalOrder::getExtraCharge)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("totalExtraCharge", totalExtraCharge);

        if (totalRentals > 0) {
            BigDecimal avgAmount = totalRevenue.divide(BigDecimal.valueOf(completedRentals > 0 ? completedRentals : totalRentals), 2, BigDecimal.ROUND_HALF_UP);
            stats.put("averageRentalAmount", avgAmount);
        } else {
            stats.put("averageRentalAmount", BigDecimal.ZERO);
        }

        return stats;
    }

    public Map<String, Object> getVehicleUtilizationStatistics(LocalDateTime startDate, LocalDateTime endDate) {
        Map<String, Object> stats = new LinkedHashMap<>();
        
        List<Vehicle> allVehicles = vehicleRepository.findAll();
        long totalVehicles = allVehicles.size();
        stats.put("totalVehicles", totalVehicles);

        long availableVehicles = allVehicles.stream()
                .filter(v -> v.getStatus() == Vehicle.VehicleStatus.AVAILABLE)
                .count();
        stats.put("availableVehicles", availableVehicles);

        long rentedVehicles = allVehicles.stream()
                .filter(v -> v.getStatus() == Vehicle.VehicleStatus.RENTED)
                .count();
        stats.put("rentedVehicles", rentedVehicles);

        long maintenanceVehicles = allVehicles.stream()
                .filter(v -> v.getStatus() == Vehicle.VehicleStatus.MAINTENANCE)
                .count();
        stats.put("maintenanceVehicles", maintenanceVehicles);

        if (totalVehicles > 0) {
            BigDecimal utilizationRate = BigDecimal.valueOf(rentedVehicles)
                    .divide(BigDecimal.valueOf(totalVehicles), 4, BigDecimal.ROUND_HALF_UP)
                    .multiply(BigDecimal.valueOf(100));
            stats.put("utilizationRate", utilizationRate.setScale(2, BigDecimal.ROUND_HALF_UP));
        } else {
            stats.put("utilizationRate", BigDecimal.ZERO);
        }

        List<RentalOrder> orders;
        if (startDate != null && endDate != null) {
            orders = rentalOrderRepository.findByPickupTimeBetween(startDate, endDate);
        } else {
            orders = rentalOrderRepository.findAll();
        }

        long completedOrders = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                .count();
        
        if (totalVehicles > 0 && completedOrders > 0) {
            BigDecimal avgRentalsPerVehicle = BigDecimal.valueOf(completedOrders)
                    .divide(BigDecimal.valueOf(totalVehicles), 2, BigDecimal.ROUND_HALF_UP);
            stats.put("avgRentalsPerVehicle", avgRentalsPerVehicle);
        } else {
            stats.put("avgRentalsPerVehicle", BigDecimal.ZERO);
        }

        return stats;
    }

    public Map<String, Object> getRevenueStatistics(LocalDateTime startDate, LocalDateTime endDate) {
        Map<String, Object> stats = new LinkedHashMap<>();
        
        List<RentalOrder> orders;
        if (startDate != null && endDate != null) {
            orders = rentalOrderRepository.findByActualReturnTimeBetween(startDate, endDate);
        } else {
            orders = rentalOrderRepository.findByStatus(RentalOrder.OrderStatus.COMPLETED);
        }

        List<RentalOrder> completedOrders = orders.stream()
                .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                .collect(Collectors.toList());

        long totalCompletedOrders = completedOrders.size();
        stats.put("totalCompletedOrders", totalCompletedOrders);

        BigDecimal totalRevenue = completedOrders.stream()
                .map(RentalOrder::getTotalAmount)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("totalRevenue", totalRevenue);

        BigDecimal baseRevenue = completedOrders.stream()
                .map(o -> o.getTotalAmount() != null && o.getExtraCharge() != null 
                        ? o.getTotalAmount().subtract(o.getExtraCharge()) 
                        : o.getTotalAmount())
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("baseRevenue", baseRevenue);

        BigDecimal extraChargeRevenue = completedOrders.stream()
                .map(RentalOrder::getExtraCharge)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("extraChargeRevenue", extraChargeRevenue);

        BigDecimal totalDeposits = completedOrders.stream()
                .map(RentalOrder::getDepositAmount)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        stats.put("totalDeposits", totalDeposits);

        if (totalCompletedOrders > 0) {
            BigDecimal avgOrderValue = totalRevenue.divide(
                    BigDecimal.valueOf(totalCompletedOrders), 2, BigDecimal.ROUND_HALF_UP);
            stats.put("avgOrderValue", avgOrderValue);
        } else {
            stats.put("avgOrderValue", BigDecimal.ZERO);
        }

        return stats;
    }

    public List<Map<String, Object>> getStatisticsByVehicleType(LocalDateTime startDate, LocalDateTime endDate) {
        List<Map<String, Object>> result = new ArrayList<>();
        List<VehicleType> vehicleTypes = vehicleTypeRepository.findAll();

        List<RentalOrder> allOrders;
        if (startDate != null && endDate != null) {
            allOrders = rentalOrderRepository.findByPickupTimeBetween(startDate, endDate);
        } else {
            allOrders = rentalOrderRepository.findAll();
        }

        for (VehicleType vehicleType : vehicleTypes) {
            Map<String, Object> typeStats = new LinkedHashMap<>();
            typeStats.put("vehicleTypeId", vehicleType.getId());
            typeStats.put("vehicleTypeName", vehicleType.getName());

            List<Vehicle> vehicles = vehicleRepository.findByVehicleType(vehicleType);
            typeStats.put("totalVehicles", vehicles.size());

            List<RentalOrder> typeOrders = allOrders.stream()
                    .filter(o -> o.getVehicle() != null 
                            && o.getVehicle().getVehicleType() != null
                            && o.getVehicle().getVehicleType().getId().equals(vehicleType.getId()))
                    .collect(Collectors.toList());

            typeStats.put("totalRentals", typeOrders.size());

            long completedRentals = typeOrders.stream()
                    .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                    .count();
            typeStats.put("completedRentals", completedRentals);

            BigDecimal totalRevenue = typeOrders.stream()
                    .filter(o -> o.getStatus() == RentalOrder.OrderStatus.COMPLETED)
                    .map(RentalOrder::getTotalAmount)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
            typeStats.put("totalRevenue", totalRevenue);

            if (!vehicles.isEmpty()) {
                long availableVehicles = vehicles.stream()
                        .filter(v -> v.getStatus() == Vehicle.VehicleStatus.AVAILABLE)
                        .count();
                long rentedVehicles = vehicles.stream()
                        .filter(v -> v.getStatus() == Vehicle.VehicleStatus.RENTED)
                        .count();
                
                typeStats.put("availableVehicles", availableVehicles);
                typeStats.put("rentedVehicles", rentedVehicles);

                BigDecimal utilizationRate = BigDecimal.valueOf(rentedVehicles)
                        .divide(BigDecimal.valueOf(vehicles.size()), 4, BigDecimal.ROUND_HALF_UP)
                        .multiply(BigDecimal.valueOf(100));
                typeStats.put("utilizationRate", utilizationRate.setScale(2, BigDecimal.ROUND_HALF_UP));
            } else {
                typeStats.put("availableVehicles", 0);
                typeStats.put("rentedVehicles", 0);
                typeStats.put("utilizationRate", BigDecimal.ZERO);
            }

            result.add(typeStats);
        }

        return result;
    }
}
