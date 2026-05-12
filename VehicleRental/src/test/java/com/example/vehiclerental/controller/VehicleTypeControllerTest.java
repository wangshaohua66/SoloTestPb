package com.example.vehiclerental.controller;

import com.example.vehiclerental.dto.DTOConverter;
import com.example.vehiclerental.dto.VehicleTypeRequestDTO;
import com.example.vehiclerental.dto.VehicleTypeResponseDTO;
import com.example.vehiclerental.entity.VehicleType;
import com.example.vehiclerental.exception.BusinessException;
import com.example.vehiclerental.exception.ResourceNotFoundException;
import com.example.vehiclerental.service.VehicleTypeService;
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

@WebMvcTest(VehicleTypeController.class)
class VehicleTypeControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private VehicleTypeService vehicleTypeService;

    @MockBean
    private DTOConverter dtoConverter;

    @Autowired
    private ObjectMapper objectMapper;

    private VehicleType sedanType;
    private VehicleTypeResponseDTO sedanDTO;
    private VehicleTypeRequestDTO createRequestDTO;

    @BeforeEach
    void setUp() {
        sedanType = new VehicleType();
        sedanType.setId(1L);
        sedanType.setName("经济型轿车");
        sedanType.setDescription("适合日常出行");
        sedanType.setBasePricePerDay(new BigDecimal("150.00"));
        sedanType.setBasePricePerHour(new BigDecimal("20.00"));
        sedanType.setAvailable(true);

        sedanDTO = new VehicleTypeResponseDTO();
        sedanDTO.setId(1L);
        sedanDTO.setName("经济型轿车");
        sedanDTO.setDescription("适合日常出行");
        sedanDTO.setBasePricePerDay(new BigDecimal("150.00"));
        sedanDTO.setBasePricePerHour(new BigDecimal("20.00"));
        sedanDTO.setAvailable(true);

        createRequestDTO = new VehicleTypeRequestDTO();
        createRequestDTO.setName("SUV");
        createRequestDTO.setDescription("适合家庭出行");
        createRequestDTO.setBasePricePerDay(new BigDecimal("300.00"));
        createRequestDTO.setBasePricePerHour(new BigDecimal("40.00"));
        createRequestDTO.setAvailable(true);
    }

    @Test
    @DisplayName("测试创建车型 - 成功")
    void testCreateVehicleType_Success() throws Exception {
        VehicleType savedType = new VehicleType();
        savedType.setId(2L);
        savedType.setName("SUV");
        savedType.setDescription("适合家庭出行");
        savedType.setBasePricePerDay(new BigDecimal("300.00"));
        savedType.setAvailable(true);

        VehicleTypeResponseDTO responseDTO = new VehicleTypeResponseDTO();
        responseDTO.setId(2L);
        responseDTO.setName("SUV");
        responseDTO.setDescription("适合家庭出行");
        responseDTO.setBasePricePerDay(new BigDecimal("300.00"));
        responseDTO.setAvailable(true);

        when(dtoConverter.toVehicleTypeEntity(any(VehicleTypeRequestDTO.class))).thenReturn(savedType);
        when(vehicleTypeService.createVehicleType(any(VehicleType.class))).thenReturn(savedType);
        when(dtoConverter.toVehicleTypeResponse(any(VehicleType.class))).thenReturn(responseDTO);

        mockMvc.perform(post("/api/vehicle-types")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequestDTO)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(2L))
                .andExpect(jsonPath("$.name").value("SUV"))
                .andExpect(jsonPath("$.basePricePerDay").value(300.00));

        verify(vehicleTypeService).createVehicleType(any(VehicleType.class));
    }

    @Test
    @DisplayName("测试创建车型 - 名称已存在，返回400")
    void testCreateVehicleType_DuplicateName() throws Exception {
        when(dtoConverter.toVehicleTypeEntity(any(VehicleTypeRequestDTO.class))).thenReturn(sedanType);
        when(vehicleTypeService.createVehicleType(any(VehicleType.class)))
                .thenThrow(new BusinessException("车型名称已存在: SUV"));

        mockMvc.perform(post("/api/vehicle-types")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createRequestDTO)))
                .andExpect(status().isBadRequest());

        verify(vehicleTypeService).createVehicleType(any(VehicleType.class));
    }

    @Test
    @DisplayName("测试获取所有车型 - 成功")
    void testGetAllVehicleTypes_Success() throws Exception {
        VehicleType suvType = new VehicleType();
        suvType.setId(2L);
        suvType.setName("SUV");

        VehicleTypeResponseDTO suvDTO = new VehicleTypeResponseDTO();
        suvDTO.setId(2L);
        suvDTO.setName("SUV");

        List<VehicleType> types = Arrays.asList(sedanType, suvType);
        List<VehicleTypeResponseDTO> dtos = Arrays.asList(sedanDTO, suvDTO);

        when(vehicleTypeService.getAllVehicleTypes()).thenReturn(types);
        when(dtoConverter.toVehicleTypeResponseList(types)).thenReturn(dtos);

        mockMvc.perform(get("/api/vehicle-types")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].id").value(1L))
                .andExpect(jsonPath("$[1].id").value(2L));

        verify(vehicleTypeService).getAllVehicleTypes();
    }

    @Test
    @DisplayName("测试获取单个车型 - 成功")
    void testGetVehicleTypeById_Success() throws Exception {
        when(vehicleTypeService.getVehicleTypeById(1L)).thenReturn(sedanType);
        when(dtoConverter.toVehicleTypeResponse(sedanType)).thenReturn(sedanDTO);

        mockMvc.perform(get("/api/vehicle-types/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.name").value("经济型轿车"))
                .andExpect(jsonPath("$.basePricePerDay").value(150.00));

        verify(vehicleTypeService).getVehicleTypeById(1L);
    }

    @Test
    @DisplayName("测试获取单个车型 - 不存在，返回404")
    void testGetVehicleTypeById_NotFound() throws Exception {
        when(vehicleTypeService.getVehicleTypeById(999L))
                .thenThrow(new ResourceNotFoundException("车型", "id", 999L));

        mockMvc.perform(get("/api/vehicle-types/999")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());

        verify(vehicleTypeService).getVehicleTypeById(999L);
    }

    @Test
    @DisplayName("测试更新车型 - 成功")
    void testUpdateVehicleType_Success() throws Exception {
        VehicleType updatedType = new VehicleType();
        updatedType.setId(1L);
        updatedType.setName("经济型轿车(更新)");
        updatedType.setDescription("适合日常出行和城市通勤");
        updatedType.setBasePricePerDay(new BigDecimal("160.00"));
        updatedType.setAvailable(true);

        VehicleTypeResponseDTO updatedDTO = new VehicleTypeResponseDTO();
        updatedDTO.setId(1L);
        updatedDTO.setName("经济型轿车(更新)");
        updatedDTO.setDescription("适合日常出行和城市通勤");
        updatedDTO.setBasePricePerDay(new BigDecimal("160.00"));
        updatedDTO.setAvailable(true);

        when(dtoConverter.toVehicleTypeEntity(any(VehicleTypeRequestDTO.class))).thenReturn(updatedType);
        when(vehicleTypeService.updateVehicleType(eq(1L), any(VehicleType.class))).thenReturn(updatedType);
        when(dtoConverter.toVehicleTypeResponse(any(VehicleType.class))).thenReturn(updatedDTO);

        VehicleTypeRequestDTO updateRequest = new VehicleTypeRequestDTO();
        updateRequest.setName("经济型轿车(更新)");
        updateRequest.setDescription("适合日常出行和城市通勤");
        updateRequest.setBasePricePerDay(new BigDecimal("160.00"));
        updateRequest.setAvailable(true);

        mockMvc.perform(put("/api/vehicle-types/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.name").value("经济型轿车(更新)"))
                .andExpect(jsonPath("$.basePricePerDay").value(160.00));

        verify(vehicleTypeService).updateVehicleType(eq(1L), any(VehicleType.class));
    }

    @Test
    @DisplayName("测试删除车型 - 成功，返回204")
    void testDeleteVehicleType_Success() throws Exception {
        doNothing().when(vehicleTypeService).deleteVehicleType(1L);

        mockMvc.perform(delete("/api/vehicle-types/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNoContent());

        verify(vehicleTypeService).deleteVehicleType(1L);
    }

    @Test
    @DisplayName("测试删除车型 - 失败（存在车辆），返回400")
    void testDeleteVehicleType_HasVehicles() throws Exception {
        doThrow(new BusinessException("该车型下存在车辆，无法删除"))
                .when(vehicleTypeService).deleteVehicleType(1L);

        mockMvc.perform(delete("/api/vehicle-types/1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isBadRequest());

        verify(vehicleTypeService).deleteVehicleType(1L);
    }

    @Test
    @DisplayName("测试获取可用车型 - 成功")
    void testGetAvailableVehicleTypes_Success() throws Exception {
        VehicleType suvType = new VehicleType();
        suvType.setId(2L);
        suvType.setName("SUV");
        suvType.setAvailable(true);

        VehicleTypeResponseDTO suvDTO = new VehicleTypeResponseDTO();
        suvDTO.setId(2L);
        suvDTO.setName("SUV");
        suvDTO.setAvailable(true);

        List<VehicleType> types = Arrays.asList(sedanType, suvType);
        List<VehicleTypeResponseDTO> dtos = Arrays.asList(sedanDTO, suvDTO);

        when(vehicleTypeService.getAvailableVehicleTypes()).thenReturn(types);
        when(dtoConverter.toVehicleTypeResponseList(types)).thenReturn(dtos);

        mockMvc.perform(get("/api/vehicle-types/available")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(2));

        verify(vehicleTypeService).getAvailableVehicleTypes();
    }
}
