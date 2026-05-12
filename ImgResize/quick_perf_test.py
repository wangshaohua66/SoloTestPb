import time
import tempfile
from pathlib import Path
from PIL import Image
import random

from img_resize.batch_processor import BatchProcessor, ProcessingConfig
from img_resize.image_processor import ImageFormat

print("=" * 60)
print("ImgResize 性能测试")
print("=" * 60)
print("\n目标: 处理100张图片的时间 ≤ 60秒")

with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_path = Path(tmp_dir)
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    
    # 生成100张测试图片
    input_dir.mkdir()
    print("\n正在生成100张测试图片...")
    
    start_gen = time.time()
    for i in range(100):
        size = random.choice([(1920, 1080), (1280, 720), (1024, 768), (800, 600)])
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        img = Image.new("RGB", size, color=color)
        
        if i % 4 == 0:
            img.save(input_dir / f"image_{i:03d}.png", "PNG", optimize=True)
        elif i % 4 == 1:
            img.save(input_dir / f"image_{i:03d}.webp", "WEBP", quality=80)
        else:
            img.save(input_dir / f"image_{i:03d}.jpg", "JPEG", quality=85, optimize=True)
        
        if (i + 1) % 25 == 0:
            print(f"  已生成 {i + 1}/100 张")
    
    total_size = sum(f.stat().st_size for f in input_dir.iterdir())
    print(f"\n测试图片生成完成: {total_size / 1024 / 1024:.2f} MB")
    
    # 运行性能测试
    print("\n开始处理测试...")
    config = ProcessingConfig(width=800, quality=80, output_format=ImageFormat.JPG)
    processor = BatchProcessor(max_workers=4, use_processes=False)
    
    start = time.time()
    result = processor.process_batch(input_dir, output_dir, config, recursive=False)
    elapsed = time.time() - start
    
    output_size = sum(f.stat().st_size for f in output_dir.iterdir())
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"  处理数量: {result.total_count} 张")
    print(f"  成功: {result.success_count} 张")
    print(f"  失败: {result.failed_count} 张")
    print(f"  成功率: {result.success_rate:.1f}%")
    print(f"  总耗时: {elapsed:.2f} 秒")
    print(f"  平均耗时: {result.average_time:.3f} 秒/张")
    print(f"  输入大小: {total_size / 1024:.1f} KB")
    print(f"  输出大小: {output_size / 1024:.1f} KB")
    print(f"  压缩比: {output_size / total_size * 100:.1f}%")
    
    print("\n" + "=" * 60)
    if elapsed <= 60:
        print("✓ 性能验收标准通过!")
        print(f"  100张图片处理时间: {elapsed:.2f} 秒 ≤ 60 秒")
        exit_code = 0
    else:
        print("✗ 性能验收标准未通过!")
        print(f"  100张图片处理时间: {elapsed:.2f} 秒 > 60 秒")
        exit_code = 1
    print("=" * 60)

exit(exit_code)
