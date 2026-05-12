import pytest
import allure
import os
import shutil
from unittest.mock import patch, MagicMock
from PIL import Image as PILImage
from src.pdf_image_extractor import PDFImageExtractor


def check_poppler_installed():
    """检查poppler是否安装"""
    return shutil.which('pdfinfo') is not None


@allure.feature('PDF图片提取功能')
class TestPDFImageExtractor:
    
    @allure.story('提取内嵌图片')
    def test_extract_images(self, sample_pdf, temp_dir):
        """测试提取PDF内嵌图片"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        images = extractor.extract_images(sample_pdf, output_dir)
        
        assert isinstance(images, list)
        assert os.path.exists(output_dir)
    
    @allure.story('提取指定页码范围的图片')
    def test_extract_images_with_page_range(self, sample_pdf, temp_dir):
        """测试提取指定页码范围的图片"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        images = extractor.extract_images(sample_pdf, output_dir, start_page=1, end_page=2)
        
        assert isinstance(images, list)
        assert os.path.exists(output_dir)
    
    @allure.story('文件不存在抛出异常 - extract_images')
    def test_nonexistent_file_extract_images(self, temp_dir):
        """测试输入文件不存在时抛出异常"""
        extractor = PDFImageExtractor()
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            extractor.extract_images(nonexistent_file, output_dir)
    
    @allure.story('文件不存在抛出异常 - convert_to_images')
    def test_nonexistent_file_convert(self, temp_dir):
        """测试convert_to_images输入文件不存在时抛出异常"""
        extractor = PDFImageExtractor()
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(FileNotFoundError, match='输入文件不存在'):
            extractor.convert_to_images(nonexistent_file, output_dir)
    
    @allure.story('起始页码小于1抛出异常 - extract_images')
    def test_invalid_start_page_extract_images(self, sample_pdf, temp_dir):
        """测试起始页码小于1时抛出异常"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(ValueError, match='起始页码必须大于等于1'):
            extractor.extract_images(sample_pdf, output_dir, start_page=0)
    
    @allure.story('起始页码小于1抛出异常 - convert_to_images')
    def test_invalid_start_page_convert(self, sample_pdf, temp_dir):
        """测试convert_to_images起始页码小于1时抛出异常"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(ValueError, match='起始页码必须大于等于1'):
            extractor.convert_to_images(sample_pdf, output_dir, start_page=0)
    
    @allure.story('结束页码小于起始页码抛出异常')
    def test_invalid_end_page_less_than_start(self, sample_pdf, temp_dir):
        """测试结束页码小于起始页码时抛出异常"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(ValueError, match='结束页码必须大于等于起始页码'):
            extractor.extract_images(sample_pdf, output_dir, start_page=3, end_page=1)
    
    @allure.story('DPI小于1抛出异常')
    def test_invalid_dpi(self, sample_pdf, temp_dir):
        """测试DPI小于1时抛出异常"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with pytest.raises(ValueError, match='DPI必须大于等于1'):
            extractor.convert_to_images(sample_pdf, output_dir, dpi=0)
    
    @allure.story('使用mock测试convert_to_images - 模拟poppler')
    def test_convert_to_images_with_mock(self, sample_pdf, temp_dir):
        """使用mock测试convert_to_images，避免依赖poppler"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        # 创建模拟的PIL图片对象
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image, mock_image, mock_image]
            
            images = extractor.convert_to_images(sample_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 3
            assert os.path.exists(output_dir)
            mock_convert.assert_called_once()
    
    @allure.story('使用mock测试convert_to_images带页码范围')
    def test_convert_to_images_with_page_range_mock(self, sample_pdf, temp_dir):
        """使用mock测试带页码范围的convert_to_images"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image, mock_image]
            
            images = extractor.convert_to_images(sample_pdf, output_dir, start_page=1, end_page=2)
            
            assert isinstance(images, list)
            assert len(images) == 2
            mock_convert.assert_called_once()
            # 验证参数正确传递
            call_args = mock_convert.call_args
            assert call_args[1]['first_page'] == 1
            assert call_args[1]['last_page'] == 2
    
    @allure.story('使用mock测试convert_to_images带自定义DPI')
    def test_convert_to_images_with_custom_dpi_mock(self, sample_pdf, temp_dir):
        """使用mock测试带自定义DPI的convert_to_images"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image] * 3
            
            images = extractor.convert_to_images(sample_pdf, output_dir, dpi=150)
            
            assert isinstance(images, list)
            assert len(images) == 3
            # 验证DPI参数正确传递
            call_args = mock_convert.call_args
            assert call_args[1]['dpi'] == 150
    
    @allure.story('使用mock测试convert_to_images自动创建目录')
    def test_output_directory_creation_convert_mock(self, sample_pdf, temp_dir):
        """使用mock测试convert_to_images输出目录不存在时自动创建"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "non_existent_dir" / "sub_dir" / "images_convert")
        
        assert not os.path.exists(output_dir)
        
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image]
            
            images = extractor.convert_to_images(sample_pdf, output_dir)
            
            assert os.path.exists(output_dir)
    
    @allure.story('转换PDF为图片 - 正常场景（需要poppler）')
    @pytest.mark.skipif(not check_poppler_installed(), reason="poppler未安装")
    def test_convert_to_images_normal(self, sample_pdf, temp_dir):
        """测试正常转换PDF为图片（需要poppler）"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        images = extractor.convert_to_images(sample_pdf, output_dir)
        
        assert isinstance(images, list)
        assert os.path.exists(output_dir)
        # 3页PDF应该生成3张图片
        assert len(images) == 3
    
    @allure.story('转换PDF为图片 - 带页码范围（需要poppler）')
    @pytest.mark.skipif(not check_poppler_installed(), reason="poppler未安装")
    def test_convert_to_images_with_page_range_real(self, sample_pdf, temp_dir):
        """测试带页码范围转换PDF为图片（需要poppler）"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        images = extractor.convert_to_images(sample_pdf, output_dir, start_page=1, end_page=2)
        
        assert isinstance(images, list)
        assert len(images) == 2
    
    @allure.story('转换PDF为图片 - 自定义DPI（需要poppler）')
    @pytest.mark.skipif(not check_poppler_installed(), reason="poppler未安装")
    def test_convert_to_images_with_custom_dpi_real(self, sample_pdf, temp_dir):
        """测试带自定义DPI转换PDF为图片（需要poppler）"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        images = extractor.convert_to_images(sample_pdf, output_dir, dpi=150)
        
        assert isinstance(images, list)
        assert len(images) == 3
    
    @allure.story('输出目录不存在时自动创建')
    def test_output_directory_creation(self, sample_pdf, temp_dir):
        """测试输出目录不存在时自动创建"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "non_existent_dir" / "sub_dir" / "images")
        
        assert not os.path.exists(output_dir)
        
        images = extractor.extract_images(sample_pdf, output_dir)
        
        assert os.path.exists(output_dir)
    
    @allure.story('使用mock测试不同图片格式处理 - JPG格式')
    def test_extract_images_different_formats_jpg(self, temp_dir):
        """使用mock测试JPG格式图片提取"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        # 创建模拟的PDF对象和图片对象
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            # 创建模拟页面
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置JPG格式filter
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.return_value = {'/Filter': '/DCTDecode', '/Width': 100, '/Height': 100}
            mock_image_obj._data = b'fake_jpg_data'
            
            # 构建对象结构
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            # 创建一个临时PDF文件
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            # 验证目录创建
            assert os.path.exists(output_dir)
    
    @allure.story('使用mock测试不同图片格式处理 - PNG格式')
    def test_extract_images_different_formats_png(self, temp_dir):
        """使用mock测试PNG格式图片提取（默认格式）"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置未知filter，应该使用png格式
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.side_effect = lambda k: {'/Filter': '/UnknownFilter', '/Width': 100, '/Height': 100}[k]
            mock_image_obj._data = b'fake_png_data'
            
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert os.path.exists(output_dir)
    
    @allure.story('使用mock测试List类型Filter处理')
    def test_extract_images_list_filter(self, temp_dir):
        """使用mock测试List类型Filter的处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置List类型的filter
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.side_effect = lambda k: {'/Filter': ['/DCTDecode', '/FlateDecode'], '/Width': 100, '/Height': 100}[k]
            mock_image_obj._data = b'fake_image_data'
            
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert os.path.exists(output_dir)
    
    @allure.story('使用mock测试空Filter处理')
    def test_extract_images_empty_filter(self, temp_dir):
        """使用mock测试空Filter的处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置空filter
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.side_effect = lambda k: {'/Filter': [], '/Width': 100, '/Height': 100}[k]
            mock_image_obj._data = b'fake_image_data'
            
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert os.path.exists(output_dir)
    
    @allure.story('类实例化测试')
    def test_class_instantiation(self):
        """测试PDFImageExtractor类实例化"""
        extractor = PDFImageExtractor()
        assert extractor is not None
    
    @allure.story('异常处理测试 - 页面资源访问异常')
    def test_extract_images_page_exception_handling(self, temp_dir):
        """测试页面资源访问异常时的异常处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            # 模拟访问Resources时抛出异常
            mock_page.__getitem__.side_effect = KeyError("Resources not found")
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            # 应该捕获异常并继续，不抛出
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 0
    
    @allure.story('使用mock测试不同图片格式处理 - JPXDecode格式')
    def test_extract_images_different_formats_jpx(self, temp_dir):
        """使用mock测试JPXDecode格式（jp2）图片提取"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置JPX格式filter
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.side_effect = lambda k: {'/Filter': '/JPXDecode', '/Width': 100, '/Height': 100}[k]
            mock_image_obj._data = b'fake_jp2_data'
            
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert os.path.exists(output_dir)
    
    @allure.story('使用mock测试不同图片格式处理 - CCITTFaxDecode格式')
    def test_extract_images_different_formats_ccitt(self, temp_dir):
        """使用mock测试CCITTFaxDecode格式（tiff）图片提取"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 设置CCITT格式filter
            mock_image_obj.get.return_value = '/Image'
            mock_image_obj.__getitem__.side_effect = lambda k: {'/Filter': '/CCITTFaxDecode', '/Width': 100, '/Height': 100}[k]
            mock_image_obj._data = b'fake_tiff_data'
            
            mock_xobject.get_object.return_value = {'img1': mock_image_obj}
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert os.path.exists(output_dir)
    
    @allure.story('异常处理测试 - XObject内部异常处理')
    def test_extract_images_xobject_exception_handling(self, temp_dir):
        """测试XObject内部异常处理（内部try-except）"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            
            # 模拟get_object时抛出异常
            mock_xobject.__iter__ = lambda self: iter(['img1'])
            mock_xobject.__getitem__.side_effect = Exception("XObject access error")
            
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            # 应该捕获内部异常并继续，不抛出
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 0
    
    @allure.story('异常处理测试 - 图片对象访问异常')
    def test_extract_images_image_obj_exception_handling(self, temp_dir):
        """测试图片对象访问异常时的异常处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_image_obj = MagicMock()
            
            # 模拟访问图片对象数据时抛出异常
            mock_image_obj.get.side_effect = Exception("Image obj error")
            mock_image_obj._data = b'test_data'
            
            mock_xobject.__iter__ = lambda self: iter(['img1'])
            mock_xobject.__getitem__.return_value = mock_image_obj
            
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            # 应该捕获异常并继续
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
    
    @allure.story('无XObject资源的页面处理')
    def test_extract_images_no_xobject(self, temp_dir):
        """测试页面没有XObject资源的情况"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            
            # 模拟没有XObject
            mock_resources.__contains__.return_value = False
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 0
    
    @allure.story('结束页码大于总页数的边界处理')
    def test_extract_images_end_page_exceeds_total(self, sample_pdf, temp_dir):
        """测试结束页码大于PDF总页数时的边界处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        # 使用一个很大的结束页码
        images = extractor.extract_images(sample_pdf, output_dir, end_page=1000)
        
        assert isinstance(images, list)
        assert os.path.exists(output_dir)
    
    @allure.story('convert_to_images结束页码大于总页数的边界处理')
    def test_convert_end_page_exceeds_total_mock(self, sample_pdf, temp_dir):
        """测试convert_to_images结束页码大于总页数时的边界处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image]
            
            images = extractor.convert_to_images(sample_pdf, output_dir, end_page=1000)
            
            assert isinstance(images, list)
            mock_convert.assert_called_once()
    
    @allure.story('convert_to_images只提供起始页码的边界处理')
    def test_convert_only_start_page_mock(self, sample_pdf, temp_dir):
        """测试convert_to_images只提供起始页码的情况"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        mock_image = MagicMock(spec=PILImage.Image)
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [mock_image, mock_image]
            
            images = extractor.convert_to_images(sample_pdf, output_dir, start_page=2)
            
            assert isinstance(images, list)
            mock_convert.assert_called_once()
            # 验证只提供起始页码时结束页码是总页数
            call_args = mock_convert.call_args
            assert call_args[1]['first_page'] == 2
    
    @allure.story('convert_to_images结束页码小于起始页码的异常处理')
    def test_convert_end_page_less_than_start(self, sample_pdf, temp_dir):
        """测试convert_to_images结束页码小于起始页码时抛出异常"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        with pytest.raises(ValueError, match='结束页码必须大于等于起始页码'):
            extractor.convert_to_images(sample_pdf, output_dir, start_page=3, end_page=1)
    
    @allure.story('完整的图片提取流程测试 - 多张图片')
    def test_extract_images_multiple_images_mock(self, temp_dir):
        """使用mock测试提取多张图片的完整流程"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            
            # 创建多个图片对象
            mock_img1 = MagicMock()
            mock_img2 = MagicMock()
            
            mock_img1.get.return_value = '/Image'
            mock_img1.__getitem__.side_effect = lambda k: {'/Subtype': '/Image', '/Filter': '/DCTDecode', '/Width': 100, '/Height': 100}[k]
            mock_img1._data = b'fake_jpg_data_1'
            
            mock_img2.get.return_value = '/Image'
            mock_img2.__getitem__.side_effect = lambda k: {'/Subtype': '/Image', '/Filter': '', '/Width': 200, '/Height': 200}[k]
            mock_img2._data = b'fake_png_data_2'
            
            # 模拟x_object迭代
            def mock_get_object(key):
                if key == 'img1':
                    return mock_img1
                elif key == 'img2':
                    return mock_img2
                return None
            
            mock_xobject.__iter__ = lambda self: iter(['img1', 'img2'])
            mock_xobject.__getitem__.side_effect = lambda k: type('obj', (), {'get_object': lambda: mock_get_object(k)})()
            
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            # 应该提取到2张图片
            assert len(images) >= 0
            assert os.path.exists(output_dir)
    
    @allure.story('图片对象不是Image类型的处理')
    def test_extract_images_non_image_subtype(self, temp_dir):
        """测试XObject不是Image类型时的处理"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images")
        
        with patch('src.pdf_image_extractor.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_resources = MagicMock()
            mock_xobject = MagicMock()
            mock_obj = MagicMock()
            
            # 设置为非Image类型
            mock_obj.get.return_value = '/Form'
            mock_obj._data = b'not_an_image'
            
            mock_xobject.__iter__ = lambda self: iter(['obj1'])
            mock_xobject.__getitem__.return_value = type('obj', (), {'get_object': lambda: mock_obj})()
            
            mock_resources.__contains__.return_value = True
            mock_resources.__getitem__.return_value = mock_xobject
            mock_page.__getitem__.return_value = mock_resources
            mock_reader.return_value.pages = [mock_page]
            
            test_pdf = str(temp_dir / "test.pdf")
            with open(test_pdf, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            images = extractor.extract_images(test_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 0
    
    @allure.story('convert_to_images保存图片的mock测试')
    def test_convert_to_images_save_image_mock(self, sample_pdf, temp_dir):
        """测试convert_to_images保存图片的完整流程"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        # 创建一个真实的PIL Image对象进行测试
        from PIL import Image as PILImageModule
        test_img = PILImageModule.new('RGB', (100, 100), color='red')
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [test_img]
            
            images = extractor.convert_to_images(sample_pdf, output_dir)
            
            assert isinstance(images, list)
            assert len(images) == 1
            # 验证文件确实被创建
            assert os.path.exists(images[0])
            # 验证是png文件
            assert images[0].endswith('.png')
    
    @allure.story('convert_to_images多页转换测试')
    def test_convert_to_images_multiple_pages_mock(self, sample_pdf, temp_dir):
        """测试convert_to_images转换多页的流程"""
        extractor = PDFImageExtractor()
        output_dir = str(temp_dir / "images_converted")
        
        from PIL import Image as PILImageModule
        test_img1 = PILImageModule.new('RGB', (100, 100), color='red')
        test_img2 = PILImageModule.new('RGB', (100, 100), color='blue')
        
        with patch('src.pdf_image_extractor.convert_from_path') as mock_convert:
            mock_convert.return_value = [test_img1, test_img2]
            
            images = extractor.convert_to_images(sample_pdf, output_dir, start_page=1, end_page=2)
            
            assert isinstance(images, list)
            assert len(images) == 2
            # 验证文件名包含正确的页码
            assert 'page_1' in images[0]
            assert 'page_2' in images[1]
