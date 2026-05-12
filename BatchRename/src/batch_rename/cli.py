"""
命令行接口模块
提供用户友好的命令行界面
"""

import argparse
import sys
import os
from typing import List, Optional

from .core import (
    SequenceRenameStrategy,
    TimestampRenameStrategy,
    ReplaceRenameStrategy,
    PrefixRenameStrategy,
    SuffixRenameStrategy,
    RegexRenameStrategy,
    BatchRenamer,
)


def print_preview(preview_list: List[tuple]):
    """
    打印预览结果
    
    Args:
        preview_list: 预览列表，每个元素为(原文件名, 新文件名)
    """
    print("\n" + "=" * 80)
    print("重命名预览")
    print("=" * 80)
    if not preview_list:
        print("  目录中没有找到文件")
    else:
        print(f"  找到 {len(preview_list)} 个文件:")
        print("-" * 80)
        for old_name, new_name in preview_list:
            status = " -> " if old_name != new_name else " (不变) "
            print(f"  {old_name}{status}{new_name}")
    print("=" * 80 + "\n")


def print_results(results: List[tuple], is_undo: bool = False):
    """
    打印执行结果
    
    Args:
        results: 结果列表，每个元素为(原文件名, 新文件名, 是否成功)
        is_undo: 是否为撤销操作
    """
    success_count = sum(1 for _, _, success in results if success)
    fail_count = len(results) - success_count

    print("\n" + "=" * 80)
    if is_undo:
        print("撤销结果")
    else:
        print("重命名结果")
    print("=" * 80)
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")
    print("-" * 80)
    for first, second, success in results:
        status = "✓" if success else "✗"
        if is_undo:
            print(f"  {status} {first} -> {second}")
        else:
            print(f"  {status} {first} -> {second}")
    print("=" * 80 + "\n")


def main():
    """
    命令行主入口函数
    """
    parser = argparse.ArgumentParser(
        description="批量文件重命名工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按序号重命名
  python -m batch_rename /path/to/files --mode sequence --name "photo"
  
  # 添加前缀
  python -m batch_rename /path/to/files --mode prefix --prefix "2024_"
  
  # 预览模式
  python -m batch_rename /path/to/files --mode sequence --name "file" --preview
  
  # 撤销上次操作
  python -m batch_rename /path/to/files --undo
        """
    )

    parser.add_argument(
        "directory",
        help="文件所在目录"
    )

    parser.add_argument(
        "--undo",
        action="store_true",
        help="撤销上次批量重命名操作"
    )

    parser.add_argument(
        "--mode",
        choices=["sequence", "timestamp", "replace", "prefix", "suffix", "regex"],
        help="重命名模式"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="预览模式，不实际执行重命名"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="强制执行模式，跳过交互式确认，适用于自动化脚本"
    )

    # 序列模式参数
    parser.add_argument(
        "--name",
        help="序列模式的基础名称"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="起始序号，默认为1"
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=3,
        help="序号填充位数，默认为3"
    )

    # 时间戳模式参数
    parser.add_argument(
        "--format",
        default="%Y%m%d_%H%M%S",
        help="日期时间格式，默认为%%Y%%m%%d_%%H%%M%%S"
    )

    # 替换模式参数
    parser.add_argument(
        "--find",
        help="要查找的字符串"
    )
    parser.add_argument(
        "--replace",
        help="替换的字符串"
    )

    # 前缀/后缀参数
    parser.add_argument(
        "--prefix",
        help="要添加的前缀"
    )
    parser.add_argument(
        "--suffix",
        help="要添加的后缀"
    )

    # 正则模式参数
    parser.add_argument(
        "--pattern",
        help="正则表达式匹配模式"
    )

    # 文件扩展名过滤
    parser.add_argument(
        "--ext",
        nargs="*",
        help="只处理指定扩展名的文件，如 --ext .jpg .png"
    )

    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        sys.exit(1)

    if not os.path.isdir(args.directory):
        print(f"错误: 不是一个目录: {args.directory}")
        sys.exit(1)

    # 处理撤销操作
    if args.undo:
        from .core import HistoryManager
        history = HistoryManager(args.directory)
        if not history.has_history():
            print("没有可撤销的重命名操作历史")
            sys.exit(0)

        renamer = BatchRenamer(args.directory, None)
        results = renamer.undo()
        print_results(results, is_undo=True)
        sys.exit(0)

    # 检查是否指定了模式
    if not args.mode:
        print("错误: 必须指定重命名模式 --mode 或使用 --undo")
        parser.print_help()
        sys.exit(1)

    # 根据模式创建策略
    strategy = None

    if args.mode == "sequence":
        if not args.name:
            print("错误: 序列模式需要指定 --name 参数")
            sys.exit(1)
        strategy = SequenceRenameStrategy(
            name=args.name,
            start=args.start,
            padding=args.padding
        )

    elif args.mode == "timestamp":
        strategy = TimestampRenameStrategy(format_str=args.format)

    elif args.mode == "replace":
        if args.find is None:
            print("错误: 替换模式需要指定 --find 参数")
            sys.exit(1)
        if args.replace is None:
            print("错误: 替换模式需要指定 --replace 参数")
            sys.exit(1)
        strategy = ReplaceRenameStrategy(
            find=args.find,
            replace=args.replace
        )

    elif args.mode == "prefix":
        if not args.prefix:
            print("错误: 前缀模式需要指定 --prefix 参数")
            sys.exit(1)
        strategy = PrefixRenameStrategy(prefix=args.prefix)

    elif args.mode == "suffix":
        if not args.suffix:
            print("错误: 后缀模式需要指定 --suffix 参数")
            sys.exit(1)
        strategy = SuffixRenameStrategy(suffix_str=args.suffix)

    elif args.mode == "regex":
        if not args.pattern:
            print("错误: 正则模式需要指定 --pattern 参数")
            sys.exit(1)
        if args.replace is None:
            print("错误: 正则模式需要指定 --replace 参数")
            sys.exit(1)
        strategy = RegexRenameStrategy(
            pattern=args.pattern,
            replace=args.replace
        )

    # 创建批量重命名器并执行
    renamer = BatchRenamer(
        directory=args.directory,
        strategy=strategy,
        file_extensions=args.ext
    )

    # 预览或执行
    if args.preview:
        preview_list = renamer.preview()
        print_preview(preview_list)
    else:
        # 先预览
        preview_list = renamer.preview()
        print_preview(preview_list)

        if preview_list:
            if args.force:
                # 强制执行模式，直接执行
                results = renamer.execute(preview=False)
                print_results(results)
            else:
                # 确认执行
                try:
                    confirm = input("确认执行重命名? (y/n): ").strip().lower()
                    if confirm == "y" or confirm == "yes":
                        results = renamer.execute(preview=False)
                        print_results(results)
                    else:
                        print("已取消操作")
                except KeyboardInterrupt:
                    print("\n已取消操作")


if __name__ == "__main__":
    main()
