import pytest
import allure
import time
import os
from PyPDF2 import PdfReader
from src.pdf_merger import PDFMerger
from src.pdf_splitter import PDFSplitter
from src.pdf_text_extractor import PDFTextExtractor
from src.pdf_image_extractor import PDFImageExtractor
from src.pdf_header_footer import PDFHeaderFooter
from src.pdf_security import PDFSecurity


@allure.feature('性能测试')
@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """
    性能测试类，验证100页PDF处理时间不超过30秒
    """
    
    PERFORMANCE_THRESHOLD = 30  # 30秒
    
    @allure.story('合并PDF性能测试')
    def test_merge_performance(self, large_pdf_100_pages, temp_dir):
        """测试合并PDF性能 - 合并多个100页PDF"""
        merger = PDFMerger()
        output_path = str(temp_dir / "merged_perf.pdf")
        
        # 创建3个100页PDF文件用于合并
        pdfs_to_merge = [large_pdf_100_pages, large_pdf_100_pages, large_pdf_100_pages]
        
        start_time = time.time()
        merger.merge_pdfs(pdfs_to_merge, output_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        reader = PdfReader(output_path)
        assert len(reader.pages) == 300
        
        print(f"\n合并PDF性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"合并PDF耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('拆分PDF性能测试')
    def test_split_performance(self, large_pdf_100_pages, temp_dir):
        """测试拆分PDF性能"""
        splitter = PDFSplitter()
        output_path = str(temp_dir / "splitted_perf.pdf")
        
        start_time = time.time()
        splitter.split_by_range(large_pdf_100_pages, output_path, 1, 50)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        reader = PdfReader(output_path)
        assert len(reader.pages) == 50
        
        print(f"\n拆分PDF性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"拆分PDF耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('提取文本性能测试')
    def test_extract_text_performance(self, large_pdf_100_pages, temp_dir):
        """测试提取文本性能"""
        extractor = PDFTextExtractor()
        output_path = str(temp_dir / "text_perf.txt")
        
        start_time = time.time()
        text = extractor.extract_text(large_pdf_100_pages, output_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        assert isinstance(text, str)
        
        print(f"\n提取文本性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"提取文本耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('添加页码性能测试')
    def test_add_page_numbers_performance(self, large_pdf_100_pages, temp_dir):
        """测试添加页码性能"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "with_numbers_perf.pdf")
        
        start_time = time.time()
        processor.add_page_numbers(large_pdf_100_pages, output_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        
        print(f"\n添加页码性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"添加页码耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('添加页眉页脚性能测试')
    def test_add_header_footer_performance(self, large_pdf_100_pages, temp_dir):
        """测试添加页眉页脚性能"""
        processor = PDFHeaderFooter()
        output_path = str(temp_dir / "with_header_perf.pdf")
        
        start_time = time.time()
        processor.add_header_footer(
            large_pdf_100_pages, 
            output_path,
            header_text='测试页眉',
            footer_text='测试页脚'
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        
        print(f"\n添加页眉页脚性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"添加页眉页脚耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('加密PDF性能测试')
    def test_encrypt_performance(self, large_pdf_100_pages, temp_dir):
        """测试加密PDF性能"""
        security = PDFSecurity()
        output_path = str(temp_dir / "encrypted_perf.pdf")
        
        start_time = time.time()
        security.encrypt_pdf(large_pdf_100_pages, output_path, password="test123")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert os.path.exists(output_path)
        assert security.is_encrypted(output_path) is True
        
        print(f"\n加密PDF性能测试: {processing_time:.2f}秒")
        assert processing_time < self.PERFORMANCE_THRESHOLD, \
            f"加密PDF耗时 {processing_time:.2f}秒，超过阈值 {self.PERFORMANCE_THRESHOLD}秒"
    
    @allure.story('PDF页面数验证')
    def test_large_pdf_page_count(self, large_pdf_100_pages):
        """验证测试用的PDF确实有100页"""
        reader = PdfReader(large_pdf_100_pages)
        assert len(reader.pages) == 100
