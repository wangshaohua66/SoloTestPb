"""
模板渲染模块单元测试
"""

import os

import allure
import pytest

from batch_mail.template_renderer import TemplateRenderer


@allure.feature("模板渲染")
@allure.story("初始化")
class TestTemplateRendererInit:
    """
    TemplateRenderer初始化测试类
    """

    @allure.title("测试默认初始化")
    def test_default_init(self):
        """
        测试默认初始化
        """
        renderer = TemplateRenderer()

        assert renderer.template_dir == os.getcwd()
        assert renderer.env is not None

    @allure.title("测试指定模板目录")
    def test_custom_template_dir(self, temp_dir: str):
        """
        测试指定模板目录
        """
        renderer = TemplateRenderer(template_dir=temp_dir)

        assert renderer.template_dir == temp_dir

    @allure.title("测试关闭自动转义")
    def test_no_autoescape(self, temp_dir: str):
        """
        测试关闭自动转义
        """
        renderer = TemplateRenderer(template_dir=temp_dir, autoescape=False)
        result = renderer.render_from_string(
            "Hello {{ name }}",
            {"name": "<script>alert('xss')</script>"},
        )

        assert "<script>" in result


@allure.feature("模板渲染")
@allure.story("字符串模板")
class TestTemplateRendererString:
    """
    TemplateRenderer字符串模板测试类
    """

    @allure.title("测试渲染字符串模板")
    def test_render_from_string(self):
        """
        测试渲染字符串模板
        """
        renderer = TemplateRenderer()
        result = renderer.render_from_string(
            "Hello {{ name }}!",
            {"name": "World"},
        )

        assert result == "Hello World!"

    @allure.title("测试渲染包含条件的模板")
    def test_render_conditional(self):
        """
        测试渲染包含条件语句的模板
        """
        renderer = TemplateRenderer()
        template = "{% if is_vip %}VIP{% else %}普通{% endif %}用户"

        result_vip = renderer.render_from_string(template, {"is_vip": True})
        result_normal = renderer.render_from_string(template, {"is_vip": False})

        assert result_vip == "VIP用户"
        assert result_normal == "普通用户"

    @allure.title("测试渲染包含循环的模板")
    def test_render_loop(self):
        """
        测试渲染包含循环的模板
        """
        renderer = TemplateRenderer()
        template = "{% for item in items %}{{ item }}{% if not loop.last %},{% endif %}{% endfor %}"

        result = renderer.render_from_string(
            template,
            {"items": ["a", "b", "c"]},
        )

        assert result == "a,b,c"

    @allure.title("测试HTML自动转义")
    def test_html_autoescape(self):
        """
        测试HTML自动转义
        """
        renderer = TemplateRenderer(autoescape=True)
        result = renderer.render_from_string(
            "{{ content }}",
            {"content": "<script>alert(1)</script>"},
        )

        assert "<script>" not in result
        assert "&lt;script&gt;" in result


@allure.feature("模板渲染")
@allure.story("文件模板")
class TestTemplateRendererFile:
    """
    TemplateRenderer文件模板测试类
    """

    @allure.title("测试渲染文件模板")
    def test_render_from_file(self, temp_dir: str):
        """
        测试从文件渲染模板
        """
        template_path = os.path.join(temp_dir, "template.html")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("<h1>Hello {{ name }}</h1>")

        renderer = TemplateRenderer(template_dir=temp_dir)
        result = renderer.render_from_file("template.html", {"name": "张三"})

        assert result == "<h1>Hello 张三</h1>"

    @allure.title("测试文件不存在抛出异常")
    def test_file_not_found(self, temp_dir: str):
        """
        测试文件不存在时抛出FileNotFoundError
        """
        renderer = TemplateRenderer(template_dir=temp_dir)

        with pytest.raises(FileNotFoundError):
            renderer.render_from_file("nonexistent.html", {})


@allure.feature("模板渲染")
@allure.story("便捷方法")
class TestTemplateRendererConvenience:
    """
    TemplateRenderer便捷方法测试类
    """

    @allure.title("测试渲染主题")
    def test_render_subject(self):
        """
        测试渲染邮件主题
        """
        renderer = TemplateRenderer()
        subject = renderer.render_subject(
            "亲爱的 {{ name }}，您的订单已确认",
            {"name": "张三"},
        )

        assert subject == "亲爱的 张三，您的订单已确认"

    @allure.title("测试渲染正文为字符串")
    def test_render_body_string(self):
        """
        测试渲染正文（内联字符串）
        """
        renderer = TemplateRenderer()
        body = renderer.render_body(
            "您好 {{ name }}！您的优惠码是：{{ code }}",
            {"name": "李四", "code": "SUMMER2024"},
            is_html=False,
        )

        assert body == "您好 李四！您的优惠码是：SUMMER2024"

    @allure.title("测试渲染正文为文件")
    def test_render_body_file(self, temp_dir: str):
        """
        测试渲染正文（文件）
        """
        template_path = os.path.join(temp_dir, "email.txt")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("感谢您，{{ name }}！")

        renderer = TemplateRenderer(template_dir=temp_dir)
        body = renderer.render_body(
            "email.txt",
            {"name": "王五"},
            is_html=False,
        )

        assert body == "感谢您，王五！"

    @allure.title("测试判断文件路径")
    def test_is_file_path(self, temp_dir: str):
        """
        测试_is_file_path方法
        """
        renderer = TemplateRenderer(template_dir=temp_dir)

        assert renderer._is_file_path("template.html") is False

        template_file = os.path.join(temp_dir, "template.html")
        with open(template_file, "w") as f:
            f.write("test")

        assert renderer._is_file_path("template.html") is True

        inline_with_newline = "Hello\n{{ name }}"
        assert renderer._is_file_path(inline_with_newline) is False

        no_extension = "hello"
        assert renderer._is_file_path(no_extension) is False
