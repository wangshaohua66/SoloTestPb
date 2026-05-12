package com.stock.manager.service;

import com.stock.manager.dto.ProductDTO;
import com.stock.manager.entity.Inventory;
import com.stock.manager.entity.Product;
import com.stock.manager.exception.ResourceNotFoundException;
import com.stock.manager.repository.InventoryRepository;
import com.stock.manager.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class ProductService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Transactional
    public ProductDTO createProduct(ProductDTO dto) {
        if (productRepository.existsByProductCode(dto.getProductCode())) {
            throw new IllegalArgumentException("商品编码已存在: " + dto.getProductCode());
        }

        Product product = convertToEntity(dto);
        product = productRepository.save(product);

        Inventory inventory = new Inventory();
        inventory.setProduct(product);
        inventory.setQuantity(0);
        inventoryRepository.save(inventory);

        return convertToDTO(product);
    }

    @Transactional(readOnly = true)
    public ProductDTO getProductById(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + id));
        return convertToDTO(product);
    }

    @Transactional(readOnly = true)
    public ProductDTO getProductByCode(String productCode) {
        Product product = productRepository.findByProductCode(productCode)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + productCode));
        return convertToDTO(product);
    }

    @Transactional(readOnly = true)
    public List<ProductDTO> getAllProducts() {
        return productRepository.findAll().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional
    public ProductDTO updateProduct(Long id, ProductDTO dto) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + id));

        if (!product.getProductCode().equals(dto.getProductCode())) {
            if (productRepository.existsByProductCode(dto.getProductCode())) {
                throw new IllegalArgumentException("商品编码已存在: " + dto.getProductCode());
            }
        }

        product.setProductCode(dto.getProductCode());
        product.setProductName(dto.getProductName());
        product.setCategory(dto.getCategory());
        product.setUnit(dto.getUnit());
        product.setUnitPrice(dto.getUnitPrice());
        product.setMinStock(dto.getMinStock());
        product.setMaxStock(dto.getMaxStock());
        product.setDescription(dto.getDescription());

        product = productRepository.save(product);
        return convertToDTO(product);
    }

    @Transactional
    public void deleteProduct(Long id) {
        Product product = productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("商品不存在: " + id));

        Optional<Inventory> inventoryOpt = inventoryRepository.findByProduct(product);
        if (inventoryOpt.isPresent()) {
            Inventory inventory = inventoryOpt.get();
            if (inventory.getQuantity() > 0) {
                throw new IllegalStateException("商品存在库存，无法删除");
            }
            inventoryRepository.delete(inventory);
        }

        productRepository.delete(product);
    }

    private Product convertToEntity(ProductDTO dto) {
        Product product = new Product();
        product.setProductCode(dto.getProductCode());
        product.setProductName(dto.getProductName());
        product.setCategory(dto.getCategory());
        product.setUnit(dto.getUnit());
        product.setUnitPrice(dto.getUnitPrice());
        product.setMinStock(dto.getMinStock());
        product.setMaxStock(dto.getMaxStock());
        product.setDescription(dto.getDescription());
        return product;
    }

    private ProductDTO convertToDTO(Product product) {
        ProductDTO dto = new ProductDTO();
        dto.setId(product.getId());
        dto.setProductCode(product.getProductCode());
        dto.setProductName(product.getProductName());
        dto.setCategory(product.getCategory());
        dto.setUnit(product.getUnit());
        dto.setUnitPrice(product.getUnitPrice());
        dto.setMinStock(product.getMinStock());
        dto.setMaxStock(product.getMaxStock());
        dto.setDescription(product.getDescription());
        return dto;
    }
}
