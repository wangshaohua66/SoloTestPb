import pytest
import pandas as pd
import os
import tempfile
from excel_merger.reader import ExcelReader


class TestExcelReader:
    """测试ExcelReader类"""

    @pytest.fixture
    def reader(self):
        """创建ExcelReader实例"""
        return ExcelReader()

    @pytest.fixture
    def temp_csv_file(self):
        """创建临时CSV文件"""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            df.to_csv(f.name, index=False)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def temp_excel_file(self):
        """创建临时Excel文件"""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        df.to_excel(temp_path, index=False, engine='openpyxl')
        yield temp_path
        os.unlink(temp_path)

    def test_read_csv_file(self, reader, temp_csv_file):
        """测试读取CSV文件"""
        df = reader.read_file(temp_csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['id', 'name', 'age']

    def test_read_excel_file(self, reader, temp_excel_file):
        """测试读取Excel文件"""
        df = reader.read_file(temp_excel_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['id', 'name', 'age']

    def test_file_not_found(self, reader):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            reader.read_file('nonexistent_file.csv')

    def test_unsupported_format(self, reader):
        """测试不支持的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        try:
            with pytest.raises(ValueError):
                reader.read_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_get_file_info(self, reader, temp_csv_file):
        """测试获取文件信息"""
        info = reader.get_file_info(temp_csv_file)
        assert 'rows' in info
        assert 'columns' in info
        assert info['rows'] == 3

    def test_get_files_from_directory(self, reader, temp_csv_file):
        """测试从目录获取文件"""
        dir_path = os.path.dirname(temp_csv_file)
        files = reader.get_files_from_directory(dir_path)
        assert len(files) > 0
        assert temp_csv_file in files

    def test_get_sheet_names(self, reader, temp_excel_file):
        """测试获取工作表名称"""
        sheets = reader.get_sheet_names(temp_excel_file)
        assert isinstance(sheets, list)
        assert len(sheets) > 0

    def test_read_multiple_files(self, reader, temp_csv_file, temp_excel_file):
        """测试批量读取多个文件"""
        results = reader.read_multiple_files([temp_csv_file, temp_excel_file])
        assert len(results) == 2
        assert all(isinstance(df, pd.DataFrame) for df in results.values())

    def test_supported_extensions(self, reader):
        """测试支持的扩展名"""
        assert '.xlsx' in reader.SUPPORTED_EXTENSIONS
        assert '.xls' in reader.SUPPORTED_EXTENSIONS
        assert '.csv' in reader.SUPPORTED_EXTENSIONS
