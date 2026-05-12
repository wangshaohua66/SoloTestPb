"""
数据提取模块
支持CSS选择器和XPath提取数据
"""
from typing import List, Dict, Any, Optional, Union
from bs4 import BeautifulSoup
from lxml import etree
import re


class DataExtractor:
    """
    数据提取器
    使用BeautifulSoup和lxml解析HTML，提取数据
    """

    def __init__(self, html_content: str, parser: str = "html.parser"):
        """
        初始化数据提取器

        Args:
            html_content: HTML内容字符串
            parser: 解析器类型，默认为html.parser
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, parser)
        self.lxml_tree = None
        try:
            parser = etree.HTMLParser()
            self.lxml_tree = etree.fromstring(html_content, parser)
        except Exception:
            pass

    def extract_by_css(
        self,
        selector: str,
        attribute: Optional[str] = None,
        is_list: bool = False,
        default_value: Any = None,
    ) -> Union[str, List[str], Any]:
        """
        使用CSS选择器提取数据

        Args:
            selector: CSS选择器
            attribute: 要提取的属性名，None表示提取文本
            is_list: 是否返回列表
            default_value: 默认值

        Returns:
            提取的数据
        """
        try:
            elements = self.soup.select(selector)
            if not elements:
                return [] if is_list else default_value

            results = []
            for element in elements:
                if attribute:
                    value = element.get(attribute, default_value)
                else:
                    value = element.get_text(strip=True)
                if value is not None:
                    results.append(value)

            if is_list:
                return results
            return results[0] if results else default_value
        except Exception as e:
            print(f"CSS选择器提取错误: {e}")
            return [] if is_list else default_value

    def extract_by_xpath(
        self,
        selector: str,
        attribute: Optional[str] = None,
        is_list: bool = False,
        default_value: Any = None,
    ) -> Union[str, List[str], Any]:
        """
        使用XPath提取数据

        Args:
            selector: XPath表达式
            attribute: 要提取的属性名，None表示提取文本
            is_list: 是否返回列表
            default_value: 默认值

        Returns:
            提取的数据
        """
        if self.lxml_tree is None:
            return [] if is_list else default_value

        try:
            if attribute:
                if not selector.endswith(f"/@{attribute}"):
                    selector = f"{selector}/@{attribute}"
                elements = self.lxml_tree.xpath(selector)
            else:
                elements = self.lxml_tree.xpath(selector)

            if not elements:
                return [] if is_list else default_value

            results = []
            for element in elements:
                if isinstance(element, etree._Element):
                    value = "".join(element.itertext()).strip()
                else:
                    value = str(element).strip()
                if value:
                    results.append(value)

            if is_list:
                return results
            return results[0] if results else default_value
        except Exception as e:
            print(f"XPath提取错误: {e}")
            return [] if is_list else default_value

    def extract(
        self,
        selector: str,
        selector_type: str = "css",
        attribute: Optional[str] = None,
        is_list: bool = False,
        default_value: Any = None,
    ) -> Union[str, List[str], Any]:
        """
        提取数据，根据选择器类型自动选择方法

        Args:
            selector: 选择器表达式
            selector_type: 选择器类型：'css'或'xpath'
            attribute: 要提取的属性名
            is_list: 是否返回列表
            default_value: 默认值

        Returns:
            提取的数据
        """
        if selector_type.lower() == "xpath":
            return self.extract_by_xpath(
                selector, attribute, is_list, default_value
            )
        else:
            return self.extract_by_css(
                selector, attribute, is_list, default_value
            )

    def extract_multiple(
        self, selectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量提取多个数据

        Args:
            selectors: 选择器配置列表，每项包含：
                - name: 字段名
                - selector: 选择器
                - selector_type: 选择器类型
                - attribute: 属性名(可选)
                - is_list: 是否列表(可选)
                - default_value: 默认值(可选)

        Returns:
            提取的数据字典
        """
        result = {}
        for sel_config in selectors:
            name = sel_config.get("name")
            selector = sel_config.get("selector")
            selector_type = sel_config.get("selector_type", "css")
            attribute = sel_config.get("attribute")
            is_list = sel_config.get("is_list", False)
            default_value = sel_config.get("default_value")

            result[name] = self.extract(
                selector=selector,
                selector_type=selector_type,
                attribute=attribute,
                is_list=is_list,
                default_value=default_value,
            )
        return result

    def extract_links(self, selector: str = "a") -> List[str]:
        """
        提取页面中的所有链接

        Args:
            selector: 链接选择器

        Returns:
            链接列表
        """
        return self.extract_by_css(
            selector=selector,
            attribute="href",
            is_list=True,
            default_value=[],
        )

    def extract_images(self, selector: str = "img") -> List[str]:
        """
        提取页面中的所有图片URL

        Args:
            selector: 图片选择器

        Returns:
            图片URL列表
        """
        return self.extract_by_css(
            selector=selector,
            attribute="src",
            is_list=True,
            default_value=[],
        )

    def clean_text(self, text: str) -> str:
        """
        清洗文本，去除多余空格和换行

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()
