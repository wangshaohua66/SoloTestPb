package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.RentalOrderRequestDTO;
import com.example.vehiclerental.dto.RentalOrderResponseDTO;
import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.service.RentalOrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/rental-orders")
public class RentalOrderController {

    @Autowired
    private RentalOrderService rentalOrderService;

    @Autowired
    private DTOConverter dtoConverter;

    @PostMapping
    public ResponseEntity<RentalOrderResponseDTO> createRentalOrder(@Valid @RequestBody RentalOrderRequestDTO requestDTO,
                                                           @RequestParam Long vehicleId) {
        RentalOrder rentalOrder = dtoConverter.toRentalOrderEntity(requestDTO);
        RentalOrder created = rentalOrderService.createRentalOrder(rentalOrder, vehicleId);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(created);
        return new ResponseEntity<>(responseDTO, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<RentalOrderResponseDTO>> getAllRentalOrders() {
        List<RentalOrder> orders = rentalOrderService.getAllRentalOrders();
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RentalOrderResponseDTO> getRentalOrderById(@PathVariable Long id) {
        RentalOrder order = rentalOrderService.getRentalOrderById(id);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(order);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/order-number/{orderNumber}")
    public ResponseEntity<RentalOrderResponseDTO> getRentalOrderByOrderNumber(@PathVariable String orderNumber) {
        RentalOrder order = rentalOrderService.getRentalOrderByOrderNumber(orderNumber);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(order);
        return ResponseEntity.ok(responseDTO);
    }

    @GetMapping("/status/{status}")
    public ResponseEntity<List<RentalOrderResponseDTO>> getOrdersByStatus(@PathVariable RentalOrder.OrderStatus status) {
        List<RentalOrder> orders = rentalOrderService.getOrdersByStatus(status);
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/vehicle/{vehicleId}")
    public ResponseEntity<List<RentalOrderResponseDTO>> getOrdersByVehicle(@PathVariable Long vehicleId) {
        List<RentalOrder> orders = rentalOrderService.getOrdersByVehicle(vehicleId);
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/customer/{customerName}")
    public ResponseEntity<List<RentalOrderResponseDTO>> getOrdersByCustomerName(@PathVariable String customerName) {
        List<RentalOrder> orders = rentalOrderService.getOrdersByCustomerName(customerName);
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/pickup-range")
    public ResponseEntity<List<RentalOrderResponseDTO>> getOrdersByPickupTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<RentalOrder> orders = rentalOrderService.getOrdersByPickupTimeRange(start, end);
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @GetMapping("/return-range")
    public ResponseEntity<List<RentalOrderResponseDTO>> getOrdersByActualReturnTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<RentalOrder> orders = rentalOrderService.getOrdersByActualReturnTimeRange(start, end);
        List<RentalOrderResponseDTO> responseDTOs = dtoConverter.toRentalOrderResponseList(orders);
        return ResponseEntity.ok(responseDTOs);
    }

    @PutMapping("/{id}")
    public ResponseEntity<RentalOrderResponseDTO> updateRentalOrder(@PathVariable Long id,
                                                           @Valid @RequestBody RentalOrderRequestDTO requestDTO) {
        RentalOrder orderDetails = dtoConverter.toRentalOrderEntity(requestDTO);
        RentalOrder updated = rentalOrderService.updateRentalOrder(id, orderDetails);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/confirm")
    public ResponseEntity<RentalOrderResponseDTO> confirmOrder(@PathVariable Long id) {
        RentalOrder updated = rentalOrderService.confirmOrder(id);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/start")
    public ResponseEntity<RentalOrderResponseDTO> startRental(@PathVariable Long id) {
        RentalOrder updated = rentalOrderService.startRental(id);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/complete")
    public ResponseEntity<RentalOrderResponseDTO> completeRental(@PathVariable Long id) {
        RentalOrder updated = rentalOrderService.completeRental(id);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }

    @PutMapping("/{id}/cancel")
    public ResponseEntity<RentalOrderResponseDTO> cancelOrder(@PathVariable Long id,
                                                    @RequestParam(required = false, defaultValue = "客户取消") String cancelReason) {
        RentalOrder updated = rentalOrderService.cancelOrder(id, cancelReason);
        RentalOrderResponseDTO responseDTO = dtoConverter.toRentalOrderResponse(updated);
        return ResponseEntity.ok(responseDTO);
    }
}
