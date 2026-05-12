import os
from PyPDF2 import PdfReader, PdfWriter


class PDFSecurity:
    """
    PDF加密解密处理器，用于PDF文件的加密和解密
    """
    
    def encrypt_pdf(self, input_path: str, output_path: str,
                    password: str) -> None:
        """
        加密PDF文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            password: 加密密码
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 密码为空
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if not password:
            raise ValueError('密码不能为空')
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        writer.encrypt(password)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def decrypt_pdf(self, input_path: str, output_path: str,
                    password: str) -> None:
        """
        解密PDF文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            password: 解密密码
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 密码为空或文件未加密
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        if not password:
            raise ValueError('密码不能为空')
        
        reader = PdfReader(input_path)
        
        if reader.is_encrypted:
            reader.decrypt(password)
        else:
            raise ValueError('PDF文件未加密')
        
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    def is_encrypted(self, input_path: str) -> bool:
        """
        检查PDF是否已加密
        
        Args:
            input_path: 输入PDF文件路径
            
        Returns:
            是否已加密
            
        Raises:
            FileNotFoundError: 输入文件不存在
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f'输入文件不存在: {input_path}')
        
        reader = PdfReader(input_path)
        return reader.is_encrypted
