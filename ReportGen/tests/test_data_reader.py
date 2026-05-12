"""
数据读取模块单元测试。
"""

import os
import pytest
import pandas as pd

from reportgen.data import DataReader


class TestDataReader:
    """
    DataReader类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        reader = DataReader()
        assert "csv" in reader.supported_file_formats
        assert "excel" in reader.supported_file_formats
        assert "json" in reader.supported_file_formats
        assert "mysql" in reader.supported_databases
        assert "sqlite" in reader.supported_databases

    def test_read_csv(self, sample_csv_file):
        """
        测试读取CSV文件。
        """
        reader = DataReader()
        df = reader.read_csv(sample_csv_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ["id", "name", "age", "salary", "department"]

    def test_read_csv_file_not_found(self):
        """
        测试CSV文件不存在时抛出异常。
        """
        reader = DataReader()

        with pytest.raises(FileNotFoundError):
            reader.read_csv("non_existent_file.csv")

    def test_read_excel(self, sample_excel_file):
        """
        测试读取Excel文件。
        """
        reader = DataReader()
        df = reader.read_excel(sample_excel_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_read_excel_file_not_found(self):
        """
        测试Excel文件不存在时抛出异常。
        """
        reader = DataReader()

        with pytest.raises(FileNotFoundError):
            reader.read_excel("non_existent_file.xlsx")

    def test_read_json(self, sample_json_file):
        """
        测试读取JSON文件。
        """
        reader = DataReader()
        df = reader.read_json(sample_json_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_read_json_file_not_found(self):
        """
        测试JSON文件不存在时抛出异常。
        """
        reader = DataReader()

        with pytest.raises(FileNotFoundError):
            reader.read_json("non_existent_file.json")

    def test_read_sqlite(self, sample_sqlite_file):
        """
        测试读取SQLite数据库。
        """
        reader = DataReader()
        df = reader.read_sqlite(sample_sqlite_file, "SELECT * FROM employees")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_read_sqlite_error(self, temp_dir):
        """
        测试SQLite查询错误时抛出异常。
        """
        reader = DataReader()
        invalid_db = os.path.join(temp_dir, "invalid.db")

        with pytest.raises(ValueError):
            reader.read_sqlite(invalid_db, "SELECT * FROM non_existent_table")

    def test_read_from_source_csv(self, sample_csv_file):
        """
        测试通过统一接口读取CSV。
        """
        reader = DataReader()
        df = reader.read_from_source(
            "csv",
            {"file_path": sample_csv_file},
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_read_from_source_excel(self, sample_excel_file):
        """
        测试通过统一接口读取Excel。
        """
        reader = DataReader()
        df = reader.read_from_source(
            "excel",
            {"file_path": sample_excel_file},
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_read_from_source_invalid_type(self):
        """
        测试不支持的数据源类型。
        """
        reader = DataReader()

        with pytest.raises(ValueError, match="不支持的数据源类型"):
            reader.read_from_source("invalid_type", {})
