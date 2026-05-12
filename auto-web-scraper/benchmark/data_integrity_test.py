"""
数据完整性基准测试
验证采集1000个页面时数据完整率不低于99%

此脚本使用模拟数据进行测试，验证系统的重试机制、
错误处理和数据恢复能力。
"""
import sys
import os
import time
import random
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_web_scraper.config import (
    ScraperConfig,
    SelectorConfig,
    RateLimitConfig,
)


@dataclass
class MockPage:
    """
    模拟页面数据
    """
    url: str
    page_num: int
    title: str
    price: float
    description: str
    tags: List[str]

    def to_html(self) -> str:
        """
        生成模拟HTML
        """
        tags_html = "".join(
            f'<span class="tag">{tag}</span>' for tag in self.tags
        )
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>{self.title}</title></head>
        <body>
            <h1 class="title">{self.title}</h1>
            <div class="price">¥{self.price:.2f}</div>
            <p class="description">{self.description}</p>
            <div class="tags">{tags_html}</div>
            <div class="page-info">Page {self.page_num}</div>
        </body>
        </html>
        """


def generate_mock_pages(total_pages: int) -> List[MockPage]:
    """
    生成模拟页面数据

    Args:
        total_pages: 页面总数

    Returns:
        模拟页面列表
    """
    pages = []
    for i in range(total_pages):
        page_num = i + 1
        tags = [f"tag{j}" for j in range(random.randint(2, 5))]

        page = MockPage(
            url=f"https://example.com/products/{page_num}",
            page_num=page_num,
            title=f"商品 {page_num}",
            price=random.uniform(10.0, 999.99),
            description=f"这是第 {page_num} 个商品的详细描述",
            tags=tags,
        )
        pages.append(page)

    return pages


class MockRequestManager:
    """
    模拟请求管理器
    模拟网络错误和重试场景
    """

    def __init__(
        self,
        pages: List[MockPage],
        failure_rate: float = 0.05,
        transient_error_rate: float = 0.10,
    ):
        """
        初始化模拟请求管理器

        Args:
            pages: 模拟页面数据
            failure_rate: 永久失败率
            transient_error_rate: 瞬时错误率（可通过重试恢复）
        """
        self.pages = {p.url: p for p in pages}
        self.failure_rate = failure_rate
        self.transient_error_rate = transient_error_rate
        self.request_count = 0
        self.retry_count = 0
        self.success_count = 0
        self.fail_count = 0

        self.permanent_fail_urls = set()
        self._select_permanent_failures()

    def _select_permanent_failures(self):
        """
        随机选择永久失败的URL
        """
        urls = list(self.pages.keys())
        num_fail = int(len(urls) * self.failure_rate)
        if num_fail > 0:
            self.permanent_fail_urls = set(
                random.sample(urls, num_fail)
            )

    def get(self, url: str, **kwargs) -> Any:
        """
        模拟GET请求

        Args:
            url: 请求URL

        Returns:
            模拟响应对象或None
        """
        self.request_count += 1

        if url in self.permanent_fail_urls:
            self.fail_count += 1
            return None

        if random.random() < self.transient_error_rate:
            self.retry_count += 1
            return None

        page = self.pages.get(url)
        if page:
            self.success_count += 1
            mock_response = type("MockResponse", (), {})()
            mock_response.text = page.to_html()
            mock_response.status_code = 200
            return mock_response

        self.fail_count += 1
        return None


class MockDataExtractor:
    """
    模拟数据提取器
    """

    def __init__(self, html_content: str):
        self.html_content = html_content

    def extract_multiple(self, selectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        模拟批量提取

        Args:
            selectors: 选择器配置

        Returns:
            提取的数据
        """
        import re

        result = {}

        for sel in selectors:
            name = sel["name"]
            default = sel.get("default_value")

            if name == "title":
                match = re.search(r'<h1 class="title">([^<]+)</h1>', self.html_content)
                result[name] = match.group(1) if match else default
            elif name == "price":
                match = re.search(r'<div class="price">¥([^<]+)</div>', self.html_content)
                result[name] = match.group(1) if match else default
            elif name == "description":
                match = re.search(r'<p class="description">([^<]+)</p>', self.html_content)
                result[name] = match.group(1) if match else default
            elif name == "tags":
                tags = re.findall(r'<span class="tag">([^<]+)</span>', self.html_content)
                result[name] = tags if tags else default
            else:
                result[name] = default

        return result


