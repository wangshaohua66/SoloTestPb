import pytest
import os
from unittest.mock import Mock, patch
from core.test_runner import TestRunner


class TestTestRunner:
    """测试运行器单元测试"""

    @pytest.fixture
    def runner(self, tmp_path):
        test_cases_dir = tmp_path / 'testcases'
        reports_dir = tmp_path / 'reports'
        test_cases_dir.mkdir()
        reports_dir.mkdir()
        return TestRunner(testcases_dir=str(test_cases_dir), reports_dir=str(reports_dir))

    @pytest.fixture
    def sample_test_case(self):
        return {
            'id': 'test_001',
            'name': '示例测试用例',
            'description': '这是一个示例测试用例',
            'tags': ['smoke', 'api'],
            'module': 'user',
            'enabled': True,
            'variables': {
                'base_url': 'https://api.example.com'
            },
            'request': {
                'method': 'GET',
                'url': '${base_url}/users',
                'headers': {
                    'Accept': 'application/json'
                }
            },
            'assertions': [
                {'type': 'status_code', 'expected': 200}
            ],
            'extract': {
                'user_count': 'data.count'
            },
            'timeout': 30
        }

    def test_initialization(self, tmp_path):
        """测试初始化"""
        test_cases_dir = tmp_path / 'testcases'
        reports_dir = tmp_path / 'reports'
        test_cases_dir.mkdir()
        reports_dir.mkdir()
        runner = TestRunner(testcases_dir=str(test_cases_dir), reports_dir=str(reports_dir))
        assert runner.testcases_dir == str(test_cases_dir)
        assert runner.reports_dir == str(reports_dir)
        assert runner.test_results == []

    def test_load_test_cases_from_file(self, runner, tmp_path, sample_test_case):
        """测试从文件加载测试用例"""
        import yaml
        test_file = tmp_path / 'testcases' / 'test_sample.yaml'
        with open(test_file, 'w', encoding='utf-8') as f:
            yaml.dump([sample_test_case], f)
        cases = runner.load_test_cases(str(test_file))
        assert len(cases) == 1
        assert cases[0]['id'] == 'test_001'

    def test_run_single_test_basic(self, runner, sample_test_case):
        """测试运行单个测试用例基础功能"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 150
                }
            }
            result = runner.run_single_test(sample_test_case)
            assert 'passed' in result
            assert 'request' in result

    def test_run_single_test_with_dependency_check(self, runner, sample_test_case):
        """测试运行带依赖检查的测试用例"""
        sample_test_case['depends_on'] = ['case_1']
        result = runner.run_single_test(sample_test_case)
        assert result['passed'] is False
        assert '依赖未满足' in result['error']

    def test_run_single_test_with_variables(self, runner, sample_test_case):
        """测试运行带变量的测试用例"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            result = runner.run_single_test(sample_test_case)
            assert 'request' in result

    def test_run_all_tests(self, runner, sample_test_case):
        """测试运行所有测试用例"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 150
                }
            }
            cases = [sample_test_case]
            results = runner.run_all_tests(cases)
            assert len(results) == 1

    def test_run_all_tests_disabled(self, runner, sample_test_case):
        """测试运行时跳过禁用的测试用例"""
        sample_test_case['enabled'] = False
        results = runner.run_all_tests([sample_test_case])
        assert len(results) == 0

    def test_generate_html_report(self, runner, sample_test_case):
        """测试生成HTML报告"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            result = runner.run_single_test(sample_test_case)
            runner.test_results = [result]
            reports = runner.generate_reports('test_report')
            assert 'html' in reports
            assert os.path.exists(reports['html'])

    def test_generate_json_report(self, runner, sample_test_case):
        """测试生成JSON报告"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            result = runner.run_single_test(sample_test_case)
            runner.test_results = [result]
            reports = runner.generate_reports('test_report')
            assert 'json' in reports
            assert os.path.exists(reports['json'])

    def test_generate_markdown_report(self, runner, sample_test_case):
        """测试生成Markdown报告"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            result = runner.run_single_test(sample_test_case)
            runner.test_results = [result]
            reports = runner.generate_reports('test_report')
            assert 'markdown' in reports
            assert os.path.exists(reports['markdown'])

    def test_generate_reports_default_name(self, runner, sample_test_case):
        """测试不指定报告名称生成报告"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            result = runner.run_single_test(sample_test_case)
            runner.test_results = [result]
            reports = runner.generate_reports()
            assert len(reports) == 3

    def test_run_with_pytest(self, runner):
        """测试使用pytest运行"""
        with patch('core.test_runner.pytest.main') as mock_main:
            mock_main.return_value = 0
            exit_code = runner.run_with_pytest([])
            assert exit_code == 0

    def test_run_with_pytest_parallel(self, runner):
        """测试并发执行pytest"""
        with patch('core.test_runner.pytest.main') as mock_main:
            mock_main.return_value = 0
            exit_code = runner.run_with_pytest([], parallel=2)
            assert exit_code == 0

    def test_http_request_failure_handling(self, runner, sample_test_case):
        """测试HTTP请求失败处理"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': False,
                'error': {
                    'message': 'Connection error',
                    'response_time_ms': 5000
                }
            }
            result = runner.run_single_test(sample_test_case)
            assert result['passed'] is False
            assert 'error' in result
            assert result['error'] == 'Connection error'

    def test_exception_handling(self, runner, sample_test_case):
        """测试异常处理"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.side_effect = Exception('Unexpected error')
            result = runner.run_single_test(sample_test_case)
            assert result['passed'] is False
            assert 'Unexpected error' in result['error']

    def test_test_results_stored(self, runner, sample_test_case):
        """测试测试结果被存储"""
        with patch.object(runner.http_client, 'request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'response': {
                    'status_code': 200,
                    'body': {},
                    'response_time_ms': 100
                }
            }
            runner.run_all_tests([sample_test_case])
            assert len(runner.test_results) == 1
