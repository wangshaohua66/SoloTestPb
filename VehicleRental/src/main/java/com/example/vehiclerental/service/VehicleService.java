package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.RentalOrderRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;

@Service
public class VehicleService {

    private static final Logger logger = LoggerFactory.getLogger(VehicleService.class);

    @Autowired
    private VehicleRepository vehicleRepository;

    @Autowired
    private VehicleTypeRepository vehicleTypeRepository;

    @Autowired
    private RentalOrderRepository rentalOrderRepository;

    @Transactional
    public Vehicle createVehicle(Vehicle vehicle, Long vehicleTypeId) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));

        if (vehicleRepository.existsByPlateNumber(vehicle.getPlateNumber())) {
            throw new BusinessException("车牌号已存在: " + vehicle.getPlateNumber());
        }

        vehicle.setVehicleType(vehicleType);
        vehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);
        return vehicleRepository.save(vehicle);
    }

    public List<Vehicle> getAllVehicles() {
        return vehicleRepository.findAll();
    }

    public Vehicle getVehicleById(Long id) {
        return vehicleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "id", id));
    }

    public Vehicle getVehicleByPlateNumber(String plateNumber) {
        return vehicleRepository.findByPlateNumber(plateNumber)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "车牌号", plateNumber));
    }

    @Transactional
    public Vehicle updateVehicle(Long id, Vehicle vehicleDetails, Long vehicleTypeId) {
        Vehicle vehicle = vehicleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "id", id));

        if (!vehicle.getPlateNumber().equals(vehicleDetails.getPlateNumber()) &&
                vehicleRepository.existsByPlateNumber(vehicleDetails.getPlateNumber())) {
            throw new BusinessException("车牌号已存在: " + vehicleDetails.getPlateNumber());
        }

        if (vehicleTypeId != null) {
            VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                    .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
            vehicle.setVehicleType(vehicleType);
        }

        vehicle.setPlateNumber(vehicleDetails.getPlateNumber());
        vehicle.setBrand(vehicleDetails.getBrand());
        vehicle.setModel(vehicleDetails.getModel());
        vehicle.setYear(vehicleDetails.getYear());
        vehicle.setColor(vehicleDetails.getColor());
        vehicle.setRemarks(vehicleDetails.getRemarks());

        return vehicleRepository.save(vehicle);
    }

    @Transactional
    public void deleteVehicle(Long id) {
        Vehicle vehicle = vehicleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "id", id));

        List<RentalOrder.OrderStatus> activeStatuses = Arrays.asList(
                RentalOrder.OrderStatus.PENDING,
                RentalOrder.OrderStatus.CONFIRMED,
                RentalOrder.OrderStatus.ACTIVE
        );
        
        List<RentalOrder> activeOrders = rentalOrderRepository.findByVehicleAndStatusIn(vehicle, activeStatuses);
        
        if (!activeOrders.isEmpty()) {
            logger.warn("尝试删除车辆 {} 失败，该车辆存在 {} 个活跃订单", vehicle.getPlateNumber(), activeOrders.size());
            throw new BusinessException("该车辆存在活跃订单（待处理/已确认/租赁中），无法删除");
        }

        vehicleRepository.delete(vehicle);
        logger.info("车辆 {} 已成功删除", vehicle.getPlateNumber());
    }

    @Transactional
    public Vehicle updateVehicleStatus(Long id, Vehicle.VehicleStatus status) {
        Vehicle vehicle = vehicleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车辆", "id", id));
        vehicle.setStatus(status);
        return vehicleRepository.save(vehicle);
    }

    public List<Vehicle> getVehiclesByStatus(Vehicle.VehicleStatus status) {
        return vehicleRepository.findByStatus(status);
    }

    public List<Vehicle> getAvailableVehicles() {
        return vehicleRepository.findByStatusIn(Arrays.asList(
                Vehicle.VehicleStatus.AVAILABLE,
                Vehicle.VehicleStatus.MAINTENANCE
        ));
    }

    public List<Vehicle> getVehiclesByType(Long vehicleTypeId) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
        return vehicleRepository.findByVehicleType(vehicleType);
    }
}
