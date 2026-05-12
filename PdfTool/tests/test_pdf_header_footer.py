import pytest
import allure
import os
from PyPDF2 import PdfReader
from src.pdf_header_footer import PDFHeaderFooter


@allure.feature('PDF页眉页脚功能')
class TestPDFHeaderFooter:
    
    @allure.story('添加页码')
    def test_add_page_numbers(self, sample_pdf, temp_dir):
        """测试给PDF添加页码"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "with_numbers.pdf")
        
        processor.add_page_numbers(sample_pdf, output_path)
        
        assert os.path.exists(output_path)
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3
    
    @allure.story('添加页眉页脚')
    def test_add_header_footer(self, sample_pdf, temp_dir):
        """测试给PDF添加页眉页脚"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "with_header.pdf")
        
        processor.add_header_footer(
            sample_pdf, 
            output_path,
            header_text='测试页眉',
            footer_text='测试页脚'
        )
        
        assert os.path.exists(output_path)
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3
    
    @allure.story('文件不存在抛出异常')
    def test_nonexistent_file(self, temp_dir):
        """测试输入文件不存在时抛出异常"""
        processor = PDFHeaderFooter()
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            processor.add_page_numbers(nonexistent_file, output_path)
    
    @allure.story('字体大小小于1抛出异常')
    def test_invalid_font_size(self, sample_pdf, temp_dir):
        """测试字体大小小于1时抛出异常"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(ValueError, match='字体大小必须大于等于1'):
            processor.add_page_numbers(sample_pdf, output_path, font_size=0)
    
    @allure.story('起始页码小于1抛出异常')
    def test_invalid_start_num(self, sample_pdf, temp_dir):
        """测试起始页码小于1时抛出异常"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "output.pdf")
        
        with pytest.raises(ValueError, match='起始页码必须大于等于1'):
            processor.add_page_numbers(sample_pdf, output_path, start_num=0)