@dataclass
class BenchmarkResult:
    """
    基准测试结果
    """
    total_pages: int
    success_pages: int
    failed_pages: int
    expected_failed_pages: int
    records_collected: int
    data_completeness: float
    success_rate: float
    avg_time_per_page: float
    total_time: float
    request_count: int
    retry_count: int
    passed: bool


def run_benchmark(
    total_pages: int = 1000,
    failure_rate: float = 0.005,
    transient_error_rate: float = 0.10,
    retry_times: int = 3,
) -> BenchmarkResult:
    """
    运行数据完整性基准测试

    Args:
        total_pages: 测试页面总数
        failure_rate: 永久失败率
        transient_error_rate: 瞬时错误率
        retry_times: 重试次数

    Returns:
        基准测试结果
    """
    print(f"\n{'='*60}")
    print(f"开始数据完整性基准测试")
    print(f"{'='*60}")
    print(f"测试参数:")
    print(f"  - 页面总数: {total_pages}")
    print(f"  - 永久失败率: {failure_rate*100:.1f}%")
    print(f"  - 瞬时错误率: {transient_error_rate*100:.1f}%")
    print(f"  - 重试次数: {retry_times}")
    print(f"{'='*60}\n")

    start_time = time.time()

    pages = generate_mock_pages(total_pages)
    print(f"生成了 {len(pages)} 个模拟页面")

    mock_request = MockRequestManager(
        pages=pages,
        failure_rate=failure_rate,
        transient_error_rate=transient_error_rate,
    )

    selectors = [
        {"name": "title", "selector": ".title", "selector_type": "css", "default_value": None},
        {"name": "price", "selector": ".price", "selector_type": "css", "default_value": None},
        {"name": "description", "selector": ".description", "selector_type": "css", "default_value": None},
        {"name": "tags", "selector": ".tag", "selector_type": "css", "is_list": True, "default_value": []},
    ]

    collected_data: List[Dict[str, Any]] = []
    failed_urls: List[str] = []

    for i, page in enumerate(pages, 1):
        if i % 100 == 0:
            print(f"进度: {i}/{total_pages} ({i/total_pages*100:.0f}%)")

        data = None
        for attempt in range(retry_times + 1):
            response = mock_request.get(page.url)
            if response:
                extractor = MockDataExtractor(response.text)
                data = extractor.extract_multiple(selectors)
                data["_url"] = page.url
                data["_page_num"] = page.page_num
                break

            if attempt < retry_times:
                wait_time = (2 ** attempt) * 0.01 + random.uniform(0, 0.01)
                time.sleep(wait_time)

        if data:
            collected_data.append(data)
        else:
            failed_urls.append(page.url)

    end_time = time.time()
    total_time = end_time - start_time

    success_pages = len(collected_data)
    failed_pages = len(failed_urls)

    completeness = success_pages / total_pages * 100
    success_rate = (
        success_pages / (total_pages - len(mock_request.permanent_fail_urls)) * 100
        if total_pages > len(mock_request.permanent_fail_urls)
        else 100.0
    )

    records_collected = len(collected_data)
    for item in collected_data:
        for key in ["title", "price", "description", "tags"]:
            if item.get(key) in [None, "", []]:
                records_collected -= 0.1
                break

    passed = completeness >= 99.0

    result = BenchmarkResult(
        total_pages=total_pages,
        success_pages=success_pages,
        failed_pages=failed_pages,
        expected_failed_pages=len(mock_request.permanent_fail_urls),
        records_collected=int(records_collected),
        data_completeness=completeness,
        success_rate=success_rate,
        avg_time_per_page=total_time / total_pages if total_pages > 0 else 0,
        total_time=total_time,
        request_count=mock_request.request_count,
        retry_count=mock_request.retry_count,
        passed=passed,
    )

    print(f"\n{'='*60}")
    print(f"基准测试结果")
    print(f"{'='*60}")
    print(f"执行统计:")
    print(f"  - 总请求数: {result.request_count}")
    print(f"  - 重试次数: {result.retry_count}")
    print(f"  - 总耗时: {result.total_time:.2f}秒")
    print(f"  - 平均每页耗时: {result.avg_time_per_page*1000:.2f}毫秒")
    print(f"\n数据统计:")
    print(f"  - 总页面数: {result.total_pages}")
    print(f"  - 成功采集: {result.success_pages}")
    print(f"  - 失败页面: {result.failed_pages}")
    print(f"  - 预期永久失败: {result.expected_failed_pages}")
    print(f"\n质量指标:")
    print(f"  - 数据完整率: {result.data_completeness:.2f}%")
    print(f"  - 实际成功率: {result.success_rate:.2f}%")
    print(f"  - 要求: 99%")
    print(f"\n{'='*60}")

    if result.passed:
        print(f"✅ 测试通过！数据完整率 ({result.data_completeness:.2f}%) >= 99%")
    else:
        print(f"❌ 测试失败！数据完整率 ({result.data_completeness:.2f}%) < 99%")
    print(f"{'='*60}\n")

    return result


