"""
命令行接口模块
提供基于argparse的命令行交互
"""

import argparse
import sys
import logging
from pathlib import Path

from .batch_processor import BatchProcessor, ProcessingConfig, BatchResult
from .image_processor import ImageFormat, ResizeMode
from .watermark import WatermarkPosition


def setup_logging(verbose: bool = False) -> None:
    """
    设置日志

    参数:
        verbose: 是否显示详细日志
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )


def parse_args(args=None) -> argparse.Namespace:
    """
    解析命令行参数

    参数:
        args: 参数列表，为None时使用sys.argv

    返回:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="图片批量压缩调整工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 调整所有图片为宽度800px，保持比例
  img-resize -i ./input -o ./output --width 800
  
  # 按比例缩小50%
  img-resize -i ./input -o ./output --scale 0.5
  
  # 转换为WebP格式，质量80%
  img-resize -i ./input -o ./output --format webp --quality 80
  
  # 添加文字水印
  img-resize -i ./input -o ./output --text-watermark "Copyright"
  
  # 清除EXIF信息
  img-resize -i ./input -o ./output --no-exif
        """
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入目录路径"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="输出目录路径"
    )

    resize_group = parser.add_argument_group("尺寸调整")
    resize_group.add_argument(
        "--width",
        type=int,
        default=None,
        help="目标宽度（像素）"
    )
    resize_group.add_argument(
        "--height",
        type=int,
        default=None,
        help="目标高度（像素）"
    )
    resize_group.add_argument(
        "--scale",
        type=float,
        default=None,
        help="缩放比例（例如：0.5表示缩小50%，2表示放大1倍）"
    )
    resize_group.add_argument(
        "--resize-mode",
        type=str,
        default="fit",
        choices=["exact", "fit", "contain", "cover"],
        help="缩放模式 (默认: fit)"
    )

    format_group = parser.add_argument_group("格式与压缩")
    format_group.add_argument(
        "--format",
        type=str,
        default=None,
        choices=["jpg", "jpeg", "png", "webp", "gif"],
        help="输出格式（不指定则保持原格式）"
    )
    format_group.add_argument(
        "--quality",
        type=int,
        default=85,
        help="输出质量 (1-100，默认: 85)"
    )

    watermark_group = parser.add_argument_group("水印")
    watermark_group.add_argument(
        "--text-watermark",
        type=str,
        default=None,
        help="文字水印内容"
    )
    watermark_group.add_argument(
        "--text-watermark-position",
        type=str,
        default="bottom_right",
        choices=[
            "top_left", "top_center", "top_right",
            "center_left", "center", "center_right",
            "bottom_left", "bottom_center", "bottom_right"
        ],
        help="文字水印位置 (默认: bottom_right)"
    )
    watermark_group.add_argument(
        "--text-watermark-font-size",
        type=int,
        default=36,
        help="文字水印字体大小 (默认: 36)"
    )
    watermark_group.add_argument(
        "--text-watermark-opacity",
        type=float,
        default=0.5,
        help="文字水印透明度 (0.0-1.0，默认: 0.5)"
    )
    watermark_group.add_argument(
        "--image-watermark",
        type=str,
        default=None,
        help="图片水印路径"
    )
    watermark_group.add_argument(
        "--image-watermark-position",
        type=str,
        default="bottom_right",
        choices=[
            "top_left", "top_center", "top_right",
            "center_left", "center", "center_right",
            "bottom_left", "bottom_center", "bottom_right"
        ],
        help="图片水印位置 (默认: bottom_right)"
    )
    watermark_group.add_argument(
        "--image-watermark-opacity",
        type=float,
        default=0.5,
        help="图片水印透明度 (0.0-1.0，默认: 0.5)"
    )
    watermark_group.add_argument(
        "--image-watermark-scale",
        type=float,
        default=1.0,
        help="图片水印缩放比例 (默认: 1.0)"
    )

    exif_group = parser.add_argument_group("EXIF")
    exif_group.add_argument(
        "--no-exif",
        action="store_true",
        default=False,
        help="清除EXIF信息（默认保留）"
    )
    exif_group.add_argument(
        "--no-auto-orient",
        action="store_true",
        default=False,
        help="不自动根据EXIF方向旋转图片"
    )

    processing_group = parser.add_argument_group("处理选项")
    processing_group.add_argument(
        "--workers",
        type=int,
        default=None,
        help="并发工作数（默认使用CPU核心数）"
    )
    processing_group.add_argument(
        "--use-threads",
        action="store_true",
        default=False,
        help="使用多线程而非多进程"
    )
    processing_group.add_argument(
        "--no-recursive",
        action="store_true",
        default=False,
        help="不递归处理子目录"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="显示详细日志"
    )

    return parser.parse_args(args)


def create_config_from_args(args: argparse.Namespace) -> ProcessingConfig:
    """
    从命令行参数创建处理配置

    参数:
        args: 解析后的命令行参数

    返回:
        ProcessingConfig: 处理配置
    """
    output_format = None
    if args.format:
        output_format = ImageFormat(args.format.upper())

    return ProcessingConfig(
        width=args.width,
        height=args.height,
        resize_mode=ResizeMode(args.resize_mode),
        scale=args.scale,
        quality=args.quality,
        output_format=output_format,
        keep_exif=not args.no_exif,
        auto_orient=not args.no_auto_orient,
        text_watermark=args.text_watermark,
        text_watermark_position=WatermarkPosition(args.text_watermark_position),
        text_watermark_font_size=args.text_watermark_font_size,
        text_watermark_opacity=args.text_watermark_opacity,
        image_watermark=args.image_watermark,
        image_watermark_position=WatermarkPosition(args.image_watermark_position),
        image_watermark_opacity=args.image_watermark_opacity,
        image_watermark_scale=args.image_watermark_scale,
    )


def print_progress(current: int, total: int, result) -> None:
    """
    打印处理进度

    参数:
        current: 当前处理数量
        total: 总数量
        result: 处理结果
    """
    status = "✓" if result.success else "✗"
    filename = result.input_path.name
    percent = current / total * 100
    
    if result.success:
        compression = ""
        if result.original_size > 0 and result.output_size > 0:
            ratio = (1 - result.output_size / result.original_size) * 100
            compression = f" ({ratio:+.1f}%)"
        
        print(
            f"[{current}/{total}] {status} {filename}"
            f"{compression} - {result.processing_time:.2f}s"
        )
    else:
        print(f"[{current}/{total}] {status} {filename} - 错误: {result.error_message}")


def print_summary(result: BatchResult) -> None:
    """
    打印处理结果摘要

    参数:
        result: 批量处理结果
    """
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
    print(f"总文件数: {result.total_count}")
    print(f"成功: {result.success_count}")
    print(f"失败: {result.failed_count}")
    print(f"成功率: {result.success_rate:.1f}%")
    print(f"总耗时: {result.total_time:.2f} 秒")
    print(f"平均耗时: {result.average_time:.2f} 秒/张")
    
    if result.failed_count > 0:
        print("\n失败文件:")
        for r in result.results:
            if not r.success:
                print(f"  - {r.input_path}: {r.error_message}")


def main(args=None) -> int:
    """
    主函数

    参数:
        args: 命令行参数，为None时使用sys.argv

    返回:
        int: 退出码
    """
    parsed_args = parse_args(args)
    setup_logging(parsed_args.verbose)

    logger = logging.getLogger(__name__)

    try:
        input_dir = Path(parsed_args.input)
        output_dir = Path(parsed_args.output)

        if not input_dir.exists():
            print(f"错误: 输入目录不存在: {input_dir}", file=sys.stderr)
            return 1

        config = create_config_from_args(parsed_args)

        processor = BatchProcessor(
            max_workers=parsed_args.workers,
            use_processes=not parsed_args.use_threads
        )

        print(f"开始处理: {input_dir} -> {output_dir}")
        print("-" * 60)

        result = processor.process_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            config=config,
            recursive=not parsed_args.no_recursive,
            progress_callback=print_progress
        )

        print_summary(result)

        return 0 if result.failed_count == 0 else 1

    except KeyboardInterrupt:
        print("\n用户中断操作", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=parsed_args.verbose)
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
