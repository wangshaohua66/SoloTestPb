"""
完整采集流程示例脚本
使用Mock数据演示系统的所有功能

此脚本展示：
1. 配置定义
2. 登录认证
3. 分页采集
4. 数据提取
5. 速率限制
6. 代理轮换
7. 数据导出
"""
import sys
import os
import time
import random
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_web_scraper.config import (
    ScraperConfig,
    SelectorConfig,
    LoginConfig,
    PaginationConfig,
    RateLimitConfig,
    ProxyConfig,
    ExportConfig,
    RequestConfig,
)
from auto_web_scraper.data_extractor import DataExtractor
from auto_web_scraper.data_exporter import DataExporter
from auto_web_scraper.rate_limiter import RateLimiter
from auto_web_scraper.proxy_manager import ProxyManager


def generate_mock_pages(total_pages: int = 10) -> Dict[str, str]:
    """
    生成模拟页面数据

    Args:
        total_pages: 页面总数

    Returns:
        URL到HTML的映射
    """
    pages = {}
    for i in range(1, total_pages + 1):
        is_last = i == total_pages

        products_html = ""
        for j in range(1, 6):
            product_id = (i - 1) * 5 + j
            products_html += f"""
            <div class="product" data-id="{product_id}">
                <h3 class="product-title">商品 {product_id}</h3>
                <span class="product-price">¥{random.randint(10, 999):.2f}</span>
                <p class="product-desc">这是第 {product_id} 个商品的描述</p>
                <div class="product-tags">
                    <span class="tag">热销</span>
                    <span class="tag">推荐</span>
                </div>
                <a href="/products/{product_id}" class="product-link">查看详情</a>
            </div>
            """

        pagination_html = ""
        if not is_last:
            pagination_html = f'<a href="/list?page={i+1}" class="next-page">下一页</a>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>商品列表 - 第 {i} 页</title>
        </head>
        <body>
            <header>
                <h1>电商平台</h1>
                <div class="user-info">
                    <span class="username">testuser</span>
                </div>
            </header>
            <main>
                <div class="product-list">
                    {products_html}
                </div>
                <div class="pagination">
                    {pagination_html}
                </div>
            </main>
        </body>
        </html>
        """

        if i == 1:
            url = f"https://example.com/list"
        else:
            url = f"https://example.com/list?page={i}"

        pages[url] = html

    return pages


def generate_login_page() -> str:
    """
    生成登录页面HTML

    Returns:
        登录页面HTML
    """
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <form id="login-form" action="/login" method="post">
            <input type="hidden" name="csrf_token" value="mock_csrf_12345">
            <input type="text" name="username">
            <input type="password" name="password">
            <button type="submit">登录</button>
        </form>
    </body>
    </html>
    """


def create_mock_config() -> ScraperConfig:
    """
    创建模拟配置

    Returns:
        采集器配置
    """
    return ScraperConfig(
        name="mock_demo_scraper",
        start_urls=["https://example.com/list"],
        selectors=[
            SelectorConfig(
                name="product_titles",
                selector=".product-title",
                selector_type="css",
                is_list=True,
                default_value=[],
            ),
            SelectorConfig(
                name="product_prices",
                selector=".product-price",
                selector_type="css",
                is_list=True,
                default_value=[],
            ),
            SelectorConfig(
                name="product_links",
                selector=".product-link",
                selector_type="css",
                attribute="href",
                is_list=True,
                default_value=[],
            ),
            SelectorConfig(
                name="first_product",
                selector="//div[@class='product'][1]//h3",
                selector_type="xpath",
                is_list=False,
                default_value=None,
            ),
        ],
        login=LoginConfig(
            login_url="https://example.com/login",
            username="testuser",
            password="testpass123",
            username_field="username",
            password_field="password",
            success_indicator="testuser",
        ),
        pagination=PaginationConfig(
            enabled=True,
            selector=".next-page",
            selector_type="css",
            max_pages=5,
            start_page=1,
        ),
        request=RequestConfig(
            timeout=30,
            verify_ssl=True,
        ),
        rate_limit=RateLimitConfig(
            min_delay=0.01,
            max_delay=0.02,
            random_delay=True,
            concurrency=1,
        ),
        proxy=ProxyConfig(
            enabled=True,
            proxies=[
                "http://proxy1:8080",
                "http://proxy2:8080",
                "http://proxy3:8080",
            ],
            rotation_strategy="round_robin",
        ),
        export=ExportConfig(
            formats=["json", "csv"],
            output_dir="./output/examples",
            filename_prefix="mock_demo",
        ),
        retry_times=3,
        retry_delay=0.01,
    )


