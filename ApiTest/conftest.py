import pytest
import allure
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import ConfigParser, HttpClient, VariableEngine, AssertionEngine, DependencyManager

@pytest.fixture(scope='session')
def config_parser():
    """配置解析器fixture"""
    return ConfigParser()

@pytest.fixture(scope='session')
def http_client():
    """HTTP客户端fixture"""
    return HttpClient()

@pytest.fixture(scope='session')
def variable_engine():
    """变量引擎fixture"""
    return VariableEngine()

@pytest.fixture(scope='session')
def assertion_engine():
    """断言引擎fixture"""
    return AssertionEngine()

@pytest.fixture(scope='session')
def dependency_manager():
    """依赖管理器fixture"""
    return DependencyManager()

@pytest.fixture(scope='function', autouse=True)
def case_info(request):
    """测试用例信息fixture"""
    allure.dynamic.title(request.node.name)
    allure.dynamic.description(f"测试用例: {request.node.name}")
