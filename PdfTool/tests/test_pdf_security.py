import pytest
import allure
import os
from src.pdf_security import PDFSecurity


@allure.feature('PDF加密解密功能')
class TestPDFSecurity:
    
    @allure.story('加密PDF文件')
    def test_encrypt_pdf(self, sample_pdf, temp_dir):
        """测试加密PDF文件"""
        security = PDFSecurity()
        encrypted_path = str(temp_dir / "encrypted.pdf")
        
        security.encrypt_pdf(sample_pdf, encrypted_path, password="test123")
        
        assert os.path.exists(encrypted_path)
        assert security.is_encrypted(encrypted_path) is True
    
    @allure.story('解密PDF文件')
    def test_decrypt_pdf(self, sample_pdf, temp_dir):
        """测试解密PDF文件"""
        security = PDFSecurity()
        encrypted_path = str(temp_dir / "encrypted.pdf")
        decrypted_path = str(temp_dir / "decrypted.pdf")
        
        security.encrypt_pdf(sample_pdf, encrypted_path, password="test123")
        security.decrypt_pdf(encrypted_path, decrypted_path, password="test123")
        
        assert os.path.exists(decrypted_path)
    
    @allure.story('文件不存在抛出异常')
    def test_nonexistent_file(self, temp_dir):
        """测试输入文件不存在时抛出异常"""
        security = PDFSecurity()
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            security.encrypt_pdf(nonexistent_file, output_path, password="test")
    
    @allure.story('密码为空抛出异常')
    def test_empty_password(self, sample_pdf, temp_dir):
        """测试密码为空时抛出异常"""
        security = PDFSecurity()
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(ValueError, match='密码不能为空'):
            security.encrypt_pdf(sample_pdf, output_path, password="")
    
    @allure.story('解密未加密文件抛出异常')
    def test_decrypt_unencrypted(self, sample_pdf, temp_dir):
        """测试解密未加密文件时抛出异常"""
        security = PDFSecurity()
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(ValueError, match='PDF文件未加密'):
            security.decrypt_pdf(sample_pdf, output_path, password="test")