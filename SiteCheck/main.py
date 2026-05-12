#!/usr/bin/env python3
"""
网站健康检测工具
主入口程序
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config, setup_logging
from src.scheduler import HealthCheckScheduler


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description='网站健康检测工具 - 自动检测网站可用性并发送告警通知'
    )

    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )

    parser.add_argument(
        '-o', '--once',
        action='store_true',
        help='只执行一次检测，不启动调度器'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='网站健康检测工具 v1.0.0'
    )

    args = parser.parse_args()

    try:
        print(f"正在加载配置文件: {args.config}")
        config = Config(args.config)

        setup_logging(config)

        scheduler = HealthCheckScheduler(config)

        if args.once:
            print("执行单次检测模式...")
            scheduler.run_once()
            print("检测完成")
        else:
            print("启动调度器...")
            scheduler.start()
            print("按 Ctrl+C 停止程序")
            scheduler.wait()

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        print("请确保配置文件存在，或使用 -c 参数指定正确的配置文件路径", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
