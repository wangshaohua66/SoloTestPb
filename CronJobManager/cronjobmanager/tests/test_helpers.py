"""
测试辅助函数模块
提供测试用的工具函数和mock函数
"""


def success_task() -> str:
    """
    成功执行的任务函数
    用于测试任务执行和示例脚本

    :return: 成功信息
    """
    return "Task executed successfully"


def failing_task() -> None:
    """
    总是失败的任务函数
    用于测试重试机制

    :raises RuntimeError: 总是抛出异常
    """
    raise RuntimeError("Test task failed intentionally")


def sample_success_func(param1: str = None, param2: int = 0) -> str:
    """
    示例成功函数
    用于测试正常执行的场景

    :param param1: 参数1
    :param param2: 参数2
    :return: 处理结果
    """
    return f"success: {param1}, {param2}"


def sample_failure_func() -> None:
    """
    示例失败函数
    用于测试异常执行的场景

    :raises RuntimeError: 总是抛出异常
    """
    raise RuntimeError("故意抛出的测试异常")


def sample_count_func() -> int:
    """
    示例计数函数
    用于测试重试机制

    :return: 执行次数
    """
    if not hasattr(sample_count_func, "call_count"):
        sample_count_func.call_count = 0
    
    sample_count_func.call_count += 1
    
    if sample_count_func.call_count < 2:
        raise RuntimeError("前两次失败")
    
    return sample_count_func.call_count
