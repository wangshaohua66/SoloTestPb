import os
import sys
import pytest
import allure
from typing import List, Dict, Any
from datetime import datetime

from .config_parser import ConfigParser
from .http_client import HttpClient
from .variable_engine import VariableEngine
from .assertion_engine import AssertionEngine
from .dependency_manager import DependencyManager
from .report_generator import ReportGenerator


class TestRunner:
    """API测试运行器，整合所有核心功能"""
    __test__ = False  # 防止pytest将此类收集为测试类

    def __init__(self, testcases_dir: str = 'testcases', reports_dir: str = 'reports'):
        """
        初始化测试运行器

        Args:
            testcases_dir: 测试用例目录
            reports_dir: 报告输出目录
        """
        self.testcases_dir = testcases_dir
        self.reports_dir = reports_dir

        self.config_parser = ConfigParser()
        self.http_client = HttpClient()
        self.variable_engine = VariableEngine()
        self.assertion_engine = AssertionEngine()
        self.dependency_manager = DependencyManager()
        self.report_generator = ReportGenerator(output_dir=reports_dir)

        self.test_results: List[Dict[str, Any]] = []
        self._loaded = False

    def load_test_cases(self, file_path: str = None) -> List[Dict[str, Any]]:
        """
        加载测试用例

        Args:
            file_path: 可选的测试用例文件路径，不指定则加载整个目录

        Returns:
            加载的测试用例列表
        """
        if file_path:
            test_cases = self.config_parser.parse_file(file_path)
        else:
            test_cases = self.config_parser.parse_directory(self.testcases_dir)

        ordered_cases = self.dependency_manager.get_execution_order(test_cases)
        self._loaded = True
        return ordered_cases

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个测试用例

        Args:
            test_case: 测试用例数据

        Returns:
            测试结果
        """
        case_id = test_case.get('id', 'unknown')
        case_name = test_case.get('name', case_id)
        case_description = test_case.get('description', '')
        case_tags = test_case.get('tags', [])
        case_module = test_case.get('module', 'default')

        result = {
            'id': case_id,
            'name': case_name,
            'description': case_description,
            'tags': case_tags,
            'module': case_module,
            'passed': True,
            'request': None,
            'response': None,
            'assertions': [],
            'error': '',
            'response_time': 0
        }

        try:
            deps_met, missing_deps = self.dependency_manager.check_dependencies_met(test_case)
            if not deps_met:
                result['passed'] = False
                result['error'] = f"依赖未满足: {', '.join(missing_deps)}"
                return result

            test_case = self.dependency_manager.resolve_dependencies(test_case)
            test_case = self.variable_engine.parse_test_case(test_case)

            request_config = test_case.get('request', {})
            method = request_config.get('method', 'GET')
            url = request_config.get('url', '')
            base_url = request_config.get('base_url', '')

            request_params = {
                'headers': request_config.get('headers', {}),
                'params': request_config.get('params', {}),
                'json': request_config.get('json', {}),
                'data': request_config.get('data', {}),
                'timeout': test_case.get('timeout', 30)
            }

            if base_url:
                request_params['base_url'] = base_url

            request_params = self.variable_engine.parse_value(request_params)

            result['request'] = {
                'method': method,
                'url': url,
                'base_url': base_url,
                **request_params
            }

            http_result = self.http_client.request(method, url, **request_params)

            if not http_result.get('success', False):
                result['passed'] = False
                result['error'] = http_result.get('error', {}).get('message', 'HTTP请求失败')
                result['response_time'] = http_result.get('error', {}).get('response_time_ms', 0)
                self.dependency_manager.store_case_result(case_id, result)
                return result

            response = http_result.get('response', {})
            result['response'] = response
            result['response_time'] = response.get('response_time_ms', 0)

            assertions = test_case.get('assertions', [])
            if assertions:
                all_passed, assertion_results = self.assertion_engine.assert_all(assertions, response)
                result['assertions'] = assertion_results
                if not all_passed:
                    result['passed'] = False

            extract_config = test_case.get('extract', {})
            if extract_config:
                self.dependency_manager.extract_data(response, extract_config)

            self.dependency_manager.store_case_result(case_id, result)

        except Exception as e:
            result['passed'] = False
            result['error'] = str(e)

        return result

    def run_all_tests(self, test_cases: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        运行所有测试用例

        Args:
            test_cases: 可选的测试用例列表，不指定则自动加载

        Returns:
            测试结果列表
        """
        if test_cases is None:
            if not self._loaded:
                test_cases = self.load_test_cases()
            else:
                test_cases = self.config_parser.get_all_test_cases()

        self.test_results = []
        self.dependency_manager.reset()
        self.variable_engine.clear_variables()

        for test_case in test_cases:
            if not test_case.get('enabled', True):
                continue

            result = self.run_single_test(test_case)
            self.test_results.append(result)

        return self.test_results

    def generate_reports(self, report_name: str = None) -> Dict[str, str]:
        """
        生成测试报告

        Args:
            report_name: 报告名称

        Returns:
            报告路径字典
        """
        if not report_name:
            report_name = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        html_report = self.report_generator.generate_html_report(self.test_results, report_name)
        json_report = self.report_generator.generate_json_report(self.test_results, report_name)
        md_report = self.report_generator.generate_markdown_report(self.test_results, report_name)

        return {
            'html': html_report,
            'json': json_report,
            'markdown': md_report
        }

    def run_with_pytest(self, test_cases: List[Dict[str, Any]] = None, parallel: int = 1) -> int:
        """
        使用pytest运行测试

        Args:
            test_cases: 测试用例列表
            parallel: 并发进程数

        Returns:
            pytest退出码
        """
        if test_cases is None:
            if not self._loaded:
                test_cases = self.load_test_cases()
            else:
                test_cases = self.config_parser.get_all_test_cases()

        pytest_args = [
            '-v',
            '--alluredir=allure-results',
            '--tb=short',
            '--junitxml=reports/junit.xml',
            '--html=reports/pytest_report.html',
            '--self-contained-html'
        ]

        if parallel > 1:
            pytest_args.extend(['-n', str(parallel)])

        os.environ['PYTEST_API_TESTCASES'] = str(len(test_cases))

        return pytest.main(pytest_args)


def run_tests():
    """命令行入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description='API接口自动化测试工具')
    parser.add_argument('-d', '--dir', default='testcases', help='测试用例目录')
    parser.add_argument('-f', '--file', help='指定单个测试用例文件')
    parser.add_argument('-r', '--report', help='报告名称')
    parser.add_argument('-p', '--parallel', type=int, default=1, help='并发进程数')
    parser.add_argument('--no-pytest', action='store_true', help='不使用pytest运行')

    args = parser.parse_args()

    runner = TestRunner(testcases_dir=args.dir)

    if args.file:
        test_cases = runner.load_test_cases(args.file)
    else:
        test_cases = runner.load_test_cases()

    print(f"加载了 {len(test_cases)} 个测试用例")

    if args.no_pytest:
        results = runner.run_all_tests(test_cases)
        passed = sum(1 for r in results if r.get('passed', False))
        print(f"执行完成: {passed}/{len(results)} 通过")

        reports = runner.generate_reports(args.report)
        print(f"报告已生成:")
        for fmt, path in reports.items():
            print(f"  {fmt.upper()}: {path}")
    else:
        exit_code = runner.run_with_pytest(test_cases, args.parallel)
        sys.exit(exit_code)


if __name__ == '__main__':
    run_tests()
