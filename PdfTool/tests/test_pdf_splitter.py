import pytest
import allure
from PyPDF2 import PdfReader
from src.pdf_splitter import PDFSplitter


@allure.feature('PDF拆分功能')
class TestPDFSplitter:
    
    @allure.story('按页码范围拆分PDF')
    def test_split_by_range(self, sample_pdf, temp_dir):
        """测试按页码范围拆分PDF"""
        splitter = PDFSplitter()
        output_path = str(temp_dir / "splitted.pdf")
        
        splitter.split_by_range(sample_pdf, output_path, 1, 2)
        
        reader = PdfReader(output_path)
        assert len(reader.pages) == 2
    
    @allure.story('超出页码范围的拆分')
    def test_split_out_of_range(self, sample_pdf, temp_dir):
        """测试超出页码范围的拆分"""
        splitter = PDFSplitter()
        output_path = str(temp_dir / "splitted.pdf")
        
        splitter.split_by_range(sample_pdf, output_path, 1, 10)
        
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3
    
    @allure.story('拆分为单页文件')
    def test_split_into_single_pages(self, sample_pdf, temp_dir):
        """测试拆分为单页文件"""
        splitter = PDFSplitter()
        output_prefix = str(temp_dir / "page")
        
        output_files = splitter.split_into_single_pages(sample_pdf, output_prefix)
        
        assert len(output_files) == 3
        for path in output_files:
            reader = PdfReader(path)
            assert len(reader.pages) == 1
