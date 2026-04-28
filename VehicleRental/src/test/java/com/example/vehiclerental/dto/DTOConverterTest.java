package com.example.vehiclerental.dto;

import com.example.vehiclerental.entity.RentalOrder;
import com.example.vehiclerental.entity.RentalPrice;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DTOConverterTest {

    private DTOConverter converter;
    private VehicleType sedanType;
    private Vehicle testVehicle;
    private RentalPrice testPrice;
    private RentalOrder testOrder;

    @BeforeEach
    void setUp() {
        converter = new DTOConverter();

        sedanType = new VehicleType();
        sedanType.setId(1L);
        sedanType.setName("经济型轿车");
        sedanType.setDescription("适合日常出行");
        sedanType.setBasePricePerDay(new BigDecimal("150.00"));
        sedanType.setBasePricePerHour(new BigDecimal("20.00"));
        sedanType.setAvailable(true);

        testVehicle = new Vehicle();
        testVehicle.setId(1L);
        testVehicle.setPlateNumber("京A12345");
        testVehicle.setBrand("丰田");
        testVehicle.setModel("卡罗拉");
        testVehicle.setYear(2023);
        testVehicle.setColor("白色");
        testVehicle.setVehicleType(sedanType);
        testVehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);
        testVehicle.setRemarks("新车状态良好");

        testPrice = new RentalPrice();
        testPrice.setId(1L);
        testPrice.setVehicleType(sedanType);
        testPrice.setPricePerDay(new BigDecimal("150.00"));
        testPrice.setPricePerHour(new BigDecimal("20.00"));
        testPrice.setPricePerWeek(new BigDecimal("900.00"));
        testPrice.setPricePerMonth(new BigDecimal("3750.00"));
        testPrice.setDepositAmount(new BigDecimal("450.00"));
        testPrice.setActive(true);
        testPrice.setEffectiveDate(LocalDateTime.now());
        testPrice.setRemarks("标准价格");

        testOrder = new RentalOrder();
        testOrder.setId(1L);
        testOrder.setOrderNumber("RL123456TEST");
        testOrder.setVehicle(testVehicle);
        testOrder.setCustomerName("张三");
        testOrder.setCustomerPhone("13800138000");
        testOrder.setCustomerIdCard("110101199001011234");
        testOrder.setPickupTime(LocalDateTime.now().plusDays(1));
        testOrder.setReturnTime(LocalDateTime.now().plusDays(3));
        testOrder.setUnitPrice(new BigDecimal("150.00"));
        testOrder.setRentalUnit(RentalOrder.RentalUnit.DAY);
        testOrder.setTotalAmount(new BigDecimal("300.00"));
        testOrder.setDepositAmount(new BigDecimal("450.00"));
        testOrder.setStatus(RentalOrder.OrderStatus.PENDING);
        testOrder.setPickupLocation("北京首都机场");
        testOrder.setReturnLocation("北京首都机场");
        testOrder.setRemarks("客户要求提前准备好车辆");
        testOrder.setCancelReason(null);
    }

    @Test
    @DisplayName("测试 VehicleType 转换为 VehicleTypeResponseDTO")
    void testToVehicleTypeResponse() {
        VehicleTypeResponseDTO dto = converter.toVehicleTypeResponse(sedanType);

        assertNotNull(dto);
        assertEquals(1L, dto.getId());
        assertEquals("经济型轿车", dto.getName());
        assertEquals("适合日常出行", dto.getDescription());
        assertEquals(new BigDecimal("150.00"), dto.getBasePricePerDay());
        assertEquals(new BigDecimal("20.00"), dto.getBasePricePerHour());
        assertTrue(dto.isAvailable());
    }

    @Test
    @DisplayName("测试 VehicleType 列表转换")
    void testToVehicleTypeResponseList() {
        VehicleType suvType = new VehicleType();
        suvType.setId(2L);
        suvType.setName("SUV");

        List<VehicleType> types = Arrays.asList(sedanType, suvType);
        List<VehicleTypeResponseDTO> dtos = converter.toVehicleTypeResponseList(types);

        assertEquals(2, dtos.size());
        assertEquals("经济型轿车", dtos.get(0).getName());
        assertEquals("SUV", dtos.get(1).getName());
    }

    @Test
    @DisplayName("测试 VehicleTypeRequestDTO 转换为 VehicleType 实体")
    void testToVehicleTypeEntity() {
        VehicleTypeRequestDTO requestDTO = new VehicleTypeRequestDTO();
        requestDTO.setName("豪华轿车");
        requestDTO.setDescription("高端商务用车");
        requestDTO.setBasePricePerDay(new BigDecimal("500.00"));
        requestDTO.setBasePricePerHour(new BigDecimal("80.00"));
        requestDTO.setAvailable(true);

        VehicleType vehicleType = converter.toVehicleTypeEntity(requestDTO);

        assertNotNull(vehicleType);
        assertEquals("豪华轿车", vehicleType.getName());
        assertEquals("高端商务用车", vehicleType.getDescription());
        assertEquals(new BigDecimal("500.00"), vehicleType.getBasePricePerDay());
        assertEquals(new BigDecimal("80.00"), vehicleType.getBasePricePerHour());
        assertTrue(vehicleType.isAvailable());
    }

    @Test
    @DisplayName("测试 Vehicle 转换为 VehicleResponseDTO")
    void testToVehicleResponse() {
        VehicleResponseDTO dto = converter.toVehicleResponse(testVehicle);

        assertNotNull(dto);
        assertEquals(1L, dto.getId());
        assertEquals("京A12345", dto.getPlateNumber());
        assertEquals("丰田", dto.getBrand());
        assertEquals("卡罗拉", dto.getModel());
        assertEquals(2023, dto.getYear());
        assertEquals("白色", dto.getColor());
        assertEquals(Vehicle.VehicleStatus.AVAILABLE, dto.getStatus());
        assertEquals("新车状态良好", dto.getRemarks());

        assertNotNull(dto.getVehicleType());
        assertEquals("经济型轿车", dto.getVehicleType().getName());
    }

    @Test
    @DisplayName("测试 Vehicle 列表转换")
    void testToVehicleResponseList() {
        Vehicle vehicle2 = new Vehicle();
        vehicle2.setId(2L);
        vehicle2.setPlateNumber("京B67890");

        List<Vehicle> vehicles = Arrays.asList(testVehicle, vehicle2);
        List<VehicleResponseDTO> dtos = converter.toVehicleResponseList(vehicles);

        assertEquals(2, dtos.size());
        assertEquals("京A12345", dtos.get(0).getPlateNumber());
        assertEquals("京B67890", dtos.get(1).getPlateNumber());
    }

    @Test
    @DisplayName("测试 VehicleRequestDTO 转换为 Vehicle 实体")
    void testToVehicleEntity() {
        VehicleRequestDTO requestDTO = new VehicleRequestDTO();
        requestDTO.setPlateNumber("京C11111");
        requestDTO.setBrand("奔驰");
        requestDTO.setModel("E级");
        requestDTO.setYear(2024);
        requestDTO.setColor("黑色");
        requestDTO.setRemarks("商务专用");

        Vehicle vehicle = converter.toVehicleEntity(requestDTO);

        assertNotNull(vehicle);
        assertEquals("京C11111", vehicle.getPlateNumber());
        assertEquals("奔驰", vehicle.getBrand());
        assertEquals("E级", vehicle.getModel());
        assertEquals(2024, vehicle.getYear());
        assertEquals("黑色", vehicle.getColor());
        assertEquals("商务专用", vehicle.getRemarks());
    }

    @Test
    @DisplayName("测试 RentalPrice 转换为 RentalPriceResponseDTO")
    void testToRentalPriceResponse() {
        RentalPriceResponseDTO dto = converter.toRentalPriceResponse(testPrice);

        assertNotNull(dto);
        assertEquals(1L, dto.getId());
        assertEquals(new BigDecimal("150.00"), dto.getPricePerDay());
        assertEquals(new BigDecimal("20.00"), dto.getPricePerHour());
        assertEquals(new BigDecimal("900.00"), dto.getPricePerWeek());
        assertEquals(new BigDecimal("3750.00"), dto.getPricePerMonth());
        assertEquals(new BigDecimal("450.00"), dto.getDepositAmount());
        assertTrue(dto.isActive());
        assertEquals("标准价格", dto.getRemarks());

        assertNotNull(dto.getVehicleType());
        assertEquals("经济型轿车", dto.getVehicleType().getName());
    }

    @Test
    @DisplayName("测试 RentalPrice 列表转换")
    void testToRentalPriceResponseList() {
        RentalPrice price2 = new RentalPrice();
        price2.setId(2L);

        List<RentalPrice> prices = Arrays.asList(testPrice, price2);
        List<RentalPriceResponseDTO> dtos = converter.toRentalPriceResponseList(prices);

        assertEquals(2, dtos.size());
        assertEquals(1L, dtos.get(0).getId());
        assertEquals(2L, dtos.get(1).getId());
    }

    @Test
    @DisplayName("测试 RentalPriceRequestDTO 转换为 RentalPrice 实体")
    void testToRentalPriceEntity() {
        RentalPriceRequestDTO requestDTO = new RentalPriceRequestDTO();
        requestDTO.setPricePerDay(new BigDecimal("500.00"));
        requestDTO.setPricePerHour(new BigDecimal("80.00"));
        requestDTO.setPricePerWeek(new BigDecimal("3000.00"));
        requestDTO.setPricePerMonth(new BigDecimal("12000.00"));
        requestDTO.setDepositAmount(new BigDecimal("1500.00"));
        requestDTO.setActive(true);
        requestDTO.setRemarks("豪华车型价格");

        RentalPrice rentalPrice = converter.toRentalPriceEntity(requestDTO);

        assertNotNull(rentalPrice);
        assertEquals(new BigDecimal("500.00"), rentalPrice.getPricePerDay());
        assertEquals(new BigDecimal("80.00"), rentalPrice.getPricePerHour());
        assertEquals(new BigDecimal("3000.00"), rentalPrice.getPricePerWeek());
        assertEquals(new BigDecimal("12000.00"), rentalPrice.getPricePerMonth());
        assertEquals(new BigDecimal("1500.00"), rentalPrice.getDepositAmount());
        assertTrue(rentalPrice.isActive());
        assertEquals("豪华车型价格", rentalPrice.getRemarks());
    }

    @Test
    @DisplayName("测试 RentalOrder 转换为 RentalOrderResponseDTO")
    void testToRentalOrderResponse() {
        testOrder.setActualReturnTime(LocalDateTime.now().plusDays(3));
        testOrder.setExtraCharge(new BigDecimal("50.00"));

        RentalOrderResponseDTO dto = converter.toRentalOrderResponse(testOrder);

        assertNotNull(dto);
        assertEquals(1L, dto.getId());
        assertEquals("RL123456TEST", dto.getOrderNumber());
        assertEquals("张三", dto.getCustomerName());
        assertEquals("13800138000", dto.getCustomerPhone());
        assertEquals("110101199001011234", dto.getCustomerIdCard());
        assertEquals(new BigDecimal("150.00"), dto.getUnitPrice());
        assertEquals(RentalOrder.RentalUnit.DAY, dto.getRentalUnit());
        assertEquals(new BigDecimal("300.00"), dto.getTotalAmount());
        assertEquals(new BigDecimal("450.00"), dto.getDepositAmount());
        assertEquals(new BigDecimal("50.00"), dto.getExtraCharge());
        assertEquals(RentalOrder.OrderStatus.PENDING, dto.getStatus());
        assertEquals("北京首都机场", dto.getPickupLocation());
        assertEquals("北京首都机场", dto.getReturnLocation());
        assertEquals("客户要求提前准备好车辆", dto.getRemarks());
        assertNull(dto.getCancelReason());

        assertNotNull(dto.getVehicle());
        assertEquals("京A12345", dto.getVehicle().getPlateNumber());
    }

    @Test
    @DisplayName("测试已取消订单的转换 - 包含取消原因")
    void testToRentalOrderResponse_Cancelled() {
        testOrder.setStatus(RentalOrder.OrderStatus.CANCELLED);
        testOrder.setCancelReason("客户改变主意");

        RentalOrderResponseDTO dto = converter.toRentalOrderResponse(testOrder);

        assertNotNull(dto);
        assertEquals(RentalOrder.OrderStatus.CANCELLED, dto.getStatus());
        assertEquals("客户改变主意", dto.getCancelReason());
    }

    @Test
    @DisplayName("测试 RentalOrder 列表转换")
    void testToRentalOrderResponseList() {
        RentalOrder order2 = new RentalOrder();
        order2.setId(2L);
        order2.setOrderNumber("RL987654TEST");

        List<RentalOrder> orders = Arrays.asList(testOrder, order2);
        List<RentalOrderResponseDTO> dtos = converter.toRentalOrderResponseList(orders);

        assertEquals(2, dtos.size());
        assertEquals("RL123456TEST", dtos.get(0).getOrderNumber());
        assertEquals("RL987654TEST", dtos.get(1).getOrderNumber());
    }

    @Test
    @DisplayName("测试 RentalOrderRequestDTO 转换为 RentalOrder 实体")
    void testToRentalOrderEntity() {
        RentalOrderRequestDTO requestDTO = new RentalOrderRequestDTO();
        requestDTO.setCustomerName("李四");
        requestDTO.setCustomerPhone("13912345678");
        requestDTO.setCustomerIdCard("110102198805155678");
        requestDTO.setPickupTime(LocalDateTime.now().plusDays(2));
        requestDTO.setReturnTime(LocalDateTime.now().plusDays(5));
        requestDTO.setRentalUnit(RentalOrder.RentalUnit.DAY);
        requestDTO.setDepositAmount(new BigDecimal("600.00"));
        requestDTO.setPickupLocation("上海浦东机场");
        requestDTO.setReturnLocation("上海虹桥机场");
        requestDTO.setRemarks("需要儿童座椅");

        RentalOrder rentalOrder = converter.toRentalOrderEntity(requestDTO);

        assertNotNull(rentalOrder);
        assertEquals("李四", rentalOrder.getCustomerName());
        assertEquals("13912345678", rentalOrder.getCustomerPhone());
        assertEquals("110102198805155678", rentalOrder.getCustomerIdCard());
        assertEquals(RentalOrder.RentalUnit.DAY, rentalOrder.getRentalUnit());
        assertEquals(new BigDecimal("600.00"), rentalOrder.getDepositAmount());
        assertEquals("上海浦东机场", rentalOrder.getPickupLocation());
        assertEquals("上海虹桥机场", rentalOrder.getReturnLocation());
        assertEquals("需要儿童座椅", rentalOrder.getRemarks());
    }

    @Test
    @DisplayName("测试空对象转换返回null")
    void testNullConversions() {
        assertNull(converter.toVehicleTypeResponse(null));
        assertNull(converter.toVehicleTypeEntity(null));
        assertNull(converter.toVehicleResponse(null));
        assertNull(converter.toVehicleEntity(null));
        assertNull(converter.toRentalPriceResponse(null));
        assertNull(converter.toRentalPriceEntity(null));
        assertNull(converter.toRentalOrderResponse(null));
        assertNull(converter.toRentalOrderEntity(null));
    }

    @Test
    @DisplayName("测试空列表转换返回空列表")
    void testEmptyListConversions() {
        assertTrue(converter.toVehicleTypeResponseList(null).isEmpty());
        assertTrue(converter.toVehicleResponseList(null).isEmpty());
        assertTrue(converter.toRentalPriceResponseList(null).isEmpty());
        assertTrue(converter.toRentalOrderResponseList(null).isEmpty());
    }
}
