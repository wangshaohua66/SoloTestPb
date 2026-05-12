"""
测试图像处理核心模块
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image

from img_resize.image_processor import (
    ImageProcessor,
    ImageFormat,
    ResizeMode
)


@pytest.fixture
def processor():
    """创建ImageProcessor实例"""
    return ImageProcessor()


@pytest.fixture
def temp_image(tmp_path):
    """创建临时测试图片"""
    img = Image.new("RGB", (800, 600), color="red")
    img_path = tmp_path / "test.jpg"
    img.save(img_path, "JPEG")
    return img_path


@pytest.fixture
def temp_png_image(tmp_path):
    """创建临时PNG测试图片（带透明）"""
    img = Image.new("RGBA", (800, 600), color=(255, 0, 0, 128))
    img_path = tmp_path / "test.png"
    img.save(img_path, "PNG")
    return img_path


class TestImageProcessor:
    """测试ImageProcessor类"""

    def test_init(self, processor):
        """测试初始化"""
        assert processor is not None

    def test_load_image(self, processor, temp_image):
        """测试加载图片"""
        img = processor.load_image(temp_image)
        assert img is not None
        assert img.size == (800, 600)

    def test_load_image_not_exists(self, processor):
        """测试加载不存在的图片"""
        with pytest.raises(FileNotFoundError):
            processor.load_image("/nonexistent/path/image.jpg")

    def test_save_image(self, processor, tmp_path):
        """测试保存图片"""
        img = Image.new("RGB", (100, 100), color="blue")
        output_path = tmp_path / "output.jpg"
        
        processor.save_image(img, output_path)
        assert output_path.exists()
        
        saved = Image.open(output_path)
        assert saved.size == (100, 100)

    def test_resize_exact(self, processor):
        """测试EXACT缩放模式"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, width=400, height=300, mode=ResizeMode.EXACT)
        
        assert resized.size == (400, 300)

    def test_resize_fit_width(self, processor):
        """测试FIT模式仅指定宽度"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, width=400, mode=ResizeMode.FIT)
        
        assert resized.size == (400, 300)

    def test_resize_fit_height(self, processor):
        """测试FIT模式仅指定高度"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, height=150, mode=ResizeMode.FIT)
        
        assert resized.size == (200, 150)

    def test_resize_fit_both(self, processor):
        """测试FIT模式同时指定宽高"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, width=300, height=300, mode=ResizeMode.FIT)
        
        assert resized.size == (300, 225)

    def test_resize_contain(self, processor):
        """测试CONTAIN模式"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, width=400, height=400, mode=ResizeMode.CONTAIN)
        
        assert resized.size == (400, 300)

    def test_resize_cover(self, processor):
        """测试COVER模式"""
        img = Image.new("RGB", (800, 600), color="red")
        resized = processor.resize_image(img, width=400, height=400, mode=ResizeMode.COVER)
        
        assert resized.size == (400, 400)

    def test_resize_cover_requires_both(self, processor):
        """测试COVER模式需要同时指定宽高"""
        img = Image.new("RGB", (800, 600), color="red")
        with pytest.raises(ValueError):
            processor.resize_image(img, width=400, mode=ResizeMode.COVER)

    def test_resize_no_dimensions(self, processor):
        """测试未指定尺寸"""
        img = Image.new("RGB", (800, 600), color="red")
        with pytest.raises(ValueError):
            processor.resize_image(img)

    def test_scale_image(self, processor):
        """测试按比例缩放"""
        img = Image.new("RGB", (800, 600), color="red")
        scaled = processor.scale_image(img, 0.5)
        
        assert scaled.size == (400, 300)

    def test_scale_image_zoom(self, processor):
        """测试放大"""
        img = Image.new("RGB", (400, 300), color="red")
        scaled = processor.scale_image(img, 2.0)
        
        assert scaled.size == (800, 600)

    def test_scale_image_one(self, processor):
        """测试缩放比例为1"""
        img = Image.new("RGB", (800, 600), color="red")
        scaled = processor.scale_image(img, 1.0)
        
        assert scaled is img

    def test_scale_image_invalid(self, processor):
        """测试无效缩放比例"""
        img = Image.new("RGB", (800, 600), color="red")
        with pytest.raises(ValueError):
            processor.scale_image(img, 0)
        
        with pytest.raises(ValueError):
            processor.scale_image(img, -1)

    def test_compress_and_save(self, processor, tmp_path):
        """测试压缩并保存图片"""
        img = Image.new("RGB", (800, 600), color="red")
        output_path = tmp_path / "compressed.jpg"
        
        processor.compress_and_save(img, output_path, quality=50)
        
        assert output_path.exists()
        saved = Image.open(output_path)
        assert saved.size == (800, 600)

    def test_compress_and_save_different_quality(self, processor, tmp_path):
        """测试不同质量参数的压缩"""
        img = Image.new("RGB", (800, 600), color="red")
        
        high_quality = tmp_path / "high.jpg"
        low_quality = tmp_path / "low.jpg"
        
        processor.compress_and_save(img, high_quality, quality=95)
        processor.compress_and_save(img, low_quality, quality=10)
        
        high_size = high_quality.stat().st_size
        low_size = low_quality.stat().st_size
        
        assert low_size <= high_size

    def test_compress_and_save_invalid_quality(self, processor, tmp_path):
        """测试无效质量参数"""
        img = Image.new("RGB", (800, 600), color="red")
        output_path = tmp_path / "test.jpg"
        
        with pytest.raises(ValueError):
            processor.compress_and_save(img, output_path, quality=0)
        
        with pytest.raises(ValueError):
            processor.compress_and_save(img, output_path, quality=101)

    def test_validate_quality(self, processor):
        """测试验证质量参数"""
        assert processor.validate_quality(50) == 50
        assert processor.validate_quality(1) == 1
        assert processor.validate_quality(100) == 100
        
        with pytest.raises(ValueError):
            processor.validate_quality(0)
        
        with pytest.raises(ValueError):
            processor.validate_quality(101)

    def test_estimate_compression_ratio(self, processor):
        """测试估算压缩比"""
        assert processor.estimate_compression_ratio(95) == 0.9
        assert processor.estimate_compression_ratio(80) == 0.6
        assert processor.estimate_compression_ratio(60) == 0.4
        assert processor.estimate_compression_ratio(40) == 0.25
        assert processor.estimate_compression_ratio(20) == 0.15

    def test_prepare_for_format_jpeg(self, processor, temp_png_image):
        """测试为JPEG格式准备图片"""
        img = Image.open(temp_png_image)
        prepared = processor.prepare_for_format(img, ImageFormat.JPG)
        
        assert prepared.mode == "RGB"

    def test_prepare_for_format_png(self, processor):
        """测试为PNG格式准备图片"""
        img = Image.new("RGB", (100, 100), color="red")
        prepared = processor.prepare_for_format(img, ImageFormat.PNG)
        
        assert prepared.mode == "RGBA"

    def test_prepare_for_format_gif(self, processor):
        """测试为GIF格式准备图片"""
        img = Image.new("RGB", (100, 100), color="red")
        prepared = processor.prepare_for_format(img, ImageFormat.GIF)
        
        assert prepared.mode == "P"

    def test_prepare_for_format_webp(self, processor):
        """测试为WebP格式准备图片（无需特殊处理）"""
        img = Image.new("RGB", (100, 100), color="red")
        prepared = processor.prepare_for_format(img, ImageFormat.WEBP)
        
        assert prepared is img

    def test_get_image_info(self, processor):
        """测试获取图片信息"""
        img = Image.new("RGB", (800, 600), color="red")
        info = processor.get_image_info(img)
        
        assert info["size"] == (800, 600)
        assert info["width"] == 800
        assert info["height"] == 600
        assert info["mode"] == "RGB"

    def test_is_supported_format(self, processor):
        """测试检查支持的格式"""
        assert ImageProcessor.is_supported_format("test.jpg")
        assert ImageProcessor.is_supported_format("test.jpeg")
        assert ImageProcessor.is_supported_format("test.png")
        assert ImageProcessor.is_supported_format("test.webp")
        assert ImageProcessor.is_supported_format("test.gif")
        assert ImageProcessor.is_supported_format("test.JPG")
        assert not ImageProcessor.is_supported_format("test.txt")
        assert not ImageProcessor.is_supported_format("test.bmp")

    def test_save_with_different_format(self, processor, tmp_path):
        """测试保存为不同格式"""
        img = Image.new("RGB", (100, 100), color="blue")
        
        output_jpg = tmp_path / "output.jpg"
        processor.save_image(img, output_jpg, format=ImageFormat.JPG)
        assert output_jpg.exists()
        
        output_png = tmp_path / "output.png"
        processor.save_image(img, output_png, format=ImageFormat.PNG)
        assert output_png.exists()
        
        output_webp = tmp_path / "output.webp"
        processor.save_image(img, output_webp, format=ImageFormat.WEBP)
        assert output_webp.exists()