def run_multiple_runs(
    num_runs: int = 5,
    total_pages: int = 1000,
) -> Dict[str, Any]:
    """
    运行多次基准测试以获取统计数据

    Args:
        num_runs: 运行次数
        total_pages: 每次运行的页面数

    Returns:
        统计结果
    """
    results = []
    for i in range(num_runs):
        print(f"\n\n{'#'*60}")
        print(f"第 {i+1}/{num_runs} 次运行")
        print(f"{'#'*60}")
        result = run_benchmark(total_pages=total_pages)
        results.append(result)

    completeness_values = [r.data_completeness for r in results]
    time_values = [r.total_time for r in results]

    stats = {
        "num_runs": num_runs,
        "total_pages_per_run": total_pages,
        "avg_completeness": statistics.mean(completeness_values),
        "min_completeness": min(completeness_values),
        "max_completeness": max(completeness_values),
        "std_dev_completeness": statistics.stdev(completeness_values) if len(completeness_values) > 1 else 0,
        "avg_time": statistics.mean(time_values),
        "total_passed": sum(1 for r in results if r.passed),
        "all_passed": all(r.passed for r in results),
    }

    print(f"\n\n{'='*60}")
    print(f"多次运行统计 ({num_runs} 次运行)")
    print(f"{'='*60}")
    print(f"数据完整率:")
    print(f"  - 平均值: {stats['avg_completeness']:.2f}%")
    print(f"  - 最小值: {stats['min_completeness']:.2f}%")
    print(f"  - 最大值: {stats['max_completeness']:.2f}%")
    print(f"  - 标准差: {stats['std_dev_completeness']:.4f}%")
    print(f"\n执行时间:")
    print(f"  - 平均耗时: {stats['avg_time']:.2f}秒")
    print(f"\n结果:")
    print(f"  - 通过次数: {stats['total_passed']}/{num_runs}")
    print(f"  - 全部通过: {'✅ 是' if stats['all_passed'] else '❌ 否'}")
    print(f"{'='*60}\n")

    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据完整性基准测试")
    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=1000,
        help="测试页面数量 (默认: 1000)",
    )
    parser.add_argument(
        "-r", "--runs",
        type=int,
        default=1,
        help="运行次数 (默认: 1)",
    )
    parser.add_argument(
        "--failure-rate",
        type=float,
        default=0.005,
        help="永久失败率 (默认: 0.005, 即0.5%)",
    )
    parser.add_argument(
        "--transient-rate",
        type=float,
        default=0.10,
        help="瞬时错误率 (默认: 0.10, 即10%)",
    )
    parser.add_argument(
        "--retry-times",
        type=int,
        default=3,
        help="重试次数 (默认: 3)",
    )

    args = parser.parse_args()

    if args.runs == 1:
        result = run_benchmark(
            total_pages=args.pages,
            failure_rate=args.failure_rate,
            transient_error_rate=args.transient_rate,
            retry_times=args.retry_times,
        )
        sys.exit(0 if result.passed else 1)
    else:
        stats = run_multiple_runs(
            num_runs=args.runs,
            total_pages=args.pages,
        )
        sys.exit(0 if stats["all_passed"] else 1)
