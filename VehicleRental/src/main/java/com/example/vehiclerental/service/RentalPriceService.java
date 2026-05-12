package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.RentalPriceRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class RentalPriceService {

    @Autowired
    private RentalPriceRepository rentalPriceRepository;

    @Autowired
    private VehicleTypeRepository vehicleTypeRepository;

    @Transactional
    public RentalPrice createRentalPrice(RentalPrice rentalPrice, Long vehicleTypeId) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
        
        rentalPrice.setVehicleType(vehicleType);
        return rentalPriceRepository.save(rentalPrice);
    }

    public List<RentalPrice> getAllRentalPrices() {
        return rentalPriceRepository.findAll();
    }

    public RentalPrice getRentalPriceById(Long id) {
        return rentalPriceRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁价格", "id", id));
    }

    @Transactional
    public RentalPrice updateRentalPrice(Long id, RentalPrice rentalPriceDetails, Long vehicleTypeId) {
        RentalPrice rentalPrice = rentalPriceRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁价格", "id", id));

        if (vehicleTypeId != null) {
            VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                    .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
            rentalPrice.setVehicleType(vehicleType);
        }

        rentalPrice.setPricePerDay(rentalPriceDetails.getPricePerDay());
        rentalPrice.setPricePerHour(rentalPriceDetails.getPricePerHour());
        rentalPrice.setPricePerWeek(rentalPriceDetails.getPricePerWeek());
        rentalPrice.setPricePerMonth(rentalPriceDetails.getPricePerMonth());
        rentalPrice.setDepositAmount(rentalPriceDetails.getDepositAmount());
        rentalPrice.setActive(rentalPriceDetails.isActive());
        rentalPrice.setEffectiveDate(rentalPriceDetails.getEffectiveDate());
        rentalPrice.setExpiryDate(rentalPriceDetails.getExpiryDate());
        rentalPrice.setRemarks(rentalPriceDetails.getRemarks());

        return rentalPriceRepository.save(rentalPrice);
    }

    @Transactional
    public void deleteRentalPrice(Long id) {
        RentalPrice rentalPrice = rentalPriceRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁价格", "id", id));
        rentalPriceRepository.delete(rentalPrice);
    }

    public List<RentalPrice> getRentalPricesByVehicleType(Long vehicleTypeId) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
        return rentalPriceRepository.findByVehicleType(vehicleType);
    }

    public Optional<RentalPrice> getActivePriceForVehicleType(Long vehicleTypeId) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
        return rentalPriceRepository.findFirstByVehicleTypeAndIsActiveTrueOrderByEffectiveDateDesc(vehicleType);
    }

    public Optional<RentalPrice> getActivePriceForVehicleTypeAtDate(Long vehicleTypeId, LocalDateTime date) {
        VehicleType vehicleType = vehicleTypeRepository.findById(vehicleTypeId)
                .orElseThrow(() -> new ResourceNotFoundException("车型", "id", vehicleTypeId));
        List<RentalPrice> prices = rentalPriceRepository.findActivePricesForDate(vehicleType, date);
        return prices.isEmpty() ? Optional.empty() : Optional.of(prices.get(0));
    }

    @Transactional
    public RentalPrice setActiveStatus(Long id, boolean isActive) {
        RentalPrice rentalPrice = rentalPriceRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("租赁价格", "id", id));
        rentalPrice.setActive(isActive);
        return rentalPriceRepository.save(rentalPrice);
    }
}
