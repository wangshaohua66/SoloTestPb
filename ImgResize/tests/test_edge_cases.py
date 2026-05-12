"""
边界情况测试
测试超大图片、损坏文件、不支持的格式等
"""

import pytest
from pathlib import Path
from PIL import Image
import random

from img_resize.image_processor import ImageProcessor, ImageFormat, ResizeMode
from img_resize.batch_processor import BatchProcessor, ProcessingConfig


@pytest.fixture
def processor():
    """创建ImageProcessor实例"""
    return ImageProcessor()


@pytest.fixture
def batch_processor():
    """创建BatchProcessor实例"""
    return BatchProcessor(max_workers=2, use_processes=False)


class TestEdgeCases:
    """边界情况测试类"""

    def test_very_large_image(self, processor, tmp_path):
        """测试处理超大图片"""
        large_img = Image.new("RGB", (4000, 4000), color="blue")
        output_path = tmp_path / "large_output.jpg"
        
        resized = processor.resize_image(
            large_img,
            width=800,
            height=800,
            mode=ResizeMode.FIT
        )
        
        assert resized.width <= 800
        assert resized.height <= 800
        
        processor.save_image(resized, output_path)
        assert output_path.exists()

    def test_tiny_image(self, processor):
        """测试处理极小图片"""
        tiny_img = Image.new("RGB", (1, 1), color="red")
        
        resized = processor.resize_image(
            tiny_img,
            width=100,
            height=100,
            mode=ResizeMode.EXACT
        )
        
        assert resized.size == (100, 100)

    def test_zero_dimensions(self, processor):
        """测试零尺寸边界"""
        img = Image.new("RGB", (100, 100), color="red")
        
        with pytest.raises(ValueError):
            processor.resize_image(img, width=0, height=0)

    def test_zero_width_raises_valueerror(self, processor):
        """测试零宽度抛出ValueError而非PIL异常"""
        img = Image.new("RGB", (100, 100), color="red")
        
        with pytest.raises(ValueError) as exc_info:
            processor.resize_image(img, width=0, height=100)
        
        assert "width" in str(exc_info.value).lower()
        # 确保不是PIL的异常
        assert "ValueError" in type(exc_info.value).__name__

    def test_zero_height_raises_valueerror(self, processor):
        """测试零高度抛出ValueError而非PIL异常"""
        img = Image.new("RGB", (100, 100), color="red")
        
        with pytest.raises(ValueError) as exc_info:
            processor.resize_image(img, width=100, height=0)
        
        assert "height" in str(exc_info.value).lower()

    def test_negative_dimensions_raises_valueerror(self, processor):
        """测试负尺寸抛出ValueError"""
        img = Image.new("RGB", (100, 100), color="red")
        
        with pytest.raises(ValueError):
            processor.resize_image(img, width=-1, height=100)
        
        with pytest.raises(ValueError):
            processor.resize_image(img, width=100, height=-1)

    def test_negative_scale(self, processor):
        """测试负缩放比例"""
        img = Image.new("RGB", (100, 100), color="red")
        
        with pytest.raises(ValueError):
            processor.scale_image(img, -1)
        
        with pytest.raises(ValueError):
            processor.scale_image(img, 0)

    def test_extreme_quality_values(self, processor, tmp_path):
        """测试极端质量值"""
        img = Image.new("RGB", (100, 100), color="red")
        output_path = tmp_path / "quality_test.jpg"
        
        processor.compress_and_save(img, output_path, quality=1)
        assert output_path.exists()
        
        output_path2 = tmp_path / "quality_test2.jpg"
        processor.compress_and_save(img, output_path2, quality=100)
        assert output_path2.exists()

    def test_corrupted_image_file(self, processor, tmp_path):
        """测试损坏的图片文件"""
        corrupted_path = tmp_path / "corrupted.jpg"
        corrupted_path.write_bytes(b"not a valid image")
        
        with pytest.raises(Exception):
            processor.load_image(corrupted_path)

    def test_unsupported_format(self, tmp_path, batch_processor):
        """测试不支持的文件格式"""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("This is not an image")
        
        assert not ImageProcessor.is_supported_format(txt_path)

    def test_empty_directory(self, tmp_path, batch_processor):
        """测试空目录"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output_dir = tmp_path / "output"
        
        config = ProcessingConfig(width=100)
        result = batch_processor.process_batch(empty_dir, output_dir, config)
        
        assert result.total_count == 0
        assert result.success_count == 0

    def test_single_pixel_image(self, processor, tmp_path):
        """测试单像素图片"""
        img = Image.new("RGB", (1, 1), color=(255, 0, 0))
        output_path = tmp_path / "single_pixel.jpg"
        
        processor.save_image(img, output_path)
        assert output_path.exists()
        
        loaded = Image.open(output_path)
        assert loaded.size == (1, 1)

    def test_mixed_formats_batch(self, tmp_path, batch_processor):
        """测试混合格式的批量处理"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        formats = [
            ("jpg", "JPEG"),
            ("png", "PNG"),
            ("webp", "WEBP"),
        ]
        
        for i, (ext, fmt) in enumerate(formats):
            img = Image.new("RGB", (200, 200), color=(i * 50, 0, 0))
            img.save(input_dir / f"image_{i}.{ext}", fmt)
        
        output_dir = tmp_path / "output"
        
        config = ProcessingConfig(
            width=100,
            output_format=ImageFormat.JPG
        )
        
        result = batch_processor.process_batch(input_dir, output_dir, config)
        
        assert result.success_count == 3
        output_files = list(output_dir.glob("*.jpg"))
        assert len(output_files) == 3

    def test_transparent_png_to_jpg(self, processor, tmp_path):
        """测试透明PNG转JPG"""
        png_img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        png_path = tmp_path / "transparent.png"
        png_img.save(png_path, "PNG")
        
        output_path = tmp_path / "output.jpg"
        
        loaded = processor.load_image(png_path)
        processor.save_image(loaded, output_path, format=ImageFormat.JPG)
        
        assert output_path.exists()
        result = Image.open(output_path)
        assert result.mode == "RGB"

    def test_gif_processing(self, processor, tmp_path):
        """测试GIF图片处理"""
        gif_img = Image.new("P", (100, 100), color=0)
        gif_path = tmp_path / "animation.gif"
        gif_img.save(gif_path, "GIF")
        
        output_path = tmp_path / "output.gif"
        
        loaded = processor.load_image(gif_path)
        processor.save_image(loaded, output_path)
        
        assert output_path.exists()

    def test_extreme_resize_ratio(self, processor):
        """测试极端缩放比例"""
        img = Image.new("RGB", (1000, 1000), color="red")
        
        tiny = processor.scale_image(img, 0.001)
        assert tiny.width <= 10
        assert tiny.height <= 10

    def test_max_dimensions(self, processor):
        """测试最大尺寸边界"""
        img = Image.new("RGB", (100, 100), color="red")
        
        large = processor.scale_image(img, 100)
        assert large.width == 10000
        assert large.height == 10000

    def test_readonly_output_directory(self, tmp_path, batch_processor):
        """测试只读输出目录"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(input_dir / "test.jpg", "JPEG")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        output_dir.chmod(0o444)
        
        config = ProcessingConfig(width=50)
        result = batch_processor.process_batch(input_dir, output_dir, config)
        
        assert result.failed_count >= 0

    def test_cover_mode_small_target(self, processor):
        """测试COVER模式目标尺寸小于原图"""
        img = Image.new("RGB", (800, 600), color="red")
        
        result = processor.resize_image(
            img,
            width=100,
            height=100,
            mode=ResizeMode.COVER
        )
        
        assert result.size == (100, 100)

    def test_fit_mode_same_ratio(self, processor):
        """测试FIT模式相同比例"""
        img = Image.new("RGB", (800, 600), color="red")
        
        result = processor.resize_image(
            img,
            width=400,
            height=300,
            mode=ResizeMode.FIT
        )
        
        assert result.size == (400, 300)

    def test_multiple_formats_same_name(self, tmp_path, batch_processor):
        """测试同名不同格式文件"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        img = Image.new("RGB", (100, 100), color="red")
        img.save(input_dir / "test.jpg", "JPEG")
        img.save(input_dir / "test.png", "PNG")
        
        output_dir = tmp_path / "output"
        
        config = ProcessingConfig(width=50)
        result = batch_processor.process_batch(input_dir, output_dir, config)
        
        assert result.success_count == 2

    def test_memory_usage_large_batch(self, tmp_path, batch_processor):
        """测试大量图片的内存处理"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(10):
            img = Image.new("RGB", (500, 500), color=(i * 25, 0, 0))
            img.save(input_dir / f"image_{i}.jpg", "JPEG")
        
        output_dir = tmp_path / "output"
        
        config = ProcessingConfig(width=200, quality=70)
        result = batch_processor.process_batch(input_dir, output_dir, config)
        
        assert result.success_count == 10

    def test_very_long_filename(self, tmp_path, processor):
        """测试超长文件名"""
        long_name = "a" * 100 + ".jpg"
        img = Image.new("RGB", (100, 100), color="red")
        output_path = tmp_path / long_name
        
        processor.save_image(img, output_path)
        assert output_path.exists()
