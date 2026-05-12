"""
分页处理模块
支持多种分页方式的自动采集
"""
from typing import Optional, List, Dict, Any, Callable
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import re


class PaginationHandler:
    """
    分页处理器
    支持多种分页方式：URL参数、下一页链接等
    """

    def __init__(
        self,
        max_pages: int = 10,
        start_page: int = 1,
        page_param_name: str = "page",
    ):
        """
        初始化分页处理器

        Args:
            max_pages: 最大采集页数
            start_page: 起始页码
            page_param_name: 页面参数名称
        """
        self.max_pages = max_pages
        self.start_page = start_page
        self.page_param_name = page_param_name
        self.current_page = start_page

    def build_page_url(
        self, base_url: str, page_number: int
    ) -> str:
        """
        根据页码构建URL

        Args:
            base_url: 基础URL
            page_number: 页码

        Returns:
            构建后的URL
        """
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query, keep_blank_values=True)

        query_params[self.page_param_name] = [str(page_number)]

        new_query = urlencode(
            {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
            doseq=True,
        )

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

    def generate_page_urls(
        self, base_url: str
    ) -> List[str]:
        """
        生成所有分页URL

        Args:
            base_url: 基础URL

        Returns:
            分页URL列表
        """
        urls = []
        for page in range(self.start_page, self.start_page + self.max_pages):
            urls.append(self.build_page_url(base_url, page))
        return urls

    def has_next_page(
        self,
        html_content: str,
        next_page_selector: str = "",
        selector_type: str = "css",
    ) -> bool:
        """
        检查是否有下一页

        Args:
            html_content: HTML内容
            next_page_selector: 下一页选择器
            selector_type: 选择器类型

        Returns:
            是否有下一页
        """
        if not next_page_selector:
            return False

        try:
            if selector_type.lower() == "xpath":
                from lxml import etree

                parser = etree.HTMLParser()
                tree = etree.fromstring(html_content, parser)
                elements = tree.xpath(next_page_selector)
                return len(elements) > 0
            else:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html_content, "html.parser")
                elements = soup.select(next_page_selector)
                return len(elements) > 0
        except Exception as e:
            print(f"检查下一页错误: {e}")
            return False

    def extract_next_page_url(
        self,
        html_content: str,
        next_page_selector: str,
        selector_type: str = "css",
        base_url: Optional[str] = None,
    ) -> Optional[str]:
        """
        提取下一页URL

        Args:
            html_content: HTML内容
            next_page_selector: 下一页选择器
            selector_type: 选择器类型
            base_url: 基础URL，用于拼接相对路径

        Returns:
            下一页URL或None
        """
        if not next_page_selector:
            return None

        try:
            next_url = None

            if selector_type.lower() == "xpath":
                from lxml import etree

                parser = etree.HTMLParser()
                tree = etree.fromstring(html_content, parser)

                href_xpath = f"{next_page_selector}/@href"
                href_elements = tree.xpath(href_xpath)
                if href_elements:
                    next_url = str(href_elements[0])
                else:
                    elements = tree.xpath(next_page_selector)
                    if elements:
                        for elem in elements:
                            if hasattr(elem, "get") and elem.get("href"):
                                next_url = elem.get("href")
                                break
            else:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html_content, "html.parser")
                elements = soup.select(next_page_selector)
                if elements:
                    element = elements[0]
                    next_url = element.get("href")
                    if next_url is None and element.name == "a":
                        next_url = element.attrs.get("href")

            if next_url and base_url:
                next_url = self._resolve_url(base_url, next_url)

            return next_url
        except Exception as e:
            print(f"提取下一页URL错误: {e}")
            return None

    def _resolve_url(self, base_url: str, relative_url: str) -> str:
        """
        解析相对URL为绝对URL

        Args:
            base_url: 基础URL
            relative_url: 相对URL

        Returns:
            绝对URL
        """
        if relative_url.startswith("http://") or relative_url.startswith(
            "https://"
        ):
            return relative_url

        parsed_base = urlparse(base_url)

        if relative_url.startswith("//"):
            return f"{parsed_base.scheme}:{relative_url}"

        if relative_url.startswith("/"):
            return (
                f"{parsed_base.scheme}://{parsed_base.netloc}{relative_url}"
            )

        base_path = parsed_base.path.rsplit("/", 1)[0] + "/"
        resolved_path = base_path + relative_url

        resolved_path = re.sub(r"/\./", "/", resolved_path)
        while "/../" in resolved_path:
            resolved_path = re.sub(
                r"[^/]+/\.\./", "", resolved_path, count=1
            )

        return (
            f"{parsed_base.scheme}://{parsed_base.netloc}{resolved_path}"
        )

    def detect_pagination_pattern(
        self,
        urls: List[str],
    ) -> Optional[str]:
        """
        检测URL中的分页模式

        Args:
            urls: URL列表

        Returns:
            分页模式正则表达式或None
        """
        if len(urls) < 2:
            return None

        patterns = [
            r"[?&]page=(\d+)",
            r"[?&]p=(\d+)",
            r"[?&]pg=(\d+)",
            r"/page/(\d+)",
            r"/p/(\d+)",
            r"/(\d+)/?",
        ]

        for pattern in patterns:
            matches = [re.search(pattern, url) for url in urls]
            if all(match for match in matches):
                return pattern

        return None
