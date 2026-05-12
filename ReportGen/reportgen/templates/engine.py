"""
模板引擎模块。

提供基于Jinja2的模板渲染功能，支持自定义报表格式。
"""

import os
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """
    模板引擎类。

    提供基于Jinja2的模板加载和渲染功能。
    """

    def __init__(
        self,
        template_dir: Optional[str] = None,
        auto_reload: bool = True,
    ):
        """
        初始化模板引擎。

        Args:
            template_dir: 模板目录路径，默认为当前目录。
            auto_reload: 是否自动重载模板文件，默认为True。
        """
        if template_dir is None:
            template_dir = os.getcwd()

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            auto_reload=auto_reload,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self._register_default_filters()

    def _register_default_filters(self):
        """
        注册默认的Jinja2过滤器。
        """

        def format_number(value, decimal_places=2):
            """
            格式化数字。
            """
            try:
                return f"{float(value):.{decimal_places}f}"
            except (ValueError, TypeError):
                return str(value)

        def format_currency(value, symbol="¥"):
            """
            格式化货币。
            """
            try:
                return f"{symbol}{float(value):,.2f}"
            except (ValueError, TypeError):
                return str(value)

        def format_date(value, format="%Y-%m-%d"):
            """
            格式化日期。
            """
            try:
                if hasattr(value, "strftime"):
                    return value.strftime(format)
                return str(value)
            except Exception:
                return str(value)

        def format_percent(value, decimal_places=2):
            """
            格式化百分比。
            """
            try:
                return f"{float(value) * 100:.{decimal_places}f}%"
            except (ValueError, TypeError):
                return str(value)

        self.env.filters["format_number"] = format_number
        self.env.filters["format_currency"] = format_currency
        self.env.filters["format_date"] = format_date
        self.env.filters["format_percent"] = format_percent

    def add_filter(self, name: str, filter_func):
        """
        添加自定义过滤器。

        Args:
            name: 过滤器名称。
            filter_func: 过滤器函数。
        """
        self.env.filters[name] = filter_func

    def add_global(self, name: str, value: Any):
        """
        添加全局变量。

        Args:
            name: 全局变量名称。
            value: 全局变量值。
        """
        self.env.globals[name] = value

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
    ) -> str:
        """
        渲染模板文件。

        Args:
            template_name: 模板文件名。
            context: 模板上下文数据。

        Returns:
            渲染后的字符串。

        Raises:
            FileNotFoundError: 模板文件不存在时抛出。
            ValueError: 模板渲染失败时抛出。
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"模板渲染失败: {str(e)}")

    def render_string(
        self,
        template_string: str,
        context: Dict[str, Any],
    ) -> str:
        """
        渲染模板字符串。

        Args:
            template_string: 模板字符串。
            context: 模板上下文数据。

        Returns:
            渲染后的字符串。

        Raises:
            ValueError: 模板渲染失败时抛出。
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"模板字符串渲染失败: {str(e)}")

    def list_templates(self) -> List[str]:
        """
        列出模板目录中的所有模板文件。

        Returns:
            模板文件名列表。
        """
        templates = []
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith((".html", ".jinja", ".jinja2", ".tmpl")):
                    rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                    templates.append(rel_path)
        return templates

    def get_default_template(self, template_type: str = "report") -> str:
        """
        获取默认模板字符串。

        Args:
            template_type: 模板类型，默认为'report'。

        Returns:
            默认模板字符串。
        """
        if template_type == "report":
            return self._get_default_report_template()
        elif template_type == "simple":
            return self._get_simple_report_template()
        else:
            return self._get_default_report_template()

    def _get_default_report_template(self) -> str:
        """
        获取默认报表模板。
        """
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ report_title | default('报表') }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .report-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .report-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .report-date {
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f4f4f4;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .summary {
            margin-top: 30px;
            padding: 15px;
            background-color: #f4f4f4;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="report-header">
        <div class="report-title">{{ report_title | default('报表') }}</div>
        <div class="report-date">生成时间: {{ report_date | default('') }}</div>
    </div>

    {% if summary %}
    <div class="summary">
        <h3>数据摘要</h3>
        {% for key, value in summary.items() %}
        <p><strong>{{ key }}:</strong> {{ value }}</p>
        {% endfor %}
    </div>
    {% endif %}

    {% if data is defined and data is not none %}
    <table>
        <thead>
            <tr>
                {% for column in columns %}
                <th>{{ column }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                {% for column in columns %}
                <td>{{ row[column] }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endif %}
</body>
</html>"""

    def _get_simple_report_template(self) -> str:
        """
        获取简单报表模板。
        """
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ title | default('简单报表') }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h1>{{ title | default('简单报表') }}</h1>
    <table>
        <thead>
            <tr>
                {% for column in columns %}
                <th>{{ column }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                {% for column in columns %}
                <td>{{ row[column] }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>"""
