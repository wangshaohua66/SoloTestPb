package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.VehicleRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class VehicleTypeService {

    @Autowired
    private VehicleTypeRepository vehicleTypeRepository;

    @Autowired
    private VehicleRepository vehicleRepository;

    @Transactional
    public VehicleType createVehicleType(VehicleType vehicleType) {
        if (vehicleTypeRepository.existsByName(vehicleType.getName())) {
            throw new BusinessException("车型名称已存在: " + vehicleType.getName());
        }
        return vehicleTypeRepository.save(vehicleType);
    }

    public List<VehicleType> getAllVehicleTypes() {
        return vehicleTypeRepository.findAll();
    }

    public VehicleType getVehicleTypeById(Long id) {
        return vehicleTypeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", id));
    }

    @Transactional
    public VehicleType updateVehicleType(Long id, VehicleType vehicleTypeDetails) {
        VehicleType vehicleType = vehicleTypeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", id));

        if (!vehicleType.getName().equals(vehicleTypeDetails.getName()) &&
                vehicleTypeRepository.existsByName(vehicleTypeDetails.getName())) {
            throw new BusinessException("车型名称已存在: " + vehicleTypeDetails.getName());
        }

        vehicleType.setName(vehicleTypeDetails.getName());
        vehicleType.setDescription(vehicleTypeDetails.getDescription());
        vehicleType.setBasePricePerDay(vehicleTypeDetails.getBasePricePerDay());
        vehicleType.setBasePricePerHour(vehicleTypeDetails.getBasePricePerHour());
        vehicleType.setAvailable(vehicleTypeDetails.isAvailable());

        return vehicleTypeRepository.save(vehicleType);
    }

    @Transactional
    public void deleteVehicleType(Long id) {
        VehicleType vehicleType = vehicleTypeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", id));

        if (!vehicleRepository.findByVehicleType(vehicleType).isEmpty()) {
            throw new BusinessException("该车型下存在车辆，无法删除");
        }

        vehicleTypeRepository.delete(vehicleType);
    }

    public List<VehicleType> getAvailableVehicleTypes() {
        return vehicleTypeRepository.findByAvailableTrue();
    }
}
