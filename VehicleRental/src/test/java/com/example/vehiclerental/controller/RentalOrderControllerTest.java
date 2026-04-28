package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.RentalOrderRequestDTO;
import com.example.vehiclerental.dto.RentalOrderResponseDTO;
import com.example.vehiclerental.dto.VehicleResponseDTO;
import com.example.vehiclerental.dto.VehicleTypeResponseDTO;
import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.service.RentalOrderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(RentalOrderController.class)
class RentalOrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private RentalOrderService rentalOrderService;

    @MockBean
    private DTOConverter dtoConverter;

    private ObjectMapper objectMapper;

    private VehicleType sedanType;
    private VehicleTypeResponseDTO sedanTypeDTO;
    private Vehicle testVehicle;
    private VehicleResponseDTO testVehicleDTO;
    private RentalOrder testOrder;
    private RentalOrderResponseDTO testOrderDTO;
    private RentalOrderRequestDTO createRequestDTO;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());

        sedanType = new VehicleType();
        sedanType.setId(1L);
        sedanType.setName("经济型轿车");
        sedanType.setBasePricePerDay(new BigDecimal("150.00"));

        sedanTypeDTO = new VehicleTypeResponseDTO();
        sedanTypeDTO.setId(1L);
        sedanTypeDTO.setName("经济型轿车");
        sedanTypeDTO.setBasePricePerDay(new BigDecimal("150.00"));

        testVehicle = new Vehicle();
        testVehicle.setId(1L);
        testVehicle.setPlateNumber("京A12345");
        testVehicle.setBrand("丰田");
        testVehicle.setModel("卡罗拉");
        testVehicle.setVehicleType(sedanType);
        testVehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        testVehicleDTO = new VehicleResponseDTO();
        testVehicleDTO.setId(1L);
        testVehicleDTO.setPlateNumber("京A12345");
        testVehicleDTO.setBrand("丰田");
        testVehicleDTO.setModel("卡罗拉");
        testVehicleDTO.setVehicleType(sedanTypeDTO);
        testVehicleDTO.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        testOrder = new RentalOrder();
        testOrder.setId(1L);
        testOrder.setOrderNumber("RL202401010001");
        testOrder.setVehicle(testVehicle);
        testOrder.setCustomerName("张三");
        testOrder.setCustomerPhone("13800138000");
        testOrder.setPickupTime(LocalDateTime.now().plusDays(1));
        testOrder.setReturnTime(LocalDateTime.now().plusDays(3));
        testOrder.setUnitPrice(new BigDecimal("150.00"));
        testOrder.setTotalAmount(new BigDecimal("300.00"));
        testOrder.setDepositAmount(new BigDecimal("450.00"));
        testOrder.setStatus(RentalOrder.OrderStatus.PENDING);

        testOrderDTO = new RentalOrderResponseDTO();
        testOrderDTO.setId(1L);
        testOrderDTO.setOrderNumber("RL202401010001");
        testOrderDTO.setVehicle(testVehicleDTO);
        testOrderDTO.setCustomerName("张三");
        testOrderDTO.setCustomerPhone("13800138000");
        testOrderDTO.setPickupTime(LocalDateTime.now().plusDays(1));
        testOrderDTO.setReturnTime(LocalDateTime.now().plusDays(3));
        testOrderDTO.setUnitPrice(new BigDecimal("150.00"));
        testOrderDTO.setTotalAmount(new BigDecimal("300.00"));
        testOrderDTO.setDepositAmount(new BigDecimal("450.00"));
        testOrderDTO.setStatus(RentalOrder.OrderStatus.PENDING);

        createRequestDTO = new RentalOrderRequestDTO();
        createRequestDTO.setCustomerName("张三");
        createRequestDTO.setCustomerPhone("13800138000");
        createRequestDTO.setPickupTime(LocalDateTime.now().plusDays(1));
        createRequestDTO.setReturnTime(LocalDateTime.now().plusDays(3));
        createRequestDTO.setRentalUnit(RentalOrder.RentalUnit.DAY);
        createRequestDTO.setDepositAmount(new BigDecimal("450.00"));
    }

    @Test
    @DisplayName("测试创建订单 - 成功，返回201")
    void testCreateRentalOrder_Success() throws Exception {
        RentalOrder savedOrder = new RentalOrder();
        savedOrder.setId(2L);
        savedOrder.setOrderNumber("RL202401010002");
        savedOrder.setCustomerName("张三");
        savedOrder.setCustomerPhone("13800138000");
        savedOrder.setStatus(RentalOrder.OrderStatus.PENDING);

        RentalOrderResponseDTO responseDTO = new RentalOrderResponseDTO();
        responseDTO.setId(2L);
        responseDTO.setOrderNumber("RL202401010002");
        responseDTO.setCustomerName("张三");
        responseDTO.setCustomerPhone("13800138000");
        responseDTO.setStatus(RentalOrder.OrderStatus.PENDING);

        when(dtoConverter.toRentalOrderEntity(any(RentalOrderRequestDTO.class))).thenReturn(savedOrder);
        when(rentalOrderService.createRentalOrder(any(RentalOrder.class), eq(1L))).thenReturn(savedOrder);
        when(dtoConverter.toRentalOrderResponse(any(RentalOrder.class))).thenReturn(responseDTO);

        mockMvc.perform(post("/api/rental-orders")
                        .param("vehicleId", "1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequestDTO)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(2L))
                .andExpect(jsonPath("$.orderNumber").value("RL202401010002"))
                .andExpect(jsonPath("$.customerName").value("张三"))
                .andExpect(jsonPath("$.status").value("PENDING"));

        verify(rentalOrderService).createRentalOrder(any(RentalOrder.class), eq(1L));
    }

    @Test
    @DisplayName("测试创建订单 - 无效手机号，返回400（DTO层面的@Pattern校验）")
    void testCreateRentalOrder_InvalidPhone() throws Exception {
        RentalOrderRequestDTO invalidRequest = new RentalOrderRequestDTO();
        invalidRequest.setCustomerName("张三");
        invalidRequest.setCustomerPhone("123456789");
        invalidRequest.setPickupTime(LocalDateTime.now().plusDays(1));
        invalidRequest.setReturnTime(LocalDateTime.now().plusDays(3));

        mockMvc.perform(post("/api/rental-orders")
                        .param("vehicleId", "1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation Error"))
                .andExpect(jsonPath("$.errors.customerPhone").value("请输入有效的11位手机号码"));

        verify(rentalOrderService, never()).createRentalOrder(any(RentalOrder.class), eq(1L));
    }

    @Test
    @DisplayName("测试获取所有订单 - 成功")
    void testGetAllRentalOrders_Success() throws Exception {
        RentalOrder order2 = new RentalOrder();
        order2.setId(2L);
        order2.setOrderNumber("RL202401010002");
        order2.setCustomerName("李四");
        order2.setStatus(RentalOrder.OrderStatus.CONFIRMED);

        RentalOrderResponseDTO dto2 = new RentalOrderResponseDTO();
        dto2.setId(2L);
        dto2.setOrderNumber("RL202401010002");
        dto2.setCustomerName("李四");
        dto2.setStatus(RentalOrder.OrderStatus.CONFIRMED);

        List<RentalOrder> orders = Arrays.asList(testOrder, order2);
        List<RentalOrderResponseDTO> dtos = Arrays.asList(testOrderDTO, dto2);

        when(rentalOrderService.getAllRentalOrders()).thenReturn(orders);
        when(dtoConverter.toRentalOrderResponseList(orders)).thenReturn(dtos);

        mockMvc.perform(get("/api/rental-orders")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].id").value(1L))
                .andExpect(jsonPath("$[1].id").value(2L));

        verify(rentalOrderService).getAllRentalOrders();
    }

    @Test
    @DisplayName("测试获取单个订单 - 成功")
    void testGetRentalOrderById_Success() throws Exception {
        when(rentalOrderService.getRentalOrderById(1L)).thenReturn(testOrder);
        when(dtoConverter.toRentalOrderResponse(testOrder)).thenReturn(testOrderDTO);

        mockMvc.perform(get("/api/rental-orders/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.orderNumber").value("RL202401010001"))
                .andExpect(jsonPath("$.customerName").value("张三"))
                .andExpect(jsonPath("$.vehicle.plateNumber").value("京A12345"));

        verify(rentalOrderService).getRentalOrderById(1L);
    }

    @Test
    @DisplayName("测试获取单个订单 - 不存在，返回404")
    void testGetRentalOrderById_NotFound() throws Exception {
        when(rentalOrderService.getRentalOrderById(999L))
                .thenThrow(new ResourceNotFoundException("租赁订单", "id", 999L));

        mockMvc.perform(get("/api/rental-orders/999")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());

        verify(rentalOrderService).getRentalOrderById(999L);
    }

    @Test
    @DisplayName("测试确认订单 - 成功")
    void testConfirmOrder_Success() throws Exception {
        RentalOrder confirmedOrder = new RentalOrder();
        confirmedOrder.setId(1L);
        confirmedOrder.setOrderNumber("RL202401010001");
        confirmedOrder.setStatus(RentalOrder.OrderStatus.CONFIRMED);

        RentalOrderResponseDTO confirmedDTO = new RentalOrderResponseDTO();
        confirmedDTO.setId(1L);
        confirmedDTO.setOrderNumber("RL202401010001");
        confirmedDTO.setStatus(RentalOrder.OrderStatus.CONFIRMED);

        when(rentalOrderService.confirmOrder(1L)).thenReturn(confirmedOrder);
        when(dtoConverter.toRentalOrderResponse(confirmedOrder)).thenReturn(confirmedDTO);

        mockMvc.perform(put("/api/rental-orders/1/confirm")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.status").value("CONFIRMED"));

        verify(rentalOrderService).confirmOrder(1L);
    }

    @Test
    @DisplayName("测试取消订单 - 成功")
    void testCancelOrder_Success() throws Exception {
        RentalOrder cancelledOrder = new RentalOrder();
        cancelledOrder.setId(1L);
        cancelledOrder.setOrderNumber("RL202401010001");
        cancelledOrder.setStatus(RentalOrder.OrderStatus.CANCELLED);
        cancelledOrder.setCancelReason("客户改变主意");

        RentalOrderResponseDTO cancelledDTO = new RentalOrderResponseDTO();
        cancelledDTO.setId(1L);
        cancelledDTO.setOrderNumber("RL202401010001");
        cancelledDTO.setStatus(RentalOrder.OrderStatus.CANCELLED);
        cancelledDTO.setCancelReason("客户改变主意");

        when(rentalOrderService.cancelOrder(1L, "客户改变主意")).thenReturn(cancelledOrder);
        when(dtoConverter.toRentalOrderResponse(cancelledOrder)).thenReturn(cancelledDTO);

        mockMvc.perform(put("/api/rental-orders/1/cancel")
                        .param("cancelReason", "客户改变主意")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.status").value("CANCELLED"))
                .andExpect(jsonPath("$.cancelReason").value("客户改变主意"));

        verify(rentalOrderService).cancelOrder(1L, "客户改变主意");
    }

    @Test
    @DisplayName("测试开始租赁 - 成功")
    void testStartRental_Success() throws Exception {
        RentalOrder activeOrder = new RentalOrder();
        activeOrder.setId(1L);
        activeOrder.setOrderNumber("RL202401010001");
        activeOrder.setStatus(RentalOrder.OrderStatus.ACTIVE);

        RentalOrderResponseDTO activeDTO = new RentalOrderResponseDTO();
        activeDTO.setId(1L);
        activeDTO.setOrderNumber("RL202401010001");
        activeDTO.setStatus(RentalOrder.OrderStatus.ACTIVE);

        when(rentalOrderService.startRental(1L)).thenReturn(activeOrder);
        when(dtoConverter.toRentalOrderResponse(activeOrder)).thenReturn(activeDTO);

        mockMvc.perform(put("/api/rental-orders/1/start")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.status").value("ACTIVE"));

        verify(rentalOrderService).startRental(1L);
    }

    @Test
    @DisplayName("测试按状态获取订单 - 成功")
    void testGetOrdersByStatus_Success() throws Exception {
        List<RentalOrder> orders = Arrays.asList(testOrder);
        List<RentalOrderResponseDTO> dtos = Arrays.asList(testOrderDTO);

        when(rentalOrderService.getOrdersByStatus(RentalOrder.OrderStatus.PENDING)).thenReturn(orders);
        when(dtoConverter.toRentalOrderResponseList(orders)).thenReturn(dtos);

        mockMvc.perform(get("/api/rental-orders/status/PENDING")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        verify(rentalOrderService).getOrdersByStatus(RentalOrder.OrderStatus.PENDING);
    }

    @Test
    @DisplayName("测试更新订单 - 成功")
    void testUpdateRentalOrder_Success() throws Exception {
        RentalOrderRequestDTO updateRequestDTO = new RentalOrderRequestDTO();
        updateRequestDTO.setCustomerName("张三(更新)");
        updateRequestDTO.setCustomerPhone("13900139000");
        updateRequestDTO.setPickupTime(LocalDateTime.now().plusDays(2));
        updateRequestDTO.setReturnTime(LocalDateTime.now().plusDays(5));
        updateRequestDTO.setRentalUnit(RentalOrder.RentalUnit.DAY);
        updateRequestDTO.setDepositAmount(new BigDecimal("500.00"));

        RentalOrder updatedOrder = new RentalOrder();
        updatedOrder.setId(1L);
        updatedOrder.setOrderNumber("RL202401010001");
        updatedOrder.setCustomerName("张三(更新)");
        updatedOrder.setCustomerPhone("13900139000");
        updatedOrder.setStatus(RentalOrder.OrderStatus.PENDING);

        RentalOrderResponseDTO updatedDTO = new RentalOrderResponseDTO();
        updatedDTO.setId(1L);
        updatedDTO.setOrderNumber("RL202401010001");
        updatedDTO.setCustomerName("张三(更新)");
        updatedDTO.setCustomerPhone("13900139000");
        updatedDTO.setStatus(RentalOrder.OrderStatus.PENDING);

        when(dtoConverter.toRentalOrderEntity(any(RentalOrderRequestDTO.class))).thenReturn(updatedOrder);
        when(rentalOrderService.updateRentalOrder(eq(1L), any(RentalOrder.class))).thenReturn(updatedOrder);
        when(dtoConverter.toRentalOrderResponse(updatedOrder)).thenReturn(updatedDTO);

        mockMvc.perform(put("/api/rental-orders/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequestDTO)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.customerName").value("张三(更新)"))
                .andExpect(jsonPath("$.customerPhone").value("13900139000"));

        verify(rentalOrderService).updateRentalOrder(eq(1L), any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试更新订单 - 无效手机号，返回400")
    void testUpdateRentalOrder_InvalidPhone() throws Exception {
        RentalOrderRequestDTO invalidRequest = new RentalOrderRequestDTO();
        invalidRequest.setCustomerName("张三");
        invalidRequest.setCustomerPhone("123456789");
        invalidRequest.setPickupTime(LocalDateTime.now().plusDays(1));
        invalidRequest.setReturnTime(LocalDateTime.now().plusDays(3));

        mockMvc.perform(put("/api/rental-orders/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation Error"))
                .andExpect(jsonPath("$.errors.customerPhone").value("请输入有效的11位手机号码"));

        verify(rentalOrderService, never()).updateRentalOrder(anyLong(), any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试更新订单 - 订单不存在，返回404")
    void testUpdateRentalOrder_NotFound() throws Exception {
        RentalOrderRequestDTO updateRequestDTO = new RentalOrderRequestDTO();
        updateRequestDTO.setCustomerName("张三");
        updateRequestDTO.setCustomerPhone("13800138000");
        updateRequestDTO.setPickupTime(LocalDateTime.now().plusDays(1));
        updateRequestDTO.setReturnTime(LocalDateTime.now().plusDays(3));

        when(dtoConverter.toRentalOrderEntity(any(RentalOrderRequestDTO.class))).thenReturn(testOrder);
        when(rentalOrderService.updateRentalOrder(eq(999L), any(RentalOrder.class)))
                .thenThrow(new ResourceNotFoundException("租赁订单", "id", 999L));

        mockMvc.perform(put("/api/rental-orders/999")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequestDTO)))
                .andExpect(status().isNotFound());

        verify(rentalOrderService).updateRentalOrder(eq(999L), any(RentalOrder.class));
    }

    @Test
    @DisplayName("测试完成租赁 - 成功")
    void testCompleteRental_Success() throws Exception {
        RentalOrder completedOrder = new RentalOrder();
        completedOrder.setId(1L);
        completedOrder.setOrderNumber("RL202401010001");
        completedOrder.setStatus(RentalOrder.OrderStatus.COMPLETED);

        RentalOrderResponseDTO completedDTO = new RentalOrderResponseDTO();
        completedDTO.setId(1L);
        completedDTO.setOrderNumber("RL202401010001");
        completedDTO.setStatus(RentalOrder.OrderStatus.COMPLETED);

        when(rentalOrderService.completeRental(1L)).thenReturn(completedOrder);
        when(dtoConverter.toRentalOrderResponse(completedOrder)).thenReturn(completedDTO);

        mockMvc.perform(put("/api/rental-orders/1/complete")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.status").value("COMPLETED"));

        verify(rentalOrderService).completeRental(1L);
    }

    @Test
    @DisplayName("测试按订单号获取订单 - 成功")
    void testGetRentalOrderByOrderNumber_Success() throws Exception {
        when(rentalOrderService.getRentalOrderByOrderNumber("RL202401010001")).thenReturn(testOrder);
        when(dtoConverter.toRentalOrderResponse(testOrder)).thenReturn(testOrderDTO);

        mockMvc.perform(get("/api/rental-orders/order-number/RL202401010001")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.orderNumber").value("RL202401010001"));

        verify(rentalOrderService).getRentalOrderByOrderNumber("RL202401010001");
    }

    @Test
    @DisplayName("测试按车辆获取订单 - 成功")
    void testGetOrdersByVehicle_Success() throws Exception {
        List<RentalOrder> orders = Arrays.asList(testOrder);
        List<RentalOrderResponseDTO> dtos = Arrays.asList(testOrderDTO);

        when(rentalOrderService.getOrdersByVehicle(1L)).thenReturn(orders);
        when(dtoConverter.toRentalOrderResponseList(orders)).thenReturn(dtos);

        mockMvc.perform(get("/api/rental-orders/vehicle/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        verify(rentalOrderService).getOrdersByVehicle(1L);
    }

    @Test
    @DisplayName("测试按客户名获取订单 - 成功")
    void testGetOrdersByCustomerName_Success() throws Exception {
        List<RentalOrder> orders = Arrays.asList(testOrder);
        List<RentalOrderResponseDTO> dtos = Arrays.asList(testOrderDTO);

        when(rentalOrderService.getOrdersByCustomerName("张三")).thenReturn(orders);
        when(dtoConverter.toRentalOrderResponseList(orders)).thenReturn(dtos);

        mockMvc.perform(get("/api/rental-orders/customer/张三")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        verify(rentalOrderService).getOrdersByCustomerName("张三");
    }
}
