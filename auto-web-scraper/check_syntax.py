"""
语法检查脚本
检查所有Python文件的语法正确性
"""
import os
import ast
import sys


def check_file_syntax(file_path: str) -> bool:
    """
    检查单个Python文件的语法

    Args:
        file_path: 文件路径

    Returns:
        是否语法正确
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source, filename=file_path)
        return True
    except SyntaxError as e:
        print(f"❌ 语法错误: {file_path}")
        print(f"   行 {e.lineno}: {e.msg}")
        print(f"   代码: {e.text}")
        return False
    except Exception as e:
        print(f"❌ 读取错误: {file_path}")
        print(f"   {e}")
        return False


def check_directory(dir_path: str, exclude_dirs: list = None) -> tuple:
    """
    检查目录下所有Python文件

    Args:
        dir_path: 目录路径
        exclude_dirs: 排除的目录列表

    Returns:
        (文件总数, 错误数)
    """
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", ".pytest_cache", "venv", "env"]

    total_files = 0
    errors = 0

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                total_files += 1
                file_path = os.path.join(root, file)
                if not check_file_syntax(file_path):
                    errors += 1
                else:
                    print(f"✅ {file_path}")

    return total_files, errors


def main():
    """
    主函数
    """
    project_root = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("Python语法检查")
    print("=" * 70)
    print(f"项目根目录: {project_root}")
    print("=" * 70)
    print()

    total_files, errors = check_directory(project_root)

    print()
    print("=" * 70)
    print("检查结果")
    print("=" * 70)
    print(f"总文件数: {total_files}")
    print(f"错误文件: {errors}")

    if errors == 0:
        print("✅ 所有文件语法正确！")
        print("=" * 70)
        return 0
    else:
        print(f"❌ 发现 {errors} 个错误！")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
