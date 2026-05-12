import pytest
import allure
import os
from src.pdf_text_extractor import PDFTextExtractor


@allure.feature('PDF文本提取功能')
class TestPDFTextExtractor:
    
    @allure.story('提取整个PDF文本')
    def test_extract_all_text(self, sample_pdf, temp_dir):
        """测试提取整个PDF的文本"""
        extractor = PDFTextExtractor()
        output_path = str(temp_dir / "output.txt")
        
        text = extractor.extract_text(sample_pdf, output_path)
        
        assert isinstance(text, str)
        assert os.path.exists(output_path)
    
    @allure.story('按页码范围提取文本')
    def test_extract_text_by_range(self, sample_pdf):
        """测试按页码范围提取文本"""
        extractor = PDFTextExtractor()
        
        text = extractor.extract_text(sample_pdf, start_page=1, end_page=2)
        
        assert isinstance(text, str)
    
    @allure.story('文件不存在抛出异常')
    def test_nonexistent_file(self, temp_dir):
        """测试输入文件不存在时抛出异常"""
        extractor = PDFTextExtractor()
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            extractor.extract_text(nonexistent_file)
    
    @allure.story('起始页码小于1抛出异常')
    def test_invalid_start_page(self, sample_pdf):
        """测试起始页码小于1时抛出异常"""
        extractor = PDFTextExtractor()
        
        with pytest.raises(ValueError, match='起始页码必须大于等于1'):
            extractor.extract_text(sample_pdf, start_page=0)
    
    @allure.story('结束页码小于起始页码抛出异常')
    def test_invalid_end_page(self, sample_pdf):
        """测试结束页码小于起始页码时抛出异常"""
        extractor = PDFTextExtractor()
        
        with pytest.raises(ValueError, match='结束页码必须大于等于起始页码'):
            extractor.extract_text(sample_pdf, start_page=2, end_page=1)