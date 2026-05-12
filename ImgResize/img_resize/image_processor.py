"""
图像处理核心模块
提供图片尺寸调整、缩放、压缩、格式转换等功能
"""

from pathlib import Path
from typing import Tuple, Optional, Union
from enum import Enum
from PIL import Image, ImageOps


class ImageFormat(str, Enum):
    """支持的图片格式枚举"""
    JPG = "JPG"
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    GIF = "GIF"


class ResizeMode(str, Enum):
    """缩放模式枚举"""
    EXACT = "exact"
    FIT = "fit"
    CONTAIN = "contain"
    COVER = "cover"


class ImageProcessor:
    """图片处理类"""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def __init__(self):
        """初始化图片处理器"""
        pass

    def load_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        加载图片

        参数:
            image_path: 图片路径

        返回:
            PIL.Image.Image: 加载的图片对象

        异常:
            FileNotFoundError: 文件不存在
            IOError: 文件无法打开
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")
        
        return Image.open(image_path)

    def save_image(
        self,
        image: Image.Image,
        output_path: Union[str, Path],
        quality: int = 85,
        optimize: bool = True,
        format: Optional[ImageFormat] = None
    ) -> None:
        """
        保存图片

        参数:
            image: PIL图片对象
            output_path: 输出路径
            quality: 保存质量 (1-100)
            optimize: 是否优化
            format: 输出格式，若为None则根据扩展名判断
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format is None:
            ext = output_path.suffix.lower()
            if ext in [".jpg", ".jpeg"]:
                save_format = "JPEG"
            elif ext == ".png":
                save_format = "PNG"
            elif ext == ".webp":
                save_format = "WEBP"
            elif ext == ".gif":
                save_format = "GIF"
            else:
                save_format = image.format or "JPEG"
        else:
            save_format = format.value
            if save_format == "JPG":
                save_format = "JPEG"

        save_kwargs = {
            "format": save_format,
            "optimize": optimize,
        }

        if save_format in ["JPEG", "WEBP"]:
            save_kwargs["quality"] = quality
            if image.mode in ("RGBA", "P") and save_format == "JPEG":
                image = self._convert_to_rgb(image)

        if save_format == "GIF":
            if image.mode != "P":
                image = image.convert("P", palette=Image.ADAPTIVE)
            save_kwargs["save_all"] = True

        image.save(output_path, **save_kwargs)

    def _convert_to_rgb(self, image: Image.Image) -> Image.Image:
        """
        将图片转换为RGB模式（用于JPEG等不支持透明通道的格式）

        参数:
            image: PIL图片对象

        返回:
            PIL.Image.Image: 转换后的图片
        """
        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        ):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1])
            return background
        return image.convert("RGB")

    def resize_image(
        self,
        image: Image.Image,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mode: ResizeMode = ResizeMode.EXACT,
        resample: int = Image.LANCZOS
    ) -> Image.Image:
        """
        调整图片尺寸

        参数:
            image: PIL图片对象
            width: 目标宽度，为None时根据高度等比例计算
            height: 目标高度，为None时根据宽度等比例计算
            mode: 缩放模式
                - EXACT: 强制调整到指定尺寸
                - FIT: 按比例缩放以适应尺寸
                - CONTAIN: 等比缩放，不超过指定尺寸
                - COVER: 等比缩放，覆盖指定尺寸并裁剪
            resample: 重采样方法

        返回:
            PIL.Image.Image: 调整尺寸后的图片

        异常:
            ValueError: width和height同时为None
        """
        if width is None and height is None:
            raise ValueError("width和height不能同时为None")
        
        if width is not None and width <= 0:
            raise ValueError("width必须大于0")
        if height is not None and height <= 0:
            raise ValueError("height必须大于0")

        original_width, original_height = image.size

        if mode == ResizeMode.EXACT:
            target_width = width or original_width
            target_height = height or original_height
            return image.resize((target_width, target_height), resample=resample)

        elif mode == ResizeMode.FIT:
            if width is None:
                ratio = height / original_height
                target_width = int(original_width * ratio)
                target_height = height
            elif height is None:
                ratio = width / original_width
                target_width = width
                target_height = int(original_height * ratio)
            else:
                width_ratio = width / original_width
                height_ratio = height / original_height
                ratio = min(width_ratio, height_ratio)
                target_width = int(original_width * ratio)
                target_height = int(original_height * ratio)

            return image.resize((target_width, target_height), resample=resample)

        elif mode == ResizeMode.CONTAIN:
            if width is None or height is None:
                return self.resize_image(image, width, height, ResizeMode.FIT, resample)
            
            width_ratio = width / original_width
            height_ratio = height / original_height
            ratio = min(width_ratio, height_ratio)
            target_width = int(original_width * ratio)
            target_height = int(original_height * ratio)

            return image.resize((target_width, target_height), resample=resample)

        elif mode == ResizeMode.COVER:
            if width is None or height is None:
                raise ValueError("COVER模式需要同时指定width和height")
            
            width_ratio = width / original_width
            height_ratio = height / original_height
            ratio = max(width_ratio, height_ratio)
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            resized = image.resize((new_width, new_height), resample=resample)
            
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            return resized.crop((left, top, right, bottom))

        return image

    def scale_image(
        self,
        image: Image.Image,
        scale: float,
        resample: int = Image.LANCZOS
    ) -> Image.Image:
        """
        按比例缩放图片

        参数:
            image: PIL图片对象
            scale: 缩放比例 (例如: 0.5表示缩小一半, 2表示放大一倍)
            resample: 重采样方法

        返回:
            PIL.Image.Image: 缩放后的图片

        异常:
            ValueError: scale小于等于0
        """
        if scale <= 0:
            raise ValueError("缩放比例必须大于0")

        if scale == 1.0:
            return image

        original_width, original_height = image.size
        target_width = int(original_width * scale)
        target_height = int(original_height * scale)

        return image.resize((target_width, target_height), resample=resample)

    def prepare_for_format(
        self,
        image: Image.Image,
        target_format: ImageFormat
    ) -> Image.Image:
        """
        为目标格式准备图片（转换为合适的模式）

        说明:
            实际的格式转换发生在save_image方法中。
            此方法仅转换图片模式，使其适合目标格式。

        参数:
            image: PIL图片对象
            target_format: 目标格式

        返回:
            PIL.Image.Image: 转换模式后的图片
        """
        if target_format in [ImageFormat.JPG, ImageFormat.JPEG]:
            return self._convert_to_rgb(image)
        elif target_format == ImageFormat.PNG:
            if image.mode != "RGBA":
                return image.convert("RGBA")
        elif target_format == ImageFormat.GIF:
            if image.mode != "P":
                return image.convert("P", palette=Image.ADAPTIVE)
        
        return image

    def compress_and_save(
        self,
        image: Image.Image,
        output_path: Union[str, Path],
        quality: int = 85,
        format: Optional[ImageFormat] = None
    ) -> None:
        """
        压缩并保存图片

        说明:
            PIL的压缩是在保存时通过quality参数实现的。
            此方法统一处理压缩和保存。

        参数:
            image: PIL图片对象
            output_path: 输出路径
            quality: 压缩质量 (1-100)，越小压缩比越高
            format: 输出格式，若为None则根据扩展名判断

        异常:
            ValueError: quality不在1-100范围内
        """
        if not (1 <= quality <= 100):
            raise ValueError("质量参数必须在1-100范围内")

        self.save_image(image, output_path, quality=quality, format=format)

    def validate_quality(self, quality: int) -> int:
        """
        验证并返回质量参数

        参数:
            quality: 质量值 (1-100)

        返回:
            int: 验证后的质量值

        异常:
            ValueError: quality不在1-100范围内
        """
        if not (1 <= quality <= 100):
            raise ValueError("质量参数必须在1-100范围内")
        return quality

    def estimate_compression_ratio(self, quality: int) -> float:
        """
        估算给定质量参数对应的压缩比

        参数:
            quality: 质量值 (1-100)

        返回:
            float: 估算的文件大小比例 (相对于原文件)
        """
        if quality >= 90:
            return 0.9
        elif quality >= 70:
            return 0.6
        elif quality >= 50:
            return 0.4
        elif quality >= 30:
            return 0.25
        else:
            return 0.15

    def get_image_info(self, image: Image.Image) -> dict:
        """
        获取图片信息

        参数:
            image: PIL图片对象

        返回:
            dict: 图片信息字典，包含尺寸、模式、格式等
        """
        return {
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
            "info": image.info
        }

    @classmethod
    def is_supported_format(cls, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否是支持的图片格式

        参数:
            file_path: 文件路径

        返回:
            bool: 是否支持
        """
        return Path(file_path).suffix.lower() in cls.SUPPORTED_FORMATS
