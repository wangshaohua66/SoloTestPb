import os
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Tuple


class PDFSplitter:
    """
    PDF拆分器，用于将PDF文件按页码范围拆分
    """
    
    def split_by_range(self, input_path: str, output_path: str, 
                       start_page: int, end_page: int) -> None:
        """
        按页码范围拆分PDF
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            start_page: 起始页码（从1开始）
            end_page: 结束页码
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 页码范围不合法
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if start_page < 1:
            raise ValueError('起始页码必须大于等于1')
        
        if end_page < start_page:
            raise ValueError('结束页码必须大于等于起始页码')
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        start_idx = start_page - 1
        end_idx = min(end_page, len(reader.pages))
        
        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def split_into_single_pages(self, input_path: str, 
                                 output_prefix: str) -> List[str]:
        """
        将PDF拆分为单个页面文件
        
        Args:
            input_path: 输入PDF文件路径
            output_prefix: 输出文件前缀
            
        Returns:
            生成的文件路径列表
            
        Raises:
            FileNotFoundError: 输入文件不存在
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        reader = PdfReader(input_path)
        output_files = []
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = f"{output_prefix}_page_{i + 1}.pdf"
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            output_files.append(output_path)
        
        return output_files
