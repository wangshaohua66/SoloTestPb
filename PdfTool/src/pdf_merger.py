import os
from PyPDF2 import PdfReader, PdfWriter
from typing import List


class PDFMerger:
    """
    PDF合并器，用于将多个PDF文件合并为一个文件
    """
    
    def merge_pdfs(self, input_paths: List[str], output_path: str) -> None:
        """
        合并多个PDF文件
        
        Args:
            input_paths: 输入PDF文件路径列表
            output_path: 输出PDF文件路径
            
        Raises:
            ValueError: 输入文件列表为空
            FileNotFoundError: 输入文件不存在
        """
        if not input_paths:
            raise ValueError('输入文件列表不能为空')
        
        for path in input_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f'输入文件不存在: {path}')
        
        writer = PdfWriter()
        
        for path in input_paths:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
