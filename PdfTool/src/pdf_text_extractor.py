import os
import pdfplumber
from typing import Optional


class PDFTextExtractor:
    """
    PDF文本提取器，用于从PDF中提取文本内容
    """
    
    def extract_text(self, input_path: str, output_path: Optional[str] = None,
                     start_page: Optional[int] = None, 
                     end_page: Optional[int] = None) -> str:
        """
        从PDF中提取文本
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出TXT文件路径（可选）
            start_page: 起始页码（从1开始，可选）
            end_page: 结束页码（可选）
            
        Returns:
            提取的文本内容
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 页码范围不合法
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if start_page is not None and start_page < 1:
            raise ValueError('起始页码必须大于等于1')
        
        if end_page is not None and start_page is not None and end_page < start_page:
            raise ValueError('结束页码必须大于等于起始页码')
        
        all_text = []
        
        with pdfplumber.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            start_idx = (start_page - 1) if start_page else 0
            end_idx = end_page if end_page else total_pages
            
            for i in range(start_idx, min(end_idx, total_pages)):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    all_text.append(text)
        
        result = '\n\n'.join(all_text)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        
        return result
