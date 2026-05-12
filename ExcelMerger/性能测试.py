#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 测试合并10个10000行Excel文件的实际耗时
支持无人值守自动运行，自动采集环境信息，执行3次测试取平均值
"""

import os
import sys
import time
import platform
import pandas as pd
from excel_merger import ExcelMerger

# 测试配置
TEST_DIR = "performance_test_data"
NUM_FILES = 10
ROWS_PER_FILE = 10000
NUM_TESTS = 3
TARGET_SECONDS = 30


def get_system_info():
    """
    采集系统环境信息

    Returns:
        dict: 包含CPU、内存、Python版本等信息的字典
    """
    info = {
        "操作系统": f"{platform.system()} {platform.release()}",
        "Python版本": platform.python_version(),
        "pandas版本": pd.__version__,
        "处理器": platform.processor() or "未知",
        "机器架构": platform.machine(),
    }

    # 尝试获取内存信息（Windows平台）
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_uint),
                ("dwMemoryLoad", ctypes.c_uint),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
            ]
        ms = MEMORYSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            info["总内存"] = f"{ms.ullTotalPhys / (1024**3):.2f} GB"
            info["可用内存"] = f"{ms.ullAvailPhys / (1024**3):.2f} GB"
    except:
        info["内存信息"] = "无法获取"

    return info


def print_system_info(info):
    """
    打印系统环境信息

    Args:
        info: 系统信息字典
    """
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "系统环境信息" + " " * 32 + "║")
    print("╚" + "═" * 68 + "╝")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()


def generate_test_files(num_files: int, rows_per_file: int, output_dir: str):
    """
    生成测试用的Excel文件

    Args:
        num_files: 文件数量
        rows_per_file: 每个文件的行数
        output_dir: 输出目录

    Returns:
        list: 生成的文件路径列表
    """
    print("═" * 70)
    print("步骤 1/4: 生成测试文件")
    print("═" * 70)
    print(f"文件数量: {num_files} 个")
    print(f"每个文件行数: {rows_per_file:,} 行")
    print(f"预计总行数: {num_files * rows_per_file:,} 行")
    print()

    # 创建目录
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    file_paths = []
    departments = ['IT', 'HR', 'Finance', 'Sales', 'Marketing']

    for i in range(num_files):
        df = pd.DataFrame({
            'id': range(i * rows_per_file, (i + 1) * rows_per_file),
            'name': [f'User_{j}' for j in range(i * rows_per_file, (i + 1) * rows_per_file)],
            'age': [20 + (j % 40) for j in range(rows_per_file)],
            'salary': [5000 + (j % 100) * 100 for j in range(rows_per_file)],
            'department': [departments[j % 5] for j in range(rows_per_file)]
        })

        file_path = os.path.join(output_dir, f'test_file_{i+1}.xlsx')
        df.to_excel(file_path, index=False, engine='openpyxl')
        file_paths.append(file_path)
        print(f"  ✓ 已创建: test_file_{i+1}.xlsx ({rows_per_file:,}行)")

    print()
    print(f"所有测试文件创建完成！")
    print(f"文件目录: {os.path.abspath(output_dir)}")
    print()

    return file_paths


def run_single_test(file_paths, test_num):
    """
    运行单次合并测试

    Args:
        file_paths: 测试文件路径列表
        test_num: 测试序号

    Returns:
        float: 本次测试耗时（秒）
        int: 合并后的总行数
    """
    print(f"测试 #{test_num}: 开始合并...")

    merger = ExcelMerger()

    start_time = time.time()
    result_df, stats = merger.merge_by_row(file_paths, remove_duplicates=False)
    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f"  ✓ 合并完成！")
    print(f"    合并行数: {len(result_df):,} 行")
    print(f"    合并列数: {len(result_df.columns)} 列")
    print(f"    处理文件: {stats['files_processed']} 个")
    print(f"    失败文件: {stats['files_failed']} 个")
    print(f"    本次耗时: {elapsed_time:.4f} 秒")
    print()

    return elapsed_time, len(result_df)


def print_test_summary(all_times, total_rows):
    """
    打印测试结果摘要

    Args:
        all_times: 每次测试的耗时列表
        total_rows: 合并后的总行数
    """
    avg_time = sum(all_times) / len(all_times)
    min_time = min(all_times)
    max_time = max(all_times)

    print("═" * 70)
    print("步骤 3/4: 测试结果统计")
    print("═" * 70)
    print()
    print(f"测试次数: {len(all_times)} 次")
    print(f"每次合并行数: {total_rows:,} 行")
    print()
    print("单次测试耗时:")
    for i, t in enumerate(all_times, 1):
        status = "✓" if t < TARGET_SECONDS else "✗"
        print(f"  测试 #{i}: {t:.4f} 秒 {status}")
    print()
    print("统计结果:")
    print(f"  最快耗时: {min_time:.4f} 秒")
    print(f"  最慢耗时: {max_time:.4f} 秒")
    print(f"  平均耗时: {avg_time:.4f} 秒")
    print()

    # 判断是否达标
    all_passed = all(t < TARGET_SECONDS for t in all_times)
    print(f"性能目标: 单轮测试 < {TARGET_SECONDS} 秒")
    if all_passed:
        print(f"  结果: ✓ 全部通过！平均耗时 {avg_time:.2f} 秒 < {TARGET_SECONDS} 秒")
    else:
        print(f"  结果: ✗ 未通过！存在测试超过 {TARGET_SECONDS} 秒")
    print()

    return all_passed, avg_time


def cleanup_test_files(output_dir: str):
    """
    自动清理测试文件

    Args:
        output_dir: 测试文件目录
    """
    print("═" * 70)
    print("步骤 4/4: 清理测试文件")
    print("═" * 70)

    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        print(f"  ✓ 测试文件已自动清理: {output_dir}/")
    else:
        print(f"  ✓ 目录不存在，无需清理")
    print()


def print_final_summary(system_info, all_passed, avg_time, all_times):
    """
    打印最终测试总结

    Args:
        system_info: 系统信息字典
        all_passed: 是否全部通过
        avg_time: 平均耗时
        all_times: 所有测试的耗时列表
    """
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 25 + "最终测试报告" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("环境信息:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    print()
    print("测试配置:")
    print(f"  文件数量: {NUM_FILES} 个")
    print(f"  每个文件行数: {ROWS_PER_FILE:,} 行")
    print(f"  测试次数: {NUM_TESTS} 次")
    print()
    print("测试结果:")
    for i, t in enumerate(all_times, 1):
        print(f"  测试 #{i}: {t:.4f} 秒")
    print()
    print(f"  平均耗时: {avg_time:.4f} 秒")
    print(f"  性能目标: < {TARGET_SECONDS} 秒")
    print()
    if all_passed:
        print("  ✓ 性能测试通过！")
    else:
        print("  ✗ 性能测试未通过！")
    print()
    print("═" * 70)
    print("测试完成！以上数据可直接用于更新README.md")
    print("═" * 70)
    print()


def main():
    """
    主函数 - 自动完成所有测试步骤，无需人工交互
    """
    # 步骤1: 采集并打印系统信息
    system_info = get_system_info()
    print_system_info(system_info)

    try:
        # 步骤2: 生成测试文件
        file_paths = generate_test_files(NUM_FILES, ROWS_PER_FILE, TEST_DIR)

        # 步骤3: 运行多次合并测试
        print("═" * 70)
        print(f"步骤 2/4: 运行 {NUM_TESTS} 次合并测试")
        print("═" * 70)
        print(f"性能目标: 单轮测试 < {TARGET_SECONDS} 秒")
        print()

        all_times = []
        total_rows = 0

        for i in range(NUM_TESTS):
            elapsed, rows = run_single_test(file_paths, i + 1)
            all_times.append(elapsed)
            total_rows = rows

        # 步骤4: 打印测试结果统计
        all_passed, avg_time = print_test_summary(all_times, total_rows)

        # 步骤5: 自动清理测试文件
        cleanup_test_files(TEST_DIR)

        # 步骤6: 打印最终总结
        print_final_summary(system_info, all_passed, avg_time, all_times)

        # 根据测试结果设置退出码
        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        cleanup_test_files(TEST_DIR)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup_test_files(TEST_DIR)
        sys.exit(1)


if __name__ == '__main__':
    main()