def run_mock_demo():
    """
    运行模拟采集演示
    """
    print("=" * 70)
    print("网页数据采集工具 - 完整采集流程演示")
    print("=" * 70)
    print(f"\n[1/7] 准备模拟数据...")

    mock_pages = generate_mock_pages(total_pages=5)
    login_page = generate_login_page()

    print(f"    已生成 {len(mock_pages)} 个模拟页面")
    print(f"    页面URL列表:")
    for url in mock_pages.keys():
        print(f"      - {url}")

    print(f"\n[2/7] 创建配置...")
    config = create_mock_config()
    print(f"    配置名称: {config.name}")
    print(f"    选择器数量: {len(config.selectors)}")
    print(f"    分页: {'启用' if config.pagination.enabled else '禁用'}")
    print(f"    代理: {'启用' if config.proxy.enabled else '禁用'}")
    print(f"    登录: {'启用' if config.login else '禁用'}")

    print(f"\n[3/7] 演示速率限制器...")
    rate_limiter = RateLimiter(
        min_delay=config.rate_limit.min_delay,
        max_delay=config.rate_limit.max_delay,
        random_delay=config.rate_limit.random_delay,
    )
    stats = rate_limiter.get_stats()
    print(f"    延迟范围: {stats['min_delay']}s - {stats['max_delay']}s")
    print(f"    随机延迟: {'是' if stats['random_delay'] else '否'}")

    print(f"\n[4/7] 演示代理管理器...")
    with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
        proxy_manager = ProxyManager(
            proxies=config.proxy.proxies,
            rotation_strategy=config.proxy.rotation_strategy,
            auto_test=False,
        )
        proxy_manager._working_proxies = proxy_manager.proxy_list

        print(f"    代理池大小: {len(proxy_manager.proxy_list)}")
        print(f"    轮换策略: {proxy_manager.rotation_strategy}")
        print(f"    前3个代理:")
        for _ in range(3):
            proxy = proxy_manager.get_proxy()
            print(f"      - {proxy['http']}")

    print(f"\n[5/7] 演示数据提取...")
    first_url = list(mock_pages.keys())[0]
    first_html = mock_pages[first_url]

    extractor = DataExtractor(first_html)

    selectors = [
        {
            "name": sel.name,
            "selector": sel.selector,
            "selector_type": sel.selector_type,
            "attribute": sel.attribute,
            "is_list": sel.is_list,
            "default_value": sel.default_value,
        }
        for sel in config.selectors
    ]

    extracted_data = extractor.extract_multiple(selectors)

    print(f"    提取的字段:")
    for key, value in extracted_data.items():
        if isinstance(value, list):
            print(f"      {key}: {len(value)} 项")
            if value:
                print(f"        示例: {value[:2]}")
        else:
            print(f"      {key}: {value}")

    print(f"\n[6/7] 演示完整采集流程（模拟）...")

    all_data: List[Dict[str, Any]] = []

    for page_num, (url, html) in enumerate(mock_pages.items(), 1):
        if page_num > config.pagination.max_pages:
            break

        print(f"    [{page_num}/{config.pagination.max_pages}] 采集: {url}")

        with rate_limiter:
            extractor = DataExtractor(html)
            page_data = extractor.extract_multiple(selectors)
            page_data["_page_url"] = url
            page_data["_page_num"] = page_num
            page_data["_scraped_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            all_data.append(page_data)

    print(f"\n    共采集 {len(all_data)} 个页面")

    print(f"\n[7/7] 演示数据导出...")
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output",
        "examples",
    )

    exporter = DataExporter(
        output_dir=output_dir,
        filename_prefix="mock_demo",
    )

    export_paths = exporter.export(all_data, formats=config.export.formats)

    print(f"    导出目录: {output_dir}")
    for fmt, path in export_paths.items():
        print(f"      {fmt.upper()}: {path}")

    print(f"\n{'='*70}")
    print("演示完成！")
    print("=" * 70)
    print(f"\n采集统计:")
    print(f"  - 总页面数: {len(all_data)}")
    print(f"  - 导出格式: {', '.join(config.export.formats)}")
    print(f"\n采集数据预览 (第1页):")
    if all_data:
        first_page = all_data[0]
        for key, value in list(first_page.items())[:5]:
            if isinstance(value, list):
                print(f"  {key}: {len(value)} 项")
            else:
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                print(f"  {key}: {str_value}")

    print(f"\n{'='*70}")
    return all_data, export_paths


if __name__ == "__main__":
    try:
        run_mock_demo()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出演示")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n演示出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
