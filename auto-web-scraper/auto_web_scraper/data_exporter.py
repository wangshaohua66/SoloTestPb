"""
数据导出模块
支持将采集数据导出为CSV、Excel、JSON格式
"""
from typing import List, Dict, Any, Optional
import os
import json
import csv
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class DataExporter:
    """
    数据导出器
    支持多种格式的数据导出
    """

    SUPPORTED_FORMATS = ["csv", "excel", "json"]

    def __init__(
        self,
        output_dir: str = "./output",
        filename_prefix: str = "scraped_data",
        encoding: str = "utf-8",
    ):
        """
        初始化数据导出器

        Args:
            output_dir: 输出目录
            filename_prefix: 文件名前缀
            encoding: 文件编码
        """
        self.output_dir = output_dir
        self.filename_prefix = filename_prefix
        self.encoding = encoding
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """
        确保输出目录存在
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def _generate_filename(self, ext: str) -> str:
        """
        生成输出文件名

        Args:
            ext: 文件扩展名

        Returns:
            完整文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.filename_prefix}_{timestamp}.{ext}"
        return os.path.join(self.output_dir, filename)

    def export_to_json(
        self,
        data: List[Dict[str, Any]],
        file_path: Optional[str] = None,
        indent: int = 2,
    ) -> str:
        """
        导出数据为JSON格式

        Args:
            data: 数据列表
            file_path: 可选的文件路径
            indent: 缩进空格数

        Returns:
            输出文件路径
        """
        if file_path is None:
            file_path = self._generate_filename("json")

        with open(file_path, "w", encoding=self.encoding) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=indent,
                default=str,
            )

        print(f"数据已导出到: {file_path}")
        return file_path

    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        file_path: Optional[str] = None,
        delimiter: str = ",",
    ) -> str:
        """
        导出数据为CSV格式

        Args:
            data: 数据列表
            file_path: 可选的文件路径
            delimiter: 字段分隔符

        Returns:
            输出文件路径
        """
        if file_path is None:
            file_path = self._generate_filename("csv")

        if not data:
            print("警告: 没有数据需要导出")
            return file_path

        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        fieldnames = sorted(all_keys)

        with open(
            file_path, "w", encoding=self.encoding, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter=delimiter,
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            for item in data:
                row = {}
                for key in fieldnames:
                    value = item.get(key, "")
                    if isinstance(value, (list, dict)):
                        value = json.dumps(
                            value, ensure_ascii=False, default=str
                        )
                    row[key] = value
                writer.writerow(row)

        print(f"数据已导出到: {file_path}")
        return file_path

    def export_to_excel(
        self,
        data: List[Dict[str, Any]],
        file_path: Optional[str] = None,
        sheet_name: str = "Sheet1",
    ) -> str:
        """
        导出数据为Excel格式

        Args:
            data: 数据列表
            file_path: 可选的文件路径
            sheet_name: 工作表名称

        Returns:
            输出文件路径

        Raises:
            ImportError: 如果pandas或openpyxl不可用
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "导出Excel需要pandas库。请运行: pip install pandas openpyxl"
            )

        if file_path is None:
            file_path = self._generate_filename("xlsx")

        if not data:
            print("警告: 没有数据需要导出")
            return file_path

        df = pd.DataFrame(data)

        with pd.ExcelWriter(
            file_path, engine="openpyxl"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"数据已导出到: {file_path}")
        return file_path

    def export(
        self,
        data: List[Dict[str, Any]],
        formats: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        导出数据为指定格式

        Args:
            data: 数据列表
            formats: 格式列表，如['json', 'csv', 'excel']

        Returns:
            格式到文件路径的映射字典
        """
        if formats is None:
            formats = ["json"]

        result = {}
        for fmt in formats:
            fmt_lower = fmt.lower()
            if fmt_lower == "json":
                result["json"] = self.export_to_json(data)
            elif fmt_lower == "csv":
                result["csv"] = self.export_to_csv(data)
            elif fmt_lower in ["excel", "xlsx"]:
                result["excel"] = self.export_to_excel(data)
            else:
                print(f"警告: 不支持的格式 '{fmt}'")

        return result

    def export_multiple_sheets(
        self,
        data_dict: Dict[str, List[Dict[str, Any]]],
        file_path: Optional[str] = None,
    ) -> str:
        """
        将多个数据集导出为单个Excel文件的多个工作表

        Args:
            data_dict: 工作表名到数据列表的映射
            file_path: 可选的文件路径

        Returns:
            输出文件路径

        Raises:
            ImportError: 如果pandas或openpyxl不可用
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "导出Excel需要pandas库。请运行: pip install pandas openpyxl"
            )

        if file_path is None:
            file_path = self._generate_filename("xlsx")

        with pd.ExcelWriter(
            file_path, engine="openpyxl"
        ) as writer:
            for sheet_name, data in data_dict.items():
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"多工作表数据已导出到: {file_path}")
        return file_path
