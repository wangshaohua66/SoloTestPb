package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.VehicleTypeRequestDTO;
import com.example.vehiclerental.dto.VehicleTypeResponseDTO;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.service.VehicleTypeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/vehicle-types")
public class VehicleTypeController {

    @Autowired
    private VehicleTypeService vehicleTypeService;

    @Autowired
    private DTOConverter dtoConverter;

    @PostMapping
    public ResponseEntity<VehicleTypeResponseDTO> createVehicleType(@Valid @RequestBody VehicleTypeRequestDTO requestDTO) {
        VehicleType vehicleType = dtoConverter.toVehicleTypeEntity(requestDTO);
        VehicleType created = vehicleTypeService.createVehicleType(vehicleType);
        VehicleTypeResponseDTO responseDTO = dtoConverter.toVehicleTypeResponse(created);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<VehicleTypeResponseDTO>> getAllVehicleTypes() {
        List<VehicleType> vehicleTypes = vehicleTypeService.getAllVehicleTypes();
        List<VehicleTypeResponseDTO> responseDTOs = dtoConverter.toVehicleTypeResponseList(vehicleTypes);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/available")
    public ResponseEntity<List<VehicleTypeResponseDTO>> getAvailableVehicleTypes() {
        List<VehicleType> vehicleTypes = vehicleTypeService.getAvailableVehicleTypes();
        List<VehicleTypeResponseDTO> responseDTOs = dtoConverter.toVehicleTypeResponseList(vehicleTypes);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/{id}")
    public ResponseEntity<VehicleTypeResponseDTO> getVehicleTypeById(@PathVariable Long id) {
        VehicleType vehicleType = vehicleTypeService.getVehicleTypeById(id);
        VehicleTypeResponseDTO responseDTO = dtoConverter.toVehicleTypeResponse(vehicleType);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}")
    public ResponseEntity<VehicleTypeResponseDTO> updateVehicleType(@PathVariable Long id, 
                                                           @Valid @RequestBody VehicleTypeRequestDTO requestDTO) {
        VehicleType vehicleTypeDetails = dtoConverter.toVehicleTypeEntity(requestDTO);
        VehicleType updated = vehicleTypeService.updateVehicleType(id, vehicleTypeDetails);
        VehicleTypeResponseDTO responseDTO = dtoConverter.toVehicleTypeResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteVehicleType(@PathVariable Long id) {
        vehicleTypeService.deleteVehicleType(id);
        return ResponseEntity.noContent().build();
    }
}
