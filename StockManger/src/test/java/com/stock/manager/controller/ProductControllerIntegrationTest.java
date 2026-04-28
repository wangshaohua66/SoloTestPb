package com.stock.manager.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stock.manager.dto.ProductDTO;
import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.repository.InventoryRepository;
import com.stock.manager.repository.ProductRepository;
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

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_CLASS)
class ProductControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    private Product product;

    @BeforeEach
    void setUp() {
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
    @DisplayName("创建商品 - POST /api/products")
    void createProduct_ShouldReturnCreatedProduct() throws Exception {
        ProductDTO dto = new ProductDTO();
        dto.setProductCode("P002");
        dto.setProductName("新商品");
        dto.setCategory("电子产品");
        dto.setUnit("个");
        dto.setUnitPrice(new BigDecimal("200.00"));

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data.productCode", is("P002")))
                .andExpect(jsonPath("$.data.productName", is("新商品")));
    }

    @Test
    @DisplayName("创建商品 - 编码已存在")
    void createProduct_DuplicateCode_ShouldReturnError() throws Exception {
        ProductDTO dto = new ProductDTO();
        dto.setProductCode("P001");
        dto.setProductName("重复商品");
        dto.setUnitPrice(new BigDecimal("150.00"));

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success", is(false)));
    }

    @Test
    @DisplayName("根据ID获取商品 - GET /api/products/{id}")
    void getProductById_ShouldReturnProduct() throws Exception {
        mockMvc.perform(get("/api/products/{id}", product.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data.id", is(product.getId().intValue())))
                .andExpect(jsonPath("$.data.productCode", is("P001")));
    }

    @Test
    @DisplayName("根据ID获取商品 - 不存在")
    void getProductById_NotFound_ShouldReturnError() throws Exception {
        mockMvc.perform(get("/api/products/{id}", 999L))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success", is(false)));
    }

    @Test
    @DisplayName("获取所有商品 - GET /api/products")
    void getAllProducts_ShouldReturnProductList() throws Exception {
        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(1)));
    }

    @Test
    @DisplayName("更新商品 - PUT /api/products/{id}")
    void updateProduct_ShouldReturnUpdatedProduct() throws Exception {
        ProductDTO dto = new ProductDTO();
        dto.setProductCode("P001");
        dto.setProductName("更新后商品");
        dto.setUnitPrice(new BigDecimal("150.00"));

        mockMvc.perform(put("/api/products/{id}", product.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data.productName", is("更新后商品")))
                .andExpect(jsonPath("$.data.unitPrice", is(150.00)));
    }

    @Test
    @DisplayName("删除商品 - DELETE /api/products/{id}")
    void deleteProduct_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(delete("/api/products/{id}", product.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)));
    }

    @Test
    @DisplayName("创建商品 - 参数验证失败")
    void createProduct_ValidationError_ShouldReturnErrors() throws Exception {
        ProductDTO dto = new ProductDTO();

        mockMvc.perform(post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.success", is(true)));
    }
}
