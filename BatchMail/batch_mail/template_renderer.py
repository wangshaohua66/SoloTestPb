"""
模板渲染模块
使用Jinja2渲染邮件模板，支持变量替换
"""

import os
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    """
    模板渲染器类
    负责加载和渲染邮件模板
    """

    def __init__(
        self,
        template_dir: Optional[str] = None,
        autoescape: bool = True,
    ) -> None:
        """
        初始化模板渲染器

        Args:
            template_dir: 模板目录路径，如果为None则使用当前目录
            autoescape: 是否自动转义HTML
        """
        if template_dir is None:
            template_dir = os.getcwd()

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "htm"]) if autoescape else False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_from_file(
        self,
        template_file: str,
        context: Dict[str, Any],
    ) -> str:
        """
        从模板文件渲染内容

        Args:
            template_file: 模板文件名
            context: 渲染上下文变量

        Returns:
            str: 渲染后的内容

        Raises:
            FileNotFoundError: 模板文件不存在时
            jinja2.exceptions.TemplateError: 模板语法错误时
        """
        template_path = os.path.join(self.template_dir, template_file)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

        template = self.env.get_template(template_file)
        return template.render(**context)

    def render_from_string(
        self,
        template_string: str,
        context: Dict[str, Any],
    ) -> str:
        """
        从字符串模板渲染内容

        Args:
            template_string: 模板字符串
            context: 渲染上下文变量

        Returns:
            str: 渲染后的内容

        Raises:
            jinja2.exceptions.TemplateError: 模板语法错误时
        """
        template = self.env.from_string(template_string)
        return template.render(**context)

    def render_subject(
        self,
        subject_template: str,
        context: Dict[str, Any],
    ) -> str:
        """
        渲染邮件主题

        Args:
            subject_template: 主题模板字符串
            context: 渲染上下文变量

        Returns:
            str: 渲染后的主题
        """
        return self.render_from_string(subject_template, context)

    def render_body(
        self,
        body_template: str,
        context: Dict[str, Any],
        is_html: bool = True,
    ) -> str:
        """
        渲染邮件正文

        Args:
            body_template: 正文模板（可以是文件路径或字符串）
            context: 渲染上下文变量
            is_html: 是否为HTML格式

        Returns:
            str: 渲染后的正文
        """
        if self._is_file_path(body_template):
            return self.render_from_file(body_template, context)
        return self.render_from_string(body_template, context)

    def _is_file_path(self, template: str) -> bool:
        """
        判断模板是否为文件路径

        Args:
            template: 模板字符串

        Returns:
            bool: True如果是文件路径，False如果是内联模板
        """
        if "\n" in template:
            return False

        ext = os.path.splitext(template)[1].lower()
        if ext in [".html", ".htm", ".txt", ".jinja", ".jinja2"]:
            return os.path.exists(os.path.join(self.template_dir, template))

        return False
