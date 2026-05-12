import pytest
import os
from PyPDF2 import PdfWriter, PdfReader


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时目录"""
    return tmp_path


@pytest.fixture
def sample_pdf(temp_dir):
    """创建一个简单的PDF文件用于测试（3页）"""
    pdf_path = temp_dir / "test.pdf"
    
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    
    return str(pdf_path)


@pytest.fixture
def sample_pdfs(temp_dir):
    """创建多个PDF文件用于测试合并（3个文件）"""
    pdf_paths = []
    for i in range(3):
        pdf_path = temp_dir / f"test_{i}.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        pdf_paths.append(str(pdf_path))
    return pdf_paths


@pytest.fixture
def large_pdf_100_pages(temp_dir):
    """创建100页的PDF文件用于性能测试"""
    pdf_path = temp_dir / "large_100_pages.pdf"
    
    writer = PdfWriter()
    for _ in range(100):
        writer.add_blank_page(width=612, height=792)
    
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    
    return str(pdf_path)


@pytest.fixture
def output_dir(temp_dir):
    """创建输出目录"""
    output_dir_path = temp_dir / "output"
    output_dir_path.mkdir(exist_ok=True)
    return str(output_dir_path)
