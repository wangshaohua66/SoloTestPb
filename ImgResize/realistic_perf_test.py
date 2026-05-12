"""
真实场景性能测试脚本
生成带有内容的图片来模拟真实照片（渐变、文字、图形等）
"""

import time
import tempfile
import tracemalloc
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

from img_resize.batch_processor import BatchProcessor, ProcessingConfig
from img_resize.image_processor import ImageFormat, ResizeMode


def generate_realistic_image(
    size: tuple,
    complexity: str = "medium"
) -> Image.Image:
    """
    生成带有内容的图片模拟真实照片

    参数:
        size: (width, height)
        complexity: 'simple', 'medium', 'high'

    返回:
        PIL.Image.Image
    """
    width, height = size
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)

    # 绘制渐变背景（模拟天空/风景）
    for y in range(height):
        r = int(135 + (100 * y / height))
        g = int(180 + (50 * y / height))
        b = int(220 - (100 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 添加噪点（模拟照片噪点）
    noise_level = {"simple": 1000, "medium": 5000, "high": 20000}[complexity]
    for _ in range(noise_level):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b = img.getpixel((x, y))
        dr = random.randint(-10, 10)
        dg = random.randint(-10, 10)
        db = random.randint(-10, 10)
        draw.point(
            (x, y),
            fill=(
                max(0, min(255, r + dr)),
                max(0, min(255, g + dg)),
                max(0, min(255, b + db))
            )
        )

    # 绘制几何图形（模拟场景中的物体）
    for _ in range({"simple": 5, "medium": 15, "high": 30}[complexity]):
        x1 = random.randint(0, width - 100)
        y1 = random.randint(0, height - 100)
        x2 = x1 + random.randint(20, 200)
        y2 = y1 + random.randint(20, 200)
        
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        
        shape_type = random.choice(["rectangle", "ellipse"])
        if shape_type == "rectangle":
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=None)
        else:
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)

    # 添加文字水印（模拟照片中的文字）
    try:
        font = ImageFont.load_default()
    except:
        font = None

    if font and complexity != "simple":
        texts = ["Photo", "Image", "Test", "Sample", "2024", "Camera"]
        for _ in range({"medium": 3, "high": 8}[complexity] if complexity != "simple" else 0):
            x = random.randint(10, width - 100)
            y = random.randint(10, height - 50)
            text = random.choice(texts)
            text_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            draw.text((x, y), text, font=font, fill=text_color)

    # 绘制线条（模拟边缘）
    if complexity in ["medium", "high"]:
        for _ in range({"medium": 20, "high": 50}[complexity]):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            line_color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    return img


