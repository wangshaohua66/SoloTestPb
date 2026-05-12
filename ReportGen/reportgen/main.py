"""
报表生成工具命令行入口。
"""

import argparse
import json
import sys
from typing import Any, Dict

from reportgen.core import ReportGenerator
from reportgen.scheduler import ReportScheduler


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件。

    Args:
        config_path: 配置文件路径。

    Returns:
        配置字典。
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_single_report(config_path: str) -> None:
    """
    运行单个报表生成任务。

    Args:
        config_path: 配置文件路径。
    """
    try:
        config = load_config(config_path)
        generator = ReportGenerator()
        result = generator.generate_report(config)

        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n报表生成成功！输出文件: {result.get('output_path')}")
        print(f"耗时: {result.get('duration_seconds'):.2f} 秒")
        print(f"数据行数: {result.get('row_count')}")
        print(f"列数: {result.get('column_count')}")

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


def run_batch_reports(config_path: str) -> None:
    """
    运行批量报表生成任务。

    Args:
        config_path: 配置文件路径（包含configs列表）。
    """
    try:
        config_data = load_config(config_path)
        configs = config_data.get("configs", [])

        if not configs:
            print("错误: 配置文件中没有找到configs列表", file=sys.stderr)
            sys.exit(1)

        generator = ReportGenerator()
        results = generator.generate_multiple_reports(configs)

        for i, result in enumerate(results):
            if "error" in result:
                print(f"\n报表 {i+1} 生成失败: {result['error']}")
            else:
                print(f"\n报表 {i+1} 生成成功！")
                print(f"  输出文件: {result.get('output_path')}")
                print(f"  耗时: {result.get('duration_seconds'):.2f} 秒")

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    主函数。
    """
    parser = argparse.ArgumentParser(
        description="自动化报表生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m reportgen.main generate -c report_config.json
  python -m reportgen.main batch -c batch_config.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    generate_parser = subparsers.add_parser("generate", help="生成单个报表")
    generate_parser.add_argument(
        "-c", "--config", required=True, help="报表配置文件路径"
    )

    batch_parser = subparsers.add_parser("batch", help="批量生成报表")
    batch_parser.add_argument(
        "-c", "--config", required=True, help="批量配置文件路径"
    )

    args = parser.parse_args()

    if args.command == "generate":
        run_single_report(args.config)
    elif args.command == "batch":
        run_batch_reports(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
