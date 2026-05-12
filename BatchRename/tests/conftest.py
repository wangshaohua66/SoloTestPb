"""
pytest测试配置和fixtures
"""

import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


@pytest.fixture(autouse=True)
def setup_test_env():
    """
    为每个测试设置测试环境
    """
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)
