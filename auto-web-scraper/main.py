"""
网页数据采集工具主入口
提供命令行界面使用采集功能
"""
import argparse
import sys
import os
import json
from typing import List, Dict, Any

from auto_web_scraper.config import ScraperConfig, ConfigLoader, SelectorConfig
from auto_web_scraper.scraper import WebScraper


def parse_args():
    """
    解析命令行参数

    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="网页数据采集工具 - 支持多种网页结构的自动化数据采集"
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="配置文件路径 (YAML或JSON格式)",
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="起始URL",
    )

    parser.add_argument(
        "-s",
        "--selector",
        type=str,
        action="append",
        help="CSS/XPath选择器，格式: name|selector|type|attribute，例如: title|h1.title|css",
    )

    parser.add_argument(
        "-p",
        "--pages",
        type=int,
        default=1,
        help="采集页数",
    )

    parser.add_argument(
        "-f",
        "--format",
        type=str,
        action="append",
        choices=["json", "csv", "excel"],
        help="输出格式，可以多次指定",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output",
        help="输出目录",
    )

    parser.add_argument(
        "--delay-min",
        type=float,
        default=1.0,
        help="最小请求间隔(秒)",
    )

    parser.add_argument(
        "--delay-max",
        type=float,
        default=3.0,
        help="最大请求间隔(秒)",
    )

    parser.add_argument(
        "--proxy",
        type=str,
        action="append",
        help="代理服务器地址，可以多次指定",
    )

    parser.add_argument(
        "--login-url",
        type=str,
        help="登录页面URL",
    )

    parser.add_argument(
        "--username",
        type=str,
        help="登录用户名",
    )

    parser.add_argument(
        "--password",
        type=str,
        help="登录密码",
    )

    return parser.parse_args()


def build_config_from_args(args) -> ScraperConfig:
    """
    根据命令行参数构建配置

    Args:
        args: 命令行参数

    Returns:
        ScraperConfig配置对象
    """
    selectors: List[SelectorConfig] = []

    if args.selector:
        for sel_str in args.selector:
            parts = sel_str.split("|")
            if len(parts) >= 2:
                name = parts[0]
                selector = parts[1]
                selector_type = parts[2] if len(parts) > 2 else "css"
                attribute = parts[3] if len(parts) > 3 else None
                is_list = False
                if len(parts) > 4:
                    is_list = parts[4].lower() == "true"

                selectors.append(
                    SelectorConfig(
                        name=name,
                        selector=selector,
                        selector_type=selector_type,
                        attribute=attribute,
                        is_list=is_list,
                    )
                )

    from auto_web_scraper.config import (
        LoginConfig,
        PaginationConfig,
        RequestConfig,
        RateLimitConfig,
        ProxyConfig,
        ExportConfig,
    )

    login_config = None
    if args.login_url and args.username and args.password:
        login_config = LoginConfig(
            login_url=args.login_url,
            username=args.username,
            password=args.password,
        )

    pagination_config = PaginationConfig(
        enabled=args.pages > 1,
        max_pages=args.pages,
    )

    export_formats = args.format if args.format else ["json"]

    proxy_config = ProxyConfig(
        enabled=args.proxy is not None and len(args.proxy) > 0,
        proxies=args.proxy if args.proxy else [],
    )

    return ScraperConfig(
        name="cli_scraper",
        start_urls=[args.url] if args.url else [],
        selectors=selectors,
        login=login_config,
        pagination=pagination_config,
        request=RequestConfig(),
        rate_limit=RateLimitConfig(
            min_delay=args.delay_min,
            max_delay=args.delay_max,
        ),
        proxy=proxy_config,
        export=ExportConfig(
            formats=export_formats,
            output_dir=args.output,
        ),
    )


def main():
    """
    主函数
    """
    args = parse_args()

    if args.config:
        print(f"使用配置文件: {args.config}")
        scraper = WebScraper(config_file=args.config)
    elif args.url:
        print(f"使用命令行参数配置")
        config = build_config_from_args(args)
        scraper = WebScraper(config=config)
    else:
        print("错误: 请指定配置文件(-c)或URL(-u)")
        print("使用 --help 查看帮助信息")
        sys.exit(1)

    print("=" * 50)
    print("开始执行采集任务...")
    print("=" * 50)

    try:
        data = scraper.scrape()

        if data:
            print(f"\n共采集到 {len(data)} 条数据")
            if len(data) > 0:
                print("前2条数据预览:")
                for i, item in enumerate(data[:2]):
                    print(f"  [{i + 1}] {json.dumps(item, ensure_ascii=False)[:200]}...")

            print("\n导出数据...")
            export_paths = scraper.export_data()
            print("导出完成:")
            for fmt, path in export_paths.items():
                print(f"  {fmt.upper()}: {path}")

        stats = scraper.get_stats()
        print("\n" + "=" * 50)
        print("采集统计:")
        print(f"  总页数: {stats.get('total_pages', 0)}")
        print(f"  成功: {stats.get('success_pages', 0)}")
        print(f"  失败: {stats.get('failed_pages', 0)}")
        print(f"  总记录: {stats.get('total_records', 0)}")
        if "success_rate" in stats:
            print(f"  成功率: {stats['success_rate']:.2f}%")
        if "duration_seconds" in stats:
            print(f"  总耗时: {stats['duration_seconds']:.2f}秒")
        print("=" * 50)

    except KeyboardInterrupt:
        print("\n用户中断，停止采集")
        scraper.stop()
    except Exception as e:
        print(f"\n采集过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
