"""
报告生成模块测试
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from src.reporter import Reporter
from src.http_checker import CheckResult


class TestReporter:
    """
    Reporter类测试
    """

    @pytest.fixture
    def temp_output_dir(self):
        """创建临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def reporter(self, temp_output_dir):
        """创建报告生成器"""
        return Reporter(output_dir=temp_output_dir, history_days=7)

    def test_reporter_init(self, reporter, temp_output_dir):
        """测试报告生成器初始化"""
        assert reporter.history_days == 7
        assert reporter.output_dir == temp_output_dir
        assert os.path.exists(temp_output_dir)

    def test_add_result(self, reporter):
        """测试添加检测结果"""
        result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            status_code=200,
            response_time=100.5,
            error_message=None,
            timestamp=datetime.now()
        )

        reporter.add_result(result)

        assert '测试站点' in reporter.history_data
        assert len(reporter.history_data['测试站点']) == 1

    def test_add_result_multiple_sites(self, reporter):
        """测试添加多个站点结果"""
        result1 = CheckResult(
            site_name='站点1',
            url='https://example1.com',
            success=True,
            status_code=200,
            response_time=100,
            error_message=None,
            timestamp=datetime.now()
        )

        result2 = CheckResult(
            site_name='站点2',
            url='https://example2.com',
            success=True,
            status_code=200,
            response_time=150,
            error_message=None,
            timestamp=datetime.now()
        )

        reporter.add_result(result1)
        reporter.add_result(result2)

        assert len(reporter.history_data) == 2

    def test_calculate_summary(self, reporter):
        """测试计算统计摘要"""
        for i in range(10):
            result = CheckResult(
                site_name='测试站点',
                url='https://example.com',
                success=i % 2 == 0,
                status_code=200 if i % 2 == 0 else 500,
                response_time=100 + i,
                error_message=None if i % 2 == 0 else 'Error',
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            reporter.add_result(result)

        summary = reporter._calculate_summary()

        assert '测试站点' in summary
        assert summary['测试站点']['total_checks'] == 10
        assert summary['测试站点']['successful_checks'] == 5
        assert summary['测试站点']['availability_rate'] == 50.0

    def test_generate_report(self, reporter):
        """测试生成报告"""
        for i in range(5):
            result = CheckResult(
                site_name='测试站点',
                url='https://example.com',
                success=True,
                status_code=200,
                response_time=100 + i * 10,
                error_message=None,
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            reporter.add_result(result)

        report_path = reporter.generate_report()

        assert os.path.exists(report_path)
        assert report_path.endswith('.html')

    def test_save_raw_data(self, reporter):
        """测试保存原始数据"""
        for i in range(3):
            result = CheckResult(
                site_name='测试站点',
                url='https://example.com',
                success=True,
                status_code=200,
                response_time=100,
                error_message=None,
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            reporter.add_result(result)

        reporter.generate_report()

        files = os.listdir(reporter.output_dir)
        json_files = [f for f in files if f.endswith('.json')]
        assert len(json_files) >= 1

    def test_old_data_cleanup(self, reporter):
        """测试旧数据清理"""
        old_result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            status_code=200,
            response_time=100,
            error_message=None,
            timestamp=datetime.now() - timedelta(days=10)
        )

        new_result = CheckResult(
            site_name='测试站点',
            url='https://example.com',
            success=True,
            status_code=200,
            response_time=100,
            error_message=None,
            timestamp=datetime.now()
        )

        reporter.add_result(old_result)
        reporter.add_result(new_result)

        assert len(reporter.history_data['测试站点']) == 1
