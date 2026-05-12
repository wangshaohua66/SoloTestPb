"""
Excel报表输出模块。

提供将数据导出为Excel格式报表的功能。
"""

import os
from typing import Any, Dict, List, Optional

import pandas as pd


class ExcelOutput:
    """
    Excel报表输出类。

    提供将DataFrame数据写入Excel文件的功能，支持自定义工作表和样式。
    """

    def __init__(self):
        """
        初始化Excel输出模块。
        """
        self.default_sheet_name = "Sheet1"

    def export(
        self,
        df: pd.DataFrame,
        output_path: str,
        sheet_name: Optional[str] = None,
        include_index: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        将DataFrame导出为Excel文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出文件路径。
            sheet_name: 工作表名称，默认为'Sheet1'。
            include_index: 是否包含索引列，默认为False。
            **kwargs: 传递给pandas.to_excel的额外参数。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            if sheet_name is None:
                sheet_name = self.default_sheet_name

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=include_index,
                    **kwargs,
                )

            return output_path
        except Exception as e:
            raise ValueError(f"导出Excel失败: {str(e)}")

    def export_multiple_sheets(
        self,
        data_dict: Dict[str, pd.DataFrame],
        output_path: str,
        include_index: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        将多个DataFrame导出到同一个Excel文件的不同工作表。

        Args:
            data_dict: 字典，key为工作表名称，value为DataFrame数据。
            output_path: 输出文件路径。
            include_index: 是否包含索引列，默认为False。
            **kwargs: 传递给pandas.to_excel的额外参数。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(
                        writer,
                        sheet_name=sheet_name,
                        index=include_index,
                        **kwargs,
                    )

            return output_path
        except Exception as e:
            raise ValueError(f"导出多工作表Excel失败: {str(e)}")

    def export_with_formatting(
        self,
        df: pd.DataFrame,
        output_path: str,
        sheet_name: Optional[str] = None,
        format_config: Optional[Dict[str, Any]] = None,
        include_index: bool = False,
    ) -> str:
        """
        将DataFrame导出为带格式的Excel文件。

        Args:
            df: 要导出的DataFrame数据。
            output_path: 输出文件路径。
            sheet_name: 工作表名称，默认为'Sheet1'。
            format_config: 格式配置字典，支持以下选项：
                - header_color: 表头背景色
                - header_font_color: 表头字体颜色
                - header_font_bold: 表头是否加粗
                - freeze_panes: 冻结窗格位置
                - column_widths: 列宽设置字典
            include_index: 是否包含索引列，默认为False。

        Returns:
            导出的文件路径。

        Raises:
            ValueError: 导出失败时抛出。
        """
        try:
            from openpyxl.styles import Alignment, Font, PatternFill

            if sheet_name is None:
                sheet_name = self.default_sheet_name

            if format_config is None:
                format_config = {}

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=include_index)

                worksheet = writer.sheets[sheet_name]

                header_fill = PatternFill(
                    start_color=format_config.get("header_color", "4472C4"),
                    end_color=format_config.get("header_color", "4472C4"),
                    fill_type="solid",
                )
                header_font = Font(
                    bold=format_config.get("header_font_bold", True),
                    color=format_config.get("header_font_color", "FFFFFF"),
                )

                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")

                column_widths = format_config.get("column_widths", {})
                for col_name, width in column_widths.items():
                    col_letter = chr(65 + list(df.columns).index(col_name))
                    worksheet.column_dimensions[col_letter].width = width

                freeze_panes = format_config.get("freeze_panes", "A2")
                if freeze_panes:
                    worksheet.freeze_panes = freeze_panes

            return output_path
        except ImportError:
            raise ValueError("需要安装openpyxl库以支持格式导出")
        except Exception as e:
            raise ValueError(f"导出带格式Excel失败: {str(e)}")
