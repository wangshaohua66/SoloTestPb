"""
核心采集器模块单元测试
"""
import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch, PropertyMock
from requests import Session, Response

from auto_web_scraper.config import (
    ScraperConfig,
    SelectorConfig,
    PaginationConfig,
    ExportConfig,
    RateLimitConfig,
    RequestConfig,
    ProxyConfig,
    LoginConfig,
)
from auto_web_scraper.scraper import WebScraper


SAMPLE_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Product Page</title>
</head>
<body>
    <h1 class="title">测试商品 1</h1>
    <div class="price">¥99.00</div>
    <div class="description">这是一个测试商品的描述</div>
    <div class="pagination">
        <a href="?page=2" class="next">下一页</a>
    </div>
</body>
</html>
"""

SAMPLE_PAGE_2_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Product Page 2</title>
</head>
<body>
    <h1 class="title">测试商品 2</h1>
    <div class="price">¥199.00</div>
    <div class="description">第二个测试商品</div>
    <div class="pagination">
        <a href="?page=3" class="next">下一页</a>
    </div>
</body>
</html>
"""

LAST_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Last Page</title>
</head>
<body>
    <h1 class="title">最后一个商品</h1>
    <div class="price">¥299.00</div>
    <div class="description">最后一个商品描述</div>
    <div class="pagination">
        <span class="next disabled">下一页</span>
    </div>
