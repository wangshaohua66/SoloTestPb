"""
测试命令行接口模块
"""

import pytest
from pathlib import Path
from PIL import Image

from img_resize.cli import (
    parse_args,
    create_config_from_args,
    main
)
from img_resize.image_processor import ImageFormat, ResizeMode
from img_resize.watermark import WatermarkPosition


class TestCLI:
    """测试CLI模块"""

    def test_parse_args_basic(self):
        """测试解析基本参数"""
        args = parse_args(["-i", "/input", "-o", "/output"])
        
        assert args.input == "/input"
        assert args.output == "/output"

    def test_parse_args_resize(self):
        """测试解析尺寸调整参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--width", "800",
            "--height", "600",
            "--resize-mode", "fit"
        ])
        
        assert args.width == 800
        assert args.height == 600
        assert args.resize_mode == "fit"

    def test_parse_args_scale(self):
        """测试解析缩放参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--scale", "0.5"
        ])
        
        assert args.scale == 0.5

    def test_parse_args_format_and_quality(self):
        """测试解析格式和质量参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--format", "webp",
            "--quality", "70"
        ])
        
        assert args.format == "webp"
        assert args.quality == 70

    def test_parse_args_text_watermark(self):
        """测试解析文字水印参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--text-watermark", "Copyright 2024",
            "--text-watermark-position", "bottom_right",
            "--text-watermark-font-size", "24",
            "--text-watermark-opacity", "0.6"
        ])
        
        assert args.text_watermark == "Copyright 2024"
        assert args.text_watermark_position == "bottom_right"
        assert args.text_watermark_font_size == 24
        assert args.text_watermark_opacity == 0.6

    def test_parse_args_image_watermark(self):
        """测试解析图片水印参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--image-watermark", "/watermark.png",
            "--image-watermark-position", "top_left",
            "--image-watermark-opacity", "0.3",
            "--image-watermark-scale", "0.5"
        ])
        
        assert args.image_watermark == "/watermark.png"
        assert args.image_watermark_position == "top_left"
        assert args.image_watermark_opacity == 0.3
        assert args.image_watermark_scale == 0.5

    def test_parse_args_exif(self):
        """测试解析EXIF参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--no-exif",
            "--no-auto-orient"
        ])
        
        assert args.no_exif is True
        assert args.no_auto_orient is True

    def test_parse_args_processing(self):
        """测试解析处理选项参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--workers", "4",
            "--use-threads",
            "--no-recursive"
        ])
        
        assert args.workers == 4
        assert args.use_threads is True
        assert args.no_recursive is True

    def test_parse_args_verbose(self):
        """测试解析详细日志参数"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--verbose"
        ])
        
        assert args.verbose is True

    def test_create_config_from_args_default(self):
        """测试从默认参数创建配置"""
        args = parse_args(["-i", "/input", "-o", "/output"])
        config = create_config_from_args(args)
        
        assert config.width is None
        assert config.height is None
        assert config.scale is None
        assert config.quality == 85
        assert config.output_format is None
        assert config.keep_exif is True
        assert config.auto_orient is True

    def test_create_config_from_args_resize(self):
        """测试从尺寸调整参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--width", "800",
            "--height", "600",
            "--resize-mode", "cover"
        ])
        config = create_config_from_args(args)
        
        assert config.width == 800
        assert config.height == 600
        assert config.resize_mode == ResizeMode.COVER

    def test_create_config_from_args_scale(self):
        """测试从缩放参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--scale", "0.5"
        ])
        config = create_config_from_args(args)
        
        assert config.scale == 0.5

    def test_create_config_from_args_format(self):
        """测试从格式参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--format", "png",
            "--quality", "90"
        ])
        config = create_config_from_args(args)
        
        assert config.output_format == ImageFormat.PNG
        assert config.quality == 90

    def test_create_config_from_args_text_watermark(self):
        """测试从文字水印参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--text-watermark", "Test",
            "--text-watermark-position", "center",
            "--text-watermark-font-size", "48",
            "--text-watermark-opacity", "0.7"
        ])
        config = create_config_from_args(args)
        
        assert config.text_watermark == "Test"
        assert config.text_watermark_position == WatermarkPosition.CENTER
        assert config.text_watermark_font_size == 48
        assert config.text_watermark_opacity == 0.7

    def test_create_config_from_args_image_watermark(self):
        """测试从图片水印参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--image-watermark", "/wm.png",
            "--image-watermark-position", "bottom_left",
            "--image-watermark-opacity", "0.4",
            "--image-watermark-scale", "0.8"
        ])
        config = create_config_from_args(args)
        
        assert config.image_watermark == "/wm.png"
        assert config.image_watermark_position == WatermarkPosition.BOTTOM_LEFT
        assert config.image_watermark_opacity == 0.4
        assert config.image_watermark_scale == 0.8

    def test_create_config_from_args_no_exif(self):
        """测试从EXIF参数创建配置"""
        args = parse_args([
            "-i", "/input", "-o", "/output",
            "--no-exif",
            "--no-auto-orient"
        ])
        config = create_config_from_args(args)
        
        assert config.keep_exif is False
        assert config.auto_orient is False

    def test_main_input_not_exists(self, tmp_path, capsys):
        """测试主函数输入目录不存在"""
        exit_code = main([
            "-i", str(tmp_path / "nonexistent"),
            "-o", str(tmp_path / "output")
        ])
        
        assert exit_code == 1
        
        captured = capsys.readouterr()
        assert "输入目录不存在" in captured.err

    def test_main_success(self, tmp_path):
        """测试主函数成功执行"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(3):
            img = Image.new("RGB", (800, 600), color="red")
            img.save(input_dir / f"test_{i}.jpg", "JPEG")
        
        output_dir = tmp_path / "output"
        
        exit_code = main([
            "-i", str(input_dir),
            "-o", str(output_dir),
            "--width", "400",
            "--workers", "2",
            "--use-threads"
        ])
        
        assert exit_code == 0
        assert len(list(output_dir.glob("*.jpg"))) == 3
