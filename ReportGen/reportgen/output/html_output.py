"""
HTML报表输出模块。

提供将数据导出为HTML格式报表的功能。
"""

import os
from typing import Any, Dict, Optional

import pandas as pd

from reportgen.templates import TemplateEngine


class HtmlOutput:
    """
    HTML报表输出类。

    提供将DataFrame数据写入HTML文件的功能，支持Jinja2模板。
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化HTML输出模块。

        Args:
            template_dir: 模板目录路径，默认为当前目录。
        """
        self.template_engine = TemplateEngine(template_dir)

    def export(
        self,
        df: pd.DataFrame,
        output_path: str,
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        将DataFrame导出为HTML文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出文件路径。
            title: 报表标题，默认为'报表'。
            **kwargs: 额外参数。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            if title is None:
                title = "报表"

            columns = list(df.columns)
            data = df.to_dict(orient="records")

            context = {
                "title": title,
                "columns": columns,
                "data": data,
            }

            template_string = self.template_engine.get_default_template("simple")
            html_content = self.template_engine.render_string(template_string, context)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return output_path
        except Exception as e:
            raise ValueError(f"导出HTML失败: {str(e)}")

    def export_with_template(
        self,
        df: pd.DataFrame,
        output_path: str,
        template_path: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        使用Jinja2模板导出HTML文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出文件路径。
            template_path: 模板文件路径。
            context: 额外的模板上下文数据。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            if context is None:
                context = {}

            columns = list(df.columns)
            data = df.to_dict(orient="records")

            context.update(
                {
                    "columns": columns,
                    "data": data,
                    "df": df,
                }
            )

            html_content = self.template_engine.render_template(template_path, context)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return output_path
        except Exception as e:
            raise ValueError(f"使用模板导出HTML失败: {str(e)}")

    def export_with_template_string(
        self,
        df: pd.DataFrame,
        output_path: str,
        template_string: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        使用模板字符串导出HTML文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出文件路径。
            template_string: 模板字符串。
            context: 额外的模板上下文数据。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            if context is None:
                context = {}

            columns = list(df.columns)
            data = df.to_dict(orient="records")

            context.update(
                {
                    "columns": columns,
                    "data": data,
                    "df": df,
                }
            )

            html_content = self.template_engine.render_string(template_string, context)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return output_path
        except Exception as e:
            raise ValueError(f"使用模板字符串导出HTML失败: {str(e)}")