def generate_test_images(output_dir: Path, count: int = 100):
    """
    生成测试图片集（模拟真实照片场景）

    参数:
        output_dir: 输出目录
        count: 图片数量
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 模拟真实照片的常见尺寸
    photo_sizes = [
        (1920, 1080),   # Full HD
        (1280, 720),    # HD
        (1024, 768),    # XGA
        (800, 600),     # SVGA
        (2560, 1440),   # 2K
        (3840, 2160),   # 4K (少量)
    ]

    # 格式分布（模拟真实场景）
    format_distribution = {
        "JPEG": 0.6,    # 60% JPG
        "PNG": 0.25,    # 25% PNG
        "WEBP": 0.15,   # 15% WebP
    }

    # 复杂度分布
    complexities = ["simple", "medium", "high"]

    print(f"正在生成 {count} 张真实场景测试图片...")
    print("=" * 60)

    sizes_used = {}
    formats_used = {}

    for i in range(count):
        # 选择尺寸
        if i < count * 0.05:
            size = (3840, 2160)  # 5% 4K
        elif i < count * 0.15:
            size = (2560, 1440)  # 10% 2K
        else:
            size = random.choice([(1920, 1080), (1280, 720), (1024, 768), (800, 600)])

        sizes_used[size] = sizes_used.get(size, 0) + 1

        # 选择复杂度
        complexity = random.choices(complexities, weights=[0.3, 0.5, 0.2])[0]

        # 生成图片
        img = generate_realistic_image(size, complexity)

        # 选择格式
        rand_val = random.random()
        if rand_val < format_distribution["JPEG"]:
            fmt = "JPEG"
            ext = ".jpg"
        elif rand_val < format_distribution["JPEG"] + format_distribution["PNG"]:
            fmt = "PNG"
            ext = ".png"
        else:
            fmt = "WEBP"
            ext = ".webp"

        formats_used[fmt] = formats_used.get(fmt, 0) + 1

        filepath = output_dir / f"photo_{i:03d}{ext}"

        # 保存图片（模拟不同质量的照片）
        if fmt == "JPEG":
            quality = random.randint(70, 95)
            img.save(filepath, "JPEG", quality=quality, optimize=True)
        elif fmt == "PNG":
            img.save(filepath, "PNG", optimize=True)
        else:
            quality = random.randint(70, 95)
            img.save(filepath, "WEBP", quality=quality)

        if (i + 1) % 20 == 0:
            print(f"  已生成 {i + 1}/{count} 张")

    # 统计信息
    total_size = sum(f.stat().st_size for f in output_dir.iterdir())

    print("=" * 60)
    print("图片生成统计:")
    print(f"  总数量: {count} 张")
    print(f"  总大小: {total_size / (1024 * 1024):.2f} MB")
    print(f"  平均大小: {total_size / count / 1024:.2f} KB/张")
    print(f"\n  尺寸分布:")
    for size, cnt in sorted(sizes_used.items()):
        print(f"    {size[0]}x{size[1]}: {cnt} 张 ({cnt/count*100:.1f}%)")
    print(f"\n  格式分布:")
    for fmt, cnt in sorted(formats_used.items()):
        print(f"    {fmt}: {cnt} 张 ({cnt/count*100:.1f}%)")

    return total_size


def run_realistic_performance_test(
    input_dir: Path,
    output_dir: Path,
    workers: int = None,
    test_name: str = "真实场景测试"
):
    """
    运行真实场景性能测试

    参数:
        input_dir: 输入目录
        output_dir: 输出目录
        workers: 并发数
        test_name: 测试名称

    返回:
        dict: 测试结果
    """
    print(f"\n{'='*60}")
    print(f"性能测试: {test_name}")
    print(f"{'='*60}")

    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 配置：模拟真实使用场景
    config = ProcessingConfig(
        width=1200,
        resize_mode=ResizeMode.FIT,
        quality=80,
        output_format=ImageFormat.JPG,
        keep_exif=False
    )

    processor = BatchProcessor(max_workers=workers, use_processes=False)

    # 开始监控内存
    tracemalloc.start()

    start_time = time.time()

    result = processor.process_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        config=config,
        recursive=False
    )

    total_time = time.time() - start_time

    # 获取内存使用
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 统计输出
    output_files = list(output_dir.iterdir())
    output_size = sum(f.stat().st_size for f in output_files)

    print(f"\n测试结果:")
    print(f"  总文件数: {result.total_count}")
    print(f"  成功: {result.success_count}")
    print(f"  失败: {result.failed_count}")
    print(f"  成功率: {result.success_rate:.1f}%")
    print(f"\n时间统计:")
    print(f"  总耗时: {total_time:.2f} 秒")
    print(f"  平均耗时: {result.average_time:.3f} 秒/张")
    print(f"  吞吐量: {result.success_count / total_time:.2f} 张/秒")
    print(f"\n大小统计:")
    print(f"  输出总大小: {output_size / (1024 * 1024):.2f} MB")
    print(f"  平均输出大小: {output_size / max(1, len(output_files)) / 1024:.2f} KB/张")
    print(f"\n内存使用:")
    print(f"  峰值内存: {peak / (1024 * 1024):.2f} MB")
    print(f"  当前内存: {current / (1024 * 1024):.2f} MB")

    passed = total_time <= 60 and result.success_count == result.total_count

    if passed:
        print(f"\n✓ 真实场景性能测试通过!")
        print(f"  100张真实场景图片处理时间: {total_time:.2f} 秒 ≤ 60 秒")
    else:
        print(f"\n✗ 真实场景性能测试未通过!")
        print(f"  100张真实场景图片处理时间: {total_time:.2f} 秒")

    return {
        "test_name": test_name,
        "total_time": total_time,
        "success_count": result.success_count,
        "failed_count": result.failed_count,
        "success_rate": result.success_rate,
        "average_time": result.average_time,
        "throughput": result.success_count / total_time if total_time > 0 else 0,
        "peak_memory_mb": peak / (1024 * 1024),
        "passed": passed,
        "workers": workers
    }


def main():
    """主函数"""
    print("=" * 60)
    print("ImgResize 真实场景性能测试")
    print("=" * 60)
    print("\n目标: 处理100张真实场景图片的时间 ≤ 60秒")
    print("测试内容: 带渐变、噪点、图形、文字的混合格式图片")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # 生成100张真实场景图片
        total_size = generate_test_images(input_dir, count=100)

        results = []

        # 运行测试
        results.append(run_realistic_performance_test(
            input_dir,
            output_dir / "workers_4",
            workers=4,
            test_name="4个并发线程"
        ))

        # 汇总
        print(f"\n{'='*60}")
        print("真实场景性能测试汇总")
        print(f"{'='*60}")

        print(f"\n测试配置:")
        print(f"  图片数量: 100 张")
        print(f"  输入大小: {total_size / (1024 * 1024):.2f} MB")
        print(f"  处理操作: 缩放至1200px + 质量80% + 转换为JPG")

        print(f"\n{'测试名称':<25} {'并发数':<10} {'耗时(秒)':<15} {'结果'}")
        print("-" * 65)

        all_passed = True
        for r in results:
            workers = r['workers'] if r['workers'] else "CPU"
            status = "✓ 通过" if r['passed'] else "✗ 失败"
            print(f"{r['test_name']:<25} {workers:<10} {r['total_time']:<15.2f} {status}")
            if not r['passed']:
                all_passed = False

        print("-" * 65)

        if all_passed:
            print("\n✓ 所有真实场景性能测试通过!")
            print("  验收标准: 100张图片 ≤ 60秒 ✓ 已满足")
            return 0
        else:
            print("\n✗ 部分真实场景性能测试未通过")
            return 1


if __name__ == "__main__":
    exit(main())
