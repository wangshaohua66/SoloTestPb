"""
函数加载器模块单元测试
"""

import pytest

from core.utils.function_loader import (
    load_function,
    execute_function,
    FunctionLoadError,
)


class TestFunctionLoader:
    """
    函数加载器类测试
    """

    def test_load_function_success(self):
        """
        测试成功加载函数
        """
        func = load_function("tests.test_helpers.sample_success_func")
        
        assert func is not None
        assert callable(func)
        
        result = func("test", 123)
        assert result == "success: test, 123"

    def test_load_function_invalid_format(self):
        """
        测试加载无效格式的函数路径
        """
        with pytest.raises(FunctionLoadError, match="无效的函数路径格式"):
            load_function("invalid_format")

    def test_load_function_nonexistent_module(self):
        """
        测试加载不存在的模块
        """
        with pytest.raises(FunctionLoadError, match="无法导入模块"):
            load_function("nonexistent.module.function")

    def test_load_function_nonexistent_function(self):
        """
        测试加载模块中不存在的函数
        """
        with pytest.raises(FunctionLoadError, match="模块.*中不存在函数"):
            load_function("tests.test_helpers.nonexistent_func")

    def test_load_function_not_callable(self):
        """
        测试加载不可调用的对象
        """
        with pytest.raises(FunctionLoadError, match="指向的对象不是可调用的函数"):
            load_function("tests.test_helpers.__doc__")

    def test_execute_function_without_timeout(self):
        """
        测试无超时执行函数
        """
        func = load_function("tests.test_helpers.sample_success_func")
        
        result = execute_function(func, args=["param1"], kwargs={"param2": 42})
        
        assert result == "success: param1, 42"

    def test_execute_function_default_args(self):
        """
        测试使用默认参数执行函数
        """
        func = load_function("tests.test_helpers.sample_success_func")
        
        result = execute_function(func)
        
        assert result == "success: None, 0"

    def test_execute_function_exception(self):
        """
        测试执行抛出异常的函数
        """
        func = load_function("tests.test_helpers.sample_failure_func")
        
        with pytest.raises(RuntimeError, match="故意抛出的测试异常"):
            execute_function(func)
