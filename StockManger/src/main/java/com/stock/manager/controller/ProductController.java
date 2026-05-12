package com.stock.manager.controller;

import com.stock.manager.common.ApiResponse;
import com.stock.manager.dto.ProductDTO;
import com.stock.manager.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/products")
@Tag(name = "商品管理", description = "商品的增删改查等基本操作接口")
public class ProductController {

    @Autowired
    private ProductService productService;

    @PostMapping
    @Operation(summary = "创建商品", description = "创建新的商品信息，商品编码唯一")
    public ResponseEntity<ApiResponse<ProductDTO>> createProduct(
            @Parameter(description = "商品信息DTO", required = true) 
            @Valid @RequestBody ProductDTO dto) {
        ProductDTO created = productService.createProduct(dto);
        return ResponseEntity.ok(ApiResponse.success("商品创建成功", created));
    }

    @GetMapping("/{id}")
    @Operation(summary = "根据ID查询商品", description = "根据商品ID获取商品详情")
    public ResponseEntity<ApiResponse<ProductDTO>> getProductById(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long id) {
        ProductDTO product = productService.getProductById(id);
        return ResponseEntity.ok(ApiResponse.success(product));
    }

    @GetMapping("/code/{productCode}")
    @Operation(summary = "根据编码查询商品", description = "根据商品编码获取商品详情")
    public ResponseEntity<ApiResponse<ProductDTO>> getProductByCode(
            @Parameter(description = "商品编码", required = true) 
            @PathVariable String productCode) {
        ProductDTO product = productService.getProductByCode(productCode);
        return ResponseEntity.ok(ApiResponse.success(product));
    }

    @GetMapping
    @Operation(summary = "查询所有商品", description = "获取所有商品列表")
    public ResponseEntity<ApiResponse<List<ProductDTO>>> getAllProducts() {
        List<ProductDTO> products = productService.getAllProducts();
        return ResponseEntity.ok(ApiResponse.success(products));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新商品", description = "根据ID更新商品信息")
    public ResponseEntity<ApiResponse<ProductDTO>> updateProduct(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long id,
            @Parameter(description = "更新的商品信息", required = true) 
            @Valid @RequestBody ProductDTO dto) {
        ProductDTO updated = productService.updateProduct(id, dto);
        return ResponseEntity.ok(ApiResponse.success("商品更新成功", updated));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除商品", description = "根据ID删除商品（逻辑删除）")
    public ResponseEntity<ApiResponse<Void>> deleteProduct(
            @Parameter(description = "商品ID", required = true) 
            @PathVariable Long id) {
        productService.deleteProduct(id);
        return ResponseEntity.ok(ApiResponse.success("商品删除成功", null));
    }
}