</body>
</html>
"""


class TestWebScraper:
    """
    网页采集器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.config = ScraperConfig(
            name="test_scraper",
            start_urls=["https://example.com/products"],
            selectors=[
                SelectorConfig(name="title", selector="h1.title"),
                SelectorConfig(name="price", selector=".price"),
                SelectorConfig(name="description", selector=".description"),
            ],
            pagination=PaginationConfig(enabled=False),
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
            export=ExportConfig(formats=["json"]),
        )

    def test_init_with_config(self):
        """
        测试使用配置对象初始化
        """
        scraper = WebScraper(config=self.config)

        assert scraper.config is self.config
        assert scraper._collected_data == []

    def test_init_with_yaml_file(self):
        """
        测试使用YAML配置文件初始化
        """
        yaml_content = """
name: yaml_test
start_urls:
  - https://test.com
selectors:
  - name: title
    selector: h1
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            scraper = WebScraper(config_file=temp_path)

            assert scraper.config.name == "yaml_test"
            assert scraper.config.start_urls == ["https://test.com"]
            assert len(scraper.config.selectors) == 1
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_init_with_json_file(self):
        """
        测试使用JSON配置文件初始化
        """
        import json

        config_dict = {
            "name": "json_test",
            "start_urls": ["https://test.com"],
            "selectors": [{"name": "title", "selector": "h1"}],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config_dict, f)
            temp_path = f.name

        try:
            scraper = WebScraper(config_file=temp_path)

            assert scraper.config.name == "json_test"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_init_with_invalid_file(self):
        """
        测试使用无效文件格式初始化
        """
        with pytest.raises(ValueError, match="不支持的配置文件格式"):
            WebScraper(config_file="config.txt")

    def test_init_default_config(self):
        """
        测试使用默认配置初始化
        """
        scraper = WebScraper()

        assert scraper.config.name == "default"
        assert scraper.config.start_urls == []

    def test_get_collected_data_empty(self):
        """
        测试获取空的采集数据
        """
        scraper = WebScraper(config=self.config)

        data = scraper.get_collected_data()

        assert data == []

    def test_get_stats_initial(self):
        """
        测试获取初始统计信息
        """
        scraper = WebScraper(config=self.config)

        stats = scraper.get_stats()

        assert stats["total_pages"] == 0
        assert stats["success_pages"] == 0
        assert stats["failed_pages"] == 0
        assert stats["total_records"] == 0

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_single_page(self, MockRequestManager):
        """
        测试采集单个页面
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        scraper = WebScraper(config=self.config)
        data = scraper.scrape()

        assert len(data) == 1
        assert data[0]["title"] == "测试商品 1"
        assert data[0]["price"] == "¥99.00"
        assert data[0]["description"] == "这是一个测试商品的描述"
        assert "_url" in data[0]
        assert "_scraped_at" in data[0]

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_with_pagination(self, MockRequestManager):
        """
        测试带分页的采集
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response1 = MagicMock(spec=Response)
        mock_response1.text = SAMPLE_PAGE_HTML

        mock_response2 = MagicMock(spec=Response)
        mock_response2.text = SAMPLE_PAGE_2_HTML

        mock_response3 = MagicMock(spec=Response)
        mock_response3.text = LAST_PAGE_HTML

        mock_manager.get.side_effect = [
            mock_response1,
            mock_response1,
            mock_response2,
            mock_response3,
        ]

        config = ScraperConfig(
            name="pagination_test",
            start_urls=["https://example.com/products?page=1"],
            selectors=[
                SelectorConfig(name="title", selector="h1.title"),
            ],
            pagination=PaginationConfig(
                enabled=True,
                selector="a.next",
                selector_type="css",
                max_pages=3,
            ),
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        scraper = WebScraper(config=config)
        data = scraper.scrape()

        assert len(data) >= 1

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_with_login(self, MockRequestManager):
        """
        测试带登录的采集
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        config = ScraperConfig(
            name="login_test",
            start_urls=["https://example.com/products"],
            selectors=[SelectorConfig(name="title", selector="h1.title")],
            login=LoginConfig(
                login_url="https://example.com/login",
                username="testuser",
                password="testpass",
            ),
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        scraper = WebScraper(config=config)

        with patch.object(
            scraper._authenticator, "form_login", return_value=True
        ) as mock_login:
            data = scraper.scrape()

            mock_login.assert_called_once()

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_proxy_usage(self, MockRequestManager):
        """
        测试使用代理采集
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        config = ScraperConfig(
            name="proxy_test",
            start_urls=["https://example.com/products"],
            selectors=[SelectorConfig(name="title", selector="h1.title")],
            proxy=ProxyConfig(
                enabled=True,
                proxies=["http://proxy1:8080", "http://proxy2:8080"],
            ),
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        scraper = WebScraper(config=config)
        data = scraper.scrape()

        assert len(data) == 1

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_failed_request(self, MockRequestManager):
        """
        测试采集时请求失败
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_manager.get.return_value = None

        scraper = WebScraper(config=self.config)
        data = scraper.scrape()

        assert len(data) == 0

        stats = scraper.get_stats()
        assert stats["failed_pages"] == 1

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_exception_handling(self, MockRequestManager):
        """
        测试采集时异常处理
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_manager.get.side_effect = Exception("Unexpected error")

        scraper = WebScraper(config=self.config)
        data = scraper.scrape()

        assert len(data) == 0

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_progress_callback(self, MockRequestManager):
        """
        测试采集进度回调
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        config = ScraperConfig(
            name="progress_test",
            start_urls=[
                "https://example.com/products/1",
                "https://example.com/products/2",
            ],
            selectors=[SelectorConfig(name="title", selector="h1.title")],
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        progress_calls = []

        def callback(current, total):
            progress_calls.append((current, total))

        scraper = WebScraper(config=config)
        data = scraper.scrape(progress_callback=callback)

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_stop_scrape(self, MockRequestManager):
        """
        测试停止采集
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        config = ScraperConfig(
            name="stop_test",
            start_urls=[
                "https://example.com/products/1",
                "https://example.com/products/2",
                "https://example.com/products/3",
            ],
            selectors=[SelectorConfig(name="title", selector="h1.title")],
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        def stop_after_one(current, total):
            if current >= 1:
                scraper.stop()

        scraper = WebScraper(config=config)
        data = scraper.scrape(progress_callback=stop_after_one)

        assert len(data) >= 1

    @patch("auto_web_scraper.scraper.DataExporter")
    def test_export_data(self, MockDataExporter):
        """
        测试导出数据
        """
        mock_exporter = MagicMock()
        mock_exporter.export.return_value = {
            "json": "/output/test.json",
        }
        MockDataExporter.return_value = mock_exporter

        test_data = [
            {"title": "Test 1", "price": "100"},
            {"title": "Test 2", "price": "200"},
        ]

        scraper = WebScraper(config=self.config)
        scraper._collected_data = test_data

        result = scraper.export_data(formats=["json"])

        assert "json" in result

    @patch("auto_web_scraper.scraper.DataExporter")
    def test_export_custom_data(self, MockDataExporter):
        """
        测试导出自定义数据
        """
        mock_exporter = MagicMock()
        mock_exporter.export.return_value = {
            "csv": "/output/custom.csv",
        }
        MockDataExporter.return_value = mock_exporter

        custom_data = [{"custom_field": "value"}]

        scraper = WebScraper(config=self.config)

        result = scraper.export_data(data=custom_data, formats=["csv"])

        assert "csv" in result

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_stats_calculation(self, MockRequestManager):
        """
        测试采集统计计算
        """
        mock_manager = MagicMock()
        MockRequestManager.return_value = mock_manager

        mock_response = MagicMock(spec=Response)
        mock_response.text = SAMPLE_PAGE_HTML
        mock_manager.get.return_value = mock_response

        scraper = WebScraper(config=self.config)
        data = scraper.scrape()

        stats = scraper.get_stats()

        assert stats["total_pages"] == 1
        assert stats["success_pages"] == 1
        assert stats["failed_pages"] == 0
        assert stats["total_records"] == 1
        assert stats["success_rate"] == 100.0
        assert "duration_seconds" in stats

    @patch("auto_web_scraper.scraper.RequestManager")
    def test_scrape_empty_urls(self, MockRequestManager):
        """
        测试空URL列表采集
        """
        config = ScraperConfig(
            name="empty_test",
            start_urls=[],
            selectors=[SelectorConfig(name="title", selector="h1.title")],
            rate_limit=RateLimitConfig(min_delay=0.01, max_delay=0.02),
        )

        scraper = WebScraper(config=config)
        data = scraper.scrape()

        assert len(data) == 0

        stats = scraper.get_stats()
        assert stats["total_pages"] == 0

    def test_get_stats_without_end_time(self):
        """
        测试没有结束时间时的统计
        """
        scraper = WebScraper(config=self.config)
        scraper._stats = {
            "start_time": None,
            "end_time": None,
            "total_pages": 0,
            "success_pages": 0,
            "failed_pages": 0,
            "total_records": 0,
        }

        stats = scraper.get_stats()

        assert "duration_seconds" not in stats
