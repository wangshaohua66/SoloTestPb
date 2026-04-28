package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.RentalPriceRequestDTO;
import com.example.vehiclerental.dto.RentalPriceResponseDTO;
import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.service.RentalPriceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/rental-prices")
public class RentalPriceController {

    @Autowired
    private RentalPriceService rentalPriceService;

    @Autowired
    private DTOConverter dtoConverter;

    @PostMapping
    public ResponseEntity<RentalPriceResponseDTO> createRentalPrice(@Valid @RequestBody RentalPriceRequestDTO requestDTO,
                                                           @RequestParam Long vehicleTypeId) {
        RentalPrice rentalPrice = dtoConverter.toRentalPriceEntity(requestDTO);
        RentalPrice created = rentalPriceService.createRentalPrice(rentalPrice, vehicleTypeId);
        RentalPriceResponseDTO responseDTO = dtoConverter.toRentalPriceResponse(created);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<RentalPriceResponseDTO>> getAllRentalPrices() {
        List<RentalPrice> prices = rentalPriceService.getAllRentalPrices();
        List<RentalPriceResponseDTO> responseDTOs = dtoConverter.toRentalPriceResponseList(prices);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RentalPriceResponseDTO> getRentalPriceById(@PathVariable Long id) {
        RentalPrice price = rentalPriceService.getRentalPriceById(id);
        RentalPriceResponseDTO responseDTO = dtoConverter.toRentalPriceResponse(price);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/vehicle-type/{vehicleTypeId}")
    public ResponseEntity<List<RentalPriceResponseDTO>> getRentalPricesByVehicleType(@PathVariable Long vehicleTypeId) {
        List<RentalPrice> prices = rentalPriceService.getRentalPricesByVehicleType(vehicleTypeId);
        List<RentalPriceResponseDTO> responseDTOs = dtoConverter.toRentalPriceResponseList(prices);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/vehicle-type/{vehicleTypeId}/active")
    public ResponseEntity<Optional<RentalPriceResponseDTO>> getActivePriceForVehicleType(@PathVariable Long vehicleTypeId) {
        Optional<RentalPrice> price = rentalPriceService.getActivePriceForVehicleType(vehicleTypeId);
        Optional<RentalPriceResponseDTO> responseDTO = price.map(dtoConverter::toRentalPriceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/vehicle-type/{vehicleTypeId}/at-date")
    public ResponseEntity<Optional<RentalPriceResponseDTO>> getActivePriceForVehicleTypeAtDate(
            @PathVariable Long vehicleTypeId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime date) {
        Optional<RentalPrice> price = rentalPriceService.getActivePriceForVehicleTypeAtDate(vehicleTypeId, date);
        Optional<RentalPriceResponseDTO> responseDTO = price.map(dtoConverter::toRentalPriceResponse);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}")
    public ResponseEntity<RentalPriceResponseDTO> updateRentalPrice(@PathVariable Long id,
                                                           @Valid @RequestBody RentalPriceRequestDTO requestDTO,
                                                           @RequestParam(required = false) Long vehicleTypeId) {
        RentalPrice rentalPriceDetails = dtoConverter.toRentalPriceEntity(requestDTO);
        RentalPrice updated = rentalPriceService.updateRentalPrice(id, rentalPriceDetails, vehicleTypeId);
        RentalPriceResponseDTO responseDTO = dtoConverter.toRentalPriceResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/active")
    public ResponseEntity<RentalPriceResponseDTO> setActiveStatus(@PathVariable Long id,
                                                        @RequestParam boolean isActive) {
        RentalPrice updated = rentalPriceService.setActiveStatus(id, isActive);
        RentalPriceResponseDTO responseDTO = dtoConverter.toRentalPriceResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRentalPrice(@PathVariable Long id) {
        rentalPriceService.deleteRentalPrice(id);
        return ResponseEntity.noContent().build();
    }
}
