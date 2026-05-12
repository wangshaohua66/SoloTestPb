"""
测试水印模块
"""

import pytest
from PIL import Image

from img_resize.watermark import Watermark, WatermarkPosition


@pytest.fixture
def watermark_processor():
    """创建Watermark实例"""
    return Watermark()


class TestWatermark:
    """测试Watermark类"""

    def test_init(self, watermark_processor):
        """测试初始化"""
        assert watermark_processor is not None

    def test_add_text_watermark(self, watermark_processor):
        """测试添加文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        result = watermark_processor.add_text_watermark(
            img,
            text="Test Watermark"
        )
        
        assert result is not None
        assert result.size == (800, 600)

    def test_add_text_watermark_empty(self, watermark_processor):
        """测试空文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        result = watermark_processor.add_text_watermark(img, text="")
        
        assert result is img

    def test_add_text_watermark_different_positions(self, watermark_processor):
        """测试不同位置的文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        
        for position in WatermarkPosition:
            result = watermark_processor.add_text_watermark(
                img,
                text="Test",
                position=position
            )
            assert result.size == (800, 600)

    def test_add_text_watermark_with_angle(self, watermark_processor):
        """测试旋转文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        result = watermark_processor.add_text_watermark(
            img,
            text="Test",
            angle=45
        )
        
        assert result.size == (800, 600)

    def test_add_text_watermark_repeat(self, watermark_processor):
        """测试平铺文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        result = watermark_processor.add_text_watermark(
            img,
            text="Test",
            repeat=True,
            repeat_spacing=100
        )
        
        assert result.size == (800, 600)

    def test_add_text_watermark_repeat_with_angle(self, watermark_processor):
        """测试带角度的平铺文字水印"""
        img = Image.new("RGB", (800, 600), color="white")
        result = watermark_processor.add_text_watermark(
            img,
            text="Test",
            repeat=True,
            angle=30
        )
        
        assert result.size == (800, 600)

    def test_add_image_watermark(self, watermark_processor):
        """测试添加图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        wm_img = Image.new("RGBA", (100, 50), color=(255, 0, 0, 128))
        
        result = watermark_processor.add_image_watermark(img, watermark_image=wm_img)
        
        assert result is not None
        assert result.size == (800, 600)

    def test_add_image_watermark_with_path(self, watermark_processor, tmp_path):
        """测试从文件添加图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        
        wm_img = Image.new("RGBA", (100, 50), color=(0, 0, 255, 128))
        wm_path = tmp_path / "watermark.png"
        wm_img.save(wm_path, "PNG")
        
        result = watermark_processor.add_image_watermark(img, watermark_image=wm_path)
        
        assert result.size == (800, 600)

    def test_add_image_watermark_with_scale(self, watermark_processor):
        """测试缩放图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        wm_img = Image.new("RGBA", (100, 50), color=(255, 0, 0, 128))
        
        result = watermark_processor.add_image_watermark(
            img,
            watermark_image=wm_img,
            scale=0.5
        )
        
        assert result.size == (800, 600)

    def test_add_image_watermark_with_opacity(self, watermark_processor):
        """测试带透明度的图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        wm_img = Image.new("RGBA", (100, 50), color=(255, 0, 0, 255))
        
        result = watermark_processor.add_image_watermark(
            img,
            watermark_image=wm_img,
            opacity=0.3
        )
        
        assert result.size == (800, 600)

    def test_add_image_watermark_different_positions(self, watermark_processor):
        """测试不同位置的图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        wm_img = Image.new("RGBA", (100, 50), color=(255, 0, 0, 128))
        
        for position in WatermarkPosition:
            result = watermark_processor.add_image_watermark(
                img,
                watermark_image=wm_img,
                position=position
            )
            assert result.size == (800, 600)

    def test_add_image_watermark_repeat(self, watermark_processor):
        """测试平铺图片水印"""
        img = Image.new("RGB", (800, 600), color="white")
        wm_img = Image.new("RGBA", (50, 30), color=(0, 255, 0, 128))
        
        result = watermark_processor.add_image_watermark(
            img,
            watermark_image=wm_img,
            repeat=True,
            repeat_spacing=100
        )
        
        assert result.size == (800, 600)

    def test_calculate_position(self, watermark_processor):
        """测试计算位置"""
        image_size = (800, 600)
        item_size = (100, 50)
        padding = 20
        
        pos = watermark_processor._calculate_position(
            image_size, item_size, WatermarkPosition.TOP_LEFT, padding
        )
        assert pos == (20, 20)
        
        pos = watermark_processor._calculate_position(
            image_size, item_size, WatermarkPosition.TOP_RIGHT, padding
        )
        assert pos == (680, 20)
        
        pos = watermark_processor._calculate_position(
            image_size, item_size, WatermarkPosition.BOTTOM_LEFT, padding
        )
        assert pos == (20, 530)
        
        pos = watermark_processor._calculate_position(
            image_size, item_size, WatermarkPosition.BOTTOM_RIGHT, padding
        )
        assert pos == (680, 530)
        
        pos = watermark_processor._calculate_position(
            image_size, item_size, WatermarkPosition.CENTER, padding
        )
        assert pos == (350, 275)

    def test_add_text_watermark_rgba_image(self, watermark_processor):
        """测试在RGBA图片上添加文字水印"""
        img = Image.new("RGBA", (800, 600), color=(255, 255, 255, 255))
        result = watermark_processor.add_text_watermark(
            img,
            text="Test"
        )
        
        assert result.mode == "RGBA"

    def test_add_image_watermark_rgba_image(self, watermark_processor):
        """测试在RGBA图片上添加图片水印"""
        img = Image.new("RGBA", (800, 600), color=(255, 255, 255, 255))
        wm_img = Image.new("RGBA", (100, 50), color=(255, 0, 0, 128))
        
        result = watermark_processor.add_image_watermark(img, watermark_image=wm_img)
        
        assert result.mode == "RGBA"
