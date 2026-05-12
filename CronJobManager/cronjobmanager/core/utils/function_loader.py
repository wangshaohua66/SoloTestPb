"""
函数加载工具模块
负责动态加载任务执行函数
"""

import importlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Callable


class FunctionLoadError(Exception):
    """
    函数加载异常
    """
    pass


class FunctionTimeoutError(Exception):
    """
    函数执行超时异常
    """
    pass


_executor: ThreadPoolExecutor = None


def get_executor() -> ThreadPoolExecutor:
    """
    获取模块级共享的线程池执行器

    :return: 线程池执行器
    """
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=10)
    return _executor


def shutdown_executor():
    """
    关闭线程池执行器
    """
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=False)
        _executor = None


def load_function(func_path: str) -> Callable[..., Any]:
    """
    根据函数路径动态加载函数

    :param func_path: 函数路径，格式为 "module.submodule.function_name"
    :return: 加载的函数对象
    :raises FunctionLoadError: 当函数加载失败时抛出
    """
    try:
        if "." not in func_path:
            raise FunctionLoadError(
                f"无效的函数路径格式: {func_path}，需要使用 module.function 格式"
            )

        module_path, func_name = func_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)

        if not callable(func):
            raise FunctionLoadError(
                f"路径 {func_path} 指向的对象不是可调用的函数"
            )

        return func
    except ImportError as e:
        raise FunctionLoadError(f"无法导入模块: {module_path}，错误: {str(e)}") from e
    except AttributeError as e:
        raise FunctionLoadError(f"模块 {module_path} 中不存在函数 {func_name}") from e
    except Exception as e:
        raise FunctionLoadError(f"加载函数 {func_path} 时发生错误: {str(e)}") from e


def execute_function(
    func: Callable[..., Any],
    args: list = None,
    kwargs: dict = None,
    timeout: int = None,
) -> Any:
    """
    执行函数，支持超时控制（跨平台实现）

    :param func: 要执行的函数
    :param args: 函数位置参数
    :param kwargs: 函数关键字参数
    :param timeout: 超时时间（秒）
    :return: 函数返回值
    :raises FunctionTimeoutError: 当函数执行超时时抛出
    """
    args = args or []
    kwargs = kwargs or {}

    if timeout is None or timeout <= 0:
        return func(*args, **kwargs)

    executor = get_executor()
    future = executor.submit(func, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except FutureTimeoutError:
        raise FunctionTimeoutError(f"函数执行超时，超过 {timeout} 秒")
