"""
代理管理模块
支持代理IP轮换，提高采集成功率
"""
from typing import List, Dict, Optional, Any
import random
import requests
from dataclasses import dataclass


@dataclass
class ProxyInfo:
    """
    代理信息类
    存储代理的详细信息
    """
    url: str
    protocol: str
    success_count: int = 0
    fail_count: int = 0
    last_used: Optional[float] = None
    response_time: Optional[float] = None


class ProxyManager:
    """
    代理管理器
    管理代理池，支持多种轮换策略
    """

    def __init__(
        self,
        proxies: List[str],
        rotation_strategy: str = "round_robin",
        test_url: str = "https://httpbin.org/ip",
        test_timeout: int = 5,
        auto_test: bool = True,
    ):
        """
        初始化代理管理器

        Args:
            proxies: 代理地址列表
            rotation_strategy: 轮换策略：round_robin, random, weighted
            test_url: 代理测试URL
            test_timeout: 测试超时时间
            auto_test: 是否自动测试代理
        """
        self.proxy_list: List[ProxyInfo] = []
        self.rotation_strategy = rotation_strategy
        self.test_url = test_url
        self.test_timeout = test_timeout
        self._current_index = 0
        self._working_proxies: List[ProxyInfo] = []

        for proxy_url in proxies:
            proxy_info = self._parse_proxy(proxy_url)
            if proxy_info:
                self.proxy_list.append(proxy_info)

        if auto_test:
            self.test_all_proxies()

    def _parse_proxy(self, proxy_url: str) -> Optional[ProxyInfo]:
        """
        解析代理地址

        Args:
            proxy_url: 代理地址字符串

        Returns:
            ProxyInfo对象或None
        """
        try:
            if proxy_url.startswith("http://"):
                protocol = "http"
            elif proxy_url.startswith("https://"):
                protocol = "https"
            else:
                protocol = "http"
                proxy_url = f"http://{proxy_url}"
            return ProxyInfo(url=proxy_url, protocol=protocol)
        except Exception:
            return None

    def test_proxy(self, proxy_info: ProxyInfo) -> bool:
        """
        测试代理是否可用

        Args:
            proxy_info: 代理信息

        Returns:
            是否可用
        """
        import time

        try:
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies={
                    "http": proxy_info.url,
                    "https": proxy_info.url,
                },
                timeout=self.test_timeout,
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                proxy_info.success_count += 1
                proxy_info.response_time = response_time
                return True
            else:
                proxy_info.fail_count += 1
                return False
        except Exception:
            proxy_info.fail_count += 1
            return False

    def test_all_proxies(self) -> Dict[str, int]:
        """
        测试所有代理

        Returns:
            测试结果统计
        """
        import concurrent.futures

        working = 0
        failed = 0
        self._working_proxies = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy
                for proxy in self.proxy_list
            }
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    result = future.result()
                    if result:
                        working += 1
                        self._working_proxies.append(proxy)
                    else:
                        failed += 1
                except Exception:
                    failed += 1

        return {"total": len(self.proxy_list), "working": working, "failed": failed}

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取下一个代理

        Returns:
            代理配置字典或None
        """
        if not self._working_proxies:
            if not self.proxy_list:
                return None
            proxies_to_use = self.proxy_list
        else:
            proxies_to_use = self._working_proxies

        if self.rotation_strategy == "random":
            proxy_info = random.choice(proxies_to_use)
        elif self.rotation_strategy == "weighted":
            proxy_info = self._get_weighted_proxy(proxies_to_use)
        else:
            proxy_info = proxies_to_use[self._current_index % len(proxies_to_use)]
            self._current_index += 1

        return {
            "http": proxy_info.url,
            "https": proxy_info.url,
        }

    def _get_weighted_proxy(
        self, proxies: List[ProxyInfo]
    ) -> ProxyInfo:
        """
        基于权重选择代理

        Args:
            proxies: 代理列表

        Returns:
            选中的代理
        """
        if not proxies:
            raise ValueError("代理列表为空")

        weights = []
        for proxy in proxies:
            total = proxy.success_count + proxy.fail_count
            if total == 0:
                weight = 1.0
            else:
                success_rate = proxy.success_count / total
                weight = success_rate * (1 / (proxy.response_time or 1))
            weights.append(max(0.1, weight))

        return random.choices(proxies, weights=weights, k=1)[0]

    def mark_proxy_failed(self, proxy_url: str):
        """
        标记代理失败

        Args:
            proxy_url: 代理地址
        """
        for proxy in self.proxy_list:
            if proxy.url == proxy_url or proxy_url in proxy.url:
                proxy.fail_count += 1
                if proxy in self._working_proxies:
                    if proxy.fail_count > proxy.success_count * 2:
                        self._working_proxies.remove(proxy)
                break

    def mark_proxy_success(self, proxy_url: str):
        """
        标记代理成功

        Args:
            proxy_url: 代理地址
        """
        for proxy in self.proxy_list:
            if proxy.url == proxy_url or proxy_url in proxy.url:
                proxy.success_count += 1
                if proxy not in self._working_proxies:
                    if proxy.success_count > proxy.fail_count:
                        self._working_proxies.append(proxy)
                break

    def get_working_proxies(self) -> List[str]:
        """
        获取可用的代理列表

        Returns:
            代理URL列表
        """
        return [proxy.url for proxy in self._working_proxies]

    def get_proxy_stats(self) -> Dict[str, Any]:
        """
        获取代理统计信息

        Returns:
            统计信息字典
        """
        return {
            "total_proxies": len(self.proxy_list),
            "working_proxies": len(self._working_proxies),
            "proxies": [
                {
                    "url": p.url,
                    "success_count": p.success_count,
                    "fail_count": p.fail_count,
                    "response_time": p.response_time,
                }
                for p in self.proxy_list
            ],
        }

    def add_proxy(self, proxy_url: str) -> bool:
        """
        添加新代理

        Args:
            proxy_url: 代理地址

        Returns:
            是否添加成功
        """
        proxy_info = self._parse_proxy(proxy_url)
        if proxy_info:
            if not any(p.url == proxy_info.url for p in self.proxy_list):
                self.proxy_list.append(proxy_info)
                if self.test_proxy(proxy_info):
                    self._working_proxies.append(proxy_info)
                return True
        return False

    def remove_proxy(self, proxy_url: str) -> bool:
        """
        移除代理

        Args:
            proxy_url: 代理地址

        Returns:
            是否移除成功
        """
        for proxy in self.proxy_list[:]:
            if proxy.url == proxy_url:
                self.proxy_list.remove(proxy)
                if proxy in self._working_proxies:
                    self._working_proxies.remove(proxy)
                return True
        return False
