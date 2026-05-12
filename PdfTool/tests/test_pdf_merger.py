import pytest
import allure
from PyPDF2 import PdfReader
from src.pdf_merger import PDFMerger


@allure.feature('PDF合并功能')
class TestPDFMerger:
    
    @allure.story('合并多个PDF文件')
    def test_merge_pdfs(self, sample_pdfs, temp_dir):
        """测试合并多个PDF文件"""
        merger = PDFMerger()
        output_path = str(temp_dir / "merged.pdf")
        
        merger.merge_pdfs(sample_pdfs, output_path)
        
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3
    
    @allure.story('合并空列表抛出异常')
    def test_merge_empty_list(self, temp_dir):
        """测试合并空列表抛出ValueError异常"""
        merger = PDFMerger()
        output_path = str(temp_dir / "merged.pdf")
        
        with pytest.raises(ValueError, match='输入文件列表不能为空'):
            merger.merge_pdfs([], output_path)
    
    @allure.story('文件不存在抛出异常')
    def test_nonexistent_file(self, temp_dir):
        """测试输入文件不存在时抛出异常"""
        merger = PDFMerger()
        output_path = str(temp_dir / "merged.pdf")
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            merger.merge_pdfs([nonexistent_file], output_path)
