package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.VehicleRequestDTO;
import com.example.vehiclerental.dto.VehicleResponseDTO;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.service.VehicleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/vehicles")
public class VehicleController {

    @Autowired
    private VehicleService vehicleService;

    @Autowired
    private DTOConverter dtoConverter;

    @PostMapping
    public ResponseEntity<VehicleResponseDTO> createVehicle(@Valid @RequestBody VehicleRequestDTO requestDTO,
                                                  @RequestParam Long vehicleTypeId) {
        Vehicle vehicle = dtoConverter.toVehicleEntity(requestDTO);
        Vehicle created = vehicleService.createVehicle(vehicle, vehicleTypeId);
        VehicleResponseDTO responseDTO = dtoConverter.toVehicleResponse(created);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<VehicleResponseDTO>> getAllVehicles() {
        List<Vehicle> vehicles = vehicleService.getAllVehicles();
        List<VehicleResponseDTO> responseDTOs = dtoConverter.toVehicleResponseList(vehicles);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/available")
    public ResponseEntity<List<VehicleResponseDTO>> getAvailableVehicles() {
        List<Vehicle> vehicles = vehicleService.getAvailableVehicles();
        List<VehicleResponseDTO> responseDTOs = dtoConverter.toVehicleResponseList(vehicles);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/{id}")
    public ResponseEntity<VehicleResponseDTO> getVehicleById(@PathVariable Long id) {
        Vehicle vehicle = vehicleService.getVehicleById(id);
        VehicleResponseDTO responseDTO = dtoConverter.toVehicleResponse(vehicle);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/plate/{plateNumber}")
    public ResponseEntity<VehicleResponseDTO> getVehicleByPlateNumber(@PathVariable String plateNumber) {
        Vehicle vehicle = vehicleService.getVehicleByPlateNumber(plateNumber);
        VehicleResponseDTO responseDTO = dtoConverter.toVehicleResponse(vehicle);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/type/{vehicleTypeId}")
    public ResponseEntity<List<VehicleResponseDTO>> getVehiclesByType(@PathVariable Long vehicleTypeId) {
        List<Vehicle> vehicles = vehicleService.getVehiclesByType(vehicleTypeId);
        List<VehicleResponseDTO> responseDTOs = dtoConverter.toVehicleResponseList(vehicles);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<List<VehicleResponseDTO>> getVehiclesByStatus(@PathVariable Vehicle.VehicleStatus status) {
        List<Vehicle> vehicles = vehicleService.getVehiclesByStatus(status);
        List<VehicleResponseDTO> responseDTOs = dtoConverter.toVehicleResponseList(vehicles);
        return ResponseEntity.ok(responseDTOs);
    }

    @PutMapping("/{id}")
    public ResponseEntity<VehicleResponseDTO> updateVehicle(@PathVariable Long id,
                                                  @Valid @RequestBody VehicleRequestDTO requestDTO,
                                                  @RequestParam(required = false) Long vehicleTypeId) {
        Vehicle vehicleDetails = dtoConverter.toVehicleEntity(requestDTO);
        Vehicle updated = vehicleService.updateVehicle(id, vehicleDetails, vehicleTypeId);
        VehicleResponseDTO responseDTO = dtoConverter.toVehicleResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<VehicleResponseDTO> updateVehicleStatus(@PathVariable Long id,
                                                        @RequestParam Vehicle.VehicleStatus status) {
        Vehicle updated = vehicleService.updateVehicleStatus(id, status);
        VehicleResponseDTO responseDTO = dtoConverter.toVehicleResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteVehicle(@PathVariable Long id) {
        vehicleService.deleteVehicle(id);
        return ResponseEntity.noContent().build();
    }
}
