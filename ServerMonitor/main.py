# -*- coding: utf-8 -*-
"""
服务器资源监控工具 - 命令行入口
"""

import argparse
import sys
from monitor.monitor import ServerMonitor


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="服务器资源监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 启动监控
  python main.py --config my.json   # 使用自定义配置文件
        """
    )

    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="配置文件路径 (默认: config.json)"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="ServerMonitor 1.0.0"
    )

    args = parser.parse_args()

    try:
        monitor = ServerMonitor(config_path=args.config)
        monitor.start()
    except KeyboardInterrupt:
        print("\n程序已停止。")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
