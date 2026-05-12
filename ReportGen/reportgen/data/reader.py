"""
数据读取模块。

支持从CSV、Excel、JSON文件以及MySQL、SQLite数据库读取数据。
"""

import json
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy import create_engine


class DataReader:
    """
    数据读取器类。

    提供从多种数据源读取数据并返回pandas DataFrame的功能。
    """

    def __init__(self):
        """
        初始化数据读取器。
        """
        self.supported_file_formats = ["csv", "excel", "json"]
        self.supported_databases = ["mysql", "sqlite"]

    def read_csv(
        self,
        file_path: str,
        encoding: str = "utf-8",
        sep: str = ",",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        从CSV文件读取数据。

        Args:
            file_path: CSV文件路径。
            encoding: 文件编码，默认为utf-8。
            sep: 分隔符，默认为逗号。
            **kwargs: 传递给pandas.read_csv的额外参数。

        Returns:
            包含CSV数据的pandas DataFrame。

        Raises:
            FileNotFoundError: 文件不存在时抛出。
            ValueError: 文件格式不正确时抛出。
        """
        try:
            df = pd.read_csv(file_path, encoding=encoding, sep=sep, **kwargs)
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV文件不存在: {file_path}")
        except Exception as e:
            raise ValueError(f"读取CSV文件失败: {str(e)}")

    def read_excel(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        从Excel文件读取数据。

        Args:
            file_path: Excel文件路径。
            sheet_name: 工作表名称，默认为第一个工作表。
            **kwargs: 传递给pandas.read_excel的额外参数。

        Returns:
            包含Excel数据的pandas DataFrame。

        Raises:
            FileNotFoundError: 文件不存在时抛出。
            ValueError: 文件格式不正确时抛出。
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            if isinstance(df, dict):
                first_sheet = list(df.keys())[0]
                return df[first_sheet]
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel文件不存在: {file_path}")
        except Exception as e:
            raise ValueError(f"读取Excel文件失败: {str(e)}")

    def read_json(
        self,
        file_path: str,
        encoding: str = "utf-8",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        从JSON文件读取数据。

        Args:
            file_path: JSON文件路径。
            encoding: 文件编码，默认为utf-8。
            **kwargs: 传递给pandas.read_json的额外参数。

        Returns:
            包含JSON数据的pandas DataFrame。

        Raises:
            FileNotFoundError: 文件不存在时抛出。
            ValueError: 文件格式不正确时抛出。
        """
        try:
            with open(file_path, "r", encoding=encoding) as f:
                data = json.load(f)

            if isinstance(data, list):
                df = pd.DataFrame(data, **kwargs)
            elif isinstance(data, dict) and "records" in data:
                df = pd.DataFrame(data["records"], **kwargs)
            else:
                df = pd.read_json(file_path, encoding=encoding, **kwargs)

            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON文件不存在: {file_path}")
        except Exception as e:
            raise ValueError(f"读取JSON文件失败: {str(e)}")

    def read_mysql(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        query: str,
        charset: str = "utf8mb4",
    ) -> pd.DataFrame:
        """
        从MySQL数据库读取数据。

        Args:
            host: 数据库主机地址。
            port: 数据库端口。
            user: 数据库用户名。
            password: 数据库密码。
            database: 数据库名称。
            query: SQL查询语句。
            charset: 字符集，默认为utf8mb4。

        Returns:
            包含查询结果的pandas DataFrame。

        Raises:
            ConnectionError: 数据库连接失败时抛出。
            ValueError: 查询执行失败时抛出。
        """
        try:
            connection_string = (
                f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
            )
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        except Exception as e:
            raise ConnectionError(f"连接MySQL数据库失败: {str(e)}")

    def read_sqlite(
        self,
        db_path: str,
        query: str,
    ) -> pd.DataFrame:
        """
        从SQLite数据库读取数据。

        Args:
            db_path: SQLite数据库文件路径。
            query: SQL查询语句。

        Returns:
            包含查询结果的pandas DataFrame。

        Raises:
            FileNotFoundError: 数据库文件不存在时抛出。
            ValueError: 查询执行失败时抛出。
        """
        try:
            connection_string = f"sqlite:///{db_path}"
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        except Exception as e:
            raise ValueError(f"读取SQLite数据库失败: {str(e)}")

    def read_from_source(
        self,
        source_type: str,
        source_config: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        从指定数据源读取数据。

        Args:
            source_type: 数据源类型，支持csv、excel、json、mysql、sqlite。
            source_config: 数据源配置参数字典。

        Returns:
            包含数据的pandas DataFrame。

        Raises:
            ValueError: 不支持的数据源类型时抛出。
        """
        source_type = source_type.lower()

        if source_type == "csv":
            return self.read_csv(**source_config)
        elif source_type == "excel":
            return self.read_excel(**source_config)
        elif source_type == "json":
            return self.read_json(**source_config)
        elif source_type == "mysql":
            return self.read_mysql(**source_config)
        elif source_type == "sqlite":
            return self.read_sqlite(**source_config)
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")
