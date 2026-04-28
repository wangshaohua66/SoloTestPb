package com.stock.manager.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stock.manager.dto.StockInDTO;
import com.stock.manager.dto.StockOutDTO;
import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.entity.StockIn;
import com.stock.manager.entity.StockOut;
import com.stock.manager.entity.StockTransaction;
import com.stock.manager.entity.StockWarning;
import com.stock.manager.entity.CheckRecord;
import com.stock.manager.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_CLASS)
class StockManagementIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private StockInRepository stockInRepository;

    @Autowired
    private StockOutRepository stockOutRepository;

    @Autowired
    private StockTransactionRepository stockTransactionRepository;

    @Autowired
    private StockWarningRepository stockWarningRepository;

    @Autowired
    private CheckRecordRepository checkRecordRepository;

    private Product product;

    @BeforeEach
    void setUp() {
        checkRecordRepository.deleteAll();
        stockWarningRepository.deleteAll();
        stockTransactionRepository.deleteAll();
        stockOutRepository.deleteAll();
        stockInRepository.deleteAll();
        inventoryRepository.deleteAll();
        productRepository.deleteAll();

        product = new Product();
        product.setProductCode("P001");
        product.setProductName("测试商品");
        product.setCategory("电子产品");
        product.setUnit("个");
        product.setUnitPrice(new BigDecimal("100.00"));
        product.setMinStock(10);
        product.setMaxStock(100);
        product = productRepository.save(product);

        Inventory inventory = new Inventory();
        inventory.setProduct(product);
        inventory.setQuantity(0);
        inventoryRepository.save(inventory);
    }

    @Test
    @DisplayName("入库操作 - POST /api/stock-in")
    void stockIn_ShouldIncreaseInventory() throws Exception {
        StockInDTO dto = new StockInDTO();
        dto.setInType("PURCHASE");
        dto.setSupplier("供应商A");
        dto.setWarehouse("主仓库");
        dto.setOperator("admin");

        List<StockInDTO.StockInItemDTO> items = new ArrayList<>();
        StockInDTO.StockInItemDTO item = new StockInDTO.StockInItemDTO();
        item.setProductId(product.getId());
        item.setQuantity(50);
        item.setUnitPrice(new BigDecimal("90.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-in")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data.totalQuantity", is(50)));

        mockMvc.perform(get("/api/inventory/product/{productId}", product.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.quantity", is(50)));
    }

    @Test
    @DisplayName("出库操作 - POST /api/stock-out")
    void stockOut_ShouldDecreaseInventory() throws Exception {
        Inventory inventory = inventoryRepository.findByProductId(product.getId()).get();
        inventory.setQuantity(100);
        inventoryRepository.save(inventory);

        StockOutDTO dto = new StockOutDTO();
        dto.setOutType("SALE");
        dto.setCustomer("客户A");
        dto.setWarehouse("主仓库");
        dto.setOperator("admin");

        List<StockOutDTO.StockOutItemDTO> items = new ArrayList<>();
        StockOutDTO.StockOutItemDTO item = new StockOutDTO.StockOutItemDTO();
        item.setProductId(product.getId());
        item.setQuantity(30);
        item.setUnitPrice(new BigDecimal("150.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-out")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data.totalQuantity", is(30)));

        mockMvc.perform(get("/api/inventory/product/{productId}", product.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.quantity", is(70)));
    }

    @Test
    @DisplayName("出库操作 - 库存不足")
    void stockOut_InsufficientStock_ShouldReturnError() throws Exception {
        Inventory inventory = inventoryRepository.findByProductId(product.getId()).get();
        inventory.setQuantity(10);
        inventoryRepository.save(inventory);

        StockOutDTO dto = new StockOutDTO();
        dto.setOutType("SALE");
        dto.setOperator("admin");

        List<StockOutDTO.StockOutItemDTO> items = new ArrayList<>();
        StockOutDTO.StockOutItemDTO item = new StockOutDTO.StockOutItemDTO();
        item.setProductId(product.getId());
        item.setQuantity(50);
        item.setUnitPrice(new BigDecimal("150.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-out")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.success", is(false)));
    }

    @Test
    @DisplayName("库存预警 - 低于下限")
    void stockIn_LowStock_ShouldTriggerWarning() throws Exception {
        Product productWithLowLimit = new Product();
        productWithLowLimit.setProductCode("P002");
        productWithLowLimit.setProductName("低库存预警商品");
        productWithLowLimit.setUnitPrice(new BigDecimal("50.00"));
        productWithLowLimit.setMinStock(20);
        productWithLowLimit = productRepository.save(productWithLowLimit);

        Inventory inventory = new Inventory();
        inventory.setProduct(productWithLowLimit);
        inventory.setQuantity(10);
        inventoryRepository.save(inventory);

        StockInDTO dto = new StockInDTO();
        dto.setInType("PURCHASE");
        dto.setOperator("admin");

        List<StockInDTO.StockInItemDTO> items = new ArrayList<>();
        StockInDTO.StockInItemDTO item = new StockInDTO.StockInItemDTO();
        item.setProductId(productWithLowLimit.getId());
        item.setQuantity(5);
        item.setUnitPrice(new BigDecimal("40.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-in")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)));

        mockMvc.perform(get("/api/warnings/low-stock"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)));
    }

    @Test
    @DisplayName("获取所有库存列表")
    void getAllInventory_ShouldReturnInventoryList() throws Exception {
        mockMvc.perform(get("/api/inventory"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(greaterThan(0))));
    }

    @Test
    @DisplayName("获取入库记录列表")
    void getAllStockIn_ShouldReturnList() throws Exception {
        StockInDTO dto = new StockInDTO();
        dto.setInType("PURCHASE");
        dto.setOperator("admin");
        List<StockInDTO.StockInItemDTO> items = new ArrayList<>();
        StockInDTO.StockInItemDTO item = new StockInDTO.StockInItemDTO();
        item.setProductId(product.getId());
        item.setQuantity(10);
        item.setUnitPrice(new BigDecimal("90.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-in")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/stock-in"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(greaterThan(0))));
    }

    @Test
    @DisplayName("获取出库记录列表")
    void getAllStockOut_ShouldReturnList() throws Exception {
        Inventory inventory = inventoryRepository.findByProductId(product.getId()).get();
        inventory.setQuantity(100);
        inventoryRepository.save(inventory);

        StockOutDTO dto = new StockOutDTO();
        dto.setOutType("SALE");
        dto.setOperator("admin");
        List<StockOutDTO.StockOutItemDTO> items = new ArrayList<>();
        StockOutDTO.StockOutItemDTO item = new StockOutDTO.StockOutItemDTO();
        item.setProductId(product.getId());
        item.setQuantity(10);
        item.setUnitPrice(new BigDecimal("150.00"));
        items.add(item);
        dto.setItems(items);

        mockMvc.perform(post("/api/stock-out")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/stock-out"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(greaterThan(0))));
    }
}
