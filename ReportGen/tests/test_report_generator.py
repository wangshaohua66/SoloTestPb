"""
报表生成器单元测试。
"""

import os
import pytest

from reportgen.core import ReportGenerator


class TestReportGenerator:
    """
    ReportGenerator类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        generator = ReportGenerator()
        assert generator.data_reader is not None
        assert generator.data_processor is not None
        assert generator.excel_output is not None
        assert generator.html_output is not None

    def test_generate_report_from_dataframe_excel(self, sample_dataframe, temp_dir):
        """
        测试从DataFrame生成Excel报表。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xlsx")

        result = generator.generate_report_from_dataframe(
            sample_dataframe,
            "excel",
            output_path,
            title="测试报表",
        )

        assert result == output_path
        assert os.path.exists(output_path)

    def test_generate_report_from_dataframe_html(self, sample_dataframe, temp_dir):
        """
        测试从DataFrame生成HTML报表。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.html")

        result = generator.generate_report_from_dataframe(
            sample_dataframe,
            "html",
            output_path,
            title="测试报表",
        )

        assert result == output_path
        assert os.path.exists(output_path)

    def test_generate_report_from_dataframe_invalid_format(self, sample_dataframe, temp_dir):
        """
        测试不支持的输出格式。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xyz")

        with pytest.raises(ValueError, match="不支持的输出格式"):
            generator.generate_report_from_dataframe(
                sample_dataframe,
                "xyz",
                output_path,
            )

    def test_generate_report_with_csv_source(self, sample_csv_file, temp_dir):
        """
        测试使用CSV数据源生成报表。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xlsx")

        config = {
            "source": {
                "type": "csv",
                "params": {"file_path": sample_csv_file},
            },
            "output": {
                "format": "excel",
                "path": output_path,
            },
        }

        result = generator.generate_report(config)

        assert result["output_path"] == output_path
        assert result["row_count"] == 5
        assert result["column_count"] == 5
        assert os.path.exists(output_path)

    def test_generate_report_with_excel_source(self, sample_excel_file, temp_dir):
        """
        测试使用Excel数据源生成报表。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.html")

        config = {
            "source": {
                "type": "excel",
                "params": {"file_path": sample_excel_file},
            },
            "output": {
                "format": "html",
                "path": output_path,
            },
        }

        result = generator.generate_report(config)

        assert result["output_path"] == output_path
        assert os.path.exists(output_path)

    def test_generate_report_with_processing(self, sample_csv_file, temp_dir):
        """
        测试带数据处理的报表生成。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xlsx")

        config = {
            "source": {
                "type": "csv",
                "params": {"file_path": sample_csv_file},
            },
            "processing": {
                "operations": [
                    {
                        "type": "filter",
                        "params": {"conditions": {"department": "技术部"}},
                    },
                ],
            },
            "output": {
                "format": "excel",
                "path": output_path,
            },
        }

        result = generator.generate_report(config)

        assert result["row_count"] == 2
        assert os.path.exists(output_path)

    def test_generate_report_with_template_string(self, sample_csv_file, temp_dir):
        """
        测试使用自定义模板字符串生成HTML报表。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.html")

        template_string = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ title }}</title></head>
        <body><h1>{{ title }}</h1></body>
        </html>
        """

        config = {
            "source": {
                "type": "csv",
                "params": {"file_path": sample_csv_file},
            },
            "output": {
                "format": "html",
                "path": output_path,
                "title": "自定义报表",
            },
            "template": {
                "template_string": template_string,
            },
        }

        result = generator.generate_report(config)

        assert result["output_path"] == output_path
        assert os.path.exists(output_path)

    def test_generate_report_missing_source_type(self, temp_dir):
        """
        测试缺少数据源类型配置时抛出异常。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xlsx")

        config = {
            "source": {
                "params": {"file_path": "test.csv"},
            },
            "output": {
                "format": "excel",
                "path": output_path,
            },
        }

        with pytest.raises(ValueError, match="数据源配置缺少type字段"):
            generator.generate_report(config)

    def test_generate_report_missing_output_format(self, sample_csv_file, temp_dir):
        """
        测试缺少输出格式配置时抛出异常。
        """
        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "report.xlsx")

        config = {
            "source": {
                "type": "csv",
                "params": {"file_path": sample_csv_file},
            },
            "output": {
                "path": output_path,
            },
        }

        with pytest.raises(ValueError, match="输出配置缺少format字段"):
            generator.generate_report(config)

    def test_generate_multiple_reports(self, sample_csv_file, temp_dir):
        """
        测试批量生成报表。
        """
        generator = ReportGenerator()
        output_path1 = os.path.join(temp_dir, "report1.xlsx")
        output_path2 = os.path.join(temp_dir, "report2.html")

        configs = [
            {
                "source": {
                    "type": "csv",
                    "params": {"file_path": sample_csv_file},
                },
                "output": {
                    "format": "excel",
                    "path": output_path1,
                },
            },
            {
                "source": {
                    "type": "csv",
                    "params": {"file_path": sample_csv_file},
                },
                "output": {
                    "format": "html",
                    "path": output_path2,
                },
            },
        ]

        results = generator.generate_multiple_reports(configs)

        assert len(results) == 2
        assert all("error" not in r for r in results)
        assert os.path.exists(output_path1)
        assert os.path.exists(output_path2)

    def test_generate_multiple_reports_with_error(self, temp_dir):
        """
        测试批量生成报表时部分失败。
        """
        generator = ReportGenerator()
        output_path1 = os.path.join(temp_dir, "report1.xlsx")

        configs = [
            {
                "source": {
                    "type": "csv",
                    "params": {"file_path": "non_existent.csv"},
                },
                "output": {
                    "format": "excel",
                    "path": output_path1,
                },
            },
        ]

        results = generator.generate_multiple_reports(configs)

        assert len(results) == 1
        assert "error" in results[0]

    def test_generate_report_performance(self, large_dataframe, temp_dir):
        """
        测试性能：处理10万行数据不超过30秒。
        """
        import time

        generator = ReportGenerator()
        output_path = os.path.join(temp_dir, "large_report.xlsx")

        start_time = time.time()

        result = generator.generate_report_from_dataframe(
            large_dataframe,
            "excel",
            output_path,
        )

        end_time = time.time()
        duration = end_time - start_time

        assert os.path.exists(output_path)
        assert duration < 30, f"性能测试失败：处理10万行数据耗时{duration:.2f}秒，超过30秒限制"
