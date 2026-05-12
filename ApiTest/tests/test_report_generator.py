import pytest
import os
import json
from core.report_generator import ReportGenerator


class TestReportGenerator:
    """报告生成器单元测试"""

    @pytest.fixture
    def generator(self, tmp_path):
        return ReportGenerator(output_dir=str(tmp_path))

    @pytest.fixture
    def sample_test_results(self):
        return [
            {
                'id': 'test_001',
                'name': '测试用例1',
                'description': '这是第一个测试用例',
                'tags': ['smoke', 'api'],
                'module': 'user',
                'passed': True,
                'response_time': 150,
                'request': {
                    'method': 'GET',
                    'url': 'https://api.example.com/users'
                },
                'response': {
                    'status_code': 200,
                    'body': {'success': True, 'data': []},
                    'headers': {'Content-Type': 'application/json'}
                },
                'assertions': [
                    {'type': 'status_code', 'passed': True}
                ]
            },
            {
                'id': 'test_002',
                'name': '测试用例2',
                'description': '这是第二个测试用例',
                'tags': ['regression'],
                'module': 'auth',
                'passed': False,
                'response_time': 300,
                'request': {
                    'method': 'POST',
                    'url': 'https://api.example.com/login'
                },
                'response': {
                    'status_code': 401,
                    'body': {'error': 'Unauthorized'},
                    'headers': {}
                },
                'assertions': [
                    {'type': 'status_code', 'passed': False}
                ],
                'error': '状态码断言失败'
            }
        ]

    def test_initialization_default(self):
        """测试默认初始化"""
        generator = ReportGenerator()
        assert 'reports' in generator.output_dir

    def test_initialization_with_output_dir(self, tmp_path):
        """测试指定输出目录初始化"""
        custom_dir = str(tmp_path / 'test_reports')
        generator = ReportGenerator(output_dir=custom_dir)
        assert generator.output_dir == custom_dir

    def test_ensure_output_dir_creates_dir(self, tmp_path):
        """测试确保输出目录被创建"""
        new_dir = str(tmp_path / 'new_dir')
        assert not os.path.exists(new_dir)
        generator = ReportGenerator(output_dir=new_dir)
        assert os.path.exists(new_dir)

    def test_prepare_report_data_basic(self, generator, sample_test_results):
        """测试准备报告基础数据"""
        data = generator._prepare_report_data(sample_test_results, 'test_report')
        assert data['report_name'] == 'test_report'
        assert 'generated_at' in data
        assert data['summary']['total'] == 2
        assert data['summary']['passed'] == 1
        assert data['summary']['failed'] == 1

    def test_prepare_report_data_success_rate(self, generator, sample_test_results):
        """测试计算成功率"""
        data = generator._prepare_report_data(sample_test_results, 'test')
        assert data['summary']['success_rate'] == 50.0

    def test_prepare_report_data_avg_time(self, generator, sample_test_results):
        """测试计算平均响应时间"""
        data = generator._prepare_report_data(sample_test_results, 'test')
        assert data['summary']['avg_time'] == 225.0

    def test_format_test_cases_count(self, generator, sample_test_results):
        """测试格式化测试用例数量"""
        formatted = generator._format_test_cases(sample_test_results)
        assert len(formatted) == 2

    def test_format_test_cases_fields(self, generator, sample_test_results):
        """测试格式化测试用例字段"""
        formatted = generator._format_test_cases(sample_test_results)
        case = formatted[0]
        assert 'index' in case
        assert 'id' in case
        assert 'name' in case
        assert 'status' in case
        assert 'request' in case
        assert 'response' in case

    def test_format_test_cases_passed_status(self, generator, sample_test_results):
        """测试通过的用例状态"""
        formatted = generator._format_test_cases(sample_test_results)
        assert formatted[0]['status'] == '通过'
        assert formatted[1]['status'] == '失败'

    def test_format_request(self, generator):
        """测试格式化请求"""
        request = {
            'method': 'POST',
            'url': 'https://api.example.com/test',
            'headers': {'Content-Type': 'application/json'},
            'params': {'page': 1},
            'json': {'key': 'value'}
        }
        formatted = generator._format_request(request)
        assert formatted['method'] == 'POST'
        assert formatted['url'] == 'https://api.example.com/test'
        assert 'headers' in formatted
        assert 'body' in formatted

    def test_format_response_json(self, generator):
        """测试格式化JSON响应"""
        response = {
            'status_code': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'success': True},
            'response_time_ms': 150
        }
        formatted = generator._format_response(response)
        assert formatted['status_code'] == 200
        assert 'body' in formatted

    def test_format_response_text(self, generator):
        """测试格式化文本响应"""
        response = {
            'status_code': 200,
            'headers': {},
            'body': 'Plain text response',
            'response_time_ms': 100
        }
        formatted = generator._format_response(response)
        assert formatted['body'] == 'Plain text response'

    def test_generate_tags_summary(self, generator, sample_test_results):
        """测试生成标签统计"""
        summary = generator._generate_tags_summary(sample_test_results)
        assert len(summary) >= 2
        tags = [s['tag'] for s in summary]
        assert 'smoke' in tags
        assert 'regression' in tags

    def test_generate_tags_summary_counts(self, generator, sample_test_results):
        """测试标签统计计数"""
        summary = generator._generate_tags_summary(sample_test_results)
        smoke_tag = next(s for s in summary if s['tag'] == 'smoke')
        assert smoke_tag['total'] == 1
        assert smoke_tag['passed'] == 1

    def test_generate_module_summary(self, generator, sample_test_results):
        """测试生成模块统计"""
        summary = generator._generate_module_summary(sample_test_results)
        assert len(summary) == 2
        modules = [s['module'] for s in summary]
        assert 'user' in modules
        assert 'auth' in modules

    def test_generate_module_summary_counts(self, generator, sample_test_results):
        """测试模块统计计数"""
        summary = generator._generate_module_summary(sample_test_results)
        user_module = next(m for m in summary if m['module'] == 'user')
        assert user_module['total'] == 1
        assert user_module['passed'] == 1

    def test_generate_html_report(self, generator, sample_test_results):
        """测试生成HTML报告"""
        report_path = generator.generate_html_report(sample_test_results, 'test_report')
        assert os.path.exists(report_path)
        assert report_path.endswith('.html')

    def test_generate_html_report_content(self, generator, sample_test_results):
        """测试HTML报告内容"""
        report_path = generator.generate_html_report(sample_test_results, 'test_report')
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<html' in content
        assert '测试用例1' in content
        assert 'test_report' in content

    def test_generate_html_report_default_name(self, generator, sample_test_results):
        """测试不指定报告名称"""
        report_path = generator.generate_html_report(sample_test_results)
        assert os.path.exists(report_path)
        assert 'test_report' in report_path

    def test_generate_json_report(self, generator, sample_test_results):
        """测试生成JSON报告"""
        report_path = generator.generate_json_report(sample_test_results, 'test_report')
        assert os.path.exists(report_path)
        assert report_path.endswith('.json')

    def test_generate_json_report_content(self, generator, sample_test_results):
        """测试JSON报告内容"""
        report_path = generator.generate_json_report(sample_test_results, 'test_report')
        with open(report_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        assert content['report_name'] == 'test_report'
        assert 'generated_at' in content
        assert len(content['test_results']) == 2

    def test_generate_markdown_report(self, generator, sample_test_results):
        """测试生成Markdown报告"""
        report_path = generator.generate_markdown_report(sample_test_results, 'test_report')
        assert os.path.exists(report_path)
        assert report_path.endswith('.md')

    def test_generate_markdown_report_content(self, generator, sample_test_results):
        """测试Markdown报告内容"""
        report_path = generator.generate_markdown_report(sample_test_results, 'test_report')
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '# test_report' in content
        assert '测试用例1' in content

    def test_generate_default_template(self, generator, sample_test_results):
        """测试生成默认模板内容"""
        data = generator._prepare_report_data(sample_test_results, 'test')
        html = generator._generate_default_template(data)
        assert '<!DOCTYPE html>' in html
        assert 'html' in html.lower()

    def test_all_report_types_generated(self, generator, sample_test_results):
        """测试所有报告类型都能生成"""
        html_path = generator.generate_html_report(sample_test_results, 'report')
        json_path = generator.generate_json_report(sample_test_results, 'report')
        md_path = generator.generate_markdown_report(sample_test_results, 'report')
        assert os.path.exists(html_path)
        assert os.path.exists(json_path)
        assert os.path.exists(md_path)
