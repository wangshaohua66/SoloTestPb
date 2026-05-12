"""
水印处理模块
支持文字水印和图片水印
"""

from typing import Tuple, Optional, Union
from enum import Enum
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class WatermarkPosition(str, Enum):
    """水印位置枚举"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class Watermark:
    """水印处理类"""

    def __init__(self):
        """初始化水印处理器"""
        pass

    def add_text_watermark(
        self,
        image: Image.Image,
        text: str,
        position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
        font_path: Optional[Union[str, Path]] = None,
        font_size: int = 36,
        color: Tuple[int, int, int, int] = (255, 255, 255, 128),
        opacity: float = 0.5,
        padding: int = 20,
        angle: float = 0,
        repeat: bool = False,
        repeat_spacing: int = 200
    ) -> Image.Image:
        """
        添加文字水印

        参数:
            image: PIL图片对象
            text: 水印文字内容
            position: 水印位置
            font_path: 字体文件路径，为None时使用默认字体
            font_size: 字体大小
            color: 文字颜色 (RGBA)
            opacity: 透明度 (0.0-1.0)
            padding: 边距（像素）
            angle: 旋转角度
            repeat: 是否平铺水印
            repeat_spacing: 平铺间隔

        返回:
            PIL.Image.Image: 添加水印后的图片
        """
        if not text:
            return image

        original_mode = image.mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        alpha = int(color[3] * opacity) if len(color) == 4 else int(255 * opacity)
        fill_color = (color[0], color[1], color[2], alpha)

        try:
            if font_path:
                font = ImageFont.truetype(str(font_path), font_size)
            else:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)

        if repeat:
            return self._repeat_watermark(
                image, overlay, draw, text, font, fill_color,
                text_width, text_height, angle, repeat_spacing
            )

        pos_x, pos_y = self._calculate_position(
            image.size, (text_width, text_height), position, padding
        )

        if angle != 0:
            text_overlay = Image.new("RGBA", (text_width + 20, text_height + 20), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_overlay)
            text_draw.text((10, 10), text, font=font, fill=fill_color)
            rotated = text_overlay.rotate(angle, expand=True, resample=Image.BICUBIC)
            
            rw, rh = rotated.size
            pos_x = pos_x - (rw - text_width) // 2
            pos_y = pos_y - (rh - text_height) // 2
            
            overlay.paste(rotated, (pos_x, pos_y), rotated)
        else:
            draw.text((pos_x, pos_y), text, font=font, fill=fill_color)

        result = Image.alpha_composite(image, overlay)
        if original_mode != "RGBA":
            result = result.convert(original_mode)

        return result

    def _repeat_watermark(
        self,
        image: Image.Image,
        overlay: Image.Image,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        fill_color: Tuple[int, int, int, int],
        text_width: int,
        text_height: int,
        angle: float,
        spacing: int
    ) -> Image.Image:
        """
        平铺水印的内部方法
        """
        img_width, img_height = image.size

        step_x = text_width + spacing
        step_y = text_height + spacing

        for y in range(-step_y, img_height + step_y, step_y):
            for x in range(-step_x, img_width + step_x, step_x):
                if angle != 0:
                    text_overlay = Image.new(
                        "RGBA", (text_width + 20, text_height + 20), (0, 0, 0, 0)
                    )
                    text_draw = ImageDraw.Draw(text_overlay)
                    text_draw.text((10, 10), text, font=font, fill=fill_color)
                    rotated = text_overlay.rotate(angle, expand=True, resample=Image.BICUBIC)
                    overlay.paste(rotated, (x, y), rotated)
                else:
                    draw.text((x, y), text, font=font, fill=fill_color)

        result = Image.alpha_composite(image, overlay)
        if image.mode != "RGBA":
            result = result.convert(image.mode)

        return result

    def add_image_watermark(
        self,
        image: Image.Image,
        watermark_image: Union[str, Path, Image.Image],
        position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
        opacity: float = 0.5,
        scale: float = 1.0,
        padding: int = 20,
        repeat: bool = False,
        repeat_spacing: int = 200
    ) -> Image.Image:
        """
        添加图片水印

        参数:
            image: 目标图片
            watermark_image: 水印图片路径或PIL图片对象
            position: 水印位置
            opacity: 透明度 (0.0-1.0)
            scale: 水印缩放比例
            padding: 边距
            repeat: 是否平铺
            repeat_spacing: 平铺间隔

        返回:
            PIL.Image.Image: 添加水印后的图片
        """
        if isinstance(watermark_image, (str, Path)):
            wm = Image.open(watermark_image).convert("RGBA")
        else:
            wm = watermark_image.convert("RGBA")

        if scale != 1.0:
            new_size = (int(wm.width * scale), int(wm.height * scale))
            wm = wm.resize(new_size, Image.LANCZOS)

        if opacity < 1.0:
            alpha = wm.split()[3]
            alpha = alpha.point(lambda p: p * opacity)
            wm.putalpha(alpha)

        original_mode = image.mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if repeat:
            return self._repeat_image_watermark(
                image, wm, repeat_spacing
            )

        pos_x, pos_y = self._calculate_position(
            image.size, wm.size, position, padding
        )

        result = image.copy()
        result.paste(wm, (pos_x, pos_y), wm)

        if original_mode != "RGBA":
            result = result.convert(original_mode)

        return result

    def _repeat_image_watermark(
        self,
        image: Image.Image,
        wm: Image.Image,
        spacing: int
    ) -> Image.Image:
        """
        平铺图片水印的内部方法
        """
        img_width, img_height = image.size
        wm_width, wm_height = wm.size

        result = image.copy()
        step_x = wm_width + spacing
        step_y = wm_height + spacing

        for y in range(-step_y, img_height + step_y, step_y):
            for x in range(-step_x, img_width + step_x, step_x):
                result.paste(wm, (x, y), wm)

        if image.mode != "RGBA":
            result = result.convert(image.mode)

        return result

    def _calculate_position(
        self,
        image_size: Tuple[int, int],
        item_size: Tuple[int, int],
        position: WatermarkPosition,
        padding: int
    ) -> Tuple[int, int]:
        """
        计算水印位置

        参数:
            image_size: 图片尺寸 (width, height)
            item_size: 水印尺寸 (width, height)
            position: 位置枚举
            padding: 边距

        返回:
            Tuple[int, int]: (x, y) 坐标
        """
        img_width, img_height = image_size
        item_width, item_height = item_size

        positions = {
            WatermarkPosition.TOP_LEFT: (padding, padding),
            WatermarkPosition.TOP_CENTER: ((img_width - item_width) // 2, padding),
            WatermarkPosition.TOP_RIGHT: (img_width - item_width - padding, padding),
            WatermarkPosition.CENTER_LEFT: (padding, (img_height - item_height) // 2),
            WatermarkPosition.CENTER: ((img_width - item_width) // 2, (img_height - item_height) // 2),
            WatermarkPosition.CENTER_RIGHT: (img_width - item_width - padding, (img_height - item_height) // 2),
            WatermarkPosition.BOTTOM_LEFT: (padding, img_height - item_height - padding),
            WatermarkPosition.BOTTOM_CENTER: ((img_width - item_width) // 2, img_height - item_height - padding),
            WatermarkPosition.BOTTOM_RIGHT: (img_width - item_width - padding, img_height - item_height - padding),
        }

        return positions.get(position, positions[WatermarkPosition.BOTTOM_RIGHT])
