"""
分页处理模块单元测试
"""
import pytest

from auto_web_scraper.pagination import PaginationHandler


class TestPaginationHandler:
    """
    分页处理器测试类
    """

    def test_build_page_url(self):
        """
        测试构建分页URL
        """
        handler = PaginationHandler(max_pages=10)

        url = handler.build_page_url("https://example.com/items", 2)
        assert "page=2" in url

        url2 = handler.build_page_url("https://example.com/items?category=books", 3)
        assert "page=3" in url2
        assert "category=books" in url2

    def test_generate_page_urls(self):
        """
        测试生成分页URL列表
        """
        handler = PaginationHandler(
            max_pages=5, start_page=1, page_param_name="page"
        )

        urls = handler.generate_page_urls("https://example.com/list")

        assert len(urls) == 5
        for i, url in enumerate(urls, 1):
            assert f"page={i}" in url

    def test_has_next_page_css(self):
        """
        测试CSS选择器检查下一页
        """
        html_with_next = """
        <div class="pagination">
            <a href="?page=2" class="next">Next</a>
        </div>
        """
        html_without_next = """
        <div class="pagination">
            <span class="next disabled">Next</span>
        </div>
        """

        handler = PaginationHandler()

        assert handler.has_next_page(
            html_with_next, next_page_selector=".next", selector_type="css"
        ) is True

        assert handler.has_next_page(
            html_without_next, next_page_selector="a.next", selector_type="css"
        ) is False

    def test_has_next_page_xpath(self):
        """
        测试XPath检查下一页
        """
        html = """
        <div>
            <a href="?p=2" rel="next">Next Page</a>
        </div>
        """

        handler = PaginationHandler()

        assert handler.has_next_page(
            html, next_page_selector="//a[@rel='next']", selector_type="xpath"
        ) is True

        assert handler.has_next_page(
            html, next_page_selector="//a[@rel='prev']", selector_type="xpath"
        ) is False

    def test_extract_next_page_url_css(self):
        """
        测试CSS选择器提取下一页URL
        """
        html = """
        <div class="pagination">
            <a href="https://example.com/page/2" class="next">Next</a>
        </div>
        """

        handler = PaginationHandler()

        next_url = handler.extract_next_page_url(
            html, next_page_selector="a.next", selector_type="css"
        )
        assert next_url == "https://example.com/page/2"

    def test_extract_next_page_url_with_base(self):
        """
        测试带基础URL解析相对路径
        """
        html = """
        <a href="/page/2" class="next">Next</a>
        """

        handler = PaginationHandler()

        next_url = handler.extract_next_page_url(
            html,
            next_page_selector="a.next",
            selector_type="css",
            base_url="https://example.com/list/page/1",
        )
        assert next_url == "https://example.com/page/2"

    def test_resolve_url_absolute(self):
        """
        测试解析绝对URL
        """
        handler = PaginationHandler()

        result = handler._resolve_url(
            "https://example.com/page1",
            "https://example.com/page2",
        )
        assert result == "https://example.com/page2"

    def test_resolve_url_relative_root(self):
        """
        测试解析根路径URL
        """
        handler = PaginationHandler()

        result = handler._resolve_url(
            "https://example.com/a/b",
            "/c/d",
        )
        assert result == "https://example.com/c/d"

    def test_resolve_url_relative(self):
        """
        测试解析相对URL
        """
        handler = PaginationHandler()

        result = handler._resolve_url(
            "https://example.com/a/page1",
            "page2",
        )
        assert result == "https://example.com/a/page2"

    def test_detect_pagination_pattern(self):
        """
        测试检测分页模式
        """
        handler = PaginationHandler()

        urls = [
            "https://example.com/items?page=1",
            "https://example.com/items?page=2",
            "https://example.com/items?page=3",
        ]

        pattern = handler.detect_pagination_pattern(urls)
        assert pattern is not None

    def test_no_selector_returns_none(self):
        """
        测试没有选择器时返回None
        """
        handler = PaginationHandler()

        assert handler.has_next_page("<html></html>", "") is False
        assert (
            handler.extract_next_page_url("<html></html>", "") is None
        )
