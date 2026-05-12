# -*- coding: utf-8 -*-
"""
报告生成模块单元测试
"""

import os
import pytest
import allure
from unittest.mock import patch, MagicMock
from monitor.reporter.report_generator import ReportGenerator


@allure.feature("报告生成模块")
class TestReportGenerator:
    """报告生成类测试"""

    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = MagicMock()
        config.get.return_value = "./test_reports"
        return config

    @pytest.fixture
    def report_generator(self, mock_config):
        """创建报告生成器实例"""
        return ReportGenerator(mock_config)

    @pytest.fixture
    def mock_data_store(self):
        """创建模拟数据存储"""
        import time

        cpu_data = [
            {
                "timestamp": time.time(),
                "overall": 50.0,
                "per_cpu": [40.0, 50.0, 60.0],
                "avg": 50.0,
                "max": 60.0,
                "min": 40.0
            }
        ]

        memory_data = [
            {
                "timestamp": time.time(),
                "virtual": {
                    "total": 8 * 1024 ** 3,
                    "available": 4 * 1024 ** 3,
                    "used": 4 * 1024 ** 3,
                    "free": 4 * 1024 ** 3,
                    "percent": 50.0,
                    "used_gb": 4.0,
                    "total_gb": 8.0,
                    "available_gb": 4.0
                },
                "swap": {
                    "total": 2 * 1024 ** 3,
                    "used": 1 * 1024 ** 3,
                    "free": 1 * 1024 ** 3,
                    "percent": 50.0,
                    "used_gb": 1.0,
                    "total_gb": 2.0
                }
            }
        ]

        disk_data = [
            {
                "timestamp": time.time(),
                "usage": {
                    "/dev/sda1": {
                        "mountpoint": "/",
                        "fstype": "ext4",
                        "total": 100 * 1024 ** 3,
                        "used": 50 * 1024 ** 3,
                        "free": 50 * 1024 ** 3,
                        "percent": 50.0,
                        "used_gb": 50.0,
                        "total_gb": 100.0,
                        "free_gb": 50.0
                    }
                },
                "io": {},
                "max_percent": 50.0
            }
        ]

        network_data = [
            {
                "timestamp": time.time(),
                "io": {
                    "interfaces": {
                        "eth0": {
                            "upload_speed": 100 * 1024,
                            "download_speed": 200 * 1024,
                            "upload_speed_mb": 0.1,
                            "download_speed_mb": 0.2,
                            "total_upload": 1000 * 1024 ** 2,
                            "total_download": 2000 * 1024 ** 2
                        }
                    },
                    "total_upload_speed": 100 * 1024,
                    "total_download_speed": 200 * 1024,
                    "total_upload_speed_mb": 0.1,
                    "total_download_speed_mb": 0.2
                }
            }
        ]

        data_store = MagicMock()
        data_store.get_cpu_data.return_value = cpu_data
        data_store.get_memory_data.return_value = memory_data
        data_store.get_disk_data.return_value = disk_data
        data_store.get_network_data.return_value = network_data

        return data_store

    @allure.story("生成报告测试")
    @allure.title("测试生成完整报告")
    def test_generate_report(self, report_generator, mock_data_store, tmp_path):
        """测试生成完整报告"""
        with patch('os.makedirs') as mock_makedirs, \
             patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('builtins.open', create=True) as mock_open:

            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            report_path = report_generator.generate_report(mock_data_store)

            assert report_path is not None
            mock_makedirs.assert_called()

    @allure.story("生成报告测试")
    @allure.title("测试空数据报告生成")
    def test_generate_report_empty_data(self, report_generator):
        """测试空数据报告生成"""
        empty_data_store = MagicMock()
        empty_data_store.get_cpu_data.return_value = []
        empty_data_store.get_memory_data.return_value = []
        empty_data_store.get_disk_data.return_value = []
        empty_data_store.get_network_data.return_value = []

        with patch('os.makedirs') as mock_makedirs, \
             patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('builtins.open', create=True) as mock_open:

            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            report_path = report_generator.generate_report(empty_data_store)

            assert report_path is not None

    @allure.story("摘要行生成测试")
    @allure.title("测试生成数据摘要行")
    def test_generate_summary_row(self, report_generator):
        """测试生成数据摘要行"""
        data = [
            {"overall": 50.0},
            {"overall": 60.0},
            {"overall": 70.0}
        ]

        result = report_generator._generate_summary_row("CPU", data, "overall")

        assert "CPU" in result
        assert "3" in result

    @allure.story("摘要行生成测试")
    @allure.title("测试空数据摘要行生成")
    def test_generate_summary_row_empty(self, report_generator):
        """测试空数据摘要行生成"""
        result = report_generator._generate_summary_row("CPU", [], "overall")

        assert "CPU" in result
        assert "0" in result

    @allure.story("磁盘摘要测试")
    @allure.title("测试生成磁盘摘要行")
    def test_generate_disk_summary_row(self, report_generator):
        """测试生成磁盘摘要行"""
        data = [
            {"max_percent": 50.0},
            {"max_percent": 60.0},
            {"max_percent": 70.0}
        ]

        result = report_generator._generate_disk_summary_row(data)

        assert "3" in result

    @allure.story("网络摘要测试")
    @allure.title("测试生成网络摘要行")
    def test_generate_network_summary_row(self, report_generator):
        """测试生成网络摘要行"""
        data = [
            {
                "io": {
                    "total_upload_speed_mb": 0.1,
                    "total_download_speed_mb": 0.2
                }
            }
        ]

        result = report_generator._generate_network_summary_row(data)

        assert "1" in result

    @allure.story("图表生成测试")
    @allure.title("测试生成CPU趋势图")
    def test_generate_cpu_chart(self, report_generator):
        """测试生成CPU趋势图"""
        cpu_data = [
            {"timestamp": 1000000, "overall": 50.0},
            {"timestamp": 1000001, "overall": 60.0}
        ]

        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close') as mock_close:
            report_generator._generate_cpu_chart(cpu_data, "./test_dir")

            mock_savefig.assert_called_once()

    @allure.story("图表生成测试")
    @allure.title("测试生成内存趋势图")
    def test_generate_memory_chart(self, report_generator):
        """测试生成内存趋势图"""
        memory_data = [
            {
                "timestamp": 1000000,
                "virtual": {"percent": 50.0},
                "swap": {"percent": 30.0}
            }
        ]

        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close') as mock_close:
            report_generator._generate_memory_chart(memory_data, "./test_dir")

            mock_savefig.assert_called_once()

    @allure.story("图表生成测试")
    @allure.title("测试生成磁盘趋势图")
    def test_generate_disk_chart(self, report_generator):
        """测试生成磁盘趋势图"""
        disk_data = [
            {"timestamp": 1000000, "max_percent": 50.0}
        ]

        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close') as mock_close:
            report_generator._generate_disk_chart(disk_data, "./test_dir")

            mock_savefig.assert_called_once()

    @allure.story("图表生成测试")
    @allure.title("测试生成网络趋势图")
    def test_generate_network_chart(self, report_generator):
        """测试生成网络趋势图"""
        network_data = [
            {
                "timestamp": 1000000,
                "io": {
                    "total_upload_speed_mb": 0.1,
                    "total_download_speed_mb": 0.2
                }
            }
        ]

        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close') as mock_close:
            report_generator._generate_network_chart(network_data, "./test_dir")

            mock_savefig.assert_called_once()

    @allure.story("HTML报告测试")
    @allure.title("测试生成HTML报告")
    def test_generate_html_report(self, report_generator):
        """测试生成HTML报告"""
        cpu_data = [{"timestamp": 1000000, "overall": 50.0}]
        memory_data = [{
            "timestamp": 1000000,
            "virtual": {"percent": 50.0},
            "swap": {"percent": 30.0}
        }]
        disk_data = [{"timestamp": 1000000, "max_percent": 50.0}]
        network_data = [{
            "timestamp": 1000000,
            "io": {
                "total_upload_speed_mb": 0.1,
                "total_download_speed_mb": 0.2
            }
        }]

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            result = report_generator._generate_html_report(
                cpu_data, memory_data, disk_data, network_data, "./test_dir"
            )

            assert result is not None
            mock_file.write.assert_called_once()
