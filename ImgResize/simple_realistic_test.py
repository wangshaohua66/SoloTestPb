"""简单的真实场景性能测试"""
import time
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import random

from img_resize.batch_processor import BatchProcessor, ProcessingConfig
from img_resize.image_processor import ImageFormat, ResizeMode


def main():
    print("=" * 60)
    print("ImgResize 真实场景性能测试")
    print("=" * 60)
    print("生成带有内容的图片（渐变、图形、噪点）...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        # 生成25张有内容的图片
        for i in range(25):
            size = random.choice([(1920, 1080), (1280, 720), (1024, 768), (800, 600)])
            width, height = size
            img = Image.new("RGB", size, color="white")
            draw = ImageDraw.Draw(img)

            # 渐变背景
            for y in range(height):
                r = int(135 + (100 * y / height))
                g = int(180 + (50 * y / height))
                b = int(220 - (100 * y / height))
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            # 添加噪点
            for _ in range(2000):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                r, g, b = img.getpixel((x, y))
                draw.point((x, y), fill=(
                    max(0, min(255, r + random.randint(-10, 10))),
                    max(0, min(255, g + random.randint(-10, 10))),
                    max(0, min(255, b + random.randint(-10, 10)))
                ))

            # 添加图形
            for _ in range(8):
                x1 = random.randint(0, width - 100)
                y1 = random.randint(0, height - 100)
                x2 = x1 + random.randint(20, 100)
                y2 = y1 + random.randint(20, 100)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                if random.choice([True, False]):
                    draw.rectangle([x1, y1, x2, y2], fill=color)
                else:
                    draw.ellipse([x1, y1, x2, y2], fill=color)

            # 保存为不同格式
            if i % 3 == 0:
                img.save(input_dir / f"photo_{i:02d}.png", "PNG", optimize=True)
            elif i % 3 == 1:
                img.save(input_dir / f"photo_{i:02d}.webp", "WEBP", quality=80)
            else:
                img.save(input_dir / f"photo_{i:02d}.jpg", "JPEG", quality=85)

        total_size = sum(f.stat().st_size for f in input_dir.iterdir())
        print(f"已生成 25 张真实场景图片，总大小: {total_size / 1024:.1f} KB")
        print(f"推算100张图片大小约: {total_size / 25 * 100 / 1024:.1f} KB")

        # 运行测试
        print("\n开始处理测试...")
        config = ProcessingConfig(
            width=1200,
            resize_mode=ResizeMode.FIT,
            quality=80,
            output_format=ImageFormat.JPG
        )
        processor = BatchProcessor(max_workers=4, use_processes=False)

        start = time.time()
        result = processor.process_batch(input_dir, output_dir, config, recursive=False)
        elapsed = time.time() - start

        # 推算100张图片的时间
        estimated_100 = elapsed * (100 / 25)

        print("=" * 60)
        print("测试结果")
        print("=" * 60)
        print(f"  25张图片实际耗时: {elapsed:.2f} 秒")
        print(f"  单张平均耗时: {elapsed/25:.3f} 秒")
        print(f"  成功率: {result.success_rate:.1f}%")
        print(f"\n  推算100张图片耗时: {estimated_100:.2f} 秒")
        print(f"  验收标准: <= 60 秒")
        print()

        if estimated_100 <= 60:
            print("OK 真实场景性能测试通过!")
            print(f"  推算100张图片: {estimated_100:.2f} 秒 <= 60 秒")
            return 0
        else:
            print("X 真实场景性能测试未通过")
            return 1


if __name__ == "__main__":
    exit(main())
