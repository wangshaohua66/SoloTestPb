"""
核心采集器模块
整合所有功能，提供统一的采集接口
"""
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import time

from .config import ScraperConfig, ConfigLoader
from .request_manager import RequestManager
from .data_extractor import DataExtractor
from .pagination import PaginationHandler
from .authenticator import Authenticator
from .proxy_manager import ProxyManager
from .rate_limiter import RateLimiter
from .data_exporter import DataExporter


class WebScraper:
    """
    网页数据采集器
    整合所有模块，提供完整的数据采集功能
    """

    def __init__(
        self,
        config: Optional[ScraperConfig] = None,
        config_file: Optional[str] = None,
    ):
        """
        初始化采集器

        Args:
            config: 配置对象
            config_file: 配置文件路径
        """
        if config_file:
            if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                self.config = ConfigLoader.from_yaml(config_file)
            elif config_file.endswith(".json"):
                self.config = ConfigLoader.from_json(config_file)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file}")
        elif config:
            self.config = config
        else:
            self.config = ScraperConfig()

        self._request_manager: Optional[RequestManager] = None
        self._authenticator: Optional[Authenticator] = None
        self._proxy_manager: Optional[ProxyManager] = None
        self._rate_limiter: Optional[RateLimiter] = None
        self._data_exporter: Optional[DataExporter] = None
        self._pagination_handler: Optional[PaginationHandler] = None

        self._collected_data: List[Dict[str, Any]] = []
        self._stats: Dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "total_pages": 0,
            "success_pages": 0,
            "failed_pages": 0,
            "total_records": 0,
        }
        self._running = False

    def _init_modules(self):
        """
        初始化所有模块
        """
        rc = self.config.request
        self._request_manager = RequestManager(
            timeout=rc.timeout,
            headers=rc.headers,
            cookies=rc.cookies,
            verify_ssl=rc.verify_ssl,
            allow_redirects=rc.allow_redirects,
            retry_times=self.config.retry_times,
            retry_delay=self.config.retry_delay,
        )

        self._authenticator = Authenticator(
            session=self._request_manager.session
        )

        pc = self.config.proxy
        if pc.enabled and pc.proxies:
            self._proxy_manager = ProxyManager(
                proxies=pc.proxies,
                rotation_strategy=pc.rotation_strategy,
                test_url=pc.test_url,
                test_timeout=pc.test_timeout,
            )

        rlc = self.config.rate_limit
        self._rate_limiter = RateLimiter(
            min_delay=rlc.min_delay,
            max_delay=rlc.max_delay,
            random_delay=rlc.random_delay,
            concurrency=rlc.concurrency,
        )

        ec = self.config.export
        self._data_exporter = DataExporter(
            output_dir=ec.output_dir,
            filename_prefix=ec.filename_prefix,
            encoding=ec.encoding,
        )

        pagc = self.config.pagination
        self._pagination_handler = PaginationHandler(
            max_pages=pagc.max_pages,
            start_page=pagc.start_page,
            page_param_name=pagc.page_param_name,
        )

    def _login_if_needed(self):
        """
        如果需要登录，执行登录操作
        """
        if not self.config.login or not self._authenticator:
            return

        login_config = self.config.login
        success = self._authenticator.form_login(
            login_url=login_config.login_url,
            username=login_config.username,
            password=login_config.password,
            username_field=login_config.username_field,
            password_field=login_config.password_field,
            submit_field=login_config.submit_field,
            extra_fields=login_config.extra_fields,
            success_indicator=login_config.success_indicator,
        )

        if success:
            print("登录成功")
        else:
            print("警告: 登录失败，继续采集可能无法获取数据")

    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """
        获取当前使用的代理

        Returns:
            代理配置字典或None
        """
        if self._proxy_manager:
            return self._proxy_manager.get_proxy()
        return None

    def _wait_for_rate_limit(self):
        """
        等待速率限制
        """
        if self._rate_limiter:
            self._rate_limiter.wait()

    def _scrape_single_page(
        self, url: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        采集单个页面

        Args:
            url: 页面URL

        Returns:
            采集的数据列表或None
        """
        try:
            self._wait_for_rate_limit()

            proxies = self._get_proxies()
            response = self._request_manager.get(url, proxies=proxies)

            if response is None:
                self._stats["failed_pages"] += 1
                if proxies:
                    proxy_url = list(proxies.values())[0]
                    self._proxy_manager.mark_proxy_failed(proxy_url)
                return None

            if proxies:
                proxy_url = list(proxies.values())[0]
                self._proxy_manager.mark_proxy_success(proxy_url)

            self._stats["success_pages"] += 1

            extractor = DataExtractor(response.text)

            selectors_config = [
                {
                    "name": sel.name,
                    "selector": sel.selector,
                    "selector_type": sel.selector_type,
                    "attribute": sel.attribute,
                    "is_list": sel.is_list,
                    "default_value": sel.default_value,
                }
                for sel in self.config.selectors
            ]

            page_data = extractor.extract_multiple(selectors_config)
            page_data["_url"] = url
            page_data["_scraped_at"] = datetime.now().isoformat()

            return [page_data]

        except Exception as e:
            print(f"采集页面错误 {url}: {e}")
            self._stats["failed_pages"] += 1
            return None

    def _collect_all_urls(self) -> List[str]:
        """
        收集所有需要采集的URL

        Returns:
            URL列表
        """
        all_urls = []
        pagc = self.config.pagination

        for start_url in self.config.start_urls:
            if pagc.enabled:
                if pagc.selector:
                    all_urls.append(start_url)
                    current_url = start_url
                    page_count = 1

                    while page_count < pagc.max_pages:
                        self._wait_for_rate_limit()
                        proxies = self._get_proxies()
                        response = self._request_manager.get(
                            current_url, proxies=proxies
                        )

                        if response is None:
                            break

                        next_url = self._pagination_handler.extract_next_page_url(
                            html_content=response.text,
                            next_page_selector=pagc.selector,
                            selector_type=pagc.selector_type,
                            base_url=current_url,
                        )

                        if not next_url or next_url == current_url:
                            break

                        all_urls.append(next_url)
                        current_url = next_url
                        page_count += 1
                else:
                    page_urls = self._pagination_handler.generate_page_urls(
                        start_url
                    )
                    all_urls.extend(page_urls)
            else:
                all_urls.append(start_url)

        return all_urls

    def scrape(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        执行采集任务

        Args:
            progress_callback: 进度回调函数，参数为(当前, 总数)

        Returns:
            采集到的所有数据
        """
        self._running = True
        self._stats["start_time"] = datetime.now()
        self._collected_data = []

        try:
            self._init_modules()
            self._login_if_needed()

            print("开始收集URL...")
            urls = self._collect_all_urls()
            self._stats["total_pages"] = len(urls)
            print(f"共发现 {len(urls)} 个页面需要采集")

            for index, url in enumerate(urls, 1):
                if not self._running:
                    print("采集已取消")
                    break

                print(f"正在采集 [{index}/{len(urls)}]: {url}")

                page_data = self._scrape_single_page(url)
                if page_data:
                    self._collected_data.extend(page_data)
                    self._stats["total_records"] += len(page_data)

                if progress_callback:
                    progress_callback(index, len(urls))

        finally:
            self._stats["end_time"] = datetime.now()
            self._running = False

            if self._rate_limiter:
                self._rate_limiter.release()

        print(
            f"采集完成: 成功 {self._stats['success_pages']} 页, "
            f"失败 {self._stats['failed_pages']} 页, "
            f"共 {self._stats['total_records']} 条记录"
        )

        return self._collected_data

    def export_data(
        self,
        formats: Optional[List[str]] = None,
        data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        """
        导出采集数据

        Args:
            formats: 导出格式列表
            data: 要导出的数据，默认为已采集的数据

        Returns:
            格式到文件路径的映射
        """
        export_data = data if data is not None else self._collected_data
        export_formats = formats if formats else self.config.export.formats

        if not self._data_exporter:
            ec = self.config.export
            self._data_exporter = DataExporter(
                output_dir=ec.output_dir,
                filename_prefix=ec.filename_prefix,
                encoding=ec.encoding,
            )

        return self._data_exporter.export(export_data, export_formats)

    def stop(self):
        """
        停止采集
        """
        self._running = False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取采集统计信息

        Returns:
            统计信息字典
        """
        stats = self._stats.copy()
        if stats["start_time"] and stats["end_time"]:
            duration = stats["end_time"] - stats["start_time"]
            stats["duration_seconds"] = duration.total_seconds()

            if stats["total_pages"] > 0:
                stats["avg_time_per_page"] = (
                    duration.total_seconds() / stats["total_pages"]
                )

        if stats["success_pages"] + stats["failed_pages"] > 0:
            stats["success_rate"] = (
                stats["success_pages"]
                / (stats["success_pages"] + stats["failed_pages"])
                * 100
            )

        return stats

    def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        获取已采集的数据

        Returns:
            采集到的数据列表
        """
        return self._collected_data.copy()
