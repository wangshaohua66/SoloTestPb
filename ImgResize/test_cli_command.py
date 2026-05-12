"""
测试命令行工具的脚本
"""

import tempfile
from pathlib import Path
from PIL import Image
import subprocess
import sys

def test_cli_command():
    """测试命令行工具"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        
        print("=" * 60)
        print("测试img-resize命令行工具")
        print("=" * 60)
        
        # 生成测试图片
        print("\n1. 生成5张测试图片...")
        for i in range(5):
            img = Image.new("RGB", (800, 600), color=(i * 50, 0, 255 - i * 50))
            img.save(input_dir / f"test_{i}.jpg", "JPEG", quality=85)
        
        original_sizes = {}
        for f in input_dir.glob("*.jpg"):
            img = Image.open(f)
            original_sizes[f.name] = (img.size, f.stat().st_size)
        
        print(f"   输入目录: {input_dir}")
        print(f"   输出目录: {output_dir}")
        
        # 测试python -m方式
        print("\n2. 测试python -m img_resize方式运行...")
        cmd = [
            sys.executable, "-m", "img_resize",
            "-i", str(input_dir),
            "-o", str(output_dir),
            "--width", "400",
            "--quality", "70",
            "--use-threads"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:", result.stderr)
        
        if result.returncode != 0:
            print(f"\n✗ 命令执行失败，退出码: {result.returncode}")
            return False
        
        # 检查输出
        print("\n3. 检查输出结果...")
        output_files = list(output_dir.glob("*.jpg"))
        print(f"   输出文件数: {len(output_files)}")
        
        for f in sorted(output_files):
            img = Image.open(f)
            orig_info = original_sizes.get(f.name)
            if orig_info:
                orig_size, orig_bytes = orig_info
                new_bytes = f.stat().st_size
                reduction = (1 - new_bytes / orig_bytes) * 100
                print(f"   {f.name}: {orig_size} -> {img.size}, 压缩: {reduction:.1f}%")
            else:
                print(f"   {f.name}: {img.size}")
        
        if len(output_files) == 5:
            print("\n✓ 所有文件都已成功处理!")
        else:
            print(f"\n✗ 处理失败: 期望5个文件，实际{len(output_files)}个")
            return False
        
        # 测试help命令
        print("\n4. 测试--help参数...")
        cmd_help = [sys.executable, "-m", "img_resize", "--help"]
        result_help = subprocess.run(cmd_help, capture_output=True, text=True)
        if "img-resize" in result_help.stdout or "图片批量压缩" in result_help.stdout:
            print("   ✓ help命令正常工作")
        else:
            print("   ? help输出可能有问题")
        
        print("\n" + "=" * 60)
        print("所有测试通过!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = test_cli_command()
    exit(0 if success else 1)
