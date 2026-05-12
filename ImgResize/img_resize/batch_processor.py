"""
批量处理模块
使用concurrent.futures实现并发图片处理
"""

from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Union, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import time
import logging

from .image_processor import ImageProcessor, ImageFormat, ResizeMode
from .watermark import Watermark, WatermarkPosition
from .exif_handler import ExifHandler


logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """处理配置类"""
    width: Optional[int] = None
    height: Optional[int] = None
    resize_mode: ResizeMode = ResizeMode.FIT
    scale: Optional[float] = None
    quality: int = 85
    output_format: Optional[ImageFormat] = None
    keep_exif: bool = True
    auto_orient: bool = True
    
    text_watermark: Optional[str] = None
    text_watermark_position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT
    text_watermark_font: Optional[str] = None
    text_watermark_font_size: int = 36
    text_watermark_color: Tuple[int, int, int, int] = (255, 255, 255, 128)
    text_watermark_opacity: float = 0.5
    
    image_watermark: Optional[Union[str, Path]] = None
    image_watermark_position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT
    image_watermark_opacity: float = 0.5
    image_watermark_scale: float = 1.0


@dataclass
class ProcessingResult:
    """处理结果类"""
    input_path: Path
    output_path: Optional[Path] = None
    success: bool = True
    error_message: Optional[str] = None
    processing_time: float = 0.0
    original_size: int = 0
    output_size: int = 0


@dataclass
class BatchResult:
    """批量处理结果类"""
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_time: float = 0.0
    results: List[ProcessingResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count * 100
    
    @property
    def average_time(self) -> float:
        """平均处理时间"""
        if self.success_count == 0:
            return 0.0
        return sum(r.processing_time for r in self.results if r.success) / self.success_count


class BatchProcessor:
    """批量处理器"""

    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = True
    ):
        """
        初始化批量处理器

        参数:
            max_workers: 最大并发数，默认为CPU核心数
            use_processes: 是否使用多进程，为False时使用多线程
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.image_processor = ImageProcessor()
        self.watermark = Watermark()
        self.exif_handler = ExifHandler()

    def get_image_files(
        self,
        input_dir: Union[str, Path],
        recursive: bool = True
    ) -> List[Path]:
        """
        获取目录中所有支持的图片文件

        参数:
            input_dir: 输入目录
            recursive: 是否递归查找子目录

        返回:
            List[Path]: 图片文件路径列表
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        if not input_dir.is_dir():
            raise NotADirectoryError(f"路径不是目录: {input_dir}")

        pattern = "**/*" if recursive else "*"
        image_files = []

        for file_path in input_dir.glob(pattern):
            if file_path.is_file() and ImageProcessor.is_supported_format(file_path):
                image_files.append(file_path)

        return sorted(image_files)

    def process_single_image(
        self,
        input_path: Path,
        output_path: Path,
        config: ProcessingConfig
    ) -> ProcessingResult:
        """
        处理单张图片

        参数:
            input_path: 输入图片路径
            output_path: 输出图片路径
            config: 处理配置

        返回:
            ProcessingResult: 处理结果
        """
        start_time = time.time()
        result = ProcessingResult(input_path=input_path)

        try:
            original_size = input_path.stat().st_size
            result.original_size = original_size

            image = self.image_processor.load_image(input_path)

            if config.auto_orient:
                image = self.exif_handler.apply_orientation(image)

            if config.scale is not None:
                image = self.image_processor.scale_image(image, config.scale)
            elif config.width is not None or config.height is not None:
                image = self.image_processor.resize_image(
                    image,
                    width=config.width,
                    height=config.height,
                    mode=config.resize_mode
                )

            if config.text_watermark:
                image = self.watermark.add_text_watermark(
                    image,
                    text=config.text_watermark,
                    position=config.text_watermark_position,
                    font_path=config.text_watermark_font,
                    font_size=config.text_watermark_font_size,
                    color=config.text_watermark_color,
                    opacity=config.text_watermark_opacity
                )

            if config.image_watermark:
                image = self.watermark.add_image_watermark(
                    image,
                    watermark_image=config.image_watermark,
                    position=config.image_watermark_position,
                    opacity=config.image_watermark_opacity,
                    scale=config.image_watermark_scale
                )

            if config.keep_exif:
                image = self.exif_handler.copy_exif(input_path, image)
            else:
                image = self.exif_handler.strip_exif(image)

            save_format = config.output_format
            self.image_processor.save_image(
                image,
                output_path,
                quality=config.quality,
                format=save_format
            )

            result.output_path = output_path
            result.output_size = output_path.stat().st_size

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"处理图片失败: {input_path}, 错误: {e}")

        result.processing_time = time.time() - start_time
        return result

    def _get_output_path(
        self,
        input_path: Path,
        input_dir: Path,
        output_dir: Path,
        config: ProcessingConfig
    ) -> Path:
        """
        计算输出文件路径

        参数:
            input_path: 输入文件路径
            input_dir: 输入目录
            output_dir: 输出目录
            config: 处理配置

        返回:
            Path: 输出文件路径
        """
        relative_path = input_path.relative_to(input_dir)
        
        if config.output_format:
            ext = f".{config.output_format.value.lower()}"
            relative_path = relative_path.with_suffix(ext)
        
        return output_dir / relative_path

    def process_batch(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        config: ProcessingConfig,
        recursive: bool = True,
        progress_callback: Optional[Callable[[int, int, ProcessingResult], None]] = None
    ) -> BatchResult:
        """
        批量处理图片

        参数:
            input_dir: 输入目录
            output_dir: 输出目录
            config: 处理配置
            recursive: 是否递归处理子目录
            progress_callback: 进度回调函数，参数为(当前索引, 总数, 当前结果)

        返回:
            BatchResult: 批量处理结果
        """
        total_start_time = time.time()

        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        image_files = self.get_image_files(input_dir, recursive)
        batch_result = BatchResult(total_count=len(image_files))

        if not image_files:
            logger.warning("没有找到可处理的图片文件")
            return batch_result

        output_dir.mkdir(parents=True, exist_ok=True)

        tasks = [
            (
                input_path,
                self._get_output_path(input_path, input_dir, output_dir, config),
                config
            )
            for input_path in image_files
        ]

        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.process_single_image, *task): task
                for task in tasks
            }

            completed = 0
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                except Exception as e:
                    task = future_to_task[future]
                    result = ProcessingResult(
                        input_path=task[0],
                        success=False,
                        error_message=str(e)
                    )
                    logger.error(f"任务执行异常: {task[0]}, 错误: {e}")

                batch_result.results.append(result)
                
                if result.success:
                    batch_result.success_count += 1
                else:
                    batch_result.failed_count += 1

                completed += 1
                if progress_callback:
                    progress_callback(completed, len(image_files), result)

        batch_result.total_time = time.time() - total_start_time

        logger.info(
            f"批量处理完成: 总数={batch_result.total_count}, "
            f"成功={batch_result.success_count}, "
            f"失败={batch_result.failed_count}, "
            f"耗时={batch_result.total_time:.2f}秒"
        )

        return batch_result


def _process_single_image_worker(args):
    """
    进程池工作函数（需要在模块级别定义以支持序列化）
    """
    input_path, output_path, config_dict = args
    
    config = ProcessingConfig(**config_dict)
    processor = BatchProcessor()
    return processor.process_single_image(input_path, output_path, config)
