"""
数据导出模块单元测试
"""
import pytest
import os
import json
import csv
import tempfile
import shutil

from auto_web_scraper.data_exporter import DataExporter


class TestDataExporter:
    """
    数据导出器测试类
    """

    def setup_method(self):
        """
        每个测试方法前的准备
        """
        self.test_data = [
            {"name": "测试1", "value": 100, "tags": ["a", "b"]},
            {"name": "测试2", "value": 200, "tags": ["c"]},
            {"name": "测试3", "value": 300, "tags": ["d", "e", "f"]},
        ]
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = DataExporter(
            output_dir=self.temp_dir,
            filename_prefix="test",
            encoding="utf-8",
        )

    def teardown_method(self):
        """
        每个测试方法后的清理
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_export_to_json(self):
        """
        测试导出JSON
        """
        file_path = os.path.join(self.temp_dir, "output.json")
        result = self.exporter.export_to_json(self.test_data, file_path=file_path)

        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            assert len(loaded) == 3
            assert loaded[0]["name"] == "测试1"

    def test_export_to_csv(self):
        """
        测试导出CSV
        """
        file_path = os.path.join(self.temp_dir, "output.csv")
        result = self.exporter.export_to_csv(self.test_data, file_path=file_path)

        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]["name"] == "测试1"

    def test_export_to_excel(self):
        """
        测试导出Excel
        """
        pytest.importorskip("pandas")
        pytest.importorskip("openpyxl")

        file_path = os.path.join(self.temp_dir, "output.xlsx")
        result = self.exporter.export_to_excel(self.test_data, file_path=file_path)

        assert os.path.exists(result)

    def test_export_multiple_formats(self):
        """
        测试同时导出多种格式
        """
        results = self.exporter.export(self.test_data, formats=["json", "csv"])

        assert "json" in results
        assert "csv" in results
        assert os.path.exists(results["json"])
        assert os.path.exists(results["csv"])

    def test_export_empty_data(self):
        """
        测试导出空数据
        """
        file_path = os.path.join(self.temp_dir, "empty.json")
        result = self.exporter.export_to_json([], file_path=file_path)

        assert os.path.exists(result)

        with open(result, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            assert loaded == []

    def test_supported_formats(self):
        """
        测试支持的格式列表
        """
        assert "csv" in DataExporter.SUPPORTED_FORMATS
        assert "excel" in DataExporter.SUPPORTED_FORMATS
        assert "json" in DataExporter.SUPPORTED_FORMATS

    def test_output_dir_creation(self):
        """
        测试输出目录创建
        """
        new_dir = os.path.join(self.temp_dir, "nested", "output")
        exporter = DataExporter(output_dir=new_dir)

        assert os.path.exists(new_dir)

    def test_generate_filename(self):
        """
        测试生成文件名
        """
        filename = self.exporter._generate_filename("json")

        assert filename.startswith(self.temp_dir)
        assert "test_" in filename
        assert filename.endswith(".json")

    def test_export_unknown_format(self):
        """
        测试未知格式
        """
        results = self.exporter.export(self.test_data, formats=["json", "unknown"])

        assert "json" in results
        assert "unknown" not in results
