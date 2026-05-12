import pytest
import os
import tempfile
import json
from excel_merger.reporter import MergeReporter


class TestMergeReporter:
    """测试MergeReporter类"""

    @pytest.fixture
    def reporter(self):
        """创建MergeReporter实例"""
        return MergeReporter()

    @pytest.fixture
    def sample_merge_stats(self):
        """创建样例合并统计数据"""
        return {
            'strategy': 'row_merge',
            'files_processed': 3,
            'files_failed': 0,
            'original_rows': 9,
            'merged_rows': 9,
            'merged_columns': ['id', 'name', 'age'],
            'duplicates_removed': 0,
            'handled_missing': 0,
            'file_details': [
                {
                    'file': '/path/to/file1.csv',
                    'rows': 3,
                    'columns': ['id', 'name', 'age'],
                    'status': 'success'
                },
                {
                    'file': '/path/to/file2.csv',
                    'rows': 3,
                    'columns': ['id', 'name', 'age'],
                    'status': 'success'
                },
                {
                    'file': '/path/to/file3.csv',
                    'rows': 3,
                    'columns': ['id', 'name', 'age'],
                    'status': 'success'
                }
            ]
        }

    @pytest.fixture
    def temp_report_dir(self):
        """创建临时报告目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_generate_report_txt(self, reporter, sample_merge_stats):
        """测试生成文本格式报告"""
        report = reporter.generate_report(sample_merge_stats, format='txt')
        assert isinstance(report, str)
        assert 'Excel 数据合并报告' in report
        assert 'row_merge' in report
        assert '合并后行数: 9' in report

    def test_generate_report_json(self, reporter, sample_merge_stats):
        """测试生成JSON格式报告"""
        report = reporter.generate_report(sample_merge_stats, format='json')
        assert isinstance(report, str)
        report_dict = json.loads(report)
        assert 'timestamp' in report_dict
        assert 'merge_stats' in report_dict
        assert report_dict['merge_stats']['strategy'] == 'row_merge'

    def test_generate_report_save_to_dir(self, reporter, sample_merge_stats, temp_report_dir):
        """测试生成报告并保存到目录"""
        report = reporter.generate_report(sample_merge_stats, output_dir=temp_report_dir, format='txt')
        assert isinstance(report, str)
        files = os.listdir(temp_report_dir)
        assert len(files) == 1
        assert files[0].startswith('merge_report_')
        assert files[0].endswith('.txt')

    def test_generate_report_save_json(self, reporter, sample_merge_stats, temp_report_dir):
        """测试生成JSON报告并保存"""
        report = reporter.generate_report(sample_merge_stats, output_dir=temp_report_dir, format='json')
        files = os.listdir(temp_report_dir)
        assert len(files) == 1
        assert files[0].endswith('.json')

    def test_get_all_reports(self, reporter, sample_merge_stats):
        """测试获取所有报告"""
        assert len(reporter.get_all_reports()) == 0
        reporter.generate_report(sample_merge_stats)
        assert len(reporter.get_all_reports()) == 1
        reporter.generate_report(sample_merge_stats)
        assert len(reporter.get_all_reports()) == 2

    def test_clear_reports(self, reporter, sample_merge_stats):
        """测试清空报告列表"""
        reporter.generate_report(sample_merge_stats)
        reporter.generate_report(sample_merge_stats)
        assert len(reporter.get_all_reports()) == 2
        reporter.clear_reports()
        assert len(reporter.get_all_reports()) == 0

    def test_print_summary(self, reporter, sample_merge_stats, capsys):
        """测试打印合并摘要"""
        reporter.print_summary(sample_merge_stats)
        captured = capsys.readouterr()
        assert '合并完成摘要' in captured.out
        assert 'row_merge' in captured.out
        assert '行数: 9' in captured.out

    def test_generate_report_with_join_stats(self, reporter):
        """测试生成关联合并的报告"""
        join_stats = {
            'strategy': 'join_merge',
            'join_key': 'id',
            'join_type': 'inner',
            'files_processed': 2,
            'files_failed': 0,
            'merged_rows': 3,
            'merged_columns': ['id', 'name', 'age'],
            'file_details': []
        }
        report = reporter.generate_report(join_stats, format='txt')
        assert 'join_merge' in report
        assert '关联键: id' in report
        assert '关联类型: inner' in report

    def test_generate_report_with_column_merge_stats(self, reporter):
        """测试生成按列合并的报告"""
        col_stats = {
            'strategy': 'column_merge',
            'files_processed': 2,
            'files_failed': 0,
            'merged_rows': 3,
            'merged_columns': ['id', 'name', 'age', 'score'],
            'merge_method': 'outer',
            'file_details': []
        }
        report = reporter.generate_report(col_stats, format='txt')
        assert 'column_merge' in report
        assert '列合并方式: outer' in report

    def test_generate_report_with_errors(self, reporter):
        """测试生成包含错误的报告"""
        error_stats = {
            'strategy': 'row_merge',
            'files_processed': 2,
            'files_failed': 1,
            'merged_rows': 3,
            'merged_columns': ['id', 'name'],
            'file_details': [
                {
                    'file': '/path/to/good.csv',
                    'rows': 3,
                    'columns': ['id', 'name'],
                    'status': 'success'
                },
                {
                    'file': '/path/to/bad.csv',
                    'status': 'failed',
                    'error': 'File not found'
                }
            ]
        }
        report = reporter.generate_report(error_stats, format='txt')
        assert '处理文件数: 2' in report
        assert '失败文件数: 1' in report
        assert 'bad.csv' in report
        assert 'File not found' in report
