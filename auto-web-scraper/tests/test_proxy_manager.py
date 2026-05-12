"""
代理管理模块单元测试
"""
import pytest
from unittest.mock import MagicMock, patch, call
from requests.exceptions import RequestException

from auto_web_scraper.proxy_manager import ProxyManager, ProxyInfo


class TestProxyInfo:
    """
    代理信息测试类
    """

    def test_proxy_info_defaults(self):
        """
        测试代理信息默认值
        """
        proxy = ProxyInfo(url="http://127.0.0.1:8080", protocol="http")

        assert proxy.url == "http://127.0.0.1:8080"
        assert proxy.protocol == "http"
        assert proxy.success_count == 0
        assert proxy.fail_count == 0
        assert proxy.last_used is None
        assert proxy.response_time is None


class TestProxyManager:
    """
    代理管理器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.proxies = [
            "http://127.0.0.1:8080",
            "http://127.0.0.1:8081",
            "https://127.0.0.1:8082",
        ]

    def test_init_defaults(self):
        """
        测试默认初始化
        """
        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=self.proxies)

            assert len(manager.proxy_list) == 3
            assert manager.rotation_strategy == "round_robin"
            assert manager._current_index == 0

    def test_parse_proxy_with_http(self):
        """
        测试解析带http前缀的代理
        """
        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=["http://proxy:8080"])

            assert len(manager.proxy_list) == 1
            assert manager.proxy_list[0].url == "http://proxy:8080"
            assert manager.proxy_list[0].protocol == "http"

    def test_parse_proxy_with_https(self):
        """
        测试解析带https前缀的代理
        """
        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=["https://proxy:8080"])

            assert len(manager.proxy_list) == 1
            assert manager.proxy_list[0].url == "https://proxy:8080"
            assert manager.proxy_list[0].protocol == "https"

    def test_parse_proxy_without_protocol(self):
        """
        测试解析不带协议前缀的代理
        """
        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=["proxy:8080"])

            assert len(manager.proxy_list) == 1
            assert manager.proxy_list[0].url.startswith("http://")
            assert manager.proxy_list[0].protocol == "http"

    def test_parse_proxy_invalid(self):
        """
        测试解析无效代理
        """
        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=[])

            assert len(manager.proxy_list) == 0

    @patch("auto_web_scraper.proxy_manager.requests")
    def test_test_proxy_success(self, mock_requests):
        """
        测试代理测试成功
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=self.proxies, auto_test=False)

        proxy = manager.proxy_list[0]
        result = manager.test_proxy(proxy)

        assert result is True
        assert proxy.success_count == 1
        assert proxy.response_time is not None

    @patch("auto_web_scraper.proxy_manager.requests")
    def test_test_proxy_failed(self, mock_requests):
        """
        测试代理测试失败
        """
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response

        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=self.proxies, auto_test=False)

        proxy = manager.proxy_list[0]
        result = manager.test_proxy(proxy)

        assert result is False
        assert proxy.fail_count == 1

    @patch("auto_web_scraper.proxy_manager.requests")
    def test_test_proxy_exception(self, mock_requests):
        """
        测试代理测试异常
        """
        mock_requests.get.side_effect = RequestException("Connection failed")

        with patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies"):
            manager = ProxyManager(proxies=self.proxies, auto_test=False)

        proxy = manager.proxy_list[0]
        result = manager.test_proxy(proxy)

        assert result is False
        assert proxy.fail_count == 1

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_proxy_round_robin(self, mock_test):
        """
        测试轮询策略获取代理
        """
        manager = ProxyManager(
            proxies=self.proxies,
            rotation_strategy="round_robin",
            auto_test=False,
        )
        manager._working_proxies = manager.proxy_list

        proxy1 = manager.get_proxy()
        proxy2 = manager.get_proxy()
        proxy3 = manager.get_proxy()

        assert proxy1["http"] == self.proxies[0]
        assert proxy2["http"] == self.proxies[1]
        assert proxy3["http"] == self.proxies[2]

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_proxy_random(self, mock_test):
        """
        测试随机策略获取代理
        """
        manager = ProxyManager(
            proxies=self.proxies,
            rotation_strategy="random",
            auto_test=False,
        )
        manager._working_proxies = manager.proxy_list

        urls = [p.url for p in manager.proxy_list]

        for _ in range(10):
            proxy = manager.get_proxy()
            assert proxy["http"] in urls

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_proxy_weighted(self, mock_test):
        """
        测试加权策略获取代理
        """
        manager = ProxyManager(
            proxies=self.proxies,
            rotation_strategy="weighted",
            auto_test=False,
        )

        manager.proxy_list[0].success_count = 10
        manager.proxy_list[0].fail_count = 1
        manager.proxy_list[0].response_time = 0.1

        manager.proxy_list[1].success_count = 5
        manager.proxy_list[1].fail_count = 5
        manager.proxy_list[1].response_time = 0.5

        manager.proxy_list[2].success_count = 1
        manager.proxy_list[2].fail_count = 10
        manager.proxy_list[2].response_time = 1.0

        manager._working_proxies = manager.proxy_list

        urls = [p.url for p in manager.proxy_list]

        for _ in range(10):
            proxy = manager.get_proxy()
            assert proxy["http"] in urls

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_proxy_empty(self, mock_test):
        """
        测试空代理池获取代理
        """
        manager = ProxyManager(proxies=[], auto_test=False)

        proxy = manager.get_proxy()

        assert proxy is None

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_mark_proxy_failed(self, mock_test):
        """
        测试标记代理失败
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)
        manager._working_proxies = manager.proxy_list.copy()

        initial_fail = manager.proxy_list[0].fail_count
        manager.mark_proxy_failed("http://127.0.0.1:8080")

        assert manager.proxy_list[0].fail_count == initial_fail + 1

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_mark_proxy_failed_remove(self, mock_test):
        """
        测试标记代理失败后移除
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)
        manager._working_proxies = manager.proxy_list.copy()

        proxy = manager.proxy_list[0]
        proxy.success_count = 1
        proxy.fail_count = 3

        manager.mark_proxy_failed("http://127.0.0.1:8080")

        assert proxy not in manager._working_proxies

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_mark_proxy_success(self, mock_test):
        """
        测试标记代理成功
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        initial_success = manager.proxy_list[0].success_count
        manager.mark_proxy_success("http://127.0.0.1:8080")

        assert manager.proxy_list[0].success_count == initial_success + 1

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_mark_proxy_success_add_back(self, mock_test):
        """
        测试标记代理成功后重新加入可用列表
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        proxy = manager.proxy_list[0]
        proxy.success_count = 3
        proxy.fail_count = 1

        manager.mark_proxy_success("http://127.0.0.1:8080")

        assert proxy in manager._working_proxies

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_working_proxies(self, mock_test):
        """
        测试获取可用代理列表
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)
        manager._working_proxies = manager.proxy_list[:2]

        working = manager.get_working_proxies()

        assert len(working) == 2
        assert self.proxies[0] in working
        assert self.proxies[1] in working

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_proxy_stats(self, mock_test):
        """
        测试获取代理统计信息
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)
        manager._working_proxies = manager.proxy_list[:1]

        stats = manager.get_proxy_stats()

        assert stats["total_proxies"] == 3
        assert stats["working_proxies"] == 1
        assert len(stats["proxies"]) == 3

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_add_proxy_new(self, mock_test):
        """
        测试添加新代理
        """
        manager = ProxyManager(proxies=self.proxies[:2], auto_test=False)

        with patch.object(manager, "test_proxy", return_value=True):
            result = manager.add_proxy("http://new-proxy:8080")

            assert result is True
            assert len(manager.proxy_list) == 3

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_add_proxy_duplicate(self, mock_test):
        """
        测试添加重复代理
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        result = manager.add_proxy("http://127.0.0.1:8080")

        assert result is False
        assert len(manager.proxy_list) == 3

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_remove_proxy_existing(self, mock_test):
        """
        测试移除存在的代理
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)
        manager._working_proxies = manager.proxy_list.copy()

        result = manager.remove_proxy("http://127.0.0.1:8080")

        assert result is True
        assert len(manager.proxy_list) == 2

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_remove_proxy_nonexistent(self, mock_test):
        """
        测试移除不存在的代理
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        result = manager.remove_proxy("http://nonexistent:8080")

        assert result is False
        assert len(manager.proxy_list) == 3

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_test_all_proxies(self, mock_test):
        """
        测试批量测试所有代理
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        with patch.object(manager, "test_proxy") as mock_test_proxy:
            mock_test_proxy.side_effect = [True, True, False]
            stats = manager.test_all_proxies()

            assert stats["total"] == 3
            assert stats["working"] == 2
            assert stats["failed"] == 1
            assert len(manager._working_proxies) == 2

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_weighted_proxy_empty(self, mock_test):
        """
        测试空代理池加权选择
        """
        manager = ProxyManager(proxies=[], auto_test=False)

        with pytest.raises(ValueError, match="代理列表为空"):
            manager._get_weighted_proxy([])

    @patch("auto_web_scraper.proxy_manager.ProxyManager.test_all_proxies")
    def test_get_weighted_proxy_no_history(self, mock_test):
        """
        测试无历史记录的加权选择
        """
        manager = ProxyManager(proxies=self.proxies, auto_test=False)

        result = manager._get_weighted_proxy(manager.proxy_list)

        assert result in manager.proxy_list
