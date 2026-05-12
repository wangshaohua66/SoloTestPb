"""
数据提取模块单元测试
"""
import pytest

from auto_web_scraper.data_extractor import DataExtractor


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1 class="main-title">Hello World</h1>
    <div id="content">
        <p class="description">This is a test page.</p>
        <a href="https://example.com/page1" class="link">Link 1</a>
        <a href="https://example.com/page2" class="link">Link 2</a>
    </div>
    <ul class="items">
        <li data-id="1">Item 1</li>
        <li data-id="2">Item 2</li>
        <li data-id="3">Item 3</li>
    </ul>
    <img src="https://example.com/image1.jpg" alt="Image 1">
    <img src="https://example.com/image2.jpg" alt="Image 2">
</body>
</html>
"""


class TestDataExtractor:
    """
    数据提取器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.extractor = DataExtractor(SAMPLE_HTML)

    def test_extract_by_css_text(self):
        """
        测试CSS选择器提取文本
        """
        result = self.extractor.extract_by_css("h1.main-title")
        assert result == "Hello World"

    def test_extract_by_css_attribute(self):
        """
        测试CSS选择器提取属性
        """
        result = self.extractor.extract_by_css(
            "ul.items li:first-child", attribute="data-id"
        )
        assert result == "1"

    def test_extract_by_css_list(self):
        """
        测试CSS选择器提取列表
        """
        result = self.extractor.extract_by_css(
            "ul.items li", is_list=True
        )
        assert len(result) == 3
        assert result == ["Item 1", "Item 2", "Item 3"]

    def test_extract_by_css_default_value(self):
        """
        测试CSS选择器默认值
        """
        result = self.extractor.extract_by_css(
            ".non-existent", default_value="N/A"
        )
        assert result == "N/A"

    def test_extract_by_xpath_text(self):
        """
        测试XPath提取文本
        """
        result = self.extractor.extract_by_xpath("//h1[@class='main-title']")
        assert result == "Hello World"

    def test_extract_by_xpath_attribute(self):
        """
        测试XPath提取属性
        """
        result = self.extractor.extract_by_xpath(
            "//ul[@class='items']/li[1]", attribute="data-id"
        )
        assert result == "1"

    def test_extract_by_xpath_list(self):
        """
        测试XPath提取列表
        """
        result = self.extractor.extract_by_xpath(
            "//ul[@class='items']/li", is_list=True
        )
        assert len(result) == 3

    def test_extract_css(self):
        """
        测试通用extract方法使用CSS
        """
        result = self.extractor.extract(
            selector="h1.main-title",
            selector_type="css",
        )
        assert result == "Hello World"

    def test_extract_xpath(self):
        """
        测试通用extract方法使用XPath
        """
        result = self.extractor.extract(
            selector="//h1[@class='main-title']",
            selector_type="xpath",
        )
        assert result == "Hello World"

    def test_extract_multiple(self):
        """
        测试批量提取
        """
        selectors = [
            {"name": "title", "selector": "h1.main-title"},
            {"name": "description", "selector": "p.description"},
            {
                "name": "items",
                "selector": "ul.items li",
                "is_list": True,
            },
        ]
        result = self.extractor.extract_multiple(selectors)

        assert result["title"] == "Hello World"
        assert result["description"] == "This is a test page."
        assert len(result["items"]) == 3

    def test_extract_links(self):
        """
        测试提取链接
        """
        links = self.extractor.extract_links("a.link")
        assert len(links) == 2
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links

    def test_extract_images(self):
        """
        测试提取图片
        """
        images = self.extractor.extract_images()
        assert len(images) == 2
        assert "https://example.com/image1.jpg" in images

    def test_clean_text(self):
        """
        测试文本清洗
        """
        dirty_text = "  Hello   \n  World  \t"
        clean = self.extractor.clean_text(dirty_text)
        assert clean == "Hello World"

    def test_empty_result(self):
        """
        测试空结果
        """
        result = self.extractor.extract_by_css(".nonexistent", is_list=True)
        assert result == []

        result_single = self.extractor.extract_by_css(
            ".nonexistent", default_value=None
        )
        assert result_single is None
