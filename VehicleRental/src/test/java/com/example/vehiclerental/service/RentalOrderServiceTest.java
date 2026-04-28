package com.example.vehiclerental.service;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.repository.RentalOrderRepository;
import com.example.vehiclerental.repository.RentalPriceRepository;
import com.example.vehiclerental.repository.VehicleRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RentalOrderServiceTest {

    @Mock
    private RentalOrderRepository rentalOrderRepository;

    @Mock
    private VehicleRepository vehicleRepository;

    @Mock
    private RentalPriceRepository rentalPriceRepository;

    @InjectMocks
    private RentalOrderService rentalOrderService;

    private VehicleType sedanType;
    private Vehicle testVehicle;
    private RentalOrder testOrder;

    @BeforeEach
    void setUp() {
        sedanType = new VehicleType();
        sedanType.setId(1L);
        sedanType.setName("经济型轿车");
        sedanType.setBasePricePerDay(new BigDecimal("150.00"));

        testVehicle = new Vehicle();
        testVehicle.setId(1L);
        testVehicle.setPlateNumber("京A12345");
        testVehicle.setVehicleType(sedanType);
        testVehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        testOrder = new RentalOrder();
        testOrder.setId(1L);
        testOrder.setOrderNumber("RL123456TEST");
        testOrder.setVehicle(testVehicle);
        testOrder.setCustomerName("张三");
        testOrder.setCustomerPhone("13800138000");
        testOrder.setPickupTime(LocalDateTime.now().plusDays(1));
        testOrder.setReturnTime(LocalDateTime.now().plusDays(3));
        testOrder.setUnitPrice(new BigDecimal("150.00"));
        testOrder.setRentalUnit(RentalOrder.RentalUnit.DAY);
        testOrder.setStatus(RentalOrder.OrderStatus.PENDING);
    }

    @Test
    @DisplayName("测试创建订单 - 成功")
    void testCreateRentalOrder_Success() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalPriceRepository.findActivePricesForDate(eq(sedanType), any(LocalDateTime.class))).thenReturn(Arrays.asList());
        when(rentalOrderRepository.findOverlappingOrders(eq(testVehicle), any(LocalDateTime.class), any(LocalDateTime.class), anyList())).thenReturn(Arrays.asList());
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> {
            RentalOrder order = invocation.getArgument(0);
            order.setId(1L);
            return order;
        });

        RentalOrder result = rentalOrderService.createRentalOrder(testOrder, 1L);

        assertNotNull(result);
        assertEquals(RentalOrder.OrderStatus.PENDING, result.getStatus());
        assertEquals(new BigDecimal("300.00"), result.getTotalAmount());
        verify(rentalOrderRepository).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 车辆不存在")
    void testCreateRentalOrder_VehicleNotFound() {
        when(vehicleRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 999L);
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 车辆不可用")
    void testCreateRentalOrder_VehicleUnavailable() {
        testVehicle.setStatus(Vehicle.VehicleStatus.MAINTENANCE);
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        assertThrows(BusinessException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 1L);
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 手机号格式无效")
    void testCreateRentalOrder_InvalidPhoneNumber() {
        testOrder.setCustomerPhone("123456789");
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        BusinessException exception = assertThrows(BusinessException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 1L);
        });

        assertTrue(exception.getMessage().contains("手机号码"));
        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 取车时间早于当前时间")
    void testCreateRentalOrder_PickupTimeBeforeNow() {
        testOrder.setPickupTime(LocalDateTime.now().minusHours(1));
        testOrder.setReturnTime(LocalDateTime.now().plusDays(1));
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        BusinessException exception = assertThrows(BusinessException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 1L);
        });

        assertTrue(exception.getMessage().contains("取车时间不能早于当前时间"));
        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 取车时间晚于还车时间")
    void testCreateRentalOrder_PickupAfterReturn() {
        testOrder.setPickupTime(LocalDateTime.now().plusDays(5));
        testOrder.setReturnTime(LocalDateTime.now().plusDays(3));
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        BusinessException exception = assertThrows(BusinessException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 1L);
        });

        assertTrue(exception.getMessage().contains("取车时间不能晚于还车时间"));
        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试创建订单 - 存在重叠订单")
    void testCreateRentalOrder_OverlappingOrders() {
        RentalOrder overlappingOrder = new RentalOrder();
        overlappingOrder.setId(2L);

        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalOrderRepository.findOverlappingOrders(eq(testVehicle), any(LocalDateTime.class), any(LocalDateTime.class), anyList())).thenReturn(Arrays.asList(overlappingOrder));

        BusinessException exception = assertThrows(BusinessException.class, () -> {
            rentalOrderService.createRentalOrder(testOrder, 1L);
        });

        assertTrue(exception.getMessage().contains("已有预约或正在租赁中"));
        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试手机号验证 - 有效手机号")
    void testPhoneValidation_Valid() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));
        when(rentalPriceRepository.findActivePricesForDate(eq(sedanType), any(LocalDateTime.class))).thenReturn(Arrays.asList());
        when(rentalOrderRepository.findOverlappingOrders(eq(testVehicle), any(LocalDateTime.class), any(LocalDateTime.class), anyList())).thenReturn(Arrays.asList());
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        String[] validPhones = {"13800138000", "13912345678", "15987654321", "18600001111", "17712345678"};

        for (String phone : validPhones) {
            testOrder.setCustomerPhone(phone);
            assertDoesNotThrow(() -> {
                rentalOrderService.createRentalOrder(testOrder, 1L);
            });
        }
    }

    @Test
    @DisplayName("测试手机号验证 - 无效手机号")
    void testPhoneValidation_Invalid() {
        when(vehicleRepository.findById(1L)).thenReturn(Optional.of(testVehicle));

        String[] invalidPhones = {"123456789", "11111111111", "12345678901", "010-12345678", "abcdefghijk", "1380013800", ""};

        for (String phone : invalidPhones) {
            testOrder.setCustomerPhone(phone);
            assertThrows(BusinessException.class, () -> {
                rentalOrderService.createRentalOrder(testOrder, 1L);
            });
        }
    }

    @Test
    @DisplayName("测试费用计算 - 日租计算")
    void testCalculateTotalAmount_DayRental() {
        BigDecimal unitPrice = new BigDecimal("150.00");
        LocalDateTime start = LocalDateTime.of(2024, 1, 1, 10, 0);
        LocalDateTime end = LocalDateTime.of(2024, 1, 4, 10, 0);

        BigDecimal result = rentalOrderService.calculateTotalAmount(unitPrice, RentalOrder.RentalUnit.DAY, start, end);

        assertEquals(new BigDecimal("450.00"), result);
    }

    @Test
    @DisplayName("测试费用计算 - 小时租计算")
    void testCalculateTotalAmount_HourRental() {
        BigDecimal unitPrice = new BigDecimal("20.00");
        LocalDateTime start = LocalDateTime.of(2024, 1, 1, 10, 0);
        LocalDateTime end = LocalDateTime.of(2024, 1, 1, 15, 0);

        BigDecimal result = rentalOrderService.calculateTotalAmount(unitPrice, RentalOrder.RentalUnit.HOUR, start, end);

        assertEquals(new BigDecimal("100.00"), result);
    }

    @Test
    @DisplayName("测试费用计算 - 最小单位为1")
    void testCalculateTotalAmount_MinimumUnit() {
        BigDecimal unitPrice = new BigDecimal("150.00");
        LocalDateTime start = LocalDateTime.of(2024, 1, 1, 10, 0);
        LocalDateTime end = LocalDateTime.of(2024, 1, 1, 12, 0);

        BigDecimal result = rentalOrderService.calculateTotalAmount(unitPrice, RentalOrder.RentalUnit.DAY, start, end);

        assertEquals(new BigDecimal("150.00"), result);
    }

    @Test
    @DisplayName("测试确认订单 - 成功")
    void testConfirmOrder_Success() {
        testOrder.setStatus(RentalOrder.OrderStatus.PENDING);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        RentalOrder result = rentalOrderService.confirmOrder(1L);

        assertEquals(RentalOrder.OrderStatus.CONFIRMED, result.getStatus());
        verify(rentalOrderRepository).save(testOrder);
    }

    @Test
    @DisplayName("测试确认订单 - 非待确认状态")
    void testConfirmOrder_NotPending() {
        testOrder.setStatus(RentalOrder.OrderStatus.CONFIRMED);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));

        assertThrows(BusinessException.class, () -> {
            rentalOrderService.confirmOrder(1L);
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试开始租赁 - 成功")
    void testStartRental_Success() {
        testOrder.setStatus(RentalOrder.OrderStatus.CONFIRMED);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        when(vehicleRepository.save(any(Vehicle.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        RentalOrder result = rentalOrderService.startRental(1L);

        assertEquals(RentalOrder.OrderStatus.ACTIVE, result.getStatus());
        assertEquals(Vehicle.VehicleStatus.RENTED, testVehicle.getStatus());
        verify(vehicleRepository).save(testVehicle);
        verify(rentalOrderRepository).save(testOrder);
    }

    @Test
    @DisplayName("测试完成租赁 - 成功")
    void testCompleteRental_Success() {
        testOrder.setStatus(RentalOrder.OrderStatus.ACTIVE);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        when(vehicleRepository.save(any(Vehicle.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        RentalOrder result = rentalOrderService.completeRental(1L);

        assertEquals(RentalOrder.OrderStatus.COMPLETED, result.getStatus());
        assertEquals(Vehicle.VehicleStatus.AVAILABLE, testVehicle.getStatus());
        assertNotNull(result.getActualReturnTime());
        verify(vehicleRepository).save(testVehicle);
        verify(rentalOrderRepository).save(testOrder);
    }

    @Test
    @DisplayName("测试取消订单 - 成功（带取消原因）")
    void testCancelOrder_Success_WithReason() {
        testOrder.setStatus(RentalOrder.OrderStatus.PENDING);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        String cancelReason = "客户改变主意";
        RentalOrder result = rentalOrderService.cancelOrder(1L, cancelReason);

        assertEquals(RentalOrder.OrderStatus.CANCELLED, result.getStatus());
        assertEquals(cancelReason, result.getCancelReason());
        verify(rentalOrderRepository).save(testOrder);
    }

    @Test
    @DisplayName("测试取消订单 - 成功（进行中订单）")
    void testCancelOrder_Success_ActiveOrder() {
        testOrder.setStatus(RentalOrder.OrderStatus.ACTIVE);
        testVehicle.setStatus(Vehicle.VehicleStatus.RENTED);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));
        when(vehicleRepository.save(any(Vehicle.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(rentalOrderRepository.save(any(RentalOrder.class))).thenAnswer(invocation -> invocation.getArgument(0));

        RentalOrder result = rentalOrderService.cancelOrder(1L, "紧急情况取消");

        assertEquals(RentalOrder.OrderStatus.CANCELLED, result.getStatus());
        assertEquals(Vehicle.VehicleStatus.AVAILABLE, testVehicle.getStatus());
        verify(vehicleRepository).save(testVehicle);
    }

    @Test
    @DisplayName("测试取消订单 - 已完成订单无法取消")
    void testCancelOrder_Completed() {
        testOrder.setStatus(RentalOrder.OrderStatus.COMPLETED);
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));

        assertThrows(BusinessException.class, () -> {
            rentalOrderService.cancelOrder(1L, "测试取消");
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试取消订单 - 订单不存在")
    void testCancelOrder_NotFound() {
        when(rentalOrderRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            rentalOrderService.cancelOrder(999L, "测试取消");
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试更新订单 - 已完成订单无法修改")
    void testUpdateOrder_Completed() {
        testOrder.setStatus(RentalOrder.OrderStatus.COMPLETED);
        RentalOrder updateDetails = new RentalOrder();
        updateDetails.setCustomerName("李四");

        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));

        assertThrows(BusinessException.class, () -> {
            rentalOrderService.updateRentalOrder(1L, updateDetails);
        });

        verify(rentalOrderRepository, never()).save(any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试获取订单 - 成功")
    void testGetRentalOrderById_Success() {
        when(rentalOrderRepository.findById(1L)).thenReturn(Optional.of(testOrder));

        RentalOrder result = rentalOrderService.getRentalOrderById(1L);

        assertNotNull(result);
        assertEquals("RL123456TEST", result.getOrderNumber());
    }

    @Test
    @DisplayName("测试获取订单 - 不存在")
    void testGetRentalOrderById_NotFound() {
        when(rentalOrderRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            rentalOrderService.getRentalOrderById(999L);
        });
    }
}
