"""
测试EXIF处理模块
"""

import pytest
from PIL import Image

from img_resize.exif_handler import ExifHandler


@pytest.fixture
def exif_handler():
    """创建ExifHandler实例"""
    return ExifHandler()


@pytest.fixture
def simple_image(tmp_path):
    """创建简单测试图片（无EXIF）"""
    img = Image.new("RGB", (100, 100), color="red")
    img_path = tmp_path / "test.jpg"
    img.save(img_path, "JPEG")
    return img_path


class TestExifHandler:
    """测试ExifHandler类"""

    def test_init(self, exif_handler):
        """测试初始化"""
        assert exif_handler is not None

    def test_read_exif_none(self, exif_handler, simple_image):
        """测试读取无EXIF的图片"""
        exif = exif_handler.read_exif(simple_image)
        assert exif is None or isinstance(exif, dict)

    def test_get_exif_bytes_none(self, exif_handler, simple_image):
        """测试获取无EXIF图片的EXIF字节"""
        exif_bytes = exif_handler.get_exif_bytes(simple_image)
        assert exif_bytes is None

    def test_has_exif_false(self, exif_handler, simple_image):
        """测试检查无EXIF图片"""
        assert exif_handler.has_exif(simple_image) is False

    def test_get_image_orientation_default(self, exif_handler, simple_image):
        """测试获取默认方向"""
        orientation = exif_handler.get_image_orientation(simple_image)
        assert orientation == 1

    def test_apply_orientation_default(self, exif_handler):
        """测试应用默认方向（无变换）"""
        img = Image.new("RGB", (100, 200), color="red")
        result = exif_handler.apply_orientation(img)
        
        assert result is img

    def test_copy_exif_none(self, exif_handler):
        """测试复制无EXIF的图片"""
        source = Image.new("RGB", (100, 100), color="red")
        target = Image.new("RGB", (50, 50), color="blue")
        
        result = exif_handler.copy_exif(source, target)
        assert result is target

    def test_strip_exif(self, exif_handler):
        """测试清除EXIF"""
        img = Image.new("RGB", (100, 100), color="red")
        img.info["exif"] = b"fake exif data"
        
        result = exif_handler.strip_exif(img)
        assert "exif" not in result.info

    def test_format_exif_for_display(self, exif_handler):
        """测试格式化EXIF显示"""
        exif_data = {
            "Make": "TestCamera",
            "Model": "TestModel",
            "GPSInfo": {
                "GPSLatitude": (0, 0, 0),
                "GPSLongitude": (0, 0, 0)
            }
        }
        
        formatted = exif_handler.format_exif_for_display(exif_data)
        
        assert "Make:" in formatted
        assert "Model:" in formatted
        assert "GPSInfo:" in formatted
        assert "GPSLatitude:" in formatted

    def test_read_exif_with_image_object(self, exif_handler):
        """测试从PIL对象读取EXIF"""
        img = Image.new("RGB", (100, 100), color="red")
        exif = exif_handler.read_exif(img)
        assert exif is None or isinstance(exif, dict)

    def test_get_exif_bytes_with_image_object(self, exif_handler):
        """测试从PIL对象获取EXIF字节"""
        img = Image.new("RGB", (100, 100), color="red")
        exif_bytes = exif_handler.get_exif_bytes(img)
        assert exif_bytes is None

    def test_has_exif_with_image_object(self, exif_handler):
        """测试检查PIL对象是否有EXIF"""
        img = Image.new("RGB", (100, 100), color="red")
        assert exif_handler.has_exif(img) is False

    def test_get_image_orientation_with_image_object(self, exif_handler):
        """测试从PIL对象获取方向"""
        img = Image.new("RGB", (100, 100), color="red")
        orientation = exif_handler.get_image_orientation(img)
        assert orientation == 1
