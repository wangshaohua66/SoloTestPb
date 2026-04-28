package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.VehicleResponseDTO;
import com.example.vehiclerental.dto.VehicleTypeResponseDTO;
import com.example.vehiclerental.entity.Vehicle;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.service.VehicleService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(VehicleController.class)
class VehicleControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private VehicleService vehicleService;

    @MockBean
    private DTOConverter dtoConverter;

    @Autowired
    private ObjectMapper objectMapper;

    private VehicleType sedanType;
    private VehicleTypeResponseDTO sedanTypeDTO;
    private Vehicle testVehicle;
    private VehicleResponseDTO testVehicleDTO;

    @BeforeEach
    void setUp() {
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
        testVehicle.setYear(2023);
        testVehicle.setColor("白色");
        testVehicle.setVehicleType(sedanType);
        testVehicle.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        testVehicleDTO = new VehicleResponseDTO();
        testVehicleDTO.setId(1L);
        testVehicleDTO.setPlateNumber("京A12345");
        testVehicleDTO.setBrand("丰田");
        testVehicleDTO.setModel("卡罗拉");
        testVehicleDTO.setYear(2023);
        testVehicleDTO.setColor("白色");
        testVehicleDTO.setVehicleType(sedanTypeDTO);
        testVehicleDTO.setStatus(Vehicle.VehicleStatus.AVAILABLE);
    }

    @Test
    @DisplayName("测试获取所有车辆 - 成功")
    void testGetAllVehicles_Success() throws Exception {
        Vehicle vehicle2 = new Vehicle();
        vehicle2.setId(2L);
        vehicle2.setPlateNumber("京B67890");
        vehicle2.setBrand("大众");
        vehicle2.setModel("朗逸");
        vehicle2.setVehicleType(sedanType);
        vehicle2.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        VehicleResponseDTO dto2 = new VehicleResponseDTO();
        dto2.setId(2L);
        dto2.setPlateNumber("京B67890");
        dto2.setBrand("大众");
        dto2.setModel("朗逸");
        dto2.setStatus(Vehicle.VehicleStatus.AVAILABLE);

        List<Vehicle> vehicles = Arrays.asList(testVehicle, vehicle2);
        List<VehicleResponseDTO> dtos = Arrays.asList(testVehicleDTO, dto2);

        when(vehicleService.getAllVehicles()).thenReturn(vehicles);
        when(dtoConverter.toVehicleResponseList(vehicles)).thenReturn(dtos);

        mockMvc.perform(get("/api/vehicles")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].id").value(1L))
                .andExpect(jsonPath("$[0].plateNumber").value("京A12345"))
                .andExpect(jsonPath("$[1].id").value(2L))
                .andExpect(jsonPath("$[1].plateNumber").value("京B67890"));

        verify(vehicleService).getAllVehicles();
    }

    @Test
    @DisplayName("测试获取单个车辆 - 成功")
    void testGetVehicleById_Success() throws Exception {
        when(vehicleService.getVehicleById(1L)).thenReturn(testVehicle);
        when(dtoConverter.toVehicleResponse(testVehicle)).thenReturn(testVehicleDTO);

        mockMvc.perform(get("/api/vehicles/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.plateNumber").value("京A12345"))
                .andExpect(jsonPath("$.brand").value("丰田"))
                .andExpect(jsonPath("$.model").value("卡罗拉"))
                .andExpect(jsonPath("$.status").value("AVAILABLE"))
                .andExpect(jsonPath("$.vehicleType.name").value("经济型轿车"));

        verify(vehicleService).getVehicleById(1L);
    }

    @Test
    @DisplayName("测试获取单个车辆 - 不存在，返回404")
    void testGetVehicleById_NotFound() throws Exception {
        when(vehicleService.getVehicleById(999L))
                .thenThrow(new ResourceNotFoundException("车辆", "id", 999L));

        mockMvc.perform(get("/api/vehicles/999")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());

        verify(vehicleService).getVehicleById(999L);
    }

    @Test
    @DisplayName("测试删除车辆 - 成功，返回204")
    void testDeleteVehicle_Success() throws Exception {
        doNothing().when(vehicleService).deleteVehicle(1L);

        mockMvc.perform(delete("/api/vehicles/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNoContent());

        verify(vehicleService).deleteVehicle(1L);
    }

    @Test
    @DisplayName("测试删除车辆 - 存在活跃订单，返回400")
    void testDeleteVehicle_HasActiveOrders() throws Exception {
        doThrow(new BusinessException("该车辆存在活跃订单（待处理/已确认/租赁中），无法删除"))
                .when(vehicleService).deleteVehicle(1L);

        mockMvc.perform(delete("/api/vehicles/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isBadRequest());

        verify(vehicleService).deleteVehicle(1L);
    }

    @Test
    @DisplayName("测试获取可用车辆 - 成功")
    void testGetAvailableVehicles_Success() throws Exception {
        List<Vehicle> vehicles = Arrays.asList(testVehicle);
        List<VehicleResponseDTO> dtos = Arrays.asList(testVehicleDTO);

        when(vehicleService.getAvailableVehicles()).thenReturn(vehicles);
        when(dtoConverter.toVehicleResponseList(vehicles)).thenReturn(dtos);

        mockMvc.perform(get("/api/vehicles/available")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        verify(vehicleService).getAvailableVehicles();
    }

    @Test
    @DisplayName("测试更新车辆状态 - 成功")
    void testUpdateVehicleStatus_Success() throws Exception {
        Vehicle updatedVehicle = new Vehicle();
        updatedVehicle.setId(1L);
        updatedVehicle.setPlateNumber("京A12345");
        updatedVehicle.setStatus(Vehicle.VehicleStatus.MAINTENANCE);

        VehicleResponseDTO updatedDTO = new VehicleResponseDTO();
        updatedDTO.setId(1L);
        updatedDTO.setPlateNumber("京A12345");
        updatedDTO.setStatus(Vehicle.VehicleStatus.MAINTENANCE);

        when(vehicleService.updateVehicleStatus(1L, Vehicle.VehicleStatus.MAINTENANCE))
                .thenReturn(updatedVehicle);
        when(dtoConverter.toVehicleResponse(updatedVehicle)).thenReturn(updatedDTO);

        mockMvc.perform(put("/api/vehicles/1/status")
                        .param("status", "MAINTENANCE")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.status").value("MAINTENANCE"));

        verify(vehicleService).updateVehicleStatus(1L, Vehicle.VehicleStatus.MAINTENANCE);
    }

    @Test
    @DisplayName("测试按车牌号获取车辆 - 成功")
    void testGetVehicleByPlateNumber_Success() throws Exception {
        when(vehicleService.getVehicleByPlateNumber("京A12345")).thenReturn(testVehicle);
        when(dtoConverter.toVehicleResponse(testVehicle)).thenReturn(testVehicleDTO);

        mockMvc.perform(get("/api/vehicles/plate/京A12345")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.plateNumber").value("京A12345"));

        verify(vehicleService).getVehicleByPlateNumber("京A12345");
    }

    @Test
    @DisplayName("测试按状态获取车辆 - 成功")
    void testGetVehiclesByStatus_Success() throws Exception {
        List<Vehicle> vehicles = Arrays.asList(testVehicle);
        List<VehicleResponseDTO> dtos = Arrays.asList(testVehicleDTO);

        when(vehicleService.getVehiclesByStatus(Vehicle.VehicleStatus.AVAILABLE)).thenReturn(vehicles);
        when(dtoConverter.toVehicleResponseList(vehicles)).thenReturn(dtos);

        mockMvc.perform(get("/api/vehicles/status/AVAILABLE")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());

        verify(vehicleService).getVehiclesByStatus(Vehicle.VehicleStatus.AVAILABLE);
    }
}
