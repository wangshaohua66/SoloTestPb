package com.stock.manager.service;

import com.stock.manager.dto.ProductDTO;
import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.InventoryRepository;
import com.stock.manager.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@ActiveProfiles("test")
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private InventoryRepository inventoryRepository;

    @InjectMocks
    private ProductService productService;

    private ProductDTO productDTO;
    private Product product;

    @BeforeEach
    void setUp() {
        productDTO = new ProductDTO();
        productDTO.setProductCode("P001");
        productDTO.setProductName("测试商品");
        productDTO.setCategory("电子产品");
        productDTO.setUnit("个");
        productDTO.setUnitPrice(new BigDecimal("100.00"));
        productDTO.setMinStock(10);
        productDTO.setMaxStock(100);

        product = new Product();
        product.setId(1L);
        product.setProductCode("P001");
        product.setProductName("测试商品");
        product.setUnitPrice(new BigDecimal("100.00"));
    }

    @Test
    @DisplayName("创建商品 - 成功")
    void createProduct_Success() {
        when(productRepository.existsByProductCode("P001")).thenReturn(false);
        when(productRepository.save(any(Product.class))).thenReturn(product);

        ProductDTO result = productService.createProduct(productDTO);

        assertNotNull(result);
        assertEquals("P001", result.getProductCode());
        assertEquals("测试商品", result.getProductName());
        verify(inventoryRepository, times(1)).save(any(Inventory.class));
    }

    @Test
    @DisplayName("创建商品 - 编码已存在")
    void createProduct_DuplicateCode() {
        when(productRepository.existsByProductCode("P001")).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> productService.createProduct(productDTO));
    }

    @Test
    @DisplayName("根据ID获取商品 - 成功")
    void getProductById_Success() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        ProductDTO result = productService.getProductById(1L);

        assertNotNull(result);
        assertEquals("P001", result.getProductCode());
    }

    @Test
    @DisplayName("根据ID获取商品 - 不存在")
    void getProductById_NotFound() {
        when(productRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> productService.getProductById(1L));
    }

    @Test
    @DisplayName("获取所有商品 - 成功")
    void getAllProducts_Success() {
        Product product2 = new Product();
        product2.setId(2L);
        product2.setProductCode("P002");
        product2.setProductName("测试商品2");

        when(productRepository.findAll()).thenReturn(Arrays.asList(product, product2));

        List<ProductDTO> result = productService.getAllProducts();

        assertEquals(2, result.size());
    }

    @Test
    @DisplayName("更新商品 - 成功")
    void updateProduct_Success() {
        ProductDTO updateDTO = new ProductDTO();
        updateDTO.setProductCode("P001");
        updateDTO.setProductName("更新后商品");
        updateDTO.setUnitPrice(new BigDecimal("150.00"));

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(productRepository.save(any(Product.class))).thenAnswer(invocation -> invocation.getArgument(0));

        ProductDTO result = productService.updateProduct(1L, updateDTO);

        assertNotNull(result);
        assertEquals("更新后商品", result.getProductName());
        assertEquals(new BigDecimal("150.00"), result.getUnitPrice());
    }

    @Test
    @DisplayName("删除商品 - 成功（库存为0")
    void deleteProduct_Success() {
        Inventory inventory = new Inventory();
        inventory.setQuantity(0);

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(inventoryRepository.findByProduct(product)).thenReturn(Optional.of(inventory));

        productService.deleteProduct(1L);

        verify(inventoryRepository, times(1)).delete(inventory);
        verify(productRepository, times(1)).delete(product);
    }

    @Test
    @DisplayName("删除商品 - 失败（有库存）")
    void deleteProduct_Fail_WithStock() {
        Inventory inventory = new Inventory();
        inventory.setQuantity(10);

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(inventoryRepository.findByProduct(product)).thenReturn(Optional.of(inventory));

        assertThrows(IllegalStateException.class, () -> productService.deleteProduct(1L));
    }
}
