"""
报表生成器核心模块。

提供统一的报表生成接口，整合数据读取、处理和输出功能。
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from reportgen.data import DataProcessor, DataReader
from reportgen.output import ExcelOutput, HtmlOutput, PdfOutput
from reportgen.templates import TemplateEngine


class ReportGenerator:
    """
    报表生成器类。

    提供统一的报表生成接口，整合数据读取、处理和输出功能。
    """

    def __init__(
        self,
        template_dir: Optional[str] = None,
    ):
        """
        初始化报表生成器。

        Args:
            template_dir: 模板目录路径，默认为当前目录。
        """
        self.data_reader = DataReader()
        self.data_processor = DataProcessor()
        self.template_engine = TemplateEngine(template_dir)
        self.excel_output = ExcelOutput()
        self.html_output = HtmlOutput(template_dir)
        self.pdf_output = PdfOutput()

    def generate_report(
        self,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        根据配置生成报表。

        Args:
            config: 报表配置字典，包含以下键：
                - source: 数据源配置
                - processing: 数据处理配置（可选）
                - output: 输出配置
                - template: 模板配置（可选）

        Returns:
            包含生成结果的字典，包含output_path和其他元数据。

        Raises:
            ValueError: 配置无效或生成失败时抛出。
        """
        try:
            start_time = datetime.now()

            source_config = config.get("source", {})
            processing_config = config.get("processing", {})
            output_config = config.get("output", {})
            template_config = config.get("template", {})

            df = self._read_data(source_config)

            df = self._process_data(df, processing_config)

            result = self._generate_output(df, output_config, template_config)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result.update(
                {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                }
            )

            return result
        except Exception as e:
            raise ValueError(f"报表生成失败: {str(e)}")

    def _read_data(self, source_config: Dict[str, Any]) -> pd.DataFrame:
        """
        从数据源读取数据。

        Args:
            source_config: 数据源配置。

        Returns:
            DataFrame数据。

        Raises:
            ValueError: 数据源配置无效时抛出。
        """
        if "type" not in source_config:
            raise ValueError("数据源配置缺少type字段")

        source_type = source_config["type"]
        source_params = source_config.get("params", {})

        return self.data_reader.read_from_source(source_type, source_params)

    def _process_data(
        self,
        df: pd.DataFrame,
        processing_config: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        处理数据。

        Args:
            df: 原始DataFrame。
            processing_config: 处理配置。

        Returns:
            处理后的DataFrame。
        """
        if not processing_config:
            return df

        operations = processing_config.get("operations", [])
        if operations:
            return self.data_processor.process_data(df, operations)

        return df

    def _generate_output(
        self,
        df: pd.DataFrame,
        output_config: Dict[str, Any],
        template_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成输出文件。

        Args:
            df: 数据DataFrame。
            output_config: 输出配置。
            template_config: 模板配置。

        Returns:
            包含输出路径的字典。

        Raises:
            ValueError: 输出格式不支持时抛出。
        """
        if "format" not in output_config:
            raise ValueError("输出配置缺少format字段")

        output_format = output_config["format"].lower()
        output_path = output_config.get("path", f"report.{output_format}")
        title = output_config.get("title", "报表")

        if output_format == "excel":
            sheet_name = output_config.get("sheet_name", "Sheet1")
            formatted = output_config.get("formatted", False)

            if formatted:
                format_config = output_config.get("format_config", {})
                result_path = self.excel_output.export_with_formatting(
                    df, output_path, sheet_name, format_config
                )
            else:
                result_path = self.excel_output.export(df, output_path, sheet_name)

        elif output_format == "html":
            use_template = template_config.get("use_template", False)
            if use_template and "template_path" in template_config:
                context = template_config.get("context", {})
                context.update({"title": title})
                result_path = self.html_output.export_with_template(
                    df, output_path, template_config["template_path"], context
                )
            elif "template_string" in template_config:
                context = template_config.get("context", {})
                context.update({"title": title})
                result_path = self.html_output.export_with_template_string(
                    df, output_path, template_config["template_string"], context
                )
            else:
                result_path = self.html_output.export(df, output_path, title)

        elif output_format == "pdf":
            result_path = self.pdf_output.export_from_dataframe(df, output_path, title)

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        return {
            "output_path": result_path,
            "output_format": output_format,
        }

    def generate_multiple_reports(
        self,
        configs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        批量生成多个报表。

        Args:
            configs: 报表配置列表。

        Returns:
            每个报表的生成结果列表。
        """
        results = []
        for config in configs:
            try:
                result = self.generate_report(config)
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "error": str(e),
                        "config": config,
                    }
                )
        return results

    def generate_report_from_dataframe(
        self,
        df: pd.DataFrame,
        output_format: str,
        output_path: str,
        title: str = "报表",
        template_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        从DataFrame直接生成报表。

        Args:
            df: 数据DataFrame。
            output_format: 输出格式（excel、html、pdf）。
            output_path: 输出文件路径。
            title: 报表标题。
            template_config: 模板配置（仅用于HTML格式）。

        Returns:
            输出文件路径。

        Raises:
            ValueError: 输出格式不支持时抛出。
        """
        output_format = output_format.lower()

        if output_format == "excel":
            return self.excel_output.export(df, output_path)
        elif output_format == "html":
            if template_config and "template_string" in template_config:
                context = template_config.get("context", {})
                return self.html_output.export_with_template_string(
                    df, output_path, template_config["template_string"], context
                )
            return self.html_output.export(df, output_path, title)
        elif output_format == "pdf":
            return self.pdf_output.export_from_dataframe(df, output_path, title)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
