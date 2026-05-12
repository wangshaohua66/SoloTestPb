"""
PDF报表输出模块。

提供将数据导出为PDF格式报表的功能。
"""

import os
from typing import Any, Dict, Optional

import pandas as pd

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except ImportError:
    HTML = None
    HAS_WEASYPRINT = False


class PdfOutput:
    """
    PDF报表输出类。

    提供将数据转换为PDF文件的功能，支持从HTML转换或直接生成。
    """

    def __init__(self):
        """
        初始化PDF输出模块。
        """
        pass

    def export_from_html(
        self,
        html_path: str,
        output_path: str,
        **kwargs: Any,
    ) -> str:
        """
        将HTML文件转换为PDF文件。

        Args:
            html_path: HTML文件路径。
            output_path: 输出PDF文件路径。
            **kwargs: 额外参数。

        Returns:
            导出的PDF文件路径。

        Raises:
            ImportError: 缺少必要库时抛出。
            ValueError: 转换失败时抛出。
        """
        try:
            if HAS_WEASYPRINT and HTML is not None:
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                HTML(filename=html_path).write_pdf(output_path)
                return output_path
            else:
                raise ImportError("需要安装WeasyPrint库以支持PDF生成")
        except ImportError:
            raise ImportError("需要安装WeasyPrint库以支持PDF生成")
        except Exception as e:
            raise ValueError(f"HTML转PDF失败: {str(e)}")

    def export_from_html_string(
        self,
        html_content: str,
        output_path: str,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        将HTML字符串转换为PDF文件。

        Args:
            html_content: HTML字符串内容。
            output_path: 输出PDF文件路径。
            base_url: 基础URL，用于解析相对路径资源。
            **kwargs: 额外参数。

        Returns:
            导出的PDF文件路径。

        Raises:
            ImportError: 缺少必要库时抛出。
            ValueError: 转换失败时抛出。
        """
        try:
            if HAS_WEASYPRINT and HTML is not None:
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                HTML(string=html_content, base_url=base_url).write_pdf(output_path)
                return output_path
            else:
                raise ImportError("需要安装WeasyPrint库以支持PDF生成")
        except ImportError:
            raise ImportError("需要安装WeasyPrint库以支持PDF生成")
        except Exception as e:
            raise ValueError(f"HTML字符串转PDF失败: {str(e)}")

    def export_from_dataframe(
        self,
        df: pd.DataFrame,
        output_path: str,
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        将DataFrame直接转换为PDF文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出PDF文件路径。
            title: 报表标题，默认为'报表'。
            **kwargs: 额外参数。

        Returns:
            导出的PDF文件路径。

        Raises:
            ValueError: 转换失败时抛出。
        """
        try:
            if title is None:
                title = "报表"

            html_content = self._dataframe_to_html(df, title)
            return self.export_from_html_string(html_content, output_path, **kwargs)
        except Exception as e:
            raise ValueError(f"DataFrame转PDF失败: {str(e)}")

    def _dataframe_to_html(self, df: pd.DataFrame, title: str) -> str:
        """
        将DataFrame转换为HTML字符串。

        Args:
            df: DataFrame数据。
            title: 报表标题。

        Returns:
            HTML字符串。
        """
        columns = list(df.columns)
        rows = df.to_dict(orient="records")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            font-size: 12px;
        }}
        h1 {{
            text-align: center;
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #999;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
            font-weight: bold;
            font-size: 11px;
        }}
        td {{
            font-size: 11px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <table>
        <thead>
            <tr>
"""

        for col in columns:
            html += f"                <th>{col}</th>\n"

        html += """            </tr>
        </thead>
        <tbody>
"""

        for row in rows:
            html += "            <tr>\n"
            for col in columns:
                value = row.get(col, "")
                html += f"                <td>{value}</td>\n"
            html += "            </tr>\n"

        html += """        </tbody>
    </table>
</body>
</html>"""

        return html
