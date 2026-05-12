"""
模板引擎模块单元测试。
"""

import os
import pytest

from reportgen.templates import TemplateEngine


class TestTemplateEngine:
    """
    TemplateEngine类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        engine = TemplateEngine()
        assert engine.template_dir is not None

    def test_init_with_template_dir(self, temp_dir):
        """
        测试使用指定模板目录初始化。
        """
        engine = TemplateEngine(template_dir=temp_dir)
        assert engine.template_dir == temp_dir

    def test_add_filter(self):
        """
        测试添加自定义过滤器。
        """
        engine = TemplateEngine()

        def my_filter(value):
            return f"[{value}]"

        engine.add_filter("my_filter", my_filter)
        assert "my_filter" in engine.env.filters

    def test_add_global(self):
        """
        测试添加全局变量。
        """
        engine = TemplateEngine()
        engine.add_global("my_var", "test_value")
        assert engine.env.globals["my_var"] == "test_value"

    def test_render_string(self):
        """
        测试渲染模板字符串。
        """
        engine = TemplateEngine()

        template = "Hello, {{ name }}!"
        context = {"name": "World"}

        result = engine.render_string(template, context)
        assert result == "Hello, World!"

    def test_render_string_with_filters(self):
        """
        测试使用默认过滤器渲染。
        """
        engine = TemplateEngine()

        template = "Price: {{ price | format_currency }}"
        context = {"price": 1234.56}

        result = engine.render_string(template, context)
        assert "¥" in result

    def test_render_string_with_invalid_template(self):
        """
        测试无效模板字符串抛出异常。
        """
        engine = TemplateEngine()

        with pytest.raises(ValueError, match="模板字符串渲染失败"):
            engine.render_string("{{ }", {})

    def test_render_template_file(self, temp_dir):
        """
        测试渲染模板文件。
        """
        template_path = os.path.join(temp_dir, "test_template.html")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("<h1>{{ title }}</h1>")

        engine = TemplateEngine(template_dir=temp_dir)
        result = engine.render_template("test_template.html", {"title": "测试标题"})

        assert "<h1>测试标题</h1>" in result

    def test_render_template_file_not_found(self, temp_dir):
        """
        测试模板文件不存在时抛出异常。
        """
        engine = TemplateEngine(template_dir=temp_dir)

        with pytest.raises(ValueError, match="模板渲染失败"):
            engine.render_template("non_existent.html", {})

    def test_list_templates(self, temp_dir):
        """
        测试列出模板文件。
        """
        template1 = os.path.join(temp_dir, "template1.html")
        template2 = os.path.join(temp_dir, "template2.jinja")

        with open(template1, "w") as f:
            f.write("")
        with open(template2, "w") as f:
            f.write("")

        engine = TemplateEngine(template_dir=temp_dir)
        templates = engine.list_templates()

        assert "template1.html" in templates
        assert "template2.jinja" in templates

    def test_get_default_template(self):
        """
        测试获取默认模板。
        """
        engine = TemplateEngine()

        template = engine.get_default_template("report")
        assert "<html" in template.lower()

    def test_get_default_template_simple(self):
        """
        测试获取简单模板。
        """
        engine = TemplateEngine()

        template = engine.get_default_template("simple")
        assert "<html" in template.lower()

    def test_get_default_template_invalid_type(self):
        """
        测试无效模板类型返回默认模板。
        """
        engine = TemplateEngine()

        template = engine.get_default_template("invalid_type")
        assert "<html" in template.lower()
