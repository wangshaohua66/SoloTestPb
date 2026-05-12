package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.RentalOrderRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import com.example.vehiclerental.repository.VehicleTypeRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class VehicleServiceTest {

    @Mock
    private VehicleRepository vehicleRepository;

    @Mock
    private VehicleTypeRepository vehicleTypeRepository;

    @Mock
    private RentalOrderRepository rentalOrderRepository;

    @InjectMocks
    private VehicleService vehicleService;

    private VehicleType sedanType;
    private Vehicle testVehicle;

    @BeforeEach
    void setUp() {
        sedanType = new VehicleType();
        sedanType.setId(1L);
        sedanType.setName("经济型轿车");
        sedanType.setDescription("测试车型");
        sedanType.setBasePricePerDay(new BigDecimal("150.00"));
        sedanType.setAvailable(true);

        testVehicle = new Vehicle();
        testVehicle.setId(1L);
        testVehicle.setPlateNumber("京A12345");
        testVehicle.setBrand("丰田");
        testVehicle.setModel("卡罗拉");
        testVehicle.setYear(2023);
        testVehicle.setVehicleType(sedanType);
        testVehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);
    }

    @Test
    @DisplayName("测试创建车辆 - 成功")
    void testCreateVehicle_Success() {
        when(vehicleTypeRepository.findById(1L)).thenReturn(Optional.of(sedanType));
        when(vehicleRepository.existsByPlateNumber("京A12345")).thenReturn(false);
        when(vehicleRepository.save(any(Vehicle.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Vehicle result = vehicleService.createVehicle(testVehicle, 1L);

        assertNotNull(result);
        assertEquals("京A12345", result.getPlateNumber());
        assertEquals(Vehicle.VehicleStatus.AVAILABLE, result.getStatus());
        verify(vehicleRepository).save(any(Vehicle.class));
    }

    @Test
    @DisplayName("测试创建车辆 - 车牌号已存在")
    void testCreateVehicle_PlateNumberExists() {
        when(vehicleTypeRepository.findById(1L)).thenReturn(Optional.of(sedanType));
        when(vehicleRepository.existsByPlateNumber("京A12345")).thenReturn(true);

        assertThrows(BusinessException.class, () -> {
            vehicleService.createVehicle(testVehicle, 1L);
        });

        verify(vehicleRepository, never()).save(any(Vehicle.class));
    }

    @Test
    @DisplayName("测试创建车辆 - 车型不存在")
    void testCreateVehicle_VehicleTypeNotFound() {
        when(vehicleTypeRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            vehicleService.createVehicle(testVehicle, 999L);
        });

        verify(vehicleRepository, never()).save(any(Vehicle.class));
    }

    @Test
    @DisplayName("测试获取车辆 - 成功")
    void testGetVehicleById_Success() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        Vehicle result = vehicleService.getVehicleById(1L);

        assertNotNull(result);
        assertEquals("京A12345", result.getPlateNumber());
    }

    @Test
    @DisplayName("测试获取车辆 - 不存在")
    void testGetVehicleById_NotFound() {
        when(vehicleRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            vehicleService.getVehicleById(999L);
        });
    }

    @Test
    @DisplayName("测试删除车辆 - 成功（无活跃订单）")
    void testDeleteVehicle_Success_NoActiveOrders() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalOrderRepository.findByVehicleAndStatusIn(eq(testVehicle), anyList())).thenReturn(Arrays.asList());

        assertDoesNotThrow(() -> {
            vehicleService.deleteVehicle(1L);
        });

        verify(vehicleRepository).delete(testVehicle);
    }

    @Test
    @DisplayName("测试删除车辆 - 成功（车辆状态为RENTED但无活跃订单）")
    void testDeleteVehicle_Success_RentedStatusButNoActiveOrders() {
        testVehicle.setStatus(Vehicle.VehicleStatus.RENTED);
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalOrderRepository.findByVehicleAndStatusIn(eq(testVehicle), anyList())).thenReturn(Arrays.asList());

        assertDoesNotThrow(() -> {
            vehicleService.deleteVehicle(1L);
        });

        verify(vehicleRepository).delete(testVehicle);
    }

    @Test
    @DisplayName("测试删除车辆 - 失败（存在活跃订单）")
    void testDeleteVehicle_Failure_ActiveOrdersExist() {
        com.example.vehiclerental.entity.RentalOrder activeOrder = new com.example.vehiclerental.entity.RentalOrder();
        activeOrder.setId(1L);
        activeOrder.setOrderNumber("RL123456TEST");
        activeOrder.setStatus(com.example.vehiclerental.entity.RentalOrder.OrderStatus.ACTIVE);

        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalOrderRepository.findByVehicleAndStatusIn(eq(testVehicle), anyList())).thenReturn(Arrays.asList(activeOrder));

        BusinessException exception = assertThrows(BusinessException.class, () -> {
            vehicleService.deleteVehicle(1L);
        });

        assertTrue(exception.getMessage().contains("活跃订单"));
        verify(vehicleRepository, never()).delete(any(Vehicle.class));
    }

    @Test
    @DisplayName("测试删除车辆 - 失败（车辆不存在）")
    void testDeleteVehicle_NotFound() {
        when(vehicleRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            vehicleService.deleteVehicle(999L);
        });

        verify(vehicleRepository, never()).delete(any(Vehicle.class));
    }

    @Test
    @DisplayName("测试更新车辆状态 - 成功")
    void testUpdateVehicleStatus_Success() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(vehicleRepository.save(any(Vehicle.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Vehicle result = vehicleService.updateVehicleStatus(1L, Vehicle.VehicleStatus.MAINTENANCE);

        assertEquals(Vehicle.VehicleStatus.MAINTENANCE, result.getStatus());
        verify(vehicleRepository).save(testVehicle);
    }

    @Test
    @DisplayName("测试获取所有车辆列表")
    void testGetAllVehicles() {
        Vehicle vehicle2 = new Vehicle();
        vehicle2.setId(2L);
        vehicle2.setPlateNumber("京B67890");

        when(vehicleRepository.findAll()).thenReturn(Arrays.asList(testVehicle, vehicle2));

        List<Vehicle> result = vehicleService.getAllVehicles();

        assertEquals(2, result.size());
        verify(vehicleRepository).findAll();
    }

    @Test
    @DisplayName("测试按状态获取车辆列表")
    void testGetVehiclesByStatus() {
        Vehicle vehicle2 = new Vehicle();
        vehicle2.setId(2L);
        vehicle2.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        when(vehicleRepository.findByStatus(Vehicle.VehicleStatus.AVAILABLE)).thenReturn(Arrays.asList(testVehicle, vehicle2));

        List<Vehicle> result = vehicleService.getVehiclesByStatus(Vehicle.VehicleStatus.AVAILABLE);

        assertEquals(2, result.size());
        verify(vehicleRepository).findByStatus(Vehicle.VehicleStatus.AVAILABLE);
    }
}
