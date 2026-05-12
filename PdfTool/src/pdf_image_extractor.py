import os
from typing import List
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image


class PDFImageExtractor:
    """
    PDF图片提取器，用于从PDF中提取图片
    """
    
    def extract_images(self, input_path: str, output_dir: str,
                       start_page: int = None, end_page: int = None) -> List[str]:
        """
        从PDF中提取图片
        
        Args:
            input_path: 输入PDF文件路径
            output_dir: 输出图片目录
            start_page: 起始页码（从1开始，可选）
            end_page: 结束页码（可选）
            
        Returns:
            提取的图片文件路径列表
            
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
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        start_idx = (start_page - 1) if start_page else 0
        end_idx = end_page if end_page else total_pages
        
        image_files = []
        image_count = 0
        
        for page_num in range(start_idx, min(end_idx, total_pages)):
            page = reader.pages[page_num]
            
            try:
                resources = page['/Resources'].get_object()
                if '/XObject' in resources:
                    x_object = resources['/XObject'].get_object()
                    
                    for obj in x_object:
                        try:
                            obj_data = x_object[obj].get_object()
                            if obj_data.get('/Subtype') == '/Image':
                                size = (obj_data['/Width'], obj_data['/Height'])
                                data = obj_data._data
                                
                                filter_obj = obj_data.get('/Filter', '')
                                if isinstance(filter_obj, list):
                                    filter_type = str(filter_obj[0]) if filter_obj else ''
                                else:
                                    filter_type = str(filter_obj)
                                
                                if filter_type == '/DCTDecode':
                                    ext = 'jpg'
                                elif filter_type == '/JPXDecode':
                                    ext = 'jp2'
                                elif filter_type == '/CCITTFaxDecode':
                                    ext = 'tiff'
                                else:
                                    ext = 'png'
                                
                                image_path = os.path.join(
                                    output_dir, 
                                    f'image_page_{page_num + 1}_{image_count + 1}.{ext}'
                                )
                                
                                with open(image_path, 'wb') as f:
                                    f.write(data)
                                
                                image_files.append(image_path)
                                image_count += 1
                        except (KeyError, Exception):
                            continue
            except (KeyError, Exception):
                continue
        
        return image_files
    
    def convert_to_images(self, input_path: str, output_dir: str,
                          start_page: int = None, end_page: int = None,
                          dpi: int = 200) -> List[str]:
        """
        将PDF页面转换为图片
        
        Args:
            input_path: 输入PDF文件路径
            output_dir: 输出图片目录
            start_page: 起始页码（从1开始，可选）
            end_page: 结束页码（可选）
            dpi: 图片分辨率
            
        Returns:
            转换后的图片文件路径列表
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 参数不合法
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if start_page is not None and start_page < 1:
            raise ValueError('起始页码必须大于等于1')
        
        if end_page is not None and start_page is not None and end_page < start_page:
            raise ValueError('结束页码必须大于等于起始页码')
        
        if dpi < 1:
            raise ValueError('DPI必须大于等于1')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        first_page = start_page if start_page else 1
        last_page = end_page if end_page else total_pages
        
        images = convert_from_path(
            input_path,
            first_page=first_page,
            last_page=last_page,
            dpi=dpi
        )
        
        image_files = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(
                output_dir, 
                f'page_{first_page + i}.png'
            )
            image.save(image_path, 'PNG')
            image_files.append(image_path)
        
        return image_files
