import os
import json
from datetime import datetime
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    """HTML测试报告生成器"""

    def __init__(self, output_dir: str = 'reports'):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
        )

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_html_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        """
        生成HTML测试报告

        Args:
            test_results: 测试结果列表
            report_name: 报告名称

        Returns:
            报告文件路径
        """
        if not report_name:
            report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        report_data = self._prepare_report_data(test_results, report_name)

        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')

        if not os.path.exists(template_path):
            html_content = self._generate_default_template(report_data)
        else:
            template = self.env.get_template('report_template.html')
            html_content = template.render(**report_data)

        report_path = os.path.join(self.output_dir, f"{report_name}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path

    def _prepare_report_data(self, test_results: List[Dict[str, Any]], report_name: str) -> Dict[str, Any]:
        """
        准备报告数据

        Args:
            test_results: 测试结果列表
            report_name: 报告名称

        Returns:
            格式化的报告数据
        """
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.get('passed', False))
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        total_response_time = sum(r.get('response_time', 0) for r in test_results)
        avg_response_time = total_response_time / total_tests if total_tests > 0 else 0

        report_data = {
            'report_name': report_name,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': round(success_rate, 2),
                'total_time': round(total_response_time, 2),
                'avg_time': round(avg_response_time, 2)
            },
            'test_cases': self._format_test_cases(test_results),
            'tags_summary': self._generate_tags_summary(test_results),
            'module_summary': self._generate_module_summary(test_results)
        }

        return report_data

    def _format_test_cases(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化测试用例数据

        Args:
            test_results: 测试结果列表

        Returns:
            格式化的测试用例列表
        """
        formatted = []
        for idx, result in enumerate(test_results):
            formatted_case = {
                'index': idx + 1,
                'id': result.get('id', f'case_{idx}'),
                'name': result.get('name', f'Test Case {idx + 1}'),
                'description': result.get('description', ''),
                'tags': result.get('tags', []),
                'module': result.get('module', 'default'),
                'passed': result.get('passed', False),
                'status': '通过' if result.get('passed', False) else '失败',
                'status_class': 'success' if result.get('passed', False) else 'danger',
                'response_time': result.get('response_time', 0),
                'request': self._format_request(result.get('request', {})),
                'response': self._format_response(result.get('response', {})),
                'assertions': result.get('assertions', []),
                'error': result.get('error', '')
            }
            formatted.append(formatted_case)

        return formatted

    def _format_request(self, request: Dict[str, Any]) -> Dict[str, str]:
        """
        格式化请求数据

        Args:
            request: 请求数据

        Returns:
            格式化的请求数据
        """
        return {
            'method': request.get('method', ''),
            'url': request.get('url', ''),
            'headers': json.dumps(request.get('headers', {}), indent=2, ensure_ascii=False),
            'params': json.dumps(request.get('params', {}), indent=2, ensure_ascii=False),
            'body': json.dumps(request.get('json', request.get('data', {})), indent=2, ensure_ascii=False)
        }

    def _format_response(self, response: Dict[str, Any]) -> Dict[str, str]:
        """
        格式化响应数据

        Args:
            response: 响应数据

        Returns:
            格式化的响应数据
        """
        body = response.get('body', {})
        if isinstance(body, (dict, list)):
            body_str = json.dumps(body, indent=2, ensure_ascii=False)
        else:
            body_str = str(body)

        return {
            'status_code': response.get('status_code', 0),
            'headers': json.dumps(response.get('headers', {}), indent=2, ensure_ascii=False),
            'body': body_str,
            'response_time': response.get('response_time_ms', 0)
        }

    def _generate_tags_summary(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成标签统计

        Args:
            test_results: 测试结果列表

        Returns:
            标签统计列表
        """
        tags_map = {}

        for result in test_results:
            tags = result.get('tags', [])
            if not tags:
                tags = ['untagged']

            for tag in tags:
                if tag not in tags_map:
                    tags_map[tag] = {'total': 0, 'passed': 0, 'failed': 0}

                tags_map[tag]['total'] += 1
                if result.get('passed', False):
                    tags_map[tag]['passed'] += 1
                else:
                    tags_map[tag]['failed'] += 1

        summary = []
        for tag, counts in tags_map.items():
            success_rate = (counts['passed'] / counts['total'] * 100) if counts['total'] > 0 else 0
            summary.append({
                'tag': tag,
                'total': counts['total'],
                'passed': counts['passed'],
                'failed': counts['failed'],
                'success_rate': round(success_rate, 2)
            })

        return sorted(summary, key=lambda x: x['total'], reverse=True)

    def _generate_module_summary(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成模块统计

        Args:
            test_results: 测试结果列表

        Returns:
            模块统计列表
        """
        module_map = {}

        for result in test_results:
            module = result.get('module', 'default')

            if module not in module_map:
                module_map[module] = {'total': 0, 'passed': 0, 'failed': 0}

            module_map[module]['total'] += 1
            if result.get('passed', False):
                module_map[module]['passed'] += 1
            else:
                module_map[module]['failed'] += 1

        summary = []
        for module, counts in module_map.items():
            success_rate = (counts['passed'] / counts['total'] * 100) if counts['total'] > 0 else 0
            summary.append({
                'module': module,
                'total': counts['total'],
                'passed': counts['passed'],
                'failed': counts['failed'],
                'success_rate': round(success_rate, 2)
            })

        return sorted(summary, key=lambda x: x['total'], reverse=True)

    def _generate_default_template(self, data: Dict[str, Any]) -> str:
        """
        生成默认模板的HTML

        Args:
            data: 报告数据

        Returns:
            HTML内容字符串
        """
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['report_name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; }}
        .summary-card h3 {{ font-size: 14px; color: #666; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }}
        .summary-card .value {{ font-size: 36px; font-weight: bold; }}
        .summary-card.success .value {{ color: #28a745; }}
        .summary-card.danger .value {{ color: #dc3545; }}
        .summary-card.info .value {{ color: #17a2b8; }}
        .section {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        .section h2 {{ font-size: 20px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .tag {{ display: inline-block; padding: 3px 10px; background: #e9ecef; color: #495057; border-radius: 15px; font-size: 11px; margin-right: 5px; }}
        .test-case-header {{ cursor: pointer; user-select: none; }}
        .test-case-header:hover {{ background: #e9ecef; }}
        .test-case-detail {{ display: none; background: #f8f9fa; }}
        .test-case-detail.active {{ display: table-row; }}
        .detail-content {{ padding: 20px; }}
        .row {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .col {{ flex: 1; }}
        pre {{ background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; line-height: 1.6; }}
        .progress-bar {{ height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; margin-top: 10px; }}
        .progress {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {data['report_name']}</h1>
            <p>生成时间: {data['generated_at']}</p>
        </div>

        <div class="summary">
            <div class="summary-card info">
                <h3>总测试用例</h3>
                <div class="value">{data['summary']['total']}</div>
            </div>
            <div class="summary-card success">
                <h3>通过</h3>
                <div class="value">{data['summary']['passed']}</div>
            </div>
            <div class="summary-card danger">
                <h3>失败</h3>
                <div class="value">{data['summary']['failed']}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="value">{data['summary']['success_rate']}%</div>
                <div class="progress-bar">
                    <div class="progress" style="width: {data['summary']['success_rate']}%"></div>
                </div>
            </div>
            <div class="summary-card">
                <h3>总耗时</h3>
                <div class="value">{data['summary']['total_time']}ms</div>
            </div>
            <div class="summary-card">
                <h3>平均耗时</h3>
                <div class="value">{data['summary']['avg_time']}ms</div>
            </div>
        </div>

        <div class="section">
            <h2>📋 模块统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>模块</th>
                        <th>总数</th>
                        <th>通过</th>
                        <th>失败</th>
                        <th>成功率</th>
                    </tr>
                </thead>
                <tbody>
"""

        for module in data['module_summary']:
            html += f"""
                    <tr>
                        <td><strong>{module['module']}</strong></td>
                        <td>{module['total']}</td>
                        <td><span class="badge badge-success">{module['passed']}</span></td>
                        <td><span class="badge badge-danger">{module['failed']}</span></td>
                        <td>{module['success_rate']}%</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🏷️ 标签统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>标签</th>
                        <th>总数</th>
                        <th>通过</th>
                        <th>失败</th>
                        <th>成功率</th>
                    </tr>
                </thead>
                <tbody>
"""

        for tag in data['tags_summary']:
            html += f"""
                    <tr>
                        <td><span class="tag">{tag['tag']}</span></td>
                        <td>{tag['total']}</td>
                        <td><span class="badge badge-success">{tag['passed']}</span></td>
                        <td><span class="badge badge-danger">{tag['failed']}</span></td>
                        <td>{tag['success_rate']}%</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📝 测试详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>用例名称</th>
                        <th>标签</th>
                        <th>状态</th>
                        <th>响应时间</th>
                    </tr>
                </thead>
                <tbody>
"""

        for case in data['test_cases']:
            tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in case['tags']])
            html += f"""
                    <tr class="test-case-header" onclick="toggleDetail({case['index']})">
                        <td>{case['index']}</td>
                        <td><strong>{case['name']}</strong><br><small>{case['description']}</small></td>
                        <td>{tags_html}</td>
                        <td><span class="badge badge-{case['status_class']}">{case['status']}</span></td>
                        <td>{case['response_time']}ms</td>
                    </tr>
                    <tr id="detail-{case['index']}" class="test-case-detail">
                        <td colspan="5">
                            <div class="detail-content">
                                <div class="row">
                                    <div class="col">
                                        <h4>📤 请求</h4>
                                        <pre>{case['request']['method']} {case['request']['url']}\n\nHeaders:\n{case['request']['headers']}\n\nBody:\n{case['request']['body']}</pre>
                                    </div>
                                    <div class="col">
                                        <h4>📥 响应</h4>
                                        <pre>Status: {case['response']['status_code']}\nTime: {case['response']['response_time']}ms\n\nHeaders:\n{case['response']['headers']}\n\nBody:\n{case['response']['body']}</pre>
                                    </div>
                                </div>
"""

            if case['assertions']:
                html += "                                <h4>✅ 断言结果</h4><ul>"
                for assertion in case['assertions']:
                    status = "✓" if assertion.get('passed', False) else "✗"
                    html += f"<li>{status} {assertion.get('type', '')}: {assertion.get('message', '')}</li>"
                html += "</ul>"

            if case['error']:
                html += f"                                <h4>❌ 错误信息</h4><pre style='background: #f8d7da; color: #721c24;'>{case['error']}</pre>"

            html += """
                            </div>
                        </td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function toggleDetail(index) {
            const detail = document.getElementById('detail-' + index);
            detail.classList.toggle('active');
        }
    </script>
</body>
</html>
"""

        return html

    def generate_json_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        """
        生成JSON格式报告

        Args:
            test_results: 测试结果列表
            report_name: 报告名称

        Returns:
            报告文件路径
        """
        if not report_name:
            report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        report_data = {
            'report_name': report_name,
            'generated_at': datetime.now().isoformat(),
            'test_results': test_results
        }

        report_path = os.path.join(self.output_dir, f"{report_name}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return report_path

    def generate_markdown_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        """
        生成Markdown格式报告

        Args:
            test_results: 测试结果列表
            report_name: 报告名称

        Returns:
            报告文件路径
        """
        if not report_name:
            report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        total = len(test_results)
        passed = sum(1 for r in test_results if r.get('passed', False))
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0

        md_content = f"""# {report_name}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试摘要

| 指标 | 值 |
|------|-----|
| 总测试用例 | {total} |
| 通过 | {passed} ✅ |
| 失败 | {failed} ❌ |
| 成功率 | {success_rate:.2f}% |

## 测试详情

"""

        for idx, result in enumerate(test_results, 1):
            status = "✅ 通过" if result.get('passed', False) else "❌ 失败"
            md_content += f"""
### {idx}. {result.get('name', f'测试用例 {idx}')}

**状态**: {status}
**响应时间**: {result.get('response_time', 0)}ms

"""

        report_path = os.path.join(self.output_dir, f"{report_name}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return report_path
