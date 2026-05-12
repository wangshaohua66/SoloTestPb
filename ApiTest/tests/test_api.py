import pytest
import allure
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import TestRunner


@pytest.fixture(scope='session')
def test_runner():
    """测试运行器fixture"""
    runner = TestRunner()
    return runner


@pytest.fixture(scope='session')
def test_cases(test_runner):
    """加载所有测试用例"""
    cases = test_runner.load_test_cases()
    return cases


def pytest_generate_tests(metafunc):
    """动态生成测试用例"""
    if 'test_case' in metafunc.fixturenames:
        runner = TestRunner()
        cases = runner.load_test_cases()
        if cases:
            metafunc.parametrize('test_case', cases, ids=lambda c: c.get('id', c.get('name')))


@allure.feature('API接口测试')
@allure.story('执行API测试用例')
def test_api_case(test_case, test_runner):
    """执行单个API测试用例"""
    if 'depends_on' in test_case and test_case['depends_on']:
        pytest.skip("跳过带有依赖的测试用例 - 需要按顺序执行")

    allure.dynamic.title(test_case.get('name', test_case.get('id')))
    allure.dynamic.description(test_case.get('description', ''))

    for tag in test_case.get('tags', []):
        allure.dynamic.tag(tag)

    result = test_runner.run_single_test(test_case)

    if result.get('request'):
        req = result['request']
        allure.attach(
            f"{req.get('method')} {req.get('url')}\n\nHeaders: {req.get('headers')}\nBody: {req.get('json', req.get('data'))}",
            'Request',
            allure.attachment_type.TEXT
        )

    if result.get('response'):
        resp = result['response']
        allure.attach(
            f"Status: {resp.get('status_code')}\nTime: {resp.get('response_time_ms')}ms\n\nBody: {resp.get('body')}",
            'Response',
            allure.attachment_type.TEXT
        )

    if result.get('error'):
        allure.attach(result['error'], 'Error', allure.attachment_type.TEXT)

    assert result.get('passed', False), f"测试失败: {result.get('error', '')}"
