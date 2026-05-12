"""
性能测试脚本
测试处理100张图片的时间，验证是否≤60秒
"""

import time
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import random

from img_resize.batch_processor import BatchProcessor, ProcessingConfig
from img_resize.image_processor import ImageFormat, ResizeMode


def generate_test_images(output_dir: Path, count: int = 100):
    """
    生成测试图片

    参数:
        output_dir: 输出目录
        count: 图片数量
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sizes = [
        (1920, 1080),
        (1280, 720),
        (1024, 768),
        (800, 600),
        (640, 480),
    ]
    
    formats = ["JPEG", "JPEG", "JPEG", "PNG", "WEBP"]
    
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 128, 128), (255, 128, 0), (128, 0, 255),
    ]
    
    print(f"正在生成 {count} 张测试图片...")
    
    for i in range(count):
        size = random.choice(sizes)
        fmt = random.choice(formats)
        color = random.choice(colors)
        
        img = Image.new("RGB", size, color=color)
        
        if fmt == "PNG":
            filename = f"image_{i:03d}.png"
        elif fmt == "WEBP":
            filename = f"image_{i:03d}.webp"
        else:
            filename = f"image_{i:03d}.jpg"
        
        filepath = output_dir / filename
        
        if fmt == "PNG":
            img.save(filepath, "PNG", optimize=True)
        elif fmt == "WEBP":
            img.save(filepath, "WEBP", quality=85)
        else:
            img.save(filepath, "JPEG", quality=90, optimize=True)
        
        if (i + 1) % 20 == 0:
            print(f"  已生成 {i + 1}/{count} 张")
    
    total_size = sum(f.stat().st_size for f in output_dir.iterdir())
    print(f"\n测试图片生成完成:")
    print(f"  数量: {count} 张")
    print(f"  总大小: {total_size / (1024 * 1024):.2f} MB")
    print(f"  平均大小: {total_size / count / 1024:.2f} KB/张")


def run_performance_test(
    input_dir: Path,
    output_dir: Path,
    workers: int = None,
    test_name: str = "默认配置"
):
    """
    运行性能测试

    参数:
        input_dir: 输入目录
        output_dir: 输出目录
        workers: 并发工作数
        test_name: 测试名称

    返回:
        dict: 测试结果
    """
    print(f"\n{'='*60}")
    print(f"性能测试: {test_name}")
    print(f"{'='*60}")
    
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = ProcessingConfig(
        width=800,
        quality=80,
        output_format=ImageFormat.JPG,
        keep_exif=False
    )
    
    processor = BatchProcessor(max_workers=workers, use_processes=True)
    
    start_time = time.time()
    
    result = processor.process_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        config=config,
        recursive=False
    )
    
    total_time = time.time() - start_time
    
    output_size = sum(f.stat().st_size for f in output_dir.iterdir() if f.is_file())
    
    print(f"\n测试结果:")
    print(f"  总文件数: {result.total_count}")
    print(f"  成功: {result.success_count}")
    print(f"  失败: {result.failed_count}")
    print(f"  成功率: {result.success_rate:.1f}%")
    print(f"  总耗时: {total_time:.2f} 秒")
    print(f"  平均耗时: {result.average_time:.3f} 秒/张")
    print(f"  输出总大小: {output_size / (1024 * 1024):.2f} MB")
    
    if total_time <= 60:
        print(f"\n✓ 性能测试通过: {total_time:.2f} 秒 ≤ 60 秒")
        passed = True
    else:
        print(f"\n✗ 性能测试失败: {total_time:.2f} 秒 > 60 秒")
        passed = False
    
    return {
        "test_name": test_name,
        "total_time": total_time,
        "success_count": result.success_count,
        "failed_count": result.failed_count,
        "success_rate": result.success_rate,
        "average_time": result.average_time,
        "passed": passed,
        "workers": workers
    }


def main():
    """主函数"""
    print("=" * 60)
    print("ImgResize 性能测试")
    print("=" * 60)
    print("\n目标: 处理100张图片的时间 ≤ 60秒")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        
        generate_test_images(input_dir, count=100)
        
        results = []
        
        results.append(run_performance_test(
            input_dir,
            output_dir / "default",
            workers=None,
            test_name="默认并发（CPU核心数）"
        ))
        
        results.append(run_performance_test(
            input_dir,
            output_dir / "workers_2",
            workers=2,
            test_name="2个并发进程"
        ))
        
        results.append(run_performance_test(
            input_dir,
            output_dir / "workers_4",
            workers=4,
            test_name="4个并发进程"
        ))
        
        print(f"\n{'='*60}")
        print("性能测试汇总")
        print(f"{'='*60}")
        
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
            print("\n✓ 所有性能测试通过！")
            return 0
        else:
            print("\n✗ 部分性能测试未通过")
            return 1


if __name__ == "__main__":
    exit(main())
