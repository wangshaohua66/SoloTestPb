"""
EXIF信息处理模块
用于读取、保留和清除图片的EXIF信息
"""

from typing import Optional, Union, Dict, Any
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class ExifHandler:
    """EXIF信息处理类"""

    def __init__(self):
        """初始化EXIF处理器"""
        pass

    def read_exif(self, image: Union[str, Path, Image.Image]) -> Optional[Dict[str, Any]]:
        """
        读取图片的EXIF信息

        参数:
            image: 图片路径或PIL图片对象

        返回:
            dict: 解析后的EXIF信息字典，如果没有EXIF则返回None
        """
        if isinstance(image, (str, Path)):
            img = Image.open(image)
        else:
            img = image

        try:
            exif_data = img._getexif()
        except AttributeError:
            return None

        if not exif_data:
            return None

        parsed_exif = {}

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            
            if tag == "GPSInfo":
                gps_data = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag] = gps_value
                parsed_exif[tag] = gps_data
            else:
                parsed_exif[tag] = value

        return parsed_exif

    def get_exif_bytes(self, image: Union[str, Path, Image.Image]) -> Optional[bytes]:
        """
        获取图片的原始EXIF字节数据

        参数:
            image: 图片路径或PIL图片对象

        返回:
            bytes: EXIF原始字节数据，如果没有则返回None
        """
        if isinstance(image, (str, Path)):
            img = Image.open(image)
        else:
            img = image

        try:
            return img.info.get("exif")
        except Exception:
            return None

    def copy_exif(
        self,
        source_image: Union[str, Path, Image.Image],
        target_image: Image.Image
    ) -> Image.Image:
        """
        从源图片复制EXIF信息到目标图片

        参数:
            source_image: 源图片路径或PIL图片对象
            target_image: 目标PIL图片对象

        返回:
            PIL.Image.Image: 带有EXIF信息的目标图片
        """
        exif_bytes = self.get_exif_bytes(source_image)
        
        if exif_bytes:
            target_image.info["exif"] = exif_bytes
        
        return target_image

    def strip_exif(self, image: Image.Image) -> Image.Image:
        """
        清除图片的EXIF信息

        参数:
            image: PIL图片对象

        返回:
            PIL.Image.Image: 清除EXIF后的图片
        """
        if "exif" in image.info:
            del image.info["exif"]
        
        new_image = image.copy()
        new_image.info = {}
        
        return new_image

    def has_exif(self, image: Union[str, Path, Image.Image]) -> bool:
        """
        检查图片是否包含EXIF信息

        参数:
            image: 图片路径或PIL图片对象

        返回:
            bool: 是否包含EXIF信息
        """
        return self.get_exif_bytes(image) is not None

    def get_image_orientation(self, image: Union[str, Path, Image.Image]) -> int:
        """
        获取图片的方向信息

        参数:
            image: 图片路径或PIL图片对象

        返回:
            int: 方向值 (1-8)，默认为1（正常方向）
        """
        exif = self.read_exif(image)
        
        if exif and "Orientation" in exif:
            return exif["Orientation"]
        
        return 1

    def apply_orientation(self, image: Image.Image) -> Image.Image:
        """
        根据EXIF方向信息自动旋转图片

        参数:
            image: PIL图片对象

        返回:
            PIL.Image.Image: 旋转后的图片
        """
        orientation = self.get_image_orientation(image)
        
        orientation_map = {
            1: None,
            2: Image.FLIP_LEFT_RIGHT,
            3: Image.ROTATE_180,
            4: Image.FLIP_TOP_BOTTOM,
            5: [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],
            6: Image.ROTATE_270,
            7: [Image.FLIP_LEFT_RIGHT, Image.ROTATE_270],
            8: Image.ROTATE_90,
        }

        transform = orientation_map.get(orientation)
        
        if transform is None:
            return image
        
        if isinstance(transform, list):
            result = image
            for t in transform:
                result = result.transpose(t)
            return result
        
        return image.transpose(transform)

    def format_exif_for_display(self, exif_data: Dict[str, Any]) -> str:
        """
        将EXIF数据格式化为可读字符串

        参数:
            exif_data: EXIF数据字典

        返回:
            str: 格式化的字符串
        """
        lines = []
        
        for key, value in sorted(exif_data.items()):
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in sorted(value.items()):
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
