"""
主入口模块单元测试。
"""

import json
import os
import pytest
from unittest.mock import MagicMock, patch

from reportgen.main import load_config, run_single_report, run_batch_reports


class TestMain:
    """
    主入口模块的单元测试。
    """

    def test_load_config(self, temp_dir):
        """
        测试加载配置文件。
        """
        config_data = {"test": "value"}
        config_path = os.path.join(temp_dir, "test_config.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        
        result = load_config(config_path)
        assert result == config_data

    def test_run_single_report_success(self, temp_dir, sample_dataframe):
        """
        测试运行单个报表成功。
        """
        # 创建测试数据文件
        data_file = os.path.join(temp_dir, "data.csv")
        sample_dataframe.to_csv(data_file, index=False)
        
        config = {
            "data_source": {"type": "file", "file_path": data_file, "file_type": "csv"},
            "output": {"type": "excel", "path": os.path.join(temp_dir, "output.xlsx")}
        }
        config_path = os.path.join(temp_dir, "config.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        
        result_data = {
            "success": True,
            "output_path": config["output"]["path"],
            "duration_seconds": 1.0,
            "row_count": len(sample_dataframe),
            "column_count": len(sample_dataframe.columns)
        }
        
        with patch('reportgen.main.ReportGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_report.return_value = result_data
            mock_gen_class.return_value = mock_gen
            
            # 成功情况下不应该抛出异常
            run_single_report(config_path)

    def test_run_single_report_failure(self, temp_dir):
        """
        测试运行单个报表失败。
        """
        config_path = os.path.join(temp_dir, "config.json")
        config = {"invalid": "config"}
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        
        with patch('reportgen.main.ReportGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_report.side_effect = ValueError("Test error")
            mock_gen_class.return_value = mock_gen
            
            with pytest.raises(SystemExit) as exc_info:
                run_single_report(config_path)
            
            assert exc_info.value.code == 1

    def test_run_batch_reports_success(self, temp_dir, sample_dataframe):
        """
        测试批量运行报表成功。
        """
        # 创建测试数据文件
        data_file = os.path.join(temp_dir, "data.csv")
        sample_dataframe.to_csv(data_file, index=False)
        
        config_data = {
            "configs": [
                {
                    "data_source": {"type": "file", "file_path": data_file, "file_type": "csv"},
                    "output": {"type": "excel", "path": os.path.join(temp_dir, "output1.xlsx")}
                },
                {
                    "data_source": {"type": "file", "file_path": data_file, "file_type": "csv"},
                    "output": {"type": "excel", "path": os.path.join(temp_dir, "output2.xlsx")}
                }
            ]
        }
        config_path = os.path.join(temp_dir, "batch_config.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        
        results = [
            {
                "success": True,
                "output_path": config_data["configs"][0]["output"]["path"],
                "duration_seconds": 1.0,
                "row_count": len(sample_dataframe),
                "column_count": len(sample_dataframe.columns)
            },
            {
                "success": True,
                "output_path": config_data["configs"][1]["output"]["path"],
                "duration_seconds": 2.0,
                "row_count": len(sample_dataframe),
                "column_count": len(sample_dataframe.columns)
            }
        ]
        
        with patch('reportgen.main.ReportGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_multiple_reports.return_value = results
            mock_gen_class.return_value = mock_gen
            
            # 成功情况下不应该抛出异常
            run_batch_reports(config_path)

    def test_run_batch_reports_no_configs(self, temp_dir):
        """
        测试批量运行报表时没有配置列表。
        """
        config_data = {}
        config_path = os.path.join(temp_dir, "batch_config.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        
        with pytest.raises(SystemExit) as exc_info:
            run_batch_reports(config_path)
        
        assert exc_info.value.code == 1

    def test_run_batch_reports_failure(self, temp_dir):
        """
        测试批量运行报表失败。
        """
        config_data = {"configs": [{"invalid": "config"}]}
        config_path = os.path.join(temp_dir, "batch_config.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        
        with patch('reportgen.main.ReportGenerator') as mock_gen_class:
            mock_gen = MagicMock()
            mock_gen.generate_multiple_reports.side_effect = ValueError("Test error")
            mock_gen_class.return_value = mock_gen
            
            with pytest.raises(SystemExit) as exc_info:
                run_batch_reports(config_path)
            
            assert exc_info.value.code == 1
