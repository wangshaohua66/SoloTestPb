import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


class PDFHeaderFooter:
    """
    PDF页码、页眉页脚处理器，用于给PDF添加页码、页眉和页脚
    """
    
    def add_page_numbers(self, input_path: str, output_path: str,
                         position: str = 'bottom_right',
                         font_size: int = 12,
                         start_num: int = 1) -> None:
        """
        给PDF添加页码
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            position: 页码位置，可选：'bottom_left', 'bottom_center', 'bottom_right',
                     'top_left', 'top_center', 'top_right'
            font_size: 字体大小
            start_num: 起始页码
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 参数不合法
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if font_size < 1:
            raise ValueError('字体大小必须大于等于1')
        
        if start_num < 1:
            raise ValueError('起始页码必须大于等于1')
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            page_num = i + start_num
            
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont('Helvetica', font_size)
            
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            x, y = self._get_position(position, page_width, page_height)
            
            can.drawString(x, y, str(page_num))
            can.save()
            
            packet.seek(0)
            new_pdf = PdfReader(packet)
            page.merge_page(new_pdf.pages[0])
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def add_header_footer(self, input_path: str, output_path: str,
                          header_text: str = '',
                          footer_text: str = '',
                          font_size: int = 10) -> None:
        """
        给PDF添加页眉和页脚
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            header_text: 页眉文本
            footer_text: 页脚文本
            font_size: 字体大小
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 参数不合法
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if font_size < 1:
            raise ValueError('字体大小必须大于等于1')
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont('Helvetica', font_size)
            
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            if header_text:
                can.drawCentredString(page_width / 2, page_height - 30, header_text)
            
            if footer_text:
                can.drawCentredString(page_width / 2, 30, footer_text)
            
            can.save()
            
            packet.seek(0)
            new_pdf = PdfReader(packet)
            page.merge_page(new_pdf.pages[0])
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def _get_position(self, position: str, width: float, height: float) -> tuple:
        """
        根据位置名称获取坐标
        
        Args:
            position: 位置名称
            width: 页面宽度
            height: 页面高度
            
        Returns:
            (x, y) 坐标
        """
        margin = 30
        
        positions = {
            'bottom_left': (margin, margin),
            'bottom_center': (width / 2, margin),
            'bottom_right': (width - margin, margin),
            'top_left': (margin, height - margin),
            'top_center': (width / 2, height - margin),
            'top_right': (width - margin, height - margin)
        }
        
        return positions.get(position, positions['bottom_right'])
