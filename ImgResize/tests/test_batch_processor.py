"""
测试批量处理模块
"""

import pytest
from pathlib import Path
from PIL import Image

from img_resize.batch_processor import (
    BatchProcessor,
    ProcessingConfig,
    ProcessingResult,
    BatchResult
)
from img_resize.image_processor import ImageFormat, ResizeMode
from img_resize.watermark import WatermarkPosition


@pytest.fixture
def batch_processor():
    """创建BatchProcessor实例"""
    return BatchProcessor(max_workers=2, use_processes=False)


@pytest.fixture
def input_dir(tmp_path):
    """创建测试输入目录"""
    input_path = tmp_path / "input"
    input_path.mkdir()
    
    for i in range(5):
        img = Image.new("RGB", (800, 600), color=(i * 50, 0, 0))
        img.save(input_path / f"image_{i}.jpg", "JPEG")
    
    return input_path


@pytest.fixture
def output_dir(tmp_path):
    """创建测试输出目录"""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return output_path


class TestBatchProcessor:
    """测试BatchProcessor类"""

    def test_init(self, batch_processor):
        """测试初始化"""
        assert batch_processor is not None
        assert batch_processor.max_workers == 2
        assert batch_processor.use_processes is False

    def test_get_image_files(self, batch_processor, input_dir):
        """测试获取图片文件"""
        files = batch_processor.get_image_files(input_dir)
        
        assert len(files) == 5
        assert all(f.suffix.lower() == ".jpg" for f in files)

    def test_get_image_files_not_recursive(self, batch_processor, input_dir):
        """测试不递归获取图片文件"""
        subdir = input_dir / "subdir"
        subdir.mkdir()
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(subdir / "nested.jpg", "JPEG")
        
        files = batch_processor.get_image_files(input_dir, recursive=False)
        assert len(files) == 5
        
        files_recursive = batch_processor.get_image_files(input_dir, recursive=True)
        assert len(files_recursive) == 6

    def test_get_image_files_not_exists(self, batch_processor, tmp_path):
        """测试获取不存在的目录"""
        with pytest.raises(FileNotFoundError):
            batch_processor.get_image_files(tmp_path / "nonexistent")

    def test_get_image_files_not_directory(self, batch_processor, tmp_path):
        """测试获取非目录路径"""
        file_path = tmp_path / "test.jpg"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(file_path, "JPEG")
        
        with pytest.raises(NotADirectoryError):
            batch_processor.get_image_files(file_path)

    def test_process_single_image(self, batch_processor, input_dir, output_dir):
        """测试处理单张图片"""
        config = ProcessingConfig(
            width=400,
            quality=80
        )
        
        input_file = input_dir / "image_0.jpg"
        output_file = output_dir / "image_0.jpg"
        
        result = batch_processor.process_single_image(
            input_file,
            output_file,
            config
        )
        
        assert result.success
        assert result.input_path == input_file
        assert result.output_path == output_file
        assert output_file.exists()
        
        saved = Image.open(output_file)
        assert saved.width == 400

    def test_process_batch(self, batch_processor, input_dir, output_dir):
        """测试批量处理"""
        config = ProcessingConfig(
            width=400,
            quality=80
        )
        
        result = batch_processor.process_batch(
            input_dir,
            output_dir,
            config,
            recursive=False
        )
        
        assert result.total_count == 5
        assert result.success_count == 5
        assert result.failed_count == 0
        assert result.success_rate == 100.0
        
        assert len(list(output_dir.glob("*.jpg"))) == 5

    def test_process_batch_with_scale(self, batch_processor, input_dir, output_dir):
        """测试使用缩放比例批量处理"""
        config = ProcessingConfig(
            scale=0.5
        )
        
        result = batch_processor.process_batch(
            input_dir,
            output_dir,
            config,
            recursive=False
        )
        
        assert result.success_count == 5
        
        for output_file in output_dir.glob("*.jpg"):
            img = Image.open(output_file)
            assert img.width == 400
            assert img.height == 300

    def test_process_batch_format_conversion(self, batch_processor, input_dir, output_dir):
        """测试格式转换批量处理"""
        config = ProcessingConfig(
            output_format=ImageFormat.PNG
        )
        
        result = batch_processor.process_batch(
            input_dir,
            output_dir,
            config,
            recursive=False
        )
        
        assert result.success_count == 5
        
        png_files = list(output_dir.glob("*.png"))
        assert len(png_files) == 5

    def test_process_batch_empty(self, batch_processor, tmp_path, output_dir):
        """测试处理空目录"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        config = ProcessingConfig(width=100)
        result = batch_processor.process_batch(
            empty_dir,
            output_dir,
            config
        )
        
        assert result.total_count == 0
        assert result.success_count == 0
        assert result.failed_count == 0

    def test_process_batch_with_progress_callback(self, batch_processor, input_dir, output_dir):
        """测试带进度回调的批量处理"""
        progress_calls = []
        
        def callback(current, total, result):
            progress_calls.append((current, total))
        
        config = ProcessingConfig(width=200)
        result = batch_processor.process_batch(
            input_dir,
            output_dir,
            config,
            recursive=False,
            progress_callback=callback
        )
        
        assert len(progress_calls) == 5
        assert all(call[1] == 5 for call in progress_calls)

    def test_process_batch_strip_exif(self, batch_processor, input_dir, output_dir):
        """测试清除EXIF"""
        config = ProcessingConfig(
            width=200,
            keep_exif=False
        )
        
        result = batch_processor.process_batch(
            input_dir,
            output_dir,
            config,
            recursive=False
        )
        
        assert result.success_count == 5


class TestProcessingConfig:
    """测试ProcessingConfig类"""

    def test_default_config(self):
        """测试默认配置"""
        config = ProcessingConfig()
        
        assert config.width is None
        assert config.height is None
        assert config.scale is None
        assert config.quality == 85
        assert config.keep_exif is True
        assert config.auto_orient is True
        assert config.text_watermark is None
        assert config.image_watermark is None

    def test_custom_config(self):
        """测试自定义配置"""
        config = ProcessingConfig(
            width=800,
            height=600,
            scale=0.5,
            quality=70,
            output_format=ImageFormat.WEBP,
            keep_exif=False,
            auto_orient=False,
            text_watermark="Test",
            text_watermark_position=WatermarkPosition.CENTER
        )
        
        assert config.width == 800
        assert config.height == 600
        assert config.scale == 0.5
        assert config.quality == 70
        assert config.output_format == ImageFormat.WEBP
        assert config.keep_exif is False
        assert config.auto_orient is False
        assert config.text_watermark == "Test"
        assert config.text_watermark_position == WatermarkPosition.CENTER


class TestBatchResult:
    """测试BatchResult类"""

    def test_empty_result(self):
        """测试空结果"""
        result = BatchResult()
        
        assert result.total_count == 0
        assert result.success_count == 0
        assert result.failed_count == 0
        assert result.success_rate == 0.0
        assert result.average_time == 0.0

    def test_success_rate(self):
        """测试成功率计算"""
        result = BatchResult(
            total_count=10,
            success_count=8,
            failed_count=2
        )
        
        assert result.success_rate == 80.0

    def test_average_time(self):
        """测试平均时间计算"""
        results = [
            ProcessingResult(input_path=Path("a.jpg"), processing_time=1.0),
            ProcessingResult(input_path=Path("b.jpg"), processing_time=2.0),
            ProcessingResult(input_path=Path("c.jpg"), success=False, processing_time=0.5)
        ]
        
        result = BatchResult(
            total_count=3,
            success_count=2,
            failed_count=1,
            results=results
        )
        
        assert result.average_time == 1.5
