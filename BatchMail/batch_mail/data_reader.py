"""
收件人数据读取模块
支持从CSV和Excel文件读取收件人列表
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class Recipient:
    """
    收件人数据类
    封装单个收件人的所有信息
    """

    email: str
    name: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        初始化后校验邮箱格式
        """
        if not self.email or "@" not in self.email:
            raise ValueError(f"无效的邮箱地址: {self.email}")


class DataReader:
    """
    数据读取器类
    负责从CSV或Excel文件读取收件人数据
    """

    REQUIRED_COLUMNS = ["email"]

    def __init__(self, file_path: str) -> None:
        """
        初始化数据读取器

        Args:
            file_path: 数据文件路径（CSV或Excel）

        Raises:
            FileNotFoundError: 文件不存在时
            ValueError: 文件格式不支持时
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        self.file_path = file_path
        self.file_ext = os.path.splitext(file_path)[1].lower()

        if self.file_ext not in [".csv", ".xlsx", ".xls"]:
            raise ValueError(f"不支持的文件格式: {self.file_ext}，仅支持CSV和Excel")

    def read(self) -> List[Recipient]:
        """
        读取文件并转换为收件人列表

        Returns:
            List[Recipient]: 收件人对象列表

        Raises:
            ValueError: 数据格式错误时
        """
        if self.file_ext == ".csv":
            df = self._read_csv()
        else:
            df = self._read_excel()

        return self._convert_to_recipients(df)

    def _read_csv(self) -> pd.DataFrame:
        """
        读取CSV文件

        Returns:
            pd.DataFrame: DataFrame数据
        """
        return pd.read_csv(self.file_path)

    def _read_excel(self) -> pd.DataFrame:
        """
        读取Excel文件

        Returns:
            pd.DataFrame: DataFrame数据
        """
        return pd.read_excel(self.file_path)

    def _convert_to_recipients(self, df: pd.DataFrame) -> List[Recipient]:
        """
        将DataFrame转换为Recipient对象列表

        Args:
            df: 原始数据DataFrame

        Returns:
            List[Recipient]: 收件人对象列表

        Raises:
            ValueError: 缺少必要列时
        """
        self._validate_columns(df)

        recipients = []
        for _, row in df.iterrows():
            recipient = self._row_to_recipient(row)
            recipients.append(recipient)

        return recipients

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        验证DataFrame是否包含必要的列
        列名不区分大小写

        Args:
            df: 要验证的DataFrame

        Raises:
            ValueError: 缺少必要列时
        """
        df_columns_lower = {col.lower() for col in df.columns}
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS
            if col.lower() not in df_columns_lower
        ]
        if missing_columns:
            raise ValueError(f"缺少必要的列: {', '.join(missing_columns)}")

    def _row_to_recipient(self, row: pd.Series) -> Recipient:
        """
        将一行数据转换为Recipient对象

        Args:
            row: DataFrame的一行数据

        Returns:
            Recipient: 收件人对象

        Raises:
            ValueError: 邮箱无效时
        """
        variables = {}
        name = None
        attachments = []
        email = None

        for column, value in row.items():
            column_lower = column.lower()
            if pd.isna(value):
                continue

            if column_lower == "email":
                email = str(value).strip()
            elif column_lower == "name":
                name = str(value).strip()
            elif column_lower == "attachment":
                atts = str(value).strip()
                if atts:
                    attachments = [a.strip() for a in atts.split(";") if a.strip()]
            else:
                variables[column] = value

        if email is None:
            raise ValueError("缺少必要的邮箱字段")

        return Recipient(
            email=email,
            name=name,
            variables=variables,
            attachments=attachments,
        )
